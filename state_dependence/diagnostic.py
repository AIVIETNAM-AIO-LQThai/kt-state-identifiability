"""Schedule-based carry-over diagnostic (X5-D02): generalized (Godambe-adjusted) composite-likelihood score test of eta = 0 in

    mu_t = -b_q + lambda_q (mu0_t + eta x_{g,t}),     x_{g,t} = within-item-centred recent error load of template g at position t,

evaluated at a fitted 2PL (B1 or B2) model. The mean shift enters the standardised mean linearly, a_t = (mu_t + lambda_q eta x)/sqrt(D_t), and
leaves D_t and rho unchanged, so d a_t / d eta = lambda_q x_t / sqrt(D_t) and d rho / d eta = 0. The per-learner score is therefore
u_eta = sum_t wobs_t lambda_q x_t / sqrt(D_t), obtained by appending a column to the derivative arrays of discrimination_free.twopl.assemble and
calling twopl.learner_scores / twopl.fisher (no extra fits).

Statistic (efficient-score form; U_theta(theta-hat) = 0 on the active coordinates):
    u~_i = u_{i,eta} - H_{eta,theta} H_{theta,theta}^{-1} u_{i,theta},   S = N * mean(u~)^2 / var(u~)  ~  chi2_1 under eta = 0,
with H the model-based pairwise sensitivity (twopl.fisher) and var(u~) the empirical (centred) variance over learners. Active coordinates are those
strictly inside their bounds (discrimination_free.polish.active_coords), so boundary nuisances are held fixed as in kt_trial.inference.sandwich.
"""
from __future__ import annotations

import copy

import numpy as np
from scipy import stats

from kt_trial.moments import Theta
from kt_trial.schedule import Template
from difficulty_free.model import with_difficulties
from discrimination_free import twopl
from discrimination_free.model import Param2PL
from discrimination_free.polish import active_coords


def item_success(Y: np.ndarray, tid: np.ndarray, ids: np.ndarray, n_items: int) -> np.ndarray:
    """Observed success rate of every item, pooled over templates and occurrences (model-free)."""
    num, den = np.zeros(n_items), np.zeros(n_items)
    for g in range(len(ids)):
        sel = tid == g
        if not sel.any():
            continue
        num += np.bincount(ids[g], weights=Y[sel].sum(0).astype(float), minlength=n_items)
        den += np.bincount(ids[g], weights=np.full(ids.shape[1], float(sel.sum())), minlength=n_items)
    return num / np.maximum(den, 1.0)


def carry_covariate(templates: list[Template], ids: np.ndarray, phat: np.ndarray, tau_x: float) -> np.ndarray:
    """(G, T) within-item-centred recent error load: L = sum_{s<t, same session, practice} exp(-(time_t - time_s)/tau_x) (1 - phat[item_s]),
    defined for practice positions only, centred over the practice occurrences of the same item (templates equally weighted); probes are 0."""
    G, T = len(templates), templates[0].T
    L = np.zeros((G, T))
    for g, tpl in enumerate(templates):
        q = 1.0 - np.asarray(phat)[ids[g]]
        for t in range(T):
            if not tpl.practice[t]:
                continue
            s = np.flatnonzero((np.arange(T) < t) & tpl.same_session[t] & tpl.practice)
            L[g, t] = float(np.sum(np.exp(-(tpl.time[t] - tpl.time[s]) / tau_x) * q[s])) if len(s) else 0.0
    prac = np.stack([t.practice for t in templates])
    x = np.zeros((G, T))
    for item in np.unique(ids):
        sel = (ids == item) & prac
        if sel.any():
            x[sel] = L[sel] - L[sel].mean()
    return x


def eta_columns(D: np.ndarray, lam: np.ndarray, ids: np.ndarray, xs: list[np.ndarray]) -> np.ndarray:
    """(G, T, K) derivatives d a_t / d eta for K covariates."""
    lt = np.asarray(lam)[ids]
    return np.stack([lt * x / np.sqrt(D) for x in xs], -1)


def adjusted_scores(S: np.ndarray, H: np.ndarray, act: list[int], k_idx: int, rcond: float = 1e-12):
    """Efficient scores u~ for the covariate in column k_idx; returns (u~, effective information)."""
    Htt, hte = H[np.ix_(act, act)], H[k_idx, act]
    coef = np.linalg.lstsq(Htt, hte, rcond=rcond)[0]
    return S[:, k_idx] - S[:, act] @ coef, float(H[k_idx, k_idx] - hte @ coef)


def score_stat(u: np.ndarray, info: float) -> dict:
    N = len(u)
    mean, var = float(u.mean()), float(u.var())
    stat = N * mean ** 2 / var if var > 0 else float("nan")
    return {"stat": stat, "p": float(stats.chi2.sf(stat, 1)) if np.isfinite(stat) else float("nan"), "U": float(u.sum()),
            "var_per_learner": var, "info": info, "eta_hat": float(mean / info) if info > 0 else float("nan"),
            "delta": float(mean / np.sqrt(var)) if var > 0 else float("nan")}


def fitted_pieces(fit: dict, templates: list[Template], ids: np.ndarray, n_items: int, K: int):
    """Param map, coordinate vector, derivative dict (without eta columns) and the pair index of a fitted 2PL result dict."""
    pm = Param2PL(fit["model"], K, n_items)
    x = np.array(fit["x"], float)
    th: Theta = pm.x_to_theta(x)
    lam = np.array(fit["lam"], float)
    ts_b = with_difficulties(templates, ids, np.array(fit["b"], float))
    iu, ju = np.triu_indices(templates[0].T, 1)
    m = twopl.assemble(pm.base, x[:pm.nt], th, ts_b, ids, lam, iu, ju, free_b=True, free_lam=True)
    return pm, x, m, iu, ju, lam


def append_eta(m: dict, cols: np.ndarray) -> dict:
    """Return a copy of the derivative dict with K extra eta coordinates (d rho / d eta = 0)."""
    m2 = dict(m)
    m2["dA"] = np.concatenate([m["dA"], cols], -1)
    m2["dR"] = np.concatenate([m["dR"], np.zeros(m["dR"].shape[:2] + (cols.shape[-1],))], -1)
    return m2


def eta_test(fit: dict, templates: list[Template], ids: np.ndarray, Y: np.ndarray, tid: np.ndarray, cfg_fit: dict, taus,
             n_items: int = 48, K: int = 4, phat: np.ndarray | None = None, chunk: int = 400) -> dict:
    """Score test of eta = 0 at the fitted model `fit` (a discrimination_free.fit.fit_2pl result with status != 'failed') for each tau_x in `taus`.
    Returns {tau_x: score_stat dict}, with the number of active nuisance coordinates under key 'n_active'."""
    taus = list(taus)
    pm, x, m, iu, ju, lam = fitted_pieces(fit, templates, ids, n_items, K)
    ph = item_success(Y, tid, ids, n_items) if phat is None else phat
    xs = [carry_covariate(templates, ids, ph, tau) for tau in taus]
    for tau, xc in zip(taus, xs):
        if not np.any(xc):
            raise ValueError(f"covariate for tau_x={tau} is identically zero: the score statistic is undefined")
    m2 = append_eta(m, eta_columns(m["D"], lam, ids, xs))
    H = twopl.fisher(m2, iu, ju)
    S = twopl.learner_scores(m2, Y, tid, chunk=chunk)
    act = active_coords(pm, x, cfg_fit)
    out = {"n_active": len(act)}
    for k, tau in enumerate(taus):
        u, info = adjusted_scores(S, H, act, pm.n + k)
        out[tau] = score_stat(u, info)
    return out
