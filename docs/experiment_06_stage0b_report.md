# Experiment 6, Stage 0b: the L1 approximation (numbers only)

Produced by `python -m feedback_model approx` (Step 1) and `python -m feedback_model audit_l1` (Step 2) with `configs/experiment_06/stage0.yaml`
(seed 20266001, N_big = 200,000, N_J = 6,000). Raw results: `results/experiment_06/stage0b/` (`points/`, `approx.json`, `points_l1/`,
`summary_l1.json`). The datasets, the 2PL fits and all thresholds are those of Stage 0 (`docs/experiment_06_stage0_report.md`). F is a statistical
component. Interpretation belongs to the Opus review.

**Gate summary**
- G0-1b (Step 1, X6-D07): **passed**, in E3 and E5 (excess chi2/df ratios L1/L0 0.014-0.023 against the limit 0.25; later-practice marginal error 0.0040 against 0.0085).
- G0-3 (Step 2, unchanged thresholds): **not met, 6 of 7 checks pass**. The failing check is E3 E[T_FB] at N = 1000: 27.9 against the reference 5.16.
  E3 sigma2_F* 0.0085 (limit 0.02), E5 sigma2_F* 0.149 (|error| 0.011, limit 0.03), E1 sigma2_F* 0.1597 and kappa* -0.0002, kappa* -0.252 (E3) and -0.251 (E5), all pass.
- G0-4 (sizes): in the tables below.

**Reduction of the 2PL misattribution of sigma2_F (pseudo-true values, B2 arms)**

| cell | truth | 2PL | L0 (Stage 0) | L1 |
|---|---|---|---|---|
| E3 | 0 | 0.145 | 0.0204 | 0.0085 |
| E5 | 0.16 | 0.415 | 0.2012 | 0.1489 |
| E4 | 0 | 0.066 | 0.000 | 0.0014 |
| E1 | 0.16 | 0.160 | 0.1596 | 0.1597 |

Learner-level footprint in E3 / E5 (truth sigma2_r 0.0225, tau_R 5, sd log lambda 0): L0 sigma2_r 0.16-0.19, tau_R 7.28 / 6.96, sd log lambda 0.07-0.08 (X6-F07);
L1 sigma2_r 0.034 / 0.035, tau_R 5.37 / 5.40, sd log lambda 0.014 / 0.014.

**G0-1b: PASSED** (complete: True). Rule: in E3 and E5, excess chi2/df of L1 <= 1/4 of L0's on the feedback-active and cross-session pairs, later-practice marginal error <= 0.0085; E1/E2 unchanged; E4 no worse than L0 (strict).

### Step 1: chi2/df per pair (expected 1 for an exact model)

| cell | model | fb_active | within_session_other | cross_session |
|---|---|---|---|---|
| E1 | no_feedback_term | 0.972 | 0.995 | 0.975 |
| E1 | L0 | 0.972 | 0.995 | 0.975 |
| E1 | L1 | 0.972 | 0.995 | 0.975 |
| E2 | no_feedback_term | 0.948 | 1.044 | 0.970 |
| E2 | L0 | 0.948 | 1.044 | 0.970 |
| E2 | L1 | 0.948 | 1.044 | 0.970 |
| E3 | no_feedback_term | 5628.140 | 0.976 | 4306.345 |
| E3 | L0 | 156.593 | 0.976 | 115.713 |
| E3 | L1 | 4.157 | 0.976 | 2.618 |
| E4 | no_feedback_term | 14.653 | 0.918 | 12.233 |
| E4 | L0 | 1.396 | 0.918 | 1.333 |
| E4 | L1 | 0.950 | 0.918 | 0.948 |
| E5 | no_feedback_term | 4968.130 | 1.076 | 3836.938 |
| E5 | L0 | 159.575 | 1.076 | 94.879 |
| E5 | L1 | 4.578 | 1.076 | 2.542 |

### Marginal success-rate error by position category (mean |empirical - model|; RMS z)

| cell | model | later practice | session start | probe |
|---|---|---|---|---|
| E1 | L0 | 0.0021; 1.0 | 0.0017; 0.8 | 0.0023; 1.0 |
| E1 | L1 | 0.0021; 1.0 | 0.0017; 0.8 | 0.0023; 1.0 |
| E2 | L0 | 0.0021; 1.0 | 0.0023; 0.9 | 0.0022; 1.0 |
| E2 | L1 | 0.0021; 1.0 | 0.0023; 0.9 | 0.0022; 1.0 |
| E3 | L0 | 0.0171; 8.4 | 0.0017; 0.7 | 0.0020; 1.0 |
| E3 | L1 | 0.0040; 1.7 | 0.0017; 0.7 | 0.0020; 1.0 |
| E4 | L0 | 0.0023; 1.1 | 0.0020; 1.0 | 0.0022; 0.9 |
| E4 | L1 | 0.0021; 1.0 | 0.0020; 1.0 | 0.0022; 0.9 |
| E5 | L0 | 0.0177; 8.5 | 0.0026; 1.1 | 0.0024; 1.0 |
| E5 | L1 | 0.0040; 1.7 | 0.0026; 1.1 | 0.0024; 1.0 |

### Gate evaluation

