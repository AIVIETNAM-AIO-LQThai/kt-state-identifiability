"""Bayesian (posterior) Cramer-Rao bound for the transient state F under the Experiment-1 generating process.

Van Trees bound with the exact Gaussian prior of the innovation parameters. Because every observation adds rank-one
information E[I(l_t)] h h' with I(l) = phi(l)^2 / (Phi(l) Phi(-l)) and l_t ~ N(h_P' mu_P - b_t, h_P' Sigma_P h_P + s2_F)
(the TRUE prior marginal, by Gauss-Hermite quadrature), the bound equals the covariance of a Kalman filter for a surrogate
linear measurement with noise variance 1 / E[I]. Covariance form: no inverse of the singular process covariance appears
(static coordinates and session resets are exact). An ideal indicator O = F + nu adds an exact linear update before the answer.
The bound is valid for ANY estimator of F, but only under this Gaussian prior with known population parameters.
"""
from __future__ import annotations

import numpy as np
from scipy.special import log_ndtr

from kt_trial.moments import Theta
from kt_trial.schedule import Template

from .model import prior_moments, propagate, rows

_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(96)
_GH_W = _GH_W / _GH_W.sum()


def probit_info(ell):
    """Fisher information of Y = 1{ell + eps > 0} about ell."""
    logphi = -0.5 * ell ** 2 - 0.5 * np.log(2 * np.pi)
    return np.exp(2.0 * logphi - log_ndtr(ell) - log_ndtr(-ell))


def mean_info(mu, var):
    """E[I(ell)], ell ~ N(mu, var)."""
    return float((_GH_W * probit_info(mu + np.sqrt(var) * _GH_X)).sum())


def ibar_path(th: Theta, tpl: Template) -> np.ndarray:
    h = rows(tpl, th)
    m0, P0 = prior_moments(th)
    mu = h @ m0 - tpl.b
    var = np.einsum("ti,ij,tj->t", h, P0, h)
    return np.array([mean_info(mu[t], var[t]) for t in range(tpl.T)])


def bcrb_path(th: Theta, tpl: Template, Rnu: float | None = None, use_answers: bool = True) -> dict:
    """Covariance recursion. Returns pre/post bound variance of F_t, (T,), and Ibar_t."""
    d = th.Sigma_M.shape[0] + 3
    h = rows(tpl, th)
    ib = ibar_path(th, tpl)
    m0, P0 = prior_moments(th)
    m = m0[None, :].copy(); P = P0[None].copy()
    pre = np.zeros(tpl.T); post = np.zeros(tpl.T)
    for t in range(tpl.T):
        propagate(m, P, th, tpl, t)
        Pt = P[0]
        if Rnu is not None:
            Pe = Pt[:, -1].copy()
            Pt = Pt - np.outer(Pe, Pe) / (Pt[-1, -1] + Rnu)
        pre[t] = Pt[-1, -1]
        if use_answers:
            Ph = Pt @ h[t]
            Pt = Pt - np.outer(Ph, Ph) / (h[t] @ Ph + 1.0 / ib[t])
        Pt = 0.5 * (Pt + Pt.T)
        P[0] = Pt
        post[t] = Pt[-1, -1]
    return {"pre": pre, "post": post, "ibar": ib}


def bcrb_direct(th: Theta, tpl: Template, t_max: int, Rnu: float | None = None) -> dict:
    """Independent cross-check on the first t_max positions: joint information matrix of (p, F_1..F_t) with the
    nonsingular joint prior (OU stationary covariance within sessions, zero across sessions), inverted directly."""
    K = th.Sigma_M.shape[0]
    h = rows(tpl, th)
    ib = ibar_path(th, tpl)
    _, P0 = prior_moments(th)
    Pp = P0[:-1, :-1]
    pre = np.zeros(t_max); post = np.zeros(t_max)
    for t in range(t_max):
        nF = t + 1
        KF = th.sigma2_F * np.where(tpl.session[:nF, None] == tpl.session[None, :nF],
                                    np.exp(-np.abs(tpl.time[:nF, None] - tpl.time[None, :nF]) / th.tau_F), 0.0)
        Sig = np.zeros((K + 2 + nF, K + 2 + nF))
        Sig[:K + 2, :K + 2] = Pp; Sig[K + 2:, K + 2:] = KF
        J = np.linalg.inv(Sig)
        for s in range(nF):
            g = np.zeros(K + 2 + nF); g[:K + 2] = h[s, :-1]; g[K + 2 + s] = 1.0
            if Rnu is not None:
                e = np.zeros(K + 2 + nF); e[K + 2 + s] = 1.0
                J = J + np.outer(e, e) / Rnu
            if s < t:
                J = J + ib[s] * np.outer(g, g)
        pre[t] = np.linalg.inv(J)[-1, -1]
        g = np.zeros(K + 2 + nF); g[:K + 2] = h[t, :-1]; g[-1] = 1.0
        J = J + ib[t] * np.outer(g, g)
        post[t] = np.linalg.inv(J)[-1, -1]
    return {"pre": pre, "post": post}


def r2_from_var(var: np.ndarray, s2F: float) -> float:
    """Average R^2 = 1 - mean(bound)/sigma_F^2 over the supplied positions."""
    return float(1.0 - np.mean(var) / s2F)
