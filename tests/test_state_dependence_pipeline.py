"""Stage-1 tests for state_dependence: job expansion and gates, rules on synthetic envelopes, and a tiny end-to-end runner check."""
import json

import numpy as np
import pytest
import yaml

from kt_trial.config import load_yaml
from state_dependence import rules

H = "a" * 64


def test_job_expansion_rep_major_gate_and_cost(tmp_path):
    from state_dependence import runner
    st = load_yaml("configs/experiment_05/stage_pilot.yaml")
    jl = runner.expand_jobs(st)
    assert len(jl) == 36 and sum(j["kind"] == "warp" for j in jl) == 6 and {j["scenario"] for j in jl if j["kind"] == "warp"} == {"E4"}
    assert all(j["rep"] == 0 for j in jl[:12]) and all(j["rep"] == 1 for j in jl[12:24])
    cost = runner.estimate_cost(st, jl)
    assert abs(cost["est_cpu_hours"] - (30 * 700 + 6 * 1100) / 3600.0) < 1e-9
    cfg = dict(st, stage="confirmatory"); p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, out=lambda m: None) == 2          # not frozen
    cfg["frozen"] = True; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, frozen_sha256="bad", out=lambda m: None) == 2


def test_level_verdict_branches():
    assert rules.level_verdict(0.06, 0.12) == "liberal"
    assert rules.level_verdict(0.03, 0.08) == "consistent with 5 %"
    assert rules.level_verdict(0.03, 0.14) == "inconclusive"
    assert rules.level_verdict(0.00, 0.03) == "inconclusive"


def _rec(sid, N, rep, p, T=0.0, ok=True):
    b2 = {"status": "ok" if ok else "flagged", "converged": ok, "theta": {"sigma2_F": 0.0, "tau_F": 5.0}, "flags": [], "sigma2_F_error_vs_star": 0.01,
          "n_polished": 1}
    d = {"by_tau_x": {t: {"p": p, "eta_hat": -0.1, "delta": -0.1, "stat": 1.0, "U": 1.0, "info": 1.0, "var_per_learner": 1.0} for t in ("2", "5", "10")}}
    return {"scenario": sid, "N": N, "rep": rep, "sigma2_F_star": 0.0, "arms": {"B1": dict(b2), "B2": b2}, "diag": {"B2": d, "B1": d}, "T": T}


def _write(rd, recs):
    (rd / "jobs").mkdir(parents=True, exist_ok=True)
    for r in recs:
        name = f"fit__{r['scenario']}__N{r['N']}__r{r['rep']}"
        (rd / "jobs" / f"{name}.json").write_text(json.dumps({"job_id": name, "job": dict(kind="fit", scenario=r["scenario"], N=r["N"], rep=r["rep"]),
                                                              "status": "ok", "result": r, "code_hash": H, "runtime": 1.0}))
    (rd / "manifest.json").write_text(json.dumps({"code_hash": H, "env": {"threads": {"OMP_NUM_THREADS": "1"}}, "stage_config": {}}))


def _cells(rej_level, rej_power, level_n=75, power_n=30, bad=0):
    recs = []
    for sid in ("E1", "E2"):
        for N in rules.NS:
            for i in range(level_n):
                recs.append(_rec(sid, N, i, 0.01 if i < rej_level else 0.5))
    for sid in ("E3", "E5"):
        for N in rules.NS:
            for i in range(power_n):
                recs.append(_rec(sid, N, i, 0.001 if i < rej_power else 0.5, ok=i >= bad))
    for N in rules.NS:
        for i in range(50):
            recs.append(_rec("E6", N, i, 0.5))
    return recs


