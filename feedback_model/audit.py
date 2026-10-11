"""Stage-0 population audit (X6-D04). For every cell E1..E5 (Experiment-5 data-generating processes), simulate N_big learners and report

  * the L0 approximation check at the TRUE parameters: model cell probabilities against empirical pair frequencies (chi2/df per pair, by pair
    category and feedback lag), for L0 and for the same parameters without feedback (kappa = 0)             [G0-1];
  * pseudo-true values of five fitted models: 2PL B1/B2, B2+eta (schedule term, tau_x = 2), B1-FB/B2-FB: sigma2_F*, tau_F, kappa*, tau_D*, eta*,
    expected T = N * 2 (ll_B2 - ll_B1)/N_big at N = 300, 1000                                                [G0-2, G0-3];
  * Godambe standard errors of (sigma2_F, kappa, tau_D) at N = 300, 1000 for the 2PL and the FB model, and corr(sigma2_F, kappa)   [G0-4].

Composite-likelihood fits depend on the data only through pair counts, so the pseudo-true fits cost the same whatever N_big is. Convergence tolerances
(gtol_abs, newton_tol) are scaled by TOL_SCALE = 100 as in Experiment 5. The Godambe sandwich uses the sensitivity H of the N_big objective
(finite-difference Hessian of the analytic gradient at the pseudo-true fit, per learner) and the covariance J of per-learner scores of N_J further
learners simulated at the same cell; the scores are the chain rule through finite-difference Jacobians of the pair intermediates (a_s, a1, a0, rho).
No confirmatory data are involved.
"""
from __future__ import annotations

import copy
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from scipy.special import ndtr

from kt_trial.composite_likelihood import cell_index, pair_counts
from kt_trial.config import generating_theta_dict, load_scenario
from kt_trial.moments import Theta, latent_moments
from kt_trial.runner import read_json, write_json_atomic
from kt_trial.schedule import build_templates
from difficulty_free.freeb import item_ids
from discrimination_free.fit import fit_2pl
from state_dependence import diagnostic as DG
from state_dependence.audit import null_reference
from state_dependence.simulator import simulate_feedback

from .etamodel import ParamEta
from .fbmodel import ObjectiveFB, ParamFB, cell_loglik, cell_prob_table, forward_template
from .fit import active_coords, fit_ext, grad_hess

N_ITEMS = 48
TOL_SCALE = 100.0
CELLS = [dict(id="E1", base="S1", feedback=None), dict(id="E2", base="S2", feedback=None),
         dict(id="E3", base="S2", feedback={"kappa": -0.25, "tau_D": 10.0}),
         dict(id="E4", base="S2", feedback={"kappa": -0.10, "tau_D": 2.0}),
         dict(id="E5", base="S1", feedback={"kappa": -0.25, "tau_D": 10.0})]
LAG_BINS = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0, 1e9]
TAU_X = 2.0


def _slim(f: dict) -> dict:
    keep = ("model", "arm", "status", "ll", "runtime", "flags", "converged", "n_params", "n_polished", "polish_line_search_failures",
            "certificate", "start_agreement", "boundary_hits", "kappa", "tau_D", "eta")
    out = {k: f[k] for k in keep if k in f}
    if f.get("status") != "failed":
        out["theta"] = f["theta"]
        out["lam_sd_log"] = float(np.std(np.log(f["lam"])))
    return out


# --------------------------------------------------------------------------------------------- approximation check (G0-1)
def true_x(pm: ParamFB, cfg: dict, feedback: dict | None, templates, ids) -> np.ndarray:
    th = Theta.from_dict(generating_theta_dict(cfg))
    b = np.zeros(N_ITEMS)
    for g, t in enumerate(templates):
        b[ids[g]] = t.b
    kappa, tau_D = (0.0, 8.0) if feedback is None else (feedback["kappa"], feedback["tau_D"])
    return pm.pack(th, b, np.ones(N_ITEMS), kappa, tau_D)


