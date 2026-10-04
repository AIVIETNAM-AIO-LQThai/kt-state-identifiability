"""Focused tests for Experiment 2 (transient_filtering): filters, SMC reference, information bound, generator checks, runner."""
import itertools
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import multivariate_normal, norm

from kt_trial.config import generating_theta_dict, load_scenario, load_yaml
from kt_trial.kernels import fast_kernel, slow_kernel
from kt_trial.moments import Theta, histories, latent_moments
from kt_trial.schedule import T_TOL, build_templates
from kt_trial.simulator import simulate
from transient_filtering.bound import bcrb_direct, bcrb_path, r2_from_var
from transient_filtering.filters import probit_update, run_full, run_persistent
from transient_filtering.model import prior_moments, propagate
from transient_filtering.reference import kalman_cov_path, run_smc

EXP1 = Path("results/experiment_01/confirmatory/1b1307a48a")


def _sim(cfg, templates, theta, n=600, seed=3, tpl=0):
    ds = simulate(cfg, 8 * n, ("tf",), seed, templates, keep_latent=True)
    m = ds.template_id == tpl
    return ds.Y[m].astype(float), ds.latent["F"][m], ds


# ---------------------------------------------------------------- probit moments and indicator update
def test_probit_update_matches_quadrature():
    m = np.array([[0.3, -0.2]]); P = np.array([[[0.8, 0.3], [0.3, 0.5]]]); h = np.array([1.0, 0.7]); b = 0.4
    g = np.linspace(-7, 7, 801); X, Yg = np.meshgrid(g, g, indexing="ij")
    pts = np.column_stack([X.ravel(), Yg.ravel()]); d = pts - m[0]
    pr = np.exp(-0.5 * np.einsum("ni,ij,nj->n", d, np.linalg.inv(P[0]), d))
    for y in (1, 0):
        lik = norm.cdf((2 * y - 1) * (pts @ h - b))
        w = pr * lik; w /= w.sum()
        mean = w @ pts; cov = (pts - mean).T @ ((pts - mean) * w[:, None])
        m2, P2 = m.copy(), P.copy()
        ell = m2 @ h - b; s = np.sqrt(1 + h @ P2[0] @ h)
        probit_update(m2, P2, h, ell, np.array([s]), np.array([float(y)]))
        assert np.allclose(m2[0], mean, atol=2e-4) and np.allclose(P2[0], cov, atol=2e-4), y


def test_probit_update_stable_in_the_tail():
    m = np.array([[-30.0, 0.0]]); P = np.array([[[1.0, 0.0], [0.0, 1.0]]]); h = np.array([1.0, 0.0])
    ell = m @ h; s = np.sqrt(1 + 1.0)
    lam2 = probit_update(m, P, h, ell, np.array([s]), np.array([1.0]))
    assert np.isfinite(m).all() and np.isfinite(P).all() and np.linalg.eigvalsh(P[0]).min() >= -1e-12 and 0 < lam2[0] < 1


def test_indicator_update_closed_form(templates, theta):
    tpl = templates[0]; n = 5
    Y = np.zeros((n, tpl.T)); R = 0.3
    O = np.random.default_rng(0).normal(size=(n, tpl.T))
    o = run_full(theta, tpl, Y, O=O, Rnu=R, use_answers=False)
    s2 = theta.sigma2_F
    assert np.allclose(o["mF_pre"][:, 0], s2 / (s2 + R) * O[:, 0])
    assert np.allclose(o["vF_pre"][:, 0], s2 * R / (s2 + R))
    assert np.allclose(o["mF_post"], o["mF_pre"])                       # no answers used in this arm


# ---------------------------------------------------------------- reset, OU propagation, causality, nesting
def test_session_reset_and_cross_covariance(templates, theta):
    tpl = templates[0]
    t = int(np.flatnonzero(tpl.session != np.roll(tpl.session, 1))[1])    # first position of session 1
    m = np.ones((2, 7)); P = np.tile(np.arange(49.0).reshape(7, 7), (2, 1, 1)); P = P + np.swapaxes(P, 1, 2) + 100 * np.eye(7)
    propagate(m, P, theta, tpl, t)
    assert np.all(m[:, -1] == 0) and np.allclose(P[:, -1, -1], theta.sigma2_F)
    assert np.all(P[:, -1, :-1] == 0) and np.all(P[:, :-1, -1] == 0)
    assert np.allclose(m[:, :-1], 1.0)                                    # persistent mean kept
    t2 = t + 1
    P0 = P.copy(); m0 = m.copy(); m0[:, -1] = 0.7
    propagate(m0, P, theta, tpl, t2)
    a = np.exp(-(tpl.time[t2] - tpl.time[t]) / theta.tau_F)
    assert np.allclose(m0[:, -1], 0.7 * a) and np.allclose(P[:, -1, -1], a * a * P0[:, -1, -1] + theta.sigma2_F * (1 - a * a))
    assert np.allclose(P[:, 0, -1], a * P0[:, 0, -1])


