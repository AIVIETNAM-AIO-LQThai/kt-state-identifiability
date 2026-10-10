"""Descriptive aggregation of Experiment-5 job envelopes (pilot and confirmatory); `--rules` appends the provisional rules (rules.py)."""
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
    cells = {}
    for e in ok:
        r = e["result"]
        cells.setdefault(f"{r['scenario']}|N={r['N']}", []).append((e, r))
    out = {}
    for key, items in sorted(cells.items()):
        rs = [r for _, r in items]
        b2 = [r["arms"]["B2"] for r in rs if r["arms"]["B2"].get("status") != "failed"]
        d2 = [r["diag"]["B2"]["by_tau_x"] for r in rs if "by_tau_x" in r["diag"].get("B2", {})]
        c = {"n": len(rs), "kinds": sorted({e["job"]["kind"] for e, _ in items}), "job_seconds_mean": _mean([e["runtime"] for e, _ in items]),
             "sigma2_F_star": rs[0]["sigma2_F_star"], "sigma2_F_mean": _mean([f["theta"]["sigma2_F"] for f in b2]),
             "tau_F_median": float(np.median([f["theta"]["tau_F"] for f in b2])) if b2 else None,
             "T": [round(r["T"], 2) for r in rs if r.get("T") is not None],
             "B2_converged": _mean([f.get("converged", False) for f in b2]), "B2_flags": sorted({fl for f in b2 for fl in f["flags"]}),
             "diag_n": len(d2)}
        for t in sorted({t for d in d2 for t in d}):
            c[f"diag_tau_x={t}"] = {"p": [round(d[t]["p"], 4) for d in d2 if t in d], "eta_hat_mean": _mean([d[t]["eta_hat"] for d in d2 if t in d]),
                                   "reject_share": _mean([d[t]["p"] < 0.05 for d in d2 if t in d])}
        warp = [r for r in rs if "fit_failed" in r]
        if warp:
            c["warp"] = {"T": [round(r["T"], 2) for r in warp if r.get("T") is not None], "T_star": [round(r["T_star"], 2) for r in warp if r.get("T_star") is not None],
                         "fit_failures": int(sum(r["fit_failed"] for r in warp)), "star_failures": int(sum(r.get("star_failed", True) for r in warp if not r["fit_failed"])),
                         "runtime_fit_mean": _mean([r.get("runtime_fit") for r in warp]), "runtime_star_mean": _mean([r.get("runtime_star") for r in warp])}
        out[key] = c
    summary = {"manifest": {k: man.get(k) for k in ("stage", "config_hash", "code_hash", "git", "env")},
               "accounting": {"jobs": len(envs), "ok": len(ok), "errors": len(envs) - len(ok)},
               "cpu_hours": float(sum(e["runtime"] for e in envs) / 3600.0), "cells": out}
    write_json_atomic(rd / "summary.json", summary)
    md = _markdown(summary)
    if with_rules:
        from . import rules
        R = rules.evaluate(rd)
        write_json_atomic(rd / "rules.json", R)
        md += "\n" + "\n".join(rules.markdown(R))
    (rd / "summary.md").write_text(md, encoding="utf-8", newline="\n")
    return summary


def _f(x, d=3):
    return "NA" if x is None else f"{x:.{d}f}"


def _markdown(S: dict) -> str:
    m = S["manifest"]
    L = ["# Experiment 5 summary: outcome-driven dynamics versus the transient state F", "",
         f"- stage `{m.get('stage')}`, config hash `{(m.get('config_hash') or '')[:12]}`, code hash `{(m.get('code_hash') or '')[:12]}`",
         f"- env: {m.get('env')}", f"- job accounting: {S['accounting']}; CPU {S['cpu_hours']:.2f} h", "",
         "| cell | n | sigma2_F* | mean sigma2_F-hat | median tau_F-hat | B2 converged | mean job s | diag reject share (tau_x 2 / 5 / 10) | eta-hat (tau_x 2) | T values |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for key, c in S["cells"].items():
        sh = " / ".join(_f(c.get(f"diag_tau_x={t}", {}).get("reject_share"), 2) for t in ("2", "5", "10"))
        L.append(f"| {key} | {c['n']} | {_f(c['sigma2_F_star'])} | {_f(c['sigma2_F_mean'])} | {_f(c['tau_F_median'], 1)} | {_f(c['B2_converged'], 2)} | "
                 f"{_f(c['job_seconds_mean'], 0)} | {sh} | {_f(c.get('diag_tau_x=2', {}).get('eta_hat_mean'))} | {c['T']} |")
    warp = {k: c["warp"] for k, c in S["cells"].items() if "warp" in c}
    if warp:
        L += ["", "## Warp units (E4): observed T and one bootstrap T* per dataset (pilot: timing only)", "",
              "| cell | T | T* | fit failures | bootstrap failures | mean s fit / replicate |", "|---|---|---|---|---|---|"]
        for k, w in warp.items():
            L.append(f"| {k} | {w['T']} | {w['T_star']} | {w['fit_failures']} | {w['star_failures']} | {_f(w['runtime_fit_mean'], 0)} / {_f(w['runtime_star_mean'], 0)} |")
    return "\n".join(L) + "\n"
