# Experiment 6 Stage 0: population audit (numbers only)

Sonnet 5.5, 2026-10-11. Config `configs/experiment_06/stage0.yaml` (seed 20266001), results `results/experiment_06/stage0/` (`summary.json`, `summary.md`, `points/E1..E5.json`).
Code: `feedback_model/` (`fbmodel.py`, `etamodel.py`, `fit.py`, `audit.py`, `cli.py`), tests `tests/test_feedback_model.py`. `.venv12`, single-thread BLAS, 5 workers, 1.7 CPU-h in total (cells 924–1,363 s, 23 min wall).

## Gate summary (X6-D04)
| gate | result |
|---|---|
| **G0-1 implementation** | met: kappa = 0 equals the 2PL objective (difference 0) and gradient (<= 1e-12); analytic gradient against central differences, relative error <= 1e-6 at B2 and B1 (all coordinates tested incl. kappa and log tau_D); cells sum to 1 within 1e-12 and are positive; B2+eta gradient checked; full suite: 166 passed with X3-F06 deselected (incl. the 7 new tests). Approximation check below: exact in E1/E2 (chi2/df 0.95–1.0), nearly exact for E4 (1.3–1.4), **not exact for E3/E5 (95–160)** |
| **G0-2 B2+eta (descriptive)** | sigma2_F* stays 0.143 (E3) and 0.408 (E5): the schedule term does not remove the misattribution (prediction of protocol 1.2 confirmed) |
| **G0-3 FB at population level** | **NOT met** (3 of 7 checks fail): E3 sigma2_F* = 0.0204 (limit 0.02); E3 expected T_FB at N = 1000 = 29.0 (limit 5.16, the 2PL null q95, a coarse reference only); E5 sigma2_F* = 0.201, i.e. |error| = 0.041 (limit 0.03). Passed: E1 sigma2_F* 0.1596 and kappa* -0.0002; kappa* -0.262 (E3) and -0.257 (E5) within 20 % of -0.25 |
| **G0-4 identifiability and sizes** | numbers below (Godambe SEs, runtimes) |

Reading of the numbers (descriptive, Opus decides): the FB model removes 86 % of the E3 misattribution (sigma2_F* 0.145 -> 0.020) and 84 % of the E5 bias (+0.255 -> +0.041), recovers kappa* and tau_D* (-0.262 / 10.97 in E3, -0.257 / 10.69 in E5; truth -0.25 / 10), and is exact for the weak cell E4 (sigma2_F* 0, kappa* -0.1006, tau_D* 2.01). In E3 a small session-level component survives (sigma2_F* 0.020 with tau_F-hat at its bound 1000; expected T_FB 8.7 / 29.0 at N = 300 / 1000). The approximation check locates the defect: L0 marginal success rates of later practice positions are off by 0.017 on average in E3/E5 (rms z 8.4), against 0.195 without a feedback term; the neglected term is the covariance between earlier errors and the latent state, which is first order in kappa (the protocol, 1.3 (d), called it second order). A smoke fit at N = 1000 (E3-type data, one dataset, 3 starts) gave kappa-hat -0.258, tau_D-hat 10.5, sigma2_F-hat 0 (T_FB = 0, 2PL T = 1,345).

N_big = 200000, N_J = 6000; fits 2PL B1/B2, B2+eta (tau_x = 2), B1-FB/B2-FB (L0); tolerances scaled x100.

Null reference (Experiment 4 V2 2PL T*): {'300': {'n': 50, 'q95': 4.231829816219397}, '1000': {'n': 49, 'q95': 5.159372954070556}}

## Pseudo-true values (B2 arms)

