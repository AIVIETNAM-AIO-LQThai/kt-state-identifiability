"""Inference: Godambe/sandwich SEs (interior fits), learner bootstrap, boundary-aware null test for sigma2_F = 0.

Independent units are learners: the variability matrix J is the covariance of learner-level composite scores,
never of the individual response pairs. The sandwich is only reported for parameters away from a bound;
the null sigma2_F = 0 lies on the boundary and is tested with a parametric bootstrap of the composite
likelihood-ratio statistic CLR = 2[l(B2) - l(B1)], repeating the complete B1 and B2 multi-start searches
(including the tau_F grid) in every replicate.
"""
from __future__ import annotations

import copy
import time

import numpy as np

from .composite_likelihood import composite_loglik, learner_scores_nat, pair_counts
from .config import rng_for
from .fit import Objective, fit_model
from .models import ParamMap
from .moments import SCALAR_NAMES, Theta
from .schedule import Template
from .simulator import Dataset, simulate

Z975 = 1.959963984540054


def _active_coords(pm: ParamMap, x, tol):
    """Coordinates strictly inside their bounds; tau_F/tau_R are dropped when their variance is inactive."""
    act = np.array([lo + tol < xi < hi - tol for xi, lo, hi in zip(x, pm.lb, pm.ub)])
    th = pm.x_to_theta(x)
    for name, var_ok in (("tau_F", th.sigma2_F > tol), ("tau_R", th.sigma2_r > tol or abs(th.r_bar) > tol)):
        if name in pm.names and not var_ok:
            act[pm.names.index(name)] = False
    return act


def sandwich(fit: dict, templates: list[Template], ds: Dataset, cfg_fit: dict, K: int) -> dict:
    """Godambe covariance V = H^-1 J H^-1 / N in free coordinates of the active parameters, plus scalar SEs."""
    if fit.get("status") == "failed":
        return {"status": "unavailable", "reason": "fit failed"}
    pm = ParamMap(fit["model"], K)
    x = np.array(fit["x"])
    tol = cfg_fit["boundary_tol"]
    act = _active_coords(pm, x, tol)
    idx = np.flatnonzero(act)
    N = ds.Y.shape[0]
    G = len(templates)
    pc = pair_counts(ds.Y, ds.template_id, G)
    obj = Objective(pm, templates, pc)
    Hm = np.zeros((len(idx), len(idx)))
    for a, i in enumerate(idx):
        h = 1e-5 * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        Hm[a] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[idx] * obj.scale / N          # d(-mean-normalised)/dx = -grad ll
    Hm = 0.5 * (Hm + Hm.T)                                                          # = -(1/N) d2 ll
    th = pm.x_to_theta(x)
    S = learner_scores_nat(th, templates, ds.Y, ds.template_id) @ pm.jacobian(x)
    S = S[:, idx]
    Jm = (S - S.mean(0)).T @ (S - S.mean(0)) / N
    out = {"status": "ok", "active": [pm.names[i] for i in idx], "inactive": [pm.names[i] for i in range(pm.n) if not act[i]],
           "H_min_eig": float(np.linalg.eigvalsh(Hm).min()), "H_cond": float(np.linalg.cond(Hm))}
    if out["H_min_eig"] <= 0:
        out["status"] = "unavailable"; out["reason"] = "sensitivity matrix not positive definite"
        return out
    Hinv = np.linalg.inv(Hm)
    V = Hinv @ Jm @ Hinv / N
    Vfull = np.zeros((pm.n, pm.n)); Vfull[np.ix_(idx, idx)] = V
    Jn = pm.jacobian(x)
    Vnat = Jn @ Vfull @ Jn.T
    ests = th.to_nat()
    res = {}
    for j, name in enumerate(SCALAR_NAMES):
        col = pm.names.index(name) if name in pm.names else None
        if col is None or not act[col]:
            continue
        se = float(np.sqrt(max(Vnat[j, j], 0.0)))
        est = float(ests[j])
        if name in ("tau_F", "tau_R"):
            lo, hi = est * np.exp(-Z975 * se / est), est * np.exp(Z975 * se / est)
        elif name == "phi":
            sx = np.sqrt(max(Vfull[col, col], 0.0)); lo = 1 / (1 + np.exp(-(x[col] - Z975 * sx))); hi = 1 / (1 + np.exp(-(x[col] + Z975 * sx)))
        elif name.startswith("sigma2"):
            lo, hi = est * np.exp(-Z975 * se / est), est * np.exp(Z975 * se / est)   # log-scale interval for a variance > 0
        else:
            lo, hi = est - Z975 * se, est + Z975 * se
        res[name] = {"estimate": est, "se": se, "ci95": [float(lo), float(hi)]}
    out["params"] = res
    return out