- **E3**: excess_fb_active: {'L0': 155.59250691289176, 'L1': 3.1573406032085325, 'ratio': 0.020292369252564103, 'ok': True}; excess_cross_session: {'L0': 114.71318795112178, 'L1': 1.6176290117820842, 'ratio': 0.014101508646689697, 'ok': True}; marginal_later_practice: {'L0': 0.017148940444896562, 'L1': 0.003973941161223086, 'limit': 0.0085, 'ok': True}
- **E5**: excess_fb_active: {'L0': 158.5749561442216, 'L1': 3.578472508470009, 'ratio': 0.022566441735070955, 'ok': True}; excess_cross_session: {'L0': 93.87945057329655, 'L1': 1.5422431257005123, 'ratio': 0.016427909582794192, 'ok': True}; marginal_later_practice: {'L0': 0.017714764544769307, 'L1': 0.003963561081087083, 'limit': 0.0085, 'ok': True}
- **E1**: max_abs_change_chi2_per_df: 0.0; ok: True
- **E2**: max_abs_change_chi2_per_df: 0.0; ok: True
- **E4**: L1_minus_L0: {'fb_active': -0.4462369128572641, 'within_session_other': 0.0, 'cross_session': -0.3849072465779837}; ok: True

Stage-0 L0 numbers reproduced by the regenerated datasets (max |diff| of chi2/df): {'E1': 0.0, 'E2': 0.0, 'E3': 0.0, 'E4': 0.0, 'E5': 0.0}

---

N_big = 200000, N_J = 6000; same datasets, 2PL fits and thresholds as Stage 0; B1-FB1 / B2-FB1 in place of the L0 arm.

### G0-3 (unchanged thresholds)

- **L1: NOT met**; checks {'E3_sigma2_F<=0.02': True, 'E3_E[T_FB](N=1000)<q95': False, 'E5_|sigma2_F-0.16|<=0.03': True, 'E1_|sigma2_F-0.16|<=0.01': True, 'E1_|kappa|<=0.02': True, 'E3_kappa_within_20pct': True, 'E5_kappa_within_20pct': True}
- values (L1): {'E1_sigma2_F': 0.1596747640007939, 'E3_sigma2_F': 0.008545020022026669, 'E5_sigma2_F': 0.1488512976296709, 'E1_kappa': -0.0001659789415325274, 'E3_kappa': -0.25220873128300525, 'E5_kappa': -0.2509115592003027, 'E3_E_T_FB_N1000': 27.880635757446292, 'q95_N1000': 5.159372954070556, 'E4_sigma2_F': 0.001448518611458473, 'E4_kappa': -0.09824177798325356}
- Stage-0 L0 for comparison: NOT met; values {'E1_sigma2_F': 0.15963632455101226, 'E3_sigma2_F': 0.02037353115344669, 'E5_sigma2_F': 0.20123013580865426, 'E1_kappa': -0.00024918398176737805, 'E3_kappa': -0.2615353974114596, 'E5_kappa': -0.2571963549679288, 'E3_E_T_FB_N1000': 29.019734020233155, 'q95_N1000': 5.159372954070556, 'E4_sigma2_F': 0.0, 'E4_kappa': -0.10061262630144115}

### Pseudo-true values, B2 arms: 2PL, L0 (Stage 0), L1

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

### Runtimes (s)

| cell | B2 (2PL) | B1-FB1 | B2-FB1 | B2-FB1 / B2 |
|---|---|---|---|---|
| E1 | 211 | 895 | 627 | 2.98 |
| E2 | 146 | 513 | 661 | 4.52 |
| E3 | 438 | 575 | 746 | 1.70 |
| E4 | 258 | 696 | 618 | 2.39 |
| E5 | 318 | 560 | 711 | 2.23 |

### Godambe SEs of the L1 fit (N = 300 / 1000; SE of tau_D on the log scale) against the 2PL (Stage 0)

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

### Expected T_FB (L1; population value times N) and fit health

| cell | E[T_FB] N=300 | E[T_FB] N=1000 | (x q95 of the 2PL null, N=1000) | 2PL E[T] N=1000 |
|---|---|---|---|---|
| E1 | 174.0 | 579.9 | 112.4 | 586.6 |
| E2 | 0.0 | 0.0 | 0.0 | 0.0 |
| E3 | 8.36 | 27.9 | 5.40 | 1352.0 |
| E4 | 0.008 | 0.028 | 0.005 | 21.7 |
| E5 | 687.2 | 2290.8 | 444.0 | 5716.2 |

- All 20 fits converged. The D22 Newton decrement is 1e-9 or smaller everywhere except B2-FB1 in E2 (`hessian_not_pd`, nan; the null cell, as for L0).
- Flags (B2-FB1): E1 and E2 `tau_D_not_identified(kappa~0)`, `secondary_optima_present`, `single_start_at_best` (E2 also `hessian_not_pd`); E3 `boundary:tau_F@upper`, `secondary_optima_present`; E4 `single_start_at_best`, `secondary_optima_present`; E5 none.
- Godambe sandwich scores: mean/sd 0.026-0.038 (limit 0.04 as in Stage 0).
- SE of sigma2_F, L1 / 2PL at N = 1000: E1 1.09, E2 1.23, E5 1.09 (E3 0.40, E4 0.65, where the 2PL value is the misattributed one). corr(sigma2_F, kappa): +0.41 (E1), +0.23 (E2), +0.51 (E3), +0.58 (E4), +0.52 (E5).
- Fit runtimes: B2-FB1 627-746 s, B1-FB1 513-895 s (1.7-4.5 x the 2PL B2 fit on the same pair counts); a likelihood-and-gradient evaluation takes 0.070 s (L0 0.043 s).
- Cost of Stage 0b: Step 1 seconds; Step 2 about 2.5 CPU-h (34 min wall, 5 workers).
