"""Numerical-validation addendum for Experiment 1: selection and per-dataset checks of saved near-null certificate warnings.

For each selected bootstrap-null dataset: regenerate it from the recorded B1 parameters and seed keys, re-run the registered
B1/B2 searches (reproduction check), inspect KKT conditions and Hessian eigenvalues at several finite-difference scales,
profile tau_F (re-optimising everything else) and record the ATTAINED likelihood improvement and the effect on the affected
p-value. A finite profile search gives an attained improvement, not a global bound. Original outputs are never modified.
"""
from __future__ import annotations

import glob
import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import load_yaml, rng_for
from kt_trial.fit import Objective, _one_start, fit_model, newton_certificate
from kt_trial.inference import null_config
from kt_trial.models import ParamMap
from kt_trial.moments import Theta
from kt_trial.runner import read_json, scenario_cfg, write_json_atomic
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate

CELLS = [("S2", 300), ("S2", 1000), ("S8n", 300), ("S8n", 1000)]


def _warned(r, flags):
    return any(f in r["flags2"] for f in flags)


def load_nulls(results: str):
    out = []
    for f in sorted(glob.glob(str(Path(results) / "jobs" / "null_rep__*.json"))):
        e = read_json(Path(f))
        if e["status"] == "ok" and not e["result"].get("failed"):
            j = e["job"]
            out.append(dict(scenario=j["scenario"], N=j["N"], rep=j["rep"], b=j["b"], job_id=e["job_id"], **{k: v for k, v in e["result"].items() if k != "b"}))
    return out


def select(cfg: dict) -> dict:
    nulls = load_nulls(cfg["exp1"]["results"])
    wf = cfg["warning_flags"]
    sel, seen = [], set()

    def add(tier, why, r):
        if r["job_id"] in seen:
            return False
        seen.add(r["job_id"])
        sel.append(dict(tier=tier, why=why, kind="null", scenario=r["scenario"], N=r["N"], rep=r["rep"], b=r["b"],
                        job_id=r["job_id"], saved={"clr": r["clr"], "sigma2_F": r["sigma2_F"], "tau_F": r["tau_F"], "flags2": r["flags2"]}))
        return True
    A = cfg["selection"]["tier_A"]["scenarios"]
    for r in sorted((r for r in nulls if r["scenario"] in A and _warned(r, wf)), key=lambda r: r["job_id"]):
        add("A", "warned S1/S8 replicate", r)
    B = cfg["selection"]["tier_B"]
    pool = [r for r in nulls if r["scenario"] in B["scenarios"]]
    for r in sorted((r for r in pool if _warned(r, wf)), key=lambda r: (-r["clr"], r["job_id"]))[:B["top_clr"]]:
        add("B", "highest saved CLR among warned S2/S8n", r)

    def round_robin(cands, k, tier, why):
        by = {c: sorted((r for r in cands if (r["scenario"], r["N"]) == c), key=lambda r: r["job_id"]) for c in CELLS}
        got = 0
        while got < k and any(by.values()):
            for c in CELLS:
                while by[c] and by[c][0]["job_id"] in seen:
                    by[c].pop(0)
                if by[c] and got < k:
                    add(tier, why, by[c].pop(0)); got += 1
    round_robin([r for r in pool if "hessian_not_pd" in r["flags2"]], B["nonpd"], "B", "non-PD Hessian, stratified by cell")
    near = [r for r in pool if not _warned(r, wf) and 1e-6 < r["sigma2_F"] <= B["near_null_max_sigma2F"]]
    round_robin(near, B["near_null_unwarned"], "B", "unwarned near-null control, stratified by cell")
    for r in sorted((r for r in pool if not _warned(r, wf)), key=lambda r: (-r["sigma2_F"], r["job_id"]))[:B["large_sigma_unwarned"] + 0]:
        add("B", "unwarned control with the largest sigma2_F", r)
    for c in cfg["selection"]["tier_C"]:
        sel.append(dict(tier="C", why="main B2 fit missed the decrement tolerance", kind="main", scenario=c["scenario"], N=c["N"],
                        rep=c["rep"], job_id=f"main__{c['scenario']}__N{c['N']}__r{c['rep']}"))
    counts = {t: sum(s["tier"] == t for s in sel) for t in "ABC"}
    return {"counts": counts, "n_datasets": len(sel), "selected": sel}


