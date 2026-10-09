"""R6 (X4-D08): damped Newton polish of an L-BFGS-B solution of the 2PL composite objective.

Works on the D22 active coordinates (strictly inside the bounds; tau_F dropped when sigma2_F = 0, tau_R when the fast component is absent),
with the central-difference Hessian of the analytic gradient in ABSOLUTE log-likelihood units, as in kt_trial.fit.newton_certificate.
"""
from __future__ import annotations

import numpy as np

from .model import Objective2PL, Param2PL

MAX_STEPS = 8
DEC_STOP = 1e-7
MIN_STEP = 1e-4
EIG_SHIFT = 1e-8


def active_coords(pm: Param2PL, x, cfg_fit: dict) -> list[int]:
    tol = cfg_fit["boundary_tol"]
    th = pm.x_to_theta(x)
    act = [i for i in range(pm.n) if pm.lb[i] + tol < x[i] < pm.ub[i] - tol]
    drop = []
    if "tau_F" in pm.names and th.sigma2_F <= tol:
        drop.append("tau_F")
    if "tau_R" in pm.names and th.sigma2_r <= tol and abs(th.r_bar) <= tol:
        drop.append("tau_R")
    return [i for i in act if pm.names[i] not in drop]


def _grad_hess(pm: Param2PL, obj: Objective2PL, x, act, cfg_fit):
    S = obj.scale
    g = obj(x)[1][act] * S
    H = np.zeros((len(act), len(act)))
    for a, i in enumerate(act):
        h = cfg_fit["hess_step"] * max(1.0, abs(x[i]))
        xp, xm = x.copy(), x.copy(); xp[i] += h; xm[i] -= h
        H[a] = ((obj(xp)[1] - obj(xm)[1]) / (2 * h))[act] * S
    return g, 0.5 * (H + H.T)


def newton_polish(pm: Param2PL, obj: Objective2PL, x0, cfg_fit: dict, max_steps: int = MAX_STEPS) -> dict:
    """Returns x, ll (absolute), decrement (at the returned x), hessian_not_pd, steps, line_search_failed, shifted."""
    x = np.clip(np.asarray(x0, float).copy(), pm.lb, pm.ub)
    steps, shifted, ls_failed = 0, False, False
    dec, not_pd = float("nan"), False
    for it in range(max_steps + 1):
        act = active_coords(pm, x, cfg_fit)
        if not act:
            dec, not_pd = 0.0, False
            break
        g, H = _grad_hess(pm, obj, x, act, cfg_fit)
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