def marginal_check(obj: ObjectiveFB, x, Y: np.ndarray, tid: np.ndarray) -> dict:
    """Empirical success rate of every position against the model's Phi(a_t) at x (L0 mean-field marginals), by position category.
    z = (empirical - model) / binomial SE; reported as mean |error| and RMS z."""
    pm = obj.pm
    xb, b, w = pm.split(x)
    th = pm.base.x_to_theta(xb); lam = np.exp(pm.P @ w)
    kappa, tau_D = pm.extra(x)
    T = obj.templates[0].T
    out = {"session_start": [], "practice_later": [], "probe": []}
    for g, tpl in enumerate(obj.templates):
        t0 = copy.copy(tpl); t0.b = np.zeros(T)
        mu0, V0 = latent_moments(t0, th)
        _, ctx = forward_template(obj.static[g], mu0, V0 - np.eye(T), lam[obj.ids[g]], b[obj.ids[g]], kappa, tau_D, obj.pc.iu, obj.pc.ju)
        pm_t = ndtr(ctx["a"])
        sel = tid == g
        emp = Y[sel].mean(0); n = sel.sum()
        se = np.sqrt(np.maximum(pm_t * (1 - pm_t), 1e-12) / n)
        for t in range(T):
            cat = "probe" if not tpl.practice[t] else ("session_start" if obj.static[g].s0[t] == t else "practice_later")
            out[cat].append((emp[t] - pm_t[t], (emp[t] - pm_t[t]) / se[t]))
    return {k: {"n_positions": len(v), "mean_abs_error": float(np.mean([abs(e) for e, _ in v])), "mean_error": float(np.mean([e for e, _ in v])),
                "rms_z": float(np.sqrt(np.mean([z * z for _, z in v])))} for k, v in out.items() if v}


def approx_check(cfg: dict, feedback: dict | None, templates, ids, pc, Y=None, tid=None) -> dict:
    """chi2/df per pair of the empirical pair-cell frequencies against the model cell probabilities at the true parameters, for L0 and for
    kappa = 0 (no feedback term), by pair category and feedback lag. Expected value 1 for an exact model (plus sampling noise of the frequencies).
    With (Y, tid) also the marginal check of the position success rates."""
    pm = ParamFB("B2", 4, N_ITEMS)
    obj = ObjectiveFB(pm, templates, pc, ids)
    x = true_x(pm, cfg, feedback, templates, ids)
    x0 = x.copy(); x0[pm.n2pl] = 0.0
    nl = pc.n_learners.astype(float)
    freq = pc.counts / np.maximum(nl, 1.0)[:, None, None]
    iu, ju = pc.iu, pc.ju
    stat = {}
    cats = {}
    for g, t in enumerate(templates):
        st = obj.static[g]
        act = st.M[iu, ju]
        ws = t.same_session[iu, ju]
        cats.setdefault("fb_active", []).append(act)
        cats.setdefault("within_session_other", []).append(ws & ~act)
        cats.setdefault("cross_session", []).append(~ws)
        lag = np.where(act, t.time[ju] - t.time[iu], np.nan)
        cats.setdefault("lag", []).append(lag)
    cats = {k: np.stack(v) for k, v in cats.items()}
    for label, xx in (("L0", x), ("no_feedback_term", x0)):
        P = cell_prob_table(*obj.intermediates(xx))
        P = np.maximum(P, 1e-12)
        chi = nl[:, None] * ((freq - P) ** 2 / P).sum(-1)                       # (G, P)  ~ chi2_3 per pair if exact
        kl = (freq * np.log(np.maximum(freq, 1e-300) / P)).sum(-1)
        maxerr = np.abs(freq - P).max(-1)
        d = {}
        for name in ("fb_active", "within_session_other", "cross_session"):
            m = cats[name]
            d[name] = {"n_pairs": int(m.sum()), "chi2_per_df": float(chi[m].mean() / 3.0), "mean_kl_x1e4": float(kl[m].mean() * 1e4),
                       "max_abs_err": float(maxerr[m].max())}
        lag = cats["lag"]
        for lo, hi in zip(LAG_BINS[:-1], LAG_BINS[1:]):
            m = cats["fb_active"] & (lag >= lo) & (lag < hi)
            if m.any():
                d[f"fb_active_lag[{lo:g},{hi:g})"] = {"n_pairs": int(m.sum()), "chi2_per_df": float(chi[m].mean() / 3.0),
                                                       "mean_kl_x1e4": float(kl[m].mean() * 1e4), "max_abs_err": float(maxerr[m].max())}
        stat[label] = d
    if Y is not None:
        stat["marginals_L0"] = marginal_check(obj, x, Y, tid)
        stat["marginals_no_feedback_term"] = marginal_check(obj, x0, Y, tid)
    return stat


