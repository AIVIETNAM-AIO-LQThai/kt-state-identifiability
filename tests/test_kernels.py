import numpy as np

from kt_trial.kernels import dfast_dtauR, dslow_dphi, fast_kernel, slow_kernel


def test_slow_limits_and_values():
    n = np.arange(0, 30)
    assert np.allclose(slow_kernel(n, 1e-8), n, atol=1e-5)               # phi->0: raw count
    assert np.allclose(slow_kernel(n, 1 - 1e-12), (n >= 1).astype(float))  # phi->1: indicator
    assert slow_kernel(0, 0.2) == 0.0 and np.isclose(slow_kernel(1, 0.2), 1.0)
    assert np.isclose(slow_kernel(2, 0.2), 1.8) and np.isclose(slow_kernel(400, 0.2), 5.0)
    assert np.all(np.diff(slow_kernel(n, 0.2)) > 0)


def test_slow_derivative_fd():
    n = np.array([0, 1, 3, 10, 24]); h = 1e-6
    fd = (slow_kernel(n, 0.2 + h) - slow_kernel(n, 0.2 - h)) / (2 * h)
    assert np.allclose(dslow_dphi(n, 0.2), fd, atol=1e-7)


def test_fast_kernel():
    lag = np.array([[0.0, 5.0, 10.0]]); expo = np.array([[False, True, True]])
    assert np.isclose(fast_kernel(lag, expo, 5.0)[0], np.exp(-1) + np.exp(-2))
    assert fast_kernel(lag, expo, 1e-6)[0] < 1e-12                         # tau_R -> 0
    assert np.isclose(fast_kernel(lag, expo, 1e9)[0], 2.0, atol=1e-6)      # tau_R -> inf: exposure count
    assert fast_kernel(lag, np.zeros_like(expo), 5.0)[0] == 0.0
    h = 1e-6
    fd = (fast_kernel(lag, expo, 5 + h) - fast_kernel(lag, expo, 5 - h)) / (2 * h)
    assert np.allclose(dfast_dtauR(lag, expo, 5.0), fd, atol=1e-8)
