"""Causal Gaussian assumed-density filters (ADF) for the Experiment-1 probit model, vectorised over learners.

Timing at every position t (strictly causal):
  1. propagate / reset the state (OU within a session, reset at a session start);
  2. take the auxiliary indicator O_t if the arm has one (available BEFORE the answer);
  3. record the PRE-answer transient estimate and the predictive probability P(Y_t = 1 | past, indicators <= t);
  4. observe the answer; ADF update (analytic one-step probit moments); record the POST-answer estimate.
No future answers, future indicators, smoothing, or latent truth is ever used by a prediction. The oracle-F arm is the
only arm that receives the true F_t, and is labelled as such.
"""
from __future__ import annotations

import numpy as np
from scipy.special import log_ndtr, ndtr

from kt_trial.moments import Theta
from kt_trial.schedule import Template

from .model import prior_moments, propagate, rows

_LOG_SQRT_2PI = 0.5 * np.log(2.0 * np.pi)


def probit_update(m, P, h, ell, s, y):
    """Exact one-step probit moments for a Gaussian prior (in place). ell = h'm - b, s = sqrt(v + h'Ph).
    Returns lambda(lambda+u) (for diagnostics). Stable tail evaluation through log-ndtr."""
    kappa = 2.0 * y - 1.0
    u = kappa * ell / s
    lam = np.exp(-0.5 * u * u - _LOG_SQRT_2PI - log_ndtr(u))
    Ph = np.einsum("nij,j->ni", P, h)
    m += (kappa * lam / s)[:, None] * Ph
    P -= (lam * (lam + u) / (s * s))[:, None, None] * Ph[:, :, None] * Ph[:, None, :]
    P += np.swapaxes(P, 1, 2)
    P *= 0.5
    return lam * (lam + u)


def run_full(th: Theta, tpl: Template, Y: np.ndarray, *, O: np.ndarray | None = None, Rnu: float | None = None,
             use_answers: bool = True) -> dict:
    """7-state ADF (persistent + F). With indicators O (n,T) the indicator is assimilated before each answer.
    With use_answers=False only the indicators are used (exact Kalman filter for F; requires O)."""
    n, T = Y.shape
    d = th.Sigma_M.shape[0] + 3
    h = rows(tpl, th)
    m0, P0 = prior_moments(th)
    m = np.tile(m0, (n, 1))
    P = np.tile(P0, (n, 1, 1))
    out = {k: np.zeros((n, T)) for k in ("p", "p_priorF", "mF_pre", "vF_pre", "mF_post", "vF_post")}
    out["mp_post"] = np.zeros((n, T, d - 1))
    out["vp_post"] = np.zeros((n, T, d - 1))
    s2F = th.sigma2_F
    for t in range(T):
        propagate(m, P, th, tpl, t)
        if O is not None:
            S = P[:, -1, -1] + Rnu
            K = P[:, :, -1] / S[:, None]
            m += K * (O[:, t] - m[:, -1])[:, None]
            P -= K[:, :, None] * P[:, -1, :][:, None, :]
            P += np.swapaxes(P, 1, 2); P *= 0.5
        ht = h[t]
        Ph = np.einsum("nij,j->ni", P, ht)
        ell = m @ ht - tpl.b[t]
        s = np.sqrt(1.0 + ht @ Ph.T)
        out["p"][:, t] = ndtr(ell / s)
        hP = ht[:-1]
        ell_p = m[:, :-1] @ hP - tpl.b[t]
        vP = np.einsum("i,nij,j->n", hP, P[:, :-1, :-1], hP)
        out["p_priorF"][:, t] = ndtr(ell_p / np.sqrt(1.0 + vP + s2F))
        out["mF_pre"][:, t] = m[:, -1]
        out["vF_pre"][:, t] = P[:, -1, -1]
        if use_answers:
            probit_update(m, P, ht, ell, s, Y[:, t].astype(float))
        out["mF_post"][:, t] = m[:, -1]
        out["vF_post"][:, t] = P[:, -1, -1]
        out["mp_post"][:, t] = m[:, :-1]
        out["vp_post"][:, t] = np.diagonal(P, axis1=1, axis2=2)[:, :-1]
    return out


def run_persistent(th: Theta, tpl: Template, Y: np.ndarray, *, extra_var: float = 0.0,
                   F_known: np.ndarray | None = None) -> dict:
    """6-state ADF without a transient coordinate. extra_var adds to the unit noise (B2-white: sigma2_F). F_known is the
    ORACLE arm: the true F_t (n,T) is added to the linear predictor before the answer."""
    n, T = Y.shape
    d = th.Sigma_M.shape[0] + 2
    h = rows(tpl, th)[:, :-1]
    m0, P0 = prior_moments(th)
    m = np.tile(m0[:-1], (n, 1))
    P = np.tile(P0[:-1, :-1], (n, 1, 1))
    v = 1.0 + extra_var
    p = np.zeros((n, T))
    mp_post = np.zeros((n, T, d)); vp_post = np.zeros((n, T, d))
    for t in range(T):
        ht = h[t]
        Ph = np.einsum("nij,j->ni", P, ht)
        ell = m @ ht - tpl.b[t] + (0.0 if F_known is None else F_known[:, t])
        s = np.sqrt(v + ht @ Ph.T)
        p[:, t] = ndtr(ell / s)
        probit_update(m, P, ht, ell, s, Y[:, t].astype(float))
        mp_post[:, t] = m
        vp_post[:, t] = np.diagonal(P, axis1=1, axis2=2)
    return {"p": p, "mp_post": mp_post, "vp_post": vp_post}