def select_cli(config_path: str) -> int:
    cfg = load_yaml(config_path)
    s = select(cfg)
    out = Path(cfg["out_dir"]); out.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out / "selection.json", s)
    print(f"selected {s['n_datasets']} datasets {s['counts']} -> {out / 'selection.json'}")
    for x in s["selected"]:
        print(f"  {x['tier']} {x['job_id']} ({x['why']})")
    return 0


# ---------------------------------------------------------------------------------------------- per-dataset checks
class _SubPM:
    def __init__(self, pm, free):
        self.lb, self.ub, self.free, self.full = pm.lb[free], pm.ub[free], free, pm

    def project_grad(self, x, g, tol=1e-9):
        pg = g.copy()
        pg[(x <= self.lb + tol) & (g > 0)] = 0.0
        pg[(x >= self.ub - tol) & (g < 0)] = 0.0
        return pg


class _Fixed:
    """Objective with one coordinate held fixed (profile likelihood), usable by kt_trial.fit._one_start."""

    def __init__(self, obj: Objective, i: int, val: float, x_ref):
        self.obj, self.i, self.val = obj, i, val
        self.free = [j for j in range(obj.pm.n) if j != i]
        self.pm = _SubPM(obj.pm, self.free)
        self.scale, self.n_eval, self.bad = obj.scale, 0, 0
        self.x_ref = np.array(x_ref, float)

    def embed(self, y):
        x = self.x_ref.copy(); x[self.free] = y; x[self.i] = self.val
        return x

    def __call__(self, y):
        self.n_eval += 1
        f, g = self.obj(self.embed(y))
        return f, g[self.free]


def hessian_info(pm, obj, x, theta, cfg_fit, step):
    tol = cfg_fit["boundary_tol"]
    act = [i for i in range(pm.n) if pm.lb[i] + tol < x[i] < pm.ub[i] - tol]
    if "tau_F" in pm.names and theta.sigma2_F <= tol:
        act = [i for i in act if pm.names[i] != "tau_F"]
    S = obj.scale
    g = obj(x)[1][act] * S
    H = np.zeros((len(act), len(act)))
    for a, i in enumerate(act):
        h = step * max(1.0, abs(x[i])); xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        H[a] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[act] * S
    H = 0.5 * (H + H.T)
    w, V = np.linalg.eigh(H)
    v0 = V[:, 0]; top = np.argsort(-np.abs(v0))[:3]
    not_pd = bool(w.min() <= 0)
    dec = float("nan") if not_pd else float(0.5 * g @ np.linalg.solve(H, g))
    return {"step": step, "n_active": len(act), "min_eig": float(w.min()), "max_eig": float(w.max()),
            "cond": float(w.max() / w.min()) if w.min() > 0 else None, "hessian_not_pd": not_pd, "newton_decrement": dec,
            "min_eig_vector_top": [(pm.names[act[k]], float(v0[k])) for k in top]}


def profile_tau(pm, obj, x_star, cfg_fit, cfg_add, rng):
    it = pm.names.index("tau_F")
    grid = np.exp(np.linspace(np.log(cfg_add["lo"]), np.log(cfg_add["hi"]), cfg_add["n"]))
    rows = []
    for tau in grid:
        fx = _Fixed(obj, it, np.log(tau), x_star)          # tau_F is a log coordinate in ParamMap (checked below)
        best = None
        for s in range(cfg_add["n_starts"]):
            y0 = np.array(x_star, float)[fx.free]
            if s > 0:
                y0 = y0 + rng.normal(0.0, cfg_add["jitter_sd"], size=y0.shape)
            r = _one_start(fx, y0, cfg_fit)
            if r["ok"] and (best is None or r["ll"] > best["ll"]):
                best = r
        rows.append({"tau_F": float(tau), "ll": None if best is None else float(best["ll"]),
                     "converged": None if best is None else bool(best["converged"])})
    return rows


