"""Stage-0 analytic identifiability audit of the 2PL-type model (decision X4-D03).

At each point (tau_F, lambda) it reports, with the 48 difficulties free and the 47 log-discrimination coordinates free versus fixed at the
truth: numerical rank, condition number, the three weakest directions (named coordinates), and design-based Godambe SEs of sigma2_F* at
several N. Local identification at the tested points only; no claim about finite-sample recovery.
"""
from __future__ import annotations

import numpy as np

from kt_trial.config import generating_theta_dict
from kt_trial.models import ParamMap
from kt_trial.moments import Theta

from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from difficulty_free.simulator import draw_lambda, simulate_lambda

from . import twopl

N_ITEMS = 48


def _display_names(pm, I):
    return (list(pm.names) + [f"b[{q // I},{q % I}]" for q in range(N_ITEMS)] + [f"loglam[{q // I},{q % I}]" for q in range(N_ITEMS)])


def _display_vector(v, pm, P):
    """Map a right-singular vector over [x | b | w] to [x | b | log-lambda(48)] for naming the loadings."""
    nx, nb = pm.n, N_ITEMS
    return np.concatenate([v[:nx], v[nx:nx + nb], P @ v[nx + nb:]])


def _godambe(H, J, idx, Ns, iF):
    Hk, Jk = H[np.ix_(idx, idx)], J[np.ix_(idx, idx)]
    w = np.linalg.eigvalsh(Hk)
    out = {"n_params": len(idx), "H_min_eigenvalue": float(w[0]), "H_condition_number": float(w[-1] / w[0]) if w[0] > 0 else float("inf")}
    if w[0] <= 0 or out["H_condition_number"] > 1e13:
        out.update(singular=True, se={str(N): None for N in Ns})
        return out
    Hi = np.linalg.inv(Hk)
    V = Hi @ Jk @ Hi
    out.update(singular=False, se={str(N): float(np.sqrt(V[iF, iF] / N)) for N in Ns}, V=V)
    return out


def audit_point(name, cfg, templates, theta_true: Theta, lam_true: np.ndarray, ac: dict, master_seed: int, seed_key=None) -> dict:
    d = cfg["design"]
    K, I = d["n_skills"], d["items_per_skill"]
    ids = item_ids(templates, I)
    pm = ParamMap("B2", K)
    P = twopl.sumzero_basis(N_ITEMS)
    th, lam, g = twopl.normalise(theta_true, lam_true)               # geometric-mean-one representation; sigma2_F* = g^2 sigma2_F
    x = pm.theta_to_x(th)
    iu, ju = np.triu_indices(templates[0].T, 1)
    m = twopl.assemble(pm, x, th, templates, ids, lam, iu, ju, free_b=True, free_lam=True)
    n = m["dA"].shape[-1]
    res = {"point": name, "tau_F": theta_true.tau_F, "sigma2_F_true_param": theta_true.sigma2_F, "g": g, "sigma2_F_star": th.sigma2_F,
           "lambda_cv": float(np.std(lam_true) / np.mean(lam_true)), "n_params": n}
    vals, Jm = twopl.observable_jacobian(m, iu, ju)
    sdw = np.sqrt(np.clip(vals * (1 - vals), 1e-12, None))
    Jw = Jm / sdw[:, None]
    names = _display_names(pm, I)
    for label, ncol in (("lambda_known", pm.n + N_ITEMS), ("lambda_free", n)):
        _, sv, Vt = np.linalg.svd(Jw[:, :ncol], full_matrices=False)
        rank = int((sv > ac["rank_rel_sv"] * sv[0]).sum())
        block = {"n_params": ncol, "numerical_rank": rank, "full_numerical_rank": bool(rank == ncol),
                 "condition_number": float(sv[0] / sv[-1]), "rel_sv_min": float(sv[-1] / sv[0]),
                 "singular_values_smallest5": [float(s) for s in sv[-5:][::-1]]}
        weak = []
        for k in (1, 2, 3):
            v = Vt[-k]
            vd = _display_vector(v, pm, P) if ncol == n else np.concatenate([v[:pm.n], v[pm.n:]])
            top = np.argsort(-np.abs(vd))[:5]
            nm = names if ncol == n else names[:ncol]
            weak.append({"rank_from_smallest": k, "singular_value": float(sv[-k]), "rel": float(sv[-k] / sv[0]),
                         "top_loadings": {nm[i]: float(vd[i]) for i in top}})
        block["weak_directions"] = weak
        res[label] = block
    # design-based Godambe SEs (scores from simulated learners of the unnormalised true model)
    H = twopl.fisher(m, iu, ju)
    key = seed_key or ("ident", name)
    big = simulate_lambda(cfg, ac["score_learners"], key, master_seed, templates,
                          lam=None if np.allclose(lam_true, 1.0) else lam_true, ids=ids, theta=theta_true)
    S = twopl.learner_scores(m, big.Y, big.template_id)
    S -= S.mean(0)
    J = S.T @ S / len(S)
    iF = pm.names.index("sigma2_F")
    gk = _godambe(H, J, list(range(pm.n + N_ITEMS)), ac["N_list"], iF)
    gf = _godambe(H, J, list(range(n)), ac["N_list"], iF)
    # SE of the log-discriminations (free model): sqrt(diag(P V_ww P'))/sqrt(N)
    if not gf["singular"]:
        Vw = gf["V"][pm.n + N_ITEMS:, pm.n + N_ITEMS:]
        sel = np.sqrt(np.clip(np.diag(P @ Vw @ P.T), 0, None))
        gf["loglam_se"] = {str(N): {"mean": float(sel.mean() / np.sqrt(N)), "max": float(sel.max() / np.sqrt(N))} for N in ac["N_list"]}
        cr = gf["V"][iF] / np.sqrt(np.diag(gf["V"]) * gf["V"][iF, iF])
        order = [i for i in np.argsort(-np.abs(cr)) if i != iF][:4]
        dn = list(pm.names) + [f"b[{q // I},{q % I}]" for q in range(N_ITEMS)] + [f"w[{j}]" for j in range(N_ITEMS - 1)]
        gf["correlation_top"] = {dn[i]: float(cr[i]) for i in order}
    for gg in (gk, gf):
        gg.pop("V", None)
        gg["sigma2_F_star_over_se"] = {N: (None if s is None else float(th.sigma2_F / s)) for N, s in gg["se"].items()}
    res["godambe_lambda_known"], res["godambe_lambda_free"] = gk, gf
    return res


