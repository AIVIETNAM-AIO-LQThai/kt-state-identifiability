"""Model fitting: L-BFGS-B on the pairwise composite likelihood with deterministic multi-start."""
from __future__ import annotations

import time
import traceback

import numpy as np
from scipy.optimize import minimize

from .composite_likelihood import PairCounts, composite_loglik
from .config import rng_for
from .models import INACTIVE, ParamMap, embed
from .moments import Theta
from .schedule import Template

CONVERGED_PREFIX = "CONVERGENCE"          # scipy: "CONVERGENCE: NORM OF PROJECTED GRADIENT <= PGTOL" / "REL_REDUCTION_OF_F..."


def default_theta(cfg_fit: dict, K: int) -> Theta:
    s = cfg_fit["start"]
    Sig = s["sigma_M"]["ind"] * np.eye(K) + s["sigma_M"]["common"] * np.ones((K, K))
    return Theta(s["alpha_bar"], s["phi"], s["sigma2_alpha"], s["r_bar"], s["tau_R"], s["sigma2_r"],
                 s["sigma2_F"], s["tau_F"], Sig)


class Objective:
    """Normalised negative composite log-likelihood (per learner-pair) in free coordinates."""

    def __init__(self, pm: ParamMap, templates, pc: PairCounts):
        self.pm, self.templates, self.pc = pm, templates, pc
        self.scale = float(pc.counts.sum())          # total pair-observations (N * pairs)
        self.n_eval = 0
        self.bad = 0

    def __call__(self, x):
        self.n_eval += 1
        th = self.pm.x_to_theta(x)
        try:
            ll, g_nat, diag = composite_loglik(th, self.templates, self.pc)
        except (np.linalg.LinAlgError, FloatingPointError, ValueError):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        if not np.isfinite(ll) or not np.all(np.isfinite(g_nat)):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        J = self.pm.jacobian(x)
        return -ll / self.scale, -(J.T @ g_nat) / self.scale

    def loglik(self, x):
        th = self.pm.x_to_theta(x)
        return composite_loglik(th, self.templates, self.pc, grad=False)[0]


def _one_start(obj: Objective, x0, cfg_fit) -> dict:
    t0 = time.time()
    obj.n_eval = 0; obj.bad = 0
    x0 = np.clip(x0, obj.pm.lb, obj.pm.ub)
    try:
        res = minimize(obj, x0, jac=True, method="L-BFGS-B", bounds=list(zip(obj.pm.lb, obj.pm.ub)),
                       options=dict(maxiter=cfg_fit["max_iter"], ftol=1e-14, gtol=cfg_fit["gtol"], maxcor=20))
        x = res.x
        f, g = obj(x)
        pg = obj.pm.project_grad(x, g)
        msg = res.message.decode() if isinstance(res.message, bytes) else str(res.message)
        return dict(ok=True, x=x.tolist(), ll=-f * obj.scale, f=f, grad_norm=float(np.linalg.norm(pg)),
                    grad_inf=float(np.abs(pg).max()), message=msg, n_iter=int(res.nit), n_eval=obj.n_eval,
                    n_bad_eval=obj.bad, converged=bool(msg.startswith(CONVERGED_PREFIX)),
                    runtime=time.time() - t0)
    except Exception as e:  # recorded as data, never silently dropped
        return dict(ok=False, error=repr(e), trace=traceback.format_exc(limit=3), runtime=time.time() - t0)


def make_starts(model: str, pm: ParamMap, cfg_fit: dict, K: int, rng, warm: Theta | None):
    """Deterministic start list (5 by default). Start 0 is unperturbed; the others get seeded jitter."""
    base = warm if warm is not None else default_theta(cfg_fit, K)
    n = cfg_fit["n_starts"]
    starts = []
    if model == "B0":
        grid = [None] * n
    elif model == "B1":
        grid = ("tau_R", cfg_fit["tau_R_grid"])
    else:
        grid = ("tau_F", cfg_fit["tau_F_grid"])
    for i in range(n):
        th = embed(base, model).copy()
        if model == "B2":                       # start F small but positive; B1 solution supplies the rest
            th = th.copy(sigma2_F=max(cfg_fit["start"]["sigma2_F"], 1e-3))
        if grid is not None and grid != [None] * n:
            setattr(th, grid[0], float(grid[1][i % len(grid[1])]))
        x = pm.theta_to_x(th)
        if i > 0:
            jit = rng.normal(0.0, cfg_fit["jitter_sd"], size=x.shape)
            if model == "B2":
                jit[pm.names.index("tau_F")] = 0.0          # keep the grid value exactly
            if model == "B1":
                jit[pm.names.index("tau_R")] = 0.0
            x = x + jit
        starts.append(np.clip(x, pm.lb, pm.ub))
    return starts