def _cell_clrs(results, sid, N):
    return {(r["rep"], r["b"]): r["clr"] for r in load_nulls(results) if r["scenario"] == sid and r["N"] == N}


def p_effect(results, sid, N, rep, b, clr_new, clr_obs):
    cell = {k: v for k, v in _cell_clrs(results, sid, N).items() if k[0] == rep}
    old = np.array(list(cell.values()))
    new = np.array([clr_new if k == (rep, b) else v for k, v in cell.items()])
    f = lambda a: (1.0 + float((a >= clr_obs).sum())) / (len(a) + 1.0)
    return {"p_registered": f(old), "p_with_improved_fit": f(new), "B": len(old)}


def check_dataset(item: dict, cfg: dict) -> dict:
    t0 = time.time()
    s1 = load_yaml(cfg["exp1"]["stage_config"])
    sid, N, rep = item["scenario"], item["N"], item["rep"]
    ms = s1["master_seed"]
    cfg1 = scenario_cfg(s1, sid)
    K = cfg1["design"]["n_skills"]
    ts = build_templates(cfg1); G = len(ts)
    fitenv = read_json(Path(cfg["exp1"]["results"]) / "jobs" / f"fit__{sid}__N{N}__r{rep}.json")["result"]
    if item["kind"] == "null":
        b = item["b"]
        seed = (sid, N, rep, "null", b)
        sim = simulate(null_config(cfg1), N, seed, ms, ts, theta=Theta.from_dict(fitenv["fits"]["B1"]["theta"]))
    else:
        seed = (sid, N, rep)
        sim = simulate(cfg1, N, ("data", sid, N, rep), ms, ts)
    pc = pair_counts(sim.Y, sim.template_id, G)
    f1 = fit_model("B1", ts, pc, cfg1["fit"], K, seed, ms)
    f2 = fit_model("B2", ts, pc, cfg1["fit"], K, seed, ms, warm=Theta.from_dict(f1["theta"]), null_fit=f1)
    clr = 2.0 * (f2["ll"] - f1["ll"])
    out = {"item": item, "runtime_fit": time.time() - t0, "clr_recomputed": clr, "sigma2_F": f2["theta"]["sigma2_F"],
           "tau_F": f2["theta"]["tau_F"], "flags_B2": f2["flags"], "flags_B1": f1["flags"], "ll_B1": f1["ll"], "ll_B2": f2["ll"]}
    if item["kind"] == "null":
        sv = item["saved"]; tol = cfg["repro_tolerance"]
        out["reproduces_registered"] = bool(abs(clr - sv["clr"]) <= tol["clr_abs"] * max(1.0, abs(sv["clr"]))
                                            and abs(f2["theta"]["sigma2_F"] - sv["sigma2_F"]) <= tol["sigma2_F_abs"])
    else:
        sv = fitenv["fits"]["B2"]
        out["reproduces_registered"] = bool(abs(f2["ll"] - sv["ll"]) <= 1e-6 * abs(sv["ll"]))
    pm = ParamMap("B2", K); obj = Objective(pm, ts, pc)
    x = np.array(f2["x"]); theta = Theta.from_dict(f2["theta"])
    g = obj(x)[1] * obj.scale
    pg = pm.project_grad(x, g)
    out["kkt"] = {"projected_gradient_inf": float(np.abs(pg).max()), "boundary_hits": f2["boundary_hits"],
                  "worst_coordinate": pm.names[int(np.abs(pg).argmax())]}
    out["hessian"] = [hessian_info(pm, obj, x, theta, cfg1["fit"], h) for h in cfg["hessian_steps"]]
    rng = rng_for(cfg["master_seed"], "addendum", sid, N, rep, item.get("b", -1))
    assert pm.names.index("tau_F") is not None
    prof = profile_tau(pm, obj, x, cfg1["fit"], cfg["tau_profile"], rng)
    out["tau_profile"] = prof
    best = max((r["ll"] for r in prof if r["ll"] is not None), default=f2["ll"])
    out["profile_best_ll"] = best
    out["attained_improvement_B2"] = float(max(0.0, best - f2["ll"]))
    # B1 re-check from perturbed starts (monotonicity is not automatic when both fits can change)
    pm1 = ParamMap("B1", K); obj1 = Objective(pm1, ts, pc); x1 = np.array(f1["x"]); b1_best = f1["ll"]
    for s in range(cfg["b1_extra_starts"]):
        r = _one_start(obj1, x1 + rng.normal(0.0, cfg["tau_profile"]["jitter_sd"], size=x1.shape), cfg1["fit"])
        if r["ok"]:
            b1_best = max(b1_best, r["ll"])
    out["attained_improvement_B1"] = float(max(0.0, b1_best - f1["ll"]))
    clr_new = 2.0 * (f2["ll"] + out["attained_improvement_B2"] - (f1["ll"] + out["attained_improvement_B1"]))
    out["clr_with_improved_fits"] = clr_new
    if item["kind"] == "null":
        obs_env = fitenv
        clr_obs = 2.0 * (obs_env["fits"]["B2"]["ll"] - obs_env["fits"]["B1"]["ll"])
        out["p_effect"] = p_effect(cfg["exp1"]["results"], sid, N, rep, item["b"], clr_new, clr_obs)
        out["p_effect"]["clr_observed_registered"] = clr_obs
    out["runtime"] = time.time() - t0
    return out


