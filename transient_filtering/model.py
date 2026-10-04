"""State-space form of the Experiment-1 probit model shared by every filter, the SMC reference and the bound.

State x = (M0[0..K-1], alpha, r, F) with K = 4 (persistent coordinates p = x[:K+2], transient F = x[K+2]).
Observation row h_t = (e_{k_t}, H^s_t, H^f_t, 1) and Z_t = h_t' x - b_t + eps_t, eps ~ N(0, 1); Y_t = 1{Z_t > 0}.
Within a session F follows the exact OU transition; at a session start F is reset to N(0, sigma2_F) independent of p.
"""
from __future__ import annotations

import numpy as np

from kt_trial.moments import Theta, histories
from kt_trial.schedule import Template


def rows(tpl: Template, th: Theta) -> np.ndarray:
    """(T, K+3) observation rows h_t."""
    K = th.Sigma_M.shape[0]
    Hs, Hf = histories(tpl, th)
    h = np.zeros((tpl.T, K + 3))
    h[np.arange(tpl.T), tpl.skill] = 1.0
    h[:, K] = Hs
    h[:, K + 1] = Hf
    h[:, K + 2] = 1.0
    return h


def prior_moments(th: Theta):
    """Population prior of x at any time: mean (K+3,), covariance blockdiag(Sigma_M, s2_alpha, s2_r, s2_F)."""
    K = th.Sigma_M.shape[0]
    m = np.zeros(K + 3)
    m[K], m[K + 1] = th.alpha_bar, th.r_bar
    P = np.zeros((K + 3, K + 3))
    P[:K, :K] = th.Sigma_M
    P[K, K], P[K + 1, K + 1], P[K + 2, K + 2] = th.sigma2_alpha, th.sigma2_r, th.sigma2_F
    return m, P


def new_session(tpl: Template, t: int) -> bool:
    return t == 0 or tpl.session[t] != tpl.session[t - 1]


def ou_a(tpl: Template, th: Theta, t: int) -> float:
    return float(np.exp(-(tpl.time[t] - tpl.time[t - 1]) / th.tau_F))


def propagate(m, P, th: Theta, tpl: Template, t: int):
    """In-place propagation/reset of mean (n,d) and covariance (n,d,d) to time t (F is the last coordinate)."""
    s2F = th.sigma2_F
    if new_session(tpl, t):
        m[:, -1] = 0.0
        P[:, -1, :] = 0.0
        P[:, :, -1] = 0.0
        P[:, -1, -1] = s2F
    else:
        a = ou_a(tpl, th, t)
        m[:, -1] *= a
        P[:, -1, :] *= a
        P[:, :, -1] *= a
        P[:, -1, -1] += s2F * (1.0 - a * a)
