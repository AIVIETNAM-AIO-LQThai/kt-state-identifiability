"""Aggregate Experiment-3 job envelopes: per-cell recovery of sigma2_F for each arm on identical datasets, H3f paired SD ratio,
convergence/certificate accounting, timings, and boundary-aware null-test results (p = (1 + #{CLR* >= CLR}) / (B + 1))."""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
from scipy import stats

from kt_trial.runner import read_json, write_json_atomic

ARMS = ("known", "cal", "free")
PARAMS = ("sigma2_F", "tau_F", "alpha_bar", "r_bar", "tau_R", "sigma2_r")


def _cp(k, n, a=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - a / 2, k + 1, n - k)
    return float(lo), float(hi)


def _boot_ratio(x, y, B=2000, seed=0):
    """Replication bootstrap of SD(x)/SD(y) over paired replications; None when fewer than 5 replications."""
    n = len(x)
    if n < 5:
        return None
    rng = np.random.default_rng(seed)
    r = []
    for _ in range(B):
        i = rng.integers(0, n, n)
        sy = np.std(np.asarray(y)[i], ddof=1)
        if sy > 0:
            r.append(np.std(np.asarray(x)[i], ddof=1) / sy)
    return [float(np.quantile(r, 0.025)), float(np.quantile(r, 0.975))]


