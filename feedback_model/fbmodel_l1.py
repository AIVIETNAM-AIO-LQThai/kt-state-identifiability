"""Feedback-aware pairwise composite likelihood, approximation L1 (X6-D07): probit linearisation of the earlier error indicators.

STEP 1 (forward pass): G0-1b met (X6-F08). STEP 2: analytic reverse-mode gradient (backward_template_l1), see below.

Per template (lt = lambda[ids], mu0 and L as in fbmodel, U = kappa W):
  Sigma_X = (lt lt') o L + I,     mut_t = -b_t + lt_t (mu0_t + m_t),  m_t = sum_r U[r,t] e_r        (as L0)
  E_r = e_r + beta_r z_r + u_r,   beta_r = -phi(a_r) / sigma_r,       s_r = Var(u_r) = e_r (1 - e_r) - phi(a_r)^2
  z = X + Lam U'(diag(beta) z + u)  =>  B[t,r] = lt_t U[r,t] beta_r,  A = (I - B)^-1,  G = A Lam U',  Sigma_z = A Sigma_X A' + G diag(s) G'
  row recursion (t = 0..T-1):  A[t,:] = e_t' + B[t,:t] A[:t,:],  G[t,:] = A[t,:] Lam U',
      sigma_t^2 = A[t] Sigma_X A[t]' + sum_r G[t,r]^2 s_r,   a_t = mut_t / sigma_t,  e_t = Phi(-a_t),  beta_t, s_t
  pair (s < t), direct effect exact (Z_t = mut_t + R_t + lt_t U_st (E_s - e_s), R_t linear):
      CovR = Sigma_z[s,t] - lt_t U_st beta_s sigma_s^2
      VarR = sigma_t^2 - 2 lt_t U_st (beta_s Sigma_z[s,t] + s_s G[t,s]) + lt_t^2 U_st^2 e_s (1 - e_s)
      a_s = mut_s / sigma_s,  a1 = (mut_t - lt_t U_st e_s) / sqrt(VarR),  a0 = (mut_t + lt_t U_st (1 - e_s)) / sqrt(VarR),  rho = CovR / (sigma_s sqrt(VarR))
  and the L0 cell formulas (fbmodel.cell_prob_table / cell_loglik) apply unchanged.
With beta = 0 (s = e (1 - e)) this is exactly L0; with kappa = 0 it is exactly the 2PL.
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.special import ndtr

from kt_trial.composite_likelihood import P_FLOOR
from kt_trial.moments import latent_moments
from discrimination_free.model import contract
from .fbmodel import ObjectiveFB, _pdf, cell_loglik


def forward_template_l1(st, mu0, L, lt, bt, kappa, tau_D, iu, ju, beta_on=True):
    """Forward pass of one template. Returns ((a_s, a1, a0, rho), ctx); ctx['a'] are the mean-field marginals' standardised means."""
    T = len(mu0)
    W = np.where(st.M, np.exp(-st.Dt / tau_D), 0.0)
    U = kappa * W
    SX = np.outer(lt, lt) * L + np.eye(T)
    LUt = lt[:, None] * U.T                                  # [k, r] = lt_k U[r, k]
    A = np.zeros((T, T)); G = np.zeros((T, T))
    e = np.zeros(T); beta = np.zeros(T); s = np.zeros(T)
    m = np.zeros(T); mut = np.empty(T); sig2 = np.empty(T); a = np.empty(T)
    for t in range(T):
        s0 = st.s0[t]
        row = np.zeros(T); row[t] = 1.0
        if s0 < t:
            u = U[s0:t, t]
            m[t] = u @ e[s0:t]
            row += (lt[t] * u * beta[s0:t]) @ A[s0:t, :]
        mut[t] = -bt[t] + lt[t] * (mu0[t] + m[t])
        A[t] = row
        G[t] = row @ LUt
        sig2[t] = row @ SX @ row + (G[t] * G[t]) @ s
        a[t] = mut[t] / np.sqrt(sig2[t])
        e[t] = ndtr(-a[t])
        if beta_on:
            beta[t] = -_pdf(a[t]) / np.sqrt(sig2[t])
            s[t] = max(e[t] * (1.0 - e[t]) - _pdf(a[t]) ** 2, 0.0)
        else:
            s[t] = e[t] * (1.0 - e[t])
    Sz = A @ SX @ A.T + (G * s[None, :]) @ G.T
    sig = np.sqrt(sig2)
    Up, es, ss, bs = U[iu, ju], e[iu], s[iu], beta[iu]
    ltt = lt[ju]
    Sst = Sz[iu, ju]
    CovR = Sst - ltt * Up * bs * sig2[iu]
    VarR = sig2[ju] - 2.0 * ltt * Up * (bs * Sst + ss * G[ju, iu]) + ltt ** 2 * Up ** 2 * es * (1.0 - es)
    var_min = float(VarR.min())
    sdR = np.sqrt(np.maximum(VarR, 1e-12))
    a_s = mut[iu] / sig[iu]
    a1 = (mut[ju] - ltt * Up * es) / sdR
    a0 = (mut[ju] + ltt * Up * (1.0 - es)) / sdR
    rho = CovR / (sig[iu] * sdR)
    ctx = dict(a=a, e=e, beta=beta, s=s, sig2=sig2, mut=mut, m=m, A=A, G=G, Sz=Sz, U=U, W=W, varR_min=var_min,
               rho_absmax=float(np.abs(rho).max()), sig2_min=float(sig2.min()),
               st=st, mu0=mu0, L=L, lt=lt, kappa=kappa, tau_D=tau_D, iu=iu, ju=ju, beta_on=beta_on, SX=SX, LUt=LUt, sig=sig,
               Up=Up, es=es, ss=ss, bs=bs, ltt=ltt, Sst=Sst, Gts=G[ju, iu], sdR=sdR, a_s=a_s, a1=a1, a0=a0, rho=rho, sig2_s=sig2[iu])
    return (a_s, a1, a0, rho), ctx


