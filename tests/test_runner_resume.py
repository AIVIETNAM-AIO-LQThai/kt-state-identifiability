import json
from pathlib import Path

import pytest
import yaml

from kt_trial.runner import (check_manifest, execute_job, expand_jobs, job_id, job_state, read_json, run_stage,
                             stage_hash)
from kt_trial.manifest import provenance
from kt_trial.summarize import summarize

TINY = {
    "stage": "smoke", "master_seed": 777, "scenarios": ["S1", "S2"], "N_list": [30], "replications": 1,
    "models": ["B0", "B1", "B2"], "n_starts": 2, "heldout_N": 30, "sandwich": True,
    "overrides": {"design": {"n_templates": 2}},
    "null_bootstrap": {"B": 2, "datasets": [{"scenario": "S1", "rep": 0}]},
    "learner_bootstrap": {"B": 2, "model": "B2", "datasets": [{"scenario": "S1", "rep": 0}]},
    "budget": {"workers": 2, "max_wall_minutes": 30},
}


@pytest.fixture(scope="module")
def tiny_run(tmp_path_factory):
    d = tmp_path_factory.mktemp("run")
    cfgp = d / "tiny.yaml"
    cfgp.write_text(yaml.safe_dump(TINY))
    lines = []
    rc = run_stage(cfgp, d / "res", workers=2, out=lines.append)
    return d, cfgp, rc, lines


def test_dry_run_prints_matrix_without_fitting(tmp_path):
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(TINY))
    lines = []
    assert run_stage(p, tmp_path / "res", dry_run=True, out=lines.append) == 0
    assert any("job matrix" in l for l in lines) and not (tmp_path / "res").exists()


@pytest.mark.slow
def test_full_run_then_idempotent_resume(tiny_run):
    d, cfgp, rc, lines = tiny_run
    assert rc == 0
    rd = next((d / "res" / "smoke").iterdir())
    jobs = sorted(p.name for p in (rd / "jobs").glob("*.json"))
    assert len(jobs) == 2 + 2 + 2                                         # 2 fit, 2 null reps, 2 lboot reps
    assert (rd / "manifest.json").exists() and (rd / "status.json").exists()
    before = {p.name: p.stat().st_mtime_ns for p in (rd / "jobs").glob("*.json")}
    lines2 = []
    assert run_stage(cfgp, d / "res", workers=2, out=lines2.append) == 0
    after = {p.name: p.stat().st_mtime_ns for p in (rd / "jobs").glob("*.json")}
    assert before == after and any("0 jobs to run" in l or "already valid" in l for l in lines2)


@pytest.mark.slow
def test_corrupt_job_is_rerun_and_summary_generated(tiny_run):
    d, cfgp, rc, _ = tiny_run
    rd = next((d / "res" / "smoke").iterdir())
    victim = rd / "jobs" / "fit__S2__N30__r0.json"
    victim.write_text("{ truncated")
    chash = stage_hash(yaml.safe_load(cfgp.read_text()))
    assert job_state(rd, dict(kind="fit", scenario="S2", N=30, rep=0), chash) == "corrupt"
    assert run_stage(cfgp, d / "res", workers=2, out=lambda *_: None) == 0
    assert job_state(rd, dict(kind="fit", scenario="S2", N=30, rep=0), chash) == "done"
    s = summarize(rd)
    assert (rd / "summary.md").exists() and "S1|N=30" in s["cells"]
    c = s["cells"]["S1|N=30"]
    assert c["N_fit"] == 30 and c["N_heldout"] == 30 and c["N_total_generated"] == 60      # N reported as fitting learners
    assert s["null_tests"] and s["learner_bootstrap"]


@pytest.mark.slow
def test_code_mismatch_is_refused(tiny_run):
    d, cfgp, rc, _ = tiny_run
    rd = next((d / "res" / "smoke").iterdir())
    m = read_json(rd / "manifest.json"); m["code_hash"] = "0" * 64
    (rd / "manifest.json").write_text(json.dumps(m))
    lines = []
    assert run_stage(cfgp, d / "res", workers=1, out=lines.append) == 3 and any("REFUSED" in l for l in lines)
    assert check_manifest(rd, provenance())


def test_failed_job_recorded_as_data(tmp_path):
    cfg = dict(TINY)
    cfg["scenarios"] = ["S1"]
    job = dict(kind="fit", scenario="NOPE", N=30, rep=0)
    r = execute_job(job, cfg, str(tmp_path), "h")
    assert r["status"] == "error"
    env = read_json(tmp_path / "jobs" / (job_id(job) + ".json"))
    assert env["status"] == "error" and "NOPE" in env["error"] + env["trace"]
    assert job_state(tmp_path, job, "h") == "error"


def test_confirmatory_requires_frozen_hash(tmp_path):
    c = dict(TINY, stage="confirmatory")
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(c))
    lines = []
    assert run_stage(p, tmp_path / "r", dry_run=True, out=lines.append) == 2               # not frozen
    c["frozen"] = True; p.write_text(yaml.safe_dump(c))
    assert run_stage(p, tmp_path / "r", dry_run=True, frozen_sha256="deadbeef", out=lines.append) == 2
    from kt_trial.config import file_sha256
    assert run_stage(p, tmp_path / "r", dry_run=True, frozen_sha256=file_sha256(p), out=lines.append) == 0


def test_job_matrix_counts():
    j = expand_jobs(TINY)
    assert len(j["phase1"]) == 2 and len(j["phase2"]) == 4
