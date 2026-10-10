"""Provisional decision rules of Experiment 5 (X5-D06; frozen only after the Opus pilot review): gates G1-G3 and H5a-H5e, computed from the job
envelopes of a results directory.

Diagnostic decision: carry-over score test at the B2 fit, tau_x = PRIMARY_TAU, chi2_1 p < 0.05. F-test decision (descriptive 2 x 2 tables, E3): T above the
per-N q95 of Experiment 4's registered V2 2PL bootstrap statistics (X5-D03). E4's F test is judged by its own warp-speed bootstrap
(difficulty_free.calibration, X3-D15). The H5a verdict thresholds are NOT given in X5-D06: H5a is reported without a verdict until Opus sets one.
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np

from kt_trial.runner import read_json
from kt_trial.summarize import clopper_pearson
from difficulty_free import calibration as CAL
from difficulty_free.rules import bias_rule

PRIMARY_TAU = "2"
ALPHA = 0.05
G1_MAX_BAD = 0.05
NS = (300, 1000)
LEVEL_CELLS = ("E1", "E2")
POWER_CELLS = ("E3", "E5")
STAGE0_POINT = {"E1": "Fpres_k0", "E2": "Fabs_k0", "E3": "Fabs_k0.25_tD10", "E4": "Fabs_k0.1_tD2", "E5": "Fpres_k0.25_tD10", "E6": "S8n_k0"}
BOUND_TAU_F = 999.0


def load(results_dir) -> dict:
    rd = Path(results_dir)
    envs = [read_json(Path(f)) for f in sorted(glob.glob(str(rd / "jobs" / "*.json")))]
    man = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    recs = [e["result"] for e in envs if e["status"] == "ok"]
    return {"envs": envs, "manifest": man, "recs": recs}


def null_q95(path, N_list=NS) -> dict:
    """Per-N q95 of Experiment 4's registered V2 2PL T* (X5-D03)."""
    out = {}
    for N in N_list:
        ts = []
        for f in sorted(Path(path, "jobs").glob(f"warp__V2__N{N}__r*.json")):
            e = read_json(f)
            r = e["result"].get("twopl", {}) if e["status"] == "ok" else {}
            if r.get("T_star") is not None and not r.get("star_failed") and r.get("star_converged", False):
                ts.append(r["T_star"])
        out[N] = float(np.quantile(ts, 0.95)) if len(ts) >= 10 else None
    return out


def _b2_ok(r) -> bool:
    b = r["arms"]["B2"]
    return bool(b.get("status") != "failed" and b.get("converged", False))


def _diag_ok(r) -> bool:
    d = r["diag"].get("B2", {})
    return bool("by_tau_x" in d and PRIMARY_TAU in d["by_tau_x"] and np.isfinite(d["by_tau_x"][PRIMARY_TAU]["p"]))


def _valid(r) -> bool:
    """A dataset enters a cell's statistics if its B2 fit converged and the diagnostic ran; warp units also need a converged bootstrap fit."""
    if not (_b2_ok(r) and _diag_ok(r)):
        return False
    if "star_failed" in r or "fit_failed" in r:
        return not r.get("fit_failed") and not r.get("star_failed", True) and bool(r.get("converged")) and bool(r.get("star_converged"))
    return True


def _cell(recs, sid, N=None):
    return [r for r in recs if r["scenario"] == sid and (N is None or r["N"] == N)]


def _reject(r, tau=PRIMARY_TAU) -> bool:
    return bool(r["diag"]["B2"]["by_tau_x"][tau]["p"] < ALPHA)


def _share(rs, tau=PRIMARY_TAU) -> dict:
    ok = [r for r in rs if _valid(r)]
    k = int(sum(_reject(r, tau) for r in ok))
    n = len(ok)
    lo, hi = clopper_pearson(k, n)
    return {"k": k, "n": n, "share": k / n if n else None, "cp95": [lo, hi]}


def level_verdict(lo: float, hi: float) -> str:
    if lo > ALPHA:
        return "liberal"
    if lo <= ALPHA <= hi and hi <= 0.10:
        return "consistent with 5 %"
    return "inconclusive"


