# Experiment 4, Stage 0: identifiability audit of the 2PL-type model (numbers only)

Analytic Jacobian/SVD of the observable map and design-based Godambe SEs (pairwise composite likelihood) at the Experiment-1 generating values with tau_F = 10. Coordinates: 18 model + 48 difficulties + 47 log-discrimination (geometric mean fixed at 1) = 113. Local identification at the tested points only. **No interpretation here: the gate review is Opus's (X4-D03).**

Provenance: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20}; threads {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}; score learners 20000; seed 20261001.

Scale invariance (lambda c, locations/c, variances/c^2): max |da| = 4.4e-16, max |drho| = 4.4e-16.

Consistency: with lambda == 1 and lambda fixed (66 coordinates) the SE of sigma2_F is 0.0221 / 0.0121 / 0.0070 at N = 300 / 1000 / 3000, identical to the Experiment-3 1PL-free audit (0.0221 / 0.0121 / 0.0070).

## Design SE of sigma2_F* (estimand sigma2_F* = g^2 sigma2_F)

| point | g | sigma2_F* | lambda fixed at truth (66) N=300 / 1000 / 3000 | lambda free (113) N=300 / 1000 / 3000 | free / fixed (N=1000) |
|---|---|---|---|---|---|
| lam1_tauF10 (lambda CV 0.00) | 1.0000 | 0.1600 | 0.0221 / 0.0121 / 0.0070 | 0.0223 / 0.0122 / 0.0070 | 1.01 |
| lamcv_tauF10 (lambda CV 0.27) | 0.9468 | 0.1434 | 0.0619 / 0.0339 / 0.0196 | 0.0208 / 0.0114 / 0.0066 | 0.34 |

## Rank, conditioning, weakest direction (lambda free, 113 parameters)

| point | numerical rank | cond. of weighted Jacobian | weakest rel. singular value | top loadings of the weakest direction | estimator correlation of sigma2_F (top) |
|---|---|---|---|---|---|
| lam1_tauF10 | 113/113 | 1.57e+03 | 6.37e-04 | tau_F -0.98, sigma2_F 0.07, b[3,11] 0.05 | tau_F -0.53, chol[3,3] 0.15, chol[2,2] 0.14 |
| lamcv_tauF10 | 113/113 | 1.72e+03 | 5.81e-04 | tau_F 0.96, b[0,0] 0.09, b[3,11] -0.08 | tau_F -0.54, chol[3,3] 0.17, chol[1,1] 0.16 |

## Design SE of the log-discriminations (lambda free)

| point | N=300 mean / max | N=1000 mean / max | N=3000 mean / max |
|---|---|---|---|
| lam1_tauF10 | 0.264 / 0.394 | 0.145 / 0.216 | 0.083 / 0.125 |
| lamcv_tauF10 | 0.280 / 0.398 | 0.153 / 0.218 | 0.089 / 0.126 |

## Robustness (other seeds and lambda draws, 40,000 score learners)

| seed | g | lambda CV | rank | cond. | lambda free SE N=300 / 1000 / 3000 | lambda fixed SE N=1000 |
|---|---|---|---|---|---|---|
| seed777 | 1.0145 | 0.28 | 113/113 | 1.62e+03 | 0.0234 / 0.0128 / 0.0074 | 0.0351 |
| seed778 | 0.9456 | 0.31 | 113/113 | 1.73e+03 | 0.0212 / 0.0116 / 0.0067 | 0.0348 |

## Gate numbers (X4-D03)

- lambda == 1: 2PL SE(sigma2_F*) at N = 1000 = 0.0122 (threshold 0.08); ratio to the lambda-fixed SE 1.01; rank-deficient: False
- lambda CV 0.3 draw: 2PL SE at N = 1000 = 0.0114; ratio to the lambda-fixed SE 0.34; rank-deficient: False

Coordinate names: the first 18 are the model parameters (8 scalars, 10 log-Cholesky), then b[skill,item], then loglam[skill,item] (log-discrimination).
