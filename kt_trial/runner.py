"""Resumable stage runner. Executes exactly the named stage config; nothing advances stages automatically."""
from __future__ import annotations

import json
import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .composite_likelihood import pair_counts
from .config import config_hash, file_sha256, generating_theta_dict, load_design, load_scenario, load_yaml
from .evaluate import heldout_scores, paired_difference, recovery_errors
from .fit import fit_model
from .inference import lboot_replicate, null_replicate, sandwich
from .manifest import VERSION_KEYS, code_hash, provenance
from .moments import Theta
from .schedule import build_templates
from .simulator import simulate

STAGES = ("smoke", "diagnostic", "confirmatory")


# ----------------------------------------------------------------------------- utilities
class _Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def write_json_atomic(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, cls=_Enc, allow_nan=True)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def job_id(j: dict) -> str:
    s = f"{j['kind']}__{j['scenario']}__N{j['N']}__r{j['rep']}"
    return s + (f"__b{j['b']}" if "b" in j else "")


def scenario_cfg(stage_cfg: dict, sid: str) -> dict:
    cfg = load_scenario(sid)
    cfg["fit"] = dict(cfg["fit"], n_starts=stage_cfg.get("n_starts", cfg["fit"]["n_starts"]))
    for sec, kv in (stage_cfg.get("overrides") or {}).items():       # e.g. {design: {n_templates: 2}} (tests only)
        cfg[sec] = {**cfg[sec], **kv}
    return cfg


def stage_hash(stage_cfg: dict) -> str:
    scen = {sid: load_scenario(sid) for sid in stage_cfg["scenarios"]}
    keep = {k: v for k, v in stage_cfg.items() if k not in ("budget",)}
    return config_hash({"stage": keep, "scenarios": scen, "design": load_design()})


# ----------------------------------------------------------------------------- job matrix
def _dataset_specs(stage_cfg, section):
    spec = stage_cfg.get(section)
    if not spec:
        return []
    out = []
    for d in spec.get("datasets", []):
        out.append(dict(scenario=d["scenario"], N=d.get("N", stage_cfg["N_list"][0]), rep=d["rep"]))
    return out


def expand_jobs(stage_cfg: dict) -> dict:
    fit = [dict(kind="fit", scenario=s, N=N, rep=r) for s in stage_cfg["scenarios"] for N in stage_cfg["N_list"]
           for r in range(stage_cfg["replications"])]
    null = [dict(kind="null_rep", b=b, **d) for d in _dataset_specs(stage_cfg, "null_bootstrap")
            for b in range(stage_cfg["null_bootstrap"]["B"])]
    lb = [dict(kind="lboot_rep", b=b, **d) for d in _dataset_specs(stage_cfg, "learner_bootstrap")
          for b in range(stage_cfg["learner_bootstrap"]["B"])]
    return {"phase1": fit, "phase2": null + lb}


def estimate_cost(stage_cfg: dict, jobs: dict) -> dict:
    c = stage_cfg.get("cost_model_sec_per_start", {"B0": 4.0, "B1": 7.0, "B2": 15.0})
    ns = stage_cfg.get("n_starts", 5)
    fit_sec = sum(ns * c[m] for m in stage_cfg["models"]) + (10.0 if stage_cfg.get("sandwich", True) else 0.0)
    null_sec = ns * (c["B1"] + c["B2"])
    lb_sec = 2 * c[stage_cfg.get("learner_bootstrap", {}).get("model", "B2")]
    n = {"fit": len(jobs["phase1"]), "null_rep": sum(j["kind"] == "null_rep" for j in jobs["phase2"]),
         "lboot_rep": sum(j["kind"] == "lboot_rep" for j in jobs["phase2"])}
    starts = {"fit": n["fit"] * ns * len(stage_cfg["models"]), "null_rep": n["null_rep"] * ns * 2, "lboot_rep": n["lboot_rep"] * 2}
    cpu = n["fit"] * fit_sec + n["null_rep"] * null_sec + n["lboot_rep"] * lb_sec
    w = stage_cfg.get("budget", {}).get("workers", 4)
    return {"jobs": n, "optimizer_starts": starts, "total_starts": int(sum(starts.values())), "est_cpu_hours": cpu / 3600.0,
            "est_wall_minutes_with_workers": cpu / 60.0 / w, "workers": w,
            "note": "estimates from the per-start seconds in cost_model_sec_per_start; N-independent objective cost"}


