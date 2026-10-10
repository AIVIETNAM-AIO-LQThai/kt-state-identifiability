"""Experiment 5, exploratory check of the carry-over diagnostic's level (X5-F10; NOT a pre-registered rule).

Read-only over the confirmatory job files. Per cell and N: rejection count at the primary tau_x = 2 (B2 fit), mean and variance of the
score statistic S (chi2_1: 1 and 2), KS test of p against uniform, p-value histogram, sign of eta-hat among rejections; E1/E2 pooled
over N with Clopper-Pearson CIs.

Usage (repo root, .venv12, single-thread BLAS):
    python scripts/experiment_05_level_check.py results/experiment_05/confirmatory/5a3afdf728
"""
import glob
import json
import os
import sys

import numpy as np
from scipy import stats


def load(root):
    rows = []
    for f in glob.glob(os.path.join(root, "jobs", "*.json")):
        with open(f) as fh:
            r = json.load(fh)["result"]
        th = r["arms"]["B2"]["theta"]
        row = dict(cell=r["scenario"], N=r["N"], s2=th["sigma2_F"], tauF=th["tau_F"])
        for arm in ("B2", "B1"):
            e = r.get("diag", {}).get(arm, {}).get("by_tau_x", {}).get("2", {})
            row[f"{arm}_p"], row[f"{arm}_eta"], row[f"{arm}_S"] = e.get("p"), e.get("eta_hat"), e.get("stat")
        rows.append(row)
    return rows


def main(root):
    rows = load(root)
    for cell in ("E1", "E2", "E6", "E4"):
        for N in (300, 1000):
            R = [x for x in rows if x["cell"] == cell and x["N"] == N]
            p = np.array([x["B2_p"] for x in R], float)
            eta = np.array([x["B2_eta"] for x in R], float)
            S = np.array([x["B2_S"] for x in R], float)
            rej = p < 0.05
            print(f"{cell} N={N}: n={len(R)} rej={rej.sum()} mean S={S.mean():.3f} var S={S.var(ddof=1):.3f} "
                  f"KS p={stats.kstest(p, 'uniform').pvalue:.3f} hist={np.histogram(p, 10, (0, 1))[0].tolist()}")
            print(f"   eta-hat sign among rejections: neg={int((eta[rej] < 0).sum())} pos={int((eta[rej] > 0).sum())}; "
                  f"mean eta-hat={eta.mean():+.4f} sd={eta.std(ddof=1):.4f}")
            if cell in ("E1", "E2"):
                pb1 = np.array([np.nan if x["B1_p"] is None else x["B1_p"] for x in R], float)
                s2 = np.array([x["s2"] for x in R])
                print(f"   B1-fit rejections: {(pb1 < 0.05).sum()}; sigma2_F-hat rejecting {s2[rej].mean():.3f} vs {s2[~rej].mean():.3f}")
    for cell in ("E1", "E2"):
        P = np.array([x["B2_p"] for x in rows if x["cell"] == cell], float)
        k = int((P < 0.05).sum())
        ci = stats.binomtest(k, len(P)).proportion_ci(method="exact")
        print(f"{cell} pooled over N: {k}/{len(P)} CP [{ci.low:.3f}, {ci.high:.3f}]; p<0.01: {(P < 0.01).sum()}; "
              f"KS p={stats.kstest(P, 'uniform').pvalue:.3f}; hist={np.histogram(P, 10, (0, 1))[0].tolist()}; "
              f"P(X>={k} | p=0.05)={stats.binom.sf(k - 1, len(P), 0.05):.4f}")


if __name__ == "__main__":
    main(sys.argv[1])
