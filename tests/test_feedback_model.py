"""Stage-0 tests for feedback_model (G0-1): kappa = 0 equals the 2PL objective, analytic gradients against finite differences, cell probabilities,
the schedule-term model, and a likelihood-ordering sanity check of the L0 approximation."""
import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_counts
from kt_trial.moments import Theta
from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from discrimination_free.model import Objective2PL, Param2PL
from state_dependence import diagnostic as DG
from state_dependence.simulator import simulate_feedback
from feedback_model.etamodel import ObjectiveEta, ParamEta
from feedback_model.fbmodel import ObjectiveFB, ParamFB, cell_prob_table

NI = 48


@pytest.fixture(scope="module")
def ids(templates):
    return item_ids(templates, 12)


@pytest.fixture(scope="module")
def b_true(templates, ids):
    return difficulties(templates, ids, NI)


@pytest.fixture(scope="module")
def data(cfg, templates, ids):
    fb = {"kappa": -0.25, "tau_D": 10.0}
    ds = simulate_feedback(cfg, 1600, ("fm", "t"), 3, templates, lam=np.ones(NI), ids=ids, feedback=fb)
    return ds, pair_counts(ds.Y, ds.template_id, len(templates))


def _x(pm, theta, b_true, kappa=-0.2, tau_D=8.0, seed=1):
    rng = np.random.default_rng(seed)
    th = theta.copy(sigma2_F=0.1, tau_F=6.0, sigma2_r=0.02)
    lam = np.exp(rng.normal(0, 0.15, NI)); lam /= np.exp(np.mean(np.log(lam)))
    return pm.pack(th, b_true + rng.normal(0, 0.1, NI), lam, kappa, tau_D)


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_kappa_zero_equals_2pl_objective_and_gradient(templates, ids, theta, b_true, data, model):
    ds, pc = data
    pm = ParamFB(model, 4, NI)
    obj = ObjectiveFB(pm, templates, pc, ids)
    x = _x(pm, theta, b_true, kappa=0.0)
    f, g = obj(x)
    pm2 = Param2PL(model, 4, NI)
    f2, g2 = Objective2PL(pm2, templates, pc, ids)(x[:pm2.n])
    assert abs(f - f2) < 1e-12
    assert np.abs(g[:pm2.n] - g2).max() < 1e-12
    assert g[pm.n2pl] != 0.0 and g[pm.n2pl + 1] == 0.0            # kappa has a gradient, tau_D has none at kappa = 0


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_fb_gradient_matches_finite_differences(templates, ids, theta, b_true, data, model):
    ds, pc = data
    pm = ParamFB(model, 4, NI)
    obj = ObjectiveFB(pm, templates, pc, ids)
    x = _x(pm, theta, b_true)
    f, g = obj(x)
    rng = np.random.default_rng(0)
    idx = list(rng.choice(pm.n - 2, 10, replace=False)) + [pm.n - 2, pm.n - 1]
    for i in idx:
        h = 1e-6 * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        fd = (obj(xp)[0] - obj(xm)[0]) / (2 * h)
        assert abs(g[i] - fd) <= 1e-5 * max(abs(fd), 1e-4), (pm.names[i], g[i], fd)


def test_cell_probabilities_sum_to_one_and_are_proper(templates, ids, theta, b_true, data):
    ds, pc = data
    pm = ParamFB("B2", 4, NI)
    obj = ObjectiveFB(pm, templates, pc, ids)
    for kappa in (-0.25, -0.6, 0.3):
        P = cell_prob_table(*obj.intermediates(_x(pm, theta, b_true, kappa=kappa)))
        assert np.abs(P.sum(-1) - 1.0).max() < 1e-12
        assert P.min() > 0.0


def test_eta_gradient_matches_finite_differences_and_eta_zero_is_2pl(templates, ids, theta, b_true, data):
    ds, pc = data
    ph = DG.item_success(ds.Y, ds.template_id, ids, NI)
    xc = DG.carry_covariate(templates, ids, ph, 2.0)
    pm = ParamEta("B2", 4, NI)
    obj = ObjectiveEta(pm, templates, pc, ids, xc)
    x = pm.from_2pl(_x(ParamFB("B2", 4, NI), theta, b_true)[:pm.n2pl], 0.15)
    f, g = obj(x)
    for i in (pm.n - 1, 4, 30, 70):
        h = 1e-6 * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        fd = (obj(xp)[0] - obj(xm)[0]) / (2 * h)
        assert abs(g[i] - fd) <= 1e-5 * max(abs(fd), 1e-4), (pm.names[i], g[i], fd)
    x0 = x.copy(); x0[-1] = 0.0
    pm2 = Param2PL("B2", 4, NI)
    f2, _ = Objective2PL(pm2, templates, pc, ids)(x0[:pm2.n])
    assert abs(obj(x0)[0] - f2) < 1e-12


def test_true_feedback_beats_no_feedback_at_true_parameters(cfg, templates, ids, b_true):
    """On data with feedback, the L0 log-likelihood at the true parameters exceeds that of the same parameters with kappa = 0
    (a sanity check of the sign and scale of the approximation, not a proof of its accuracy)."""
    th = Theta.from_dict(__import__("kt_trial.config", fromlist=["x"]).generating_theta_dict(cfg))
    ds = simulate_feedback(cfg, 6000, ("fm", "ord"), 11, templates, lam=np.ones(NI), ids=ids, feedback={"kappa": -0.25, "tau_D": 10.0})
    pc = pair_counts(ds.Y, ds.template_id, len(templates))
    pm = ParamFB("B2", 4, NI)
    obj = ObjectiveFB(pm, templates, pc, ids)
    x1 = pm.pack(th, b_true, np.ones(NI), -0.25, 10.0)
    x0 = pm.pack(th, b_true, np.ones(NI), 0.0, 10.0)
    assert obj.loglik(x1) > obj.loglik(x0)