def fit_model(model: str, templates: list[Template], pc: PairCounts, cfg_fit: dict, K: int,
              seed_keys: tuple, master_seed: int, warm: Theta | None = None,
              null_fit: dict | None = None) -> dict:
    """Multi-start fit of one model. `null_fit` (a B1 fit dict) supplies the embedded-null candidate for B2."""
    t0 = time.time()
    pm = ParamMap(model, K)
    obj = Objective(pm, templates, pc)
    rng = rng_for(master_seed, "fit", model, *seed_keys)
    starts = make_starts(model, pm, cfg_fit, K, rng, warm)
    runs = [_one_start(obj, x0, cfg_fit) for x0 in starts]
    good = [r for r in runs if r["ok"] and np.isfinite(r["ll"])]
    out = dict(model=model, n_params=pm.n, N=pc.N, runs=[{k: v for k, v in r.items() if k != "x"} for r in runs],
               flags=[], seed_keys=[str(k) for k in seed_keys])
    if not good:
        out.update(status="failed", flags=["all_starts_failed"], runtime=time.time() - t0)
        return out
    best = max(good, key=lambda r: r["ll"])
    x = np.array(best["x"])
    theta = pm.x_to_theta(x)
    fell_back = False
    if model == "B2" and null_fit is not None and null_fit.get("status") != "failed" and null_fit["ll"] > best["ll"] + 1e-9:
        theta = embed(Theta.from_dict(null_fit["theta"]), "B2").copy(sigma2_F=0.0)
        x = pm.theta_to_x(theta)
        best = dict(best, ll=null_fit["ll"], grad_norm=float("nan"), converged=True, message="embedded_null")
        fell_back = True
    tol = cfg_fit["boundary_tol"]
    hits = pm.boundary_hits(x, tol)
    flags = [f"boundary:{h}" for h in hits]
    if not best["converged"]:
        flags.append("not_converged")
    if best["grad_norm"] == best["grad_norm"] and best["grad_norm"] > cfg_fit["grad_flag_tol"]:
        flags.append("large_projected_gradient")
    if any(r["n_bad_eval"] > 0 for r in good):
        flags.append("nonfinite_objective_encountered")
    if fell_back:
        flags.append("embedded_null_selected")
    lls = np.array([r["ll"] for r in good])
    norm = pc.counts.sum()
    agree = lls >= lls.max() - 1e-6 * norm
    xs = np.array([r["x"] for r in good])
    thetas = [pm.x_to_theta(v) for v in xs[agree]]
    gap = float(max(np.abs(a.to_nat()[:8] - b.to_nat()[:8]).max() for a in thetas for b in thetas))
    if agree.sum() < 2:
        flags.append("no_start_agreement")
    if model == "B2" and theta.sigma2_F <= tol:
        flags.append("tau_F_not_identified(sigma2_F=0)")
    out.update(status="ok" if not ({"not_converged", "all_starts_failed"} & set(flags)) else "flagged",
               theta=theta.to_dict(), x=x.tolist(), ll=float(best["ll"]), loglik_per_pair=float(best["ll"] / norm),
               grad_norm=best["grad_norm"], converged=bool(best["converged"]), message=best["message"],
               boundary_hits=hits, flags=flags, n_starts=len(starts), n_good_starts=len(good),
               start_agreement={"n_within_1e-6_per_pair": int(agree.sum()), "max_scalar_param_gap": gap,
                                "ll_range": float(lls.max() - lls.min())},
               n_iter_total=int(sum(r.get("n_iter", 0) for r in good)),
               n_eval_total=int(sum(r.get("n_eval", 0) for r in good)), runtime=time.time() - t0)
    return out
