"""Tests for the pre-freeze corrections C6-C8 (decisions D23-D25)."""
import numpy as np

from kt_trial.inference import variance_wald_ci
from kt_trial.runner import expand_jobs
from kt_trial.summarize import _bias_verdict, pre_registered


def test_c6_variance_ci_na_near_boundary():
    assert variance_wald_ci(0.05, 0.03) is None                    # est <= 2*SE
    assert variance_wald_ci(0.06, 0.03) is None                    # boundary case: est == 2*SE
    lo, hi = variance_wald_ci(0.16, 0.04)
    assert 0 < lo < 0.16 < hi and np.isclose(np.sqrt(lo * hi), 0.16)      # geometric symmetry (log scale)


def test_c7_compact_specs_and_per_dataset_B():
    cfg = {"stage": "confirmatory", "scenarios": ["S1"], "N_list": [300], "replications": 2, "models": ["B0"],
           "null_bootstrap": {"B": 19, "datasets": [
               {"scenarios": ["S2", "S8n"], "N_list": [300, 1000], "rep_range": [0, 10], "B": 99},
               {"scenarios": ["S1", "S8"], "N_list": [300, 1000], "rep_range": [0, 10]}]},
           "learner_bootstrap": {"B": 50, "datasets": [{"scenario": "S1", "N": 1000, "rep": 0}]}}
    j = expand_jobs(cfg)["phase2"]
    nulls = [x for x in j if x["kind"] == "null_rep"]
    assert len(nulls) == 40 * 99 + 40 * 19 == 4720
    assert {x["N"] for x in nulls} == {300, 1000} and max(x["rep"] for x in nulls) == 9
    assert sum(x["scenario"] == "S2" for x in nulls) == 20 * 99 and sum(x["scenario"] == "S8" for x in nulls) == 10 * 2 * 19
    lb = [x for x in j if x["kind"] == "lboot_rep"]
    assert len(lb) == 50 and lb[0]["N"] == 1000
    # old explicit form still works
    old = {**cfg, "null_bootstrap": {"B": 3, "datasets": [{"scenario": "S1", "rep": 0}, {"scenario": "S1", "rep": 1}]}}
    assert len([x for x in expand_jobs(old)["phase2"] if x["kind"] == "null_rep"]) == 6


def test_c8_bias_verdict_boundaries():
    assert _bias_verdict(0.0, 0.01)["verdict"] == "pass"               # CI [-0.0196, 0.0196]
    assert _bias_verdict(0.03, 0.01)["verdict"] == "inconclusive"     # CI [0.0104, 0.0496]
    assert _bias_verdict(0.08, 0.01)["verdict"] == "fail"             # CI [0.0604, 0.0996] disjoint from [-0.04, 0.04]
    assert _bias_verdict(-0.08, 0.01)["verdict"] == "fail"
    assert _bias_verdict(0.0, 0.05)["verdict"] == "inconclusive"      # imprecise -> inconclusive, never pass


def _fit(s2, tau=10.0, err=0.0):
    return {"status": "ok", "theta": {"sigma2_F": s2, "tau_F": tau}, "errors": {"sigma2_F": err}}


def _rep(s2, err, d=0.0, tau=10.0):
    return {"fits": {"B2": _fit(s2, tau, err)}, "prediction": {"pairwise_composite_log_score": {"B2-B1": {"mean": d}}}}


def test_c8_ph_rules_on_synthetic_results():
    rng = np.random.default_rng(1)
    groups = {("S1", 300): [_rep(0.16, e, d=1.0 + 0.1 * e) for e in rng.normal(0.0, 0.01, 20)],
              ("S2", 300): [_rep(0.0, 0.0) for _ in range(10)],
              ("S8n", 300): [_rep(0.05 if i < 3 else 0.0, 0.0, tau=0.1 if i < 3 else 1.0, d=-0.05) for i in range(10)]}
    nt = {}
    for i in range(10):
        nt[f"S1|N=300|rep={i}"] = {"reject_at_alpha": True}
        nt[f"S2|N=300|rep={i}"] = {"reject_at_alpha": False}
        nt[f"S8n|N=300|rep={i}"] = {"reject_at_alpha": i < 5}         # 5/10 reject -> excess false positives
    out = pre_registered(groups, nt)["PH"]
    assert out["PH1"]["cells"]["N=300"]["verdict"] == "pass"
    assert out["PH2"]["cells"]["N=300"]["k"] == 10
    assert out["PH3"]["verdict"].startswith("no evidence") and out["PH3"]["null_test_rejections"]["k"] == 0
    assert out["PH4"]["verdict"] == "evidence of excess false positives"          # CP lower bound of 5/10 is > 0.05
    assert out["PH4"]["near_white_share"]["k"] == 3 and out["PH4"]["sigma2_F_hat_distribution"]["share_at_zero"] == 0.7
    assert out["PH6"]["S1|N=300"]["positive_ci"] and out["PH6"]["S1|N=300"]["verdict"] == "improvement: yes"
    assert out["PH6"]["S8n|N=300"]["verdict"] == "spurious superiority: not shown"
    # exactly at the threshold: 4/20 rejections -> lower CP bound just above 0.05 (evidence); 3/20 -> none
    from kt_trial.summarize import clopper_pearson
    assert clopper_pearson(4, 20)[0] > 0.05 and clopper_pearson(3, 20)[0] < 0.05