def lboot_replicate(fit: dict, templates: list[Template], ds: Dataset, cfg_fit: dict, K: int, b: int,
                    seed_keys: tuple, master_seed: int) -> dict:
    """One learner-bootstrap replicate: resample whole learners, refit the same model from the full-sample estimate."""
    rng = rng_for(master_seed, "learner_bootstrap", fit["model"], *seed_keys, b)
    N, G = ds.Y.shape[0], len(templates)
    ii = rng.integers(0, N, size=N)
    pc = pair_counts(ds.Y[ii], ds.template_id[ii], G)
    f = fit_model(fit["model"], templates, pc, dict(cfg_fit, n_starts=2), K, seed_keys + ("lb", b), master_seed,
                  warm=Theta.from_dict(fit["theta"]))
    if f["status"] == "failed":
        return {"b": b, "failed": True}
    return {"b": b, "failed": False, "theta": f["theta"], "flags": f["flags"], "converged": f["converged"], "ll": f["ll"]}


def lboot_summary(reps: list[dict], B_requested: int) -> dict:
    ok = [r for r in reps if not r["failed"]]
    arr = {n: np.array([r["theta"][n] for r in ok]) for n in SCALAR_NAMES} if ok else {}
    return {"B": B_requested, "n_ok": len(ok), "n_failed": len(reps) - len(ok),
            "sd": {n: float(v.std(ddof=1)) for n, v in arr.items() if len(v) > 1},
            "mean": {n: float(v.mean()) for n, v in arr.items() if len(v)}}


def learner_bootstrap(fit, templates, ds, cfg_fit, K, B, seed_keys, master_seed) -> dict:
    t0 = time.time()
    reps = [lboot_replicate(fit, templates, ds, cfg_fit, K, b, seed_keys, master_seed) for b in range(B)]
    return {**lboot_summary(reps, B), "runtime": time.time() - t0, "replicates": reps}


def null_config(cfg: dict) -> dict:
    """Scenario config with the clean (fitted-model) DGP options, used to simulate from the fitted null."""
    cfg0 = copy.deepcopy(cfg)
    cfg0["dgp"] = {"session_start_corr": 0.0, "error_jump": 0.0, "gain_dist": "normal", "gain_cv": 0.6, "gain_corr_m0": 0.5}
    cfg0["scenario"] = dict(cfg["scenario"], violations=[])
    return cfg0


def null_replicate(fit_b1: dict, templates: list[Template], cfg: dict, N: int, b: int, seed_keys: tuple,
                   master_seed: int) -> dict:
    """One parametric-bootstrap replicate from the fitted B1 null: simulate, then repeat the full B1 and B2 searches."""
    K, G = cfg["design"]["n_skills"], len(templates)
    t0 = time.time()
    sim = simulate(null_config(cfg), N, seed_keys + ("null", b), master_seed, templates, theta=Theta.from_dict(fit_b1["theta"]))
    pc = pair_counts(sim.Y, sim.template_id, G)
    f1 = fit_model("B1", templates, pc, cfg["fit"], K, seed_keys + ("null", b), master_seed)
    f2 = fit_model("B2", templates, pc, cfg["fit"], K, seed_keys + ("null", b), master_seed,
                   warm=Theta.from_dict(f1["theta"]) if f1["status"] != "failed" else None, null_fit=f1)
    if f1["status"] == "failed" or f2["status"] == "failed":
        return {"b": b, "failed": True, "runtime": time.time() - t0}
    return {"b": b, "failed": False, "clr": float(2.0 * (f2["ll"] - f1["ll"])), "sigma2_F": f2["theta"]["sigma2_F"],
            "tau_F": f2["theta"]["tau_F"], "flags1": f1["flags"], "flags2": f2["flags"], "runtime": time.time() - t0}


def null_summary(clr_obs: float, reps: list[dict], B_requested: int, alpha=0.05) -> dict:
    ok = [r for r in reps if not r["failed"]]
    clr = np.array([r["clr"] for r in ok])
    n_ok = len(clr)
    p = (1.0 + float((clr >= clr_obs).sum())) / (n_ok + 1.0) if n_ok else float("nan")
    return {"statistic": "composite LR 2[l(B2)-l(B1)]", "clr_observed": float(clr_obs), "B": B_requested, "n_ok": n_ok,
            "n_failed": len(reps) - n_ok, "p_value": p, "alpha": alpha, "reject_at_alpha": bool(p <= alpha) if n_ok else None,
            "min_attainable_p": 1.0 / (n_ok + 1.0) if n_ok else None,
            "p_mc_se_at_alpha": float(np.sqrt(alpha * (1 - alpha) / max(n_ok, 1))),
            "clr_null_quantiles": {str(q): float(np.quantile(clr, q)) for q in (0.5, 0.9, 0.95, 0.99)} if n_ok else {},
            "share_null_replicates_sigma2F_at_zero": float(np.mean([r["sigma2_F"] <= 1e-6 for r in ok])) if n_ok else None}


def null_test(fit_b1: dict, fit_b2: dict, templates: list[Template], cfg: dict, N: int, B: int, seed_keys: tuple,
              master_seed: int, alpha=0.05) -> dict:
    """Parametric-bootstrap test of sigma2_F = 0 (statistic: composite LR, B2 vs B1) with full nuisance re-search."""
    t0 = time.time()
    reps = [null_replicate(fit_b1, templates, cfg, N, b, seed_keys, master_seed) for b in range(B)]
    out = null_summary(2.0 * (fit_b2["ll"] - fit_b1["ll"]), reps, B, alpha)
    out.update(runtime=time.time() - t0, replicates=reps)
    return out
