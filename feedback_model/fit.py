"""Multi-start fits of the extended 2PL models: B1-FB / B2-FB (kappa, tau_D) and B2+eta. Mirrors discrimination_free.fit.fit_2pl (D19 absolute
stopping rule, R6 Newton polish, D22 Newton-decrement certificate, X4-D09 ridge rule), with an active-coordinate rule that also drops tau_D
when |kappa| <= KAPPA_OFF (tau_D is not identified without feedback)."""
from __future__ import annotations

import time

import numpy as np

from kt_trial.config import rng_for
from kt_trial.fit import _one_start, default_theta, make_starts
from kt_trial.models import embed
from kt_trial.moments import Theta
from difficulty_free.model import start_difficulties
from discrimination_free.fit import (B_JITTER_SD, EXTREME_LOG_LAMBDA, POLISH_WINDOW, W_JITTER_SD, ridge_converged, ridge_flag)

from .etamodel import ObjectiveEta, ParamEta
from .fbmodel import ObjectiveFB, ParamFB

KAPPA_OFF = 5e-3
FB_START_GRID = [(-0.15, 8.0), (-0.30, 2.0), (0.0, 20.0), (-0.05, 5.0), (-0.20, 12.0)]       # (kappa, tau_D) per start
ETA_START_GRID = [0.0, -0.2, 0.2, -0.4, -0.1]
MAX_STEPS, DEC_STOP, MIN_STEP, EIG_SHIFT = 8, 1e-7, 1e-4, 1e-8


def active_coords(pm, x, cfg_fit) -> list[int]:
    tol = cfg_fit["boundary_tol"]
    th = pm.x_to_theta(x)
    act = [i for i in range(pm.n) if pm.lb[i] + tol < x[i] < pm.ub[i] - tol]
    drop = []
    if "tau_F" in pm.names and th.sigma2_F <= tol:
        drop.append("tau_F")
    if "tau_R" in pm.names and th.sigma2_r <= tol and abs(th.r_bar) <= tol:
        drop.append("tau_R")
    if "tau_D" in pm.names and abs(x[pm.names.index("kappa")]) <= KAPPA_OFF:
        drop.append("tau_D")
    return [i for i in act if pm.names[i] not in drop]


def grad_hess(pm, obj, x, act, cfg_fit):
    S = obj.scale
    g = obj(x)[1][act] * S
    H = np.zeros((len(act), len(act)))
    for a, i in enumerate(act):
        h = cfg_fit["hess_step"] * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        H[a] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[act] * S
    return g, 0.5 * (H + H.T)


def newton_polish(pm, obj, x0, cfg_fit, max_steps: int = MAX_STEPS) -> dict:
    x = np.clip(np.asarray(x0, float).copy(), pm.lb, pm.ub)
    steps, shifted, ls_failed = 0, False, False
    dec, not_pd = float("nan"), False
    for it in range(max_steps + 1):
        act = active_coords(pm, x, cfg_fit)
        if not act:
            dec, not_pd = 0.0, False
            break
        g, H = grad_hess(pm, obj, x, act, cfg_fit)
        if not np.all(np.isfinite(H)) or not np.all(np.isfinite(g)):
            dec, not_pd = float("nan"), True
            break
        ev = np.linalg.eigvalsh(H)
        not_pd = bool(ev.min() <= 0)
        mu = 0.0 if not not_pd else EIG_SHIFT * ev.max() - ev.min()
        shifted = shifted or mu > 0
        d = -np.linalg.solve(H + mu * np.eye(len(act)), g)
        dec = float(-0.5 * g @ d) if not not_pd else float("nan")
        if (not not_pd and dec < DEC_STOP) or it == max_steps:
            break
        f0 = obj(x)[0]
        t, moved = 1.0, False
        while t > MIN_STEP:
            xn = x.copy(); xn[act] += t * d; xn = np.clip(xn, pm.lb, pm.ub)
            if obj(xn)[0] < f0:
                x, moved = xn, True
                break
            t /= 2.0
        if not moved:
            ls_failed = True
            break
        steps += 1
    f, _ = obj(x)
    return dict(x=x, ll=float(-f * obj.scale), decrement=dec, hessian_not_pd=not_pd, steps=steps, line_search_failed=ls_failed, shifted=shifted)


