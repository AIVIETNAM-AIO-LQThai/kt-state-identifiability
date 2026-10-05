"""Simulation with optional item-level discrimination misfit:  Z_t = -b_q + lambda_q * (M0 + alpha H^s + r H^f + F) + eps.

With lam=None the draws and the response model are exactly kt_trial.simulator.simulate (only the clean Experiment-1 DGP options
are supported here). lambda_q is drawn once per (scenario, N, replication) in its own RNG namespace, so response randomness is
untouched; lognormal with mean 1 and coefficient of variation `cv`.
"""
from __future__ import annotations

import numpy as np

from kt_trial.config import generating_theta_dict, rng_for
from kt_trial.moments import Theta, histories
from kt_trial.schedule import Template, assign_templates, build_templates
from kt_trial.simulator import Dataset, _gains

CLEAN_DGP = {"session_start_corr": 0.0, "error_jump": 0.0, "gain_dist": "normal"}


def draw_lambda(master_seed: int, scenario_id: str, N: int, rep: int, cv: float, n_items: int) -> np.ndarray:
    if cv <= 0:
        return np.ones(n_items)
    rng = rng_for(master_seed, "lambda", scenario_id, N, rep)
    s = np.sqrt(np.log1p(cv ** 2))
    return np.exp(s * rng.standard_normal(n_items) - s * s / 2.0)


def simulate_lambda(cfg: dict, N: int, seed_keys: tuple, master_seed: int, templates: list[Template] | None = None,
                    lam: np.ndarray | None = None, ids: np.ndarray | None = None, keep_latent: bool = False,
                    theta: Theta | None = None) -> Dataset:
    for k, v in CLEAN_DGP.items():
        if cfg["dgp"][k] != v:
            raise ValueError(f"difficulty_free.simulate_lambda supports only the clean DGP option {k}={v!r}")
    templates = templates or build_templates(cfg)
    th = theta or Theta.from_dict(generating_theta_dict(cfg))
    dgp = cfg["dgp"]
    rng = rng_for(master_seed, "simulate", *seed_keys)
    G = len(templates); K = th.Sigma_M.shape[0]
    tid = assign_templates(rng, N, G)
    M0 = rng.multivariate_normal(np.zeros(K), th.Sigma_M, size=N)
    alpha_u, r_u = _gains(rng, th, dgp, M0, th.Sigma_M)
    sF, tauF, rhoS = np.sqrt(th.sigma2_F), th.tau_F, dgp["session_start_corr"]
    Gshared = rng.standard_normal(N)                                  # consumed to keep the stream identical to kt_trial
    Y = np.zeros((N, templates[0].T), np.int8)
    Fall = np.zeros_like(Y, dtype=float) if keep_latent else None
    for g, tpl in enumerate(templates):
        idx = np.flatnonzero(tid == g)
        n = len(idx)
        if n == 0:
            continue
        Hs, Hf = histories(tpl, th)
        lam_t = None if lam is None else np.asarray(lam)[ids[g]]
        F = np.zeros(n)
        for t in range(tpl.T):
            if t == 0 or tpl.session[t] != tpl.session[t - 1]:
                eps = rng.standard_normal(n)
                F = sF * (np.sqrt(rhoS) * Gshared[idx] + np.sqrt(1 - rhoS) * eps)
            else:
                a = np.exp(-(tpl.time[t] - tpl.time[t - 1]) / tauF)
                F = a * F + np.sqrt(max(sF ** 2 * (1 - a * a), 0.0)) * rng.standard_normal(n)
            if lam_t is None:
                mean = -tpl.b[t] + M0[idx, tpl.skill[t]] + alpha_u[idx] * Hs[t] + r_u[idx] * Hf[t] + F
            else:
                mean = -tpl.b[t] + lam_t[t] * (M0[idx, tpl.skill[t]] + alpha_u[idx] * Hs[t] + r_u[idx] * Hf[t] + F)
            z = mean + rng.standard_normal(n)
            Y[idx, t] = z > 0
            if Fall is not None:
                Fall[idx, t] = F
    meta = {"scenario": cfg["scenario"]["id"], "N": int(N), "seed_keys": [str(k) for k in seed_keys], "master_seed": int(master_seed),
            "lambda_cv": None if lam is None else float(np.std(lam) / np.mean(lam)), "mean_success": float(Y.mean())}
    return Dataset(Y, tid, meta, {"F": Fall} if keep_latent else None)
