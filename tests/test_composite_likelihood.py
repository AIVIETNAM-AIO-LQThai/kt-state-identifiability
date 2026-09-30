import numpy as np
from scipy.stats import multivariate_normal as mvn
from scipy.stats import norm

from kt_trial.bvn import cell_probs_and_grads
from kt_trial.composite_likelihood import (composite_loglik, learner_scores_nat, pair_counts,
                                           pair_quantities)
from kt_trial.config import load_scenario
from kt_trial.moments import Theta, latent_moments
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


def _small():
    cfg = load_scenario("S1")
    return cfg, build_templates(cfg)[:2]


def _scipy_cells(mu, V, i, j):
    cov = V[np.ix_([i, j], [i, j])]
    m = mu[[i, j]]
    p11 = mvn.cdf(m, mean=[0, 0], cov=cov, abseps=1e-13, releps=1e-13)      # P(Z_i>0, Z_j>0) by symmetry
    pa, pb = norm.cdf(m[0] / np.sqrt(cov[0, 0])), norm.cdf(m[1] / np.sqrt(cov[1, 1]))
    return np.array([p11, pa - p11, pb - p11, 1 - pa - pb + p11])


def test_counts_tiny_hand_case():
    Y = np.array([[1, 0, 1], [1, 1, 0], [0, 0, 1], [1, 0, 1]], dtype=np.int8)
    pc = pair_counts(Y, np.zeros(4, int), 1)
    k = list(zip(pc.iu, pc.ju)).index((0, 1))          # rows -> (1,0),(1,1),(0,0),(1,0)
    assert pc.counts[0, k].tolist() == [1, 2, 0, 1]
    assert pc.counts[0].sum() == 4 * 3 and pc.N == 4


def test_pair_cell_probabilities_match_scipy(theta):
    _, ts = _small()
    mu, V = latent_moments(ts[0], theta)
    for (i, j) in [(3, 40), (0, 1), (100, 111), (50, 60)]:
        iu, ju = np.array([i]), np.array([j])
        pj = pair_quantities(theta, [ts[0]], iu, ju, need_jac=False)
        p, _ = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
        assert np.allclose(p[0, 0], _scipy_cells(mu, V, i, j), atol=1e-10)


def test_loglik_equals_hand_sum_over_selected_pairs(theta):
    cfg, ts = _small()
    ds = simulate(cfg, 40, ("cl3",), 3, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    pairs = [(0, 1), (5, 40), (10, 111), (100, 111), (50, 60)]
    expected = 0.0
    keep = np.zeros(len(pc.iu), bool)
    for g, t in enumerate(ts):
        mu, V = latent_moments(t, theta)
        for (i, j) in pairs:
            k = list(zip(pc.iu, pc.ju)).index((i, j))
            keep[k] = True
            expected += float((pc.counts[g, k] * np.log(_scipy_cells(mu, V, i, j))).sum())
    pc.counts[:, ~keep, :] = 0
    assert np.isclose(composite_loglik(theta, ts, pc, grad=False)[0], expected, rtol=1e-10)


def test_gradient_matches_finite_difference(theta):
    cfg, ts = _small()
    ds = simulate(cfg, 300, ("cl",), 1, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    ll, g, diag = composite_loglik(theta, ts, pc)
    assert diag["finite"] and diag["n_floored_cells"] == 0
    x0 = theta.to_nat()
    for j in range(len(x0)):
        h = 1e-6 * max(1.0, abs(x0[j]))
        xp, xm = x0.copy(), x0.copy(); xp[j] += h; xm[j] -= h
        fd = (composite_loglik(Theta.from_nat(xp, 4), ts, pc, grad=False)[0]
              - composite_loglik(Theta.from_nat(xm, 4), ts, pc, grad=False)[0]) / (2 * h)
        assert abs(g[j] - fd) <= 1e-5 * max(1.0, abs(fd)), (j, g[j], fd)


def test_scores_sum_to_gradient(theta):
    cfg, ts = _small()
    ds = simulate(cfg, 120, ("cl2",), 2, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    _, g, _ = composite_loglik(theta, ts, pc)
    S = learner_scores_nat(theta, ts, ds.Y, ds.template_id)
    assert np.allclose(S.sum(0), g, rtol=1e-8, atol=1e-6)
