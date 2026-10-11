"""B2+eta (X6-D03): the 2PL pairwise model with a free schedule-term mean shift,  mu_t = -b_q + lambda_q (mu0_t + eta x_{g,t}),
x = state_dependence.diagnostic.carry_covariate (within-item-centred recent error load, probes 0). Coordinates [2PL | eta]."""
from __future__ import annotations

import copy

import numpy as np

from kt_trial.bvn import weighted_cell_loglik_obs
from kt_trial.composite_likelihood import P_FLOOR, PairCounts
from kt_trial.moments import latent_moments
from discrimination_free.model import Objective2PL, Param2PL, contract

ETA_BOUNDS = (-3.0, 3.0)


class ParamEta(Param2PL):
    EXTRA = ["eta"]

    def __init__(self, model: str, K: int, n_items: int):
        super().__init__(model, K, n_items)
        self.n2pl = self.n
        self.names = list(self.names) + self.EXTRA
        self.lb = np.concatenate([self.lb, [ETA_BOUNDS[0]]])
        self.ub = np.concatenate([self.ub, [ETA_BOUNDS[1]]])
        self.n = self.n2pl + 1

    def split(self, x):
        x = np.asarray(x, float)
        return x[:self.nt], x[self.nt:self.nt + self.nb], x[self.nt + self.nb:self.n2pl]

    def extra(self, x):
        return float(np.asarray(x, float)[self.n2pl])

    def from_2pl(self, x2pl, eta=0.0):
        return np.clip(np.concatenate([np.asarray(x2pl, float), [eta]]), self.lb, self.ub)


class ObjectiveEta(Objective2PL):
    def __init__(self, pm: ParamEta, templates, pc: PairCounts, ids: np.ndarray, xcov: np.ndarray):
        super().__init__(pm, templates, pc, ids)
        self.xcov = np.asarray(xcov, float)          # (G, T)

    def loglik_grad(self, x, grad=True):
        pm = self.pm
        xb, b, w = pm.split(x)
        eta = pm.extra(x)
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
            mu = -b[self.ids[g]] + lt * (mu0 + eta * self.xcov[g])
            V = np.outer(lt, lt) * L + eye
            d = np.diag(V); sd = np.sqrt(d)
            a[g] = mu / sd
            rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
            mom.append((mu0, L, lt, mu, V, d, sd))
        ll, wts, _ = weighted_cell_loglik_obs(a, iu, ju, rho, self.pc.counts, P_FLOOR, grad=grad)
        if not grad:
            return ll, None
        g_nat = 0.0; g_l = np.zeros(pm.nb); g_b = np.zeros(pm.nb); g_eta = 0.0
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
            g_lt = g_mu * (mu0 + eta * self.xcov[g]) + 2.0 * ((Gm * L) @ lt)
            g_l += np.bincount(self.ids[g], weights=g_lt, minlength=pm.nb)
            g_b -= np.bincount(self.ids[g], weights=g_mu, minlength=pm.nb)
            g_eta += float((lt * g_mu) @ self.xcov[g])
        M = lam[:, None] * pm.P
        gx = pm.base.jacobian(xb).T @ g_nat
        return ll, np.concatenate([gx, g_b, M.T @ g_l, [g_eta]])
