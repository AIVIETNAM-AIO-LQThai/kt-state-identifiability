"""Nested models B0 < B1 < B2, their free-coordinate parameterisations, bounds and transforms.

B0: baseline mastery + slow exposure with learner-specific slow gain
    free: alpha_bar, logit(phi), sigma2_alpha, Sigma_M (log-Cholesky)                   -> 13 parameters
B1: B0 + fast recency with learner-specific gain
    adds: r_bar, log(tau_R), sigma2_r                                                    -> 16 parameters
B2: B1 + shared session-resetting OU transient state F
    adds: sigma2_F (variance coordinate, lower bound exactly 0), log(tau_F)              -> 18 parameters
Variances are optimised on the variance scale with a lower bound of exactly 0 so the null boundary
is representable (an sd-coordinate has zero gradient at 0). Inactive parameters are fixed at
INACTIVE values (their kernels are then irrelevant).
"""
from __future__ import annotations

import numpy as np

from .moments import N_SCALAR, SCALAR_NAMES, Theta, tril_idx

INACTIVE = {"r_bar": 0.0, "sigma2_r": 0.0, "tau_R": 1.0, "sigma2_F": 0.0, "tau_F": 1.0}
MODEL_FREE = {
    "B0": ["alpha_bar", "phi", "sigma2_alpha"],
    "B1": ["alpha_bar", "phi", "sigma2_alpha", "r_bar", "tau_R", "sigma2_r"],
    "B2": ["alpha_bar", "phi", "sigma2_alpha", "r_bar", "tau_R", "sigma2_r", "sigma2_F", "tau_F"],
}
# coordinate kind and bounds in coordinate space
_KIND = {"alpha_bar": ("id", -3.0, 3.0), "phi": ("logit", -6.0, 6.0), "sigma2_alpha": ("id", 0.0, 2.0),
         "r_bar": ("id", -5.0, 5.0), "tau_R": ("log", np.log(0.1), np.log(120.0)), "sigma2_r": ("id", 0.0, 2.0),
         "sigma2_F": ("id", 0.0, 3.0), "tau_F": ("log", np.log(0.05), np.log(1000.0))}
CHOL_DIAG_BOUNDS = (-4.0, 2.0)
CHOL_OFF_BOUNDS = (-3.0, 3.0)
VARIANCE_NAMES = {"sigma2_alpha", "sigma2_r", "sigma2_F"}


class ParamMap:
    def __init__(self, model: str, K: int):
        self.model, self.K = model, K
        self.scalars = MODEL_FREE[model]
        self.chol_idx = tril_idx(K)
        self.names = list(self.scalars) + [f"chol[{i},{j}]" for i, j in zip(*self.chol_idx)]
        lb, ub = [], []
        for n in self.scalars:
            lb.append(_KIND[n][1]); ub.append(_KIND[n][2])
        for i, j in zip(*self.chol_idx):
            b = CHOL_DIAG_BOUNDS if i == j else CHOL_OFF_BOUNDS
            lb.append(b[0]); ub.append(b[1])
        self.lb, self.ub = np.array(lb), np.array(ub)
        self.n = len(self.names)

    # -- x <-> Theta
    def _L(self, x):
        L = np.zeros((self.K, self.K))
        v = x[len(self.scalars):]
        r, c = self.chol_idx
        L[r, c] = v
        L[np.diag_indices(self.K)] = np.exp(np.diag(L))
        return L

    def x_to_theta(self, x) -> Theta:
        x = np.asarray(x, float)
        d = dict(INACTIVE)
        for n, xi in zip(self.scalars, x):
            kind = _KIND[n][0]
            d[n] = xi if kind == "id" else (np.exp(xi) if kind == "log" else 1.0 / (1.0 + np.exp(-xi)))
        L = self._L(x)
        return Theta(**{n: float(d[n]) for n in SCALAR_NAMES}, Sigma_M=L @ L.T)

    def theta_to_x(self, th: Theta) -> np.ndarray:
        x = []
        for n in self.scalars:
            v = getattr(th, n); kind = _KIND[n][0]
            x.append(v if kind == "id" else (np.log(v) if kind == "log" else np.log(v / (1.0 - v))))
        Lc = np.linalg.cholesky(th.Sigma_M)
        Lc[np.diag_indices(self.K)] = np.log(np.diag(Lc))
        r, c = self.chol_idx
        return np.clip(np.concatenate([x, Lc[r, c]]), self.lb, self.ub)

    def jacobian(self, x) -> np.ndarray:
        """dnat/dx, shape (Q, n)."""
        x = np.asarray(x, float)
        Q = N_SCALAR + self.K * (self.K + 1) // 2
        J = np.zeros((Q, self.n))
        for col, n in enumerate(self.scalars):
            kind = _KIND[n][0]
            row = SCALAR_NAMES.index(n)
            if kind == "id":
                J[row, col] = 1.0
            elif kind == "log":
                J[row, col] = np.exp(x[col])
            else:
                s = 1.0 / (1.0 + np.exp(-x[col])); J[row, col] = s * (1.0 - s)
        L = self._L(x)
        r, c = self.chol_idx
        off = len(self.scalars)
        for j, (i0, j0) in enumerate(zip(r, c)):
            dL = np.zeros((self.K, self.K))
            dL[i0, j0] = L[i0, j0] if i0 == j0 else 1.0
            dS = dL @ L.T + L @ dL.T
            J[N_SCALAR:, off + j] = dS[r, c]
        return J

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


def embed(th: Theta, model: str) -> Theta:
    """Restrict a Theta to a nested model by fixing inactive parameters."""
    d = th.copy()
    for n, v in INACTIVE.items():
        if n not in MODEL_FREE[model]:
            setattr(d, n, v)
    return d