| cell | model | sigma2_F* | tau_F | kappa* | tau_D* | eta* | E[T] N=300 (x q95) | E[T] N=1000 (x q95) | converged | flags |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 2PL | 0.160 | 9.92 | NA | NA | NA | 175.99 (41.59) | 586.64 (113.70) | True |  |
| E1 | 2PL+eta | 0.160 | 9.92 | NA | NA | -0.001 | NA | NA | True |  |
| E1 | FB | 0.160 | 9.90 | -0.000 | 50.00 | NA | 172.92 (40.86) | 576.42 (111.72) | True | boundary:tau_D@upper, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E2 | 2PL | 0.001 | 1.67 | NA | NA | NA | 0.00 (0.00) | 0.00 (0.00) | True | single_start_at_best |
| E2 | 2PL+eta | 0.001 | 1.65 | NA | NA | -0.003 | NA | NA | True | single_start_at_best |
| E2 | FB | 0.000 | 0.50 | -0.000 | 10.00 | NA | 0.00 (0.00) | 0.00 (0.00) | True | hessian_not_pd, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E3 | 2PL | 0.145 | 790.33 | NA | NA | NA | 405.60 (95.85) | 1352.01 (262.05) | True | boundary:tau_R@upper |
| E3 | 2PL+eta | 0.143 | 1000.00 | NA | NA | -0.273 | NA | NA | True | boundary:tau_R@upper, boundary:tau_F@upper |
| E3 | FB | 0.020 | 1000.00 | -0.262 | 10.97 | NA | 8.71 (2.06) | 29.02 (5.62) | True | boundary:tau_F@upper, secondary_optima_present |
| E4 | 2PL | 0.066 | 2.13 | NA | NA | NA | 6.52 (1.54) | 21.72 (4.21) | True |  |
| E4 | 2PL+eta | 0.066 | 2.12 | NA | NA | -0.089 | NA | NA | True |  |
| E4 | FB | 0.000 | 1.99 | -0.101 | 2.01 | NA | 0.00 (0.00) | 0.00 (0.00) | True | boundary:sigma2_F@lower, tau_F_not_identified(sigma2_F=0) |
| E5 | 2PL | 0.415 | 34.80 | NA | NA | NA | 1714.87 (405.23) | 5716.24 (1107.93) | True | boundary:tau_R@upper |
| E5 | 2PL+eta | 0.408 | 35.82 | NA | NA | -0.274 | NA | NA | True | boundary:tau_R@upper |
| E5 | FB | 0.201 | 60.52 | -0.257 | 10.69 | NA | 596.59 (140.98) | 1988.63 (385.44) | True |  |

## Approximation check at the true parameters: chi2/df per pair (1 = exact model)