def test_causality(cfg, templates, theta):
    Y, F, ds = _sim(cfg, templates, theta, n=40)
    tpl = templates[0]; t0 = 50
    O = F + 0.5 * np.random.default_rng(1).normal(size=F.shape)
    Y2 = Y.copy(); Y2[:, t0 + 1:] = 1 - Y2[:, t0 + 1:]
    O2 = O.copy(); O2[:, t0 + 1:] += 5.0
    a, b = run_full(theta, tpl, Y, O=O, Rnu=0.2), run_full(theta, tpl, Y2, O=O2, Rnu=0.2)
    for k in ("p", "p_priorF", "mF_pre", "vF_pre"):
        assert np.array_equal(a[k][:, :t0 + 1], b[k][:, :t0 + 1]), k
    assert np.array_equal(a["mF_post"][:, :t0 + 1], b["mF_post"][:, :t0 + 1])
    pa, pb = run_persistent(theta, tpl, Y), run_persistent(theta, tpl, Y2)
    assert np.array_equal(pa["p"][:, :t0 + 1], pb["p"][:, :t0 + 1])
    ra, rb = run_smc(theta, tpl, Y[:4], 256, np.random.default_rng(2)), run_smc(theta, tpl, Y2[:4], 256, np.random.default_rng(2))
    assert np.allclose(ra["p"][:, :t0 + 1], rb["p"][:, :t0 + 1], atol=1e-12)


def test_b2_with_zero_variance_equals_b1(cfg, templates, theta):
    Y, F, _ = _sim(cfg, templates, theta, n=40)
    th0 = theta.copy(sigma2_F=0.0)
    f, p = run_full(th0, templates[0], Y), run_persistent(th0, templates[0], Y)
    assert np.allclose(f["p"], p["p"], atol=1e-12) and np.allclose(f["p_priorF"], p["p"], atol=1e-12)
    assert np.allclose(f["mF_post"], 0) and np.allclose(f["vF_post"], 0)


def test_priorF_equals_full_at_first_position(cfg, templates, theta):
    Y, F, _ = _sim(cfg, templates, theta, n=30)
    o = run_full(theta, templates[0], Y)
    assert np.allclose(o["p"][:, 0], o["p_priorF"][:, 0])


def test_first_prediction_is_exact_marginal(cfg, templates, theta):
    Y, F, _ = _sim(cfg, templates, theta, n=10)
    mu, V = latent_moments(templates[0], theta)
    assert np.allclose(run_full(theta, templates[0], Y)["p"][:, 0], norm.cdf(mu[0] / np.sqrt(V[0, 0])))


def test_keep_latent_changes_nothing(cfg, templates):
    a = simulate(cfg, 500, ("kl",), 9, templates, keep_latent=False)
    b = simulate(cfg, 500, ("kl",), 9, templates, keep_latent=True)
    assert np.array_equal(a.Y, b.Y) and np.array_equal(a.template_id, b.template_id) and a.latent is None and b.latent is not None


# ---------------------------------------------------------------- SMC reference
def test_smc_matches_orthant(cfg, templates, theta):
    tpl = templates[0]; mu, V = latent_moments(tpl, theta); k = 3
    pats = np.array(list(itertools.product([0, 1], repeat=k)))
    Y = np.zeros((len(pats), tpl.T)); Y[:, :k] = pats
    exact = []
    for y in pats:
        D = np.diag(-(2.0 * y - 1.0))                                    # W_i = -kappa_i Z_i <= 0  <=>  y_i
        exact.append(multivariate_normal(mean=D @ mu[:k], cov=D @ V[:k, :k] @ D, allow_singular=False).cdf(np.zeros(k)))
    ests = []
    for s in range(8):
        r = _smc_prefix(theta, tpl, Y, k, 40000, 100 + s)
        ests.append(np.prod(r, axis=1))
    ests = np.array(ests); exact = np.array(exact)
    se = ests.std(0, ddof=1) / np.sqrt(len(ests))
    assert np.all(np.abs(ests.mean(0) - exact) <= 4 * se + 2e-4), (ests.mean(0), exact, se)
    assert abs(exact.sum() - 1.0) < 1e-5


def _smc_prefix(theta, tpl, Y, k, npart, seed):
    out = run_smc(theta, tpl, Y, npart, np.random.default_rng(seed))
    p = out["p"][:, :k]
    return np.where(Y[:, :k] == 1, p, 1 - p)


