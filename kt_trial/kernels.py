"""Exposure-history kernels (identical definitions are used in simulation and fitting).

Exposure rule: only *practice* attempts are exposures. An attempt made at absolute time T_e is an
exposure for a response at T_t iff same skill, practice, and T_e < T_t strictly. Delayed probes are
never exposures. Clock is absolute minutes; session resets of F do not reset exposure history.

Slow kernel  (dimensionless "exposure-equivalents"):  H^s = sum_{j<n} (1-phi)^j = (1-(1-phi)^n)/phi,
    n = number of prior same-skill practice exposures, phi in (0,1). phi -> 0: raw count n;
    phi -> 1: 1{n >= 1}. Asymptote 1/phi.
Fast kernel  (dimensionless):  H^f = sum_{e in E_t} exp(-(T_t - T_e)/tau_R), tau_R in minutes.
"""
from __future__ import annotations

import numpy as np


def slow_kernel(n, phi):
    n = np.asarray(n, dtype=float)
    return -np.expm1(n * np.log1p(-phi)) / phi


def dslow_dphi(n, phi):
    n = np.asarray(n, dtype=float)
    return (n * (1.0 - phi) ** np.maximum(n - 1.0, 0.0) * phi - (1.0 - (1.0 - phi) ** n)) / phi ** 2


def fast_kernel(lag, expo, tau_R):
    """lag[t, e] = T_t - T_e (minutes); expo[t, e] bool mask of valid prior same-skill practice exposures."""
    return np.where(expo, np.exp(-np.where(expo, lag, 0.0) / tau_R), 0.0).sum(axis=-1)


def dfast_dtauR(lag, expo, tau_R):
    lg = np.where(expo, lag, 0.0)
    return np.where(expo, np.exp(-lg / tau_R) * lg / tau_R ** 2, 0.0).sum(axis=-1)
