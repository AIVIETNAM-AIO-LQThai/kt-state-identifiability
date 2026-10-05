"""Free-difficulty model: B1/B2 coordinates plus one difficulty b_q per item (48), and the pairwise composite objective.

x = [ free coordinates of ParamMap(model) | b_0 .. b_{n_items-1} ].  Location is fixed by E[M0] = 0 (kt_trial's Theta has no
baseline mean), so all b_q are identified in the probit scale of the unit residual. The log-likelihood gradient in b is
    d ll / d b_q = - sum_{t: item(t) = q} wa_t / sqrt(D_t),
where wa_t is the per-observation adjoint of a_t = mu_t / sqrt(D_t) already formed in kt_trial.composite_likelihood.
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.stats import norm

from kt_trial.bvn import weighted_cell_loglik_obs
from kt_trial.composite_likelihood import P_FLOOR, PairCounts, _adjoint_gradient
from kt_trial.models import ParamMap
from kt_trial.moments import Theta, latent_moments
from kt_trial.schedule import Template

B_BOUNDS = (-4.0, 4.0)


def with_difficulties(templates: list[Template], ids: np.ndarray, b: np.ndarray) -> list[Template]:
    """Shallow copies of the templates whose difficulty vector is b[item id]."""
    out = []
    for g, t in enumerate(templates):
        d = copy.copy(t)
        d.b = np.asarray(b, float)[ids[g]]
        out.append(d)
    return out


class FreeParamMap:
    def __init__(self, model: str, K: int, n_items: int):
        self.base = ParamMap(model, K)
        self.model, self.K, self.nb, self.nt = model, K, n_items, self.base.n
        self.n = self.nt + n_items
        self.names = list(self.base.names) + [f"b[{q}]" for q in range(n_items)]
        self.lb = np.concatenate([self.base.lb, np.full(n_items, B_BOUNDS[0])])
        self.ub = np.concatenate([self.base.ub, np.full(n_items, B_BOUNDS[1])])

    def x_to_theta(self, x) -> Theta:
        return self.base.x_to_theta(np.asarray(x, float)[:self.nt])

    def theta_b_to_x(self, th: Theta, b) -> np.ndarray:
        return np.clip(np.concatenate([self.base.theta_to_x(th), np.asarray(b, float)]), self.lb, self.ub)

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


class FreeObjective:
    """Normalised negative composite log-likelihood (per learner-pair) in the free coordinates incl. difficulties."""

    def __init__(self, pm: FreeParamMap, templates: list[Template], pc: PairCounts, ids: np.ndarray):
        self.pm, self.templates, self.pc, self.ids = pm, templates, pc, ids
        self.scale = float(pc.counts.sum())
        self.n_eval = 0
        self.bad = 0

    def loglik_grad(self, x, grad=True):
        pm = self.pm
        x = np.asarray(x, float)
        th = pm.x_to_theta(x)
        tpls = with_difficulties(self.templates, self.ids, x[pm.nt:])
        G, T = len(tpls), tpls[0].T
        iu, ju = self.pc.iu, self.pc.ju
        a = np.empty((G, T)); rho = np.empty((G, len(iu))); moms = []
        for g, tpl in enumerate(tpls):
            mu, V = latent_moments(tpl, th)
            sd = np.sqrt(np.diag(V))
            a[g] = mu / sd
            rho[g] = V[iu, ju] / (sd[iu] * sd[ju])
            moms.append((mu, V))
        ll, w, nfl = weighted_cell_loglik_obs(a, iu, ju, rho, self.pc.counts, P_FLOOR, grad=grad)
        if not grad:
            return ll, None, None
        g_nat = 0.0
        g_b = np.zeros(pm.nb)
        for g, tpl in enumerate(tpls):
            wa = np.bincount(iu, weights=w[g, :, 0], minlength=T) + np.bincount(ju, weights=w[g, :, 1], minlength=T)
            g_nat = g_nat + _adjoint_gradient(th, tpl, moms[g][0], moms[g][1], wa, w[g, :, 2], iu, ju)
            sd = np.sqrt(np.diag(moms[g][1]))
            g_b -= np.bincount(self.ids[g], weights=wa / sd, minlength=pm.nb)
        return ll, g_nat, g_b

    def __call__(self, x):
        self.n_eval += 1
        try:
            ll, g_nat, g_b = self.loglik_grad(x)
        except (np.linalg.LinAlgError, FloatingPointError, ValueError):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        if not np.isfinite(ll) or not np.all(np.isfinite(g_nat)) or not np.all(np.isfinite(g_b)):
            self.bad += 1
            return 1e10, np.zeros(self.pm.n)
        J = self.pm.base.jacobian(np.asarray(x, float)[:self.pm.nt])
        g = np.concatenate([J.T @ g_nat, g_b])
        return -ll / self.scale, -g / self.scale

    def loglik(self, x):
        return self.loglik_grad(x, grad=False)[0]


def marginal_probabilities(pc: PairCounts) -> np.ndarray:
    """(G, T) observed success proportions per template position, from the pair counts (no raw data needed)."""
    G, P, _ = pc.counts.shape
    T = int(round((1 + np.sqrt(1 + 8 * P)) / 2))
    p = np.zeros((G, T))
    for g in range(G):
        n = pc.n_learners[g]
        if n == 0:
            p[g] = 0.5
            continue
        c = pc.counts[g]
        p[g, 0] = (c[0, 0] + c[0, 1]) / n                  # first position: pairs (0, t) are the first T-1 entries
        p[g, 1:] = (c[:T - 1, 0] + c[:T - 1, 2]) / n
    return p


def start_difficulties(templates, ids, pc, theta0: Theta, n_items: int) -> np.ndarray:
    """b_q start from the item's observed marginal proportion: b = E[mu without b] - Phi^-1(p) * E[sqrt(D)]."""
    p = np.clip(marginal_probabilities(pc), 1e-3, 1 - 1e-3)
    num = np.zeros(n_items); cnt = np.zeros(n_items)
    for g, t in enumerate(templates):
        t0 = copy.copy(t); t0.b = np.zeros(t.T)
        mu, V = latent_moments(t0, theta0)
        val = mu - norm.ppf(p[g]) * np.sqrt(np.diag(V))
        num += np.bincount(ids[g], weights=val, minlength=n_items)
        cnt += np.bincount(ids[g], minlength=n_items)
    return np.clip(num / np.maximum(cnt, 1), B_BOUNDS[0] + 0.01, B_BOUNDS[1] - 0.01)
