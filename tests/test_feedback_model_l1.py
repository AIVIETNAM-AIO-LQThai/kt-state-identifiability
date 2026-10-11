"""Step-1 tests for the L1 approximation (X6-D07): beta off = L0 exactly, kappa = 0 = the 2PL exactly, proper cells, positive variances."""
import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_counts
from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from discrimination_free.model import Objective2PL, Param2PL
from state_dependence.simulator import simulate_feedback
from feedback_model.fbmodel import ObjectiveFB, ParamFB, cell_prob_table
from feedback_model.fbmodel_l1 import ObjectiveFB1

NI = 48


@pytest.fixture(scope="module")
def ids(templates):
    return item_ids(templates, 12)


@pytest.fixture(scope="module")
def b_true(templates, ids):
    return difficulties(templates, ids, NI)


@pytest.fixture(scope="module")
def pc(cfg, templates, ids):
    ds = simulate_feedback(cfg, 1600, ("fm1", "t"), 3, templates, lam=np.ones(NI), ids=ids, feedback={"kappa": -0.25, "tau_D": 10.0})
    return pair_counts(ds.Y, ds.template_id, len(templates))


def _x(pm, theta, b_true, kappa=-0.2, tau_D=8.0, seed=1):
    rng = np.random.default_rng(seed)
    th = theta.copy(sigma2_F=0.1, tau_F=6.0, sigma2_r=0.02)
    lam = np.exp(rng.normal(0, 0.15, NI)); lam /= np.exp(np.mean(np.log(lam)))
    return pm.pack(th, b_true + rng.normal(0, 0.1, NI), lam, kappa, tau_D)


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_beta_off_equals_l0_exactly(templates, ids, theta, b_true, pc, model):
    pm = ParamFB(model, 4, NI)
    x = _x(pm, theta, b_true, kappa=-0.25, tau_D=10.0)
    l0 = ObjectiveFB(pm, templates, pc, ids).intermediates(x)
    l1 = ObjectiveFB1(pm, templates, pc, ids, beta_on=False).intermediates(x)
    for u, v in zip(l0, l1):
        assert np.abs(u - v).max() < 1e-10
    # and with beta on L1 differs from L0 (feedback present)
    l1b = ObjectiveFB1(pm, templates, pc, ids, beta_on=True).intermediates(x)
    assert max(np.abs(u - v).max() for u, v in zip(l0, l1b)) > 1e-4


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_kappa_zero_equals_2pl(templates, ids, theta, b_true, pc, model):
    pm = ParamFB(model, 4, NI)
    x = _x(pm, theta, b_true, kappa=0.0)
    pm2 = Param2PL(model, 4, NI)
    f2 = Objective2PL(pm2, templates, pc, ids).loglik(x[:pm2.n])
    for beta_on in (True, False):
        assert abs(ObjectiveFB1(pm, templates, pc, ids, beta_on=beta_on).loglik(x) - f2) < 1e-8 * max(1.0, abs(f2))


def test_cells_proper_and_variances_positive_on_grid(templates, ids, theta, b_true, pc):
    pm = ParamFB("B2", 4, NI)
    obj = ObjectiveFB1(pm, templates, pc, ids)
    for kappa in (-0.6, -0.25, 0.3):
        for tau_D in (1.0, 5.0, 10.0, 30.0):
            x = _x(pm, theta, b_true, kappa=kappa, tau_D=tau_D)
            arr, ctxs, _, _ = obj.intermediates(x, keep_ctx=True)
            P = cell_prob_table(*arr)
            assert np.abs(P.sum(-1) - 1.0).max() < 1e-12
            assert P.min() > 0.0
            assert min(c["varR_min"] for c in ctxs) > 0.0, (kappa, tau_D)
            assert min(c["sig2_min"] for c in ctxs) > 0.0
            assert max(c["rho_absmax"] for c in ctxs) < 1.0, (kappa, tau_D)


# ------------------------------------------------------------------------------------------------ Step 2: analytic gradient
def _fd_check(obj, x, idx, tol=1e-5):
    f, g = obj(x)
    for i in idx:
        h = 1e-6 * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        fd = (obj(xp)[0] - obj(xm)[0]) / (2 * h)
        assert abs(g[i] - fd) <= tol * max(abs(fd), 1e-4), (obj.pm.names[i], g[i], fd)


@pytest.mark.parametrize("model", ["B2", "B1"])
@pytest.mark.parametrize("beta_on", [True, False])
def test_l1_gradient_matches_finite_differences(templates, ids, theta, b_true, pc, model, beta_on):
    pm = ParamFB(model, 4, NI)
    obj = ObjectiveFB1(pm, templates, pc, ids, beta_on=beta_on)
    x = _x(pm, theta, b_true)
    rng = np.random.default_rng(0)
    idx = list(range(pm.nt)) + list(rng.choice(np.arange(pm.nt, pm.n - 2), 12, replace=False)) + [pm.n - 2, pm.n - 1]
    _fd_check(obj, x, idx)


@pytest.mark.parametrize("kappa,tau_D", [(-0.6, 3.0), (0.3, 20.0)])
def test_l1_gradient_other_regimes(templates, ids, theta, b_true, pc, kappa, tau_D):
    pm = ParamFB("B2", 4, NI)
    obj = ObjectiveFB1(pm, templates, pc, ids)
    x = _x(pm, theta, b_true, kappa=kappa, tau_D=tau_D, seed=2)
    _fd_check(obj, x, list(range(pm.nt)) + [pm.nt + 3, pm.nt + NI + 5, pm.n - 2, pm.n - 1])


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_l1_beta_off_gradient_equals_l0(templates, ids, theta, b_true, pc, model):
    pm = ParamFB(model, 4, NI)
    x = _x(pm, theta, b_true, kappa=-0.25, tau_D=10.0)
    f0, g0 = ObjectiveFB(pm, templates, pc, ids)(x)
    f1, g1 = ObjectiveFB1(pm, templates, pc, ids, beta_on=False)(x)
    assert abs(f0 - f1) < 1e-10
    assert np.abs(g0 - g1).max() < 1e-9 * max(1.0, np.abs(g0).max())


@pytest.mark.parametrize("model", ["B2", "B1"])
def test_l1_kappa_zero_gradient_equals_2pl(templates, ids, theta, b_true, pc, model):
    pm = ParamFB(model, 4, NI)
    x = _x(pm, theta, b_true, kappa=0.0)
    pm2 = Param2PL(model, 4, NI)
    f2, g2 = Objective2PL(pm2, templates, pc, ids)(x[:pm2.n])
    f1, g1 = ObjectiveFB1(pm, templates, pc, ids)(x)
    assert abs(f1 - f2) < 1e-10
    assert np.abs(g1[:pm2.n] - g2).max() < 1e-9 * max(1.0, np.abs(g2).max())
    assert g1[pm.n2pl + 1] == 0.0