def _worker(args):
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    item, cfg, out_dir = args
    p = Path(out_dir) / "datasets" / (item["job_id"] + ".json")
    try:
        res = check_dataset(item, cfg)
        res["status"] = "ok"
    except Exception as e:
        res = {"item": item, "status": "error", "error": repr(e), "trace": traceback.format_exc(limit=5)}
    write_json_atomic(p, res)
    return item["job_id"], res["status"], res.get("runtime", 0.0)


def run_cli(config_path: str, workers: int, limit: int | None, tiers: list[str] | None) -> int:
    cfg = load_yaml(config_path)
    out_dir = Path(cfg["out_dir"])
    if (out_dir / "selection.json").exists():
        sel = read_json(out_dir / "selection.json")
    else:
        sel = select(cfg); write_json_atomic(out_dir / "selection.json", sel)
    items = [x for x in sel["selected"] if (tiers is None or x["tier"] in tiers)]
    if limit:
        items = items[:limit]
    todo = [x for x in items if not (out_dir / "datasets" / (x["job_id"] + ".json")).exists()
            or read_json(out_dir / "datasets" / (x["job_id"] + ".json")).get("status") != "ok"]
    print(f"{len(items)} datasets selected for this call, {len(todo)} to run ({len(items) - len(todo)} already done)")
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for jid, st, rt in ex.map(_worker, [(x, cfg, str(out_dir)) for x in todo]):
            print(f"  {jid} {st} {rt:.0f}s [{(time.time() - t0) / 60:.1f} min]", flush=True)
    return 0