def _pooled(recs, cells, tau=PRIMARY_TAU):
    s = _share([r for sid in cells for r in _cell(recs, sid)], tau)
    s["verdict"] = level_verdict(*s["cp95"]) if s["n"] else "not evaluable (no data)"
    if s["n"] and s["cp95"][1] < ALPHA:
        s["note"] = "conservative: CI entirely below 0.05"
    return s


def _warp_rows(recs, sid, N=None):
    rows = []
    for r in _cell(recs, sid, N):
        if "fit_failed" not in r:
            continue
        rows.append(dict(fit_failed=bool(r["fit_failed"]), star_failed=bool(r.get("star_failed", True)),
                         converged=bool(r.get("converged", False)) and bool(r.get("star_converged", False)), T=r.get("T"), T_star=r.get("T_star"),
                         sigma2_F=r.get("sigma2_F"), tau_F=r.get("tau_F"), sigma2_F_star=r.get("sigma2_F_star_boot"), tau_F_star=r.get("tau_F_star"),
                         N=r["N"], rep=r["rep"]))
    return rows


def _stage0_predictions(path):
    p = Path(path) if path else None
    if not p or not p.exists():
        return None
    S = read_json(p)["points"]
    out = {}
    for cell, pt in STAGE0_POINT.items():
        r = S.get(pt)
        if r:
            d = r.get("diag_B2", {}).get(PRIMARY_TAU + ".0", r.get("diag_B2", {}).get(PRIMARY_TAU, {}))
            out[cell] = {"sigma2_F_star": r["sigma2_F_star"], "tau_F": r["tau_F"], "E_T": r["E_T"], "E_T_over_q95": r["E_T_over_q95"],
                         "diag_power": d.get("power") if d else None}
    return out