# --------------------------------------------------------------------------------------------- Godambe sandwich (G0-4)
def godambe(obj: ObjectiveFB, x, act: list[int], cfg_fit: dict, Y: np.ndarray, tid: np.ndarray, N_list, n_pairs: int) -> dict:
    """Asymptotic covariance of the fitted active coordinates `act` at N learners. H: per-learner sensitivity of the N_big objective.
    J: covariance of per-learner composite scores of the learners (Y, tid)."""
    pm = obj.pm
    N_big = obj.scale / n_pairs
    _, Habs = grad_hess(pm, obj, np.asarray(x, float), act, cfg_fit)               # Hessian of -loglik (absolute units, N_big learners)
    H = Habs / N_big
    G = len(obj.templates)
    iu, ju = obj.pc.iu, obj.pc.ju
    P = len(iu)
    base = obj.intermediates(x)
    nA = len(act)
    Jint = np.zeros((G, P, 4, nA))
    for a, k in enumerate(act):
        h = 1e-6 * max(1.0, abs(x[k]))
        xp, xm = np.array(x, float), np.array(x, float); xp[k] += h; xm[k] -= h
        ip, im = obj.intermediates(xp), obj.intermediates(xm)
        for q in range(4):
            Jint[:, :, q, a] = (ip[q] - im[q]) / (2.0 * h)
    # cell weight table: weights of log P_c for a unit count in cell c
    table = np.zeros((G, P, 4, 4))                                             # [g, pair, cell, weight(a_s, a1, a0, rho)]
    for c in range(4):
        cnt = np.zeros((G, P, 4)); cnt[..., c] = 1.0
        _, w, _ = cell_loglik(*base, cnt, grad=True)
        for q in range(4):
            table[:, :, c, q] = w[q]
    S = np.zeros((len(Y), nA))
    ar = np.arange(P)[None, :]
    for g in range(G):
        idx = np.flatnonzero(tid == g)
        Jg = Jint[g].reshape(P * 4, nA)
        for s in range(0, len(idx), 250):
            ii = idx[s:s + 250]
            y = Y[ii].astype(np.int64)
            cell = cell_index(y[:, iu], y[:, ju])
            wg = table[g][ar, cell]                                           # (n, P, 4)
            S[ii] = wg.reshape(len(ii), P * 4) @ Jg
    Jm = np.cov(S.T, bias=True)
    Hi = np.linalg.pinv(H)
    Vl = Hi @ Jm @ Hi                                                         # per-learner asymptotic covariance
    names = [pm.names[k] for k in act]
    out = {"names": names, "mean_score_over_sd": float(np.abs(S.mean(0) / (S.std(0) + 1e-300)).max()), "N_J": int(len(Y))}
    for N in N_list:
        V = Vl / N
        se = np.sqrt(np.maximum(np.diag(V), 0.0))
        d = {n: float(s) for n, s in zip(names, se) if n in ("sigma2_F", "tau_F", "kappa", "tau_D", "sigma2_r", "tau_R", "r_bar", "alpha_bar")}
        if "sigma2_F" in names and "kappa" in names:
            i, j = names.index("sigma2_F"), names.index("kappa")
            d["corr_sigma2F_kappa"] = float(V[i, j] / (se[i] * se[j])) if se[i] > 0 and se[j] > 0 else float("nan")
        out[str(N)] = d
    return out


def _x_for(pm: ParamFB, f: dict, fb: bool) -> np.ndarray:
    return np.array(f["x"], float) if fb else pm.from_2pl(np.array(f["x"], float), 0.0, 8.0)


