"""Resumable Experiment-5 runner: deterministic job ids, atomic writes, dry-run, manifest-mismatch refusal, frozen gate, enforced CPU cap.
A modified copy of discrimination_free.runner: the same job expansion (rep-major option, per-scenario rep_range), job ids and stage hash are
imported from it; the code hash covers all four packages and the cost model is per scenario."""
from __future__ import annotations

import hashlib
import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from kt_trial.config import file_sha256, load_yaml
from kt_trial.manifest import environment_info, git_info
from kt_trial.runner import write_json_atomic
from difficulty_free.runner import cap_reached, check_manifest, job_state, spent_seconds
from discrimination_free.runner import expand_jobs, job_id, stage_hash

from . import jobs as J

STAGES = ("pilot", "confirmatory")
REPO = Path(__file__).resolve().parent.parent
PACKAGES = ("kt_trial", "difficulty_free", "discrimination_free", "state_dependence")


def code_hash() -> str:
    """LF-normalised sha256 over the sources of the four packages."""
    h = hashlib.sha256()
    for d in PACKAGES:
        for f in sorted((REPO / d).glob("*.py")):
            h.update(f"{d}/{f.name}".encode()); h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def provenance() -> dict:
    return {"code_hash": code_hash(), "git": git_info(), "env": {**environment_info(), "threads": {k: os.environ.get(k) for k in
            ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}}


def estimate_cost(stage: dict, jl: list[dict]) -> dict:
    c = stage["cost_model_sec"]
    cpu = sum(c.get(j["scenario"], c["default"]) for j in jl)
    w = stage.get("budget", {}).get("workers", 4)
    return {"jobs": {k: sum(j["kind"] == k for j in jl) for k in ("fit", "warp")}, "est_cpu_hours": cpu / 3600.0,
            "est_wall_minutes": cpu / 60.0 / w, "workers": w}


def execute_job(job: dict, stage: dict, results_dir: str, chash: str) -> dict:
    rd = Path(results_dir)
    t0 = time.time()
    env = {"job_id": job_id(job), "job": job, "config_hash": chash, "code_hash": code_hash(), "env": environment_info(),
           "started": datetime.now(timezone.utc).isoformat()}
    try:
        res = (J.run_fit_job if job["kind"] == "fit" else J.run_warp_job)(stage, job["scenario"], job["N"], job["rep"])
        env.update(status="ok", result=res)
    except Exception as e:
        env.update(status="error", error=repr(e), trace=traceback.format_exc(limit=6))
    env["runtime"] = time.time() - t0
    env["finished"] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(rd / "jobs" / (env["job_id"] + ".json"), env)
    return {"job_id": env["job_id"], "status": env["status"], "runtime": env["runtime"]}


def run_stage(stage_path, results_root="results/experiment_05", workers=None, dry_run=False, retry_errors=False,
              allow_mismatch=False, frozen_sha256=None, out=print) -> int:
    stage_path = Path(stage_path)
    stage = load_yaml(stage_path)
    name = stage["stage"]
    if name not in STAGES:
        out(f"unknown stage {name!r}"); return 2
    if name == "confirmatory":
        if not stage.get("frozen"):
            out("REFUSED: confirmatory config must contain `frozen: true` (set only after explicit approval)."); return 2
        if frozen_sha256 != file_sha256(stage_path):
            out(f"REFUSED: --frozen-sha256 does not match the config (current sha256: {file_sha256(stage_path)})."); return 2
    chash = stage_hash(stage)
    jl = expand_jobs(stage)
    cost = estimate_cost(stage, jl)
    rd = Path(results_root) / name / chash[:10]
    out(f"stage={name} config_hash={chash[:12]} results_dir={rd}")
    out(f"jobs: {cost['jobs']}  estimated {cost['est_cpu_hours']:.2f} CPU-h, ~{cost['est_wall_minutes']:.0f} min on {cost['workers']} workers")
    if dry_run:
        for j in jl[:40]:
            out("  " + job_id(j))
        return 0
    cur = provenance()
    diffs = check_manifest(rd, cur)
    if diffs and not allow_mismatch:
        out("REFUSED: existing results were produced with a different code/software state:")
        for d in diffs:
            out("  " + d)
        return 3
    rd.mkdir(parents=True, exist_ok=True)
    if not (rd / "manifest.json").exists() or diffs:
        write_json_atomic(rd / "manifest.json", {"stage": name, "config_hash": chash, "stage_config": stage, "mismatch_allowed": diffs or None, **cur})
    workers = workers or stage.get("budget", {}).get("workers", 4)
    wall_cap = stage.get("budget", {}).get("max_wall_minutes")
    spent = spent_seconds(rd)
    if cap_reached(spent, stage):
        out(f"CPU CAP already reached ({spent / 3600:.1f} CPU-h): nothing submitted."); return 5
    todo, before = [], 0
    for j in jl:
        st = job_state(rd, j, chash)
        if st == "done" or (st == "error" and not retry_errors):
            before += 1
        else:
            todo.append(j)
    out(f"{len(todo)} jobs to run ({before} already valid/recorded)")
    stats = {"done_before": before, "ran": 0, "error": 0}
    t_start = time.time()
    capped = False
    if todo:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            pending, it, stop = {}, iter(todo), False

            def submit_next():
                try:
                    j = next(it)
                except StopIteration:
                    return
                pending[ex.submit(execute_job, j, stage, str(rd), chash)] = j
            for _ in range(workers):
                submit_next()
            while pending:
                for fut in as_completed(list(pending)):
                    pending.pop(fut); r = fut.result()
                    stats["ran"] += 1; stats["error"] += r["status"] != "ok"; spent += r["runtime"]
                    out(f"  {r['job_id']} {r['status']} {r['runtime']:.0f}s [{stats['ran']} run, {stats['error']} error, {(time.time() - t_start) / 60:.1f} min]")
                    if cap_reached(spent, stage) and not stop:
                        out(f"CPU CAP reached ({spent / 3600:.1f} CPU-h): not submitting more jobs. Finished work is kept."); stop = True; capped = True
                    if wall_cap and (time.time() - t_start) / 60 > wall_cap and not stop:
                        out(f"WALL BUDGET of {wall_cap} min reached: not submitting more jobs. Re-run to resume."); stop = True
                    if not stop:
                        submit_next()
                    break
            if stop:
                return 5 if capped else 4
    write_json_atomic(rd / "status.json", {"finished": datetime.now(timezone.utc).isoformat(), **stats, "wall_minutes": (time.time() - t_start) / 60})
    out(f"stage {name} finished: {stats}")
    return 0