def evaluate(results_dir) -> dict:
    L = load(results_dir)
    recs, envs = L["recs"], L["envs"]
    sc = L["manifest"].get("stage_config", {})
    q95 = null_q95(sc["null_reference"]) if sc.get("null_reference") and Path(sc["null_reference"]).exists() else {N: None for N in NS}
    R = {"gates": {}, "rules": {}, "descriptives": {}, "null_q95": {str(k): v for k, v in q95.items()}}
    th = (L["manifest"].get("env") or {}).get("threads") or {}
    hashes = {e.get("code_hash") for e in envs}
    R["gates"]["G2 single code hash"] = {"ok": len(hashes) == 1 and (not L["manifest"].get("code_hash") or hashes == {L["manifest"]["code_hash"]}),
                                         "hashes": sorted(str(h)[:12] for h in hashes)}
    R["gates"]["G3 single-thread BLAS"] = {"ok": bool(th and all(str(v) == "1" for v in th.values())), "threads": th}
    nerr = sum(e["status"] != "ok" for e in envs)
    R["gates"]["no job errors"] = {"ok": nerr == 0, "errors": nerr}
    cells = sorted({r["scenario"] for r in recs})
    for sid in cells:
        for N in NS:
            rs = _cell(recs, sid, N)
            if not rs:
                continue
            n_ok = sum(_valid(r) for r in rs)
            R["gates"][f"G1 {sid} N={N}"] = {"ok": bool(1 - n_ok / len(rs) <= G1_MAX_BAD), "n": len(rs), "n_valid": n_ok, "share_bad": 1 - n_ok / len(rs)}
    gates = R["gates"]
    g1 = lambda sid, Ns=NS: all(gates.get(f"G1 {sid} N={N}", {"ok": False})["ok"] for N in Ns)

    # H5a (no verdict thresholds in X5-D06)
    h5a = {"verdict": "descriptive (thresholds pending Opus)", "E3": {}, "E4": {}}
    for N in NS:
        T = [r["T"] for r in _cell(recs, "E3", N) if _valid(r) and r.get("T") is not None]
        if T and q95.get(N):
            k = int(sum(t > q95[N] for t in T)); lo, hi = clopper_pearson(k, len(T))
            h5a["E3"][f"N={N}"] = {"k": k, "n": len(T), "share": k / len(T), "cp95": [lo, hi], "q95_ref": q95[N]}
        T4 = [r["T"] for r in _cell(recs, "E4", N) if _valid(r) and r.get("T") is not None]
        if T4 and q95.get(N):
            k = int(sum(t > q95[N] for t in T4)); lo, hi = clopper_pearson(k, len(T4))
            h5a["E4"][f"ref_q95_N={N}"] = {"k": k, "n": len(T4), "share": k / len(T4), "cp95": [lo, hi]}
    rows4 = _warp_rows(recs, "E4")
    if rows4:
        h5a["E4"]["warp_own_T_star_pooled"] = CAL._cell_stats(rows4, seed=1)
        for N in NS:
            rN = _warp_rows(recs, "E4", N)
            if rN:
                h5a["E4"][f"warp_own_T_star_N={N}"] = CAL._cell_stats(rN, seed=2 + N)
    R["rules"]["H5a"] = h5a

    # H5b
    pw = {}
    for sid in POWER_CELLS:
        for N in NS:
            if _cell(recs, sid, N):
                pw[f"{sid} N={N}"] = _share(_cell(recs, sid, N))
    prim = [pw.get(f"{sid} N=1000") for sid in POWER_CELLS]
    if any(p is None or not p["n"] for p in prim) or not all(g1(sid, (1000,)) for sid in POWER_CELLS):
        v = "not evaluable (gate or missing cells)"
    elif all(p["share"] >= 0.8 and p["cp95"][0] > 0.5 for p in prim):
        v = "supported"
    elif any(p["share"] < 0.8 for p in prim):
        v = "not supported"
    else:
        v = "inconclusive"
    R["rules"]["H5b"] = {"verdict": v, "cells": pw, "E4_descriptive": {f"N={N}": _share(_cell(recs, "E4", N)) for N in NS if _cell(recs, "E4", N)}}

    # H5c, H5d
    ok = all(g1(sid) for sid in LEVEL_CELLS if _cell(recs, sid))
    pc = _pooled(recs, LEVEL_CELLS)
    R["rules"]["H5c"] = {"verdict": pc["verdict"] if ok else "not evaluable (gate)", "pooled": pc,
                         "per_cell": {f"{sid} N={N}": _share(_cell(recs, sid, N)) for sid in LEVEL_CELLS for N in NS if _cell(recs, sid, N)}}
    pe = _pooled(recs, ("E6",))
    R["rules"]["H5d"] = {"verdict": pe["verdict"] if g1("E6") or not _cell(recs, "E6") else "not evaluable (gate)", "pooled": pe,
                         "per_N": {f"N={N}": _share(_cell(recs, "E6", N)) for N in NS if _cell(recs, "E6", N)}}

    # H5e (descriptive)
    h5e = {}
    for N in NS:
        errs = [r["arms"]["B2"]["sigma2_F_error_vs_star"] for r in _cell(recs, "E5", N) if _valid(r)]
        if len(errs) >= 2:
            h5e[f"N={N}"] = bias_rule(errs, 0.0)
    R["rules"]["H5e"] = {"verdict": "descriptive", "cells": h5e}

    # descriptives
    D = R["descriptives"]
    D["stage0_predictions"] = _stage0_predictions(sc.get("stage0_summary"))
    D["secondary_tau_x_rejection"] = {f"{sid} N={N} tau_x={t}": _share(_cell(recs, sid, N), t) for sid in cells for N in NS if _cell(recs, sid, N) for t in ("5", "10")}
    D["f_by_diagnostic_2x2"] = {}
    for sid in cells:
        for N in NS:
            rs = [r for r in _cell(recs, sid, N) if _valid(r) and r.get("T") is not None]
            if rs and q95.get(N):
                a = np.array([[r["T"] > q95[N], _reject(r)] for r in rs])
                D["f_by_diagnostic_2x2"][f"{sid} N={N}"] = {"n": len(rs), "F_only": int((a[:, 0] & ~a[:, 1]).sum()), "diag_only": int((~a[:, 0] & a[:, 1]).sum()),
                                                            "both": int((a[:, 0] & a[:, 1]).sum()), "neither": int((~a[:, 0] & ~a[:, 1]).sum())}
    D["p_value_hist_E1_E2"] = np.histogram([r["diag"]["B2"]["by_tau_x"][PRIMARY_TAU]["p"] for r in recs if r["scenario"] in LEVEL_CELLS and _valid(r)],
                                           bins=np.linspace(0, 1, 11))[0].tolist()
    D["eta_hat_mean"] = {f"{sid} N={N}": float(np.mean([r["diag"]["B2"]["by_tau_x"][PRIMARY_TAU]["eta_hat"] for r in _cell(recs, sid, N) if _valid(r)]))
                         for sid in cells for N in NS if any(_valid(r) for r in _cell(recs, sid, N))}
    D["fit_summary"] = {f"{sid} N={N}": _fit_summary(_cell(recs, sid, N)) for sid in cells for N in NS if _cell(recs, sid, N)}
    R["frozen_rules_version"] = "X5-D06 (provisional)"
    return R