def test_smc_matches_adf_to_first_order_and_ess_ok(cfg, templates, theta):
    Y, F, _ = _sim(cfg, templates, theta, n=20)
    r = run_smc(theta, templates[0], Y[:6], 2048, np.random.default_rng(4))
    a = run_full(theta, templates[0], Y[:6])
    assert r["ess"].min() > 100 and np.abs(r["p"] - a["p"]).mean() < 0.01
    pre, post, s2 = kalman_cov_path(theta, templates[0])
    assert np.allclose(pre[0, -1, -1], theta.sigma2_F)


# ---------------------------------------------------------------- information bound
def test_bound_recursion_matches_direct_inversion(templates, theta):
    for tpl, kw in ((templates[0], {}), (templates[5], dict(Rnu=0.3))):
        a, b = bcrb_path(theta, tpl, **kw), bcrb_direct(theta, tpl, 20, **kw)
        assert np.allclose(a["pre"][:20], b["pre"], atol=1e-10) and np.allclose(a["post"][:20], b["post"], atol=1e-10)


def test_bound_reproduces_independent_figures(templates, theta):
    s2 = theta.sigma2_F
    mean = lambda kw, k: np.mean([bcrb_path(theta, t, **kw)[k] for t in templates], 0)
    exp = {"ans": ({}, 0.1151, 0.1464), "r3": (dict(Rnu=s2 * 0.7 / 0.3), 0.5534, 0.5635), "r6": (dict(Rnu=s2 * 0.4 / 0.6), 0.7531, 0.7564)}
    for name, (kw, pre, post) in exp.items():
        assert abs(r2_from_var(mean(kw, "pre"), s2) - pre) < 6e-5 and abs(r2_from_var(mean(kw, "post"), s2) - post) < 6e-5, name
    ind = mean(dict(Rnu=s2 * 0.7 / 0.3, use_answers=False), "pre")
    assert abs(r2_from_var(ind, s2) - 0.5425) < 6e-5                      # exact Kalman filter, no answers


def test_bound_dominates_adf_and_smc_error(cfg, templates, theta):
    Y, F, _ = _sim(cfg, templates, theta, n=1200)
    a = run_full(theta, templates[0], Y)
    b = bcrb_path(theta, templates[0])
    mse_post = ((a["mF_post"] - F) ** 2).mean(0)
    assert (mse_post.mean() >= b["post"].mean() - 4 * mse_post.std() / np.sqrt(len(Y) * len(mse_post)) - 1e-4)


# ---------------------------------------------------------------- generator checks (shared-kernel independence)
def test_histories_match_naive_event_loop(cfg, templates, theta):
    for tpl in templates[:3]:
        for t in range(tpl.T):
            n, hf = 0, 0.0
            for e in range(tpl.T):
                if tpl.practice[e] and tpl.skill[e] == tpl.skill[t] and tpl.time[e] < tpl.time[t] - T_TOL:
                    n += 1; hf += np.exp(-(tpl.time[t] - tpl.time[e]) / theta.tau_R)
            hs = sum((1 - theta.phi) ** j for j in range(n))
            Hs, Hf = histories(tpl, theta)
            assert abs(Hs[t] - hs) < 1e-10 and abs(Hf[t] - hf) < 1e-10


@pytest.mark.slow
def test_pair_probabilities_match_analytic(cfg, templates, theta):
    ds = simulate(cfg, 8 * 40000, ("pairs",), 21, templates, keep_latent=False)
    g = 1; tpl = templates[g]; Y = ds.Y[ds.template_id == g]; mu, V = latent_moments(tpl, theta)
    prac = np.flatnonzero(tpl.practice)
    first = prac[tpl.session[prac] == 0]
    def pick(cond):
        for i in first:
            for j in first:
                if j > i and cond(i, j):
                    return i, j
    pairs = {"same-skill short lag": pick(lambda i, j: tpl.skill[i] == tpl.skill[j] and tpl.time[j] - tpl.time[i] < 3),
             "cross-skill same session": pick(lambda i, j: tpl.skill[i] != tpl.skill[j] and tpl.time[j] - tpl.time[i] < 3)}
    s1 = np.flatnonzero(tpl.session == 1)
    pairs["cross-session"] = (first[5], s1[3])
    pr = np.flatnonzero(~tpl.practice)
    pairs["probe-probe"] = (pr[0], pr[7])
    for name, (i, j) in pairs.items():
        sd = np.sqrt(np.diag(V)[[i, j]]); r = V[i, j] / (sd[0] * sd[1])
        p11 = multivariate_normal(mean=[0, 0], cov=[[1, r], [r, 1]]).cdf([mu[i] / sd[0], mu[j] / sd[1]])
        emp = np.mean((Y[:, i] == 1) & (Y[:, j] == 1)); se = np.sqrt(p11 * (1 - p11) / len(Y))
        assert abs(emp - p11) < 4.5 * se, (name, emp, p11)


