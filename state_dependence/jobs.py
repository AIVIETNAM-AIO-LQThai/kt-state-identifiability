"""Job bodies for Experiment 5: `fit` (2PL B1 and B2 on one dataset, plus the carry-over score test at each fit) and `warp` (the same, plus one
parametric-bootstrap replicate T* from the fitted B1 null, for the cell whose F-test margin is thin: E4, X5-D06).

Data: difficulty_free.jobs.scenario_cfg_from(spec) -> state_dependence.simulator.simulate_feedback (lambda == 1; optional feedback {kappa, tau_D}
in the scenario spec). Estimator: discrimination_free.fit.fit_2pl (with the X4-D08/D09 polish). The estimand sigma2_F* equals the generating
sigma2_F because lambda == 1 (g = 1).
"""
from __future__ import annotations

import numpy as np

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import generating_theta_dict
from kt_trial.moments import Theta
from kt_trial.schedule import build_templates
from difficulty_free import jobs as DJ
from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from discrimination_free.fit import fit_2pl
from discrimination_free.jobs import _summ, null_2pl_replicate

from . import diagnostic as DG
from .simulator import simulate_feedback

N_ITEMS = 48
KEEP = ("stat", "p", "eta_hat", "delta", "U", "info", "var_per_learner")


def make_dataset(stage: dict, spec: dict, N: int, rep: int):
    cfg = DJ.scenario_cfg_from(spec, stage.get("n_starts"))
    ts = build_templates(cfg)
    ids = item_ids(ts, cfg["design"]["items_per_skill"])
    ds = simulate_feedback(cfg, N, ("data", spec["id"], N, rep), stage["master_seed"], ts, lam=None, ids=ids, feedback=spec.get("feedback"))
    return cfg, ts, ids, ds


def _diag(f: dict, ts, ids, ds, cfg, taus) -> dict:
    if f.get("status") == "failed":
        return {"error": "fit failed"}
    try:
        out = DG.eta_test(f, ts, ids, ds.Y, ds.template_id, cfg["fit"], taus, N_ITEMS, cfg["design"]["n_skills"])
    except Exception as e:                                                  # recorded as data, never silently dropped
        return {"error": repr(e)}
    return {"n_active": out["n_active"], "by_tau_x": {f"{t:g}": {k: out[t][k] for k in KEEP} for t in taus}}


def _fit_pair(stage: dict, spec: dict, N: int, rep: int, tag: str):
    cfg, ts, ids, ds = make_dataset(stage, spec, N, rep)
    K, G, ms = cfg["design"]["n_skills"], len(ts), stage["master_seed"]
    pc = pair_counts(ds.Y, ds.template_id, G)
    skey = (spec["id"], N, rep, tag)
    f1 = fit_2pl("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms)
    f2 = fit_2pl("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey, ms,
                 warm=(Theta.from_dict(f1["theta"]), f1["b"], f1["lam"]) if f1["status"] != "failed" else None, null_fit=f1)
    return cfg, ts, ids, ds, f1, f2, skey


def _record(stage: dict, spec: dict, N: int, rep: int, cfg, ts, ids, ds, f1, f2) -> dict:
    taus = list(stage["taus_x"])
    th = Theta.from_dict(generating_theta_dict(cfg))
    tr = {"sigma2_F_star": float(th.sigma2_F), "lam": np.ones(N_ITEMS)}
    b_true = difficulties(ts, ids, N_ITEMS)
    res = {"scenario": spec["id"], "N": N, "rep": rep, "spec": spec, "sigma2_F_star": tr["sigma2_F_star"],
           "arms": {"B1": _summ(f1, tr, b_true), "B2": _summ(f2, tr, b_true)}, "data_meta": ds.meta,
           "diag": {"B2": _diag(f2, ts, ids, ds, cfg, taus), "B1": _diag(f1, ts, ids, ds, cfg, taus)}}
    if f1["status"] != "failed" and f2["status"] != "failed":
        res["T"] = float(2.0 * (f2["ll"] - f1["ll"]))
    return res


def run_fit_job(stage: dict, sid: str, N: int, rep: int) -> dict:
    spec = DJ.spec_of(stage, sid)
    cfg, ts, ids, ds, f1, f2, skey = _fit_pair(stage, spec, N, rep, "fit")
    return _record(stage, spec, N, rep, cfg, ts, ids, ds, f1, f2)


def run_warp_job(stage: dict, sid: str, N: int, rep: int) -> dict:
    """Fit job plus one bootstrap replicate from the fitted B1 null (feedback-free simulation, as discrimination_free.jobs.null_2pl_replicate)."""
    spec = DJ.spec_of(stage, sid)
    cfg, ts, ids, ds, f1, f2, skey = _fit_pair(stage, spec, N, rep, "warp")
    res = _record(stage, spec, N, rep, cfg, ts, ids, ds, f1, f2)
    res["fit_failed"] = bool(f1["status"] == "failed" or f2["status"] == "failed")
    if not res["fit_failed"]:
        res.update(sigma2_F=f2["theta"]["sigma2_F"], tau_F=f2["theta"]["tau_F"], flags_B2=f2["flags"],
                   converged=bool(f1["converged"] and f2["converged"]), ridge_converged=bool("converged_on_ridge" in f2["flags"]),
                   runtime_fit=f1["runtime"] + f2["runtime"])
        star = null_2pl_replicate(f1, ts, cfg, ids, N, 0, skey, stage["master_seed"])
        res["star_failed"] = bool(star.get("failed"))
        if not res["star_failed"]:
            res.update(T_star=star["clr"], sigma2_F_star_boot=star["sigma2_F"], tau_F_star=star["tau_F"], runtime_star=star["runtime"],
                       star_converged=bool(star.get("converged", "not_converged" not in star["flags2"])),
                       star_ridge_converged=bool("converged_on_ridge" in star["flags2"]))
    return res
