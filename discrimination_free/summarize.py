"""Descriptive aggregation of Experiment-4 job envelopes (pilot). Pre-registered decision rules (PH4*) are added at the freeze, after the
Opus pilot review. Estimand: sigma2_F* = g^2 sigma2_F per replication; errors are estimate - sigma2_F* for both estimators."""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np

from kt_trial.runner import read_json, write_json_atomic


def _mean(v):
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else None


def summarize(results_dir: str, with_rules: bool = False) -> dict:
    rd = Path(results_dir)
    envs = [read_json(Path(f)) for f in sorted(glob.glob(str(rd / "jobs" / "*.json")))]
    ok = [e for e in envs if e["status"] == "ok"]
    man = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    fits = [e["result"] for e in ok if e["job"]["kind"] == "fit"]
    warps = [e for e in ok if e["job"]["kind"] == "warp"]
    cells = {}
    for r in fits:
        cells.setdefault(f"{r['scenario']}|N={r['N']}", []).append(r)
    out_cells = {}
    for key, reps in sorted(cells.items()):
        c = {"n_reps": len(reps), "sigma2_F_star_mean": _mean([r["sigma2_F_star"] for r in reps]), "g_mean": _mean([r["g"] for r in reps]), "arms": {}}
        for arm in ("free1", "twopl"):
            a = {}
            for model in ("B1", "B2"):
                fs = [r["arms"][arm][model] for r in reps]
                good = [f for f in fs if f.get("status") != "failed"]
                a[model] = {"n_failed": len(fs) - len(good), "converged": _mean([f.get("converged", False) for f in good]),
                            "flagged": _mean([f.get("status") == "flagged" for f in good]), "mean_runtime_s": _mean([f["runtime"] for f in good]),
                            "newton_decrement_large": int(sum("newton_decrement_large" in f["flags"] for f in good)),
                            "hessian_not_pd": int(sum("hessian_not_pd" in f["flags"] for f in good)),
                            "start_agreement_lt3_of5": int(sum(f["start_agreement"]["n_starts_at_best"] < 3 for f in good)),
                            "max_newton_decrement": (lambda v: float(np.nanmax(v)) if len(v) and not np.all(np.isnan(v)) else None)(
                                np.array([f["certificate"]["newton_decrement"] for f in good], float))}
            b2 = [r["arms"][arm]["B2"] for r in reps if r["arms"][arm]["B2"].get("status") != "failed"]
            err = np.array([f["sigma2_F_error_vs_star"] for f in b2])
            a["sigma2_F_error_vs_star"] = {"mean": float(err.mean()), "sd": float(err.std(ddof=1)) if len(err) > 1 else None,
                                           "values": err.tolist(), "share_at_zero": float(np.mean([f["theta"]["sigma2_F"] <= 1e-6 for f in b2]))}
            a["tau_F_mean"] = _mean([f["theta"]["tau_F"] for f in b2])
            a["b_rmse_mean"] = _mean([f["b_rmse"] for f in b2])
            if arm == "twopl":
                a["lambda_rmse_centred_log"] = _mean([f["lambda_recovery"]["rmse_centred_log_lambda"] for f in b2])
                a["lambda_corr"] = _mean([f["lambda_recovery"]["corr"] for f in b2])
                a["n_extreme_lambda_mean"] = _mean([f.get("n_extreme_lambda") for f in b2])
                a["many_extreme_lambda_fits"] = int(sum("many_extreme_lambda" in f["flags"] for f in b2))
            c["arms"][arm] = a
        out_cells[key] = c
    warp_cells = {}
    for e in warps:
        r = e["result"]
        w = warp_cells.setdefault(f"{r['scenario']}|N={r['N']}", {"estimators": {}, "job_seconds": []})
        w["job_seconds"].append(e["runtime"])
        for est in ("twopl", "free1"):
            if est in r:
                w["estimators"].setdefault(est, []).append({k: r[est].get(k) for k in ("T", "T_star", "sigma2_F", "tau_F", "converged", "fit_failed", "star_failed", "runtime_fit", "runtime_star", "star_converged", "sigma2_F_star_boot", "tau_F_star")})
    summary = {"manifest": {k: man.get(k) for k in ("stage", "config_hash", "code_hash", "git", "env")},
               "accounting": {"jobs": len(envs), "ok": len(ok), "errors": len(envs) - len(ok)},
               "cpu_hours": float(sum(e["runtime"] for e in envs) / 3600.0), "cells": out_cells, "warp": warp_cells}
    write_json_atomic(rd / "summary.json", summary)
    md = _markdown(summary)
    if with_rules:
        from . import rules
        R = rules.evaluate(rd)
        write_json_atomic(rd / "rules.json", R)
        md += "\n" + "\n".join(rules.markdown(R))
    (rd / "summary.md").write_text(md, encoding="utf-8")
    return summary