| cell | group | L0 | no feedback term | n pairs | L0 mean KL x1e4 | no-fb mean KL x1e4 |
|---|---|---|---|---|---|---|
| E1 | fb_active | 0.97 | 0.97 | 11904 | 0.58 | 0.58 |
| E1 | within_session_other | 1.00 | 1.00 | 960 | 0.60 | 0.60 |
| E1 | cross_session | 0.97 | 0.97 | 36864 | 0.58 | 0.58 |
| E1 | fb_active_lag[0,1) | 0.90 | 0.90 | 430 | 0.54 | 0.54 |
| E1 | fb_active_lag[1,2) | 0.99 | 0.99 | 709 | 0.59 | 0.59 |
| E1 | fb_active_lag[2,5) | 0.99 | 0.99 | 2015 | 0.59 | 0.59 |
| E1 | fb_active_lag[5,10) | 0.96 | 0.96 | 2844 | 0.58 | 0.58 |
| E1 | fb_active_lag[10,20) | 0.97 | 0.97 | 3984 | 0.58 | 0.58 |
| E1 | fb_active_lag[20,1e+09) | 0.98 | 0.98 | 1922 | 0.59 | 0.59 |
| E2 | fb_active | 0.95 | 0.95 | 11904 | 0.57 | 0.57 |
| E2 | within_session_other | 1.04 | 1.04 | 960 | 0.63 | 0.63 |
| E2 | cross_session | 0.97 | 0.97 | 36864 | 0.58 | 0.58 |
| E2 | fb_active_lag[0,1) | 0.96 | 0.96 | 430 | 0.58 | 0.58 |
| E2 | fb_active_lag[1,2) | 0.95 | 0.95 | 709 | 0.57 | 0.57 |
| E2 | fb_active_lag[2,5) | 0.95 | 0.95 | 2015 | 0.57 | 0.57 |
| E2 | fb_active_lag[5,10) | 0.94 | 0.94 | 2844 | 0.57 | 0.57 |
| E2 | fb_active_lag[10,20) | 0.95 | 0.95 | 3984 | 0.57 | 0.57 |
| E2 | fb_active_lag[20,1e+09) | 0.96 | 0.96 | 1922 | 0.57 | 0.57 |
| E3 | fb_active | 156.59 | 5628.14 | 11904 | 88.90 | 2168.11 |
| E3 | within_session_other | 0.98 | 0.98 | 960 | 0.59 | 0.59 |
| E3 | cross_session | 115.71 | 4306.35 | 36864 | 65.72 | 1799.13 |
| E3 | fb_active_lag[0,1) | 143.74 | 6461.57 | 430 | 80.86 | 2238.52 |
| E3 | fb_active_lag[1,2) | 149.68 | 6388.38 | 709 | 84.74 | 2243.02 |
| E3 | fb_active_lag[2,5) | 155.25 | 6118.62 | 2015 | 87.77 | 2200.86 |
| E3 | fb_active_lag[5,10) | 169.89 | 6006.87 | 2844 | 96.32 | 2228.13 |
| E3 | fb_active_lag[10,20) | 166.45 | 5447.32 | 3984 | 94.69 | 2179.94 |
| E3 | fb_active_lag[20,1e+09) | 123.32 | 4461.42 | 1922 | 70.45 | 1977.02 |
| E4 | fb_active | 1.40 | 14.65 | 11904 | 0.83 | 8.61 |
| E4 | within_session_other | 0.92 | 0.92 | 960 | 0.55 | 0.55 |
| E4 | cross_session | 1.33 | 12.23 | 36864 | 0.80 | 7.21 |
| E4 | fb_active_lag[0,1) | 1.29 | 19.67 | 430 | 0.77 | 11.39 |
| E4 | fb_active_lag[1,2) | 1.28 | 17.17 | 709 | 0.77 | 9.99 |
| E4 | fb_active_lag[2,5) | 1.38 | 15.72 | 2015 | 0.83 | 9.21 |
| E4 | fb_active_lag[5,10) | 1.47 | 14.95 | 2844 | 0.88 | 8.79 |
| E4 | fb_active_lag[10,20) | 1.39 | 13.98 | 3984 | 0.83 | 8.23 |
| E4 | fb_active_lag[20,1e+09) | 1.37 | 12.44 | 1922 | 0.82 | 7.34 |
| E5 | fb_active | 159.57 | 4968.13 | 11904 | 91.01 | 1990.16 |
| E5 | within_session_other | 1.08 | 1.08 | 960 | 0.65 | 0.65 |
| E5 | cross_session | 94.88 | 3836.94 | 36864 | 53.87 | 1658.84 |
| E5 | fb_active_lag[0,1) | 144.59 | 5436.92 | 430 | 82.07 | 2010.54 |
| E5 | fb_active_lag[1,2) | 152.64 | 5432.36 | 709 | 87.11 | 2024.32 |
| E5 | fb_active_lag[2,5) | 160.35 | 5289.04 | 2015 | 91.39 | 2001.31 |
| E5 | fb_active_lag[5,10) | 176.73 | 5294.84 | 2844 | 100.77 | 2045.63 |
| E5 | fb_active_lag[10,20) | 169.03 | 4892.64 | 3984 | 96.38 | 2015.56 |
| E5 | fb_active_lag[20,1e+09) | 119.68 | 4028.61 | 1922 | 68.46 | 1826.57 |

## Marginal check at the true parameters: empirical position success rate against the model Phi(a_t) (mean |error|; rms z)

| cell | session starts (L0) | practice, later in session (L0) | probes (L0) | practice, later in session (no feedback term) |
|---|---|---|---|---|
| E1 | 0.0017; z 0.8 | 0.0021; z 1.0 | 0.0023; z 1.0 | 0.0021; z 1.0 |
| E2 | 0.0023; z 0.9 | 0.0021; z 1.0 | 0.0022; z 1.0 | 0.0021; z 1.0 |
| E3 | 0.0017; z 0.7 | 0.0171; z 8.4 | 0.0020; z 1.0 | 0.1950; z 83.9 |
| E4 | 0.0020; z 1.0 | 0.0023; z 1.1 | 0.0022; z 0.9 | 0.0116; z 4.7 |
| E5 | 0.0026; z 1.1 | 0.0177; z 8.5 | 0.0024; z 1.0 | 0.1892; z 80.0 |

