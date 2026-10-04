"""Focused tests for the Experiment-3 Stage-0 audit (difficulty_free): derivatives in b, agreement with kt_trial when b is
known, and the exact white-noise scale ridge that exists when b is free."""
import copy

import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_quantities
from kt_trial.identifiability import fisher_pairwise, observable_jacobian
from kt_trial.models import ParamMap
from kt_trial.moments import Theta
from difficulty_free.freeb import (fisher_free, item_ids, learner_scores_free, observable_jacobian_free, ridge_tangent_nat)
from difficulty_free.audit import audit_point, difficulties

I_PER_SKILL, N_ITEMS = 12, 48


@pytest.fixture(scope="module")
def setup(cfg, templates, theta):
    pm = ParamMap("B2", 4)
    x = pm.theta_to_x(theta)
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    ids = item_ids(templates, I_PER_SKILL)
    return pm, x, iu, ju, ids


def _templates_with_b(templates, ids, q, h):
    out = []
    for g, t in enumerate(templates):
        d = copy.copy(t)
        d.b = t.b + h * (ids[g] == q)
        out.append(d)
    return out


def _values(pm, x, templates, iu, ju):
    from scipy.special import ndtr
    from kt_trial.bvn import cell_probs_and_grads
    pj = pair_quantities(pm.x_to_theta(x), templates, iu, ju, need_jac=False)
    p, _ = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    return np.concatenate([ndtr(pj.a).ravel(), p[..., 0].ravel()])


def test_item_ids_cover_48_items_and_difficulty_is_consistent(templates):
    ids = item_ids(templates, I_PER_SKILL)
    assert ids.min() == 0 and ids.max() == N_ITEMS - 1
    for g, t in enumerate(templates):                       # one difficulty per item across all templates
        for q in np.unique(ids[g]):
            assert len(np.unique(t.b[ids[g] == q])) == 1
    b = difficulties(templates, ids, N_ITEMS)
    assert np.isfinite(b).all()


def test_difficulty_derivative_matches_finite_differences(templates, setup):
    pm, x, iu, ju, ids = setup
    _, J = observable_jacobian_free(pm, x, templates, iu, ju, ids, N_ITEMS, True)
    h = 1e-5
    for q in (0, 17, 47):
        fd = (_values(pm, x, _templates_with_b(templates, ids, q, h), iu, ju)
              - _values(pm, x, _templates_with_b(templates, ids, q, -h), iu, ju)) / (2 * h)
        assert np.abs(fd - J[:, pm.n + q]).max() < 1e-7


def test_known_b_block_equals_kt_trial(templates, setup):
    pm, x, iu, ju, ids = setup
    v1, J1 = observable_jacobian(pm, x, templates, iu, ju)
    v2, J2 = observable_jacobian_free(pm, x, templates, iu, ju, ids, N_ITEMS, False)
    assert np.allclose(v1, v2) and np.allclose(J1, J2, atol=1e-12)
    _, J3 = observable_jacobian_free(pm, x, templates, iu, ju, ids, N_ITEMS, True)
    assert np.allclose(J3[:, :pm.n], J1, atol=1e-12)
    H1 = fisher_pairwise(pm, x, templates, iu, ju)
    H2 = fisher_free(pm, x, templates, iu, ju, ids, N_ITEMS, False)
    H3 = fisher_free(pm, x, templates, iu, ju, ids, N_ITEMS, True)
    assert np.allclose(H1, H2) and np.allclose(H3[:pm.n, :pm.n], H1)
    assert np.allclose(H3, H3.T) and np.linalg.eigvalsh(H3).min() > -1e-9


def test_scores_known_block_equals_kt_trial_and_are_centred(cfg, templates, theta, setup):
    from kt_trial.composite_likelihood import learner_scores_nat
    from kt_trial.simulator import simulate
    pm, x, iu, ju, ids = setup
    ds = simulate(cfg, 2400, ("sc",), 5, templates, theta=theta)
    S = learner_scores_free(pm, x, templates, ds.Y, ds.template_id, ids, N_ITEMS, True)
    S0 = learner_scores_nat(theta, templates, ds.Y, ds.template_id) @ pm.jacobian(x)
    assert np.allclose(S[:, :pm.n], S0, atol=1e-10)
    t = S.mean(0) / (S.std(0) / np.sqrt(len(S)) + 1e-300)
    assert np.abs(t[pm.n:]).max() < 4.5                      # scores in the difficulties have mean zero at the truth


def _scaled(th, c, tau):
    nat = th.to_nat()
    out = th.copy(alpha_bar=c * th.alpha_bar, r_bar=c * th.r_bar, sigma2_alpha=c * c * th.sigma2_alpha,
                  sigma2_r=c * c * th.sigma2_r, sigma2_F=c * c * (1.0 + th.sigma2_F) - 1.0, tau_F=tau,
                  Sigma_M=c * c * th.Sigma_M)
    return out


def test_white_noise_scale_ridge_is_exact_only_for_white_F(templates, theta):
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    c = 0.9
    tiny = 1e-6                                              # F white at the design lags (>= 0.4 min)
    th_w = theta.copy(tau_F=tiny)
    sc_t = []
    for t in templates:
        d = copy.copy(t); d.b = c * t.b; sc_t.append(d)
    pj0 = pair_quantities(th_w, templates, iu, ju, need_jac=False)
    pj1 = pair_quantities(_scaled(th_w, c, tiny), sc_t, iu, ju, need_jac=False)
    assert np.abs(pj0.a - pj1.a).max() < 1e-10 and np.abs(pj0.rho - pj1.rho).max() < 1e-10
    pj2 = pair_quantities(theta, templates, iu, ju, need_jac=False)                       # tau_F = 10: OU covariance
    pj3 = pair_quantities(_scaled(theta, c, theta.tau_F), sc_t, iu, ju, need_jac=False)
    assert np.abs(pj2.rho - pj3.rho).max() > 1e-3            # the OU kernel breaks the ridge


def test_ridge_tangent_is_a_null_direction_of_the_white_model(templates, theta, setup):
    pm, x, iu, ju, ids = setup
    th_w = theta.copy(tau_F=1e-6)
    xw = pm.theta_to_x(th_w)
    b = difficulties(templates, ids, N_ITEMS)
    _, J = observable_jacobian_free(pm, xw, templates, iu, ju, ids, N_ITEMS, True)
    vnat, vb = ridge_tangent_nat(th_w, b, N_ITEMS)
    vx = np.linalg.lstsq(pm.jacobian(xw), vnat, rcond=None)[0]
    v = np.concatenate([vx, vb])
    resp = np.linalg.norm(J @ v) / np.linalg.norm(J, 2) / np.linalg.norm(v)
    assert resp < 1e-6


@pytest.mark.slow
def test_audit_point_smoke(cfg, templates, theta):
    ac = {"rank_rel_sv": 1e-8, "score_learners": 2000, "N_list": [300, 1000]}
    r = audit_point("generating", cfg, templates, theta, ac, 20261001)
    assert r["b_known"]["n_params"] == 18 and r["b_free"]["n_params"] == 66
    assert r["b_known"]["full_numerical_rank"]
    g = r["godambe_b_known"]
    assert g["se"]["300"] > g["se"]["1000"] > 0 and not g["singular"]
    assert 0.01 < g["se"]["300"] < 0.08                       # same order as the Experiment-1 audit (0.0385)