# --------------------------------------------------------------------------------------------- one cell
def run_point(cell: dict, ac: dict) -> dict:
    t0 = time.time()
    cfg = copy.deepcopy(load_scenario(cell["base"]))
    cfg_fit = dict(cfg["fit"], n_starts=ac.get("n_starts", 5))
    cfg_fit["gtol_abs"] = cfg_fit["gtol_abs"] * TOL_SCALE
    cfg_fit["newton_tol"] = cfg_fit["newton_tol"] * TOL_SCALE
    ts = build_templates(cfg)
    K, G = cfg["design"]["n_skills"], len(ts)
    ids = item_ids(ts, cfg["design"]["items_per_skill"])
    ms, Nb = ac["master_seed"], int(ac["N_big"])
    skey = ("pop", cell["id"])
    ds = simulate_feedback(cfg, Nb, skey, ms, ts, lam=np.ones(N_ITEMS), ids=ids, feedback=cell["feedback"])
    pc = pair_counts(ds.Y, ds.template_id, G)
    res = {"cell": cell["id"], "base": cell["base"], "feedback": cell["feedback"], "N_big": Nb, "mean_success": float(ds.Y.mean())}
    res["approx_check"] = approx_check(cfg, cell["feedback"], ts, ids, pc, ds.Y, ds.template_id)
    t1 = time.time()
    f1 = fit_2pl("B1", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms)
    f2 = fit_2pl("B2", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms, warm=(Theta.from_dict(f1["theta"]), f1["b"], f1["lam"]), null_fit=f1)
    ph = DG.item_success(ds.Y, ds.template_id, ids, N_ITEMS)
    xc = DG.carry_covariate(ts, ids, ph, TAU_X)
    fe = fit_ext("eta", "B2", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms, warm=f2, xcov=xc)
    fb1 = fit_ext("fb", "B1", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms, warm=f1)
    fb2 = fit_ext("fb", "B2", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms, warm=fb1, null_fit=fb1)
    res["fits"] = {"B1": _slim(f1), "B2": _slim(f2), "B2_eta": _slim(fe), "B1_FB": _slim(fb1), "B2_FB": _slim(fb2)}
    res["fit_runtime"] = {k: v.get("runtime") for k, v in res["fits"].items()}
    ok = lambda *fs: all(f["status"] != "failed" for f in fs)
    if ok(f1, f2):
        res["T_per_learner_2PL"] = float(2.0 * (f2["ll"] - f1["ll"]) / Nb)
    if ok(fb1, fb2):
        res["T_per_learner_FB"] = float(2.0 * (fb2["ll"] - fb1["ll"]) / Nb)
    # Godambe SEs
    if ok(fb2, f2):
        dsJ = simulate_feedback(cfg, int(ac["N_J"]), ("popJ", cell["id"]), ms, ts, lam=np.ones(N_ITEMS), ids=ids, feedback=cell["feedback"])
        pm = ParamFB("B2", K, N_ITEMS)
        obj = ObjectiveFB(pm, ts, pc, ids)
        n_pairs = len(pc.iu)
        xfb = _x_for(pm, fb2, True)
        res["godambe_FB"] = godambe(obj, xfb, active_coords(pm, xfb, cfg_fit), cfg_fit, dsJ.Y, dsJ.template_id, ac["N_list"], n_pairs)
        x2 = _x_for(pm, f2, False)
        act2 = [k for k in active_coords(pm, x2, cfg_fit) if k < pm.n2pl]
        res["godambe_2PL"] = godambe(obj, x2, act2, cfg_fit, dsJ.Y, dsJ.template_id, ac["N_list"], n_pairs)
    res["runtime"] = time.time() - t0
    res["runtime_fits_only"] = time.time() - t1
    return res


def run_audit(ac: dict, out_dir, workers: int = 5, log=print) -> int:
    out = Path(out_dir); (out / "points").mkdir(parents=True, exist_ok=True)
    todo = [c for c in CELLS if not (out / "points" / f"{c['id']}.json").exists()]
    log(f"{len(todo)} cells to run")
    if not todo:
        return 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_point, c, ac): c for c in todo}
        for fut in as_completed(futs):
            c = futs[fut]
            try:
                r = fut.result()
                write_json_atomic(out / "points" / f"{c['id']}.json", r)
                log(f"  {c['id']} done in {r['runtime']:.0f}s")
            except Exception as e:                                    # recorded, not silent
                log(f"  {c['id']} FAILED: {e!r}")
    return 0