# ---------------------------------------------------------------------------------------------- addendum summary
def summarize_cli(config_path: str) -> int:
    """Aggregate the per-dataset checks. Only datasets whose registered result was reproduced are interpreted; the rest are
    listed as provenance failures (the regeneration environment differs from the one that produced the registered data)."""
    cfg = load_yaml(config_path)
    out_dir = Path(cfg["out_dir"])
    rows, bad = [], []
    for f in sorted(glob.glob(str(out_dir / "datasets" / "*.json"))):
        r = read_json(Path(f))
        if r.get("status") != "ok":
            bad.append({"job_id": r["item"]["job_id"], "status": "error", "error": r.get("error")}); continue
        rows.append(r)
    repro = [r for r in rows if r["reproduces_registered"]]
    fail = [r for r in rows if not r["reproduces_registered"]]
    def line(r):
        pe = r.get("p_effect") or {}
        h = r["hessian"]
        return {"job_id": r["item"]["job_id"], "tier": r["item"]["tier"], "why": r["item"]["why"],
                "registered": r["item"].get("saved"), "clr_recomputed": r["clr_recomputed"], "sigma2_F": r["sigma2_F"], "tau_F": r["tau_F"],
                "flags_B2": r["flags_B2"], "kkt_projected_gradient_inf": r["kkt"]["projected_gradient_inf"],
                "boundary_hits": r["kkt"]["boundary_hits"],
                "hessian_min_eig_by_step": {str(x["step"]): x["min_eig"] for x in h},
                "hessian_not_pd_by_step": {str(x["step"]): x["hessian_not_pd"] for x in h},
                "newton_decrement_by_step": {str(x["step"]): x["newton_decrement"] for x in h},
                "attained_improvement_B2": r["attained_improvement_B2"], "attained_improvement_B1": r["attained_improvement_B1"],
                "clr_with_improved_fits": r["clr_with_improved_fits"], "p_effect": pe,
                "profile_best_tau": max((x for x in r["tau_profile"] if x["ll"] is not None), key=lambda x: x["ll"], default={}).get("tau_F")}
    summary = {"n_datasets": len(rows), "n_errors": len(bad), "n_reproduced": len(repro), "n_not_reproduced": len(fail),
               "interpreted": [line(r) for r in repro],
               "provenance_failures": [{"job_id": r["item"]["job_id"], "clr_recomputed": r["clr_recomputed"],
                                        "registered_clr": (r["item"].get("saved") or {}).get("clr")} for r in fail],
               "errors": bad}
    tiers = {}
    for x in summary["interpreted"]:
        t = tiers.setdefault(x["tier"], {"n": 0, "max_attained_B2": 0.0, "p_changed": 0})
        t["n"] += 1; t["max_attained_B2"] = max(t["max_attained_B2"], x["attained_improvement_B2"])
        pe = x["p_effect"]
        t["p_changed"] += int(bool(pe) and pe["p_registered"] != pe["p_with_improved_fit"])
    summary["by_tier"] = tiers
    write_json_atomic(out_dir / "summary.json", summary)
    L = ["# Experiment 1 numerical addendum: summary", "",
         f"- datasets {len(rows)}; reproduced the registered result {len(repro)}; NOT reproduced {len(fail)} (provenance failures, not interpreted); errors {len(bad)}", ""]
    if fail:
        L += ["**Provenance failure**: the regenerated dataset does not reproduce the registered CLR for "
              f"{len(fail)} dataset(s); these are not evidence about the registered fits. First: {summary['provenance_failures'][0]}", ""]
    L += [f"- by tier (reproduced datasets only): {tiers}", "",
          "| tier | dataset | registered CLR | B2 flags | KKT inf-norm | min Hessian eig (steps) | attained B2 gain | attained B1 gain | p registered -> with improved fits |",
          "|---|---|---|---|---|---|---|---|---|"]
    for x in summary["interpreted"]:
        pe = x["p_effect"]
        L.append(f"| {x['tier']} | {x['job_id']} | {_fmt((x['registered'] or {}).get('clr'))} | {x['flags_B2']} | {_fmt(x['kkt_projected_gradient_inf'])} | "
                 f"{x['hessian_min_eig_by_step']} | {_fmt(x['attained_improvement_B2'])} | {_fmt(x['attained_improvement_B1'])} | "
                 f"{_fmt(pe.get('p_registered'))} -> {_fmt(pe.get('p_with_improved_fit'))} |")
    (out_dir / "summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'summary.json'} ({len(repro)} interpreted, {len(fail)} provenance failures, {len(bad)} errors)")
    return 0


def _fmt(x):
    return "NA" if x is None else (f"{x:.4g}" if isinstance(x, float) else str(x))
