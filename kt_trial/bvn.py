"""Vectorised bivariate normal probabilities with analytic derivatives.

Phi2(a,b;rho) = Phi(a)Phi(b) + int_0^rho phi2(a,b;r) dr. With r = sin(theta) the integrand
exp(-(a^2 - 2 a b sin(theta) + b^2)/(2 cos^2 theta))/(2 pi) is smooth on [0, asin(rho)], so a fixed
Gauss-Legendre rule is accurate for |rho| well below 1 (validated against scipy in the tests).
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

# Tiered Gauss-Legendre rules: (max |rho|, nodes). Errors vs scipy < 1e-13 in each tier (see tests).
_TIERS = [(0.5, 8), (0.7, 12), (0.9, 24), (0.9995, 48)]
_RULES = {n: np.polynomial.legendre.leggauss(n) for _, n in _TIERS}
RHO_MAX = 0.9995
_INV_SQRT_2PI = 1.0 / np.sqrt(2.0 * np.pi)


def _pdf(x):
    return _INV_SQRT_2PI * np.exp(-0.5 * x * x)


def _integral(a, b, rho, nodes):
    x, w = _RULES[nodes]
    half = 0.5 * np.arcsin(rho)
    th = half[..., None] * (x + 1.0)                       # nodes on [0, asin rho]
    ex = np.exp(-(a[..., None] ** 2 - 2.0 * a[..., None] * b[..., None] * np.sin(th) + b[..., None] ** 2)
                / (2.0 * np.cos(th) ** 2))
    return half * (ex @ w) / (2.0 * np.pi)                 # int_0^{asin rho} f dtheta / (2 pi)


def bvn_cdf(a, b, rho):
    a, b, rho = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float), np.asarray(rho, float))
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    out = np.empty(a.shape)
    lo = 0.0
    todo = np.ones(a.shape, bool)
    for hi, n in _TIERS:
        m = todo & (np.abs(rho) <= hi)
        if m.any():
            out[m] = _integral(a[m], b[m], rho[m], n)
        todo &= ~m
    return ndtr(a) * ndtr(b) + out


def bvn_pdf(a, b, rho):
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    s2 = 1.0 - rho * rho
    return np.exp(-(a * a - 2.0 * rho * a * b + b * b) / (2.0 * s2)) / (2.0 * np.pi * np.sqrt(s2))


def cell_probs_and_grads(a, b, rho):
    """Return p (...,4) and dp (...,4,3) for cells (11,10,01,00), derivatives w.r.t. (a, b, rho)."""
    a, b, rho = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float), np.asarray(rho, float))
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    s = np.sqrt(1.0 - rho * rho)
    p11 = bvn_cdf(a, b, rho)
    Pa, Pb = ndtr(a), ndtr(b)
    d11 = np.stack([_pdf(a) * ndtr((b - rho * a) / s), _pdf(b) * ndtr((a - rho * b) / s), bvn_pdf(a, b, rho)], -1)
    da = np.stack([_pdf(a), np.zeros_like(a), np.zeros_like(a)], -1)
    db = np.stack([np.zeros_like(b), _pdf(b), np.zeros_like(b)], -1)
    p = np.stack([p11, Pa - p11, Pb - p11, 1.0 - Pa - Pb + p11], -1)
    dp = np.stack([d11, da - d11, db - d11, d11 - da - db], -2)
    return p, dp


def weighted_cell_loglik(a, b, rho, counts, p_floor=1e-300, grad=True):
    """sum_c counts_c log p_c and its gradient weights w.r.t. (a, b, rho), without forming dp explicitly.

    With r_c = n_c / p_c and Delta = r11 - r10 - r01 + r00 (cells 11,10,01,00):
        w_a = d11_a Delta + phi(a)(r10 - r00),  w_b = d11_b Delta + phi(b)(r01 - r00),  w_rho = d11_rho Delta.
    Returns (ll, w or None, n_floored_cells).
    """
    rho = np.clip(rho, -RHO_MAX, RHO_MAX)
    p11 = bvn_cdf(a, b, rho)
    Pa, Pb = ndtr(a), ndtr(b)
    p = np.stack([p11, Pa - p11, Pb - p11, 1.0 - Pa - Pb + p11], -1)
    nf = int(((p < p_floor) & (counts > 0)).sum())
    pf = np.maximum(p, p_floor)
    ll = float(np.sum(np.where(counts > 0, counts * np.log(pf), 0.0)))
    if not grad:
        return ll, None, nf
    r = counts / pf
    delta = r[..., 0] - r[..., 1] - r[..., 2] + r[..., 3]
    s = np.sqrt(1.0 - rho * rho)
    w = np.stack([_pdf(a) * ndtr((b - rho * a) / s) * delta + _pdf(a) * (r[..., 1] - r[..., 3]),
                  _pdf(b) * ndtr((a - rho * b) / s) * delta + _pdf(b) * (r[..., 2] - r[..., 3]),
                  bvn_pdf(a, b, rho) * delta], -1)
    return ll, w, nf
