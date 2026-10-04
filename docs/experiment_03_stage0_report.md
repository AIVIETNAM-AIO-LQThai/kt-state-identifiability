# Experiment 3, Stage 0: identifiability audit with item difficulties known vs free (numbers only)

Analytic Jacobian/SVD of the observable map and design-based Godambe SEs of sigma2_F (pairwise composite likelihood), at the Experiment-1 generating values except tau_F. 48 item difficulties are the extra coordinates (66 free parameters instead of 18). Local identification at the tested points only. **No interpretation here: the gate review is Opus's (X3-D03).**

Provenance: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20}; threads {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}; score learners 20000; seed 20261001.

Consistency with the Experiment-1 audit (b known, tau_F = 10): SE(sigma2_F) here 0.0386 / 0.0211 (N = 300 / 1000) against 0.0385 / 0.0211 in Experiment 1.

## Design SE of sigma2_F

| tau_F (min) | b known N=300 | N=1000 | N=3000 | b free N=300 | N=1000 | N=3000 | free/known (N=1000) |
|---|---|---|---|---|---|---|---|
| 0.2 | 0.0419 | 0.0230 | 0.0133 | 3.8256 | 2.0954 | 1.2098 | 91.26 |
| 1 | 0.0418 | 0.0229 | 0.0132 | 0.1157 | 0.0634 | 0.0366 | 2.77 |
| 3 | 0.0410 | 0.0225 | 0.0130 | 0.0377 | 0.0207 | 0.0119 | 0.92 |
| 10 | 0.0386 | 0.0211 | 0.0122 | 0.0221 | 0.0121 | 0.0070 | 0.57 |
| 60 | 0.0357 | 0.0196 | 0.0113 | 0.0190 | 0.0104 | 0.0060 | 0.53 |

## Rank, conditioning and the white-noise scale ridge (b free, 66 parameters)

| tau_F | numerical rank | cond. of weighted Jacobian | weakest rel. singular value | ridge response (rel.) | cos(ridge, weakest 1/2/3) | top loadings of weakest direction |
|---|---|---|---|---|---|---|
| 0.2 | 66/66 | 9.78e+04 | 1.02e-05 | 6.64e-05 | 0.79, 0.62, 0.00 | tau_F 0.62, sigma2_F -0.33, b[3,11] -0.20 |
| 1 | 66/66 | 5.56e+03 | 1.80e-04 | 9.27e-04 | 0.39, 0.92, 0.07 | tau_F 0.92, sigma2_F -0.16, b[3,11] -0.10 |
| 3 | 66/66 | 2.43e+03 | 4.11e-04 | 2.11e-03 | 0.27, 0.91, 0.31 | tau_F -0.96, sigma2_F 0.11, b[3,11] 0.07 |
| 10 | 66/66 | 1.57e+03 | 6.37e-04 | 3.98e-03 | 0.19, 0.77, 0.58 | tau_F 0.98, sigma2_F -0.07, b[3,11] -0.05 |
| 60 | 66/66 | 2.86e+03 | 3.50e-04 | 6.74e-03 | 0.07, 0.69, 0.61 | tau_F -1.00, sigma2_F 0.03, b[3,11] 0.02 |

The ridge is exact only for white-noise F (tau_F -> 0); at larger tau_F the OU covariance breaks it (tested). b known: full rank 18/18 at all points; condition numbers 1.19e+04, 2.39e+03, 1.53e+03, 1.19e+03, 2.34e+03 (same order as tau_F listed above).

## Estimator correlation of sigma2_F (b free)

- tau_F 0.2: top correlated coordinates (index: correlation) {'17': 0.9993127199091553, '13': 0.9993090870586554, '10': 0.9992261510531504, '65': 0.9992152885900609}; H condition 7.25e+09
- tau_F 1: top correlated coordinates (index: correlation) {'7': -0.8905726645914736, '17': 0.6358882635152914, '13': 0.6234882416781387, '65': 0.6063793753944945}; H condition 2.26e+07
- tau_F 3: top correlated coordinates (index: correlation) {'7': -0.7205649515025253, '17': 0.26851180965767446, '13': 0.2642325979409312, '8': 0.2484367903045366}; H condition 4.31e+06
- tau_F 10: top correlated coordinates (index: correlation) {'7': -0.5281292860489636, '13': 0.17174423205943432, '10': 0.16379127495219353, '8': 0.1583767778960348}; H condition 1.75e+06
- tau_F 60: top correlated coordinates (index: correlation) {'7': -0.5547753732163445, '5': -0.27076806940426607, '2': -0.18181773633512002, '13': 0.1409563680826576}; H condition 5.79e+06

## Robustness (different seed 777, 40,000 score learners)

- tau_F 10.0: b known {'300': 0.03841348326893746, '1000': 0.021039931298744333, '3000': 0.012147409999061274}; b free {'300': 0.022180142279582257, '1000': 0.012148564255201258, '3000': 0.007013976843007912}
- tau_F 0.2: b known {'300': 0.04226406354253355, '1000': 0.023148980974077325, '3000': 0.01336507039684907}; b free {'300': 3.826154600168818, '1000': 2.0956711830146215, '3000': 1.2099363216464332}

## Gate numbers (X3-D03)

- design SE of sigma2_F, b free, tau_F = 10, N = 1000: 0.0121 (threshold 0.08)
- rank-deficient at tau_F = 10 with b free: False

Index map for coordinate indices above: 0-7 the eight scalar parameters (alpha_bar, phi, sigma2_alpha, r_bar, tau_R, sigma2_r, sigma2_F, tau_F), 8-17 log-Cholesky of Sigma_M, 18-65 the 48 difficulties b[skill,item].