def summarize(ac: dict, out_dir) -> dict:
    out = Path(out_dir)
    pts = {f.stem: read_json(f) for f in sorted((out / "points").glob("*.json"))}
    ref = null_reference(ac["null_reference"], ac["N_list"])
    rows = {}
    for cid, r in pts.items():
        fits = r["fits"]
        row = {"feedback": r["feedback"], "base": r["base"], "mean_success": r["mean_success"]}
        for key in ("B2", "B2_eta", "B2_FB"):
            f = fits[key]
            if f["status"] == "failed":
                continue
            row[key] = {"sigma2_F": f["theta"]["sigma2_F"], "tau_F": f["theta"]["tau_F"], "tau_R": f["theta"]["tau_R"],
                        "kappa": f.get("kappa"), "tau_D": f.get("tau_D"), "eta": f.get("eta"), "converged": f.get("converged"), "flags": f.get("flags"),
                        "runtime": f.get("runtime")}
        row["B1_FB"] = {k: fits["B1_FB"].get(k) for k in ("kappa", "tau_D", "converged", "flags", "runtime")}
        row["B1"] = {"converged": fits["B1"].get("converged"), "flags": fits["B1"].get("flags"), "runtime": fits["B1"].get("runtime")}
        for lab in ("2PL", "FB"):
            t = r.get(f"T_per_learner_{lab}")
            row[f"E_T_{lab}"] = None if t is None else {str(N): t * N for N in ac["N_list"]}
            row[f"E_T_{lab}_over_q95"] = None if t is None else {str(N): (t * N / ref[str(N)]["q95"] if ref[str(N)]["q95"] else None) for N in ac["N_list"]}
        row["godambe_FB"] = r.get("godambe_FB"); row["godambe_2PL"] = r.get("godambe_2PL")
        row["approx_check"] = r["approx_check"]
        rows[cid] = row
    G = _gates(rows, ref)
    summary = {"null_reference_q95": ref, "gates": G, "cells": rows, "N_big": ac["N_big"], "N_J": ac["N_J"]}
    write_json_atomic(out / "summary.json", summary)
    return summary


def _gates(rows: dict, ref: dict) -> dict:
    g = {}
    def get(cid, key, f):
        r = rows.get(cid, {}).get(key)
        return None if r is None else r.get(f)
    # G0-2: B2+eta
    e3, e5 = get("E3", "B2_eta", "sigma2_F"), get("E5", "B2_eta", "sigma2_F")
    g["G0-2"] = {"E3_sigma2_F_eta": e3, "E5_sigma2_F_eta": e5,
                 "cheap_route_works": bool(e3 is not None and e5 is not None and e3 <= 0.02 and abs(e5 - 0.16) <= 0.03)}
    # G0-3: FB route
    s3, s5, s1 = get("E3", "B2_FB", "sigma2_F"), get("E5", "B2_FB", "sigma2_F"), get("E1", "B2_FB", "sigma2_F")
    k1, k3, k5 = get("E1", "B2_FB", "kappa"), get("E3", "B2_FB", "kappa"), get("E5", "B2_FB", "kappa")
    eT3 = (rows.get("E3", {}).get("E_T_FB") or {}).get("1000")
    q = ref["1000"]["q95"]
    c = {"E3_sigma2_F<=0.02": None if s3 is None else bool(s3 <= 0.02),
         "E3_E[T_FB](N=1000)<q95": None if eT3 is None or q is None else bool(eT3 < q),
         "E5_|sigma2_F-0.16|<=0.03": None if s5 is None else bool(abs(s5 - 0.16) <= 0.03),
         "E1_|sigma2_F-0.16|<=0.01": None if s1 is None else bool(abs(s1 - 0.16) <= 0.01),
         "E1_|kappa|<=0.02": None if k1 is None else bool(abs(k1) <= 0.02),
         "E3_kappa_within_20pct": None if k3 is None else bool(abs(k3 + 0.25) <= 0.05),
         "E5_kappa_within_20pct": None if k5 is None else bool(abs(k5 + 0.25) <= 0.05)}
    g["G0-3"] = {"values": {"E1_sigma2_F": s1, "E3_sigma2_F": s3, "E5_sigma2_F": s5, "E1_kappa": k1, "E3_kappa": k3, "E5_kappa": k5, "E3_E_T_FB_N1000": eT3,
                            "q95_N1000": q, "E4_sigma2_F": get("E4", "B2_FB", "sigma2_F"), "E4_kappa": get("E4", "B2_FB", "kappa")},
                 "checks": c, "all_pass": bool(all(v is True for v in c.values()))}
    return g