# ----------------------------------------------------------------------------- job execution
def _run_fit_job(job: dict, stage_cfg: dict) -> dict:
    sid, N, rep, ms = job["scenario"], job["N"], job["rep"], stage_cfg["master_seed"]
    cfg = scenario_cfg(stage_cfg, sid)
    K, G = cfg["design"]["n_skills"], cfg["design"]["n_templates"]
    ts = build_templates(cfg)
    truth = Theta.from_dict(generating_theta_dict(cfg))
    ds = simulate(cfg, N, ("data", sid, N, rep), ms, ts)
    Nt = stage_cfg.get("heldout_N", 0)
    te = simulate(cfg, Nt, ("heldout", sid, N, rep), ms, ts) if Nt else None
    pc = pair_counts(ds.Y, ds.template_id, G)
    skey = (sid, N, rep)
    fits, sw, scores = {}, {}, {}
    for m in stage_cfg["models"]:
        if m == "B0":
            fits[m] = fit_model("B0", ts, pc, cfg["fit"], K, skey, ms)
        elif m == "B1":
            fits[m] = fit_model("B1", ts, pc, cfg["fit"], K, skey, ms)
        else:
            b1 = fits.get("B1")
            fits[m] = fit_model("B2", ts, pc, cfg["fit"], K, skey, ms,
                                warm=Theta.from_dict(b1["theta"]) if b1 and b1["status"] != "failed" else None, null_fit=b1)
        f = fits[m]
        if f["status"] != "failed":
            f["errors"] = recovery_errors(Theta.from_dict(f["theta"]), truth)
            if stage_cfg.get("sandwich", True) and m in ("B1", "B2"):
                try:
                    sw[m] = sandwich(f, ts, ds, cfg["fit"], K)
                except Exception as e:
                    sw[m] = {"status": "error", "error": repr(e)}
            if te is not None:
                scores[m] = heldout_scores(Theta.from_dict(f["theta"]), ts, te)
    pred = {}
    if scores:
        for k in ("marginal_bernoulli_log_score", "pairwise_composite_log_score"):
            pred[k] = {m: float(s[k].mean()) for m, s in scores.items()}
            for a, b in (("B1", "B0"), ("B2", "B1")):
                if a in scores and b in scores:
                    pred[k][f"{a}-{b}"] = paired_difference(scores[a][k], scores[b][k])
    return {"scenario": sid, "N_fit": N, "N_heldout": Nt, "N_total_generated": N + Nt, "rep": rep,
            "truth": truth.to_dict(), "data_meta": ds.meta, "fits": fits, "sandwich": sw, "prediction": pred,
            "violations": cfg["scenario"]["violations"]}


def _load_fit_result(results_dir: Path, j: dict) -> dict:
    p = results_dir / "jobs" / (job_id(dict(kind="fit", scenario=j["scenario"], N=j["N"], rep=j["rep"])) + ".json")
    env = read_json(p)
    if env["status"] != "ok":
        raise RuntimeError(f"prerequisite fit job failed: {p.name}")
    return env["result"]


def _run_null_rep(job, stage_cfg, results_dir):
    cfg = scenario_cfg(stage_cfg, job["scenario"])
    fr = _load_fit_result(results_dir, job)
    ts = build_templates(cfg)
    return null_replicate(fr["fits"]["B1"], ts, cfg, job["N"], job["b"], (job["scenario"], job["N"], job["rep"]),
                          stage_cfg["master_seed"])


def _run_lboot_rep(job, stage_cfg, results_dir):
    sid, N, rep = job["scenario"], job["N"], job["rep"]
    cfg = scenario_cfg(stage_cfg, sid)
    fr = _load_fit_result(results_dir, job)
    ts = build_templates(cfg)
    ds = simulate(cfg, N, ("data", sid, N, rep), stage_cfg["master_seed"], ts)
    model = stage_cfg["learner_bootstrap"].get("model", "B2")
    return lboot_replicate(fr["fits"][model], ts, ds, cfg["fit"], cfg["design"]["n_skills"], job["b"], (sid, N, rep),
                           stage_cfg["master_seed"])


def execute_job(job: dict, stage_cfg: dict, results_dir: str, chash: str) -> dict:
    """Run one job and write its envelope atomically. Exceptions are recorded, not raised."""
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    rd = Path(results_dir)
    t0 = time.time()
    env = {"job_id": job_id(job), "job": job, "config_hash": chash, "code_hash": code_hash(),
           "started": datetime.now(timezone.utc).isoformat()}
    try:
        if job["kind"] == "fit":
            res = _run_fit_job(job, stage_cfg)
        elif job["kind"] == "null_rep":
            res = _run_null_rep(job, stage_cfg, rd)
        else:
            res = _run_lboot_rep(job, stage_cfg, rd)
        env.update(status="ok", result=res)
    except Exception as e:
        env.update(status="error", error=repr(e), trace=traceback.format_exc(limit=6))
    env["runtime"] = time.time() - t0
    env["finished"] = datetime.now(timezone.utc).isoformat()
    write_json_atomic(rd / "jobs" / (env["job_id"] + ".json"), env)
    return {"job_id": env["job_id"], "status": env["status"], "runtime": env["runtime"]}


