"""Observable map of the 2PL-type model and its derivatives.

    Z_t = -b_q + lambda_q * (M0[k] + alpha H^s + r H^f + F_t) + eps_t,   eps ~ N(0, 1),   q = item of observation t.

With mu0 and L the Experiment-1 latent mean and covariance WITHOUT the unit residual (kt_trial.moments evaluated at b = 0, V0 = L + I):
    mu_t = -b_q + lambda_q mu0_t,   V_tt' = lambda_q lambda_q' L_tt' + delta_tt',   D_t = lambda_q^2 L_tt + 1,
    a_t = mu_t / sqrt(D_t),   rho_tt' = V_tt' / sqrt(D_t D_t').
Scale invariance: (lambda c, locations/c, variances/c^2) leaves a and rho unchanged, so identification fixes the geometric mean of
lambda to 1 (sum of log lambda = 0): 47 free coordinates w, with log lambda = P w for an orthonormal sum-zero basis P (48 x 47).
Coordinates of the full model: [free coordinates of ParamMap (18 for B2) | b (48) | w (47)] = 113.
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.special import ndtr

from kt_trial.bvn import cell_probs_and_grads
from kt_trial.composite_likelihood import P_FLOOR, cell_index
from kt_trial.models import ParamMap
from kt_trial.moments import Theta, moment_jacobians

_INV = 1.0 / np.sqrt(2 * np.pi)


def sumzero_basis(n_items: int) -> np.ndarray:
    """Orthonormal basis (n_items x n_items-1) of the subspace {v : sum v = 0}."""
    Q, _ = np.linalg.qr(np.column_stack([np.ones(n_items), np.eye(n_items)[:, :n_items - 1]]))
    return Q[:, 1:]


def normalise(theta: Theta, lam: np.ndarray):
    """Move (theta, lam) to the geometric-mean-one representation: lam* = lam/g, locations x g, variances x g^2.
    Returns (theta*, lam*, g); sigma2_F* = g^2 sigma2_F is the estimand."""
    g = float(np.exp(np.mean(np.log(lam))))
    th = theta.copy(alpha_bar=theta.alpha_bar * g, r_bar=theta.r_bar * g, sigma2_alpha=theta.sigma2_alpha * g * g,
                    sigma2_r=theta.sigma2_r * g * g, sigma2_F=theta.sigma2_F * g * g, Sigma_M=theta.Sigma_M * g * g)
    return th, np.asarray(lam, float) / g, g


def core(theta: Theta, templates, ids: np.ndarray, lam: np.ndarray, iu, ju, need_jac=True) -> dict:
    """a (G,T), rho (G,P), D (G,T) and, if need_jac, derivatives with respect to the natural parameter vector Theta.to_nat() (Q) and
    with respect to lambda_q (n_items). Templates must carry the difficulties in .b."""
    G, T = len(templates), templates[0].T
    n_items = len(lam)
    a = np.empty((G, T)); D = np.empty((G, T)); rho = np.empty((G, len(iu)))
    out = {"a": a, "D": D, "rho": rho}
    if need_jac:
        Q = len(theta.to_nat())
        out.update(dA_x=np.empty((G, T, Q)), dR_x=np.empty((G, len(iu), Q)), dA_l=np.empty((G, T, n_items)),
                   dR_l=np.empty((G, len(iu), n_items)))
    for g, tpl in enumerate(templates):
        t0 = copy.copy(tpl); t0.b = np.zeros(T)
        mu0, V0, dmu0, dV0 = moment_jacobians(t0, theta)
        L = V0 - np.eye(T)
        lt = np.asarray(lam)[ids[g]]
        mu = -tpl.b + lt * mu0
        V = np.outer(lt, lt) * L + np.eye(T)
        d = np.diag(V); sd = np.sqrt(d)
        a[g] = mu / sd; D[g] = d
        rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
        if not need_jac:
            continue
        dmu = lt[:, None] * dmu0
        dV = np.outer(lt, lt)[..., None] * dV0
        dD = np.einsum("ttq->tq", dV)
        out["dA_x"][g] = dmu / sd[:, None] - (mu / (2.0 * d * sd))[:, None] * dD
        out["dR_x"][g] = (dV[iu, ju, :] / (sd[iu] * sd[ju])[:, None]
                          - 0.5 * rho[g][:, None] * (dD[iu] / d[iu][:, None] + dD[ju] / d[ju][:, None]))
        E = np.zeros((T, n_items)); E[np.arange(T), ids[g]] = 1.0
        dmu_l = mu0[:, None] * E
        dD_l = (2.0 * lt * np.diag(L))[:, None] * E
        dV_l = L[iu, ju][:, None] * (lt[ju][:, None] * E[iu] + lt[iu][:, None] * E[ju])
        out["dA_l"][g] = dmu_l / sd[:, None] - (mu / (2.0 * d * sd))[:, None] * dD_l
        out["dR_l"][g] = (dV_l / (sd[iu] * sd[ju])[:, None]
                          - 0.5 * rho[g][:, None] * (dD_l[iu] / d[iu][:, None] + dD_l[ju] / d[ju][:, None]))
    return out


def assemble(pm: ParamMap, x, theta: Theta, templates, ids, lam, iu, ju, free_b=True, free_lam=True) -> dict:
    """Derivatives with respect to the full coordinate vector [x | b | w] (blocks switched off when fixed)."""
    n_items = len(lam)
    c = core(theta, templates, ids, lam, iu, ju)
    Jn = pm.jacobian(x)
    dA = [c["dA_x"] @ Jn]; dR = [c["dR_x"] @ Jn]
    G, T = c["a"].shape
    if free_b:
        ab = np.zeros((G, T, n_items))
        g_, t_ = np.indices((G, T))
        ab[g_, t_, ids] = -1.0 / np.sqrt(c["D"])
        dA.append(ab); dR.append(np.zeros((G, len(iu), n_items)))
    if free_lam:
        P = sumzero_basis(n_items)
        M = np.asarray(lam)[:, None] * P                                   # d lambda / d w
        dA.append(c["dA_l"] @ M); dR.append(c["dR_l"] @ M)
    return {"a": c["a"], "rho": c["rho"], "D": c["D"], "dA": np.concatenate(dA, -1), "dR": np.concatenate(dR, -1)}


def observable_jacobian(m: dict, iu, ju):
    a, rho, dA, dR = m["a"], m["rho"], m["dA"], m["dR"]
    p, dp = cell_probs_and_grads(a[:, iu], a[:, ju], rho)
    d11 = dp[..., 0, :]
    dmarg = (_INV * np.exp(-0.5 * a ** 2))[..., None] * dA
    dj = d11[..., 0:1] * dA[:, iu] + d11[..., 1:2] * dA[:, ju] + d11[..., 2:3] * dR
    n = dA.shape[-1]
    J = np.concatenate([dmarg.reshape(-1, n), dj.reshape(-1, n)], 0)
    vals = np.concatenate([ndtr(a).ravel(), p[..., 0].ravel()])
    return vals, J


def fisher(m: dict, iu, ju):
    a, rho, dA, dR = m["a"], m["rho"], m["dA"], m["dR"]
    p, dp = cell_probs_and_grads(a[:, iu], a[:, ju], rho)
    G, n = len(a), dA.shape[-1]
    H = np.zeros((n, n))
    for g in range(G):
        dc = (dp[g, :, :, 0:1] * dA[g][iu][:, None, :] + dp[g, :, :, 1:2] * dA[g][ju][:, None, :]
              + dp[g, :, :, 2:3] * dR[g][:, None, :])
        H += np.einsum("pcq,pcr,pc->qr", dc, dc, 1.0 / p[g])
    return H / G


def learner_scores(m: dict, Y: np.ndarray, tid: np.ndarray, chunk=400) -> np.ndarray:
    import scipy.sparse as sp
    a, rho, dA, dR = m["a"], m["rho"], m["dA"], m["dR"]
    T = Y.shape[1]
    iu, ju = np.triu_indices(T, 1)
    P = len(iu)
    p, dp = cell_probs_and_grads(a[:, iu], a[:, ju], rho)
    dlogp = dp / np.maximum(p, P_FLOOR)[..., None]
    Iu = sp.csr_matrix((np.ones(P), (np.arange(P), iu)), shape=(P, T))
    Ju = sp.csr_matrix((np.ones(P), (np.arange(P), ju)), shape=(P, T))
    S = np.zeros((Y.shape[0], dA.shape[-1]))
    ar = np.arange(P)[None, :]
    for g in range(len(a)):
        idx = np.flatnonzero(tid == g)
        for s in range(0, len(idx), chunk):
            ii = idx[s:s + chunk]
            y = Y[ii].astype(np.int64)
            cell = cell_index(y[:, iu], y[:, ju])
            w = dlogp[g][ar, cell]
            wobs = (Iu.T @ w[:, :, 0].T).T + (Ju.T @ w[:, :, 1].T).T
            S[ii] = wobs @ dA[g] + w[:, :, 2] @ dR[g]
    return S
