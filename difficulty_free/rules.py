"""Pre-registered decision rules and validity gates of Experiment 3 (decision X3-D12), computed from the summary dictionary.

Bias rules: Monte Carlo CI (bias +- 1.96 MCSE) against +-0.04 -> pass (inside) / fail (disjoint) / inconclusive.
Rates carry Clopper-Pearson (CP) 95 % limits. Gates G1-G3 are evaluated first; a rule whose cell fails a gate is reported as not evaluable.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

BIAS_TOL = 0.04
G1_MAX_BAD = 0.10        # share of B2 fits failed or not converged
G2_MAX_FAIL = 0.05       # share of failed null replicates
DESIGN_SD_RATIO = 0.57   # Stage-0 design ratio SD(free)/SD(known) at tau_F = 10
NEAR = {"known": "known", "free": "free", "cal": "cal"}


def cp(k: int, n: int, alpha=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def bias_rule(values, truth, tol=BIAS_TOL) -> dict:
    v = np.asarray(values, float)
    n = len(v)
    if n < 2:
        return {"n": n, "verdict": "not evaluable (n < 2)"}
    bias = float(v.mean() - truth)
    mcse = float(v.std(ddof=1) / np.sqrt(n))
    lo, hi = bias - 1.96 * mcse, bias + 1.96 * mcse
    verdict = "pass" if (lo >= -tol and hi <= tol) else ("fail" if (hi < -tol or lo > tol) else "inconclusive")
    return {"n": n, "bias": bias, "mcse": mcse, "mc_ci": [lo, hi], "sd": float(v.std(ddof=1)),
            "rmse": float(np.sqrt(((v - truth) ** 2).mean())), "verdict": verdict}


def false_positive_rule(k: int, n: int) -> dict:
    lo, hi = cp(k, n)
    return {"rejections": k, "n": n, "cp95": [lo, hi],
            "verdict": "evidence of excess false positives" if lo > 0.05 else f"no evidence of excess false positives (CP upper bound {hi:.2f})"}


def _cell(S, sid, N):
    return S["cells"].get(f"{sid}|N={N}")


def _arm_gate(cell, arm):
    """G1 for one arm of a cell: share of B2 fits failed or not converged."""
    a = (cell or {}).get("arms", {}).get(arm)
    if not a:
        return {"ok": False, "reason": "arm not run"}
    n = a["n"]
    good = n - a["B2"]["n_failed"]
    conv = 0 if a["B2"]["converged"] is None else round(a["B2"]["converged"] * good)
    bad = (n - conv) / n if n else 1.0
    return {"ok": bool(bad <= G1_MAX_BAD), "share_bad": float(bad), "n": n}


def _null_gate(S, sid, N):
    """G2 for the free-arm null replicates of a cell."""
    ok = failed = 0
    for k, v in S["null_tests"].items():
        s, n, _, arm = k.split("|")
        if s == sid and n == f"N={N}" and arm == "free":
            ok += v["B_ok"]; failed += v["B_failed"]
    share = failed / (ok + failed) if ok + failed else 0.0
    return {"ok": bool(share <= G2_MAX_FAIL), "share_failed": float(share), "n_replicates": ok + failed}


def _values(cell, arm):
    return list(cell["arms"][arm].get("sigma2F_by_rep", {}).values())


def _paired(cell, a, b):
    ra, rb = cell["arms"][a].get("sigma2F_by_rep", {}), cell["arms"][b].get("sigma2F_by_rep", {})
    reps = sorted(set(ra) & set(rb))
    return reps, np.array([ra[r] - rb[r] for r in reps])


def _null_rate(S, sid, Ns):
    k = n = 0
    for key, v in S["null_tests"].items():
        s, nn, _, arm = key.split("|")
        if s == sid and arm == "free" and int(nn[2:]) in Ns and v["B_ok"] > 0:
            n += 1; k += int(v["reject_at_0.05"])
    return k, n


def evaluate(S: dict, Ns=(300, 1000)) -> dict:
    R = {"gates": {}, "rules": {}}
    env = (S.get("manifest") or {}).get("env") or {}
    th = env.get("threads") or {}
    R["gates"]["G3"] = {"ok": bool(env.get("numpy") and th and all(str(v) == "1" for v in th.values())), "threads": th,
                        "numpy": env.get("numpy")}
    R["gates"]["no_job_errors"] = {"ok": S["accounting"]["errors"] == 0, "errors": S["accounting"]["errors"]}
    for sid in ("U1", "U2", "U3", "U4", "U5", "A02"):
        for N in Ns:
            c = _cell(S, sid, N)
            if not c:
                continue
            for arm in c["arms"]:
                R["gates"][f"G1 {sid} N={N} {arm}"] = _arm_gate(c, arm)
    for key in sorted(S["null_tests"]):                      # G2 depends on the null tests themselves, not on a fit cell
        sid, nn, _, arm = key.split("|")
        if arm == "free":
            R["gates"][f"G2 {sid} {nn}"] = _null_gate(S, sid, int(nn[2:]))

    def gated(key_list):
        bad = [k for k in key_list if k in R["gates"] and not R["gates"][k]["ok"]]
        return bad

    # PH3a: free-b recovery, U1
    for N in Ns:
        c = _cell(S, "U1", N)
        if c and "free" in c["arms"]:
            bad = gated([f"G1 U1 N={N} free"])
            R["rules"][f"PH3a U1 N={N}"] = ({"verdict": "not evaluable (G1)", "gates": bad} if bad
                                             else bias_rule(_values(c, "free"), c["truth"]["sigma2_F"]))
    # PH3b: false positives, U2 free (pooled over N)
    k, n = _null_rate(S, "U2", Ns)
    bad = gated([f"G2 U2 N={N}" for N in Ns])
    R["rules"]["PH3b U2 free"] = {"verdict": "not evaluable (G2)", "gates": bad} if bad else (false_positive_rule(k, n) if n else {"verdict": "no null tests"})
    # PH3c: misfit without F, U4 free
    k, n = _null_rate(S, "U4", Ns)
    bad = gated([f"G2 U4 N={N}" for N in Ns])
    ph3c = {"verdict": "not evaluable (G2)", "gates": bad} if bad else (false_positive_rule(k, n) if n else {"verdict": "no null tests"})
    dist = {}
    for N in Ns:
        c = _cell(S, "U4", N)
        if c and "free" in c["arms"]:
            v = np.array(_values(c, "free"))
            dist[f"N={N}"] = {"share_at_zero": float(np.mean(v <= 1e-6)), "mean": float(v.mean()), "p90": float(np.quantile(v, 0.9)), "n": len(v)}
    ph3c["sigma2_F_hat_distribution"] = dist
    R["rules"]["PH3c U4 free"] = ph3c
    # PH3d: robustness, U5 (free primary; known reported)
    for N in Ns:
        c = _cell(S, "U5", N)
        if c and "free" in c["arms"]:
            bad = gated([f"G1 U5 N={N} free"])
            r = {"verdict": "not evaluable (G1)", "gates": bad} if bad else bias_rule(_values(c, "free"), c["truth"]["sigma2_F"])
            if "known" in c["arms"]:
                r["known_arm_reported"] = bias_rule(_values(c, "known"), c["truth"]["sigma2_F"])
            R["rules"][f"PH3d U5 N={N}"] = r
    # PH3e: calibration error inflates sigma2_F-hat (paired against the known-difficulty estimator)
    for sid in ("U1", "U2"):
        for N in Ns:
            c = _cell(S, sid, N)
            if c and "cal" in c["arms"] and "known" in c["arms"]:
                bad = gated([f"G1 {sid} N={N} cal", f"G1 {sid} N={N} known"])
                if bad:
                    R["rules"][f"PH3e {sid} N={N}"] = {"verdict": "not evaluable (G1)", "gates": bad}
                    continue
                reps, d = _paired(c, "cal", "known")
                if len(d) < 2:
                    R["rules"][f"PH3e {sid} N={N}"] = {"verdict": "not evaluable (n < 2)"}
                    continue
                m, se = float(d.mean()), float(d.std(ddof=1) / np.sqrt(len(d)))
                lo, hi = m - 1.96 * se, m + 1.96 * se
                R["rules"][f"PH3e {sid} N={N}"] = {"n_pairs": len(d), "mean_difference": m, "mc_ci": [lo, hi],
                                                    "verdict": "inflation" if lo > 0 else ("no inflation shown" if hi >= 0 else "deflation")}
    # PH3f (descriptive): SD ratio free/known on identical datasets, U1
    for N in Ns:
        c = _cell(S, "U1", N)
        if c and "free" in c["arms"] and "known" in c["arms"]:
            reps, _ = _paired(c, "free", "known")
            rf, rk = c["arms"]["free"]["sigma2F_by_rep"], c["arms"]["known"]["sigma2F_by_rep"]
            x, y = [rf[r] for r in reps], [rk[r] for r in reps]
            ratio = float(np.std(x, ddof=1) / np.std(y, ddof=1)) if len(x) > 1 and np.std(y, ddof=1) > 0 else None
            boot = None
            if len(x) >= 5:
                rng = np.random.default_rng(0)
                rr = []
                for _ in range(2000):
                    i = rng.integers(0, len(x), len(x))
                    sy = np.std(np.asarray(y)[i], ddof=1)
                    if sy > 0:
                        rr.append(np.std(np.asarray(x)[i], ddof=1) / sy)
                boot = [float(np.quantile(rr, 0.025)), float(np.quantile(rr, 0.975))]
            R["rules"][f"PH3f U1 N={N}"] = {"sd_ratio_free_over_known": ratio, "bootstrap_ci95": boot, "design_ratio": DESIGN_SD_RATIO, "n_pairs": len(x),
                                             "bias_free": float(np.mean(x) - c["truth"]["sigma2_F"]), "bias_known": float(np.mean(y) - c["truth"]["sigma2_F"]),
                                             "descriptive": True}
    # power (descriptive)
    for sid in ("U1", "U5"):
        for N in Ns:
            k = n = 0
            for key, v in S["null_tests"].items():
                s, nn, _, arm = key.split("|")
                if s == sid and nn == f"N={N}" and arm == "free" and v["B_ok"] > 0:
                    n += 1; k += int(v["reject_at_0.05"])
            if n:
                lo, hi = cp(k, n)
                R["rules"][f"power {sid} N={N}"] = {"rejections": k, "n": n, "cp95": [lo, hi], "descriptive": True}
    # H3c (descriptive): partial identification, U3 and the tau_F = 0.2 appendix
    for sid in ("U3", "A02"):
        for N in Ns:
            c = _cell(S, sid, N)
            if not c:
                continue
            row = {}
            for arm in c["arms"]:
                row[arm] = bias_rule(_values(c, arm), c["truth"]["sigma2_F"]) if len(_values(c, arm)) > 1 else {"n": len(_values(c, arm))}
            R["rules"][f"H3c {sid} N={N}"] = {"arms": row, "descriptive": True}
    R["all_gates_ok"] = bool(all(g["ok"] for g in R["gates"].values()))
    return R


def markdown(R: dict) -> list[str]:
    L = ["## Pre-registered rules (X3-D12)", "", f"- all gates ok: **{R['all_gates_ok']}**"]
    bad = {k: v for k, v in R["gates"].items() if not v["ok"]}
    if bad:
        L.append(f"- gates NOT ok: {bad}")
    L += ["", "| rule | result |", "|---|---|"]
    for k, v in R["rules"].items():
        keys = [x for x in ("verdict", "bias", "mcse", "mc_ci", "rejections", "n", "cp95", "mean_difference", "sd_ratio_free_over_known",
                            "bootstrap_ci95", "bias_free", "bias_known", "sigma2_F_hat_distribution", "arms") if x in v]
        L.append(f"| {k} | " + "; ".join(f"{x}: {v[x]}" for x in keys) + " |")
    return L + [""]
