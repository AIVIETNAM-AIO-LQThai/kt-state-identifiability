"""Frozen decision rules of Experiment 4 (X4-D08 (4)): gates G1/G2, PH4a-PH4e, computed from the job envelopes of a results directory.

Estimand: sigma2_F* = g^2 sigma2_F per replication (stored in every fit job). Bias rules use errors (estimate - sigma2_F*) against 0, +-0.04.
Calibration rules reuse difficulty_free.calibration (strict '>', pairs bootstrap, X3-D15 verdicts). Nothing here is tuned on the pilot.
"""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
from scipy import stats

from kt_trial.runner import read_json
from difficulty_free import calibration as CAL
from difficulty_free.rules import BIAS_TOL, bias_rule

G1_MAX_BAD = 0.05
N_BOOT = 2000
RIDGE_DELTA = 0.25          # X4-D09 sensitivity margin in T units
NS = (300, 1000)


def load(results_dir) -> dict:
    rd = Path(results_dir)
    envs = [read_json(Path(f)) for f in sorted(glob.glob(str(rd / "jobs" / "*.json")))]
    man = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    return {"envs": envs, "manifest": man,
            "fits": [e["result"] for e in envs if e["status"] == "ok" and e["job"]["kind"] == "fit"],
            "warps": [e["result"] for e in envs if e["status"] == "ok" and e["job"]["kind"] == "warp"]}


def _b2(r, arm):
    return r["arms"][arm]["B2"]


def _fit_gate(reps, arm):
    n = len(reps)
    bad = sum(_b2(r, arm).get("status") == "failed" or not _b2(r, arm).get("converged", False) for r in reps)
    return {"ok": bool(n > 0 and bad / n <= G1_MAX_BAD), "n": n, "n_bad": int(bad), "share_bad": bad / n if n else 1.0}


def _warp_rows(warps, sid, est, N=None):
    rows = []
    for w in warps:
        if w["scenario"] != sid or est not in w or (N is not None and w["N"] != N):
            continue
        e = w[est]
        rows.append(dict(fit_failed=bool(e.get("fit_failed")), star_failed=bool(e.get("star_failed", True)),
                         converged=bool(e.get("converged", False)) and bool(e.get("star_converged", False)),
                         ridge=bool(e.get("ridge_converged", False)), ridge_star=bool(e.get("star_ridge_converged", False)),
                         T=e.get("T"), T_star=e.get("T_star"), sigma2_F=e.get("sigma2_F"), tau_F=e.get("tau_F"),
                         sigma2_F_star=e.get("sigma2_F_star_boot"), tau_F_star=e.get("tau_F_star"), N=w["N"], rep=w["rep"]))
    return rows


def _cal(rows, seed):
    return CAL._cell_stats(rows, seed=seed) if rows else {"n_datasets": 0, "n_ok": 0, "verdict": "not evaluable (no data)", "gate_ok": False}


def _shift(rows, which):
    """X4-D09 sensitivity: 'plus' adds RIDGE_DELTA to T of units whose observed B2 fit is converged on the ridge (most liberal);
    'minus' adds it to T* of units whose bootstrap B2 fit is converged on the ridge (most conservative)."""
    out = []
    for r in rows:
        r = dict(r)
        if which == "plus" and r.get("ridge") and r["T"] is not None:
            r["T"] = r["T"] + RIDGE_DELTA
        if which == "minus" and r.get("ridge_star") and r["T_star"] is not None:
            r["T_star"] = r["T_star"] + RIDGE_DELTA
        out.append(r)
    return out


def _cal_sens(rows, seed):
    """Primary X3-D15 cell statistics plus the two ridge-sensitivity verdicts; 'fragile' if either differs from the primary verdict."""
    c = _cal(rows, seed)
    sp, sm = _cal(_shift(rows, "plus"), seed), _cal(_shift(rows, "minus"), seed)
    c = dict(c, sens_plus_verdict=sp["verdict"], sens_minus_verdict=sm["verdict"], alpha_hat_plus=sp.get("alpha_hat"), alpha_hat_minus=sm.get("alpha_hat"),
             fragile=bool(not c["verdict"].startswith("not evaluable") and (sp["verdict"] != c["verdict"] or sm["verdict"] != c["verdict"])),
             n_ridge_obs=int(sum(r.get("ridge", False) for r in rows)), n_ridge_star=int(sum(r.get("ridge_star", False) for r in rows)))
    return c


