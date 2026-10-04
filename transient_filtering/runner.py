"""Resumable Experiment-2 runner: deterministic job identities, atomic writes, dry-run, manifest-mismatch refusal.
Runs exactly the named stage; nothing advances automatically. The confirmatory stage needs `frozen: true` and --frozen-sha256."""
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
PKG = Path(__file__).resolve().parent
REPO = PKG.parent


def code_hash() -> str:
    """LF-normalised sha256 over kt_trial/*.py and transient_filtering/*.py (immune to Windows CRLF checkouts)."""
    h = hashlib.sha256()
    for d in ("kt_trial", "transient_filtering"):
        for f in sorted((REPO / d).glob("*.py")):
            h.update(f"{d}/{f.name}".encode()); h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def provenance() -> dict:
    g = git_info()
    return {"code_hash": code_hash(), "git": g, "env": environment_info()}


def job_id(j: dict) -> str:
    if j["kind"] == "bound":
        return "bound"
    if j["kind"] == "track":
        return f"track__{j['scenario']}__N{j['N']}__r{j['rep']}"
    return f"ref__{j['scenario']}__N{j['N']}__r{j['rep']}"


def _range(r):
    return range(r[0], r[1])


def expand_jobs(cfg2: dict) -> list[dict]:
    out = [dict(kind="bound")]
    for d in cfg2["track"]["datasets"]:
        for sid in d["scenarios"]:
            for N in d["N_list"]:
                out += [dict(kind="track", scenario=sid, N=N, rep=r) for r in _range(d["rep_range"])]
    rc = cfg2.get("ref")
    if rc:
        out += [dict(kind="ref", scenario=rc["scenario"], N=rc["N"], rep=r) for r in _range(rc["rep_range"])]
    return out


def stage_hash(cfg2: dict) -> str:
    keep = {k: v for k, v in cfg2.items() if k not in ("budget", "cost_model_sec")}
    return config_hash({"stage": keep, "design": load_design(), "exp1_stage_sha": file_sha256(cfg2["exp1"]["stage_config"])})


def estimate_cost(cfg2: dict, jl: list[dict]) -> dict:
    c = cfg2.get("cost_model_sec", {"bound": 1.0, "track": 3.0, "ref_per_learner_per_kparticle": 0.3})
    n = {k: sum(j["kind"] == k for j in jl) for k in ("bound", "track", "ref")}
    rc = cfg2.get("ref")
    ref_sec = 0.0
    if rc:
        runs = rc["n_seeds"] + rc["doubling_factor"] + rc.get("n_seeds_b1", 3)
        ref_sec = 8 * rc["per_template"] * rc["n_particles"] / 1000.0 * runs * c["ref_per_learner_per_kparticle"] * 0.9
    cpu = n["bound"] * c["bound"] + n["track"] * c["track"] + n["ref"] * ref_sec
    w = cfg2.get("budget", {}).get("workers", 4)
    return {"jobs": n, "est_cpu_hours": cpu / 3600.0, "est_wall_minutes": cpu / 60.0 / w, "workers": w}


def execute_job(job: dict, cfg2: dict, results_dir: str, chash: str) -> dict:
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    rd = Path(results_dir); t0 = time.time()
    env = {"job_id": job_id(job), "job": job, "config_hash": chash, "code_hash": code_hash(),
           "started": datetime.now(timezone.utc).isoformat()}
    try:
        if job["kind"] == "bound":
            res = J.run_bound(cfg2)
        elif job["kind"] == "track":
            res = J.run_track(cfg2, job["scenario"], job["N"], job["rep"])
        else:
            res = J.run_ref(cfg2, job["rep"])
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


def run_stage(stage_path, results_root="results/experiment_02", workers=None, dry_run=False, retry_errors=False,
              allow_mismatch=False, frozen_sha256=None, out=print) -> int:
    stage_path = Path(stage_path)
    cfg2 = load_yaml(stage_path)
    stage = cfg2["stage"]
    if stage not in STAGES:
        out(f"unknown stage {stage!r}"); return 2
    if stage == "confirmatory":
        if not cfg2.get("frozen"):
            out("REFUSED: confirmatory config must contain `frozen: true` (set only after explicit approval)."); return 2
        if frozen_sha256 != file_sha256(stage_path):
            out(f"REFUSED: --frozen-sha256 does not match the config (current sha256: {file_sha256(stage_path)})."); return 2
    chash = stage_hash(cfg2)
    jl = expand_jobs(cfg2)
    cost = estimate_cost(cfg2, jl)
    rd = Path(results_root) / stage / chash[:10]
    out(f"stage={stage} config_hash={chash[:12]} results_dir={rd} data_source={cfg2['data_source']}")
    out(f"jobs: {cost['jobs']}  estimated {cost['est_cpu_hours']:.2f} CPU-h, ~{cost['est_wall_minutes']:.0f} min on {cost['workers']} workers")
    if dry_run:
        for j in jl[:60]:
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
        write_json_atomic(rd / "manifest.json", {"stage": stage, "config_hash": chash, "stage_config": cfg2,
                                                 "mismatch_allowed": diffs or None, **cur})
    workers = workers or cfg2.get("budget", {}).get("workers", 4)
    wall_cap = cfg2.get("budget", {}).get("max_wall_minutes")
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
    if todo:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            pending, it, stop = {}, iter(todo), False
            def submit_next():
                try:
                    j = next(it)
                except StopIteration:
                    return
                pending[ex.submit(execute_job, j, cfg2, str(rd), chash)] = j
            for _ in range(workers):
                submit_next()
            while pending:
                for fut in as_completed(list(pending)):
                    pending.pop(fut); r = fut.result()
                    stats["ran"] += 1; stats["error"] += r["status"] != "ok"
                    out(f"  {r['job_id']} {r['status']} {r['runtime']:.0f}s [{stats['ran']} run, {stats['error']} error, {(time.time()-t_start)/60:.1f} min]")
                    if wall_cap and (time.time() - t_start) / 60 > wall_cap and not stop:
                        out(f"WALL BUDGET of {wall_cap} min reached: not submitting more jobs. Re-run to resume."); stop = True
                    if not stop:
                        submit_next()
                    break
            if stop:
                return 4
    write_json_atomic(rd / "status.json", {"finished": datetime.now(timezone.utc).isoformat(), **stats,
                                           "wall_minutes": (time.time() - t_start) / 60})
    out(f"stage {stage} finished: {stats}")
    return 0