def _f(x, d=4):
    return "NA" if x is None else f"{x:.{d}f}"


def _markdown(S: dict) -> str:
    m = S["manifest"]
    L = ["# Experiment 4 summary: recovery of F with unknown item difficulties and discriminations", "",
         f"- stage `{m.get('stage')}`, config hash `{(m.get('config_hash') or '')[:12]}`, code hash `{(m.get('code_hash') or '')[:12]}`",
         f"- env: {m.get('env')}", f"- job accounting: {S['accounting']}; CPU {S['cpu_hours']:.2f} h", ""]
    for key, c in S["cells"].items():
        L += [f"## {key}  ({c['n_reps']} replications; mean sigma2_F* {_f(c['sigma2_F_star_mean'])}, mean g {_f(c['g_mean'])})", "",
              "| estimator | error vs sigma2_F* (mean / SD) | share at 0 | tau_F mean | b RMSE | lambda RMSE (centred log) | B2 converged / flagged | newton dec. large | not PD | starts<3/5 (B1, B2) | max Newton dec. | s/fit B1, B2 |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for arm, a in c["arms"].items():
            e = a["sigma2_F_error_vs_star"]
            L.append(f"| {arm} | {_f(e['mean'])} / {_f(e['sd'])} | {_f(e['share_at_zero'], 2)} | {_f(a['tau_F_mean'], 2)} | {_f(a['b_rmse_mean'], 3)} | {_f(a.get('lambda_rmse_centred_log'), 3)} | "
                     f"{_f(a['B2']['converged'], 2)} / {_f(a['B2']['flagged'], 2)} | {a['B2']['newton_decrement_large']} | {a['B2']['hessian_not_pd']} | "
                     f"{a['B1']['start_agreement_lt3_of5']}, {a['B2']['start_agreement_lt3_of5']} | {_f(a['B2']['max_newton_decrement'], 5)} | "
                     f"{_f(a['B1']['mean_runtime_s'], 0)}, {_f(a['B2']['mean_runtime_s'], 0)} |")
        tw = c["arms"]["twopl"]
        L.append(f"\n2PL: lambda corr with truth {_f(tw.get('lambda_corr'), 2)}; mean items with |log lambda-hat| > log 4: {_f(tw.get('n_extreme_lambda_mean'), 2)}; fits with many extreme lambda: {tw.get('many_extreme_lambda_fits')}\n")
    if S["warp"]:
        L += ["## Warp units (observed CLR T and one bootstrap CLR T* per fresh null dataset; pilot, timing only)", "",
              "| cell | estimator | datasets | T (values) | T* (values) | fit failures | not converged | mean s/dataset-unit (fit, replicate) | mean job s |", "|---|---|---|---|---|---|---|---|---|"]
        for key, w in S["warp"].items():
            for est, rows in w["estimators"].items():
                L.append(f"| {key} | {est} | {len(rows)} | {[round(r['T'], 2) for r in rows if r['T'] is not None]} | {[round(r['T_star'], 2) for r in rows if r.get('T_star') is not None]} | "
                         f"{sum(bool(r['fit_failed']) for r in rows)} | {sum(not r['converged'] for r in rows if r['converged'] is not None)} | "
                         f"{_f(_mean([r['runtime_fit'] for r in rows]), 0)}, {_f(_mean([r['runtime_star'] for r in rows]), 0)} | {_f(_mean(w['job_seconds']), 0)} |")
    return "\n".join(L) + "\n"