def _alpha(rows):
    ok = [r for r in rows if not r["fit_failed"] and not r["star_failed"] and r["converged"]]
    return ok, np.array([r["T"] for r in ok]), np.array([r["T_star"] for r in ok])


def paired_delta(rows_free, rows_2pl, B=N_BOOT, seed=7) -> dict:
    """Delta = alpha-hat(1PL-free) - alpha-hat(2PL) on the datasets valid for both; pairs bootstrap resamples datasets jointly."""
    a = {(r["N"], r["rep"]): r for r in _alpha(rows_free)[0]}
    b = {(r["N"], r["rep"]): r for r in _alpha(rows_2pl)[0]}
    keys = sorted(set(a) & set(b))
    if len(keys) < 10:
        return {"n": len(keys), "verdict": "not evaluable"}
    T1, S1 = np.array([a[k]["T"] for k in keys]), np.array([a[k]["T_star"] for k in keys])
    T2, S2 = np.array([b[k]["T"] for k in keys]), np.array([b[k]["T_star"] for k in keys])
    d0 = CAL.alpha_hat(T1, S1) - CAL.alpha_hat(T2, S2)
    rng = np.random.default_rng(seed)
    vals = np.empty(B)
    for i in range(B):
        j = rng.integers(0, len(keys), len(keys))
        vals[i] = CAL.alpha_hat(T1[j], S1[j]) - CAL.alpha_hat(T2[j], S2[j])
    ci = [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]
    return {"n": len(keys), "delta": float(d0), "ci95": ci, "ci_above_zero": bool(ci[0] > 0)}


def _errors(reps, arm):
    return np.array([_b2(r, arm)["sigma2_F_error_vs_star"] for r in reps if _b2(r, arm).get("status") != "failed"])


def _cell_fits(L, sid, N):
    return [r for r in L["fits"] if r["scenario"] == sid and r["N"] == N]


