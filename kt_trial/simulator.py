"""Data simulation for all Experiment-1 scenarios (sequential over observations, vectorised over learners)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.special import ndtri

from .config import generating_theta_dict, rng_for
from .moments import Theta, histories
from .schedule import Template, assign_templates, build_templates


@dataclass
class Dataset:
    Y: np.ndarray                 # (N, T) int8 responses, chronological within each template
    template_id: np.ndarray       # (N,) int
    meta: dict = field(default_factory=dict)
    latent: dict | None = None    # simulator-only truth (M0, alpha, r, F); never used by estimators


def _gains(rng, th: Theta, dgp: dict, M0: np.ndarray, Sigma_M: np.ndarray):
    """Return learner-level slow/fast gains (alpha_u, r_u) for the requested distribution."""
    N = M0.shape[0]
    if dgp["gain_dist"] == "normal":
        return (th.alpha_bar + np.sqrt(th.sigma2_alpha) * rng.standard_normal(N),
                th.r_bar + np.sqrt(th.sigma2_r) * rng.standard_normal(N))
    if dgp["gain_dist"] != "lognormal":
        raise ValueError(dgp["gain_dist"])
    K = M0.shape[1]
    sd_mean = np.sqrt(np.ones(K) @ Sigma_M @ np.ones(K)) / K          # theoretical sd of mean_k M0
    zm = M0.mean(1) / sd_mean
    rho = dgp["gain_corr_m0"]
    ze_a = rho * zm + np.sqrt(1 - rho ** 2) * rng.standard_normal(N)
    ze_r = rho * zm + np.sqrt(1 - rho ** 2) * rng.standard_normal(N)
    s = np.sqrt(np.log1p(dgp["gain_cv"] ** 2))
    return (th.alpha_bar * np.exp(s * ze_a - s ** 2 / 2), th.r_bar * np.exp(s * ze_r - s ** 2 / 2))


def simulate(cfg: dict, N: int, seed_keys: tuple, master_seed: int, templates: list[Template] | None = None,
             keep_latent: bool = False, theta: Theta | None = None) -> Dataset:
    """Simulate N learners under scenario config `cfg` (design + generating + dgp)."""
    templates = templates or build_templates(cfg)
    th = theta or Theta.from_dict(generating_theta_dict(cfg))
    dgp = cfg["dgp"]
    rng = rng_for(master_seed, "simulate", *seed_keys)
    G = len(templates); K = th.Sigma_M.shape[0]
    tid = assign_templates(rng, N, G)
    M0 = rng.multivariate_normal(np.zeros(K), th.Sigma_M, size=N)
    alpha_u, r_u = _gains(rng, th, dgp, M0, th.Sigma_M)
    sF, tauF, rhoS, jump = np.sqrt(th.sigma2_F), th.tau_F, dgp["session_start_corr"], dgp["error_jump"]
    Gshared = rng.standard_normal(N)                                  # learner factor for S6
    Y = np.zeros((N, templates[0].T), np.int8)
    Fall = np.zeros((N, templates[0].T)) if keep_latent else None
    Zall = np.zeros((N, templates[0].T)) if keep_latent else None
    for g, tpl in enumerate(templates):
        idx = np.flatnonzero(tid == g)
        n = len(idx)
        if n == 0:
            continue
        Hs, Hf = histories(tpl, th)
        F = np.zeros(n); jumped = np.zeros(n)
        for t in range(tpl.T):
            new_session = t == 0 or tpl.session[t] != tpl.session[t - 1]
            if new_session:
                eps = rng.standard_normal(n)
                F = sF * (np.sqrt(rhoS) * Gshared[idx] + np.sqrt(1 - rhoS) * eps)
            else:
                a = np.exp(-(tpl.time[t] - tpl.time[t - 1]) / tauF)
                F = a * (F + jumped) + np.sqrt(max(sF ** 2 * (1 - a * a), 0.0)) * rng.standard_normal(n)
            mean = (-tpl.b[t] + M0[idx, tpl.skill[t]] + alpha_u[idx] * Hs[t] + r_u[idx] * Hf[t] + F)
            z = mean + rng.standard_normal(n)
            y = (z > 0)
            Y[idx, t] = y
            if Fall is not None:
                Fall[idx, t] = F
                Zall[idx, t] = z
            # S7: practice error shifts F; the jump then evolves with the OU transition to the next attempt
            jumped = np.where(tpl.practice[t] & ~y, jump, 0.0) if jump != 0.0 else np.zeros(n)
    def _corr(x, y):
        return float(np.corrcoef(x, y)[0, 1]) if N > 2 and x.std() > 0 and y.std() > 0 else None

    def _cv(x):
        return float(x.std() / abs(x.mean())) if N > 2 and x.mean() != 0 else None

    meta = {"scenario": cfg["scenario"]["id"], "N": int(N), "seed_keys": [str(k) for k in seed_keys],
            "master_seed": int(master_seed), "violations": cfg["scenario"]["violations"],
            "realised": {"corr_alpha_r": _corr(alpha_u, r_u), "corr_alpha_meanM0": _corr(alpha_u, M0.mean(1)),
                         "cv_alpha": _cv(alpha_u), "cv_r": _cv(r_u), "mean_success": float(Y.mean())}}
    latent = {"M0": M0, "alpha": alpha_u, "r": r_u, "F": Fall, "Z": Zall} if keep_latent else None
    return Dataset(Y, tid, meta, latent)
