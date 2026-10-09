"""Operating characteristics of the X3-D15 calibration rule (pooled over N) as a function of the number of warp datasets.
Null CLR ~ 0.5 chi2_0 + 0.5 chi2_1; T scaled so that P(T > q95 of the T* law) equals the true level."""
import numpy as np
from scipy import stats
from difficulty_free.calibration import alpha_hat, pairs_bootstrap_ci, verdict

def draw(rng, n, scale=1.0):
    return np.where(rng.random(n) < 0.5, 0.0, scale * rng.chisquare(1, n))

q = stats.chi2.ppf(0.9, 1)                       # 95 % point of the mixture
for a_true in (0.05, 0.10, 0.13):
    scale = q / stats.chi2.ppf(1 - 2 * a_true, 1)  # P(T > q) = 0.5 P(chi2 > q/scale) = a_true
    for R in (150, 200, 300):
        rng = np.random.default_rng(R); v = []
        for s in range(300):
            T, Ts = draw(rng, R, scale), draw(rng, R)
            v.append(verdict(pairs_bootstrap_ci(T, Ts, B=1000, seed=s)))
        c = {k: v.count(k) / len(v) for k in ("consistent with 5 %", "liberal", "inconclusive")}
        print(f"true alpha {a_true:.2f}  R pooled {R}:  " + "  ".join(f"{k}: {c.get(k, 0):.2f}" for k in c) + f"   (all: {sorted(set(v))})", flush=True)
