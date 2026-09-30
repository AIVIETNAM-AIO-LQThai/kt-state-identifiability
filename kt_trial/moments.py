"""Analytic latent-response moments (mu, V) of Z given a fixed schedule template, and their Jacobians.

Z_t = -b_t + M0[k_t] + alpha H^s_t + r H^f_t + F_t + eps_t, eps ~ N(0,1).
    mu_t   = -b_t + alpha_bar H^s_t + r_bar H^f_t
    V_tt   = D_t = 1 + Sigma_M[k_t,k_t] + s2_alpha (H^s_t)^2 + s2_r (H^f_t)^2 + s2_F
    V_tt'  = C_tt' = Sigma_M[k_t,k_t'] + s2_alpha H^s_t H^s_t' + s2_r H^f_t H^f_t'
                     + 1{s_t = s_t'} s2_F exp(-|T_t - T_t'| / tau_F)
Natural parameter vector ("nat"): the eight scalars in SCALAR_NAMES followed by the K(K+1)/2
lower-triangular entries of Sigma_M (row-major tril order).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .kernels import dfast_dtauR, dslow_dphi, fast_kernel, slow_kernel
from .schedule import Template

SCALAR_NAMES = ["alpha_bar", "phi", "sigma2_alpha", "r_bar", "tau_R", "sigma2_r", "sigma2_F", "tau_F"]
N_SCALAR = len(SCALAR_NAMES)


def tril_idx(K):
    return np.tril_indices(K)


def nat_names(K):
    r, c = tril_idx(K)
    return SCALAR_NAMES + [f"SigmaM[{i},{j}]" for i, j in zip(r, c)]


@dataclass
class Theta:
    alpha_bar: float
    phi: float
    sigma2_alpha: float
    r_bar: float
    tau_R: float
    sigma2_r: float
    sigma2_F: float
    tau_F: float
    Sigma_M: np.ndarray = field(repr=False)

    def to_nat(self) -> np.ndarray:
        r, c = tril_idx(self.Sigma_M.shape[0])
        return np.concatenate([[getattr(self, n) for n in SCALAR_NAMES], self.Sigma_M[r, c]])

    @staticmethod
    def from_nat(v, K) -> "Theta":
        v = np.asarray(v, float)
        S = np.zeros((K, K))
        r, c = tril_idx(K)
        S[r, c] = v[N_SCALAR:]
        S = S + S.T - np.diag(np.diag(S))
        return Theta(*[float(x) for x in v[:N_SCALAR]], S)

    @staticmethod
    def from_dict(d) -> "Theta":
        return Theta(**{k: (np.array(d[k], float) if k == "Sigma_M" else float(d[k]))
                        for k in SCALAR_NAMES + ["Sigma_M"]})

    def to_dict(self) -> dict:
        return {**{n: float(getattr(self, n)) for n in SCALAR_NAMES}, "Sigma_M": self.Sigma_M.tolist()}

    def copy(self, **kw) -> "Theta":
        d = {**{n: getattr(self, n) for n in SCALAR_NAMES}, "Sigma_M": self.Sigma_M.copy()}
        d.update(kw)
        return Theta(**d)


def histories(tpl: Template, th: Theta):
    return (slow_kernel(tpl.n_prior, th.phi), fast_kernel(tpl.lag, tpl.expo, th.tau_R))


def ou_kernel(tpl: Template, tau_F: float) -> np.ndarray:
    return np.where(tpl.same_session, np.exp(-tpl.absdt / tau_F), 0.0)


def latent_moments(tpl: Template, th: Theta):
    """Return (mu, V) with V the full latent covariance including the unit residual variance."""
    Hs, Hf = histories(tpl, th)
    mu = -tpl.b + th.alpha_bar * Hs + th.r_bar * Hf
    V = (th.Sigma_M[np.ix_(tpl.skill, tpl.skill)] + th.sigma2_alpha * np.outer(Hs, Hs)
         + th.sigma2_r * np.outer(Hf, Hf) + th.sigma2_F * ou_kernel(tpl, th.tau_F))
    V = V + np.eye(tpl.T)
    return mu, V


def moment_jacobians(tpl: Template, th: Theta):
    """(mu, V, dmu[T,P], dV[T,T,P]) with derivatives w.r.t. the natural parameter vector."""
    K = th.Sigma_M.shape[0]
    P = N_SCALAR + K * (K + 1) // 2
    T = tpl.T
    Hs, Hf = histories(tpl, th)
    dHs = dslow_dphi(tpl.n_prior, th.phi)
    dHf = dfast_dtauR(tpl.lag, tpl.expo, th.tau_R)
    Kou = ou_kernel(tpl, th.tau_F)
    mu, V = latent_moments(tpl, th)
    dmu = np.zeros((T, P)); dV = np.zeros((T, T, P))
    dmu[:, 0] = Hs                                                   # alpha_bar
    dmu[:, 1] = th.alpha_bar * dHs                                   # phi
    dV[:, :, 1] = th.sigma2_alpha * (np.outer(dHs, Hs) + np.outer(Hs, dHs))
    dV[:, :, 2] = np.outer(Hs, Hs)                                   # sigma2_alpha
    dmu[:, 3] = Hf                                                   # r_bar
    dmu[:, 4] = th.r_bar * dHf                                       # tau_R
    dV[:, :, 4] = th.sigma2_r * (np.outer(dHf, Hf) + np.outer(Hf, dHf))
    dV[:, :, 5] = np.outer(Hf, Hf)                                   # sigma2_r
    dV[:, :, 6] = Kou                                                # sigma2_F
    dV[:, :, 7] = th.sigma2_F * Kou * tpl.absdt / th.tau_F ** 2      # tau_F
    r, c = tril_idx(K)
    for j, (k, l) in enumerate(zip(r, c)):
        m = (tpl.skill[:, None] == k) & (tpl.skill[None, :] == l)
        if k != l:
            m = m | ((tpl.skill[:, None] == l) & (tpl.skill[None, :] == k))
        dV[:, :, N_SCALAR + j] = m
    return mu, V, dmu, dV
