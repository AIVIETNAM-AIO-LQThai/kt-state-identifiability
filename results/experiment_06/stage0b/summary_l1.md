# Experiment 6 Stage 0b: population audit of the L1 arm (numbers only)

N_big = 200000, N_J = 6000; same datasets, 2PL fits and thresholds as Stage 0; B1-FB1 / B2-FB1 in place of the L0 arm.

## G0-3 (unchanged thresholds)

- **L1: NOT met**; checks {'E3_sigma2_F<=0.02': True, 'E3_E[T_FB](N=1000)<q95': False, 'E5_|sigma2_F-0.16|<=0.03': True, 'E1_|sigma2_F-0.16|<=0.01': True, 'E1_|kappa|<=0.02': True, 'E3_kappa_within_20pct': True, 'E5_kappa_within_20pct': True}
- values (L1): {'E1_sigma2_F': 0.1596747640007939, 'E3_sigma2_F': 0.008545020022026669, 'E5_sigma2_F': 0.1488512976296709, 'E1_kappa': -0.0001659789415325274, 'E3_kappa': -0.25220873128300525, 'E5_kappa': -0.2509115592003027, 'E3_E_T_FB_N1000': 27.880635757446292, 'q95_N1000': 5.159372954070556, 'E4_sigma2_F': 0.001448518611458473, 'E4_kappa': -0.09824177798325356}
- Stage-0 L0 for comparison: NOT met; values {'E1_sigma2_F': 0.15963632455101226, 'E3_sigma2_F': 0.02037353115344669, 'E5_sigma2_F': 0.20123013580865426, 'E1_kappa': -0.00024918398176737805, 'E3_kappa': -0.2615353974114596, 'E5_kappa': -0.2571963549679288, 'E3_E_T_FB_N1000': 29.019734020233155, 'q95_N1000': 5.159372954070556, 'E4_sigma2_F': 0.0, 'E4_kappa': -0.10061262630144115}

## Pseudo-true values, B2 arms: 2PL, L0 (Stage 0), L1

| cell | model | sigma2_F* | tau_F | kappa* | tau_D* | sigma2_r | tau_R | sd log lambda | E[T] N=1000 | converged | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | 2PL | 0.160 | 9.92 | NA | NA | 0.021 | 5.02 | 0.010 | 586.6 | True | |
| E1 | L0 | 0.160 | 9.90 | -0.000 | 50.00 | NA | 5.04 | NA | NA | True | boundary:tau_D@upper, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E1 | L1 | 0.160 | 9.90 | -0.000 | 20.11 | 0.021 | 5.03 | 0.010 | 579.9 | True | single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E2 | 2PL | 0.001 | 1.67 | NA | NA | 0.023 | 5.01 | 0.008 | 0.0 | True | |
| E2 | L0 | 0.000 | 0.50 | -0.000 | 10.00 | NA | 5.02 | NA | NA | True | hessian_not_pd, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E2 | L1 | 0.001 | 0.50 | -0.000 | 13.09 | 0.022 | 5.02 | 0.008 | 0.0 | True | hessian_not_pd, single_start_at_best, secondary_optima_present, tau_D_not_identified(kappa~0) |
| E3 | 2PL | 0.145 | 790.33 | NA | NA | 0.025 | 120.00 | 0.171 | 1352.0 | True | |
| E3 | L0 | 0.020 | 1000.00 | -0.262 | 10.97 | NA | 7.28 | NA | NA | True | boundary:tau_F@upper, secondary_optima_present |
| E3 | L1 | 0.009 | 1000.00 | -0.252 | 10.35 | 0.034 | 5.37 | 0.014 | 27.9 | True | boundary:tau_F@upper, secondary_optima_present |
| E4 | 2PL | 0.066 | 2.13 | NA | NA | 0.027 | 4.97 | 0.018 | 21.7 | True | |
| E4 | L0 | 0.000 | 1.99 | -0.101 | 2.01 | NA | 5.05 | NA | NA | True | boundary:sigma2_F@lower, tau_F_not_identified(sigma2_F=0) |
| E4 | L1 | 0.001 | 4.23 | -0.098 | 1.99 | 0.023 | 5.02 | 0.007 | 0.0 | True | single_start_at_best, secondary_optima_present |
| E5 | 2PL | 0.415 | 34.80 | NA | NA | 0.024 | 120.00 | 0.190 | 5716.2 | True | |
| E5 | L0 | 0.201 | 60.52 | -0.257 | 10.69 | NA | 6.96 | NA | NA | True |  |
| E5 | L1 | 0.149 | 15.38 | -0.251 | 10.30 | 0.035 | 5.40 | 0.014 | 2290.8 | True |  |

## Runtimes (s)

| cell | B2 (2PL) | B1-FB1 | B2-FB1 | B2-FB1 / B2 |
|---|---|---|---|---|
| E1 | 211 | 895 | 627 | 2.98 |
| E2 | 146 | 513 | 661 | 4.52 |
| E3 | 438 | 575 | 746 | 1.70 |
| E4 | 258 | 696 | 618 | 2.39 |
| E5 | 318 | 560 | 711 | 2.23 |

## Godambe SEs of the L1 fit (N = 300 / 1000; SE of tau_D on the log scale) against the 2PL (Stage 0)

| cell | model | SE sigma2_F | SE kappa | SE log tau_D | corr(sigma2_F, kappa) |
|---|---|---|---|---|---|
| E1 N=300 | 2PL | 0.0224 | NA | NA | NA |
| E1 N=300 | L1 | 0.0245 | 0.0129 | NA | 0.41 |
| E1 N=1000 | 2PL | 0.0123 | NA | NA | NA |
| E1 N=1000 | L1 | 0.0134 | 0.0071 | NA | 0.41 |
| E2 N=300 | 2PL | 0.0292 | NA | NA | NA |
| E2 N=300 | L1 | 0.0359 | 0.0161 | NA | 0.23 |
| E2 N=1000 | 2PL | 0.0160 | NA | NA | NA |
| E2 N=1000 | L1 | 0.0197 | 0.0088 | NA | 0.23 |
| E3 N=300 | 2PL | 0.0259 | NA | NA | NA |
| E3 N=300 | L1 | 0.0104 | 0.0260 | 0.1161 | 0.51 |
| E3 N=1000 | 2PL | 0.0142 | NA | NA | NA |
| E3 N=1000 | L1 | 0.0057 | 0.0143 | 0.0636 | 0.51 |
| E4 N=300 | 2PL | 0.0478 | NA | NA | NA |
| E4 N=300 | L1 | 0.0308 | 0.0858 | 0.9112 | 0.58 |
| E4 N=1000 | 2PL | 0.0262 | NA | NA | NA |
| E4 N=1000 | L1 | 0.0169 | 0.0470 | 0.4991 | 0.58 |
| E5 N=300 | 2PL | 0.0441 | NA | NA | NA |
| E5 N=300 | L1 | 0.0480 | 0.0262 | 0.1281 | 0.52 |
| E5 N=1000 | 2PL | 0.0242 | NA | NA | NA |
| E5 N=1000 | L1 | 0.0263 | 0.0144 | 0.0702 | 0.52 |
