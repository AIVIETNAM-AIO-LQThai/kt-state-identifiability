"""Resumable Experiment-3 runner: deterministic job identities, atomic writes, dry-run, manifest-mismatch refusal, frozen gate.
Runs exactly the named stage; nothing advances automatically. Every result records the interpreter and package versions."""
from __future__ import annotations

import hashlib
import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from kt_trial.config import config_hash, file_sha256, load_design, load_yaml
from kt_trial.manifest import VERSION_KEYS, environment_info, git_info
from kt_trial.runner import read_json, write_json_atomic

from . import jobs as J

STAGES = ("pilot", "confirmatory")
REPO = Path(__file__).resolve().parent.parent


def code_hash() -> str:
    """LF-normalised sha256 over kt_trial/*.py and difficulty_free/*.py."""
    h = hashlib.sha256()
    for d in ("kt_trial", "difficulty_free"):
        for f in sorted((REPO / d).glob("*.py")):
            h.update(f"{d}/{f.name}".encode()); h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def provenance() -> dict:
    return {"code_hash": code_hash(), "git": git_info(), "env": {**environment_info(), "threads": {k: os.environ.get(k) for k in
            ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}}}


def job_id(j: dict) -> str:
    if j["kind"] == "fit":
        return f"fit__{j['scenario']}__N{j['N']}__r{j['rep']}"
    return f"null__{j['scenario']}__N{j['N']}__r{j['rep']}__{j['arm']}__b{j['b']}"


def expand_jobs(stage: dict) -> dict:
    fit = [dict(kind="fit", scenario=s["id"], N=N, rep=r) for s in stage["scenarios"] for N in stage["N_list"]
           for r in range(*stage["reps"].get(s["id"], stage["reps"]["default"]))]
    null = []
    for d in stage.get("null_bootstrap", []):
        for sid in d["scenarios"]:
            for N in d["N_list"]:
                for r in range(*d["rep_range"]):
                    for arm in d["arms"]:
                        null += [dict(kind="null", scenario=sid, N=N, rep=r, arm=arm, b=b) for b in range(d["B"])]
    return {"phase1": fit, "phase2": null}


def stage_hash(stage: dict) -> str:
    keep = {k: v for k, v in stage.items() if k not in ("budget", "cost_model_sec")}
    return config_hash({"stage": keep, "design": load_design()})


def estimate_cost(stage: dict, jobs: dict) -> dict:
    c = stage["cost_model_sec"]
    cpu = 0.0
    for j in jobs["phase1"]:
        cpu += sum(c[f"fit_{a}"] for a in stage["arms"].get(j["scenario"], ["known", "cal", "free"]))
    for j in jobs["phase2"]:
        cpu += c[f"null_{j['arm']}"]
    w = stage.get("budget", {}).get("workers", 4)
    return {"jobs": {"fit": len(jobs["phase1"]), "null": len(jobs["phase2"])}, "est_cpu_hours": cpu / 3600.0,
            "est_wall_minutes": cpu / 60.0 / w, "workers": w}


def execute_job(job: dict, stage: dict, results_dir: str, chash: str) -> dict:
    rd = Path(results_dir)
    t0 = time.time()
    env = {"job_id": job_id(job), "job": job, "config_hash": chash, "code_hash": code_hash(), "env": environment_info(),
           "started": datetime.now(timezone.utc).isoformat()}
    try:
        res = (J.run_fit_job(stage, job["scenario"], job["N"], job["rep"]) if job["kind"] == "fit"
               else J.run_null_job(stage, results_dir, job["scenario"], job["N"], job["rep"], job["arm"], job["b"]))
        env.update(status="ok", result=res)
    except Exception as e:
        env.update(status="error", error=repr(e), trace=traceback.format_exc(limit=6))
    env["runtime"] = time.time() - t0
    env["finished"] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(rd / "jobs" / (env["job_id"] + ".json"), env)
    return {"job_id": env["job_id"], "status": env["status"], "runtime": env["runtime"]}


def job_state(rd: Path, j: dict, chash: str) -> str:
    p = rd / "jobs" / (job_id(j) + ".json")
    if not p.exists():
        return "missing"
    try:
        env = read_json(p)
        if env.get("job_id") != job_id(j) or env.get("config_hash") != chash or "status" not in env:
            return "corrupt"
        return "done" if env["status"] == "ok" else "error"
    except Exception:
        return "corrupt"


def check_manifest(rd: Path, current: dict) -> list[str]:
    mp = rd / "manifest.json"
    if not mp.exists():
        return []
    old = read_json(mp)
    diffs = []
    if old.get("code_hash") != current["code_hash"]:
        diffs.append(f"code_hash: {old.get('code_hash', '?')[:12]} -> {current['code_hash'][:12]}")
    for k in VERSION_KEYS:
        if old.get("env", {}).get(k) != current["env"].get(k):
            diffs.append(f"{k}: {old.get('env', {}).get(k)} -> {current['env'].get(k)}")
    return diffs


def run_stage(stage_path, results_root="results/experiment_03", workers=None, dry_run=False, retry_errors=False,
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
    jobs = expand_jobs(stage)
    cost = estimate_cost(stage, jobs)
    rd = Path(results_root) / name / chash[:10]
    out(f"stage={name} config_hash={chash[:12]} results_dir={rd}")
    out(f"jobs: {cost['jobs']}  estimated {cost['est_cpu_hours']:.2f} CPU-h, ~{cost['est_wall_minutes']:.0f} min on {cost['workers']} workers")
    if dry_run:
        for j in jobs["phase1"][:40]:
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
    t_start = time.time()
    stats = {"done_before": 0, "ran": 0, "error": 0}
    for phase in ("phase1", "phase2"):
        todo = []
        for j in jobs[phase]:
            st = job_state(rd, j, chash)
            if st == "done" or (st == "error" and not retry_errors):
                stats["done_before"] += 1
            else:
                todo.append(j)
        if phase == "phase2":
            todo = [j for j in todo if job_state(rd, dict(kind="fit", scenario=j["scenario"], N=j["N"], rep=j["rep"]), chash) == "done"]
        out(f"[{phase}] {len(todo)} jobs to run ({len(jobs[phase]) - len(todo)} already valid/recorded)")
        if not todo:
            continue
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
                    stats["ran"] += 1; stats["error"] += r["status"] != "ok"
                    out(f"  {r['job_id']} {r['status']} {r['runtime']:.0f}s [{stats['ran']} run, {stats['error']} error, {(time.time() - t_start) / 60:.1f} min]")
                    if wall_cap and (time.time() - t_start) / 60 > wall_cap and not stop:
                        out(f"WALL BUDGET of {wall_cap} min reached: not submitting more jobs. Re-run to resume."); stop = True
                    if not stop:
                        submit_next()
                    break
            if stop:
                return 4
    write_json_atomic(rd / "status.json", {"finished": datetime.now(timezone.utc).isoformat(), **stats, "wall_minutes": (time.time() - t_start) / 60})
    out(f"stage {name} finished: {stats}")
    return 0
