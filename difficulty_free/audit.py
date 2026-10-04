"""Stage-0 analytic identifiability audit with the item difficulties known versus free.

At each tau_F point (other parameters at the generating values) it reports, for b known and b free: numerical rank, condition
number, the three weakest right-singular directions (named coordinates), the response of the observable map along the exact
white-noise scale ridge, and design-based Godambe standard errors of sigma2_F at several N. It makes no claim beyond local
identification at the tested points.
"""
from __future__ import annotations

import numpy as np

from kt_trial.config import generating_theta_dict
from kt_trial.models import ParamMap
from kt_trial.moments import Theta
from kt_trial.simulator import simulate

from .freeb import (fisher_free, item_ids, learner_scores_free, observable_jacobian_free, ridge_tangent_nat)


def difficulties(templates, ids, n_items) -> np.ndarray:
    b = np.full(n_items, np.nan)
    for t, i in zip(templates, ids):
        b[i] = t.b
    return b


def _names(pm, n_items, items_per_skill, free_b):
    nm = list(pm.names)
    if free_b:
        nm += [f"b[{q // items_per_skill},{q % items_per_skill}]" for q in range(n_items)]
    return nm


def _se_table(H, Jmat, Ns, idx_F, n_keep):
    """Godambe SE of the sigma2_F coordinate using the first n_keep coordinates; None when H is numerically singular."""
    Hk, Jk = H[:n_keep, :n_keep], Jmat[:n_keep, :n_keep]
    w = np.linalg.eigvalsh(Hk)
    cond = float(w[-1] / w[0]) if w[0] > 0 else float("inf")
    out = {"H_condition_number": cond, "H_min_eigenvalue": float(w[0])}
    if not np.isfinite(cond) or cond > 1e13:
        out["se"] = {str(N): None for N in Ns}
        out["singular"] = True
        return out
    Hinv = np.linalg.inv(Hk)
    V = Hinv @ Jk @ Hinv
    out["se"] = {str(N): float(np.sqrt(V[idx_F, idx_F] / N)) for N in Ns}
    out["se_if_others_known"] = {str(N): float(np.sqrt(1.0 / (N * Hk[idx_F, idx_F]))) for N in Ns}
    cr = V[idx_F] / np.sqrt(np.diag(V) * V[idx_F, idx_F])
    order = [i for i in np.argsort(-np.abs(cr)) if i != idx_F][:4]
    out["correlation_top"] = {int(i): float(cr[i]) for i in order}
    out["singular"] = False
    return out


def audit_point(name: str, cfg: dict, templates, th: Theta, ac: dict, master_seed: int) -> dict:
    d = cfg["design"]
    K, I = d["n_skills"], d["items_per_skill"]
    n_items = K * I
    ids = item_ids(templates, I)
    pm = ParamMap("B2", K)
    x = pm.theta_to_x(th)
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    b_true = difficulties(templates, ids, n_items)
    res = {"point": name, "tau_F": th.tau_F, "sigma2_F": th.sigma2_F, "n_items": n_items}
    names_free = _names(pm, n_items, I, True)
    # ---- observable-map Jacobian (b known uses the first pm.n columns of the same matrix)
    vals, Jm = observable_jacobian_free(pm, x, templates, iu, ju, ids, n_items, True)
    sdw = np.sqrt(np.clip(vals * (1 - vals), 1e-12, None))
    Jw = Jm / sdw[:, None]
    ridge_ok = th.tau_F < 1e-3
    for label, ncol in (("b_known", pm.n), ("b_free", pm.n + n_items)):
        U, sv, Vt = np.linalg.svd(Jw[:, :ncol], full_matrices=False)
        nm = names_free[:ncol]
        block = {"n_params": ncol, "numerical_rank": int((sv > ac["rank_rel_sv"] * sv[0]).sum()),
                 "full_numerical_rank": bool((sv > ac["rank_rel_sv"] * sv[0]).sum() == ncol),
                 "condition_number": float(sv[0] / sv[-1]), "rel_sv_min": float(sv[-1] / sv[0]),
                 "singular_values_smallest5": [float(s) for s in sv[-5:][::-1]]}
        weak = []
        for k in (1, 2, 3):
            v = Vt[-k]
            top = np.argsort(-np.abs(v))[:5]
            weak.append({"rank_from_smallest": k, "singular_value": float(sv[-k]), "rel": float(sv[-k] / sv[0]),
                         "top_loadings": {nm[i]: float(v[i]) for i in top}})
        block["weak_directions"] = weak
        if label == "b_free":
            Jn = pm.jacobian(x)
            vnat, vb = ridge_tangent_nat(th, b_true, n_items)
            vx = np.linalg.lstsq(Jn, vnat, rcond=None)[0]
            vfull = np.concatenate([vx, vb])
            vhat = vfull / np.linalg.norm(vfull)
            block["ridge_response_rel"] = float(np.linalg.norm(Jw @ vhat) / sv[0])
            block["ridge_cosine_with_weakest"] = [float(abs(vhat @ Vt[-k])) for k in (1, 2, 3)]
            block["ridge_is_exact_at_this_point"] = bool(ridge_ok)
        res[label] = block
    # ---- Godambe SEs of sigma2_F
    H = fisher_free(pm, x, templates, iu, ju, ids, n_items, True)
    big = simulate(cfg, ac["score_learners"], ("ident", name), master_seed, templates, theta=th)
    S = learner_scores_free(pm, x, templates, big.Y, big.template_id, ids, n_items, True)
    S -= S.mean(0)
    Jmat = S.T @ S / len(S)
    iF = pm.names.index("sigma2_F")
    res["godambe_b_known"] = _se_table(H, Jmat, ac["N_list"], iF, pm.n)
    res["godambe_b_free"] = _se_table(H, Jmat, ac["N_list"], iF, pm.n + n_items)
    for lab in ("godambe_b_known", "godambe_b_free"):
        g = res[lab]
        g["sigma2_F_over_se"] = {N: (None if s is None or th.sigma2_F <= 0 else float(th.sigma2_F / s)) for N, s in g["se"].items()}
    return res


def run_audit(cfg: dict, templates, ac: dict) -> dict:
    out = {"points": {}}
    for tau in ac["tau_F_points"]:
        th = Theta.from_dict(generating_theta_dict(cfg)).copy(tau_F=float(tau))
        name = "generating" if abs(tau - cfg["generating"]["tau_F"]) < 1e-12 else f"tauF{tau}"
        out["points"][name] = audit_point(name, cfg, templates, th, ac, ac["master_seed"])
    return out


def gate(audit: dict, cfg: dict, ac: dict) -> dict:
    """Numbers for the Opus gate review (X3-D03): no decision is made here."""
    g = audit["points"]["generating"]
    se = g["godambe_b_free"]["se"].get("1000")
    return {"design_se_sigma2_F_b_free_N1000_tauF10": se, "threshold": ac["gate_se_threshold"],
            "exceeds_threshold": None if se is None else bool(se > ac["gate_se_threshold"]),
            "rank_deficient_b_free_tauF10": not g["b_free"]["full_numerical_rank"]}
