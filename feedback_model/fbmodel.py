"""Feedback-aware pairwise composite likelihood, approximation L0 (X6-D02), with analytic (reverse-mode) gradient.

Per template, with lt = lambda[ids], mu0 and L the Experiment-1 latent mean and covariance without the unit residual (kt_trial.moments, b = 0),
U[r,t] = kappa W[r,t], W[r,t] = 1{r < t, r practice, same session} exp(-(time_t - time_r)/tau_D):

  forward recursion (t = 0..T-1)   m_t = sum_r U[r,t] e_r,   v_t = sum_r U[r,t]^2 h_r,   h_r = e_r (1 - e_r)
      mut_t = -b_t + lt_t (mu0_t + m_t),   d_t = 1 + lt_t^2 (L_tt + v_t),   a_t = mut_t / sqrt(d_t),   e_t = 1 - Phi(a_t)
  shared-history covariance        C = U' diag(h) U,    Lam = L + C   (C_tt = v_t)
  pair (s < t), direct effect exact:
      dd = d_t - lt_t^2 U_st^2 h_s,  mu1 = mut_t - lt_t U_st e_s,  mu0p = mut_t + lt_t U_st (1 - e_s)
      a_s = mut_s / sqrt(d_s),  a1 = mu1 / sqrt(dd),  a0 = mu0p / sqrt(dd),  rho = lt_s lt_t Lam_st / sqrt(d_s dd)
      P11 = Phi2(a_s, a1; rho),  P10 = Phi(a_s) - P11,  P01 = Phi(a0) - Phi2(a_s, a0; rho),  P00 = 1 - Phi(a_s) - P01   (cells 11, 10, 01, 00).
At kappa = 0 this is exactly the 2PL objective (discrimination_free.model.Objective2PL).

Coordinates: x = [ free coordinates of ParamMap | b (48) | w (47) | kappa | log tau_D ].
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.special import ndtr

from kt_trial.bvn import RHO_MAX, bvn_cdf, bvn_pdf
from kt_trial.composite_likelihood import P_FLOOR, PairCounts
from kt_trial.moments import latent_moments
from discrimination_free.model import Objective2PL, Param2PL, contract

KAPPA_BOUNDS = (-1.0, 1.0)
TAU_D_BOUNDS = (0.5, 50.0)
_INV = 1.0 / np.sqrt(2.0 * np.pi)


def _pdf(x):
    return _INV * np.exp(-0.5 * x * x)


class ParamFB(Param2PL):
    """2PL coordinates plus kappa and log tau_D."""
    EXTRA = ["kappa", "tau_D"]

    def __init__(self, model: str, K: int, n_items: int):
        super().__init__(model, K, n_items)
        self.n2pl = self.n
        self.names = list(self.names) + self.EXTRA
        self.lb = np.concatenate([self.lb, [KAPPA_BOUNDS[0], np.log(TAU_D_BOUNDS[0])]])
        self.ub = np.concatenate([self.ub, [KAPPA_BOUNDS[1], np.log(TAU_D_BOUNDS[1])]])
        self.n = self.n2pl + 2

    def split(self, x):
        x = np.asarray(x, float)
        return x[:self.nt], x[self.nt:self.nt + self.nb], x[self.nt + self.nb:self.n2pl]

    def extra(self, x):
        """(kappa, tau_D)."""
        x = np.asarray(x, float)
        return float(x[self.n2pl]), float(np.exp(x[self.n2pl + 1]))

    def pack(self, th, b, lam=None, kappa=0.0, tau_D=8.0):
        w = np.zeros(self.nw) if lam is None else self.P.T @ np.log(np.asarray(lam, float))
        ex = [kappa, np.log(tau_D)]
        return np.clip(np.concatenate([self.base.theta_to_x(th), np.asarray(b, float), w, ex]), self.lb, self.ub)

    def from_2pl(self, x2pl, kappa=0.0, tau_D=8.0):
        return np.clip(np.concatenate([np.asarray(x2pl, float), [kappa, np.log(tau_D)]]), self.lb, self.ub)


class _Static:
    """Template constants of the feedback mask: M[r,t] (r < t, r practice, same session), Dt[r,t] = time_t - time_r on M, block starts."""

    def __init__(self, tpl):
        T = tpl.T
        self.M = np.triu(np.ones((T, T), bool), 1) & tpl.practice[:, None] & tpl.same_session
        self.Dt = np.where(self.M, tpl.time[None, :] - tpl.time[:, None], 0.0)
        self.s0 = np.array([int(np.flatnonzero(self.M[:, t]).min()) if self.M[:, t].any() else t for t in range(T)])


def forward_template(st: _Static, mu0, L, lt, bt, kappa, tau_D, iu, ju):
    """Forward pass of one template. Returns the pair intermediates (a_s, a1, a0, rho) and a context for the adjoint."""
    T = len(mu0)
    W = np.where(st.M, np.exp(-st.Dt / tau_D), 0.0)
    U = kappa * W
    e = np.zeros(T); h = np.zeros(T); m = np.zeros(T); v = np.zeros(T)
    mut = np.empty(T); d = np.empty(T); a = np.empty(T)
    for t in range(T):
        s0 = st.s0[t]
        if s0 < t:
            u = U[s0:t, t]
            m[t] = u @ e[s0:t]
            v[t] = (u * u) @ h[s0:t]
        mut[t] = -bt[t] + lt[t] * (mu0[t] + m[t])
        d[t] = 1.0 + lt[t] ** 2 * (L[t, t] + v[t])
        a[t] = mut[t] / np.sqrt(d[t])
        e[t] = ndtr(-a[t])
        h[t] = e[t] * (1.0 - e[t])
    C = U.T @ (h[:, None] * U)
    Lam = L + C
    Up, es, hs = U[iu, ju], e[iu], h[iu]
    ltt, lts = lt[ju], lt[iu]
    dd = d[ju] - ltt ** 2 * Up ** 2 * hs
    sds, sdd = np.sqrt(d[iu]), np.sqrt(dd)
    a_s = mut[iu] / sds
    a1 = (mut[ju] - ltt * Up * es) / sdd
    a0 = (mut[ju] + ltt * Up * (1.0 - es)) / sdd
    Lam_st = Lam[iu, ju]
    rho = lts * ltt * Lam_st / (sds * sdd)
    ctx = dict(st=st, U=U, W=W, e=e, h=h, m=m, v=v, mut=mut, d=d, a=a, dd=dd, sds=sds, sdd=sdd, Up=Up, es=es, hs=hs, ltt=ltt, lts=lts,
               Lam_st=Lam_st, a_s=a_s, a1=a1, a0=a0, rho=rho, mu0=mu0, L=L, lt=lt, kappa=kappa, tau_D=tau_D, iu=iu, ju=ju)
    return (a_s, a1, a0, rho), ctx


def cell_prob_table(a_s, a1, a0, rho):
    """(..., 4) cell probabilities (11, 10, 01, 00) of the L0 pair model."""
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    F1, F0 = bvn_cdf(a_s, a1, rho), bvn_cdf(a_s, a0, rho)
    Pa, Pb0 = ndtr(a_s), ndtr(a0)
    return np.stack([F1, Pa - F1, Pb0 - F0, 1.0 - Pa - Pb0 + F0], -1)


def cell_loglik(a_s, a1, a0, rho, counts, floor=P_FLOOR, grad=True):
    """sum_c counts_c log P_c for the four L0 cells and, if grad, the weights w.r.t. (a_s, a1, a0, rho). Arrays (G, P) / counts (G, P, 4)."""
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    F1 = bvn_cdf(a_s, a1, rho)
    F0 = bvn_cdf(a_s, a0, rho)
    Pa, Pb0 = ndtr(a_s), ndtr(a0)
    P = np.stack([F1, Pa - F1, Pb0 - F0, 1.0 - Pa - Pb0 + F0], -1)
    nf = int(((P < floor) & (counts > 0)).sum())
    pf = np.maximum(P, floor)
    ll = float(np.sum(np.where(counts > 0, counts * np.log(pf), 0.0)))
    if not grad:
        return ll, None, nf
    r = counts / pf
    c1 = r[..., 0] - r[..., 1]
    c0 = r[..., 3] - r[..., 2]
    s = np.sqrt(1.0 - rho * rho)
    pa, pb1, pb0 = _pdf(a_s), _pdf(a1), _pdf(a0)
    w_as = c1 * pa * ndtr((a1 - rho * a_s) / s) + c0 * pa * ndtr((a0 - rho * a_s) / s) + pa * (r[..., 1] - r[..., 3])
    w_a1 = c1 * pb1 * ndtr((a_s - rho * a1) / s)
    w_a0 = c0 * pb0 * ndtr((a_s - rho * a0) / s) + pb0 * (r[..., 2] - r[..., 3])
    w_rho = c1 * bvn_pdf(a_s, a1, rho) + c0 * bvn_pdf(a_s, a0, rho)
    return ll, (w_as, w_a1, w_a0, w_rho), nf


def backward_template(ctx, w):
    """Adjoint of one template. `w` = weights w.r.t. (a_s, a1, a0, rho) (each (P,)). Returns gradients w.r.t.
    (mu0 (T,), L as symmetric-full G (T,T), lt (T,), b_t (T,), kappa, tau_D)."""
    st, U, W = ctx["st"], ctx["U"], ctx["W"]
    e, h, m, v, mut, d, a, dd = (ctx[k] for k in ("e", "h", "m", "v", "mut", "d", "a", "dd"))
    sds, sdd, Up, es, hs, ltt, lts = (ctx[k] for k in ("sds", "sdd", "Up", "es", "hs", "ltt", "lts"))
    a_s, a1, a0, rho, Lam_st = ctx["a_s"], ctx["a1"], ctx["a0"], ctx["rho"], ctx["Lam_st"]
    mu0, L, lt, kappa, tau_D, iu, ju = ctx["mu0"], ctx["L"], ctx["lt"], ctx["kappa"], ctx["tau_D"], ctx["iu"], ctx["ju"]
    was, w1, w0, wr = w
    T = len(mu0)
    # pair-level adjoints
    g_dd = -(w1 * a1 + w0 * a0 + wr * rho) / (2.0 * dd)
    g_ds = -(was * a_s + wr * rho) / (2.0 * d[iu])
    g_mus = was / sds
    g_mu1, g_mu0p = w1 / sdd, w0 / sdd
    g_V = wr / (sds * sdd)
    g_q = -g_dd
    g_ltt = g_q * 2.0 * ltt * Up ** 2 * hs + (-g_mu1 * Up * es + g_mu0p * Up * (1.0 - es)) + g_V * lts * Lam_st
    g_Up = g_q * 2.0 * ltt ** 2 * Up * hs + (-g_mu1 * ltt * es + g_mu0p * ltt * (1.0 - es))
    g_hs = g_q * ltt ** 2 * Up ** 2
    g_es = -(g_mu1 + g_mu0p) * ltt * Up
    g_lts = g_V * ltt * Lam_st
    g_Lam = g_V * lts * ltt
    G_mut = np.bincount(iu, weights=g_mus, minlength=T) + np.bincount(ju, weights=g_mu1 + g_mu0p, minlength=T)
    G_d = np.bincount(iu, weights=g_ds, minlength=T) + np.bincount(ju, weights=g_dd, minlength=T)
    G_e = np.bincount(iu, weights=g_es, minlength=T)
    G_h = np.bincount(iu, weights=g_hs, minlength=T)
    G_lt = np.bincount(iu, weights=g_lts, minlength=T) + np.bincount(ju, weights=g_ltt, minlength=T)
    G_U = np.zeros((T, T)); G_U[iu, ju] = g_Up
    GC = np.zeros((T, T)); GC[iu, ju] = 0.5 * g_Lam
    GC = GC + GC.T                                          # off-diagonal, symmetric-full convention (dl = sum_ij G_ij dL_ij)
    G_L = GC.copy()
    # C = U' diag(h) U (off-diagonal part)
    UG = U @ GC
    G_U += 2.0 * h[:, None] * UG
    G_h += (U * UG).sum(1)
    # reverse recursion
    G_mu0 = np.zeros(T); G_b = np.zeros(T)
    sd_pos = np.sqrt(d)
    for t in range(T - 1, -1, -1):
        G_e[t] += G_h[t] * (1.0 - 2.0 * e[t])
        Ga = -_pdf(a[t]) * G_e[t]
        G_mut[t] += Ga / sd_pos[t]
        G_d[t] += -Ga * a[t] / (2.0 * d[t])
        Gm = G_mut[t] * lt[t]
        Gv = G_d[t] * lt[t] ** 2
        G_mu0[t] = Gm
        G_b[t] = -G_mut[t]
        G_lt[t] += G_mut[t] * (mu0[t] + m[t]) + G_d[t] * 2.0 * lt[t] * (L[t, t] + v[t])
        G_L[t, t] += Gv
        s0 = st.s0[t]
        if s0 < t:
            u = U[s0:t, t]
            G_U[s0:t, t] += Gm * e[s0:t] + Gv * 2.0 * u * h[s0:t]
            G_e[s0:t] += Gm * u
            G_h[s0:t] += Gv * u * u
    g_kappa = float((G_U * W).sum())
    g_tau = float((G_U * kappa * W * st.Dt).sum() / tau_D ** 2)
    return G_mu0, G_L, G_lt, G_b, g_kappa, g_tau


class ObjectiveFB(Objective2PL):
    """Normalised negative composite log-likelihood (per learner-pair) of the L0 feedback model; compatible with kt_trial.fit._one_start."""

    def __init__(self, pm: ParamFB, templates, pc: PairCounts, ids: np.ndarray):
        super().__init__(pm, templates, pc, ids)
        self.static = [_Static(t) for t in templates]
        self.n_floored = 0

    def intermediates(self, x, keep_ctx=False):
        """((G,P) arrays a_s, a1, a0, rho) at coordinate vector x (and the per-template contexts)."""
        pm = self.pm
        xb, b, w = pm.split(x)
        th = pm.base.x_to_theta(xb)
        lam = np.exp(pm.P @ w)
        kappa, tau_D = pm.extra(x)
        iu, ju = self.pc.iu, self.pc.ju
        T = self.templates[0].T
        eye = np.eye(T)
        outs, ctxs = [], []
        for g, tpl in enumerate(self.templates):
            t0 = copy.copy(tpl); t0.b = np.zeros(T)
            mu0, V0 = latent_moments(t0, th)
            o, c = forward_template(self.static[g], mu0, V0 - eye, lam[self.ids[g]], b[self.ids[g]], kappa, tau_D, iu, ju)
            outs.append(o); ctxs.append(c)
        arr = tuple(np.stack([o[k] for o in outs]) for k in range(4))
        return (arr, ctxs, th, lam) if keep_ctx else arr

    def loglik_grad(self, x, grad=True):
        pm = self.pm
        (a_s, a1, a0, rho), ctxs, th, lam = self.intermediates(x, keep_ctx=True)
        ll, wts, nf = cell_loglik(a_s, a1, a0, rho, self.pc.counts, P_FLOOR, grad=grad)
        self.n_floored = nf
        if not grad:
            return ll, None
        g_nat = 0.0; g_l = np.zeros(pm.nb); g_b = np.zeros(pm.nb); g_k = 0.0; g_t = 0.0
        for g, tpl in enumerate(self.templates):
            G_mu0, G_L, G_lt, G_bt, gk, gt = backward_template(ctxs[g], tuple(wk[g] for wk in wts))
            g_nat = g_nat + contract(th, tpl, G_mu0, G_L)
            g_l += np.bincount(self.ids[g], weights=G_lt, minlength=pm.nb)
            g_b += np.bincount(self.ids[g], weights=G_bt, minlength=pm.nb)
            g_k += gk; g_t += gt
        xb = pm.split(x)[0]
        M = lam[:, None] * pm.P
        gx = pm.base.jacobian(xb).T @ g_nat
        _, tau_D = pm.extra(x)
        return ll, np.concatenate([gx, g_b, M.T @ g_l, [g_k, g_t * tau_D]])           # d/d(log tau_D) = tau_D d/d tau_D