def markdown(S: dict) -> str:
    f = lambda x, d=3: "NA" if x is None else f"{x:.{d}f}"
    L = ["# Experiment 6 Stage 0: population audit (numbers only)", "",
         f"N_big = {S['N_big']}, N_J = {S['N_J']}; fits 2PL B1/B2, B2+eta (tau_x = {TAU_X:g}), B1-FB/B2-FB (L0); tolerances scaled x{TOL_SCALE:g}.", "",
         f"Null reference (Experiment 4 V2 2PL T*): {S['null_reference_q95']}", "",
         "## Pseudo-true values (B2 arms)", "",
         "| cell | model | sigma2_F* | tau_F | kappa* | tau_D* | eta* | E[T] N=300 (x q95) | E[T] N=1000 (x q95) | converged | flags |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for cid, r in S["cells"].items():
        for key, lab in (("B2", "2PL"), ("B2_eta", "2PL+eta"), ("B2_FB", "FB")):
            m = r.get(key)
            if not m:
                continue
            et = r.get(f"E_T_{lab}") if lab != "2PL+eta" else None
            eto = r.get(f"E_T_{lab}_over_q95") if lab != "2PL+eta" else None
            L.append(f"| {cid} | {lab} | {f(m['sigma2_F'])} | {f(m['tau_F'], 2)} | {f(m['kappa'])} | {f(m['tau_D'], 2)} | {f(m['eta'])} | "
                     f"{f(et['300'], 2) + ' (' + f(eto['300'], 2) + ')' if et else 'NA'} | {f(et['1000'], 2) + ' (' + f(eto['1000'], 2) + ')' if et else 'NA'} | "
                     f"{m['converged']} | {', '.join(m['flags'] or [])} |")
    L += ["", "## Approximation check at the true parameters: chi2/df per pair (1 = exact model)", "",
          "| cell | group | L0 | no feedback term | n pairs | L0 mean KL x1e4 | no-fb mean KL x1e4 |", "|---|---|---|---|---|---|---|"]
    for cid, r in S["cells"].items():
        ac = r["approx_check"]
        for grp in ac["L0"]:
            a, b = ac["L0"][grp], ac["no_feedback_term"][grp]
            L.append(f"| {cid} | {grp} | {f(a['chi2_per_df'], 2)} | {f(b['chi2_per_df'], 2)} | {a['n_pairs']} | {f(a['mean_kl_x1e4'], 2)} | {f(b['mean_kl_x1e4'], 2)} |")
    L += ["", "## Marginal check at the true parameters: empirical position success rate against the model Phi(a_t) (mean |error|; rms z)", "",
          "| cell | session starts (L0) | practice, later in session (L0) | probes (L0) | practice, later in session (no feedback term) |", "|---|---|---|---|---|"]
    for cid, r in S["cells"].items():
        m, m0 = r["approx_check"].get("marginals_L0"), r["approx_check"].get("marginals_no_feedback_term")
        if not m:
            continue
        cell = lambda d, k: f"{f(d[k]['mean_abs_error'], 4)}; z {f(d[k]['rms_z'], 1)}"
        L.append(f"| {cid} | {cell(m, 'session_start')} | {cell(m, 'practice_later')} | {cell(m, 'probe')} | {cell(m0, 'practice_later')} |")
    L += ["", "## Fit runtimes (s, N_big pair counts; 5 starts) and health", "",
          "| cell | B1 | B2 | B2+eta | B1-FB | B2-FB | B2-FB / B2 | B2-FB flags |", "|---|---|---|---|---|---|---|---|"]
    for cid, r in S["cells"].items():
        rt = lambda k: (r.get(k) or {}).get("runtime")
        ratio = None if not rt("B2") or not rt("B2_FB") else rt("B2_FB") / rt("B2")
        L.append(f"| {cid} | {f(rt('B1'), 0)} | {f(rt('B2'), 0)} | {f(rt('B2_eta'), 0)} | {f(rt('B1_FB'), 0)} | {f(rt('B2_FB'), 0)} | {f(ratio, 2)} | "
                 f"{', '.join((r.get('B2_FB') or {}).get('flags') or [])} |")
    L += ["", "## Godambe SEs (asymptotic, at N = 300 / 1000; SE of tau_D is on the log scale; NA = coordinate inactive at the fit)", "",
          "| cell | model | SE sigma2_F | SE kappa | SE log tau_D | corr(sigma2_F, kappa) |", "|---|---|---|---|---|---|"]
    for cid, r in S["cells"].items():
        for key, lab in (("godambe_2PL", "2PL"), ("godambe_FB", "FB")):
            gd = r.get(key)
            if not gd:
                continue
            for N in ("300", "1000"):
                d = gd[N]
                L.append(f"| {cid} N={N} | {lab} | {f(d.get('sigma2_F'), 4)} | {f(d.get('kappa'), 4)} | {f(d.get('tau_D'), 4)} | {f(d.get('corr_sigma2F_kappa'), 2)} |")
    L += ["", f"## G0-2: {S['gates']['G0-2']}", "", f"## G0-3: {S['gates']['G0-3']}", ""]
    return "\n".join(L)
