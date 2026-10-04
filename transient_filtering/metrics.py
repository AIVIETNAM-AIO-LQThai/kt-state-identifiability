"""Endpoint summaries. Every value is a learner-level mean over the positions of a bin (equal position weights), summarised
by (n, mean, variance) across learners so that results can be pooled exactly and uncertainty computed at the right level."""
from __future__ import annotations

import numpy as np

from kt_trial.schedule import Template

Z90 = 1.6448536269514722


def bin_masks(tpl: Template) -> dict:
    """Positions by within-session index j (0-based): first answer j=0; j=1..4; j=5..15; j=16..31; probes separate."""
    T = tpl.T
    j = np.zeros(T, int)
    for t in range(T):
        j[t] = 0 if t == 0 or tpl.session[t] != tpl.session[t - 1] else j[t - 1] + 1
    prac = tpl.practice.astype(bool)
    return {"first": prac & (j == 0), "j1_4": prac & (j >= 1) & (j <= 4), "j5_15": prac & (j >= 5) & (j <= 15),
            "j16_31": prac & (j >= 16), "probe": ~prac, "practice": prac, "all": np.ones(T, bool)}


def summ(v: np.ndarray) -> dict:
    v = np.asarray(v, float)
    return {"n": int(len(v)), "mean": float(v.mean()), "var": float(v.var(ddof=1)) if len(v) > 1 else 0.0}


def per_bin(a: np.ndarray, masks: dict) -> dict:
    """a (n, T) -> {bin: summ(learner means)}"""
    return {k: summ(a[:, m].mean(1)) for k, m in masks.items()}


def logloss(p: np.ndarray, Y: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(Y * np.log(p) + (1 - Y) * np.log1p(-p))


def paired(a: np.ndarray, b: np.ndarray, masks: dict) -> dict:
    """Gain of arm A over arm B in nats per response: logloss(B) - logloss(A) (positive = A better)."""
    return per_bin(b - a, masks)


def state_metrics(mF, vF, F, masks) -> dict:
    err2 = (mF - F) ** 2
    z = np.abs(mF - F) <= Z90 * np.sqrt(np.maximum(vF, 1e-300))
    return {"mse": per_bin(err2, masks), "coverage90": per_bin(z.astype(float), masks),
            "width90": per_bin(2 * Z90 * np.sqrt(np.maximum(vF, 0.0)), masks), "post_var": per_bin(vF, masks)}


def excursion(mF: np.ndarray, tpl: Template, thresh: float = 0.2) -> dict:
    """Null-safety statistics of the POST-answer transient estimate (absolute units): energy, lag-1 autocorrelation sums
    over consecutive same-session positions, and run lengths of |m| > thresh within a session."""
    n, T = mF.shape
    same = np.array([False] + [bool(tpl.session[t] == tpl.session[t - 1]) for t in range(1, T)])
    num = float((mF[:, 1:] * mF[:, :-1])[:, same[1:]].sum())
    den = float((mF[:, 1:] ** 2)[:, same[1:]].sum())
    runs, total = 0, 0
    over = np.abs(mF) > thresh
    for s in np.unique(tpl.session):
        idx = np.flatnonzero(tpl.session == s)
        o = over[:, idx]
        starts = o & ~np.concatenate([np.zeros((n, 1), bool), o[:, :-1]], 1)
        runs += int(starts.sum()); total += int(o.sum())
    return {"energy_post": per_bin(mF ** 2, bin_masks(tpl)), "lag1_num": num, "lag1_den": den,
            "runs": runs, "run_positions": total, "thresh": thresh}


def persistent_recovery(mp, vp, latent: dict, t_last: int) -> dict:
    """Posterior mean error of (M0 mean over skills, alpha, r) after the last practice answer, and 90% coverage."""
    K = latent["M0"].shape[1]
    m, v = mp[:, t_last], vp[:, t_last]
    truth = np.column_stack([latent["M0"], latent["alpha"], latent["r"]])
    err = m - truth
    cov = np.abs(err) <= Z90 * np.sqrt(np.maximum(v, 1e-300))
    return {"mse_M0": summ((err[:, :K] ** 2).mean(1)), "mse_alpha": summ(err[:, K] ** 2), "mse_r": summ(err[:, K + 1] ** 2),
            "cover90_M0": summ(cov[:, :K].mean(1).astype(float)), "cover90_alpha": summ(cov[:, K].astype(float)),
            "cover90_r": summ(cov[:, K + 1].astype(float))}