def certificate(pm, obj, x, cfg_fit) -> dict:
    """D22 on the active coordinates (as kt_trial.fit.newton_certificate, with the FB-aware active set)."""
    act = active_coords(pm, x, cfg_fit)
    g, H = grad_hess(pm, obj, x, act, cfg_fit)
    w = np.linalg.eigvalsh(H) if len(act) else np.array([1.0])
    not_pd = bool(not np.all(np.isfinite(H)) or w.min() <= 0)
    dec = float("nan") if not_pd else float(0.5 * g @ np.linalg.solve(H, g)) if len(act) else 0.0
    return {"newton_decrement": dec, "hessian_min_eig": float(w.min()), "hessian_not_pd": not_pd, "active_coords": [pm.names[i] for i in act]}


def polish_starts(pm, obj, runs, cfg_fit) -> None:
    ok = [r for r in runs if r["ok"] and np.isfinite(r["ll"])]
    if not ok:
        return
    best_ll = max(r["ll"] for r in ok)
    best_run = max(ok, key=lambda r: r["ll"])
    for r in ok:
        r["polished"] = False
        if r is best_run or (not r["converged"] and r["ll"] >= best_ll - POLISH_WINDOW):
            p = newton_polish(pm, obj, np.array(r["x"]), cfg_fit)
            r.update(polished=True, polish_steps=p["steps"], polish_dll=p["ll"] - r["ll"], polish_line_search_failed=p["line_search_failed"],
                     polish_decrement=p["decrement"], polish_not_pd=p["hessian_not_pd"], n_iter_lbfgs=r["n_iter"])
            if p["ll"] >= r["ll"] - 1e-9:
                r.update(x=p["x"].tolist(), ll=p["ll"])
            if not r["converged"] and not p["hessian_not_pd"] and p["decrement"] <= cfg_fit["newton_tol"]:
                r["converged"] = True
                r["message"] = r["message"] + " | converged by Newton polish"


