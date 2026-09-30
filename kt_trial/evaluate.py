"""Held-out prediction scores and parameter-recovery errors.

Scores here are *population-marginal* quantities computed under fitted parameters on learners that were not
used for fitting: (i) the per-observation Bernoulli log score with p_t = Phi(mu_t / sqrt(D_t)); (ii) the
per-learner pairwise composite log score (sum over all response pairs of log cell probability). Neither
conditions on the held-out learner's own earlier responses, so neither is a next-response prediction.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

from .bvn import cell_probs_and_grads
from .composite_likelihood import P_FLOOR, cell_index, pair_quantities
from .moments import SCALAR_NAMES, Theta
from .schedule import Template
from .simulator import Dataset


def heldout_scores(theta: Theta, templates: list[Template], ds: Dataset) -> dict:
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    pj = pair_quantities(theta, templates, iu, ju, need_jac=False)
    P1 = np.clip(ndtr(pj.a), 1e-300, 1 - 1e-16)
    p, _ = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    logp = np.log(np.maximum(p, P_FLOOR))
    N = ds.Y.shape[0]
    marg, pair = np.zeros(N), np.zeros(N)
    ar = np.arange(len(iu))[None, :]
    for g in range(len(templates)):
        idx = np.flatnonzero(ds.template_id == g)
        if not len(idx):
            continue
        y = ds.Y[idx].astype(np.int64)
        marg[idx] = (y * np.log(P1[g]) + (1 - y) * np.log1p(-P1[g])).mean(1)
        pair[idx] = logp[g][ar, cell_index(y[:, iu], y[:, ju])].sum(1)
    return {"marginal_bernoulli_log_score": marg, "pairwise_composite_log_score": pair}


def paired_difference(a: np.ndarray, b: np.ndarray) -> dict:
    d = a - b
    return {"mean": float(d.mean()), "se": float(d.std(ddof=1) / np.sqrt(len(d)))}


def recovery_errors(theta_hat: Theta, theta_true: Theta) -> dict:
    return {n: float(getattr(theta_hat, n) - getattr(theta_true, n)) for n in SCALAR_NAMES}