def summarize(results_dir: str) -> dict:
    rd = Path(results_dir)
    envs = [read_json(Path(f)) for f in sorted(glob.glob(str(rd / "jobs" / "*.json")))]
    ok = [e for e in envs if e["status"] == "ok"]
    man = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    fits = [e["result"] for e in ok if e["job"]["kind"] == "fit"]
    nulls = [e for e in ok if e["job"]["kind"] == "null"]
    cells = {}
    for r in fits:
        cells.setdefault(f"{r['scenario']}|N={r['N']}", []).append(r)
    out_cells = {}
    for key, reps in sorted(cells.items()):
        truth = reps[0]["truth"]
        c = {"n_reps": len(reps), "truth": {p: truth[p] for p in PARAMS if p in truth}, "arms": {}}
        for arm in ARMS:
            rr = [r for r in reps if arm in r["arms"]]
            if not rr:
                continue
            a = {"n": len(rr)}
            for model in ("B1", "B2"):
                fs = [r["arms"][arm][model] for r in rr]
                good = [f for f in fs if f.get("status") != "failed"]
                a[model] = {"n_failed": len(fs) - len(good), "converged": float(np.mean([f.get("converged", False) for f in good])) if good else None,
                            "flagged": float(np.mean([f.get("status") == "flagged" for f in good])) if good else None,
                            "newton_decrement_large": int(sum("newton_decrement_large" in f["flags"] for f in good)),
                            "hessian_not_pd": int(sum("hessian_not_pd" in f["flags"] for f in good)),
                            "mean_runtime_s": float(np.mean([f["runtime"] for f in good])) if good else None,
                            "max_newton_decrement": (lambda v: float(np.nanmax(v)) if len(v) and not np.all(np.isnan(v)) else None)(
                                np.array([f["certificate"]["newton_decrement"] for f in good], float)) if good else None,
                            "single_start_at_best": int(sum(f["start_agreement"]["n_starts_at_best"] < 2 for f in good))}
            b2 = [r["arms"][arm]["B2"] for r in rr if r["arms"][arm]["B2"].get("status") != "failed"]
            for p in ("sigma2_F", "tau_F", "alpha_bar", "r_bar"):
                v = np.array([f["theta"][p] for f in b2])
                tv = truth[p]
                a.setdefault("B2_estimates", {})[p] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None,
                                                       "bias": float(v.mean() - tv), "mcse_bias": float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else None,
                                                       "rmse": float(np.sqrt(((v - tv) ** 2).mean())), "values": v.tolist()}
            a["share_sigma2F_at_zero"] = float(np.mean([f["theta"]["sigma2_F"] <= 1e-6 for f in b2])) if b2 else None
            if arm == "free":
                a["b_rmse_mean"] = float(np.mean([f["b_rmse"] for f in b2]))
                a["b_bias_mean"] = float(np.mean([f["b_bias"] for f in b2]))
            if arm == "cal":
                a["calibration_error_rmse"] = float(np.mean([r["arms"]["cal"]["b_cal_rmse"] for r in rr]))
            c["arms"][arm] = a
        if "free" in c["arms"] and "known" in c["arms"] and truth["sigma2_F"] > 0:
            x = c["arms"]["free"]["B2_estimates"]["sigma2_F"]["values"]; y = c["arms"]["known"]["B2_estimates"]["sigma2_F"]["values"]
            n = min(len(x), len(y))
            c["H3f_sd_ratio_free_over_known"] = {"ratio": (float(np.std(x[:n], ddof=1) / np.std(y[:n], ddof=1)) if n > 1 and np.std(y[:n], ddof=1) > 0 else None),
                                                 "bootstrap_ci95": _boot_ratio(x[:n], y[:n]), "n_pairs": n}
        out_cells[key] = c
    null_summary = {}
    groups = {}
    for e in nulls:
        j = e["job"]
        groups.setdefault((j["scenario"], j["N"], j["rep"], j["arm"]), []).append(e["result"])
    for (sid, N, rep, arm), reps in sorted(groups.items()):
        fr = next((r for r in fits if (r["scenario"], r["N"], r["rep"]) == (sid, N, rep)), None)
        good = [r for r in reps if not r.get("failed")]
        if fr is None or not good:
            continue
        b1, b2 = fr["arms"][arm]["B1"], fr["arms"][arm]["B2"]
        clr_obs = 2.0 * (b2["ll"] - b1["ll"])
        clr = np.array([r["clr"] for r in good])
        p = (1.0 + (clr >= clr_obs).sum()) / (len(clr) + 1.0)
        null_summary[f"{sid}|N={N}|rep={rep}|{arm}"] = {"clr_observed": float(clr_obs), "B_ok": len(good), "B_failed": len(reps) - len(good), "p_value": float(p),
                                                        "min_attainable_p": 1.0 / (len(clr) + 1.0), "reject_at_0.05": bool(p <= 0.05),
                                                        "mean_null_runtime_s": float(np.mean([r["runtime"] for r in good])),
                                                        "null_clr_q95": float(np.quantile(clr, 0.95))}
    summary = {"manifest": {k: man.get(k) for k in ("stage", "config_hash", "code_hash", "git", "env")},
               "accounting": {"jobs": len(envs), "ok": len(ok), "errors": len(envs) - len(ok)}, "cells": out_cells, "null_tests": null_summary}
    write_json_atomic(rd / "summary.json", summary)
    (rd / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    return summary


def _f(x, d=4):
    return "NA" if x is None else f"{x:.{d}f}"


def _markdown(S: dict) -> str:
    m = S["manifest"]
    L = ["# Experiment 3 summary: recovery of the shared transient latent state F with unknown item difficulties", "",
         f"- stage `{m.get('stage')}`, config hash `{(m.get('config_hash') or '')[:12]}`, code hash `{(m.get('code_hash') or '')[:12]}`",
         f"- env: {m.get('env')}", f"- job accounting: {S['accounting']}", ""]
    for key, c in S["cells"].items():
        L += [f"## {key}  ({c['n_reps']} replications; true sigma2_F {c['truth'].get('sigma2_F')}, tau_F {c['truth'].get('tau_F')})", "",
              "| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, a in c["arms"].items():
            e = a["B2_estimates"]["sigma2_F"]
            L.append(f"| {arm} | {a['n']} | {_f(e['mean'])} | {_f(e['bias'])} ({_f(e['mcse_bias'])}) | {_f(e['sd'])} | {_f(e['rmse'])} | {_f(a['share_sigma2F_at_zero'], 2)} | "
                     f"{_f(a['B2_estimates']['tau_F']['mean'], 2)} | {_f(a['B2']['converged'], 2)} | {_f(a['B2']['flagged'], 2)} | {_f(a['B2']['max_newton_decrement'], 5)} | "
                     f"{_f(a['B1']['mean_runtime_s'], 0)}, {_f(a['B2']['mean_runtime_s'], 0)} | {_f(a.get('b_rmse_mean', a.get('calibration_error_rmse')), 3)} |")
        h = c.get("H3f_sd_ratio_free_over_known")
        if h:
            L += ["", f"H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = {_f(h['ratio'], 2)} (n = {h['n_pairs']}; bootstrap CI {h['bootstrap_ci95']}); design ratio about 0.57 at tau_F = 10."]
        L.append("")
    if S["null_tests"]:
        L += ["## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)", "", "| dataset | arm | CLR obs | B ok/failed | p | min p | reject | s/replicate |", "|---|---|---|---|---|---|---|---|"]
        for k, v in S["null_tests"].items():
            sid, N, rep, arm = k.split("|")
            L.append(f"| {sid} {N} {rep} | {arm} | {_f(v['clr_observed'], 2)} | {v['B_ok']}/{v['B_failed']} | {_f(v['p_value'], 3)} | {_f(v['min_attainable_p'], 3)} | {v['reject_at_0.05']} | {_f(v['mean_null_runtime_s'], 0)} |")
    return "\n".join(L) + "\n"