def evaluate(results_dir, frozen_sha_ok: bool | None = None) -> dict:
    L = load(results_dir)
    R = {"gates": {}, "rules": {}, "descriptives": {}}
    env = (L["manifest"].get("env") or {})
    th = env.get("threads") or {}
    R["gates"]["G2 single code hash"] = {"ok": len({e.get("code_hash") for e in L["envs"]}) == 1 and
                                         (not L["manifest"].get("code_hash") or {e.get("code_hash") for e in L["envs"]} == {L["manifest"]["code_hash"]}),
                                         "hashes": sorted({str(e.get("code_hash"))[:12] for e in L["envs"]})}
    if frozen_sha_ok is not None:
        R["gates"]["G2 frozen sha"] = {"ok": bool(frozen_sha_ok)}
    R["gates"]["G3 single-thread BLAS"] = {"ok": bool(th and all(str(v) == "1" for v in th.values())), "threads": th}
    nerr = sum(e["status"] != "ok" for e in L["envs"])
    R["gates"]["no job errors"] = {"ok": nerr == 0, "errors": nerr}
    for sid in ("V1", "V5"):
        for N in NS:
            reps = _cell_fits(L, sid, N)
            for arm in ("twopl", "free1"):
                if reps:
                    R["gates"][f"G1 {sid} N={N} {arm}"] = _fit_gate(reps, arm)
    for sid, ests in (("V2", ("twopl",)), ("V4", ("twopl", "free1"))):
        for est in ests:
            rows = _warp_rows(L["warps"], sid, est)
            if rows:
                n_ok = len(_alpha(rows)[0])
                R["gates"][f"G1 {sid} {est}"] = {"ok": bool(1 - n_ok / len(rows) <= G1_MAX_BAD), "n": len(rows), "n_ok": n_ok, "share_bad": 1 - n_ok / len(rows)}
    gates = R["gates"]
    gate_ok = lambda keys: all(gates[k]["ok"] for k in keys if k in gates) and all(k in gates for k in keys)

    # PH4a
    cells, keys = {}, []
    for sid in ("V1", "V5"):
        for N in NS:
            reps = _cell_fits(L, sid, N)
            if not reps:
                continue
            e2, e1 = _errors(reps, "twopl"), _errors(reps, "free1")
            cells[f"{sid} N={N}"] = {"twopl": bias_rule(e2, 0.0), "free1": bias_rule(e1, 0.0)}
            keys.append(f"G1 {sid} N={N} twopl")
    vs = [c["twopl"]["verdict"] for c in cells.values()]
    if not cells or not gate_ok(keys) or len(cells) < 4:
        v = "not evaluable (gate or missing cells)"
    elif all(x == "pass" for x in vs):
        v = "supported"
    elif any(x == "fail" for x in vs):
        v = "not supported"
    else:
        v = "inconclusive"
    R["rules"]["PH4a"] = {"verdict": v, "cells": cells}

    # PH4b
    r2, r1 = _warp_rows(L["warps"], "V4", "twopl"), _warp_rows(L["warps"], "V4", "free1")
    cal2, cal1 = _cal_sens(r2, 1), _cal_sens(r1, 1)
    dl = paired_delta(r1, r2)
    dl_s = {w: paired_delta(_shift(r1, w), _shift(r2, w)) for w in ("plus", "minus")}
    dl["sens_plus_ci_above_zero"] = dl_s["plus"].get("ci_above_zero"); dl["sens_minus_ci_above_zero"] = dl_s["minus"].get("ci_above_zero")
    dl["fragile"] = bool(dl.get("ci_above_zero") is not None and (dl_s["plus"].get("ci_above_zero") != dl["ci_above_zero"] or dl_s["minus"].get("ci_above_zero") != dl["ci_above_zero"]))
    per_n = {f"N={N}": {"twopl": _cal_sens(_warp_rows(L["warps"], "V4", "twopl", N), 2 + N), "free1": _cal_sens(_warp_rows(L["warps"], "V4", "free1", N), 2 + N)} for N in NS}
    if not gate_ok(["G1 V4 twopl"]):
        v = "not evaluable (gate)"
    elif cal2["verdict"] == "consistent with 5 %":
        v = "supported"
    elif cal2["verdict"] == "liberal":
        v = "not supported"
    elif dl.get("ci_above_zero"):
        v = "partly supported"
    else:
        v = "inconclusive"
    fragile_b = bool(cal2.get("fragile") or dl.get("fragile"))
    R["rules"]["PH4b"] = {"verdict": v, "fragile": fragile_b, "twopl_pooled": cal2, "free1_pooled": cal1, "paired_delta": dl, "per_N": per_n,
                          "note": "P(inconclusive | exactly calibrated) is about 0.4 at 150 pooled datasets (X4-F12)"}

    # PH4c
    rv2 = _warp_rows(L["warps"], "V2", "twopl")
    calc = _cal_sens(rv2, 3)
    v = ("not evaluable (gate)" if not gate_ok(["G1 V2 twopl"]) else "supported" if calc["verdict"] == "consistent with 5 %"
         else "not supported" if calc["verdict"] == "liberal" else "inconclusive")
    R["rules"]["PH4c"] = {"verdict": v, "fragile": bool(calc.get("fragile")), "V2_pooled": calc, "V2_plus_V4_twopl_pooled": _cal_sens(rv2 + r2, 4)}

    # PH4d (descriptive)
    d = {}
    rng = np.random.default_rng(11)
    for N in NS:
        reps = [r for r in _cell_fits(L, "V1", N) if _b2(r, "twopl").get("status") != "failed" and _b2(r, "free1").get("status") != "failed"]
        if len(reps) < 3:
            continue
        s2 = np.array([_b2(r, "twopl")["theta"]["sigma2_F"] for r in reps]); s1 = np.array([_b2(r, "free1")["theta"]["sigma2_F"] for r in reps])
        bs = [np.std(s2[i], ddof=1) / np.std(s1[i], ddof=1) for i in (rng.integers(0, len(reps), len(reps)) for _ in range(N_BOOT))]
        d[f"V1 N={N}"] = {"n": len(reps), "sd_ratio_2pl_over_free1": float(np.std(s2, ddof=1) / np.std(s1, ddof=1)),
                          "ci95": [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]}
    for sid in ("V1", "V5"):
        for N in NS:
            reps = [r for r in _cell_fits(L, sid, N) if _b2(r, "twopl").get("status") != "failed"]
            if reps:
                d[f"{sid} N={N} lambda"] = {"rmse_centred_log_lambda_mean": float(np.mean([_b2(r, "twopl")["lambda_recovery"]["rmse_centred_log_lambda"] for r in reps]))}
    R["rules"]["PH4d"] = {"verdict": "descriptive", "cells": d}

    # PH4e (descriptive)
    e = {}
    for N in NS:
        reps = [r for r in _cell_fits(L, "V5", N) if _b2(r, "twopl").get("status") != "failed" and _b2(r, "free1").get("status") != "failed"]
        if len(reps) < 3:
            continue
        diff = np.array([_b2(r, "free1")["sigma2_F_error_vs_star"] - _b2(r, "twopl")["sigma2_F_error_vs_star"] for r in reps])
        se = diff.std(ddof=1) / np.sqrt(len(diff)); t = stats.t.ppf(0.975, len(diff) - 1)
        e[f"V5 N={N}"] = {"n": len(reps), "mean_diff_free1_minus_2pl": float(diff.mean()), "ci95": [float(diff.mean() - t * se), float(diff.mean() + t * se)],
                          "bias_2pl": float(_errors(reps, "twopl").mean()), "bias_free1": float(_errors(reps, "free1").mean())}
    R["rules"]["PH4e"] = {"verdict": "descriptive", "cells": e}

    # descriptives
    D = R["descriptives"]
    D["free1_V4_replication_of_X3_D17"] = {"pooled": cal1, "per_N": {k: v["free1"] for k, v in per_n.items()}}
    pw = {}
    for sid in ("V1", "V5"):
        for N in NS:
            reps = _cell_fits(L, sid, N)
            null = [r["T_star"] for r in _warp_rows(L["warps"], "V2", "twopl", N) + _warp_rows(L["warps"], "V4", "twopl", N)
                    if not r["star_failed"] and r["converged"] and r["T_star"] is not None]
            if reps and len(null) >= 10:
                q = float(np.quantile(null, 0.95))
                T = [2.0 * (_b2(r, "twopl")["ll"] - r["arms"]["twopl"]["B1"]["ll"]) for r in reps
                     if _b2(r, "twopl").get("status") != "failed" and r["arms"]["twopl"]["B1"].get("status") != "failed"]
                pw[f"{sid} N={N}"] = {"q95_null": q, "share_T_above": float(np.mean(np.array(T) > q)), "n": len(T)}
    D["power_2pl"] = pw
    fits2 = [r["arms"]["twopl"][m] for r in L["fits"] for m in ("B1", "B2") if r["arms"]["twopl"][m].get("status") != "failed"]
    D["twopl_fit_stats"] = {"n_fits": len(fits2), "n_polished_total": int(sum(f.get("n_polished", 0) for f in fits2)),
                            "polish_line_search_failures": int(sum(f.get("polish_line_search_failures", 0) for f in fits2)),
                            "starts_lt3_of5": int(sum(f["start_agreement"]["n_starts_at_best"] < 3 for f in fits2)),
                            "white_noise_ridge": int(sum("white_noise_ridge" in f["flags"] for f in fits2)),
                            "w_bound_hits": int(sum(any(h.startswith("w[") for h in f["boundary_hits"]) for f in fits2)),
                            "many_extreme_lambda": int(sum("many_extreme_lambda" in f["flags"] for f in fits2))}
    D["ridge_converged_counts"] = {f"{sid} {est}": {"observed": int(sum(r["ridge"] for r in rows)), "bootstrap": int(sum(r["ridge_star"] for r in rows)), "units": len(rows)}
                                   for sid, est in (("V2", "twopl"), ("V4", "twopl"), ("V4", "free1")) for rows in [_warp_rows(L["warps"], sid, est)] if rows}
    D["recovery_ridge_converged_B2"] = int(sum("converged_on_ridge" in r["arms"]["twopl"]["B2"]["flags"] for r in L["fits"] if r["arms"]["twopl"]["B2"].get("status") != "failed"))
    R["frozen_rules_version"] = "X4-D08+D09"
    return R


