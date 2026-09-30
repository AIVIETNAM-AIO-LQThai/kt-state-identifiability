"""Regression tests for the H1-review corrections (D19: absolute stopping rule; C2: no NA-truth statistics)."""
import json

import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import generating_theta_dict, load_scenario
from kt_trial.fit import Objective, effective_gtol, fit_model
from kt_trial.models import ParamMap
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate
from kt_trial.summarize import summarize, truth_status


def test_stopping_rule_is_n_invariant_in_absolute_units():
    cfg = load_scenario("S1")
    ts = build_templates(cfg)
    fit_cfg = cfg["fit"]
    for N in (64, 300, 1000):
        ds = simulate(cfg, N, ("stop",), 1, ts)
        obj = Objective(ParamMap("B2", 4), ts, pair_counts(ds.Y, ds.template_id, 8))
        assert effective_gtol(fit_cfg, obj.scale) * obj.scale == pytest.approx(fit_cfg["gtol_abs"])
    assert fit_cfg["ftol"] <= 1e-14 and fit_cfg["max_iter"] >= 3000


@pytest.mark.slow
def test_all_b2_starts_reach_the_same_optimum_on_fixed_n300_dataset():
    """The dataset on which the old per-pair rule stopped a start 79 log-lik units short (H1 review, C1)."""
    cfg = load_scenario("S1")
    ts = build_templates(cfg)
    ms = 20261001
    ds = simulate(cfg, 300, ("data", "S1", 300, 0), ms, ts)
    pc = pair_counts(ds.Y, ds.template_id, 8)
    f1 = fit_model("B1", ts, pc, cfg["fit"], 4, ("S1", 300, 0), ms)
    from kt_trial.moments import Theta
    f2 = fit_model("B2", ts, pc, cfg["fit"], 4, ("S1", 300, 0), ms, warm=Theta.from_dict(f1["theta"]), null_fit=f1)
    ll = np.array([r["ll"] for r in f2["runs"] if r.get("ok")])
    assert ll.max() - ll.min() < 0.01, ll - ll.max()
    assert f2["start_agreement"]["n_starts_at_best"] == 5 and f2["start_agreement"]["secondary_optima"] == 0
    assert f2["converged"] and f2["grad_norm"] < cfg["fit"]["grad_flag_abs"]
    assert abs(f2["theta"]["sigma2_F"] - 0.187) < 0.01


def test_truth_status_marks_boundary_and_inactive_truths():
    s2 = truth_status(generating_theta_dict(load_scenario("S2")) | {})
    assert s2["sigma2_F"] is not None and s2["tau_F"] is not None and s2["phi"] is None
    s3 = truth_status(generating_theta_dict(load_scenario("S3")))
    assert s3["sigma2_r"] is not None and s3["tau_R"] is not None and s3["r_bar"] is None and s3["sigma2_F"] is None
    s1 = truth_status(generating_theta_dict(load_scenario("S1")))
    assert all(v is None for v in s1.values())
    s8n = truth_status(generating_theta_dict(load_scenario("S8n")))
    assert s8n["sigma2_F"] is not None and s8n["tau_F"] is not None


def _fake_fit(theta, ll=0.0):
    return {"status": "ok", "converged": True, "runtime": 1.0, "theta": theta, "ll": ll, "flags": [],
            "boundary_hits": [], "grad_inf_abs": 1e-4, "grad_norm": 1e-4,
            "start_agreement": {"n_starts_at_best": 5, "secondary_optima": 0},
            "errors": {}}


def test_summary_never_reports_bias_or_coverage_for_na_truths(tmp_path):
    cfg = load_scenario("S2")
    truth = {**{k: v for k, v in generating_theta_dict(cfg).items() if k != "Sigma_M"},
             "Sigma_M": generating_theta_dict(cfg)["Sigma_M"].tolist()}
    fits, sw = {}, {}
    for m in ("B0", "B1", "B2"):
        th = dict(truth, sigma2_F=0.02 if m == "B2" else 0.0, tau_F=7.0)
        f = _fake_fit(th)
        f["errors"] = {k: th[k] - truth[k] for k in truth if k != "Sigma_M"}
        fits[m] = f
    sw["B2"] = {"status": "ok", "params": {n: {"estimate": truth[n], "se": 0.01, "ci95": [truth[n] - 1, truth[n] + 1]}
                                            for n in ("alpha_bar", "phi", "sigma2_F", "tau_F")}}
    res = {"scenario": "S2", "N_fit": 30, "N_heldout": 30, "N_total_generated": 60, "rep": 0, "truth": truth,
           "data_meta": {}, "fits": fits, "sandwich": sw, "prediction": {}, "violations": []}
    (tmp_path / "jobs").mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"stage": "smoke", "config_hash": "h", "code_hash": "c"}))
    (tmp_path / "jobs" / "fit__S2__N30__r0.json").write_text(json.dumps(
        {"job_id": "fit__S2__N30__r0", "job": {"kind": "fit", "scenario": "S2", "N": 30, "rep": 0}, "status": "ok",
         "result": res, "runtime": 1.0}))
    s = summarize(tmp_path)
    b2 = s["cells"]["S2|N=30"]["models"]["B2"]
    for n in ("sigma2_F", "tau_F"):
        assert "na_reason" in b2["params"][n] and "bias" not in b2["params"][n]
        assert n not in b2["sandwich_coverage"]
    assert "bias" in b2["params"]["alpha_bar"] and "alpha_bar" in b2["sandwich_coverage"]
    cov = b2["sandwich_coverage"]["alpha_bar"]
    assert cov["cond_n"] == 1 and cov["uncond_n"] == 1
    assert b2["tau_F_when_sigma2F_positive"] is None
    assert "NA (" in (tmp_path / "summary.md").read_text(encoding="utf-8")