def fit_ext(kind: str, model: str, templates, pc, cfg_fit: dict, K: int, ids: np.ndarray, n_items: int, seed_keys: tuple, master_seed: int,
            warm: dict | None = None, null_fit: dict | None = None, xcov: np.ndarray | None = None) -> dict:
    """kind 'fb' (kappa, tau_D) or 'eta'. `warm` = a 2PL or smaller-FB fit dict (theta, b, lam[, kappa, tau_D]); `null_fit` = the B1-FB fit (embedded-null
    candidate for B2-FB)."""
    t0 = time.time()
    pm = ParamFB(model, K, n_items) if kind == "fb" else ParamEta(model, K, n_items)
    obj = ObjectiveFB(pm, templates, pc, ids) if kind == "fb" else ObjectiveEta(pm, templates, pc, ids, xcov)
    rng = rng_for(master_seed, f"fit_{kind}", model, *seed_keys)
    th_warm = Theta.from_dict(warm["theta"]) if warm is not None else None
    b0 = np.asarray(warm["b"], float) if warm is not None else start_difficulties(templates, ids, pc, default_theta(cfg_fit, K), n_items)
    lam0 = np.asarray(warm["lam"], float) if warm is not None else np.ones(n_items)
    w0 = pm.P.T @ np.log(lam0)
    starts = []
    for i, xt in enumerate(make_starts(model, pm.base, cfg_fit, K, rng, th_warm)):
        bj = b0 if i == 0 else b0 + rng.normal(0.0, B_JITTER_SD, size=b0.shape)
        wj = w0 if i == 0 else w0 + rng.normal(0.0, W_JITTER_SD, size=w0.shape)
        if kind == "fb":
            k0, td0 = FB_START_GRID[i % len(FB_START_GRID)]
            if i == 0 and warm is not None and "kappa" in warm:
                k0, td0 = warm["kappa"], warm["tau_D"]
            ex = [k0, np.log(td0)]
        else:
            ex = [ETA_START_GRID[i % len(ETA_START_GRID)]]
        starts.append(np.clip(np.concatenate([xt, bj, wj, ex]), pm.lb, pm.ub))
    runs = [_one_start(obj, x0, cfg_fit) for x0 in starts]
    polish_starts(pm, obj, runs, cfg_fit)
    good = [r for r in runs if r["ok"] and np.isfinite(r["ll"])]
    out = dict(model=model, arm=kind, n_params=pm.n, N=pc.N, runs=[{k: v for k, v in r.items() if k != "x"} for r in runs], flags=[],
               seed_keys=[str(k) for k in seed_keys])
    if not good:
        out.update(status="failed", flags=["all_starts_failed"], runtime=time.time() - t0)
        return out
    best = max(good, key=lambda r: r["ll"])
    x = np.array(best["x"])
    theta = pm.x_to_theta(x)
    fell_back = False
    if kind == "fb" and model == "B2" and null_fit is not None and null_fit.get("status") != "failed" and null_fit["ll"] > best["ll"] + 1e-9:
        theta = embed(Theta.from_dict(null_fit["theta"]), "B2").copy(sigma2_F=0.0)
        x = pm.pack(theta, null_fit["b"], null_fit["lam"], null_fit["kappa"], null_fit["tau_D"])
        best = dict(best, ll=null_fit["ll"], grad_norm=float("nan"), grad_inf=float("nan"), converged=True, message="embedded_null")
        fell_back = True
    tol = cfg_fit["boundary_tol"]
    hits = pm.boundary_hits(x, tol)
    flags = [f"boundary:{h}" for h in hits if not h.startswith(("b[", "w["))]
    n_bw = sum(h.startswith(("b[", "w[")) for h in hits)
    if n_bw:
        flags.append(f"boundary:b_or_w x{n_bw}")
    cert = dict(null_fit["certificate"], reused_from="B1-FB") if fell_back else certificate(pm, obj, x, cfg_fit)
    if not best["converged"] and str(best["message"]).startswith("ABNORMAL") and not cert["hessian_not_pd"] \
            and cert["newton_decrement"] <= cfg_fit["newton_tol"]:
        best = dict(best, converged=True)
    if ridge_converged(model, theta, cert, tol, best["converged"]):
        best = dict(best, converged=True)
        flags.append("converged_on_ridge")
    if not best["converged"]:
        flags.append("not_converged")
    if cert["hessian_not_pd"]:
        flags.append("hessian_not_pd")
    elif cert["newton_decrement"] > cfg_fit["newton_tol"]:
        flags.append("newton_decrement_large")
    if any(r["n_bad_eval"] > 0 for r in good):
        flags.append("nonfinite_objective_encountered")
    if fell_back:
        flags.append("embedded_null_selected")
    lls = np.array([r["ll"] for r in good])
    ll_best = float(lls.max())
    at_best = np.array([r["ll"] >= ll_best - cfg_fit["agree_tol"] for r in good])
    secondary = np.array([bool(r["converged"]) and r["ll"] < ll_best - cfg_fit["secondary_delta"] for r in good])
    if at_best.sum() < 2:
        flags.append("single_start_at_best")
    if secondary.any():
        flags.append("secondary_optima_present")
    if model == "B2" and theta.sigma2_F <= tol:
        flags.append("tau_F_not_identified(sigma2_F=0)")
    if ridge_flag(model, theta, tol):
        flags.append("white_noise_ridge")
    if kind == "fb":
        kappa, tau_D = pm.extra(x)
        if abs(kappa) <= KAPPA_OFF:
            flags.append("tau_D_not_identified(kappa~0)")
        out.update(kappa=kappa, tau_D=tau_D)
    else:
        out.update(eta=pm.extra(x))
    n_pol = sum(bool(r.get("polished")) for r in good)
    lam = pm.lam(x)
    n_ext = int((np.abs(np.log(lam)) > EXTREME_LOG_LAMBDA).sum())
    if n_ext > 0.05 * n_items:
        flags.append("many_extreme_lambda")
    out.update(status="ok" if not ({"not_converged", "all_starts_failed"} & set(flags)) else "flagged",
               theta=theta.to_dict(), b=x[pm.nt:pm.nt + pm.nb].tolist(), lam=lam.tolist(), n_extreme_lambda=n_ext, x=x.tolist(),
               ll=float(best["ll"]), grad_inf_abs=best["grad_inf"], certificate=cert, converged=bool(best["converged"]),
               message=best["message"], boundary_hits=hits, flags=flags, n_starts=len(starts), n_good_starts=len(good),
               start_agreement={"n_starts_at_best": int(at_best.sum()), "secondary_optima": int(secondary.sum()), "ll_range": float(lls.max() - lls.min())},
               n_polished=n_pol, polish_line_search_failures=int(sum(bool(r.get("polish_line_search_failed")) for r in good)),
               runtime=time.time() - t0)
    return out
