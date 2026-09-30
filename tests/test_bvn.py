import numpy as np
from scipy.stats import multivariate_normal as mvn

from kt_trial.bvn import bvn_cdf, cell_probs_and_grads


def test_bvn_against_scipy():
    rng = np.random.default_rng(0)
    worst = 0.0
    for rho in [-0.95, -0.6, -0.3, 0.0, 0.05, 0.3, 0.59, 0.61, 0.85, 0.91, 0.98]:
        for _ in range(25):
            a, b = rng.normal(size=2) * 1.8
            ref = mvn.cdf([a, b], mean=[0, 0], cov=[[1, rho], [rho, 1]], abseps=1e-13, releps=1e-13)
            worst = max(worst, abs(float(bvn_cdf(a, b, rho)) - ref))
    assert worst < 1e-11


def test_series_branch_matches_scipy_over_wide_arguments():
    rng = np.random.default_rng(4)
    worst = 0.0
    for rho in [-0.35, -0.1, 0.02, 0.2, 0.35, 0.36, 0.5]:            # straddles the series / quadrature switch
        for _ in range(40):
            a, b = rng.uniform(-5.5, 5.5, 2)
            ref = mvn.cdf([a, b], mean=[0, 0], cov=[[1, rho], [rho, 1]], abseps=1e-14, releps=1e-14)
            worst = max(worst, abs(float(bvn_cdf(a, b, rho)) - ref))
    assert worst < 1e-11


def test_independent_and_symmetry():
    from scipy.special import ndtr
    assert np.isclose(bvn_cdf(0.3, -0.4, 0.0), ndtr(0.3) * ndtr(-0.4))
    assert np.isclose(bvn_cdf(0.0, 0.0, 0.5), 0.25 + np.arcsin(0.5) / (2 * np.pi))     # closed form
    assert np.isclose(bvn_cdf(0.3, -0.4, 0.5), bvn_cdf(-0.4, 0.3, 0.5))


def test_cells_sum_to_one_and_gradients():
    rng = np.random.default_rng(1)
    a, b, r = rng.normal(size=20), rng.normal(size=20), rng.uniform(-0.8, 0.8, 20)
    p, dp = cell_probs_and_grads(a, b, r)
    assert np.allclose(p.sum(-1), 1.0) and np.all(p > 0) and np.allclose(dp.sum(-2), 0.0, atol=1e-12)
    h = 1e-6
    for k, args in enumerate(((a + h, b, r), (a, b + h, r), (a, b, r + h))):
        pm = cell_probs_and_grads(*[x - (h if i == k else 0) for i, x in enumerate((a, b, r))])[0]
        pp = cell_probs_and_grads(*args)[0]
        assert np.allclose(dp[..., k], (pp - pm) / (2 * h), atol=1e-8)