def scale_invariance_check(cfg, templates, theta: Theta, lam: np.ndarray, c: float = 1.37) -> dict:
    d = cfg["design"]
    ids = item_ids(templates, d["items_per_skill"])
    iu, ju = np.triu_indices(templates[0].T, 1)
    th2 = theta.copy(alpha_bar=theta.alpha_bar / c, r_bar=theta.r_bar / c, sigma2_alpha=theta.sigma2_alpha / c ** 2,
                     sigma2_r=theta.sigma2_r / c ** 2, sigma2_F=theta.sigma2_F / c ** 2, Sigma_M=theta.Sigma_M / c ** 2)
    c1 = twopl.core(theta, templates, ids, lam, iu, ju, need_jac=False)
    c2 = twopl.core(th2, templates, ids, lam * c, iu, ju, need_jac=False)
    return {"c": c, "max_abs_diff_a": float(np.abs(c1["a"] - c2["a"]).max()), "max_abs_diff_rho": float(np.abs(c1["rho"] - c2["rho"]).max())}


def run_audit(cfg: dict, templates, ac: dict) -> dict:
    out = {"points": {}}
    n_items = N_ITEMS
    for tau in ac["tau_F_points"]:
        base = Theta.from_dict(generating_theta_dict(cfg)).copy(tau_F=float(tau))
        is_gen = abs(tau - cfg["generating"]["tau_F"]) < 1e-12
        out["points"][f"lam1_tauF{tau:g}"] = audit_point(f"lam1_tauF{tau:g}", cfg, templates, base, np.ones(n_items), ac, ac["master_seed"],
                                                          seed_key=("ident", "generating") if is_gen else None)
        lam = draw_lambda(ac["lambda_seed"], "audit", 300, 0, ac["lambda_cv"], n_items)
        out["points"][f"lamcv_tauF{tau:g}"] = audit_point(f"lamcv_tauF{tau:g}", cfg, templates, base, lam, ac, ac["master_seed"])
    lam = draw_lambda(ac["lambda_seed"], "audit", 300, 0, ac["lambda_cv"], n_items)
    out["scale_invariance"] = scale_invariance_check(cfg, templates, Theta.from_dict(generating_theta_dict(cfg)), lam)
    return out


def gate(audit: dict, ac: dict) -> dict:
    """Numbers for the Opus gate review (X4-D03): no decision is made here."""
    res = {}
    for key in ("lam1_tauF10", "lamcv_tauF10"):
        if key not in audit["points"]:
            continue
        p = audit["points"][key]
        se2, se1 = p["godambe_lambda_free"]["se"].get("1000"), p["godambe_lambda_known"]["se"].get("1000")
        res[key] = {"se_2pl_N1000": se2, "se_lambda_known_N1000": se1, "ratio": None if se2 is None or not se1 else se2 / se1,
                    "exceeds_threshold": None if se2 is None else bool(se2 > ac["gate_se_threshold"]),
                    "rank_deficient": not p["lambda_free"]["full_numerical_rank"]}
    res["threshold"] = ac["gate_se_threshold"]
    return res
