"""Tests of the pre-registered Experiment-3 rules and gates (X3-D12) on synthetic summaries."""
import numpy as np

from difficulty_free.rules import bias_rule, cp, evaluate, false_positive_rule

THREADS = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"}


def _arm(values, converged=1.0, n_failed=0):
    return {"n": len(values), "B2": {"n_failed": n_failed, "converged": converged}, "sigma2F_by_rep": {i: v for i, v in enumerate(values)}}


def _S(cells=None, nulls=None, threads=THREADS, errors=0):
    return {"cells": cells or {}, "null_tests": nulls or {}, "manifest": {"env": {"numpy": "2.5.3", "threads": threads}}, "accounting": {"errors": errors}}


def _null(sid, N, rep, reject, B_ok=39, B_failed=0):
    return f"{sid}|N={N}|rep={rep}|free", {"B_ok": B_ok, "B_failed": B_failed, "reject_at_0.05": reject}


def test_bias_rule_pass_fail_inconclusive():
    rng = np.random.default_rng(0)
    assert bias_rule(0.16 + rng.normal(0, 0.01, 20), 0.16)["verdict"] == "pass"
    assert bias_rule(0.16 + 0.10 + rng.normal(0, 0.01, 20), 0.16)["verdict"] == "fail"
    assert bias_rule(0.16 + 0.04 + rng.normal(0, 0.05, 20), 0.16)["verdict"] == "inconclusive"
    assert bias_rule([0.1], 0.16)["verdict"].startswith("not evaluable")


def test_false_positive_rule_clopper_pearson():
    r0 = false_positive_rule(0, 20)
    assert r0["verdict"].startswith("no evidence") and abs(r0["cp95"][1] - 0.168) < 0.005
    assert false_positive_rule(3, 20)["verdict"].startswith("no evidence")
    assert false_positive_rule(4, 20)["verdict"] == "evidence of excess false positives"       # CP lower limit 0.057 > 0.05
    assert cp(0, 20)[0] == 0.0 and cp(20, 20)[1] == 1.0


def test_evaluate_all_rules_on_a_clean_synthetic_summary():
    rng = np.random.default_rng(3)
    cells, nulls = {}, {}
    for N in (300, 1000):
        known = 0.16 + rng.normal(0, 0.03, 20)
        cells[f"U1|N={N}"] = {"truth": {"sigma2_F": 0.16}, "arms": {"known": _arm(known), "free": _arm(0.16 + rng.normal(0, 0.015, 20)),
                                                                   "cal": _arm(known + 0.10 + rng.normal(0, 0.02, 20))}}
        cells[f"U2|N={N}"] = {"truth": {"sigma2_F": 0.0}, "arms": {"known": _arm(np.abs(rng.normal(0, 0.01, 20))), "free": _arm(np.abs(rng.normal(0, 0.01, 20))),
                                                                   "cal": _arm(0.2 + rng.normal(0, 0.05, 20))}}
        cells[f"U4|N={N}"] = {"truth": {"sigma2_F": 0.0}, "arms": {"free": _arm(np.abs(rng.normal(0, 0.01, 20)))}}
        cells[f"U5|N={N}"] = {"truth": {"sigma2_F": 0.16}, "arms": {"free": _arm(0.16 + rng.normal(0, 0.02, 20)), "known": _arm(0.16 + rng.normal(0, 0.03, 20))}}
        cells[f"U3|N={N}"] = {"truth": {"sigma2_F": 0.16}, "arms": {"free": _arm(0.15 + rng.normal(0, 0.04, 20)), "known": _arm(0.14 + rng.normal(0, 0.02, 20))}}
        for rep in range(10):
            nulls.update([_null("U2", N, rep, False), _null("U4", N, rep, False)])
        for rep in range(5):
            nulls.update([_null("U1", N, rep, True, 19), _null("U5", N, rep, True, 19)])
    R = evaluate(_S(cells, nulls))
    assert R["all_gates_ok"], {k: v for k, v in R["gates"].items() if not v["ok"]}
    assert R["rules"]["PH3a U1 N=1000"]["verdict"] == "pass" and R["rules"]["PH3d U5 N=300"]["verdict"] == "pass"
    assert R["rules"]["PH3b U2 free"]["rejections"] == 0 and R["rules"]["PH3b U2 free"]["n"] == 20
    assert R["rules"]["PH3b U2 free"]["verdict"].startswith("no evidence")
    assert R["rules"]["PH3c U4 free"]["verdict"].startswith("no evidence") and "N=300" in R["rules"]["PH3c U4 free"]["sigma2_F_hat_distribution"]
    assert R["rules"]["PH3e U1 N=1000"]["verdict"] == "inflation" and R["rules"]["PH3e U2 N=300"]["verdict"] == "inflation"
    f = R["rules"]["PH3f U1 N=1000"]
    assert f["sd_ratio_free_over_known"] < 1.0 and f["bootstrap_ci95"] is not None and f["descriptive"]
    assert R["rules"]["power U1 N=300"]["rejections"] == 5 and R["rules"]["power U1 N=300"]["n"] == 5
    assert "H3c U3 N=300" in R["rules"]