# ----------------------------------------------------------------------------- orchestration
def job_state(rd: Path, j: dict, chash: str) -> str:
    """'done' (valid ok result), 'error' (recorded exception), 'corrupt', or 'missing'."""
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
        diffs.append(f"code_hash: {old.get('code_hash','?')[:12]} -> {current['code_hash'][:12]}")
    for k in VERSION_KEYS:
        if old.get("env", {}).get(k) != current["env"].get(k):
            diffs.append(f"{k}: {old.get('env', {}).get(k)} -> {current['env'].get(k)}")
    return diffs


def run_stage(stage_path, results_root="results/experiment_01", workers=None, dry_run=False, retry_errors=False,
              allow_mismatch=False, frozen_sha256=None, out=print) -> int:
    stage_path = Path(stage_path)
    stage_cfg = load_yaml(stage_path)
    stage = stage_cfg["stage"]
    if stage not in STAGES:
        out(f"unknown stage {stage!r}"); return 2
    if stage == "confirmatory":
        if not stage_cfg.get("frozen"):
            out("REFUSED: confirmatory config must contain `frozen: true` (set only after explicit approval)."); return 2
        if frozen_sha256 != file_sha256(stage_path):
            out("REFUSED: --frozen-sha256 does not match the sha256 of the approved confirmatory config "
                f"(current sha256: {file_sha256(stage_path)})."); return 2
    chash = stage_hash(stage_cfg)
    jobs = expand_jobs(stage_cfg)
    cost = estimate_cost(stage_cfg, jobs)
    rd = Path(results_root) / stage / chash[:10]
    out(f"stage={stage} config_hash={chash[:12]} results_dir={rd}")
    out(f"job matrix: {cost['jobs']}  optimizer starts: {cost['optimizer_starts']} (total {cost['total_starts']})")
    out(f"estimated cost: {cost['est_cpu_hours']:.2f} CPU-h, ~{cost['est_wall_minutes_with_workers']:.0f} min wall "
        f"on {cost['workers']} workers")
    if dry_run:
        for j in jobs["phase1"][:50]:
            out("  " + job_id(j))
        if len(jobs["phase1"]) > 50:
            out(f"  ... {len(jobs['phase1'])} fit jobs; {len(jobs['phase2'])} replicate jobs follow")
        return 0
    cur = provenance()
    diffs = check_manifest(rd, cur)
    if diffs and not allow_mismatch:
        out("REFUSED: existing results were produced with a different code/software state:")
        for d in diffs:
            out("  " + d)
        out("Use a fresh results directory or pass --allow-mismatch (results will then be mixed and flagged)."); return 3
    rd.mkdir(parents=True, exist_ok=True)
    if not (rd / "manifest.json").exists() or diffs:
        write_json_atomic(rd / "manifest.json", {"stage": stage, "config_hash": chash, "stage_config": stage_cfg,
                                                 "mismatch_allowed": diffs or None, **cur})
    workers = workers or stage_cfg.get("budget", {}).get("workers", 4)
    wall_cap = stage_cfg.get("budget", {}).get("max_wall_minutes")
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
            pending, it = {}, iter(todo)
            stop = False
            def submit_next():
                try:
                    j = next(it)
                except StopIteration:
                    return False
                pending[ex.submit(execute_job, j, stage_cfg, str(rd), chash)] = j
                return True
            for _ in range(workers):
                submit_next()
            while pending:
                for fut in as_completed(list(pending)):
                    j = pending.pop(fut)
                    r = fut.result()
                    stats["ran"] += 1; stats["error"] += r["status"] != "ok"
                    out(f"  {r['job_id']} {r['status']} {r['runtime']:.0f}s  [{stats['ran']} run, {stats['error']} error, "
                        f"{(time.time()-t_start)/60:.1f} min]")
                    if wall_cap and (time.time() - t_start) / 60 > wall_cap and not stop:
                        out(f"WALL BUDGET of {wall_cap} min reached: not submitting more jobs. Re-run the same command to resume.")
                        stop = True
                    if not stop:
                        submit_next()
                    break
        if stop:
            return 4
    write_json_atomic(rd / "status.json", {"finished": datetime.now(timezone.utc).isoformat(), **stats,
                                           "wall_minutes": (time.time() - t_start) / 60})
    out(f"stage {stage} finished: {stats}, wall {(time.time()-t_start)/60:.1f} min")
    return 0
