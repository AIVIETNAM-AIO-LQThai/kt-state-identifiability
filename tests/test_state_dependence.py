"""Stage-0 tests for state_dependence (G0-1): simulator equivalences, score and information correctness, invariances, null/alternative smoke."""
import numpy as np
import pytest

from kt_trial.bvn import weighted_cell_loglik_obs
from kt_trial.composite_likelihood import P_FLOOR, pair_counts
from kt_trial.config import load_scenario
from kt_trial.simulator import simulate
from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from difficulty_free.simulator import draw_lambda, simulate_lambda
from discrimination_free import twopl
from state_dependence import diagnostic as DG
from state_dependence.simulator import simulate_feedback

NI = 48


@pytest.fixture(scope="module")
def ids(templates):
    return item_ids(templates, 12)


@pytest.fixture(scope="module")
def b_true(templates, ids):
    return difficulties(templates, ids, NI)


def test_kappa_zero_equals_simulate_lambda_bit_for_bit(cfg, templates, theta, ids):
    for lam in (None, draw_lambda(5, "t", 300, 0, 0.3, NI)):
        a = simulate_lambda(cfg, 600, ("e5", "a"), 77, templates, lam=lam, ids=ids, theta=theta)
        for fb in (None, {"kappa": 0.0, "tau_D": 10.0}):
            b = simulate_feedback(cfg, 600, ("e5", "a"), 77, templates, lam=lam, ids=ids, theta=theta, feedback=fb)
            assert np.array_equal(a.Y, b.Y) and np.array_equal(a.template_id, b.template_id)


def test_tau_D_equals_tau_F_reproduces_S7(cfg, templates):
    """F + D with tau_D = tau_F and lambda == 1 is kt_trial's S7 process: identical responses and latent."""
    s7 = load_scenario("S7")
    assert s7["dgp"]["error_jump"] == -0.25 and cfg["generating"]["tau_F"] == s7["generating"]["tau_F"]
    ref = simulate(s7, 20000, ("e5", "s7"), 78, templates, keep_latent=True)
    new = simulate_feedback(cfg, 20000, ("e5", "s7"), 78, templates, lam=np.ones(NI), ids=item_ids(templates, 12),
                            feedback={"kappa": -0.25, "tau_D": cfg["generating"]["tau_F"]}, keep_latent=True)
    assert np.array_equal(ref.Y, new.Y)
    assert np.abs(ref.latent["F"] - (new.latent["F"] + new.latent["D"])).max() < 1e-12


def test_feedback_state_resets_and_only_practice_errors_feed_back(cfg, templates, ids):
    ds = simulate_feedback(cfg, 2000, ("e5", "r"), 79, templates, lam=None, ids=ids, feedback={"kappa": -0.25, "tau_D": 5.0}, keep_latent=True)
    D = ds.latent["D"]
    for g, tpl in enumerate(templates):
        rows = ds.template_id == g
        starts = [t for t in range(tpl.T) if t == 0 or tpl.session[t] != tpl.session[t - 1]]
        assert np.all(D[np.ix_(rows, starts)] == 0.0)
        assert np.all(D[np.ix_(rows, np.flatnonzero(~tpl.practice))] == 0.0)          # probe session: nothing carries in
    assert D.max() <= 0.0 and D.min() < -0.1
    with pytest.raises(ValueError):
        simulate_feedback(load_scenario("S7"), 10, ("x",), 1, templates, feedback=None)


def _fake_fit(theta, b_true, lam):
    from discrimination_free.model import Param2PL
    pm = Param2PL("B2", 4, NI)
    th_n, lam_n, g = twopl.normalise(theta, lam)
    return {"model": "B2", "x": pm.pack(th_n, b_true, lam_n).tolist(), "b": list(b_true), "lam": lam_n.tolist()}


@pytest.fixture(scope="module")
def clean_data(cfg, templates, theta, ids):
    ds = simulate_feedback(cfg, 20000, ("e5", "clean"), 80, templates, lam=None, ids=ids, theta=theta)
    return ds, pair_counts(ds.Y, ds.template_id, len(templates))


