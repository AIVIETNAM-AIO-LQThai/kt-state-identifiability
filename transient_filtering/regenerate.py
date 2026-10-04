"""Regeneration of the Experiment-1 datasets from their recorded seeds, with fingerprint checks against the saved fits.

Experiment 1 drew `data` and `heldout` streams with seed keys (kind, scenario, N, rep) under master seed 20261201. Regeneration
is deterministic only within one numpy/LAPACK build (the generating Sigma_M has a repeated eigenvalue, so the SVD-based
multivariate normal sampler is build-sensitive); the fingerprint check below decides whether a given environment reproduces
the saved data. Estimators never receive the latent truth; it is retained here only for evaluation.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from kt_trial.composite_likelihood import composite_loglik, pair_counts
from kt_trial.config import generating_theta_dict, load_yaml
from kt_trial.evaluate import heldout_scores
from kt_trial.moments import Theta
from kt_trial.runner import read_json, scenario_cfg
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


def exp1_stage_cfg(path: str) -> dict:
    return load_yaml(path)


def regenerate(stage_cfg: dict, sid: str, N: int, rep: int, kind: str, keep_latent: bool = True):
    """kind in {'data', 'heldout'}. Returns (cfg, templates, dataset)."""
    cfg = scenario_cfg(stage_cfg, sid)
    ts = build_templates(cfg)
    n = N if kind == "data" else stage_cfg["heldout_N"]
    ds = simulate(cfg, n, (kind, sid, N, rep), stage_cfg["master_seed"], ts, keep_latent=keep_latent)
    return cfg, ts, ds


def load_fit_result(results_dir: str, sid: str, N: int, rep: int) -> dict:
    env = read_json(Path(results_dir) / "jobs" / f"fit__{sid}__N{N}__r{rep}.json")
    if env["status"] != "ok":
        raise RuntimeError(f"Experiment-1 fit job {sid} N={N} rep={rep} did not finish ok")
    return env["result"]


def true_theta(cfg: dict) -> Theta:
    return Theta.from_dict(generating_theta_dict(cfg))


def fingerprint(stage_cfg: dict, results_dir: str, sid: str, N: int, rep: int, rel_tol: float = 1e-9) -> dict:
    """Compare regenerated data with Experiment 1's saved outputs. A mismatch is a provenance finding, not float noise:
    composite counts are integers, so any changed response moves the log-likelihood by O(1)."""
    res = load_fit_result(results_dir, sid, N, rep)
    cfg, ts, ds = regenerate(stage_cfg, sid, N, rep, "data", keep_latent=False)
    _, _, ds_l = regenerate(stage_cfg, sid, N, rep, "data", keep_latent=True)
    pc = pair_counts(ds.Y, ds.template_id, len(ts))
    out = {"scenario": sid, "N": N, "rep": rep, "keep_latent_invariant": bool(np.array_equal(ds.Y, ds_l.Y)
                                                                              and np.array_equal(ds.template_id, ds_l.template_id))}
    real_saved = res["data_meta"]["realised"]
    out["realised_max_abs_diff"] = float(max(abs(real_saved[k] - ds.meta["realised"][k]) for k in real_saved
                                             if real_saved[k] is not None))
    lls = {}
    for m, f in res["fits"].items():
        ll = composite_loglik(Theta.from_dict(f["theta"]), ts, pc, grad=False)[0]
        lls[m] = {"saved": f["ll"], "regenerated": float(ll), "abs_diff": float(abs(ll - f["ll"])),
                  "rel_diff": float(abs(ll - f["ll"]) / abs(f["ll"]))}
    out["loglik"] = lls
    _, tsh, te = regenerate(stage_cfg, sid, N, rep, "heldout", keep_latent=False)
    hs = heldout_scores(Theta.from_dict(res["fits"]["B2"]["theta"]), tsh, te)
    for k, saved in res["prediction"].items():
        out.setdefault("heldout", {})[k] = {"saved": saved["B2"], "regenerated": float(hs[k].mean()),
                                            "abs_diff": float(abs(hs[k].mean() - saved["B2"]))}
    worst = max(max(v["rel_diff"] for v in lls.values()),
                max(v["abs_diff"] / max(abs(v["saved"]), 1e-300) for v in out["heldout"].values()))
    out["worst_relative_difference"] = float(worst)
    out["match"] = bool(worst <= rel_tol and out["keep_latent_invariant"] and out["realised_max_abs_diff"] <= 1e-12)
    return out