## Fit runtimes (s, N_big pair counts; 5 starts) and health

| cell | B1 | B2 | B2+eta | B1-FB | B2-FB | B2-FB / B2 | B2-FB flags |
|---|---|---|---|---|---|---|---|
| E1 | 129 | 177 | 181 | 406 | 397 | 2.23 | boundary:tau_D@upper, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E2 | 131 | 119 | 127 | 249 | 266 | 2.24 | hessian_not_pd, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E3 | 190 | 363 | 329 | 219 | 235 | 0.65 | boundary:tau_F@upper, secondary_optima_present |
| E4 | 136 | 217 | 224 | 310 | 265 | 1.22 | boundary:sigma2_F@lower, tau_F_not_identified(sigma2_F=0) |
| E5 | 183 | 265 | 247 | 218 | 299 | 1.13 |  |

## Godambe SEs (asymptotic, at N = 300 / 1000; SE of tau_D is on the log scale; NA = coordinate inactive at the fit)

| cell | model | SE sigma2_F | SE kappa | SE log tau_D | corr(sigma2_F, kappa) |
|---|---|---|---|---|---|
| E1 N=300 | 2PL | 0.0224 | NA | NA | NA |
| E1 N=1000 | 2PL | 0.0123 | NA | NA | NA |
| E1 N=300 | FB | 0.0233 | 0.0095 | NA | 0.27 |
| E1 N=1000 | FB | 0.0128 | 0.0052 | NA | 0.27 |
| E2 N=300 | 2PL | 0.0292 | NA | NA | NA |
| E2 N=1000 | 2PL | 0.0160 | NA | NA | NA |
| E2 N=300 | FB | 0.0028 | 0.0206 | NA | -0.34 |
| E2 N=1000 | FB | 0.0015 | 0.0113 | NA | -0.34 |
| E3 N=300 | 2PL | 0.0259 | NA | NA | NA |
| E3 N=1000 | 2PL | 0.0142 | NA | NA | NA |
| E3 N=300 | FB | 0.0197 | 0.0279 | 0.1396 | 0.09 |
| E3 N=1000 | FB | 0.0108 | 0.0153 | 0.0764 | 0.09 |
| E4 N=300 | 2PL | 0.0478 | NA | NA | NA |
| E4 N=1000 | 2PL | 0.0262 | NA | NA | NA |
| E4 N=300 | FB | NA | 0.0919 | 0.9651 | NA |
| E4 N=1000 | FB | NA | 0.0504 | 0.5286 | NA |
| E5 N=300 | 2PL | 0.0441 | NA | NA | NA |
| E5 N=1000 | 2PL | 0.0242 | NA | NA | NA |
| E5 N=300 | FB | 0.0428 | 0.0282 | 0.1434 | 0.31 |
| E5 N=1000 | FB | 0.0235 | 0.0155 | 0.0786 | 0.31 |

## G0-2: {'E3_sigma2_F_eta': 0.14304272138496424, 'E5_sigma2_F_eta': 0.4081974603199152, 'cheap_route_works': False}

## G0-3: {'values': {'E1_sigma2_F': 0.15963632455101226, 'E3_sigma2_F': 0.02037353115344669, 'E5_sigma2_F': 0.20123013580865426, 'E1_kappa': -0.00024918398176737805, 'E3_kappa': -0.2615353974114596, 'E5_kappa': -0.2571963549679288, 'E3_E_T_FB_N1000': 29.019734020233155, 'q95_N1000': 5.159372954070556, 'E4_sigma2_F': 0.0, 'E4_kappa': -0.10061262630144115}, 'checks': {'E3_sigma2_F<=0.02': False, 'E3_E[T_FB](N=1000)<q95': False, 'E5_|sigma2_F-0.16|<=0.03': False, 'E1_|sigma2_F-0.16|<=0.01': True, 'E1_|kappa|<=0.02': True, 'E3_kappa_within_20pct': True, 'E5_kappa_within_20pct': True}, 'all_pass': False}
