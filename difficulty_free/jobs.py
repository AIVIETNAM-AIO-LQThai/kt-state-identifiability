"""Job bodies for Experiment 3: `fit` (known / calibrated / free difficulties on the SAME dataset) and `null_rep`
(one parametric-bootstrap replicate of the boundary-aware composite-LR test of sigma2_F = 0 for an arm).

Arms: known = true difficulties (Experiment-1 estimator); cal = difficulties with calibration error N(0, cal_sd^2) treated as known
(own RNG namespace); free = difficulties estimated jointly (66 coordinates for B2).
"""
from __future__ import annotations

import copy
import time
from pathlib import Path

import numpy as np

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import generating_theta_dict, load_scenario, rng_for
from kt_trial.evaluate import recovery_errors
from kt_trial.fit import fit_model
from kt_trial.inference import null_config, null_replicate
from kt_trial.moments import Theta
from kt_trial.runner import read_json
from kt_trial.schedule import build_templates

from .audit import difficulties
from .fit import fit_free
from .freeb import item_ids
from .model import with_difficulties
from .simulator import draw_lambda, simulate_lambda

N_ITEMS = 48


def scenario_cfg_from(spec: dict, n_starts: int | None = None) -> dict:
    cfg = copy.deepcopy(load_scenario(spec["base"]))
    if "tau_F" in spec:
        cfg["generating"]["tau_F"] = float(spec["tau_F"])
    cfg["scenario"] = dict(cfg["scenario"], id=spec["id"])
    if n_starts:
        cfg["fit"] = dict(cfg["fit"], n_starts=n_starts)
    return cfg


def spec_of(stage: dict, sid: str) -> dict:
    return next(s for s in stage["scenarios"] if s["id"] == sid)


def make_dataset(stage: dict, spec: dict, N: int, rep: int):
    cfg = scenario_cfg_from(spec, stage.get("n_starts"))
    ts = build_templates(cfg)
    ids = item_ids(ts, cfg["design"]["items_per_skill"])
    cv = float(spec.get("lambda_cv", 0.0))
    lam = draw_lambda(stage["master_seed"], spec["id"], N, rep, cv, N_ITEMS) if cv > 0 else None
    ds = simulate_lambda(cfg, N, ("data", spec["id"], N, rep), stage["master_seed"], ts, lam=lam, ids=ids)
    return cfg, ts, ids, ds


def calibrated_difficulties(stage: dict, sid: str, N: int, rep: int, b_true: np.ndarray) -> np.ndarray:
    """b + N(0, cal_sd^2): own RNG namespace, never touches the response stream."""
    return b_true + rng_for(stage["master_seed"], "cal", sid, N, rep).normal(0.0, stage["cal_sd"], size=b_true.shape)


def _summ(f: dict, truth: Theta | None = None, b_true=None) -> dict:
    keep = ("model", "arm", "status", "ll", "runtime", "flags", "certificate", "start_agreement", "boundary_hits", "converged",
            "n_params", "n_starts", "n_good_starts")
    out = {k: f[k] for k in keep if k in f}
    if f.get("status") != "failed":
        out["theta"] = f["theta"]
        if truth is not None:
            out["errors"] = recovery_errors(Theta.from_dict(f["theta"]), truth)
        if "b" in f and b_true is not None:
            e = np.array(f["b"]) - b_true
            out["b_rmse"], out["b_bias"] = float(np.sqrt((e ** 2).mean())), float(e.mean())
            out["b"] = f["b"]
    return out


def _known_pair(ts, pc, cfg, K, skey, ms):
    f1 = fit_model("B1", ts, pc, cfg["fit"], K, skey, ms)
    f2 = fit_model("B2", ts, pc, cfg["fit"], K, skey, ms, warm=Theta.from_dict(f1["theta"]) if f1["status"] != "failed" else None, null_fit=f1)
    return f1, f2


