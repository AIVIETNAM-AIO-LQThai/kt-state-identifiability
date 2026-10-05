"""Multi-start fit of B1/B2 with free item difficulties (66 coordinates for B2). Mirrors kt_trial.fit.fit_model: D19 absolute stopping
rule, D22 Newton-decrement certificate on all active coordinates, deterministic starts (tau_F / tau_R grids), embedded null for B2."""
from __future__ import annotations

import time

import numpy as np

from kt_trial.composite_likelihood import PairCounts
from kt_trial.config import rng_for
from kt_trial.fit import _one_start, default_theta, make_starts, newton_certificate
from kt_trial.models import embed
from kt_trial.moments import Theta
from kt_trial.schedule import Template

from .model import FreeObjective, FreeParamMap, start_difficulties

B_JITTER_SD = 0.05


def fit_free(model: str, templates: list[Template], pc: PairCounts, cfg_fit: dict, K: int, ids: np.ndarray, n_items: int,
             seed_keys: tuple, master_seed: int, warm: tuple | None = None, null_fit: dict | None = None) -> dict:
    """`warm` = (Theta, b) from a smaller model; `null_fit` = a B1-free fit dict (embedded-null candidate for B2)."""
    t0 = time.time()
    pm = FreeParamMap(model, K, n_items)
    obj = FreeObjective(pm, templates, pc, ids)
    rng = rng_for(master_seed, "fitfree", model, *seed_keys)
    th_warm = warm[0] if warm is not None else None
    b0 = np.asarray(warm[1], float) if warm is not None else start_difficulties(templates, ids, pc, default_theta(cfg_fit, K), n_items)
    starts = []
    for i, xt in enumerate(make_starts(model, pm.base, cfg_fit, K, rng, th_warm)):
        bj = b0 if i == 0 else b0 + rng.normal(0.0, B_JITTER_SD, size=b0.shape)
        starts.append(np.clip(np.concatenate([xt, bj]), pm.lb, pm.ub))
    runs = [_one_start(obj, x0, cfg_fit) for x0 in starts]
    good = [r for r in runs if r["ok"] and np.isfinite(r["ll"])]
    out = dict(model=model, arm="free", n_params=pm.n, N=pc.N, runs=[{k: v for k, v in r.items() if k != "x"} for r in runs],
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
        x = pm.theta_b_to_x(theta, null_fit["b"])
        best = dict(best, ll=null_fit["ll"], grad_norm=float("nan"), grad_inf=float("nan"), converged=True, message="embedded_null")
        fell_back = True
    tol = cfg_fit["boundary_tol"]
    hits = pm.boundary_hits(x, tol)
    flags = [f"boundary:{h}" for h in hits if not h.startswith("b[")]
    flags += [f"boundary:{h}" for h in hits if h.startswith("b[")][:3]
    cert = dict(null_fit["certificate"], reused_from="B1") if fell_back else newton_certificate(pm, obj, x, theta, cfg_fit)
    if not best["converged"] and str(best["message"]).startswith("ABNORMAL") and not cert["hessian_not_pd"] \
            and cert["newton_decrement"] <= cfg_fit["newton_tol"]:
        best = dict(best, converged=True)
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
    ll_best = float(lls.max())
    at_best = np.array([r["ll"] >= ll_best - cfg_fit["agree_tol"] for r in good])
    secondary = np.array([bool(r["converged"]) and r["ll"] < ll_best - cfg_fit["secondary_delta"] for r in good])
    if at_best.sum() < 2:
        flags.append("single_start_at_best")
    if secondary.any():
        flags.append("secondary_optima_present")
    if model == "B2" and theta.sigma2_F <= tol:
        flags.append("tau_F_not_identified(sigma2_F=0)")
    out.update(status="ok" if not ({"not_converged", "all_starts_failed"} & set(flags)) else "flagged",
               theta=theta.to_dict(), b=x[pm.nt:].tolist(), x=x.tolist(), ll=float(best["ll"]),
               grad_inf_abs=best["grad_inf"], certificate=cert, converged=bool(best["converged"]), message=best["message"],
               boundary_hits=hits, flags=flags, n_starts=len(starts), n_good_starts=len(good),
               start_agreement={"n_starts_at_best": int(at_best.sum()), "secondary_optima": int(secondary.sum()),
                                "ll_range": float(lls.max() - lls.min())},
               runtime=time.time() - t0)
    return out
