"""Runner/summary smoke test for difficulty_free (tiny dataset, one start): dry-run, resume, manifest refusal, frozen gate, calibration isolation."""
import json

import numpy as np
import pytest
import yaml

from kt_trial.config import load_yaml


def _tiny(tmp_path):
    cfg = load_yaml("configs/experiment_03/stage_pilot.yaml")
    cfg.update(n_starts=1, N_list=[150], reps={"default": [0, 1]}, scenarios=[{"id": "U2", "base": "S2"}], arms={"U2": ["known", "cal", "free"]},
               null_bootstrap=[{"scenarios": ["U2"], "N_list": [150], "rep_range": [0, 1], "arms": ["free", "known"], "B": 1}])
    p = tmp_path / "tiny.yaml"
    p.write_text(yaml.safe_dump(cfg))
    return p


def test_calibration_noise_is_isolated_and_deterministic():
    from difficulty_free.jobs import calibrated_difficulties
    st = {"master_seed": 5, "cal_sd": 0.2}
    b = np.zeros(48)
    c1, c2 = calibrated_difficulties(st, "U1", 300, 0, b), calibrated_difficulties(st, "U1", 300, 0, b)
    assert np.array_equal(c1, c2) and not np.array_equal(c1, calibrated_difficulties(st, "U1", 300, 1, b))
    assert abs(c1.std() - 0.2) < 0.06


def test_confirmatory_requires_frozen_flag_and_sha(tmp_path):
    from difficulty_free import runner
    cfg = load_yaml("configs/experiment_03/stage_pilot.yaml"); cfg["stage"] = "confirmatory"
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, out=lambda m: None) == 2
    cfg["frozen"] = True; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, frozen_sha256="bad", out=lambda m: None) == 2


@pytest.mark.slow
def test_runner_end_to_end_resume_refusal_and_summary(tmp_path):
    from difficulty_free import runner
    from difficulty_free.summarize import summarize
    p = _tiny(tmp_path); root = tmp_path / "res"; msgs = []
    assert runner.run_stage(p, results_root=str(root), dry_run=True, out=msgs.append) == 0 and not root.exists()
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0
    rd = next((root / "pilot").iterdir())
    names = sorted(f.name for f in (rd / "jobs").glob("*.json"))
    assert len(names) == 3 and not list((rd / "jobs").glob("*.tmp"))          # 1 fit + 2 null (free, known)
    env = json.loads((rd / "jobs" / names[0]).read_text())
    assert env["status"] == "ok" and env["env"]["numpy"]
    fr = json.loads((rd / "jobs" / "fit__U2__N150__r0.json").read_text())["result"]
    assert set(fr["arms"]) == {"known", "cal", "free"} and len(fr["arms"]["free"]["B2"]["b"]) == 48
    msgs.clear()
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0 and any("0 jobs to run" in m for m in msgs)
    man = json.loads((rd / "manifest.json").read_text()); man["code_hash"] = "0" * 64
    (rd / "manifest.json").write_text(json.dumps(man))
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 3
    S = summarize(str(rd))
    assert S["accounting"]["errors"] == 0 and "U2|N=150" in S["cells"] and len(S["null_tests"]) == 2
    assert (rd / "summary.md").exists()
