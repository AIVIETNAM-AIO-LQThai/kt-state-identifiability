"""Tests of the warp-speed calibration estimator, its rules, the enforced CPU cap and the warp job (X3-D15)."""
import numpy as np
import pytest
import yaml

from kt_trial.config import load_yaml
from difficulty_free.calibration import alpha_hat, evaluate, pairs_bootstrap_ci, verdict


def test_alpha_hat_is_nominal_when_T_and_Tstar_have_the_same_law():
    rng = np.random.default_rng(1)
    T, Ts = rng.chisquare(2, 6000), rng.chisquare(2, 6000)
    assert abs(alpha_hat(T, Ts) - 0.05) < 0.015 and abs(alpha_hat(T, Ts, 0.10) - 0.10) < 0.02
    exact = float(np.exp(-(5.991464547 - 3.0) / 2.0))                  # P(chi2_2 > q95 - 3) for a T shifted up by 3 (liberal): 0.224
    assert abs(alpha_hat(T + 3.0, Ts) - exact) < 0.02


def test_alpha_hat_with_point_mass_at_zero_follows_the_registered_pvalue_logic():
    rng = np.random.default_rng(2)
    mix = lambda n: np.where(rng.random(n) < 0.4, 0.0, rng.chisquare(1, n))
    T, Ts = mix(8000), mix(8000)
    assert abs(alpha_hat(T, Ts) - 0.05) < 0.015
    Ts0 = np.zeros(1000)                                              # quantile 0: any T > 0 rejects, T = 0 never does
    assert alpha_hat(np.array([0.0, 0.0, 1.0, 2.0]), Ts0) == 0.5


def test_verdict_rules():
    assert verdict([0.10, 0.20]) == "liberal"
    assert verdict([0.02, 0.08]) == "consistent with 5 %" and verdict([0.03, 0.10]) == "consistent with 5 %"
    assert verdict([0.03, 0.14]) == "inconclusive" and verdict([0.0, 0.04]) == "inconclusive"   # CI below 0.05: not "consistent" by the rule


def test_pairs_bootstrap_ci_covers_the_true_level_in_most_replications():
    rng = np.random.default_rng(3)
    hit = 0
    for _ in range(40):
        T, Ts = rng.chisquare(2, 200), rng.chisquare(2, 200)
        lo, hi = pairs_bootstrap_ci(T, Ts, B=300, seed=int(rng.integers(1e6)))
        hit += lo <= 0.05 <= hi
    assert hit >= 34


def _rows(sid, N, n, shift=0.0, bad=0, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        T, Ts = rng.chisquare(2) + shift, rng.chisquare(2)
        r = {"scenario": sid, "N": N, "rep": i, "fit_failed": False, "star_failed": False, "converged": True, "T": T, "T_star": Ts,
             "sigma2_F": 0.01, "tau_F": 5.0, "sigma2_F_star": 0.01, "tau_F_star": 5.0}
        rows.append(r)
    for i in range(bad):
        rows[i]["fit_failed"] = True
    return rows


def test_evaluate_pooled_and_per_n_with_gate():
    ok = _rows("C2", 300, 150, seed=1) + _rows("C2", 1000, 150, seed=2)
    lib = _rows("C4", 300, 150, shift=2.5, seed=3) + _rows("C4", 1000, 150, shift=2.5, seed=4)
    C = evaluate(ok + lib)
    assert C["C2"]["pooled"]["verdict"] in ("consistent with 5 %", "inconclusive") and C["C2"]["pooled"]["ci95"][0] < 0.08
    assert C["C4"]["pooled"]["verdict"] == "liberal" and "N=300" in C["C4"] and C["C4"]["pooled"]["n_ok"] == 300
    gated = evaluate(_rows("C2", 300, 100, bad=10, seed=5))                  # 10 % failed > 5 %
    assert gated["C2"]["pooled"]["verdict"] == "not evaluable (gate)"
    assert evaluate(_rows("C2", 300, 5))["C2"]["pooled"]["verdict"].startswith("not evaluable")


def test_cpu_cap_helpers(tmp_path):
    from difficulty_free.runner import cap_reached, spent_seconds
    (tmp_path / "jobs").mkdir()
    for i, rt in enumerate((1800.0, 1800.0, 3600.0)):
        (tmp_path / "jobs" / f"j{i}.json").write_text('{"runtime": %s}' % rt)
    (tmp_path / "jobs" / "bad.json").write_text("not json")
    assert spent_seconds(tmp_path) == 7200.0
    st = {"budget": {"max_cpu_hours": 2.0, "enforce_cpu_cap": True}}
    assert cap_reached(7200.0, st) and not cap_reached(7199.0, st)
    assert not cap_reached(10 ** 9, {"budget": {"max_cpu_hours": 2.0}})      # not enforced unless asked


def test_calibration_stage_requires_frozen_flag_and_sha(tmp_path):
    from difficulty_free import runner
    cfg = load_yaml("configs/experiment_03/stage_pilot.yaml"); cfg["stage"] = "calibration"
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, out=lambda m: None) == 2
    cfg["frozen"] = True; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, frozen_sha256="bad", out=lambda m: None) == 2


def test_warp_jobs_expand_and_cost(tmp_path):
    from difficulty_free.runner import estimate_cost, expand_jobs
    st = {"stage": "pilot", "master_seed": 1, "scenarios": [{"id": "C2", "base": "S2"}], "warp": {"scenarios": ["C2"], "N_list": [300, 1000], "rep_range": [0, 3]},
          "cost_model_sec": {"warp": 700}, "budget": {"workers": 6}}
    jobs = expand_jobs(st)
    assert len(jobs["phase1"]) == 6 and all(j["kind"] == "warp" for j in jobs["phase1"]) and jobs["phase2"] == []
    assert abs(estimate_cost(st, jobs)["est_cpu_hours"] - 6 * 700 / 3600) < 1e-9


@pytest.mark.slow
def test_warp_job_end_to_end_on_a_tiny_dataset():
    from difficulty_free.jobs import run_warp_job
    st = {"master_seed": 7, "n_starts": 1, "scenarios": [{"id": "C2", "base": "S2"}]}
    r = run_warp_job(st, "C2", 150, 0)
    assert not r["fit_failed"] and not r["star_failed"] and np.isfinite(r["T"]) and np.isfinite(r["T_star"]) and r["T"] >= -1e-6
    assert r["runtime_fit"] > 0 and r["runtime_star"] > 0


def test_frozen_calibration_matrix_and_cap():
    from difficulty_free.runner import estimate_cost, expand_jobs
    st = load_yaml("configs/experiment_03/addendum_calibration.yaml")
    assert st["frozen"] is True and st["stage"] == "calibration" and st["master_seed"] == 20262101
    assert st["budget"]["max_cpu_hours"] == 100 and st["budget"]["enforce_cpu_cap"] is True
    jobs = expand_jobs(st)
    cnt = {}
    for j in jobs["phase1"]:
        assert j["kind"] == "warp"
        cnt[(j["scenario"], j["N"])] = cnt.get((j["scenario"], j["N"]), 0) + 1
    assert cnt == {(s, N): 100 for s in ("C2", "C4") for N in (300, 1000)} and jobs["phase2"] == []
    assert estimate_cost(st, jobs)["est_cpu_hours"] <= 100
