"""Aggregate Experiment-2 job envelopes. Uncertainty: learners are dependent response sequences. Fitted arms use the
replication (independent training fits) as the unit; known-parameter arms pool independent evaluation learners across
replications. Both are reported. R^2 = 1 - MSE / sigma_F^2 is reported only where sigma_F^2 > 0 (S1); null scenarios use
absolute excursion measures."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy import stats

from kt_trial.runner import read_json, write_json_atomic

BINS = ["first", "j1_4", "j5_15", "j16_31", "practice", "probe", "all"]
NEAR = 0.2


def pool_reps(items):
    m = np.array([i["mean"] for i in items], float)
    R = len(m)
    se = float(m.std(ddof=1) / np.sqrt(R)) if R > 1 else float("nan")
    h = float(stats.t.ppf(0.975, R - 1) * se) if R > 1 else float("nan")
    return {"mean": float(m.mean()), "se": se, "lo": float(m.mean() - h), "hi": float(m.mean() + h), "R": R}


def pool_learners(items):
    n = np.array([i["n"] for i in items], float)
    m = np.array([i["mean"] for i in items], float)
    v = np.array([i["var"] for i in items], float)
    mean = float((n * m).sum() / n.sum())
    se = float(np.sqrt((n * v).sum()) / n.sum())
    return {"mean": mean, "se": se, "lo": mean - 1.96 * se, "hi": mean + 1.96 * se, "n": int(n.sum())}


def _both(items):
    return {"by_replication": pool_reps(items), "by_learner": pool_learners(items)}


def _load(rd: Path):
    jobs = []
    for f in sorted(glob.glob(str(rd / "jobs" / "*.json"))):
        e = read_json(Path(f))
        jobs.append(e)
    return jobs


def _agg_cells(track_jobs, exclude=()):
    cells = {}
    for e in track_jobs:
        r = e["result"]
        cells.setdefault(f"{r['scenario']}|N={r['N']}", []).append(r)
    out = {}
    for key, reps in cells.items():
        c = {"n_reps": len(reps), "sigma2_F_true": reps[0]["sigma2_F_true"], "data_source": reps[0]["data_source"],
             "logloss": {}, "gain": {}, "state": {}, "excursion": {}, "persistent": {}}
        for a in reps[0]["logloss"]:
            c["logloss"][a] = {b: _both([r["logloss"][a][b] for r in reps]) for b in BINS}
        pairs = set().union(*[set(r["gain"]) for r in reps])
        for pr in sorted(pairs):
            rr = [r for r in reps if pr in r["gain"]]
            c["gain"][pr] = {b: _both([r["gain"][pr][b] for r in rr]) for b in BINS}
        for a in reps[0]["state"]:
            c["state"][a] = {ph: {met: {b: _both([r["state"][a][ph][met][b] for r in reps]) for b in BINS}
                                  for met in ("mse", "coverage90", "width90")} for ph in ("pre", "post")}
            ex = [r["excursion"][a] for r in reps]
            num, den = sum(e["post"]["lag1_num"] for e in ex), sum(e["post"]["lag1_den"] for e in ex)
            runs, tot = sum(e["post"]["runs"] for e in ex), sum(e["post"]["run_positions"] for e in ex)
            c["excursion"][a] = {"energy_post": {b: _both([e["post"]["energy_post"][b] for e in ex]) for b in BINS},
                                 "energy_pre": {b: _both([e["pre_energy"][b] for e in ex]) for b in BINS},
                                 "lag1_autocorr": num / den if den > 0 else None,
                                 "mean_run_length": tot / runs if runs else None, "n_runs": runs, "thresh": NEAR}
        for a in reps[0]["persistent"]:
            c["persistent"][a] = {k: _both([r["persistent"][a][k] for r in reps]) for k in reps[0]["persistent"][a]}
        c["fitted_sigma2_F"] = [r["fitted"]["B2"]["sigma2_F"] for r in reps]
        ex = [r for r in reps if (r["scenario"], r["N"], r["rep"]) in exclude]
        if ex:                                              # prespecified sensitivity analysis: drop flagged fits
            kept = [r for r in reps if r not in ex]
            g = pool_reps([r["gain"]["full_fit__over__priorF_fit"]["practice"] for r in kept])
            c["sensitivity"] = {"excluded": [r["rep"] for r in ex], "n_reps_kept": len(kept),
                                "gain_full_over_priorF_practice": g, "spurious_tracking_gain": bool(g["lo"] > 0)}
        out[key] = c
    return out


def _ref_rules(ref_jobs, bound):
    if not ref_jobs:
        return None
    R = [e["result"] for e in ref_jobs]
    s2 = R[0]["sigma2_F"]; ns = R[0]["n_seeds"]; Np = R[0]["n_particles"]
    nl = np.array([r["n_learners"] for r in R], float)
    out = {"n_reps": len(R), "n_learners": int(nl.sum()), "n_seeds": ns, "n_particles": Np}
    for ph in ("pre", "post"):
        by_seed = np.array([[sum(r[f"mse_{ph}_by_seed"][s]["practice"] * r["n_learners"] for r in R) / nl.sum()] for s in range(ns)]).ravel()
        r2s = 1 - by_seed / s2
        big = 1 - sum(r[f"mse_{ph}_big"]["practice"] * r["n_learners"] for r in R) / nl.sum() / s2
        adf = 1 - sum(r[f"mse_{ph}_adf"]["practice"] * r["n_learners"] for r in R) / nl.sum() / s2
        bnd = 1 - sum(r[f"bound_mse_{ph}"]["practice"] * r["n_learners"] for r in R) / nl.sum() / s2
        sd = float(r2s.std(ddof=1)); fct = R[0].get("doubling_factor", 4)
        ref_pl = np.concatenate([r["learner_mse_practice"][ph]["ref"] for r in R]); adf_pl = np.concatenate([r["learner_mse_practice"][ph]["adf"] for r in R])
        d = (adf_pl - ref_pl) / s2                              # R2_ref - R2_adf per learner
        se_ref = float(ref_pl.std(ddof=1) / np.sqrt(len(ref_pl)) / s2)
        out[ph] = {"R2_ref_mean_of_seeds": float(r2s.mean()), "R2_ref_single_run_sd": sd,
                   "R2_ref_big_run": float(big), "doubling_diff": float(big - r2s.mean()),
                   "doubling_se": float(sd * np.sqrt(1 / ns + 1 / fct)), "R2_adf": float(adf), "R2_bound": float(bnd),
                   "R2_ref_minus_bound": float(r2s.mean() - bnd), "learner_sampling_se_of_R2": se_ref,
                   "delta_R2_ref_minus_adf": {"mean": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(len(d)))}}
    p_rms = float(np.sqrt(np.average([r["p_seed_sd_rms"] ** 2 for r in R], weights=nl)))
    dp = pool_learners([{"n": r["n_learners"], "mean": r["p_adf_minus_ref"]["practice"]["mean_abs"], "var": 0.0} for r in R])["mean"]
    gain = pool_learners([r["gain_ref_over_adf"]["practice"] for r in R])
    gain_b1 = pool_learners([r["B1fit"]["gain_ref_over_adf"]["practice"] for r in R])
    out.update({"p_single_run_mc_rms": p_rms, "adf_vs_ref_mean_abs_dp_practice": dp,
                "logloss_gain_ref_over_adf_practice": gain, "B1fit_logloss_gain_ref_over_adf_practice": gain_b1,
                "B1fit_mean_abs_dp_practice": float(np.average([r["B1fit"]["p_adf_minus_ref_mean_abs"]["practice"] for r in R], weights=nl)),
                "ess_min": float(min(r["ess_min"] for r in R)), "ess_mean": float(np.mean([r["ess_mean"] for r in R]))})
    o = out["post"]
    out["R1"] = {"R2_single_run_mc_sd_le_0.002": bool(max(out["pre"]["R2_ref_single_run_sd"], o["R2_ref_single_run_sd"]) <= 0.002),
                 "p_single_run_mc_rms_le_0.001": bool(p_rms <= 0.001),
                 "doubling_within_2se": bool(abs(o["doubling_diff"]) <= 2 * o["doubling_se"] and abs(out["pre"]["doubling_diff"]) <= 2 * out["pre"]["doubling_se"]),
                 "orthant_check": "unit test test_smc_matches_orthant (tests/test_transient_filtering.py)"}
    out["R1"]["passed"] = bool(all(v for k, v in out["R1"].items() if isinstance(v, bool)))
    lo, hi = gain["lo"], gain["hi"]
    out["R2_validation_subset_indicative"] = {"mean_abs_dp_le_0.005": bool(dp <= 0.005), "logloss_gain_ci_within_pm_5e-4": bool(lo >= -5e-4 and hi <= 5e-4)}
    out["R2_validation_subset_indicative"]["adf_approximation_negligible_for_forecasting"] = bool(all(out["R2_validation_subset_indicative"].values()))
    return out

BIN_REPORT = ["practice", "probe", "all", "first", "j1_4", "j5_15", "j16_31"]


def _r2(g, s2):
    return {"mean": 1 - g["mean"] / s2, "se": g["se"] / s2, "lo": 1 - g["hi"] / s2, "hi": 1 - g["lo"] / s2}


def _scaled(g, s2, sign=1.0):
    a, b = sign * g["lo"] / s2, sign * g["hi"] / s2
    return {"mean": sign * g["mean"] / s2, "se": g["se"] / s2, "lo": min(a, b), "hi": max(a, b)}


def _production(P, cells):
    """Gap decomposition on the production learners: R2_bound >= R2_ref >= R2_ADF(known) >= R2_ADF(fitted)."""
    if not P:
        return None
    s2 = P[0]["sigma2_F"]
    out = {"n_reps": len(P), "n_learners": int(sum(r["n_learners"] for r in P)), "n_particles": P[0]["n_particles"],
           "ess_min": float(min(r["ess_min"] for r in P)), "gap": {}, "provenance_hashes": len({r["provenance"]["eval_sha256"] for r in P})}
    for ph in ("pre", "post"):
        out["gap"][ph] = {}
        for b in BIN_REPORT:
            bnd = 1 - float(np.mean([r["bound_mse"][ph][b] for r in P])) / s2
            L = {a: pool_learners([r["mse"][a][ph][b] for r in P]) for a in ("ref", "adf_known", "adf_fit")}
            Rp = {a: pool_reps([r["mse"][a][ph][b] for r in P]) for a in ("adf_fit",)}
            d1 = pool_learners([r["mse_diff"]["adf_known_minus_ref"][ph][b] for r in P])
            d2l = pool_learners([r["mse_diff"]["adf_fit_minus_adf_known"][ph][b] for r in P])
            d2r = pool_reps([r["mse_diff"]["adf_fit_minus_adf_known"][ph][b] for r in P])
            out["gap"][ph][b] = {"R2_bound": bnd, "R2_ref": _r2(L["ref"], s2), "R2_adf_known": _r2(L["adf_known"], s2),
                                 "R2_adf_fit": _r2(L["adf_fit"], s2), "R2_adf_fit_by_replication": _r2(Rp["adf_fit"], s2),
                                 "approximation_loss_ref_minus_adf_known": _scaled(d1, s2),
                                 "estimation_loss_adf_known_minus_adf_fit_by_learner": _scaled(d2l, s2),
                                 "estimation_loss_adf_known_minus_adf_fit_by_replication": _scaled(d2r, s2),
                                 "bound_minus_ref": bnd - _r2(L["ref"], s2)["mean"]}
    # R0 implementation-validity gate: nothing may exceed the information bound by more than 2 learner-SE
    r0 = {}
    for ph in ("pre", "post"):
        g = out["gap"][ph]["practice"]
        for a in ("R2_ref", "R2_adf_known"):
            ex = g[a]["mean"] - g["R2_bound"]
            r0[f"{a}_{ph}"] = {"excess_over_bound": ex, "learner_se": g[a]["se"], "ok": bool(ex <= 2 * g[a]["se"])}
    for key, c in cells.items():
        if key.startswith("S1|") and "full_known" in c["state"]:
            for ph in ("pre", "post"):
                m = c["state"]["full_known"][ph]["mse"]["practice"]["by_learner"]
                bd = (S1_BOUND.get(ph))
                if bd is not None:
                    r = _r2(m, c["sigma2_F_true"]); ex = r["mean"] - bd
                    r0[f"track_{key}_full_known_{ph}"] = {"excess_over_bound": ex, "learner_se": r["se"], "ok": bool(ex <= 2 * r["se"])}
    out["R0"] = {"checks": r0, "passed": bool(all(v["ok"] for v in r0.values()))}
    dp = float(np.mean([r["dp_abs"]["adf_known"]["practice"] for r in P]))
    gk = pool_learners([r["gain"]["ref__over__adf_known"]["practice"] for r in P])
    out["R2"] = {"mean_abs_dp_adf_known_practice": dp, "mean_abs_dp_adf_fit_practice": float(np.mean([r["dp_abs"]["adf_fit"]["practice"] for r in P])),
                 "logloss_gain_ref_over_adf_known_practice": gk,
                 "mean_abs_dp_le_0.005": bool(dp <= 0.005), "logloss_gain_ci_within_pm_5e-4": bool(gk["lo"] >= -5e-4 and gk["hi"] <= 5e-4)}
    out["R2"]["adf_approximation_negligible_for_forecasting"] = bool(out["R2"]["mean_abs_dp_le_0.005"] and out["R2"]["logloss_gain_ci_within_pm_5e-4"])
    out["forecasting_gain_nats_per_response"] = {
        k: {"by_learner": pool_learners([r["gain"][k]["practice"] for r in P]), "by_replication": pool_reps([r["gain"][k]["practice"] for r in P])}
        for k in P[0]["gain"]}
    return out


S1_BOUND = {}


def _r3(cells):
    out = {}
    for key, c in cells.items():
        sid = key.split("|")[0]
        if sid in ("S2", "S8n") and "full_fit__over__priorF_fit" in c["gain"]:
            g = c["gain"]["full_fit__over__priorF_fit"]["practice"]["by_replication"]
            out[key] = {"gain_full_over_priorF_nats_per_response": g, "spurious_tracking_gain": bool(g["lo"] > 0),
                        "rule": "spurious if the replication-level 95% CI lies entirely above 0",
                        "sensitivity_excluding_flagged_fits": c.get("sensitivity")}
    return out


def summarize(results_dir: str) -> dict:
    rd = Path(results_dir)
    envs = _load(rd)
    ok = [e for e in envs if e["status"] == "ok"]
    man = read_json(rd / "manifest.json") if (rd / "manifest.json").exists() else {}
    bound = next((e["result"] for e in ok if e["job"]["kind"] == "bound"), None)
    excl = {(x["scenario"], x["N"], x["rep"]) for x in (man.get("stage_config") or {}).get("sensitivity_exclude", [])}
    cells = _agg_cells([e for e in ok if e["job"]["kind"] == "track"], excl)
    if bound:
        S1_BOUND.update({"pre": bound["arms"]["answers_only"]["R2_pre"]["practice"], "post": bound["arms"]["answers_only"]["R2_post"]["practice"]})
    prod = _production([e["result"] for e in ok if e["job"]["kind"] == "ref_prod"], cells)
    allres = [e["result"] for e in ok if e["job"]["kind"] in ("track", "ref", "ref_prod")]
    prov = {"jobs_with_hashes": sum("provenance" in r for r in allres),
            "numpy": sorted({r["provenance"]["numpy"] for r in allres if "provenance" in r}),
            "scipy": sorted({r["provenance"]["scipy"] for r in allres if "provenance" in r})}
    summary = {"manifest": {k: man.get(k) for k in ("stage", "config_hash", "code_hash", "git", "env")},
               "accounting": {"jobs": len(envs), "ok": len(ok), "errors": len(envs) - len(ok)},
               "bound": bound, "cells": cells, "reference": _ref_rules([e for e in ok if e["job"]["kind"] == "ref"], bound),
               "production_reference": prod, "provenance": prov, "null_safety_R3": _r3(cells)}
    write_json_atomic(rd / "summary.json", summary)
    (rd / "summary.md").write_text(_markdown(summary), encoding="utf-8")
    return summary


def _f(x, d=4):
    return "NA" if x is None else f"{x:.{d}f}"


def _ci(g, d=4):
    return f"{g['mean']:.{d}f} [{g['lo']:.{d}f}, {g['hi']:.{d}f}]"


def _markdown(S) -> str:
    L = ["# Experiment 2 summary: individual tracking of the shared transient latent state F", ""]
    m = S["manifest"]
    L += [f"- stage `{m.get('stage')}`, config hash `{(m.get('config_hash') or '')[:12]}`, code hash `{(m.get('code_hash') or '')[:12]}`, "
          f"git `{((m.get('git') or {}).get('sha') or '')[:10]}` (dirty: {(m.get('git') or {}).get('dirty')})",
          f"- env: {m.get('env')}", f"- job accounting: {S['accounting']}", ""]
    if S["bound"]:
        L += ["## Information bound (S1 generating parameters, Gaussian prior; expected R^2 upper bound for ANY estimator)", "",
              "| channel | pre-answer (practice) | post-answer (practice) | pre (all 112) | post (all 112) | pre (probe) |", "|---|---|---|---|---|---|"]
        for a, d in S["bound"]["arms"].items():
            L.append(f"| {a} | {_f(d['R2_pre']['practice'])} | {_f(d['R2_post']['practice'])} | {_f(d['R2_pre']['all'])} | {_f(d['R2_post']['all'])} | {_f(d['R2_pre']['probe'])} |")
        L.append("")
    for key, c in S["cells"].items():
        s2 = c["sigma2_F_true"]
        L += [f"## {key}  ({c['n_reps']} fitted replications, {c['data_source']} evaluation learners, sigma2_F true {s2})", ""]
        if s2 > 0:
            L += ["### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)", "",
                  "| arm | pre-answer | post-answer | 90% coverage post |", "|---|---|---|---|"]
            for a, d in c["state"].items():
                pre, post = d["pre"]["mse"]["practice"]["by_learner"], d["post"]["mse"]["practice"]["by_learner"]
                L.append(f"| {a} | {_f(1 - pre['mean'] / s2)} | {_f(1 - post['mean'] / s2)} | {_f(d['post']['coverage90']['practice']['by_learner']['mean'], 3)} |")
            L.append("")
        else:
            L += ["### Excursions of the post-answer transient estimate (true F = 0; absolute units)", "",
                  "| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |", "|---|---|---|---|---|"]
            for a, d in c["excursion"].items():
                L.append(f"| {a} | {_ci(d['energy_post']['practice']['by_replication'], 5)} | {_f(d['lag1_autocorr'], 3)} | {_f(d['mean_run_length'], 2)} | {_f(d['energy_pre']['practice']['by_replication']['mean'], 5)} |")
            L.append("")
        L += ["### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI", "",
              "| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |", "|---|---|---|---|---|"]
        for pr, d in c["gain"].items():
            L.append(f"| {pr.replace('__over__', ' over ')} | {_ci(d['practice']['by_replication'], 5)} | {_ci(d['practice']['by_learner'], 5)} | "
                     f"{_ci(d['probe']['by_replication'], 5)} | {_ci(d['first']['by_replication'], 5)} |")
        L.append("")
        if c["persistent"]:
            L += ["### Persistent coordinates after the last practice answer (MSE; learner-pooled)", "", "| arm | M0 | alpha | r | M0 90% cover |", "|---|---|---|---|---|"]
            for a, d in c["persistent"].items():
                L.append(f"| {a} | {_f(d['mse_M0']['by_learner']['mean'], 4)} | {_f(d['mse_alpha']['by_learner']['mean'], 5)} | {_f(d['mse_r']['by_learner']['mean'], 5)} | {_f(d['cover90_M0']['by_learner']['mean'], 3)} |")
            L.append("")
    if S["null_safety_R3"]:
        L += ["## Null safety (R3): spurious tracking gain of B2-full over B2-priorF", ""]
        for k, d in S["null_safety_R3"].items():
            g = d["gain_full_over_priorF_nats_per_response"]
            L.append(f"- **{k}**: {_ci(g, 5)} nats/response -> spurious tracking gain: **{d['spurious_tracking_gain']}**"
                     + (f"; sensitivity excluding flagged fit(s) {d['sensitivity_excluding_flagged_fits']}" if d.get("sensitivity_excluding_flagged_fits") else ""))
        L.append("")
    PR = S.get("production_reference")
    if PR:
        L += ["## Production reference (all S1 N=1000 evaluation learners): gap decomposition", "",
              f"- {PR['n_learners']} learners, {PR['n_reps']} replications, {PR['n_particles']} particles, min ESS {_f(PR['ess_min'], 0)}",
              f"- **R0 (implementation validity)**: passed = **{PR['R0']['passed']}**  {PR['R0']['checks']}",
              f"- **R2 (ADF approximation, production learners)**: {PR['R2']}", "",
              "R^2 = 1 - MSE/sigma2_F. Order expected: bound >= reference >= ADF(known) >= ADF(fitted). Learner CIs.", "",
              "| phase | bin | bound | reference | ADF known | ADF fitted | approx. loss (ref - ADF known) | estimation loss (ADF known - fitted), learner CI | estimation loss, replication CI |", "|---|---|---|---|---|---|---|---|---|"]
        for ph in ("pre", "post"):
            for b in ("practice", "first", "j1_4", "j5_15", "j16_31", "probe"):
                g = PR["gap"][ph][b]
                L.append(f"| {ph} | {b} | {_f(g['R2_bound'])} | {_ci(g['R2_ref'])} | {_ci(g['R2_adf_known'])} | {_ci(g['R2_adf_fit'])} | "
                         f"{_ci(g['approximation_loss_ref_minus_adf_known'], 5)} | {_ci(g['estimation_loss_adf_known_minus_adf_fit_by_learner'], 5)} | "
                         f"{_ci(g['estimation_loss_adf_known_minus_adf_fit_by_replication'], 5)} |")
        L += ["", "Causal log-loss gains on the production learners, nats per response (practice; positive = first arm better):", ""]
        for k, d in PR["forecasting_gain_nats_per_response"].items():
            L.append(f"- {k.replace('__over__', ' over ')}: learner CI {_ci(d['by_learner'], 5)}; replication CI {_ci(d['by_replication'], 5)}")
        L.append("")
    if S.get("provenance"):
        L += [f"- provenance: {S['provenance']}", ""]
    R = S["reference"]
    if R:
        L += ["## SMC reference: gates (R1) and ADF approximation (R2)", "",
              f"- {R['n_learners']} learners from {R['n_reps']} replications, {R['n_seeds']} independent seeds, {R['n_particles']} particles; min ESS {_f(R['ess_min'], 0)}",
              f"- **R1** {R['R1']}", f"- R2 on this validation subset (indicative only): {R['R2_validation_subset_indicative']}",
              f"- single-run MC SD of R^2: pre {_f(R['pre']['R2_ref_single_run_sd'], 5)}, post {_f(R['post']['R2_ref_single_run_sd'], 5)}; single-run RMS MC SD of p: {_f(R['p_single_run_mc_rms'], 5)}",
              f"- R^2 (practice, these learners) post: reference {_f(R['post']['R2_ref_mean_of_seeds'])}, ADF {_f(R['post']['R2_adf'])}, bound {_f(R['post']['R2_bound'])} "
              f"(ref - bound {_f(R['post']['R2_ref_minus_bound'])}, learner-sampling SE {_f(R['post']['learner_sampling_se_of_R2'])}); pre: ref {_f(R['pre']['R2_ref_mean_of_seeds'])}, ADF {_f(R['pre']['R2_adf'])}, bound {_f(R['pre']['R2_bound'])}",
              f"- ADF vs reference: mean |dp| (practice) {_f(R['adf_vs_ref_mean_abs_dp_practice'], 5)}; log-loss gain of reference over ADF {_ci(R['logloss_gain_ref_over_adf_practice'], 6)} nats/response; "
              f"delta R^2 post (ref - ADF) {R['post']['delta_R2_ref_minus_adf']}",
              f"- B1 (fitted) ADF vs reference: mean |dp| {_f(R['B1fit_mean_abs_dp_practice'], 5)}; gain {_ci(R['B1fit_logloss_gain_ref_over_adf_practice'], 6)}", ""]
    return "\n".join(L) + "\n"
