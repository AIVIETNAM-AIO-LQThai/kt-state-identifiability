"""Stage-0 tests for discrimination_free: 2PL moment map, derivatives, equivalence with difficulty_free at lambda == 1,
and the scale invariance that forces the geometric-mean-one normalisation."""
import copy

import numpy as np
import pytest

from kt_trial.models import ParamMap
from kt_trial.moments import Theta
from difficulty_free.audit import difficulties
from difficulty_free.freeb import fisher_free, item_ids, observable_jacobian_free
from difficulty_free.simulator import draw_lambda
from discrimination_free import twopl

NI, I_PER_SKILL = 48, 12


@pytest.fixture(scope="module")
def setup(cfg, templates, theta):
    pm = ParamMap("B2", 4)
    x = pm.theta_to_x(theta)
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    ids = item_ids(templates, I_PER_SKILL)
    return pm, x, iu, ju, ids


def _with_b(templates, ids, q, h):
    out = []
    for g, t in enumerate(templates):
        d = copy.copy(t); d.b = t.b + h * (ids[g] == q); out.append(d)
    return out


def _values(theta, templates, ids, lam, iu, ju):
    from scipy.special import ndtr
    from kt_trial.bvn import cell_probs_and_grads
    c = twopl.core(theta, templates, ids, lam, iu, ju, need_jac=False)
    p, _ = cell_probs_and_grads(c["a"][:, iu], c["a"][:, ju], c["rho"])
    return np.concatenate([ndtr(c["a"]).ravel(), p[..., 0].ravel()])


def test_sumzero_basis_is_orthonormal_and_sums_to_zero():
    P = twopl.sumzero_basis(NI)
    assert P.shape == (NI, NI - 1) and np.allclose(P.T @ P, np.eye(NI - 1), atol=1e-12) and np.abs(P.sum(0)).max() < 1e-12


def test_lambda_one_reproduces_difficulty_free(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    lam = np.ones(NI)
    m = twopl.assemble(pm, x, theta, templates, ids, lam, iu, ju, free_b=True, free_lam=False)
    v1, J1 = observable_jacobian_free(pm, x, templates, iu, ju, ids, NI, True)
    v2, J2 = twopl.observable_jacobian(m, iu, ju)
    assert np.allclose(v1, v2, atol=1e-12) and np.allclose(J1, J2, atol=1e-10)
    H1, H2 = fisher_free(pm, x, templates, iu, ju, ids, NI, True), twopl.fisher(m, iu, ju)
    assert np.allclose(H1, H2, rtol=1e-8, atol=1e-8)


def test_derivative_in_lambda_matches_finite_differences(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    c = twopl.core(theta, templates, ids, lam, iu, ju)
    from scipy.special import ndtr
    from kt_trial.bvn import cell_probs_and_grads
    p, dp = cell_probs_and_grads(c["a"][:, iu], c["a"][:, ju], c["rho"])
    d11 = dp[..., 0, :]
    dmarg = (np.exp(-0.5 * c["a"] ** 2) / np.sqrt(2 * np.pi))[..., None] * c["dA_l"]
    dj = d11[..., 0:1] * c["dA_l"][:, iu] + d11[..., 1:2] * c["dA_l"][:, ju] + d11[..., 2:3] * c["dR_l"]
    Jl = np.concatenate([dmarg.reshape(-1, NI), dj.reshape(-1, NI)], 0)
    h = 1e-6
    for q in (0, 19, 47):
        lp, lm = lam.copy(), lam.copy(); lp[q] += h; lm[q] -= h
        fd = (_values(theta, templates, ids, lp, iu, ju) - _values(theta, templates, ids, lm, iu, ju)) / (2 * h)
        assert np.abs(fd - Jl[:, q]).max() < 2e-7, q


def test_derivative_in_difficulty_matches_finite_differences(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    m = twopl.assemble(pm, x, theta, templates, ids, lam, iu, ju, free_b=True, free_lam=False)
    _, J = twopl.observable_jacobian(m, iu, ju)
    h = 1e-5
    for q in (1, 30):
        fd = (_values(theta, _with_b(templates, ids, q, h), ids, lam, iu, ju)
              - _values(theta, _with_b(templates, ids, q, -h), ids, lam, iu, ju)) / (2 * h)
        assert np.abs(fd - J[:, pm.n + q]).max() < 1e-7


def test_derivative_in_model_parameters_matches_finite_differences(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    m = twopl.assemble(pm, x, theta, templates, ids, lam, iu, ju, free_b=False, free_lam=False)
    _, J = twopl.observable_jacobian(m, iu, ju)
    for j in (0, 3, 6, 7, 9):
        h = 1e-6 * max(1.0, abs(x[j]))
        xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
        fd = (_values(pm.x_to_theta(xp), templates, ids, lam, iu, ju) - _values(pm.x_to_theta(xm), templates, ids, lam, iu, ju)) / (2 * h)
        assert np.abs(fd - J[:, j]).max() < 5e-6, pm.names[j]


def test_scale_invariance_of_the_observables(templates, theta, setup):
    """(lambda c, locations/c, variances/c^2) leaves a and rho unchanged: the reason for the geometric-mean-one constraint."""
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    c = 1.37
    th2 = theta.copy(alpha_bar=theta.alpha_bar / c, r_bar=theta.r_bar / c, sigma2_alpha=theta.sigma2_alpha / c ** 2,
                     sigma2_r=theta.sigma2_r / c ** 2, sigma2_F=theta.sigma2_F / c ** 2, Sigma_M=theta.Sigma_M / c ** 2)
    c1 = twopl.core(theta, templates, ids, lam, iu, ju, need_jac=False)
    c2 = twopl.core(th2, templates, ids, lam * c, iu, ju, need_jac=False)
    assert np.abs(c1["a"] - c2["a"]).max() < 1e-10 and np.abs(c1["rho"] - c2["rho"]).max() < 1e-10


def test_normalise_gives_geometric_mean_one_and_the_same_observables(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    th_n, lam_n, g = twopl.normalise(theta, lam)
    assert abs(np.mean(np.log(lam_n))) < 1e-12 and abs(g - np.exp(np.mean(np.log(lam)))) < 1e-12
    assert abs(th_n.sigma2_F - g * g * theta.sigma2_F) < 1e-15
    c1 = twopl.core(theta, templates, ids, lam, iu, ju, need_jac=False)
    c2 = twopl.core(th_n, templates, ids, lam_n, iu, ju, need_jac=False)
    assert np.abs(c1["a"] - c2["a"]).max() < 1e-10 and np.abs(c1["rho"] - c2["rho"]).max() < 1e-10


def test_scores_have_mean_zero_at_the_truth_and_known_block_matches(cfg, templates, theta, setup):
    from difficulty_free.simulator import simulate_lambda
    pm, x, iu, ju, ids = setup
    lam = draw_lambda(3, "t", 300, 0, 0.3, NI)
    th_n, lam_n, g = twopl.normalise(theta, lam)
    xn = pm.theta_to_x(th_n)
    ds = simulate_lambda(cfg, 2400, ("sc2",), 5, templates, lam=lam, ids=ids, theta=theta)
    m = twopl.assemble(pm, xn, th_n, templates, ids, lam_n, iu, ju)
    S = twopl.learner_scores(m, ds.Y, ds.template_id)
    assert S.shape[1] == pm.n + NI + (NI - 1)
    t = S.mean(0) / (S.std(0) / np.sqrt(len(S)) + 1e-300)
    assert np.abs(t).max() < 4.6, np.abs(t).max()