def backward_template_l1(ctx, w):
    """Adjoint of one L1 template. `w` = weights w.r.t. (a_s, a1, a0, rho) (each (P,)). Returns gradients w.r.t.
    (mu0 (T,), L as symmetric-full G (T,T), lt (T,), b_t (T,), kappa, tau_D); same convention as fbmodel.backward_template."""
    st, U, W = ctx["st"], ctx["U"], ctx["W"]
    A, G, SX, LUt = ctx["A"], ctx["G"], ctx["SX"], ctx["LUt"]
    e, beta, s, m, mut, sig2, a = (ctx[k] for k in ("e", "beta", "s", "m", "mut", "sig2", "a"))
    mu0, L, lt, kappa, tau_D, iu, ju, beta_on = (ctx[k] for k in ("mu0", "L", "lt", "kappa", "tau_D", "iu", "ju", "beta_on"))
    Up, es, ss, bs, ltt, Sst, Gts, sdR, sig2_s = (ctx[k] for k in ("Up", "es", "ss", "bs", "ltt", "Sst", "Gts", "sdR", "sig2_s"))
    a_s, a1, a0, rho = ctx["a_s"], ctx["a1"], ctx["a0"], ctx["rho"]
    was, w1, w0, wr = w
    T = len(mu0)
    sig_s = np.sqrt(sig2_s)
    # ---- pair level -> per-position vectors and matrices
    v = -(w1 * a1 + w0 * a0 + wr * rho) / (2.0 * sdR ** 2)                 # adjoint of VarR
    c = wr / (sig_s * sdR)                                                  # adjoint of CovR
    lin = bs * Sst + ss * Gts
    mut_bar = np.bincount(iu, weights=was / sig_s, minlength=T) + np.bincount(ju, weights=(w1 + w0) / sdR, minlength=T)
    sig2_bar = (np.bincount(iu, weights=-(was * a_s + wr * rho) / (2.0 * sig2_s) - c * ltt * Up * bs, minlength=T)
                + np.bincount(ju, weights=v, minlength=T))
    lt_bar = np.bincount(ju, weights=(-w1 * Up * es + w0 * Up * (1.0 - es)) / sdR - c * Up * bs * sig2_s
                         + v * (-2.0 * Up * lin + 2.0 * ltt * Up ** 2 * es * (1.0 - es)), minlength=T)
    Up_bar = (-w1 * ltt * es + w0 * ltt * (1.0 - es)) / sdR - c * ltt * bs * sig2_s + v * (-2.0 * ltt * lin + 2.0 * ltt ** 2 * Up * es * (1.0 - es))
    e_bar = np.bincount(iu, weights=-(w1 + w0) * ltt * Up / sdR + v * ltt ** 2 * Up ** 2 * (1.0 - 2.0 * es), minlength=T)
    beta_bar = np.bincount(iu, weights=-c * ltt * Up * sig2_s + v * (-2.0 * ltt * Up * Sst), minlength=T)
    s_bar = np.bincount(iu, weights=v * (-2.0 * ltt * Up * Gts), minlength=T)
    Sbar = np.zeros((T, T)); Sbar[iu, ju] = c + v * (-2.0 * ltt * Up * bs)
    Gbar = np.zeros((T, T)); Gbar[ju, iu] = v * (-2.0 * ltt * Up * ss)
    Ubar = np.zeros((T, T)); Ubar[iu, ju] = Up_bar
    # ---- Sz = A SX A' + G diag(s) G'
    Ssym = Sbar + Sbar.T
    Abar = Ssym @ A @ SX
    SXbar = A.T @ Sbar @ A
    Gbar += Ssym @ (G * s[None, :])
    s_bar += ((Sbar @ G) * G).sum(0)
    # ---- reverse row recursion
    mask_s = np.ones(T, bool) if not beta_on else (e * (1.0 - e) - _pdf(a) ** 2 > 0.0)
    G_mu0 = np.zeros(T); G_b = np.zeros(T)
    for t in range(T - 1, -1, -1):
        sg = np.sqrt(sig2[t])
        # local chain: s_t, beta_t, e_t, a_t, sigma_t
        a_bar = 0.0
        sg_bar = 0.0
        if mask_s[t]:
            e_bar[t] += s_bar[t] * (1.0 - 2.0 * e[t])
            if beta_on:
                a_bar += s_bar[t] * 2.0 * a[t] * _pdf(a[t]) ** 2
        if beta_on:
            a_bar += beta_bar[t] * a[t] * _pdf(a[t]) / sg
            sg_bar += beta_bar[t] * _pdf(a[t]) / sg ** 2
        a_bar += -_pdf(a[t]) * e_bar[t]
        mut_bar[t] += a_bar / sg
        sg_bar += -a_bar * a[t] / sg
        sig2_bar[t] += sg_bar / (2.0 * sg)
        row = A[t]
        s0 = st.s0[t]
        rbar = Abar[t] + 2.0 * sig2_bar[t] * (SX @ row)
        Gbar[t] += 2.0 * sig2_bar[t] * G[t] * s
        s_bar += sig2_bar[t] * G[t] * G[t]
        rbar += LUt @ Gbar[t]
        mt = mut_bar[t]
        G_mu0[t] = lt[t] * mt
        G_b[t] = -mt
        lt_bar[t] += mt * (mu0[t] + m[t])
        m_bar = lt[t] * mt
        if s0 < t:
            u = U[s0:t, t]
            c_vec = lt[t] * u * beta[s0:t]
            Abar[s0:t, :] += np.outer(c_vec, rbar)
            cbar = A[s0:t, :] @ rbar
            lt_bar[t] += cbar @ (u * beta[s0:t])
            Ubar[s0:t, t] += lt[t] * cbar * beta[s0:t] + m_bar * e[s0:t]
            beta_bar[s0:t] += lt[t] * cbar * u
            e_bar[s0:t] += m_bar * u
    # ---- batched terms
    SXbar += A.T @ (sig2_bar[:, None] * A)
    LUbar = A.T @ Gbar                                          # LUt[k, r] = lt_k U[r, k]
    lt_bar += (LUbar * U.T).sum(1)
    Ubar += lt[None, :] * LUbar.T
    G_L = SXbar * np.outer(lt, lt)
    G_L = 0.5 * (G_L + G_L.T)
    lt_bar += ((SXbar + SXbar.T) * L) @ lt
    g_kappa = float((Ubar * W).sum())
    g_tau = float((Ubar * kappa * W * st.Dt).sum() / tau_D ** 2)
    return G_mu0, G_L, lt_bar, G_b, g_kappa, g_tau