def run_fit_job(stage: dict, sid: str, N: int, rep: int) -> dict:
    spec = spec_of(stage, sid)
    cfg, ts, ids, ds = make_dataset(stage, spec, N, rep)
    K, G, ms = cfg["design"]["n_skills"], len(ts), stage["master_seed"]
    truth = Theta.from_dict(generating_theta_dict(cfg))
    b_true = difficulties(ts, ids, N_ITEMS)
    pc = pair_counts(ds.Y, ds.template_id, G)
    skey = (sid, N, rep)
    arms = stage["arms"].get(sid, ["known", "cal", "free"])
    res = {"scenario": sid, "N": N, "rep": rep, "truth": truth.to_dict(), "spec": spec, "arms": {}, "data_meta": ds.meta}
    if "known" in arms:
        f1, f2 = _known_pair(ts, pc, cfg, K, skey + ("known",), ms)
        res["arms"]["known"] = {"B1": _summ(f1, truth), "B2": _summ(f2, truth)}
    if "cal" in arms:
        b_cal = calibrated_difficulties(stage, sid, N, rep, b_true)
        f1, f2 = _known_pair(with_difficulties(ts, ids, b_cal), pc, cfg, K, skey + ("cal",), ms)
        res["arms"]["cal"] = {"B1": _summ(f1, truth), "B2": _summ(f2, truth), "b_cal_rmse": float(np.sqrt(((b_cal - b_true) ** 2).mean()))}
    if "free" in arms:
        f1 = fit_free("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("free",), ms)
        f2 = fit_free("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, skey + ("free",), ms,
                      warm=(Theta.from_dict(f1["theta"]), f1["b"]) if f1["status"] != "failed" else None, null_fit=f1)
        res["arms"]["free"] = {"B1": _summ(f1, truth, b_true), "B2": _summ(f2, truth, b_true)}
        res["arms"]["free"]["_b1_for_null"] = {k: f1[k] for k in ("status", "theta", "b", "ll", "certificate") if k in f1}
    return res


def null_free_replicate(fit_b1: dict, ts, cfg, ids, N: int, b: int, seed_keys: tuple, ms: int) -> dict:
    """Parametric-bootstrap replicate from the fitted B1-free null: simulate with its theta and difficulties, then repeat the full
    B1-free and B2-free searches (as in Experiment 1, but with the difficulties re-estimated in every replicate)."""
    K, G = cfg["design"]["n_skills"], len(ts)
    t0 = time.time()
    th, bh = Theta.from_dict(fit_b1["theta"]), np.array(fit_b1["b"])
    sim = simulate_lambda(null_config(cfg), N, seed_keys + ("null", b), ms, with_difficulties(ts, ids, bh), theta=th)
    pc = pair_counts(sim.Y, sim.template_id, G)
    f1 = fit_free("B1", ts, pc, cfg["fit"], K, ids, N_ITEMS, seed_keys + ("null", b), ms)
    f2 = fit_free("B2", ts, pc, cfg["fit"], K, ids, N_ITEMS, seed_keys + ("null", b), ms,
                  warm=(Theta.from_dict(f1["theta"]), f1["b"]) if f1["status"] != "failed" else None, null_fit=f1)
    if f1["status"] == "failed" or f2["status"] == "failed":
        return {"b": b, "failed": True, "runtime": time.time() - t0}
    return {"b": b, "failed": False, "clr": float(2.0 * (f2["ll"] - f1["ll"])), "sigma2_F": f2["theta"]["sigma2_F"],
            "tau_F": f2["theta"]["tau_F"], "flags1": f1["flags"], "flags2": f2["flags"], "runtime": time.time() - t0}


def run_null_job(stage: dict, results_dir: str, sid: str, N: int, rep: int, arm: str, b: int) -> dict:
    spec = spec_of(stage, sid)
    cfg, ts, ids, _ = make_dataset_templates(stage, spec)
    ms = stage["master_seed"]
    fr = read_json(Path(results_dir) / "jobs" / f"fit__{sid}__N{N}__r{rep}.json")["result"]
    skey = (sid, N, rep)
    if arm == "free":
        return null_free_replicate(fr["arms"]["free"]["_b1_for_null"], ts, cfg, ids, N, b, skey + ("free",), ms)
    ts_arm = ts if arm == "known" else with_difficulties(ts, ids, calibrated_difficulties(stage, sid, N, rep, difficulties(ts, ids, N_ITEMS)))
    return null_replicate(fr["arms"][arm]["B1"], ts_arm, cfg, N, b, skey + (arm,), ms)


def make_dataset_templates(stage: dict, spec: dict):
    cfg = scenario_cfg_from(spec, stage.get("n_starts"))
    ts = build_templates(cfg)
    return cfg, ts, item_ids(ts, cfg["design"]["items_per_skill"]), None
