"""Simulation with outcome feedback:  Z_t = -b_q + lambda_q (M0 + alpha H^s + r H^f + F_t + D_t) + eps,

    D_t = kappa * sum_{s < t, same session, s a practice attempt} 1{Y_s = 0} exp(-(time_t - time_s) / tau_D)      (reset at session start).

With kappa = 0 the draws and responses equal difficulty_free.simulator.simulate_lambda bit for bit. With tau_D = tau_F and lambda == 1,
F + D is the process of kt_trial's scenario S7 (error_jump = kappa). Only the random-number stream of simulate_lambda is consumed.
Optional non-normal (lognormal) gains reproduce Experiment 1's S8/S8n generator through kt_trial.simulator._gains.
"""
from __future__ import annotations

import numpy as np

from kt_trial.config import generating_theta_dict, rng_for
from kt_trial.moments import Theta, histories
from kt_trial.schedule import Template, assign_templates, build_templates
from kt_trial.simulator import Dataset, _gains


def simulate_feedback(cfg: dict, N: int, seed_keys: tuple, master_seed: int, templates: list[Template] | None = None,
                      lam: np.ndarray | None = None, ids: np.ndarray | None = None, theta: Theta | None = None,
                      feedback: dict | None = None, keep_latent: bool = False) -> Dataset:
    """`feedback` = {"kappa": float, "tau_D": float} or None. The scenario's dgp options other than gain_dist are the clean ones."""
    dgp = cfg["dgp"]
    for k, v in (("session_start_corr", 0.0), ("error_jump", 0.0)):
        if dgp[k] != v:
            raise ValueError(f"simulate_feedback supports only the clean DGP option {k}={v!r}")
    kappa = 0.0 if feedback is None else float(feedback["kappa"])
    tau_D = None if feedback is None else float(feedback["tau_D"])
    if kappa != 0.0 and not tau_D > 0:
        raise ValueError("tau_D must be positive")
    templates = templates or build_templates(cfg)
    th = theta or Theta.from_dict(generating_theta_dict(cfg))
    rng = rng_for(master_seed, "simulate", *seed_keys)
    G = len(templates); K = th.Sigma_M.shape[0]
    tid = assign_templates(rng, N, G)
    M0 = rng.multivariate_normal(np.zeros(K), th.Sigma_M, size=N)
    alpha_u, r_u = _gains(rng, th, dgp, M0, th.Sigma_M)
    sF, tauF = np.sqrt(th.sigma2_F), th.tau_F
    rng.standard_normal(N)                                            # consumed to keep the stream identical to simulate_lambda
    T = templates[0].T
    Y = np.zeros((N, T), np.int8)
    Fall = np.zeros((N, T)) if keep_latent else None
    Dall = np.zeros((N, T)) if keep_latent else None
    for g, tpl in enumerate(templates):
        idx = np.flatnonzero(tid == g)
        n = len(idx)
        if n == 0:
            continue
        Hs, Hf = histories(tpl, th)
        lam_t = None if lam is None else np.asarray(lam)[ids[g]]
        F = np.zeros(n); D = np.zeros(n)
        for t in range(T):
            if t == 0 or tpl.session[t] != tpl.session[t - 1]:
                F = sF * rng.standard_normal(n)
                D = np.zeros(n)
            else:
                dt = tpl.time[t] - tpl.time[t - 1]
                a = np.exp(-dt / tauF)
                F = a * F + np.sqrt(max(sF ** 2 * (1 - a * a), 0.0)) * rng.standard_normal(n)
                if kappa != 0.0:
                    D = np.exp(-dt / tau_D) * (D + jump)
            if lam_t is None:
                mean = -tpl.b[t] + M0[idx, tpl.skill[t]] + alpha_u[idx] * Hs[t] + r_u[idx] * Hf[t] + (F + D)
            else:
                mean = -tpl.b[t] + lam_t[t] * (M0[idx, tpl.skill[t]] + alpha_u[idx] * Hs[t] + r_u[idx] * Hf[t] + (F + D))
            y = (mean + rng.standard_normal(n)) > 0
            Y[idx, t] = y
            if Fall is not None:
                Fall[idx, t] = F; Dall[idx, t] = D
            jump = np.where(tpl.practice[t] & ~y, kappa, 0.0) if kappa != 0.0 else 0.0
    meta = {"scenario": cfg["scenario"]["id"], "N": int(N), "seed_keys": [str(k) for k in seed_keys], "master_seed": int(master_seed),
            "feedback": feedback, "lambda_cv": None if lam is None else float(np.std(lam) / np.mean(lam)), "mean_success": float(Y.mean())}
    return Dataset(Y, tid, meta, {"F": Fall, "D": Dall} if keep_latent else None)
