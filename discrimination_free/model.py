"""2PL-type model coordinates and pairwise-composite objective with analytic gradient.

x = [ free coordinates of ParamMap(model) | b (48) | w (47) ],  log lambda = P w with P the orthonormal sum-zero basis, so the geometric mean
of lambda is exactly 1 (identification). The gradient chains the per-observation weights wa_t = dl/da_t and per-pair weights w_rho = dl/drho
(as in kt_trial.composite_likelihood) through the Jacobians of twopl.core.
"""
from __future__ import annotations

import numpy as np

import copy

from kt_trial.bvn import weighted_cell_loglik_obs
from kt_trial.composite_likelihood import P_FLOOR, PairCounts
from kt_trial.kernels import dfast_dtauR, dslow_dphi, fast_kernel, slow_kernel
from kt_trial.models import ParamMap
from kt_trial.moments import N_SCALAR, Theta, latent_moments, ou_kernel, tril_idx
from difficulty_free.model import B_BOUNDS

from . import twopl

W_BOUND = 1.5


def contract(theta: Theta, tpl, g_mu: np.ndarray, G: np.ndarray) -> np.ndarray:
    """Adjoint contraction to the natural parameter vector, for dl = g_mu . d(mu0) + sum_ij G_ij dL_ij  (L = latent covariance without the
    unit residual; identical algebra to kt_trial.composite_likelihood._adjoint_gradient)."""
    K = theta.Sigma_M.shape[0]
    T = tpl.T
    Hs = slow_kernel(tpl.n_prior, theta.phi); Hf = fast_kernel(tpl.lag, tpl.expo, theta.tau_R)
    dHs = dslow_dphi(tpl.n_prior, theta.phi); dHf = dfast_dtauR(tpl.lag, tpl.expo, theta.tau_R)
    Kou = ou_kernel(tpl, theta.tau_F)
    GHs, GHf = G @ Hs, G @ Hf
    g = np.zeros(N_SCALAR + K * (K + 1) // 2)
    g[0] = g_mu @ Hs
    g[1] = theta.alpha_bar * (g_mu @ dHs) + 2.0 * theta.sigma2_alpha * (GHs @ dHs)
    g[2] = Hs @ GHs
    g[3] = g_mu @ Hf
    g[4] = theta.r_bar * (g_mu @ dHf) + 2.0 * theta.sigma2_r * (GHf @ dHf)
    g[5] = Hf @ GHf
    GK = G * Kou
    g[6] = GK.sum()
    g[7] = theta.sigma2_F * (GK * tpl.absdt).sum() / theta.tau_F ** 2
    S = np.zeros((T, K)); S[np.arange(T), tpl.skill] = 1.0
    GS = S.T @ G @ S
    r, c = tril_idx(K)
    g[N_SCALAR:] = np.where(r == c, GS[r, c], GS[r, c] + GS[c, r])
    return g


class Param2PL:
    def __init__(self, model: str, K: int, n_items: int):
        self.base = ParamMap(model, K)
        self.model, self.K, self.nb = model, K, n_items
        self.nt = self.base.n
        self.nw = n_items - 1
        self.n = self.nt + n_items + self.nw
        self.P = twopl.sumzero_basis(n_items)
        self.names = (list(self.base.names) + [f"b[{q}]" for q in range(n_items)] + [f"w[{j}]" for j in range(self.nw)])
        self.lb = np.concatenate([self.base.lb, np.full(n_items, B_BOUNDS[0]), np.full(self.nw, -W_BOUND)])
        self.ub = np.concatenate([self.base.ub, np.full(n_items, B_BOUNDS[1]), np.full(self.nw, W_BOUND)])

    def split(self, x):
        x = np.asarray(x, float)
        return x[:self.nt], x[self.nt:self.nt + self.nb], x[self.nt + self.nb:]

    def x_to_theta(self, x) -> Theta:
        return self.base.x_to_theta(np.asarray(x, float)[:self.nt])

    def lam(self, x) -> np.ndarray:
        return np.exp(self.P @ self.split(x)[2])

    def pack(self, th: Theta, b, lam=None) -> np.ndarray:
        w = np.zeros(self.nw) if lam is None else self.P.T @ np.log(np.asarray(lam, float))
        return np.clip(np.concatenate([self.base.theta_to_x(th), np.asarray(b, float), w]), self.lb, self.ub)

    def boundary_hits(self, x, tol):
        hits = []
        for n, xi, lo, hi in zip(self.names, x, self.lb, self.ub):
            if xi <= lo + tol:
                hits.append(f"{n}@lower")
            elif xi >= hi - tol:
                hits.append(f"{n}@upper")
        return hits

    def project_grad(self, x, g, tol=1e-9):
        pg = g.copy()
        pg[(x <= self.lb + tol) & (g > 0)] = 0.0
        pg[(x >= self.ub - tol) & (g < 0)] = 0.0
        return pg


class Objective2PL:
    """Normalised negative composite log-likelihood (per learner-pair), compatible with kt_trial.fit._one_start."""

    def __init__(self, pm: Param2PL, templates, pc: PairCounts, ids: np.ndarray):
        self.pm, self.templates, self.pc, self.ids = pm, templates, pc, ids
        self.scale = float(pc.counts.sum())
        self.n_eval = 0
        self.bad = 0

    def loglik_grad(self, x, grad=True):
        pm = self.pm
        xb, b, w = pm.split(x)
        th = pm.base.x_to_theta(xb)
        lam = np.exp(pm.P @ w)
        iu, ju = self.pc.iu, self.pc.ju
        G, T = len(self.templates), self.templates[0].T
        a = np.empty((G, T)); rho = np.empty((G, len(iu))); mom = []
        eye = np.eye(T)
        for g, tpl in enumerate(self.templates):
            t0 = copy.copy(tpl); t0.b = np.zeros(T)
            mu0, V0 = latent_moments(t0, th)
            L = V0 - eye
            lt = lam[self.ids[g]]
            mu = -b[self.ids[g]] + lt * mu0
            V = np.outer(lt, lt) * L + eye
            d = np.diag(V); sd = np.sqrt(d)
            a[g] = mu / sd
            rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
            mom.append((mu0, L, lt, mu, V, d, sd))
        ll, wts, _ = weighted_cell_loglik_obs(a, iu, ju, rho, self.pc.counts, P_FLOOR, grad=grad)
        if not grad:
            return ll, None
        g_nat = 0.0; g_l = np.zeros(pm.nb); g_b = np.zeros(pm.nb)
        for g, tpl in enumerate(self.templates):
            mu0, L, lt, mu, V, d, sd = mom[g]
            wa = np.bincount(iu, weights=wts[g, :, 0], minlength=T) + np.bincount(ju, weights=wts[g, :, 1], minlength=T)
            w_rho = wts[g, :, 2]
            rh = rho[g]
            g_mu = wa / sd
            g_D = (-wa * mu / (2.0 * d * sd) - np.bincount(iu, weights=w_rho * rh, minlength=T) / (2.0 * d)
                   - np.bincount(ju, weights=w_rho * rh, minlength=T) / (2.0 * d))
            Gm = np.zeros((T, T)); Gm[iu, ju] = 0.5 * w_rho / (sd[iu] * sd[ju])
            Gm = Gm + Gm.T
            Gm[np.diag_indices(T)] = g_D
            g_nat = g_nat + contract(th, tpl, lt * g_mu, np.outer(lt, lt) * Gm)
            g_lt = g_mu * mu0 + 2.0 * ((Gm * L) @ lt)
            g_l += np.bincount(self.ids[g], weights=g_lt, minlength=pm.nb)
            g_b -= np.bincount(self.ids[g], weights=g_mu, minlength=pm.nb)
        M = lam[:, None] * pm.P
        gx = pm.base.jacobian(xb).T @ g_nat
        return ll, np.concatenate([gx, g_b, M.T @ g_l])

    def __call__(self, x):
        self.n_eval += 1
        try:
            ll, g = self.loglik_grad(x)
        except (np.linalg.LinAlgError, FloatingPointError, ValueError):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        if not np.isfinite(ll) or not np.all(np.isfinite(g)):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        return -ll / self.scale, -g / self.scale

    def loglik(self, x):
        return self.loglik_grad(x, grad=False)[0]