def _fit_summary(rs) -> dict:
    b2 = [r["arms"]["B2"] for r in rs if r["arms"]["B2"].get("status") != "failed"]
    if not b2:
        return {"n": len(rs)}
    return {"n": len(rs), "sigma2_F_mean": float(np.mean([f["theta"]["sigma2_F"] for f in b2])),
            "sigma2_F_error_vs_star_mean": float(np.mean([f["sigma2_F_error_vs_star"] for f in b2])),
            "tau_F_median": float(np.median([f["theta"]["tau_F"] for f in b2])),
            "tau_F_at_bound": int(sum(f["theta"]["tau_F"] >= BOUND_TAU_F for f in b2)),
            "T_median": float(np.median([r["T"] for r in rs if r.get("T") is not None])) if any(r.get("T") is not None for r in rs) else None,
            "ridge_converged_B2": int(sum("converged_on_ridge" in f["flags"] for f in b2)),
            "not_converged_B2": int(sum(not f.get("converged", False) for f in b2)),
            "polished_B1_B2": int(sum(r["arms"][m].get("n_polished", 0) for r in rs for m in ("B1", "B2") if r["arms"][m].get("status") != "failed"))}


def markdown(R: dict) -> list[str]:
    f = lambda x, d=3: "NA" if x is None else f"{x:.{d}f}"
    L = ["## Provisional rules (X5-D06)", "", "### Gates", "", "| gate | ok | detail |", "|---|---|---|"]
    for k, g in R["gates"].items():
        L.append(f"| {k} | {'yes' if g['ok'] else '**NO**'} | {', '.join(f'{a}={b}' for a, b in g.items() if a != 'ok')} |")
    L += ["", "### Verdicts", "", "| rule | verdict |", "|---|---|"] + [f"| {k} | **{r['verdict']}** |" for k, r in R["rules"].items()]
    L += ["", f"Null reference q95 (Experiment 4 V2 2PL T*): {R['null_q95']}", ""]
    for key in ("H5b",):
        L += ["H5b diagnostic rejection shares (tau_x = " + PRIMARY_TAU + ", B2): "]
        L += [f"- {c}: {v['k']}/{v['n']} = {f(v['share'], 2)}, CP {[round(x, 3) for x in v['cp95']]}" for c, v in R["rules"][key]["cells"].items()]
        L += [f"- E4 (descriptive) {c}: {v['k']}/{v['n']} = {f(v['share'], 2)}, CP {[round(x, 3) for x in v['cp95']]}" for c, v in R["rules"][key]["E4_descriptive"].items()]
    for key in ("H5c", "H5d"):
        p = R["rules"][key]["pooled"]
        L += ["", f"{key}: pooled {p.get('k')}/{p.get('n')} = {f(p.get('share'), 3)}, CP {p.get('cp95')}, {p.get('verdict')} {p.get('note', '')}"]
    L += ["", f"H5a: {R['rules']['H5a']}", "", f"H5e: {R['rules']['H5e']}", "", f"Descriptives: {R['descriptives']}", ""]
    return L
