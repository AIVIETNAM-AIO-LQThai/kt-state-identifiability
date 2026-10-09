"""Power of a paired comparison delta = alpha-hat(1PL-free) - alpha-hat(2PL) on the same warp datasets (pairs bootstrap over datasets),
with the two estimators' statistics drawn independently (conservative: real pairing is positively correlated)."""
import numpy as np
from scipy import stats

def draw(rng, n, scale=1.0):
    return np.where(rng.random(n) < 0.5, 0.0, scale * rng.chisquare(1, n))

def ah(T, Ts):
    return np.mean(T > np.quantile(Ts, 0.95))

q = stats.chi2.ppf(0.9, 1)
sc = lambda a: q / stats.chi2.ppf(1 - 2 * a, 1)
for a1 in (0.10, 0.13):
    for R in (150, 200, 250, 300):
        rng = np.random.default_rng(R); hit = 0; S = 300
        for s in range(S):
            T1, T1s, T2, T2s = draw(rng, R, sc(a1)), draw(rng, R), draw(rng, R), draw(rng, R)
            idx = rng.integers(0, R, (1000, R))
            d = np.array([ah(T1[i], T1s[i]) - ah(T2[i], T2s[i]) for i in idx])
            hit += np.quantile(d, 0.025) > 0
        print(f"alpha 1PL-free {a1:.2f} vs 2PL 0.05, R pooled {R}: P(CI of delta above 0) = {hit / S:.2f}", flush=True)