class ObjectiveFB1(ObjectiveFB):
    """Objective of the L1 model in the ParamFB coordinates (analytic reverse-mode gradient, Step 2)."""

    def __init__(self, pm, templates, pc, ids, beta_on: bool = True):
        super().__init__(pm, templates, pc, ids)
        self.beta_on = beta_on

    def intermediates(self, x, keep_ctx=False):
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
            o, c = forward_template_l1(self.static[g], mu0, V0 - eye, lam[self.ids[g]], b[self.ids[g]], kappa, tau_D, iu, ju, self.beta_on)
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
            G_mu0, G_L, G_lt, G_bt, gk, gt = backward_template_l1(ctxs[g], tuple(wk[g] for wk in wts))
            g_nat = g_nat + contract(th, tpl, G_mu0, G_L)
            g_l += np.bincount(self.ids[g], weights=G_lt, minlength=pm.nb)
            g_b += np.bincount(self.ids[g], weights=G_bt, minlength=pm.nb)
            g_k += gk; g_t += gt
        xb = pm.split(x)[0]
        M = lam[:, None] * pm.P
        gx = pm.base.jacobian(xb).T @ g_nat
        _, tau_D = pm.extra(x)
        return ll, np.concatenate([gx, g_b, M.T @ g_l, [g_k, g_t * tau_D]])