def test_eta_score_and_information_match_finite_differences(cfg, templates, theta, ids, b_true, clean_data):
    ds, pc = clean_data
    fit = _fake_fit(theta, b_true, np.ones(NI))
    pm, x, m, iu, ju, lam = DG.fitted_pieces(fit, templates, ids, NI, 4)
    ph = DG.item_success(ds.Y, ds.template_id, ids, NI)
    xc = DG.carry_covariate(templates, ids, ph, 5.0)
    col = DG.eta_columns(m["D"], lam, ids, [xc])
    m2 = DG.append_eta(m, col)
    S = twopl.learner_scores(m2, ds.Y, ds.template_id)
    H = twopl.fisher(m2, iu, ju)
    ll = lambda eta: weighted_cell_loglik_obs(m["a"] + eta * col[..., 0], iu, ju, m["rho"], pc.counts, P_FLOOR, grad=False)[0]
    h = 1e-4
    fd = (ll(h) - ll(-h)) / (2 * h)
    assert abs(S[:, pm.n].sum() - fd) < 1e-5 * max(1.0, abs(fd))
    # information identity: -d2 ll / d eta2 / N is H_eta,eta up to sampling error (data generated at eta = 0)
    hess = -(ll(h) - 2 * ll(0.0) + ll(-h)) / h ** 2 / ds.Y.shape[0]
    assert abs(hess / H[pm.n, pm.n] - 1.0) < 0.05, (hess, H[pm.n, pm.n])


def test_statistic_is_invariant_to_covariate_rescaling_and_zero_covariate_is_refused(cfg, templates, theta, ids, b_true, clean_data):
    ds, _ = clean_data
    fit = _fake_fit(theta, b_true, np.ones(NI))
    pm, x, m, iu, ju, lam = DG.fitted_pieces(fit, templates, ids, NI, 4)
    xc = DG.carry_covariate(templates, ids, DG.item_success(ds.Y, ds.template_id, ids, NI), 5.0)
    m2 = DG.append_eta(m, DG.eta_columns(m["D"], lam, ids, [xc, 3.7 * xc]))
    S = twopl.learner_scores(m2, ds.Y, ds.template_id)
    H = twopl.fisher(m2, iu, ju)
    act = list(range(pm.n))
    r1 = DG.score_stat(*DG.adjusted_scores(S, H, act, pm.n))
    r2 = DG.score_stat(*DG.adjusted_scores(S, H, act, pm.n + 1))
    assert abs(r1["stat"] - r2["stat"]) < 1e-8 * max(1.0, r1["stat"]) and abs(r1["eta_hat"] - 3.7 * r2["eta_hat"]) < 1e-8
    # probes carry x == 0 exactly and the covariate is centred within item
    prac = np.stack([t.practice for t in templates])
    assert np.all(xc[~prac] == 0.0)
    for q in range(NI):
        sel = (ids == q) & prac
        if sel.any():
            assert abs(xc[sel].mean()) < 1e-12
    # an item-success vector of all ones makes every error load zero
    with pytest.raises(ValueError):
        DG.eta_test(fit, templates, ids, ds.Y[:50], ds.template_id[:50], {"boundary_tol": 1e-6}, [5.0], phat=np.ones(NI))


@pytest.mark.slow
def test_null_statistic_is_about_chi2_1_and_alternative_is_detected(cfg, templates, theta, ids, b_true):
    fit = _fake_fit(theta, b_true, np.ones(NI))
    pm, x, m, iu, ju, lam = DG.fitted_pieces(fit, templates, ids, NI, 4)
    big = simulate_feedback(cfg, 20000, ("e5", "ph"), 81, templates, lam=None, ids=ids, theta=theta)
    xc = DG.carry_covariate(templates, ids, DG.item_success(big.Y, big.template_id, ids, NI), 5.0)
    m2 = DG.append_eta(m, DG.eta_columns(m["D"], lam, ids, [xc]))
    H = twopl.fisher(m2, iu, ju)
    act = list(range(pm.n))
    stats0, stats1 = [], []
    for r in range(40):
        d0 = simulate_feedback(cfg, 1000, ("e5", "n", r), 82, templates, lam=None, ids=ids, theta=theta)
        stats0.append(DG.score_stat(*DG.adjusted_scores(twopl.learner_scores(m2, d0.Y, d0.template_id), H, act, pm.n))["stat"])
    for r in range(8):
        d1 = simulate_feedback(cfg, 1000, ("e5", "a", r), 83, templates, lam=None, ids=ids, theta=theta, feedback={"kappa": -0.25, "tau_D": 10.0})
        stats1.append(DG.score_stat(*DG.adjusted_scores(twopl.learner_scores(m2, d1.Y, d1.template_id), H, act, pm.n))["stat"])
    assert 0.5 < np.mean(stats0) < 1.8, np.mean(stats0)
    assert np.mean(stats1) > 5 * np.mean(stats0) and np.mean(stats1) > 10, np.mean(stats1)
