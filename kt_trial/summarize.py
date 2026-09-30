"""Aggregate job envelopes into summary.json / summary.md (bias, RMSE, MCSE, coverage, boundary, predictive, runtime)."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import beta

from .inference import lboot_summary, null_summary
from .moments import SCALAR_NAMES
from .runner import read_json, write_json_atomic

ACTIVE = {"B0": ["alpha_bar", "phi", "sigma2_alpha"],
          "B1": ["alpha_bar", "phi", "sigma2_alpha", "r_bar", "tau_R", "sigma2_r"],
          "B2": SCALAR_NAMES}
BIAS_TOL_SIGMA2F = 0.04


VARIANCE_PARAMS = ("sigma2_alpha", "sigma2_r", "sigma2_F")


def truth_status(truth: dict) -> dict:
    """Map each scalar parameter to None (interior truth: bias/coverage meaningful) or a reason string (NA).

    A variance whose true value is 0 lies on the boundary (estimates are one-sided; Wald coverage is not
    meaningful); a time constant whose variance / gain is absent does not exist in the generating process.
    """
    st = {n: None for n in ACTIVE["B2"]}
    for v in VARIANCE_PARAMS:
        if truth[v] == 0:
            st[v] = "true value on the boundary (0)"
    if truth["sigma2_F"] == 0:
        st["tau_F"] = "inactive: no transient state in the generating process"
    if truth["sigma2_r"] == 0 and truth["r_bar"] == 0:
        st["tau_R"] = "inactive: no fast recency in the generating process"
    return st


def clopper_pearson(k: int, n: int, level=0.95):
    if n == 0:
        return [float("nan"), float("nan")]
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return [lo, hi]


def _stats(errs):
    e = np.asarray(errs, float)
    n = len(e)
    if n == 0:
        return None
    sd = float(e.std(ddof=1)) if n > 1 else float("nan")
    return {"n": n, "bias": float(e.mean()), "mcse_bias": sd / np.sqrt(n) if n > 1 else float("nan"),
            "sd": sd, "rmse": float(np.sqrt(np.mean(e ** 2)))}


def load_envelopes(rd: Path):
    return [read_json(p) for p in sorted((rd / "jobs").glob("*.json"))]


def summarize(rd) -> dict:
    rd = Path(rd)
    envs = load_envelopes(rd)
    manifest = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    fitenv = [e for e in envs if e["job"]["kind"] == "fit"]
    ok = [e for e in fitenv if e["status"] == "ok"]
    out = {"stage": manifest.get("stage"), "config_hash": manifest.get("config_hash"), "code_hash": manifest.get("code_hash"),
           "git": manifest.get("git"), "env": manifest.get("env"),
           "job_accounting": {"fit_jobs": len(fitenv), "fit_ok": len(ok), "fit_error": len(fitenv) - len(ok),
                              "errors": [{"job": e["job_id"], "error": e.get("error")} for e in envs if e["status"] != "ok"],
                              "cpu_hours_total": sum(e.get("runtime", 0.0) for e in envs) / 3600.0},
           "cells": {}, "null_tests": {}, "learner_bootstrap": {}}
    groups = defaultdict(list)
    for e in ok:
        r = e["result"]; groups[(r["scenario"], r["N_fit"])].append(r)
    for (sid, N), rs in sorted(groups.items()):
        cell = {"scenario": sid, "N_fit": N, "N_heldout": rs[0]["N_heldout"], "N_total_generated": rs[0]["N_total_generated"],
                "n_reps": len(rs), "violations": rs[0]["violations"], "models": {}}
        truth = rs[0]["truth"]
        for m in ("B0", "B1", "B2"):
            fits = [r["fits"][m] for r in rs if m in r["fits"]]
            if not fits:
                continue
            good = [f for f in fits if f["status"] != "failed"]
            mc = {"n_fits": len(fits), "n_failed": len(fits) - len(good),
                  "convergence_rate": float(np.mean([f["converged"] for f in good])) if good else None,
                  "flagged_rate": float(np.mean([f["status"] == "flagged" for f in good])) if good else None,
                  "boundary_hit_rate": {}, "params": {}, "runtime_sec_mean": float(np.mean([f["runtime"] for f in fits])),
                  "starts_at_best_mean": float(np.mean([f["start_agreement"]["n_starts_at_best"] for f in good])) if good else None,
                  "single_start_at_best_rate": float(np.mean([f["start_agreement"]["n_starts_at_best"] < 2 for f in good])) if good else None,
                  "secondary_optima_rate": float(np.mean([f["start_agreement"]["secondary_optima"] > 0 for f in good])) if good else None,
                  "max_newton_decrement": (float(np.nanmax([f["certificate"]["newton_decrement"] for f in good]))
                                           if good and not np.all(np.isnan([f["certificate"]["newton_decrement"] for f in good])) else None),
                  "hessian_not_pd_count": int(sum(f["certificate"]["hessian_not_pd"] for f in good)),
                  "hessian_not_pd_outside_allowance": int(sum(
                      f["certificate"]["hessian_not_pd"] and not (m == "B2" and f["theta"]["sigma2_F"] < 0.02) for f in good)),
                  "newton_decrement_large_count": int(sum("newton_decrement_large" in f["flags"] for f in good)),
                  "max_abs_projected_gradient": float(np.nanmax([f["grad_inf_abs"] for f in good])) if good and not np.all(np.isnan([f["grad_inf_abs"] for f in good])) else None}
            bh = defaultdict(int)
            for f in good:
                for h in f["boundary_hits"]:
                    bh[h] += 1
            mc["boundary_hit_rate"] = {k: v / len(good) for k, v in bh.items()}
            tstat = truth_status(truth)
            for n in ACTIVE[m]:
                if tstat[n] is not None:                       # NA: report the estimate distribution only
                    est = [f["theta"][n] for f in good]
                    mc["params"][n] = {"truth": truth[n], "na_reason": tstat[n], "n": len(est),
                                       "mean_estimate": float(np.mean(est)) if est else None,
                                       "share_at_zero": float(np.mean([e <= 1e-6 for e in est])) if est and n in VARIANCE_PARAMS else None}
                    continue
                st = _stats([f["errors"][n] for f in good])
                if st:
                    st["truth"] = truth[n]
                    mc["params"][n] = st
            if m == "B2":
                pos = [f for f in good if f["theta"]["sigma2_F"] > 1e-6]
                mc["tau_F_when_sigma2F_positive"] = (_stats([f["errors"]["tau_F"] for f in pos])
                                                     if pos and tstat["tau_F"] is None else None)
                mc["share_sigma2F_at_zero"] = 1 - len(pos) / len(good) if good else None
                if "sigma2_F" in mc["params"] and truth["sigma2_F"] > 0:
                    p = mc["params"]["sigma2_F"]
                    lo, hi = p["bias"] - 2 * p["mcse_bias"], p["bias"] + 2 * p["mcse_bias"]
                    p["bias_within_0.04"] = ("yes" if max(abs(lo), abs(hi)) <= BIAS_TOL_SIGMA2F else
                                             "no" if min(abs(lo), abs(hi)) > BIAS_TOL_SIGMA2F and lo * hi > 0 else "inconclusive")
            # Wald coverage of the learner-score sandwich, only for parameters with an interior truth.
            # conditional = fits where the parameter was interior and had a CI; unconditional = all converged fits
            # (a fit at a bound, or without a CI, counts as not covering).
            cov = {}
            for r in rs:
                f = r["fits"].get(m)
                if not f or f["status"] == "failed":
                    continue
                sw = r["sandwich"].get(m)
                for n in ACTIVE[m]:
                    if tstat[n] is not None or n not in SCALAR_NAMES:
                        continue
                    c = cov.setdefault(n, {"cond_covered": 0, "cond_n": 0, "uncond_covered": 0, "uncond_n": 0})
                    c["uncond_n"] += 1
                    d = sw["params"].get(n) if sw and sw.get("status") == "ok" else None
                    if d is not None and d.get("ci95") is None:
                        c["n_ci_na"] = c.get("n_ci_na", 0) + 1          # C6: counted as non-covering, not in the conditional set
                    elif d is not None:
                        hit = int(d["ci95"][0] <= truth[n] <= d["ci95"][1])
                        c["cond_n"] += 1; c["cond_covered"] += hit; c["uncond_covered"] += hit
            mc["sandwich_coverage"] = {n: {**c, "conditional_cp95": clopper_pearson(c["cond_covered"], c["cond_n"]),
                                           "unconditional_cp95": clopper_pearson(c["uncond_covered"], c["uncond_n"])}
                                       for n, c in cov.items()}
            cell["models"][m] = mc
        pred = {}
        for score in ("marginal_bernoulli_log_score", "pairwise_composite_log_score"):
            for cmp_ in ("B1-B0", "B2-B1"):
                v = [r["prediction"][score][cmp_]["mean"] for r in rs if r["prediction"].get(score, {}).get(cmp_)]
                if v:
                    pred[f"{score}:{cmp_}"] = {"mean_over_reps": float(np.mean(v)), "mcse": float(np.std(v, ddof=1) / np.sqrt(len(v))) if len(v) > 1 else None,
                                              "n_reps": len(v), "n_reps_positive": int(np.sum(np.array(v) > 0))}
        cell["heldout_prediction"] = pred
        out["cells"][f"{sid}|N={N}"] = cell
    # null tests and learner bootstrap from replicate envelopes
    by_ds = defaultdict(list)
    for e in envs:
        if e["job"]["kind"] in ("null_rep", "lboot_rep"):
            j = e["job"]; by_ds[(j["kind"], j["scenario"], j["N"], j["rep"])].append(e)
    fit_lookup = {(r["scenario"], r["N_fit"], r["rep"]): r for grp in groups.values() for r in grp}
    for (kind, sid, N, rep), es in sorted(by_ds.items()):
        fr = fit_lookup.get((sid, N, rep))
        if not fr:
            continue
        reps = [e["result"] if e["status"] == "ok" else {"b": e["job"]["b"], "failed": True} for e in es]
        key = f"{sid}|N={N}|rep={rep}"
        if kind == "null_rep":
            b1, b2 = fr["fits"]["B1"], fr["fits"]["B2"]
            if b1["status"] != "failed" and b2["status"] != "failed":
                s = null_summary(2.0 * (b2["ll"] - b1["ll"]), reps, len(reps))
                s["observed_sigma2_F_hat"] = b2["theta"]["sigma2_F"]
                s["true_sigma2_F"] = fr["truth"]["sigma2_F"]
                out["null_tests"][key] = s
        else:
            s = lboot_summary(reps, len(reps))
            sw = fr["sandwich"].get("B2", {})
            s["sandwich_se"] = {n: d["se"] for n, d in sw.get("params", {}).items()} if sw.get("status") == "ok" else None
            out["learner_bootstrap"][key] = s
    if out["null_tests"]:
        byscn = defaultdict(list)
        for k, v in out["null_tests"].items():
            byscn[k.split("|")[0]].append(v["reject_at_alpha"])
        out["null_test_rejection_rates"] = {s: {"rejections": int(sum(v)), "n_datasets": len(v), "rate": sum(v) / len(v),
                                                "cp95": clopper_pearson(int(sum(v)), len(v))} for s, v in byscn.items()}
    out["pre_registered"] = pre_registered(groups, out["null_tests"])
    write_json_atomic(rd / "summary.json", out)
    (rd / "summary.md").write_text(to_markdown(out), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------------------------
# Pre-registered decision rules PH1-PH6 (decision D24; fixed before any Stage 3 data existed).
# 95 % Monte Carlo CI = estimate +- 1.96 * MCSE; rates carry Clopper-Pearson 95 % limits.
# ---------------------------------------------------------------------------------------------
Z = 1.959963984540054
NEAR_WHITE_TAU = 0.4          # minutes: below the shortest design lag
DESIGN_SE_SIGMA2F = {"300": 0.0338, "1000": 0.0185}      # audit: predicted Godambe SE of sigma2_F at sigma2_F = 0.04


def _bias_verdict(bias, mcse, tol=BIAS_TOL_SIGMA2F):
    lo, hi = bias - Z * mcse, bias + Z * mcse
    if lo >= -tol and hi <= tol:
        v = "pass"
    elif lo > tol or hi < -tol:
        v = "fail"
    else:
        v = "inconclusive"
    return {"bias": bias, "mcse": mcse, "mc_ci95": [lo, hi], "tolerance": tol, "verdict": v}


def _rate(k, n):
    return {"k": int(k), "n": int(n), "rate": (k / n) if n else None, "cp95": clopper_pearson(int(k), int(n))}


def _mean_ci(v):
    v = np.asarray(v, float)
    n = len(v)
    m = float(v.mean()) if n else float("nan")
    se = float(v.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
    return {"mean": m, "mcse": se, "n": n, "mc_ci95": [m - Z * se, m + Z * se]}


def pre_registered(groups: dict, null_tests: dict) -> dict:
    """groups[(scenario, N)] -> list of fit-job results; null_tests[key] -> null_summary + dataset info."""
    out = {"rules": "D24 (docs/experiment_01_decisions.md); thresholds fixed before Stage 3 data", "PH": {}}
    Ns = sorted({N for (_, N) in groups})

    def b2fits(sid, N):
        return [r["fits"]["B2"] for r in groups.get((sid, N), []) if r["fits"]["B2"]["status"] != "failed"]

    def sigma_errs(sid, N):
        return [f["errors"]["sigma2_F"] for f in b2fits(sid, N)]

    def null_by(sid, N=None):
        return [v for k, v in null_tests.items() if k.split("|")[0] == sid and (N is None or k.split("|")[1] == f"N={N}")]

    # PH1 (S1) and PH5 (S8): bias of sigma2_F
    for ph, sid in (("PH1", "S1"), ("PH5", "S8")):
        cells = {}
        for N in Ns:
            e = sigma_errs(sid, N)
            if len(e) > 1:
                cells[f"N={N}"] = {**_bias_verdict(float(np.mean(e)), float(np.std(e, ddof=1) / np.sqrt(len(e)))),
                                   "n_fits": len(e), "rmse": float(np.sqrt(np.mean(np.square(e)))), "sd": float(np.std(e, ddof=1))}
        out["PH"][ph] = {"scenario": sid, "cells": cells}
    # PH2: power of the boundary-aware test in S1
    out["PH"]["PH2"] = {"scenario": "S1", "cells": {
        f"N={N}": _rate(sum(bool(v["reject_at_alpha"]) for v in null_by("S1", N)), len(null_by("S1", N))) for N in Ns if null_by("S1", N)}}
    # PH3 (S2) and PH4 (S8n): false-positive behaviour
    for ph, sid in (("PH3", "S2"), ("PH4", "S8n")):
        nt = null_by(sid)
        k, n = sum(bool(v["reject_at_alpha"]) for v in nt), len(nt)
        r = _rate(k, n)
        allfits = [f for N in Ns for f in b2fits(sid, N)]
        s2 = np.array([f["theta"]["sigma2_F"] for f in allfits]) if allfits else np.array([])
        nw = [f for f in allfits if f["theta"]["sigma2_F"] > 1e-6 and f["theta"]["tau_F"] < NEAR_WHITE_TAU]
        out["PH"][ph] = {"scenario": sid, "null_test_rejections": r,
                         "verdict": ("evidence of excess false positives" if n and r["cp95"][0] > 0.05 else
                                     f"no evidence of excess false positives (CP upper bound {r['cp95'][1]:.2f})") if n else "no null tests",
                         "sigma2_F_hat_distribution": {"n_fits": len(s2), "share_at_zero": float(np.mean(s2 <= 1e-6)) if len(s2) else None,
                                                       "mean": float(s2.mean()) if len(s2) else None,
                                                       "p90": float(np.quantile(s2, 0.9)) if len(s2) else None},
                         "near_white_share": _rate(len(nw), len(allfits))}
    # PH6: held-out pairwise composite score, B2 - B1
    ph6 = {}
    for sid, kind in (("S1", "improvement"), ("S2", "spurious superiority"), ("S8n", "spurious superiority")):
        for N in Ns:
            v = [r["prediction"]["pairwise_composite_log_score"]["B2-B1"]["mean"] for r in groups.get((sid, N), [])
                 if r["prediction"].get("pairwise_composite_log_score", {}).get("B2-B1")]
            if len(v) > 1:
                ci = _mean_ci(v)
                ph6[f"{sid}|N={N}"] = {**ci, "claim": kind, "positive_ci": bool(ci["mc_ci95"][0] > 0),
                                       "verdict": (f"{kind}: yes" if ci["mc_ci95"][0] > 0 else f"{kind}: not shown")}
    out["PH"]["PH6"] = ph6
    # descriptive extras
    out["near_white_share_by_scenario"] = {
        sid: _rate(sum(1 for N in Ns for f in b2fits(sid, N) if f["theta"]["sigma2_F"] > 1e-6 and f["theta"]["tau_F"] < NEAR_WHITE_TAU),
                   sum(len(b2fits(sid, N)) for N in Ns)) for sid in sorted({s for (s, _) in groups})}
    out["mde_design_based_detectability"] = {
        "note": "MDE sigma2_F = 0.04 is NOT a confirmatory criterion (D21/D24). Design-based predicted SE at sigma2_F = 0.04:",
        "predicted_se": DESIGN_SE_SIGMA2F,
        "empirical_sd_sigma2F_hat_in_S1": {f"N={N}": (float(np.std(sigma_errs("S1", N), ddof=1)) if len(sigma_errs("S1", N)) > 1 else None) for N in Ns}}
    return out


def pre_registered_markdown(pr: dict) -> list:
    L = ["## Pre-registered decision rules (D24)", "",
         "Bias verdicts use the 95 % Monte Carlo CI (bias +- 1.96 MCSE) against +-0.04; rates use Clopper-Pearson 95 % limits.", ""]
    for ph in ("PH1", "PH5"):
        d = pr["PH"][ph]
        for cell, v in d["cells"].items():
            L.append(f"- **{ph}** ({d['scenario']} {cell}, {v['n_fits']} fits): bias {v['bias']:.4f}, MCSE {v['mcse']:.4f}, MC CI [{v['mc_ci95'][0]:.4f}, {v['mc_ci95'][1]:.4f}] -> **{v['verdict']}** (RMSE {v['rmse']:.4f}, SD {v['sd']:.4f})")
    for cell, v in pr["PH"]["PH2"]["cells"].items():
        L.append(f"- **PH2** (S1 {cell}): boundary-aware test rejects {v['k']}/{v['n']} (CP95 [{v['cp95'][0]:.2f}, {v['cp95'][1]:.2f}])")
    for ph in ("PH3", "PH4"):
        d = pr["PH"][ph]; r = d["null_test_rejections"]; s = d["sigma2_F_hat_distribution"]; nw = d["near_white_share"]
        L.append(f"- **{ph}** ({d['scenario']}, sigma2_F = 0): rejects {r['k']}/{r['n']} (CP95 [{r['cp95'][0]:.2f}, {r['cp95'][1]:.2f}]) -> **{d['verdict']}**; "
                 f"sigma2_F-hat at 0 in {_f(s['share_at_zero'],2)}, mean {_f(s['mean'],4)}, p90 {_f(s['p90'],4)}; near-white (sigma2_F-hat > 0 and tau_F-hat < {NEAR_WHITE_TAU} min) {nw['k']}/{nw['n']}")
    for cell, v in pr["PH"]["PH6"].items():
        L.append(f"- **PH6** ({cell}): held-out pairwise composite B2-B1 = {v['mean']:.3f} per learner, MCSE {_f(v['mcse'],3)}, MC CI [{v['mc_ci95'][0]:.3f}, {v['mc_ci95'][1]:.3f}] -> {v['verdict']}")
    m = pr["mde_design_based_detectability"]
    L += ["", f"MDE (descriptive only): {m['note']} {m['predicted_se']}; empirical SD of sigma2_F-hat in S1: {m['empirical_sd_sigma2F_hat_in_S1']}", ""]
    return L


def _f(x, d=3):
    return "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.{d}f}"


def to_markdown(s: dict) -> str:
    L = [f"# Experiment 1 summary — stage `{s['stage']}`", "",
         f"- config hash `{(s['config_hash'] or '')[:12]}`, code hash `{(s['code_hash'] or '')[:12]}`, git `{(s.get('git') or {}).get('sha','?')[:10] if (s.get('git') or {}).get('sha') else '?'}` "
         f"(dirty: {(s.get('git') or {}).get('dirty')})",
         f"- env: {s.get('env')}", f"- job accounting: {s['job_accounting']['fit_ok']}/{s['job_accounting']['fit_jobs']} fit jobs ok; "
         f"{s['job_accounting']['fit_error']} errors; total CPU {s['job_accounting']['cpu_hours_total']:.2f} h", ""]
    if s["stage"] == "smoke":
        L += ["> Smoke stage: verifies the pipeline. It is **not** evidence for the research claim.", ""]
    for key, c in s["cells"].items():
        L += [f"## {key}  (fit N={c['N_fit']}, held-out N={c['N_heldout']}, generated {c['N_total_generated']}; {c['n_reps']} reps; violations: {c['violations'] or 'none'})", ""]
        L += ["| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for m, mc in c["models"].items():
            L.append(f"| {m} | {mc['n_fits']} | {mc['n_failed']} | {_f(mc['convergence_rate'],2)} | {_f(mc['flagged_rate'],2)} | "
                     f"{_f(mc['starts_at_best_mean'],1)} | {_f(mc['single_start_at_best_rate'],2)} | {_f(mc['secondary_optima_rate'],2)} | "
                     f"{mc['max_newton_decrement'] if mc['max_newton_decrement'] is None else format(mc['max_newton_decrement'], '.2e')} | "
                     f"{mc['hessian_not_pd_count']} ({mc['hessian_not_pd_outside_allowance']}) | {mc['runtime_sec_mean']:.0f} |")
        L += ["", "| model | param | truth | bias | MCSE(bias) | RMSE | n |", "|---|---|---|---|---|---|---|"]
        for m, mc in c["models"].items():
            for n, p in mc["params"].items():
                if "na_reason" in p:
                    z = "" if p["share_at_zero"] is None else "; share at 0: %.2f" % p["share_at_zero"]
                    L.append(f"| {m} | {n} | {_f(p['truth'],4)} | NA ({p['na_reason']}) | mean estimate {_f(p['mean_estimate'],4)}{z} | NA | {p['n']} |")
                else:
                    L.append(f"| {m} | {n} | {_f(p['truth'],4)} | {_f(p['bias'],4)} | {_f(p['mcse_bias'],4)} | {_f(p['rmse'],4)} | {p['n']} |")
        b2 = c["models"].get("B2")
        if b2:
            L += ["", f"B2: share of fits with sigma2_F at 0: {_f(b2.get('share_sigma2F_at_zero'),2)}; boundary hits: {b2['boundary_hit_rate']}"]
            if b2.get("tau_F_when_sigma2F_positive"):
                L.append(f"B2: tau_F error when sigma2_F > 0: {b2['tau_F_when_sigma2F_positive']}")
            if b2["sandwich_coverage"]:
                L.append("B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): " + "; ".join(
                    f"{n}: {d['cond_covered']}/{d['cond_n']} [{d['uncond_covered']}/{d['uncond_n']}]" for n, d in b2["sandwich_coverage"].items()))
        if c["heldout_prediction"]:
            L += ["", "Held-out (population-marginal; not next-response) score differences, mean over reps:"]
            for k, v in c["heldout_prediction"].items():
                L.append(f"- {k}: {v['mean_over_reps']:.5f} (MCSE {_f(v['mcse'],5)}; positive in {v['n_reps_positive']}/{v['n_reps']})")
        L.append("")
    if s["null_tests"]:
        L += ["## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)", "",
              "| dataset | CLR obs | B ok/failed | p | reject@0.05 | sigma2_F hat | true |", "|---|---|---|---|---|---|---|"]
        for k, v in s["null_tests"].items():
            L.append(f"| {k} | {_f(v['clr_observed'],2)} | {v['n_ok']}/{v['n_failed']} | {_f(v['p_value'],3)} (min {_f(v['min_attainable_p'],3)}) | {v['reject_at_alpha']} | {_f(v['observed_sigma2_F_hat'],3)} | {_f(v['true_sigma2_F'],3)} |")
        L.append("")
    if s["learner_bootstrap"]:
        L += ["## Learner bootstrap vs sandwich SE (B2)", ""]
        for k, v in s["learner_bootstrap"].items():
            L.append(f"- {k}: replicates ok {v['n_ok']}/{v['n_ok']+v['n_failed']}; bootstrap SD {({n: round(x,4) for n,x in v['sd'].items()})}; sandwich SE {v['sandwich_se']}")
        L.append("")
    if s.get("pre_registered"):
        L += pre_registered_markdown(s["pre_registered"])
    if s["job_accounting"]["errors"]:
        L += ["## Job errors", ""] + [f"- {e['job']}: {e['error']}" for e in s["job_accounting"]["errors"]] + [""]
    return "\n".join(L)
