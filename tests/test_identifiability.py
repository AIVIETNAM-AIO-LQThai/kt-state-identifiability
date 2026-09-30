import numpy as np
import pytest

from kt_trial.composite_likelihood import learner_scores_nat
from kt_trial.config import load_scenario
from kt_trial.identifiability import (analyse_point, deficient_templates, fisher_pairwise, observable_jacobian,
                                      point_theta)
from kt_trial.models import ParamMap
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


@pytest.fixture(scope="module")
def cfg():
    return load_scenario("S1")


@pytest.fixture(scope="module")
def ts2(cfg):
    return build_templates(cfg)[:2]


def _analyse(cfg, ts, th, **kw):
    ic = cfg["identifiability"]
    return analyse_point("t", cfg, ts, th, 0, 1, ic["weak_rel_sv"], ic["rank_rel_sv"], ic["fd_steps"],
                         ic["N_reference"], do_godambe=False)


def test_actual_design_full_rank_and_fd_stable(cfg, ts2):
    r = _analyse(cfg, ts2, point_theta(cfg, {}))
    assert r["full_numerical_rank"] and r["rel_sv_min"] > 1e-6
    for h, d in r["finite_difference_check"].items():
        assert d["max_rel_sv_diff"] < 1e-4


def test_deficient_design_is_flagged(cfg, ts2):
    r = _analyse(cfg, deficient_templates(ts2), point_theta(cfg, {}))
    assert not r["full_numerical_rank"] and r["numerical_rank"] == 16
    assert r["weak_direction_flag"]
    top = r["weak_directions"][1]["top_loadings"]                       # collinearity of sigma2_F with Sigma_M shift
    assert "sigma2_F" in top


def test_analytic_jacobian_matches_finite_difference(cfg, ts2):
    from kt_trial.identifiability import _map_values
    pm = ParamMap("B2", 4)
    x = pm.theta_to_x(point_theta(cfg, {"sigma2_F": 0.04, "tau_F": 20.0}))
    iu, ju = np.triu_indices(ts2[0].T, 1)
    _, J = observable_jacobian(pm, x, ts2, iu, ju)
    h = 1e-6
    for j in range(pm.n):
        xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
        fd = (_map_values(pm, xp, ts2, iu, ju) - _map_values(pm, xm, ts2, iu, ju)) / (2 * h)
        assert np.abs(J[:, j] - fd).max() < 1e-6


@pytest.mark.slow
def test_information_identity_sensitivity_vs_score_covariance(cfg, ts2):
    th = point_theta(cfg, {})
    pm = ParamMap("B2", 4)
    x = pm.theta_to_x(th)
    iu, ju = np.triu_indices(ts2[0].T, 1)
    H = fisher_pairwise(pm, x, ts2, iu, ju)
    assert np.allclose(H, H.T, rtol=1e-8) and np.linalg.eigvalsh(H).min() > 0
    ds = simulate(cfg, 6000, ("info",), 5, ts2, theta=th)
    S = learner_scores_nat(th, ts2, ds.Y, ds.template_id) @ pm.jacobian(x)
    # score covariance J >= H is not required, but E[score]=0 and diag(J)/diag(H) must be O(1) (J = H iff pairwise indep.)
    assert np.all(np.abs(S.mean(0) / (S.std(0) / np.sqrt(len(S)))) < 4.5)
    ratio = np.diag(S.T @ S / len(S)) / np.diag(H)
    assert np.all(ratio > 0.9)                                          # dependence between pairs inflates J over H
