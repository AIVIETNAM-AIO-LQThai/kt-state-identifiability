"""All-pairs, equal-weight pairwise composite likelihood built from per-template pair-count tables.

For template g and observation pair (t,t'), the standardised endpoints are
    a_t = mu_t / sqrt(D_t),  rho_tt' = C_tt' / sqrt(D_t D_t'),
and the four response-cell probabilities follow from Phi2(a_t, a_t'; rho_tt') by differencing.
The data enter only through the counts (G, P, 4) of cells (11,10,01,00), so an objective evaluation
costs the same for any N. Derivatives are with respect to the natural parameter vector (moments.py).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .bvn import cell_probs_and_grads, weighted_cell_loglik
from .kernels import dfast_dtauR, dslow_dphi, fast_kernel, slow_kernel
from .moments import N_SCALAR, Theta, latent_moments, moment_jacobians, ou_kernel, tril_idx
from .schedule import Template

P_FLOOR = 1e-300


@dataclass
class PairCounts:
    counts: np.ndarray        # (G, P, 4) float
    n_learners: np.ndarray    # (G,)
    iu: np.ndarray
    ju: np.ndarray

    @property
    def N(self) -> int:
        return int(self.n_learners.sum())


def cell_index(yi, yj):
    """Cell (11,10,01,00) -> 0..3."""
    return (1 - yi) * 2 + (1 - yj)


def pair_counts(Y: np.ndarray, tid: np.ndarray, G: int) -> PairCounts:
    T = Y.shape[1]
    iu, ju = np.triu_indices(T, 1)
    counts = np.zeros((G, len(iu), 4))
    nl = np.zeros(G, int)
    for g in range(G):
        Yg = Y[tid == g].astype(float)
        nl[g] = len(Yg)
        if not len(Yg):
            continue
        N1 = Yg.T @ Yg; N10 = Yg.T @ (1 - Yg); N01 = (1 - Yg).T @ Yg; N00 = (1 - Yg).T @ (1 - Yg)
        counts[g] = np.stack([N1[iu, ju], N10[iu, ju], N01[iu, ju], N00[iu, ju]], -1)
    return PairCounts(counts, nl, iu, ju)


@dataclass
class PairJac:
    """Standardised endpoint quantities for one theta, all templates (G templates, T obs, P pairs)."""
    a: np.ndarray        # (G,T)
    da: np.ndarray       # (G,T,Q)   d a / d nat
    rho: np.ndarray      # (G,P)
    drho: np.ndarray     # (G,P,Q)
    D: np.ndarray        # (G,T)


def pair_quantities(theta: Theta, templates: list[Template], iu, ju, need_jac=True) -> PairJac:
    G, T = len(templates), templates[0].T
    Q = len(theta.to_nat())
    a = np.empty((G, T)); D = np.empty((G, T)); rho = np.empty((G, len(iu)))
    da = np.empty((G, T, Q)) if need_jac else None
    drho = np.empty((G, len(iu), Q)) if need_jac else None
    for g, tpl in enumerate(templates):
        mu, V, dmu, dV = moment_jacobians(tpl, theta)
        d = np.diag(V); sd = np.sqrt(d)
        a[g] = mu / sd; D[g] = d
        rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
        if need_jac:
            dD = np.einsum("ttq->tq", dV)
            da[g] = dmu / sd[:, None] - (mu / (2.0 * d * sd))[:, None] * dD
            drho[g] = (dV[iu, ju, :] / (sd[iu] * sd[ju])[:, None]
                       - 0.5 * rho[g][:, None] * (dD[iu] / d[iu][:, None] + dD[ju] / d[ju][:, None]))
    return PairJac(a, da, rho, drho, D)


def _adjoint_gradient(theta: Theta, tpl: Template, mu, V, wa_obs, w_rho, iu, ju) -> np.ndarray:
    """Reverse-mode gradient w.r.t. nat of  sum_t wa_obs[t] a_t + sum_pairs w_rho rho, for one template."""
    K = theta.Sigma_M.shape[0]
    T = tpl.T
    d = np.diag(V); sd = np.sqrt(d)
    rho = V[iu, ju] / (sd[iu] * sd[ju])
    # adjoints of (mu, V)
    g_mu = wa_obs / sd
    g_D = -wa_obs * mu / (2.0 * d * sd)
    g_D = g_D - np.bincount(iu, weights=w_rho * rho, minlength=T) / (2.0 * d) \
                - np.bincount(ju, weights=w_rho * rho, minlength=T) / (2.0 * d)
    G = np.zeros((T, T))
    G[iu, ju] = 0.5 * w_rho / (sd[iu] * sd[ju])
    G = G + G.T
    G[np.diag_indices(T)] = g_D
    Hs = slow_kernel(tpl.n_prior, theta.phi); Hf = fast_kernel(tpl.lag, tpl.expo, theta.tau_R)
    dHs = dslow_dphi(tpl.n_prior, theta.phi); dHf = dfast_dtauR(tpl.lag, tpl.expo, theta.tau_R)
    Kou = ou_kernel(tpl, theta.tau_F)
    GHs, GHf = G @ Hs, G @ Hf
    g = np.zeros(N_SCALAR + K * (K + 1) // 2)
    g[0] = g_mu @ Hs
    g[1] = theta.alpha_bar * (g_mu @ dHs) + 2.0 * theta.sigma2_alpha * (GHs @ dHs)
    g[2] = Hs @ GHs
    g[3] = g_mu @ Hf
    g[4] = theta.r_bar * (g_mu @ dHf) + 2.0 * theta.sigma2_r * (GHf @ dHf)
    g[5] = Hf @ GHf
    GK = G * Kou
    g[6] = GK.sum()
    g[7] = theta.sigma2_F * (GK * tpl.absdt).sum() / theta.tau_F ** 2
    S = np.zeros((T, K)); S[np.arange(T), tpl.skill] = 1.0
    GS = S.T @ G @ S
    r, c = tril_idx(K)
    g[N_SCALAR:] = np.where(r == c, GS[r, c], GS[r, c] + GS[c, r])
    return g


def composite_loglik(theta: Theta, templates: list[Template], pc: PairCounts, grad=True):
    """Return (loglik, grad_nat or None, diagnostics). Cells with p below P_FLOOR are floored and counted."""
    G, T = len(templates), templates[0].T
    iu, ju = pc.iu, pc.ju
    a = np.empty((G, T)); rho = np.empty((G, len(iu))); moms = []
    for g, tpl in enumerate(templates):
        mu, V = latent_moments(tpl, theta)
        sd = np.sqrt(np.diag(V))
        a[g] = mu / sd
        rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
        moms.append((mu, V))
    ll, w, nfl = weighted_cell_loglik(a[:, iu], a[:, ju], rho, pc.counts, P_FLOOR, grad=grad)
    diag = {"n_floored_cells": nfl, "finite": bool(np.isfinite(ll)), "max_abs_rho": float(np.abs(rho).max())}
    if not grad:
        return ll, None, diag
    g_nat = np.zeros(N_SCALAR + theta.Sigma_M.shape[0] * (theta.Sigma_M.shape[0] + 1) // 2)
    for g, tpl in enumerate(templates):
        wa = np.bincount(iu, weights=w[g, :, 0], minlength=T) + np.bincount(ju, weights=w[g, :, 1], minlength=T)
        g_nat += _adjoint_gradient(theta, tpl, moms[g][0], moms[g][1], wa, w[g, :, 2], iu, ju)
    return ll, g_nat, diag


def learner_scores_nat(theta: Theta, templates: list[Template], Y: np.ndarray, tid: np.ndarray, chunk=400) -> np.ndarray:
    """Per-learner composite scores (N, Q) w.r.t. the natural parameter vector."""
    import scipy.sparse as sp
    T = Y.shape[1]
    iu, ju = np.triu_indices(T, 1)
    P = len(iu)
    pj = pair_quantities(theta, templates, iu, ju)
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)       # (G,P,4), (G,P,4,3)
    dlogp = dp / np.maximum(p, P_FLOOR)[..., None]
    Iu = sp.csr_matrix((np.ones(P), (np.arange(P), iu)), shape=(P, T))
    Ju = sp.csr_matrix((np.ones(P), (np.arange(P), ju)), shape=(P, T))
    S = np.zeros((Y.shape[0], pj.da.shape[2]))
    ar = np.arange(P)[None, :]
    for g in range(len(templates)):
        idx = np.flatnonzero(tid == g)
        for s in range(0, len(idx), chunk):
            ii = idx[s:s + chunk]
            y = Y[ii].astype(np.int64)
            cell = cell_index(y[:, iu], y[:, ju])                        # (n,P)
            w = dlogp[g][ar, cell]                                       # (n,P,3)
            wobs = (Iu.T @ w[:, :, 0].T).T + (Ju.T @ w[:, :, 1].T).T     # (n,T)
            S[ii] = wobs @ pj.da[g] + w[:, :, 2] @ pj.drho[g]
    return S
