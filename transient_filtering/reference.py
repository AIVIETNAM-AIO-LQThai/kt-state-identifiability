"""High-accuracy causal reference: Rao-Blackwellised, fully adapted SMC over the latent utilities Z_t.

Given the latent utilities Z_{1:t} the state x is linear-Gaussian, so for each particle the posterior of x is a Kalman filter
whose COVARIANCE is identical for all particles (and for all learners of a template); only the means differ. Each particle
draws Z_t from its exact predictive N(h'm - b, 1 + h'Ph) truncated to the observed sign (optimal proposal); the incremental
weight is that particle's predictive probability of the observed answer. E[F_t | y_<=t] and P(y_t = 1 | y_<t) are weighted
averages of exact conditional quantities. Resampling (systematic) happens when ESS < thresh * n_particles.
This is a finite-N Monte Carlo reference, NOT an exact posterior: its error is assessed by the gates in the protocol (R1).
"""
from __future__ import annotations

import numpy as np
from scipy.special import log_ndtr, ndtr, ndtri_exp

from kt_trial.moments import Theta
from kt_trial.schedule import Template

from .model import prior_moments, propagate, rows


def kalman_cov_path(th: Theta, tpl: Template):
    """Deterministic covariance path of the latent-utility Kalman filter (unit observation noise): pre/post (T,d,d), s2_t."""
    d = th.Sigma_M.shape[0] + 3
    h = rows(tpl, th)
    m0, P0 = prior_moments(th)
    m = m0[None, :].copy()
    P = P0[None].copy()
    pre = np.zeros((tpl.T, d, d)); post = np.zeros((tpl.T, d, d)); s2 = np.zeros(tpl.T)
    for t in range(tpl.T):
        propagate(m, P, th, tpl, t)
        pre[t] = P[0]
        Ph = P[0] @ h[t]
        s2[t] = 1.0 + h[t] @ Ph
        P[0] = P[0] - np.outer(Ph, Ph) / s2[t]
        P[0] = 0.5 * (P[0] + P[0].T)
        post[t] = P[0]
    return pre, post, s2


def _systematic(w: np.ndarray, rng) -> np.ndarray:
    """w (n, Np) normalised -> ancestor indices (n, Np) by systematic resampling per learner."""
    n, Np = w.shape
    c = np.cumsum(w, axis=1)
    c[:, -1] = 1.0
    u = (rng.random((n, 1)) + np.arange(Np)[None, :]) / Np
    return np.minimum((u[:, :, None] > c[:, None, :]).sum(2) if Np <= 64 else
                      np.stack([np.searchsorted(c[i], u[i]) for i in range(n)]), Np - 1)


def run_smc(th: Theta, tpl: Template, Y: np.ndarray, n_particles: int, rng, thresh: float = 0.5) -> dict:
    n, T = Y.shape
    d = th.Sigma_M.shape[0] + 3
    h = rows(tpl, th)
    pre, post, s2 = kalman_cov_path(th, tpl)
    m0, _ = prior_moments(th)
    m = np.tile(m0, (n, n_particles, 1))                                 # (n, Np, d) particle means
    logw = np.full((n, n_particles), -np.log(n_particles))
    out = {k: np.zeros((n, T)) for k in ("p", "mF_pre", "vF_pre", "mF_post", "vF_post", "ess")}
    out["mp_post"] = np.zeros((n, T, d - 1))
    n_resample = 0
    for t in range(T):
        # propagate particle means (covariance path is precomputed)
        if t == 0 or tpl.session[t] != tpl.session[t - 1]:
            m[:, :, -1] = 0.0
        else:
            m[:, :, -1] *= np.exp(-(tpl.time[t] - tpl.time[t - 1]) / th.tau_F)
        w = np.exp(logw - logw.max(1, keepdims=True)); w /= w.sum(1, keepdims=True)
        ell = m @ h[t] - tpl.b[t]                                        # (n, Np)
        s = np.sqrt(s2[t])
        out["p"][:, t] = (w * ndtr(ell / s)).sum(1)
        mF = (w * m[:, :, -1]).sum(1)
        out["mF_pre"][:, t] = mF
        out["vF_pre"][:, t] = pre[t, -1, -1] + (w * (m[:, :, -1] - mF[:, None]) ** 2).sum(1)
        kappa = (2.0 * Y[:, t] - 1.0)[:, None]
        c = kappa * ell / s
        logU = np.log(rng.random(ell.shape))
        v = -ndtri_exp(logU + log_ndtr(c))                               # N(0,1) truncated to v > -c
        innov = s * kappa * v                                            # Z - ell
        m += (innov / s2[t])[:, :, None] * (pre[t] @ h[t])[None, None, :]
        logw = logw + log_ndtr(c)
        logw -= np.log(np.exp(logw - logw.max(1, keepdims=True)).sum(1, keepdims=True)) + logw.max(1, keepdims=True)
        w = np.exp(logw)
        mF = (w * m[:, :, -1]).sum(1)
        out["mF_post"][:, t] = mF
        out["vF_post"][:, t] = post[t, -1, -1] + (w * (m[:, :, -1] - mF[:, None]) ** 2).sum(1)
        out["mp_post"][:, t] = np.einsum("nj,njd->nd", w, m[:, :, :-1])
        ess = 1.0 / (w ** 2).sum(1)
        out["ess"][:, t] = ess
        need = ess < thresh * n_particles
        if need.any():
            idx = np.flatnonzero(need)
            anc = _systematic(w[idx], rng)
            m[idx] = np.take_along_axis(m[idx], anc[:, :, None], axis=1)
            logw[idx] = -np.log(n_particles)
            n_resample += len(idx)
    out["n_resample"] = n_resample
    return out
