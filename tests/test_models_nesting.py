import numpy as np
import pytest

from kt_trial.composite_likelihood import composite_loglik, pair_counts
from kt_trial.config import load_scenario
from kt_trial.models import INACTIVE, MODEL_FREE, ParamMap, embed
from kt_trial.moments import Theta
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


@pytest.fixture(scope="module")
def small():
    cfg = load_scenario("S1")
    ts = build_templates(cfg)[:2]
    ds = simulate(cfg, 200, ("nest",), 1, ts)
    return ts, pair_counts(ds.Y, ds.template_id, 2)


def test_parameter_counts():
    assert [ParamMap(m, 4).n for m in ("B0", "B1", "B2")] == [13, 16, 18]


def test_transform_round_trip_and_jacobian(theta):
    for m in ("B0", "B1", "B2"):
        pm = ParamMap(m, 4)
        th = embed(theta, m)
        x = pm.theta_to_x(th)
        assert np.allclose(pm.x_to_theta(x).to_nat(), th.to_nat(), atol=1e-12)
        J = pm.jacobian(x)
        for j in range(pm.n):
            h = 1e-6; xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
            fd = (pm.x_to_theta(xp).to_nat() - pm.x_to_theta(xm).to_nat()) / (2 * h)
            assert np.allclose(J[:, j], fd, atol=1e-7)


def test_sigma_M_psd_by_construction():
    pm = ParamMap("B2", 4)
    rng = np.random.default_rng(0)
    for _ in range(20):
        x = rng.uniform(pm.lb, pm.ub)
        assert np.linalg.eigvalsh(pm.x_to_theta(x).Sigma_M).min() > 0


def test_variance_lower_bounds_admit_exact_zero():
    pm = ParamMap("B2", 4)
    for n in ("sigma2_alpha", "sigma2_r", "sigma2_F"):
        assert pm.lb[pm.names.index(n)] == 0.0
    x = pm.lb.copy(); x[pm.names.index("tau_F")] = 0.0
    assert pm.x_to_theta(x).sigma2_F == 0.0


def test_b2_reduces_to_b1_and_b1_to_b0(small, theta):
    ts, pc = small
    ll_b2, g2, _ = composite_loglik(embed(theta, "B2").copy(sigma2_F=0.0, tau_F=37.0), ts, pc)
    ll_b1, g1, _ = composite_loglik(embed(theta, "B1"), ts, pc)
    assert ll_b2 == pytest.approx(ll_b1, rel=0, abs=1e-8 * abs(ll_b1))
    assert g2[7] == 0.0                                    # tau_F is inert at sigma2_F = 0
    th0 = theta.copy(r_bar=0.0, sigma2_r=0.0, sigma2_F=0.0)
    ll_b1_0, g, _ = composite_loglik(th0, ts, pc)
    ll_b0, _, _ = composite_loglik(embed(theta, "B0"), ts, pc)
    assert ll_b1_0 == pytest.approx(ll_b0, abs=1e-8 * abs(ll_b0))
    assert g[4] == 0.0                                     # tau_R inert when r_bar = sigma2_r = 0
    assert set(MODEL_FREE["B0"]) < set(MODEL_FREE["B1"]) < set(MODEL_FREE["B2"])


def test_inactive_values():
    assert INACTIVE["sigma2_F"] == 0.0 and INACTIVE["r_bar"] == 0.0
