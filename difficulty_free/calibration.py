"""Warp-speed Monte Carlo estimate of the size of the free-difficulty boundary-aware bootstrap test (decision X3-D15).

Per fresh null dataset r we hold the observed statistic T_r and ONE bootstrap statistic T*_r drawn from that dataset's fitted null.
The infinite-B level of the bootstrap test at alpha is  alpha_hat = mean_r 1{ T_r > q_{1-alpha}({T*}) }  (Giacomini, Politis & White 2013).
A strict '>' matches the registered p-value (p = (1 + #{T* >= T}) / (B + 1)): a dataset with T = 0 never rejects; if the quantile is 0,
any T > 0 rejects. Uncertainty: pairs bootstrap over datasets (resample (T_r, T*_r) jointly).
"""
from __future__ import annotations

import numpy as np
from scipy import stats

ALPHA = 0.05
N_BOOT = 2000
CONSISTENT_UPPER = 0.10
G_MAX_BAD = 0.05
RIDGE_TAU = 0.4


def alpha_hat(T, Tstar, alpha: float = ALPHA) -> float:
    T, Tstar = np.asarray(T, float), np.asarray(Tstar, float)
    q = np.quantile(Tstar, 1.0 - alpha)
    return float(np.mean(T > q))


def pairs_bootstrap_ci(T, Tstar, alpha: float = ALPHA, B: int = N_BOOT, seed: int = 0) -> list[float]:
    T, Tstar = np.asarray(T, float), np.asarray(Tstar, float)
    n = len(T)
    rng = np.random.default_rng(seed)
    vals = np.empty(B)
    for b in range(B):
        i = rng.integers(0, n, n)
        vals[b] = alpha_hat(T[i], Tstar[i], alpha)
    return [float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))]


def verdict(ci: list[float]) -> str:
    lo, hi = ci
    if lo > ALPHA:
        return "liberal"
    if lo <= ALPHA <= hi and hi <= CONSISTENT_UPPER:
        return "consistent with 5 %"
    return "inconclusive"


def _cell_stats(rows: list[dict], seed: int) -> dict:
    n_all = len(rows)
    ok = [r for r in rows if not r.get("fit_failed") and not r.get("star_failed", True) and r.get("converged", False)]
    bad = 1.0 - len(ok) / n_all if n_all else 1.0
    out = {"n_datasets": n_all, "n_ok": len(ok), "share_bad": float(bad), "gate_ok": bool(bad <= G_MAX_BAD)}
    if len(ok) < 10:
        out["verdict"] = "not evaluable (too few datasets)"
        return out
    T = np.array([r["T"] for r in ok]); Ts = np.array([r["T_star"] for r in ok])
    ah = alpha_hat(T, Ts)
    ci = pairs_bootstrap_ci(T, Ts, seed=seed)
    out.update(alpha_hat=ah, ci95=ci, verdict=verdict(ci) if out["gate_ok"] else "not evaluable (gate)")
    out["alpha_hat_at_0.10"] = alpha_hat(T, Ts, 0.10)
    out["alpha_hat_at_0.01"] = alpha_hat(T, Ts, 0.01)
    out["T_quantiles"] = {str(q): float(np.quantile(T, q)) for q in (0.5, 0.9, 0.95, 0.99)}
    out["Tstar_quantiles"] = {str(q): float(np.quantile(Ts, q)) for q in (0.5, 0.9, 0.95, 0.99)}
    ks = stats.ks_2samp(T, Ts)
    out["ks_T_vs_Tstar"] = {"statistic": float(ks.statistic), "p": float(ks.pvalue)}
    out["share_T_zero"] = float(np.mean(T <= 1e-9)); out["share_Tstar_zero"] = float(np.mean(Ts <= 1e-9))
    ridge = lambda rr, key_s, key_t: float(np.mean([(r[key_s] > 1e-6) and (r[key_t] < RIDGE_TAU) for r in rr]))
    out["ridge_share_data"] = ridge(ok, "sigma2_F", "tau_F"); out["ridge_share_bootstrap"] = ridge(ok, "sigma2_F_star", "tau_F_star")
    return out


def evaluate(warp_results: list[dict]) -> dict:
    """Per scenario: pooled over N (primary) and per N (secondary)."""
    out = {}
    scen = sorted({r["scenario"] for r in warp_results})
    for sid in scen:
        rows = [r for r in warp_results if r["scenario"] == sid]
        out[sid] = {"pooled": _cell_stats(rows, seed=1)}
        for N in sorted({r["N"] for r in rows}):
            out[sid][f"N={N}"] = _cell_stats([r for r in rows if r["N"] == N], seed=2 + N)
    return out


def markdown(C: dict) -> list[str]:
    L = ["## Calibration of the free-difficulty null test (warp-speed Monte Carlo, X3-D15)", "",
         "| scenario | cell | datasets (ok) | alpha-hat (5 %) | 95 % CI | verdict | alpha-hat at 10 % / 1 % | T zero share (data / bootstrap) | ridge share (data / bootstrap) | KS p |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda x, d=3: "NA" if x is None else f"{x:.{d}f}"
    for sid, cells in C.items():
        for name, c in cells.items():
            if "alpha_hat" not in c:
                L.append(f"| {sid} | {name} | {c['n_datasets']} ({c['n_ok']}) | NA | NA | {c['verdict']} | | | | |")
                continue
            L.append(f"| {sid} | {name} | {c['n_datasets']} ({c['n_ok']}) | {f(c['alpha_hat'])} | [{f(c['ci95'][0])}, {f(c['ci95'][1])}] | **{c['verdict']}** | "
                     f"{f(c['alpha_hat_at_0.10'], 2)} / {f(c['alpha_hat_at_0.01'], 2)} | {f(c['share_T_zero'], 2)} / {f(c['share_Tstar_zero'], 2)} | "
                     f"{f(c['ridge_share_data'], 2)} / {f(c['ridge_share_bootstrap'], 2)} | {f(c['ks_T_vs_Tstar']['p'], 3)} |")
    return L + [""]