def test_gates_make_rules_not_evaluable_and_false_positives_are_flagged():
    cells = {"U1|N=300": {"truth": {"sigma2_F": 0.16}, "arms": {"free": _arm(np.full(20, 0.16), converged=0.7)}}}   # 30 % not converged
    nulls = dict([_null("U2", 300, r, r < 6, 39, 5) for r in range(10)])                                          # 5/44 failed (11 %) > 5 %
    R = evaluate(_S(cells, nulls))
    assert not R["gates"]["G1 U1 N=300 free"]["ok"] and R["rules"]["PH3a U1 N=300"]["verdict"] == "not evaluable (G1)"
    assert not R["gates"]["G2 U2 N=300"]["ok"] and R["rules"]["PH3b U2 free"]["verdict"] == "not evaluable (G2)"
    assert not R["all_gates_ok"]
    nulls = dict([_null("U2", 300, r, r < 6) for r in range(10)])                                                  # 6/10 rejected, no failures
    R = evaluate(_S({}, nulls))
    assert R["rules"]["PH3b U2 free"]["verdict"] == "evidence of excess false positives"


def test_g3_requires_single_thread_blas_and_no_job_errors():
    assert not evaluate(_S(threads={"OMP_NUM_THREADS": "8"}))["gates"]["G3"]["ok"]
    assert evaluate(_S())["gates"]["G3"]["ok"]
    assert not evaluate(_S(errors=2))["gates"]["no_job_errors"]["ok"]


def test_frozen_confirmatory_matrix_and_budget():
    from kt_trial.config import load_yaml
    from difficulty_free.runner import estimate_cost, expand_jobs
    st = load_yaml("configs/experiment_03/stage_confirmatory.yaml")
    assert st["frozen"] is True and st["master_seed"] == 20262002 and st["budget"]["max_cpu_hours"] == 150
    jobs = expand_jobs(st)
    fits = jobs["phase1"]
    cnt = {}
    for j in fits:
        cnt.setdefault((j["scenario"], j["N"]), 0)
        cnt[(j["scenario"], j["N"])] += 1
    assert all(cnt[(s, N)] == 20 for s in ("U1", "U2", "U3", "U4", "U5") for N in (300, 1000))
    assert cnt[("A02", 1000)] == 5 and ("A02", 300) not in cnt and len(fits) == 205
    nulls = jobs["phase2"]
    assert len(nulls) == 1940 and all(j["arm"] == "free" for j in nulls)
    assert {j["scenario"] for j in nulls} == {"U1", "U2", "U4", "U5"}
    assert estimate_cost(st, jobs)["est_cpu_hours"] <= 150
