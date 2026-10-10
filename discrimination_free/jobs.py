"""Job bodies for Experiment 4: `fit` (1PL-free and 2PL on the SAME dataset) and `warp` (observed CLR T and one bootstrap CLR T* for each
estimator on one fresh null dataset). The estimand is sigma2_F* = g^2 sigma2_F, with g the geometric mean of the replication's true
discriminations (identification: geometric mean of lambda-hat = 1)."""
from __future__ import annotations

import time

import numpy as np

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import generating_theta_dict
from kt_trial.inference import null_config
from kt_trial.moments import Theta
from difficulty_free import jobs as DJ
from difficulty_free.audit import difficulties
from difficulty_free.fit import fit_free
from difficulty_free.model import with_difficulties
from difficulty_free.simulator import draw_lambda, simulate_lambda

from . import twopl
from .fit import fit_2pl

N_ITEMS = 48


def truth_2pl(cfg: dict, stage: dict, spec: dict, N: int, rep: int) -> dict:
    th = Theta.from_dict(generating_theta_dict(cfg))
    cv = float(spec.get("lambda_cv", 0.0))
    lam = draw_lambda(stage["master_seed"], spec["id"], N, rep, cv, N_ITEMS) if cv > 0 else np.ones(N_ITEMS)
    th_star, lam_star, g = twopl.normalise(th, lam)
    return {"theta": th, "lam": lam, "g": g, "sigma2_F_star": float(th_star.sigma2_F), "lam_star": lam_star}


def _lambda_recovery(lam_hat, lam_true) -> dict:
    lh, lt = np.log(np.asarray(lam_hat, float)), np.log(np.asarray(lam_true, float))
    e = (lh - lh.mean()) - (lt - lt.mean())
    return {"rmse_centred_log_lambda": float(np.sqrt((e ** 2).mean())), "bias_centred_log_lambda": float(e.mean()),
            "corr": float(np.corrcoef(lh, lt)[0, 1]) if lt.std() > 0 and lh.std() > 0 else None}


def _summ(f: dict, tr: dict, b_true) -> dict:
    keep = ("model", "arm", "status", "ll", "runtime", "flags", "certificate", "start_agreement", "boundary_hits", "converged", "n_params",
            "n_starts", "n_good_starts", "n_extreme_lambda", "n_polished", "polish_line_search_failures")
    out = {k: f[k] for k in keep if k in f}
    if f.get("status") != "failed":
        out["theta"] = f["theta"]
        e = np.array(f["b"]) - b_true
        out["b_rmse"] = float(np.sqrt((e ** 2).mean()))
        out["sigma2_F_error_vs_star"] = float(f["theta"]["sigma2_F"] - tr["sigma2_F_star"])
        if "lam" in f:
            out["lambda_recovery"] = _lambda_recovery(f["lam"], tr["lam"])
            out["lam"] = f["lam"]
        out["b"] = f["b"]
    return out