def markdown(R: dict) -> list[str]:
    f = lambda x, d=3: "NA" if x is None else f"{x:.{d}f}"
    L = ["## Frozen rules (X4-D08)", "", "### Gates", "", "| gate | ok | detail |", "|---|---|---|"]
    for k, g in R["gates"].items():
        L.append(f"| {k} | {'yes' if g['ok'] else '**NO**'} | {', '.join(f'{a}={b}' for a, b in g.items() if a != 'ok')} |")
    L += ["", "### Verdicts", "", "| rule | verdict |", "|---|---|"]
    for k, r in R["rules"].items():
        L.append(f"| {k} | **{r['verdict']}**{' (fragile to ridge fits)' if r.get('fragile') else ''} |")
    a = R["rules"]["PH4a"]["cells"]
    if a:
        L += ["", "PH4a: bias of sigma2_F-hat against sigma2_F* (mean, MC CI, verdict)", "", "| cell | 2PL | 1PL-free |", "|---|---|---|"]
        for k, c in a.items():
            fm = lambda x: f"{f(x.get('bias'))} [{f(x['mc_ci'][0])}, {f(x['mc_ci'][1])}] {x['verdict']}" if "bias" in x else x["verdict"]
            L.append(f"| {k} | {fm(c['twopl'])} | {fm(c['free1'])} |")
    for key, title in (("PH4b", "V4 (misfit null)"), ("PH4c", "V2 (clean null)")):
        r = R["rules"][key]
        L += ["", f"{key}: {title}", "", "| set | datasets (ok) | alpha-hat | 95 % CI | verdict |", "|---|---|---|---|---|"]
        items = ([("2PL pooled", r["twopl_pooled"]), ("1PL-free pooled", r["free1_pooled"])] if key == "PH4b"
                 else [("2PL pooled", r["V2_pooled"]), ("2PL V2+V4 pooled", r["V2_plus_V4_twopl_pooled"])])
        if key == "PH4b":
            items += [(f"{n} {e}", v[e]) for n, v in r["per_N"].items() for e in ("twopl", "free1")]
        for name, c in items:
            L.append(f"| {name} | {c.get('n_datasets')} ({c.get('n_ok')}) | {f(c.get('alpha_hat'))} | "
                     f"{'NA' if 'ci95' not in c else '[' + f(c['ci95'][0]) + ', ' + f(c['ci95'][1]) + ']'} | {c['verdict']} |")
        if key == "PH4b":
            L.append(f"\nPaired delta (1PL-free minus 2PL): {r['paired_delta']}. {r['note']}")
        L.append("")
        L.append(f"{key} ridge sensitivity (delta {RIDGE_DELTA}): " +"; ".join(f"{n}: S+ {c.get('sens_plus_verdict')}, S- {c.get('sens_minus_verdict')}, ridge units {c.get('n_ridge_obs')}/{c.get('n_ridge_star')}" for n, c in items))
    for key in ("PH4d", "PH4e"):
        L += ["", f"{key} (descriptive): {R['rules'][key]['cells']}"]
    L += ["", f"Descriptives: {R['descriptives']}", ""]
    return L