def test_rules_verdict_branches_and_gates(tmp_path):
    ev = lambda sub, **kw: (_write(tmp_path / sub, _cells(**kw)), rules.evaluate(tmp_path / sub))[1]
    R = ev("good", rej_level=4, rej_power=30)                       # 16 / 300 = 0.053 pooled (4 per cell and N); E3/E5 reject all
    assert R["rules"]["H5b"]["verdict"] == "supported" and R["rules"]["H5c"]["verdict"] == "consistent with 5 %"
    assert all(g["ok"] for g in R["gates"].values())
    R = ev("lib", rej_level=25, rej_power=30)                       # 100 / 300 = 0.33 pooled
    assert R["rules"]["H5c"]["verdict"] == "liberal"
    R = ev("weak", rej_level=4, rej_power=15)                       # half of E3 / E5 rejected
    assert R["rules"]["H5b"]["verdict"] == "not supported"
    R = ev("bad", rej_level=4, rej_power=30, bad=5)                 # 5 / 30 non-converged in E3 and E5 -> G1 fails
    assert R["gates"]["G1 E3 N=1000"]["ok"] is False and R["rules"]["H5b"]["verdict"].startswith("not evaluable")
    assert R["rules"]["H5d"]["pooled"]["share"] == 0.0 and "conservative" in R["rules"]["H5d"]["pooled"]["note"]
    md = "\n".join(rules.markdown(R))
    assert "H5b" in md and "Gates" in md


@pytest.mark.slow
def test_runner_end_to_end_resume_refusal_and_summary(tmp_path):
    from state_dependence import runner
    from state_dependence.summarize import summarize
    st = load_yaml("configs/experiment_05/stage_pilot.yaml")
    st.update(n_starts=1, fit={"scenarios": ["E5"], "N_list": [150], "rep_range": {"E5": [0, 1]}},
              warp={"scenarios": ["E4"], "N_list": [150], "rep_range": {"E4": [0, 1]}}, cost_model_sec={"default": 100})
    p = tmp_path / "tiny.yaml"; p.write_text(yaml.safe_dump(st)); root = tmp_path / "res"; msgs = []
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0
    rd = next((root / "pilot").iterdir())
    assert len(list((rd / "jobs").glob("*.json"))) == 2 and not list((rd / "jobs").glob("*.tmp"))
    fr = json.loads((rd / "jobs" / "fit__E5__N150__r0.json").read_text())["result"]
    d = fr["diag"]["B2"]["by_tau_x"]
    assert set(d) == {"2", "5", "10"} and all(0.0 <= v["p"] <= 1.0 for v in d.values()) and np.isfinite(fr["T"]) and abs(fr["sigma2_F_star"] - 0.16) < 1e-12
    wr = json.loads((rd / "jobs" / "warp__E4__N150__r0.json").read_text())["result"]
    assert np.isfinite(wr["T"]) and np.isfinite(wr["T_star"]) and wr["sigma2_F_star"] == 0.0 and "by_tau_x" in wr["diag"]["B2"]
    msgs.clear()
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0 and any("0 jobs to run" in m for m in msgs)
    man = json.loads((rd / "manifest.json").read_text()); man["code_hash"] = "0" * 64
    (rd / "manifest.json").write_text(json.dumps(man))
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 3
    S = summarize(str(rd), with_rules=True)
    assert S["accounting"]["errors"] == 0 and "E5|N=150" in S["cells"] and "warp" in S["cells"]["E4|N=150"] and (rd / "rules.json").exists()


def _ref_dir(tmp_path):
    ref = tmp_path / "ref" / "jobs"
    ref.mkdir(parents=True)
    for N in rules.NS:
        for i in range(50):
            (ref / f"warp__V2__N{N}__r{i}.json").write_text(json.dumps({"status": "ok", "result": {"twopl": {
                "T_star": 5.0 * i / 49.0, "star_failed": False, "star_converged": True}}}))
    return str(tmp_path / "ref")


def test_h5a_verdict_branches(tmp_path):
    ref = _ref_dir(tmp_path)
    assert abs(rules.null_q95(ref)[1000] - 4.75) < 0.05
    for name, n_hi, want in (("sup", 30, "supported"), ("notsup", 0, "not supported"), ("inc", 15, "inconclusive")):
        rd = tmp_path / name
        recs = _cells(rej_level=4, rej_power=30)
        recs = [dict(r, T=(100.0 if (r["scenario"] == "E3" and r["rep"] < n_hi) else 0.0)) if r["scenario"] == "E3" else r for r in recs]
        _write(rd, recs)
        man = json.loads((rd / "manifest.json").read_text()); man["stage_config"] = {"null_reference": ref}
        (rd / "manifest.json").write_text(json.dumps(man))
        R = rules.evaluate(rd)
        assert R["rules"]["H5a"]["verdict"] == want, (name, R["rules"]["H5a"]["E3"])
    assert R["frozen_rules_version"] == "X5-D06+D07" and "tau_R_at_upper_bound" in R["descriptives"]["fit_summary"]["E3 N=1000"]
