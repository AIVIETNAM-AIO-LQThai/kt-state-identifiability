"""Observable map, Jacobian and pairwise-composite sensitivity with the item difficulties b_q as additional free parameters.

a_t = mu_t / sqrt(D_t) with mu_t = -b_{q_t} + ...; D_t and rho_tt' do not depend on b. Hence
    d a_t / d b_q = -1{item(t) = q} / sqrt(D_t),    d rho / d b = 0.
Items are identified by (skill, item-within-skill): global id = skill * items_per_skill + item (48 items in the Experiment-1 design).
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

from kt_trial.bvn import cell_probs_and_grads
from kt_trial.composite_likelihood import cell_index, pair_quantities, P_FLOOR
from kt_trial.models import ParamMap
from kt_trial.schedule import Template

_INV = 1.0 / np.sqrt(2 * np.pi)


def item_ids(templates: list[Template], items_per_skill: int) -> np.ndarray:
    """(G, T) global item id of every observation."""
    return np.stack([t.skill * items_per_skill + t.item for t in templates])


def dab(pj, ids: np.ndarray, n_items: int) -> np.ndarray:
    """(G, T, n_items): derivative of a_t with respect to each item difficulty."""
    G, T = ids.shape
    out = np.zeros((G, T, n_items))
    g, t = np.indices((G, T))
    out[g, t, ids] = -1.0 / np.sqrt(pj.D)
    return out


def observable_jacobian_free(pm: ParamMap, x, templates, iu, ju, ids, n_items, free_b=True):
    """Jacobian of [Phi(a_t) (all t, all templates); Phi2 pair probabilities] with respect to the free coordinates
    of B2 (n of them) followed, if free_b, by the n_items difficulties. Returns (values, J)."""
    th = pm.x_to_theta(x)
    Jn = pm.jacobian(x)
    pj = pair_quantities(th, templates, iu, ju)
    Q = pj.da.shape[2]
    dmarg = (_INV * np.exp(-0.5 * pj.a ** 2))[..., None] * pj.da
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    d11 = dp[..., 0, :]
    dj = d11[..., 0:1] * pj.da[:, iu] + d11[..., 1:2] * pj.da[:, ju] + d11[..., 2:3] * pj.drho
    J = np.concatenate([dmarg.reshape(-1, Q), dj.reshape(-1, Q)], 0) @ Jn
    if free_b:
        ab = dab(pj, ids, n_items)
        mb = (_INV * np.exp(-0.5 * pj.a ** 2))[..., None] * ab
        jb = d11[..., 0:1] * ab[:, iu] + d11[..., 1:2] * ab[:, ju]
        J = np.concatenate([J, np.concatenate([mb.reshape(-1, n_items), jb.reshape(-1, n_items)], 0)], 1)
    vals = np.concatenate([ndtr(pj.a).ravel(), p[..., 0].ravel()])
    return vals, J


def fisher_free(pm: ParamMap, x, templates, iu, ju, ids, n_items, free_b=True):
    """Per-learner pairwise-composite sensitivity H = sum_pairs sum_c p_c s_c s_c' (averaged over templates), with
    the difficulties appended as extra coordinates when free_b."""
    th = pm.x_to_theta(x)
    Jn = pm.jacobian(x)
    pj = pair_quantities(th, templates, iu, ju)
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    G = len(templates)
    ab = dab(pj, ids, n_items) if free_b else None
    n = pm.n + (n_items if free_b else 0)
    H = np.zeros((n, n))
    for g in range(G):
        dc = (dp[g, :, :, 0:1] * pj.da[g][iu][:, None, :] + dp[g, :, :, 1:2] * pj.da[g][ju][:, None, :]
              + dp[g, :, :, 2:3] * pj.drho[g][:, None, :]) @ Jn
        if free_b:
            db = dp[g, :, :, 0:1] * ab[g][iu][:, None, :] + dp[g, :, :, 1:2] * ab[g][ju][:, None, :]
            dc = np.concatenate([dc, db], -1)
        H += np.einsum("pcq,pcr,pc->qr", dc, dc, 1.0 / p[g])
    return H / G


def learner_scores_free(pm: ParamMap, x, templates, Y, tid, ids, n_items, free_b=True, chunk=400):
    """Per-learner composite scores with respect to the free coordinates (n) and, if free_b, the difficulties."""
    import scipy.sparse as sp
    th = pm.x_to_theta(x)
    Jn = pm.jacobian(x)
    T = Y.shape[1]
    iu, ju = np.triu_indices(T, 1)
    P = len(iu)
    pj = pair_quantities(th, templates, iu, ju)
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    dlogp = dp / np.maximum(p, P_FLOOR)[..., None]
    Iu = sp.csr_matrix((np.ones(P), (np.arange(P), iu)), shape=(P, T))
    Ju = sp.csr_matrix((np.ones(P), (np.arange(P), ju)), shape=(P, T))
    ab = dab(pj, ids, n_items) if free_b else None
    S = np.zeros((Y.shape[0], pm.n + (n_items if free_b else 0)))
    ar = np.arange(P)[None, :]
    for g in range(len(templates)):
        idx = np.flatnonzero(tid == g)
        for s in range(0, len(idx), chunk):
            ii = idx[s:s + chunk]
            y = Y[ii].astype(np.int64)
            cell = cell_index(y[:, iu], y[:, ju])
            w = dlogp[g][ar, cell]
            wobs = (Iu.T @ w[:, :, 0].T).T + (Ju.T @ w[:, :, 1].T).T
            S[ii, :pm.n] = (wobs @ pj.da[g] + w[:, :, 2] @ pj.drho[g]) @ Jn
            if free_b:
                S[ii, pm.n:] = wobs @ ab[g]
    return S


def ridge_tangent_nat(th, b: np.ndarray, n_items: int):
    """Tangent (in natural coordinates + difficulties) of the exact scale ridge that exists when F is white noise:
    locations (b, alpha_bar, r_bar) scale by c, variances (sigma2_alpha, sigma2_r, Sigma_M) by c^2, and the white
    variance by sigma2_F' = c^2 (1 + sigma2_F) - 1. Returns (v_nat over Theta.to_nat(), v_b)."""
    nat = th.to_nat()
    v = np.zeros_like(nat)
    from kt_trial.moments import SCALAR_NAMES
    for i, nme in enumerate(SCALAR_NAMES):
        if nme in ("alpha_bar", "r_bar"):
            v[i] = nat[i]
        elif nme in ("sigma2_alpha", "sigma2_r"):
            v[i] = 2.0 * nat[i]
        elif nme == "sigma2_F":
            v[i] = 2.0 * (1.0 + nat[i])
    v[len(SCALAR_NAMES):] = 2.0 * nat[len(SCALAR_NAMES):]
    return v, b.copy()