def run_fit_job(stage: dict, sid: str, N: int, rep: int) -> dict:
    spec = DJ.spec_of(stage, sid)
    cfg, ts, ids, ds = DJ.make_dataset(stage, spec, N, rep)
    K, G, ms = cfg["design"]["n_skills"], len(ts), stage["master_seed"]
    tr = truth_2pl(cfg, stage, spec, N, rep)
    b_true = difficulties(ts, ids, N_ITEMS)
    pc = pair_counts(ds.Y, ds.template_id, G)
    skey = (sid, N, rep)
    res = {"scenario": sid, "N": N, "rep": rep, "spec": spec, "g": tr["g"], "sigma2_F_true": tr["theta"].sigma2_F,
           "sigma2_F_star": tr["sigma2_F_star"], "lambda_cv_realised": float(np.std(tr["lam"]) / np.mean(tr["lam"])), "arms": {},
           "data_meta": ds.meta}
    f1 = fit_free("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("free1",), ms)
    f2 = fit_free("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("free1",), ms,
                  warm=(Theta.from_dict(f1["theta"]), f1["b"]) if f1["status"] != "failed" else None, null_fit=f1)
    res["arms"]["free1"] = {"B1": _summ(f1, tr, b_true), "B2": _summ(f2, tr, b_true)}
    g1 = fit_2pl("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("2pl",), ms)
    g2 = fit_2pl("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("2pl",), ms,
                 warm=(Theta.from_dict(g1["theta"]), g1["b"], g1["lam"]) if g1["status"] != "failed" else None, null_fit=g1)
    res["arms"]["twopl"] = {"B1": _summ(g1, tr, b_true), "B2": _summ(g2, tr, b_true)}
    return res


def null_2pl_replicate(fit_b1: dict, ts, cfg, ids, N: int, b: int, seed_keys: tuple, ms: int) -> dict:
    """One parametric-bootstrap replicate from the fitted B1-2PL null (theta, difficulties and discriminations), then the full B1-2PL and
    B2-2PL searches."""
    K, G = cfg["design"]["n_skills"], len(ts)
    t0 = time.time()
    th, bh, lh = Theta.from_dict(fit_b1["theta"]), np.array(fit_b1["b"]), np.array(fit_b1["lam"])
    sim = simulate_lambda(null_config(cfg), N, seed_keys + ("null", b), ms, with_difficulties(ts, ids, bh), lam=lh, ids=ids, theta=th)
    pc = pair_counts(sim.Y, sim.template_id, G)
    f1 = fit_2pl("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, seed_keys + ("null", b), ms)
    f2 = fit_2pl("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, seed_keys + ("null", b), ms,
                 warm=(Theta.from_dict(f1["theta"]), f1["b"], f1["lam"]) if f1["status"] != "failed" else None, null_fit=f1)
    if f1["status"] == "failed" or f2["status"] == "failed":
        return {"b": b, "failed": True, "runtime": time.time() - t0}
    return {"b": b, "failed": False, "clr": float(2.0 * (f2["ll"] - f1["ll"])), "sigma2_F": f2["theta"]["sigma2_F"],
            "tau_F": f2["theta"]["tau_F"], "flags2": f2["flags"], "converged": bool(f1["converged"] and f2["converged"]),
            "runtime": time.time() - t0}


def run_warp_job(stage: dict, sid: str, N: int, rep: int) -> dict:
    """Warp-speed unit on one fresh null dataset: for each estimator in stage['warp']['estimators'] the observed CLR T and one bootstrap CLR T*."""
    spec = DJ.spec_of(stage, sid)
    cfg, ts, ids, ds = DJ.make_dataset(stage, spec, N, rep)
    K, G, ms = cfg["design"]["n_skills"], len(ts), stage["master_seed"]
    pc = pair_counts(ds.Y, ds.template_id, G)
    out = {"scenario": sid, "N": N, "rep": rep}
    for est in stage["warp"].get("estimators", {}).get(sid, ["twopl"]):
        e = {}
        if est == "free1":
            skey = (sid, N, rep, "free")
            f1 = fit_free("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms)
            f2 = fit_free("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms,
                          warm=(Theta.from_dict(f1["theta"]), f1["b"]) if f1["status"] != "failed" else None, null_fit=f1)
            star = (DJ.null_free_replicate(f1, ts, cfg, ids, N, 0, skey, ms) if f1["status"] != "failed" else {"failed": True})
        else:
            skey = (sid, N, rep, "2pl")
            f1 = fit_2pl("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms)
            f2 = fit_2pl("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms,
                         warm=(Theta.from_dict(f1["theta"]), f1["b"], f1["lam"]) if f1["status"] != "failed" else None, null_fit=f1)
            star = (null_2pl_replicate(f1, ts, cfg, ids, N, 0, skey, ms) if f1["status"] != "failed" else {"failed": True})
        e["fit_failed"] = bool(f1["status"] == "failed" or f2["status"] == "failed")
        if not e["fit_failed"]:
            e.update(T=float(2.0 * (f2["ll"] - f1["ll"])), sigma2_F=f2["theta"]["sigma2_F"], tau_F=f2["theta"]["tau_F"], flags_B2=f2["flags"],
                     converged=bool(f1["converged"] and f2["converged"]), runtime_fit=f1["runtime"] + f2["runtime"],
                     ridge_converged=bool("converged_on_ridge" in f2["flags"]))
            e["star_failed"] = bool(star.get("failed"))
            if not e["star_failed"]:
                e.update(T_star=star["clr"], sigma2_F_star_boot=star["sigma2_F"], tau_F_star=star["tau_F"], runtime_star=star["runtime"],
                         star_converged=bool(star.get("converged", "not_converged" not in star["flags2"])),
                         star_ridge_converged=bool("converged_on_ridge" in star["flags2"]))
        out[est] = e
    return out