@pytest.mark.slow
def test_s8_gain_moments_match_analytic():
    cfg8 = load_scenario("S8"); ts = build_templates(cfg8)
    ds = simulate(cfg8, 200000, ("s8",), 5, ts, keep_latent=True)
    a, r, M0 = ds.latent["alpha"], ds.latent["r"], ds.latent["M0"]
    s = np.sqrt(np.log1p(0.6 ** 2))
    assert abs(a.mean() - 0.15) < 0.002 and abs(r.mean() - 0.35) < 0.004
    assert abs(a.var() - (0.6 * 0.15) ** 2) / (0.6 * 0.15) ** 2 < 0.05 and abs(r.var() - (0.6 * 0.35) ** 2) / (0.6 * 0.35) ** 2 < 0.05
    expect = 0.5 * s / np.sqrt(np.exp(s * s) - 1)                         # Corr(lognormal gain, standardised mean M0)
    assert abs(np.corrcoef(a, M0.mean(1))[0, 1] - expect) < 0.01


# ---------------------------------------------------------------- provenance of the regeneration
@pytest.mark.skipif(not EXP1.exists(), reason="Experiment-1 results not present")
def test_regeneration_build_independent_quantities_match_saved():
    """The RNG stream, template assignment and gains regenerate exactly in any build; only the per-skill basis of the
    repeated-eigenvalue M0 draw can differ between LAPACK builds (reported by `fingerprint`, not asserted here)."""
    from transient_filtering.regenerate import exp1_stage_cfg, load_fit_result, regenerate
    s1 = exp1_stage_cfg("configs/experiment_01/stage_confirmatory.yaml")
    res = load_fit_result(str(EXP1), "S1", 300, 0)
    _, _, ds = regenerate(s1, "S1", 300, 0, "data", keep_latent=False)
    for k in ("corr_alpha_r", "corr_alpha_meanM0", "cv_alpha", "cv_r"):
        assert abs(res["data_meta"]["realised"][k] - ds.meta["realised"][k]) < 1e-12, k


# ---------------------------------------------------------------- runner
def _tiny_cfg(tmp_path):
    cfg = load_yaml("configs/experiment_02/stage_pilot.yaml")
    cfg["track"]["datasets"] = [{"scenarios": ["S1"], "N_list": [300], "rep_range": [0, 1]}]
    cfg["heldout_N"] = 40
    cfg["ref"].update(rep_range=[0, 1], per_template=1, n_seeds=3, n_particles=256, doubling_factor=2, n_seeds_b1=2)
    import yaml
    p = tmp_path / "tiny.yaml"; p.write_text(yaml.safe_dump(cfg)); return p


@pytest.mark.skipif(not EXP1.exists(), reason="Experiment-1 results not present")
def test_runner_dry_run_resume_refusal_and_summary(tmp_path):
    from transient_filtering import runner
    cfgp = _tiny_cfg(tmp_path); root = tmp_path / "res"; msgs = []
    assert runner.run_stage(cfgp, results_root=str(root), dry_run=True, out=msgs.append) == 0 and not root.exists()
    assert runner.run_stage(cfgp, results_root=str(root), workers=1, out=msgs.append) == 0
    rd = next((root / "pilot").iterdir())
    assert len(list((rd / "jobs").glob("*.json"))) == 3 and not list((rd / "jobs").glob("*.tmp"))
    msgs.clear()
    assert runner.run_stage(cfgp, results_root=str(root), workers=1, out=msgs.append) == 0
    assert any("0 jobs to run" in m for m in msgs)                        # resume: nothing re-run
    import json
    man = json.loads((rd / "manifest.json").read_text()); man["code_hash"] = "0" * 64
    (rd / "manifest.json").write_text(json.dumps(man))
    assert runner.run_stage(cfgp, results_root=str(root), workers=1, out=msgs.append) == 3   # refuses on mismatch
    from transient_filtering.summarize import summarize
    S = summarize(str(rd))
    assert S["accounting"]["errors"] == 0 and "S1|N=300" in S["cells"] and S["reference"]["n_learners"] == 8
    assert (rd / "summary.md").exists()


def test_confirmatory_requires_frozen_flag_and_sha(tmp_path):
    from transient_filtering import runner
    import yaml
    cfg = load_yaml("configs/experiment_02/stage_pilot.yaml"); cfg["stage"] = "confirmatory"
    p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, out=lambda m: None) == 2
    cfg["frozen"] = True; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, frozen_sha256="bad", out=lambda m: None) == 2


def test_code_hash_is_line_ending_invariant(tmp_path, monkeypatch):
    from transient_filtering import runner
    h = runner.code_hash()
    assert len(h) == 64 and h == runner.code_hash()
