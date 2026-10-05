"""Stage-1 tests for difficulty_free: free-b objective and gradient, equivalence with kt_trial, nesting, starts, simulator, recovery."""
import numpy as np
import pytest

from kt_trial.composite_likelihood import composite_loglik, pair_counts
from kt_trial.models import ParamMap
from kt_trial.moments import Theta
from kt_trial.simulator import simulate
from difficulty_free.audit import difficulties
from difficulty_free.fit import fit_free
from difficulty_free.freeb import item_ids
from difficulty_free.model import (FreeObjective, FreeParamMap, marginal_probabilities, start_difficulties, with_difficulties)
from difficulty_free.simulator import draw_lambda, simulate_lambda

NI = 48


@pytest.fixture(scope="module")
def ids(templates):
    return item_ids(templates, 12)


@pytest.fixture(scope="module")
def b_true(templates, ids):
    return difficulties(templates, ids, NI)


@pytest.fixture(scope="module")
def data(cfg, templates, theta):
    ds = simulate(cfg, 1200, ("ff",), 11, templates, theta=theta)
    return ds, pair_counts(ds.Y, ds.template_id, len(templates))


def test_free_objective_equals_kt_trial_when_b_is_the_truth(templates, theta, ids, b_true, data):
    ds, pc = data
    for model in ("B1", "B2"):
        pm = FreeParamMap(model, 4, NI)
        obj = FreeObjective(pm, templates, pc, ids)
        th = theta if model == "B2" else theta.copy(sigma2_F=0.0, tau_F=1.0)
        x = pm.theta_b_to_x(th, b_true)
        ref = composite_loglik(pm.x_to_theta(x), templates, pc, grad=False)[0]
        assert abs(obj.loglik(x) - ref) < 1e-8 * abs(ref)


def test_gradient_matches_finite_differences_including_difficulties(templates, theta, ids, b_true, data):
    ds, pc = data
    pm = FreeParamMap("B2", 4, NI)
    obj = FreeObjective(pm, templates, pc, ids)
    x = pm.theta_b_to_x(theta, b_true) + np.random.default_rng(1).normal(0, 0.03, pm.n)
    f0, g = obj(x)
    for j in [0, 3, 6, 7, 10, pm.nt + 0, pm.nt + 13, pm.nt + 47]:
        h = 1e-6 * max(1.0, abs(x[j]))
        xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
        fd = (obj(xp)[0] - obj(xm)[0]) / (2 * h)
        assert abs(fd - g[j]) < 2e-4 * max(1.0, abs(g[j])) + 1e-9, (pm.names[j], fd, g[j])


def test_b2_free_with_zero_variance_equals_b1_free(templates, theta, ids, b_true, data):
    ds, pc = data
    th1 = theta.copy(sigma2_F=0.0, tau_F=1.0)
    p1, p2 = FreeParamMap("B1", 4, NI), FreeParamMap("B2", 4, NI)
    l1 = FreeObjective(p1, templates, pc, ids).loglik(p1.theta_b_to_x(th1, b_true))
    l2 = FreeObjective(p2, templates, pc, ids).loglik(p2.theta_b_to_x(th1, b_true))
    assert abs(l1 - l2) < 1e-6 * abs(l1)


def test_marginal_probabilities_and_start_difficulties(cfg, templates, theta, ids, b_true, data):
    ds, pc = data
    p = marginal_probabilities(pc)
    for g in (0, 5):
        assert np.allclose(p[g], ds.Y[ds.template_id == g].mean(0), atol=1e-12)
    b0 = start_difficulties(templates, ids, pc, theta, NI)
    assert np.isfinite(b0).all() and abs(np.corrcoef(b0, b_true)[0, 1]) > 0.9 and np.abs(b0 - b_true).mean() < 0.35


def test_simulator_with_unit_lambda_reproduces_kt_trial(cfg, templates, theta, ids):
    a = simulate(cfg, 3000, ("eq",), 5, templates, theta=theta)
    b = simulate_lambda(cfg, 3000, ("eq",), 5, templates, lam=np.ones(NI), ids=ids, theta=theta)
    c = simulate_lambda(cfg, 3000, ("eq",), 5, templates, theta=theta)
    assert np.array_equal(a.Y, c.Y) and np.array_equal(a.template_id, c.template_id)
    assert (a.Y != b.Y).mean() < 1e-3                                   # identical up to rounding of the sum order


def test_lambda_draw_is_isolated_and_has_unit_mean_and_requested_cv():
    lam = draw_lambda(7, "U4", 300, 0, 0.3, 5000)
    assert abs(lam.mean() - 1.0) < 0.02 and abs(lam.std() / lam.mean() - 0.3) < 0.02
    assert np.array_equal(lam, draw_lambda(7, "U4", 300, 0, 0.3, 5000)) and not np.array_equal(lam, draw_lambda(7, "U4", 300, 1, 0.3, 5000))
    assert (draw_lambda(7, "U4", 300, 0, 0.0, 10) == 1.0).all()


def test_discrimination_misfit_changes_responses(cfg, templates, theta, ids):
    lam = draw_lambda(7, "U4", 300, 0, 0.3, NI)
    a = simulate_lambda(cfg, 3000, ("eq",), 5, templates, theta=theta)
    b = simulate_lambda(cfg, 3000, ("eq",), 5, templates, lam=lam, ids=ids, theta=theta)
    assert (a.Y != b.Y).mean() > 0.01


@pytest.mark.slow
def test_b1_free_recovers_difficulties_and_nests_with_known_fit(cfg, templates, theta, ids, b_true):
    ds = simulate(cfg, 2500, ("rec",), 21, templates, theta=theta)
    pc = pair_counts(ds.Y, ds.template_id, len(templates))
    fit_cfg = dict(cfg["fit"], n_starts=2)
    f = fit_free("B1", templates, pc, fit_cfg, 4, ids, NI, ("rec",), 21)
    assert f["status"] == "ok" and f["converged"]
    err = np.array(f["b"]) - b_true
    assert np.sqrt((err ** 2).mean()) < 0.12                           # difficulties recovered at N = 2500
    assert abs(f["theta"]["r_bar"] - 0.35) < 0.08
    assert f["certificate"]["newton_decrement"] <= cfg["fit"]["newton_tol"] or f["certificate"]["hessian_not_pd"]
