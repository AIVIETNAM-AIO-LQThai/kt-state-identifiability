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


def effective_gtol(cfg_fit: dict, scale: float) -> float:
    """Per-pair-objective gradient tolerance equal to `gtol_abs` log-likelihood units, whatever N is (D19)."""
    return cfg_fit["gtol_abs"] / scale


def newton_certificate(pm: ParamMap, obj: "Objective", x, theta: Theta, cfg_fit: dict) -> dict:
    """D22: Newton decrement g'H^-1 g / 2 (absolute log-lik units) on the active free coordinates.

    Active = strictly inside the bounds; tau_F is dropped when sigma2_F = 0 and tau_R when the fast component is
    absent. H is the symmetrised central-difference Jacobian of the analytic gradient of -loglik. A non-positive-
    definite H returns hessian_not_pd = True and a NaN decrement.
    """
    tol = cfg_fit["boundary_tol"]
    x = np.asarray(x, float)
    act = [i for i in range(pm.n) if pm.lb[i] + tol < x[i] < pm.ub[i] - tol]
    drop = []
    if "tau_F" in pm.names and theta.sigma2_F <= tol:
        drop.append("tau_F")
    if "tau_R" in pm.names and theta.sigma2_r <= tol and abs(theta.r_bar) <= tol:
        drop.append("tau_R")
    act = [i for i in act if pm.names[i] not in drop]
    S = obj.scale
    g = obj(x)[1][act] * S
    H = np.zeros((len(act), len(act)))
    for a, i in enumerate(act):
        h = cfg_fit["hess_step"] * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        H[a] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[act] * S
    H = 0.5 * (H + H.T)
    w = np.linalg.eigvalsh(H) if len(act) else np.array([1.0])
    not_pd = bool(not np.all(np.isfinite(H)) or w.min() <= 0)
    dec = float("nan") if not_pd else float(0.5 * g @ np.linalg.solve(H, g)) if len(act) else 0.0
    return {"newton_decrement": dec, "hessian_min_eig": float(w.min()), "hessian_not_pd": not_pd,
            "active_coords": [pm.names[i] for i in act]}


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
                       options=dict(maxiter=cfg_fit["max_iter"], ftol=cfg_fit["ftol"],
                                    gtol=effective_gtol(cfg_fit, obj.scale), maxcor=20))
        x = res.x
        f, g = obj(x)
        pg = obj.pm.project_grad(x, g) * obj.scale             # ABSOLUTE log-likelihood units
        msg = res.message.decode() if isinstance(res.message, bytes) else str(res.message)
        grad_inf = float(np.abs(pg).max())
        converged = bool(msg.startswith(CONVERGED_PREFIX))     # ABNORMAL stalls are re-judged by the D22 certificate
        return dict(ok=True, x=x.tolist(), ll=-f * obj.scale, f=f, grad_norm=float(np.linalg.norm(pg)),
                    grad_inf=grad_inf, message=msg, n_iter=int(res.nit), n_eval=obj.n_eval,
                    n_bad_eval=obj.bad, converged=converged, runtime=time.time() - t0)
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
        best = dict(best, ll=null_fit["ll"], grad_norm=float("nan"), grad_inf=float("nan"), converged=True,
                    message="embedded_null")
        fell_back = True
    tol = cfg_fit["boundary_tol"]
    hits = pm.boundary_hits(x, tol)
    flags = [f"boundary:{h}" for h in hits]
    if fell_back:
        cert = dict(null_fit["certificate"], reused_from="B1")
    else:
        cert = newton_certificate(pm, obj, x, theta, cfg_fit)
    if not best["converged"] and best["message"].startswith("ABNORMAL") and not cert["hessian_not_pd"] \
            and cert["newton_decrement"] <= cfg_fit["newton_tol"]:
        best = dict(best, converged=True)                 # line-search stall at a certified optimum
    if not best["converged"]:
        flags.append("not_converged")
    if cert["hessian_not_pd"]:
        flags.append("hessian_not_pd")
    elif cert["newton_decrement"] > cfg_fit["newton_tol"]:
        flags.append("newton_decrement_large")
    if any(r["n_bad_eval"] > 0 for r in good):
        flags.append("nonfinite_objective_encountered")
    if fell_back:
        flags.append("embedded_null_selected")
    lls = np.array([r["ll"] for r in good])
    norm = pc.counts.sum()
    ll_best = float(lls.max())                          # best START (independent of the embedded-null candidate)
    at_best = np.array([r["ll"] >= ll_best - cfg_fit["agree_tol"] for r in good])
    secondary = np.array([bool(r["converged"]) and r["ll"] < ll_best - cfg_fit["secondary_delta"] for r in good])
    xs = np.array([r["x"] for r in good])
    thetas = [pm.x_to_theta(v) for v in xs[at_best]]
    names_cmp = list(range(8))
    if theta.sigma2_F <= tol and model == "B2":
        names_cmp.remove(7)                              # tau_F is inert when sigma2_F = 0
    gap = float(max(np.abs(a.to_nat()[names_cmp] - b.to_nat()[names_cmp]).max() for a in thetas for b in thetas))
    if at_best.sum() < 2:
        flags.append("single_start_at_best")
    if secondary.any():
        flags.append("secondary_optima_present")
    if model == "B2" and theta.sigma2_F <= tol:
        flags.append("tau_F_not_identified(sigma2_F=0)")
    out.update(status="ok" if not ({"not_converged", "all_starts_failed"} & set(flags)) else "flagged",
               theta=theta.to_dict(), x=x.tolist(), ll=float(best["ll"]), loglik_per_pair=float(best["ll"] / norm),
               grad_norm=best["grad_norm"], grad_inf_abs=best["grad_inf"], certificate=cert, converged=bool(best["converged"]), message=best["message"],
               boundary_hits=hits, flags=flags, n_starts=len(starts), n_good_starts=len(good),
               start_agreement={"n_starts_at_best": int(at_best.sum()), "secondary_optima": int(secondary.sum()),
                                "max_scalar_param_gap": gap, "ll_range": float(lls.max() - lls.min())},
               n_iter_total=int(sum(r.get("n_iter", 0) for r in good)),
               n_eval_total=int(sum(r.get("n_eval", 0) for r in good)), runtime=time.time() - t0)
    return out
