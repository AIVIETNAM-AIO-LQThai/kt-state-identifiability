"""Local identifiability diagnostics for the observable mean-and-pairwise-probability map.

The observable map sends a parameter point x (free coordinates of B2) to
    m(x) = [ Phi(a_t)  for all t ,  Phi2(a_t, a_t'; rho_tt') for all pairs t<t' ]   (every template),
i.e. success probabilities Phi(mu_t / sqrt(D_t)) and joint response probabilities determined by the
standardised means and the correlations C_tt' / sqrt(D_t D_t'). Rows are weighted by the Bernoulli sd of
each probability (so singular values are comparable across rows) and columns are in the unit-scaled
free coordinates used by the estimator (identity for alpha_bar / r_bar / variances, log for time
constants, logit for phi, log-Cholesky for Sigma_M). A full-rank Jacobian supports LOCAL identification
at the tested point only; it says nothing about global uniqueness or finite-sample recovery.
The unknown endpoint scales D_t are differentiated jointly with the correlations (they enter a_t and rho).
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.special import ndtr

from .bvn import cell_probs_and_grads
from .composite_likelihood import learner_scores_nat, pair_quantities
from .config import generating_theta_dict
from .models import ParamMap
from .moments import Theta
from .schedule import Template
from .simulator import simulate

_INV = 1.0 / np.sqrt(2 * np.pi)


def point_theta(cfg: dict, overrides: dict) -> Theta:
    th = Theta.from_dict(generating_theta_dict(cfg))
    return th.copy(**overrides)


def _map_values(pm: ParamMap, x, templates, iu, ju):
    th = pm.x_to_theta(x)
    pj = pair_quantities(th, templates, iu, ju, need_jac=False)
    p, _ = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    return np.concatenate([ndtr(pj.a).ravel(), p[..., 0].ravel()])


def observable_jacobian(pm: ParamMap, x, templates, iu, ju):
    """Analytic Jacobian of the unweighted observable map w.r.t. free coordinates: (rows, n)."""
    th = pm.x_to_theta(x)
    Jn = pm.jacobian(x)                                                  # (Q, n)
    pj = pair_quantities(th, templates, iu, ju)
    G, T, Q = pj.da.shape
    dmarg = (_INV * np.exp(-0.5 * pj.a ** 2))[..., None] * pj.da         # (G,T,Q)
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
    d11 = dp[..., 0, :]                                                  # (G,P,3)
    dj = d11[..., 0:1] * pj.da[:, iu] + d11[..., 1:2] * pj.da[:, ju] + d11[..., 2:3] * pj.drho   # (G,P,Q)
    J = np.concatenate([dmarg.reshape(-1, Q), dj.reshape(-1, Q)], 0) @ Jn
    vals = np.concatenate([ndtr(pj.a).ravel(), p[..., 0].ravel()])
    return vals, J


def fisher_pairwise(pm: ParamMap, x, templates, iu, ju):
    """Per-learner sensitivity H = -E[Hessian of pairwise composite loglik] = sum_pairs sum_c p_c s_c s_c'
    (information identity holds pair by pair under the model), averaged over templates."""
    th = pm.x_to_theta(x)
    Jn = pm.jacobian(x)
    pj = pair_quantities(th, templates, iu, ju)
    p, dp = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)       # (G,P,4), (G,P,4,3)
    G = len(templates)
    H = np.zeros((pm.n, pm.n))
    for g in range(G):
        dc = (dp[g, :, :, 0:1] * pj.da[g][iu][:, None, :] + dp[g, :, :, 1:2] * pj.da[g][ju][:, None, :]
              + dp[g, :, :, 2:3] * pj.drho[g][:, None, :]) @ Jn          # (P,4,n)
        H += np.einsum("pcq,pcr,pc->qr", dc, dc, 1.0 / p[g])
    return H / G


def kl_along(pm: ParamMap, x, direction, steps, templates, iu, ju):
    """Per-learner pairwise-composite KL(theta || theta + s v) for each s."""
    th0 = pm.x_to_theta(x)
    pj0 = pair_quantities(th0, templates, iu, ju, need_jac=False)
    p0, _ = cell_probs_and_grads(pj0.a[:, iu], pj0.a[:, ju], pj0.rho)
    out = []
    for s in steps:
        xs = np.clip(x + s * direction, pm.lb + 1e-12, pm.ub)
        pj = pair_quantities(pm.x_to_theta(xs), templates, iu, ju, need_jac=False)
        p1, _ = cell_probs_and_grads(pj.a[:, iu], pj.a[:, ju], pj.rho)
        out.append(float(np.sum(p0 * (np.log(p0) - np.log(np.maximum(p1, 1e-300)))) / len(templates)))
    return out


def analyse_point(name, cfg, templates, th: Theta, n_score_learners: int, master_seed: int, weak_rel, rank_rel,
                  fd_steps, N_ref, do_godambe=True):
    K = cfg["design"]["n_skills"]
    pm = ParamMap("B2", K)
    x = pm.theta_to_x(th)
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    vals, Jm = observable_jacobian(pm, x, templates, iu, ju)
    G = len(templates); nm = G * T
    p_all = vals.copy()
    sdw = np.sqrt(np.clip(p_all * (1 - p_all), 1e-12, None))
    Jw = Jm / sdw[:, None]
    U, sv, Vt = np.linalg.svd(Jw, full_matrices=False)
    res = {"point": name, "theta": th.to_dict(), "param_names": pm.names, "x": x.tolist(),
           "singular_values": sv.tolist(), "condition_number": float(sv[0] / sv[-1]),
           "rel_sv_min": float(sv[-1] / sv[0]), "numerical_rank": int((sv > rank_rel * sv[0]).sum()),
           "n_params": pm.n, "n_rows": int(Jw.shape[0])}
    res["full_numerical_rank"] = res["numerical_rank"] == pm.n
    res["weak_direction_flag"] = bool(sv[-1] / sv[0] < weak_rel)
    # weakest directions: loadings and KL detectability distance
    weak = []
    steps = np.geomspace(1e-3, 3.0, 25)
    for k in (1, 2, 3):
        v = Vt[-k]
        load = np.argsort(-np.abs(v))[:4]
        kl = kl_along(pm, x, v, steps, templates, iu, ju)
        det = {}
        for N in N_ref:
            hit = [s for s, q in zip(steps, kl) if N * q >= 1.92]
            det[str(N)] = float(hit[0]) if hit else None
        weak.append({"rank_from_smallest": k, "singular_value": float(sv[-k]),
                     "top_loadings": {pm.names[i]: float(v[i]) for i in load},
                     "step_where_N*KL_reaches_1.92": det})
    res["weak_directions"] = weak
    # finite-difference stability of the unweighted Jacobian
    fd = {}
    for h in fd_steps:
        Jfd = np.empty_like(Jm)
        for j in range(pm.n):
            xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
            Jfd[:, j] = (_map_values(pm, xp, templates, iu, ju) - _map_values(pm, xm, templates, iu, ju)) / (2 * h)
        svfd = np.linalg.svd(Jfd / sdw[:, None], compute_uv=False)
        fd[str(h)] = {"max_abs_jac_diff": float(np.abs(Jfd - Jm).max()),
                      "max_rel_sv_diff": float(np.max(np.abs(svfd - sv) / sv))}
    res["finite_difference_check"] = fd
    if do_godambe:
        H = fisher_pairwise(pm, x, templates, iu, ju)
        Hinv = np.linalg.inv(H)
        big = simulate(cfg, n_score_learners, ("ident", name), master_seed, templates, theta=th)
        S = learner_scores_nat(th, templates, big.Y, big.template_id) @ pm.jacobian(x)
        S -= S.mean(0)
        Jmat = S.T @ S / len(S)
        Jn = pm.jacobian(x)
        se = {}
        for N in N_ref:
            Vx = Hinv @ Jmat @ Hinv / N
            Vnat = Jn @ Vx @ Jn.T
            names = ["alpha_bar", "phi", "sigma2_alpha", "r_bar", "tau_R", "sigma2_r", "sigma2_F", "tau_F"]
            se[str(N)] = {n: float(np.sqrt(Vnat[i, i])) for i, n in enumerate(names)}
            se[str(N)]["sigma2_F_if_others_known"] = float(np.sqrt(1.0 / (N * H[pm.names.index("sigma2_F"), pm.names.index("sigma2_F")])))
        res["predicted_godambe_se"] = se
        iF = pm.names.index("sigma2_F")
        Vx = Hinv @ Jmat @ Hinv
        cr = Vx[iF] / np.sqrt(np.diag(Vx) * Vx[iF, iF])
        order = [i for i in np.argsort(-np.abs(cr)) if i != iF][:4]
        res["sigma2_F_estimator_correlation_top"] = {pm.names[i]: float(cr[i]) for i in order}
        res["H_condition_number"] = float(np.linalg.cond(H))
        z = {str(N): float(th.sigma2_F / se[str(N)]["sigma2_F"]) if th.sigma2_F > 0 else None for N in N_ref}
        res["sigma2_F_over_predicted_se"] = z
    return res


def deficient_templates(templates: list[Template]) -> list[Template]:
    """Deliberately deficient design: F never resets and never decays (all pairs share one session with
    zero time separation in the OU kernel), so F is exactly a learner-level intercept. It is then
    indistinguishable from a common shift of Sigma_M, and tau_F has no effect. Only the OU kernel is
    altered; exposure lags for the fast kernel are untouched."""
    out = []
    for t in templates:
        d = copy.copy(t)
        d.same_session = np.ones_like(t.same_session)
        d.absdt = np.zeros_like(t.absdt)
        out.append(d)
    return out


def run_identifiability(cfg: dict, templates: list[Template], master_seed: int, n_score_learners=None,
                        include_deficient=True) -> dict:
    ic = cfg["identifiability"]
    n_sc = n_score_learners or ic["score_learners"]
    out = {"points": {}}
    for name, ov in ic["points"].items():
        th = point_theta(cfg, ov)
        out["points"][name] = analyse_point(name, cfg, templates, th, n_sc, master_seed, ic["weak_rel_sv"],
                                            ic["rank_rel_sv"], ic["fd_steps"], ic["N_reference"])
    if include_deficient:
        th = point_theta(cfg, {})
        dt = deficient_templates(templates)
        out["deficient_single_session_constant_F"] = analyse_point(
            "deficient", cfg, dt, th, 0, master_seed, ic["weak_rel_sv"], ic["rank_rel_sv"], ic["fd_steps"],
            ic["N_reference"], do_godambe=False)
    return out
