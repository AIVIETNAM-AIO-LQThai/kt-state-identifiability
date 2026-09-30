import numpy as np
import pytest

from kt_trial.config import load_scenario
from kt_trial.moments import Theta, latent_moments, moment_jacobians, N_SCALAR
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


def test_psd_and_symmetry(templates, theta):
    iu = np.triu_indices(templates[0].T, 1)
    for t in templates:
        mu, V = latent_moments(t, theta)
        assert np.allclose(V, V.T) and np.linalg.eigvalsh(V).min() >= 1.0 - 1e-9     # V = I + PSD
        d = np.sqrt(np.diag(V))
        assert np.abs(V[iu] / np.outer(d, d)[iu]).max() < 1.0                       # |rho| < 1


def test_diagonal_matches_formula(templates, theta):
    t = templates[1]
    from kt_trial.moments import histories
    Hs, Hf = histories(t, theta)
    mu, V = latent_moments(t, theta)
    D = 1 + np.diag(theta.Sigma_M)[t.skill] + theta.sigma2_alpha * Hs ** 2 + theta.sigma2_r * Hf ** 2 + theta.sigma2_F
    assert np.allclose(np.diag(V), D)
    assert np.allclose(mu, -t.b + theta.alpha_bar * Hs + theta.r_bar * Hf)


def test_ou_session_reset_in_covariance(templates, theta):
    t = templates[0]
    _, V0 = latent_moments(t, theta)
    _, V1 = latent_moments(t, theta.copy(sigma2_F=0.0))
    dV = V0 - V1
    assert np.all(dV[~t.same_session] == 0.0)                                    # no cross-session F covariance
    i, j = np.flatnonzero(t.session == 0)[[0, 5]]
    assert np.isclose(dV[i, j], theta.sigma2_F * np.exp(-abs(t.time[i] - t.time[j]) / theta.tau_F))


@pytest.mark.slow
def test_analytic_vs_monte_carlo(templates, theta, cfg):
    ds = simulate(cfg, 400_000, ("mc",), 7, templates, keep_latent=True)
    for g in (0, 5):
        Z = ds.latent["Z"][ds.template_id == g]
        mu, V = latent_moments(templates[g], theta)
        assert np.abs(Z.mean(0) - mu).max() < 0.03
        assert np.abs(np.cov(Z.T) - V).max() < 0.05
    # implied marginal success probabilities
    from scipy.stats import norm
    g = 2; t = templates[g]; mu, V = latent_moments(t, theta)
    assert np.abs(ds.Y[ds.template_id == g].mean(0) - norm.cdf(mu / np.sqrt(np.diag(V)))).max() < 0.012


@pytest.mark.slow
def test_session_reset_clean_vs_S6():
    ts = build_templates(load_scenario("S1"))
    t0 = ts[0]
    first = [int(np.flatnonzero(t0.session == s)[0]) for s in range(3)]           # first obs of each practice session
    for sid, expect in (("S1", 0.0), ("S6", 0.16 * 0.5)):
        cfg = load_scenario(sid)
        ds = simulate(cfg, 80_000, ("reset",), 3, ts, keep_latent=True)
        F = ds.latent["F"][ds.template_id == 0]
        cov01 = np.mean(F[:, first[0]] * F[:, first[1]])
        assert abs(cov01 - expect) < 0.02, (sid, cov01)                          # rho_S sigma_F^2 under S6, 0 if clean
        assert abs(F[:, first[0]].var() - 0.16) < 0.01                           # stationary start variance kept


@pytest.mark.slow
def test_S7_error_jump_shifts_next_F():
    ts = build_templates(load_scenario("S1"))
    cfg = load_scenario("S7")
    ds = simulate(cfg, 80_000, ("s7",), 4, ts, keep_latent=True)
    m = ds.template_id == 0
    t = 10; a = np.exp(-(ts[0].time[t + 1] - ts[0].time[t]) / 10.0)
    err = ds.Y[m][:, t] == 0
    d = ds.latent["F"][m][err, t + 1].mean() - ds.latent["F"][m][~err, t + 1].mean()
    # jump persists as a * delta relative to the no-jump path (plus selection effect through F_t itself)
    assert d < -0.05 * 0.25                                                       # clearly negative shift
    ds0 = simulate(load_scenario("S1"), 80_000, ("s7",), 4, ts, keep_latent=True)
    m0 = ds0.template_id == 0
    F0 = ds0.latent["F"][m0]; e0 = ds0.Y[m0][:, t] == 0
    d0 = F0[e0, t + 1].mean() - F0[~e0, t + 1].mean()
    assert d < d0 - 0.15 * a                                                      # jump adds ~ a*|delta| beyond selection


@pytest.mark.slow
def test_S8_gain_distribution():
    ts = build_templates(load_scenario("S1"))
    ds = simulate(load_scenario("S8"), 60_000, ("s8",), 5, ts, keep_latent=True)
    r = ds.meta["realised"]
    assert abs(r["cv_alpha"] - 0.6) < 0.03 and abs(r["cv_r"] - 0.6) < 0.03
    assert 0.3 < r["corr_alpha_meanM0"] < 0.5                                     # 0.5 latent, attenuated by lognormal
    assert ds.latent["alpha"].min() > 0 and abs(ds.latent["alpha"].mean() - 0.15) < 0.003


def test_deterministic_simulation(cfg, templates):
    a = simulate(cfg, 500, ("d",), 11, templates); b = simulate(cfg, 500, ("d",), 11, templates)
    c = simulate(cfg, 500, ("d",), 12, templates)
    assert np.array_equal(a.Y, b.Y) and np.array_equal(a.template_id, b.template_id)
    assert not np.array_equal(a.Y, c.Y)


def test_jacobians_vs_finite_difference(templates, theta):
    t = templates[3]
    mu, V, dmu, dV = moment_jacobians(t, theta)
    x0 = theta.to_nat(); K = theta.Sigma_M.shape[0]
    for j in range(len(x0)):
        h = 1e-6 * max(1.0, abs(x0[j]))
        xp, xm = x0.copy(), x0.copy(); xp[j] += h; xm[j] -= h
        mp, Vp = latent_moments(t, Theta.from_nat(xp, K)); mm, Vm = latent_moments(t, Theta.from_nat(xm, K))
        assert np.allclose(dmu[:, j], (mp - mm) / (2 * h), atol=2e-6), j
        assert np.allclose(dV[:, :, j], (Vp - Vm) / (2 * h), atol=2e-6), j


def test_negative_gains_not_clipped(cfg, templates):
    ds = simulate(cfg, 20000, ("gain",), 5, templates, keep_latent=True)
    assert ds.latent["alpha"].min() < 0.0                                          # Gaussian gains keep negative draws
