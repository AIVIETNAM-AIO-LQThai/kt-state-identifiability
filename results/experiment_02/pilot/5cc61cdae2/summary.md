# Experiment 2 summary: individual tracking of the shared transient latent state F

- stage `pilot`, config hash `5cc61cdae220`, code hash `f989415953e7`, git `35a6a8f364` (dirty: True)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v64-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: {'jobs': 6, 'ok': 6, 'errors': 0}

## Information bound (S1 generating parameters, Gaussian prior; expected R^2 upper bound for ANY estimator)

| channel | pre-answer (practice) | post-answer (practice) | pre (all 112) | post (all 112) | pre (probe) |
|---|---|---|---|---|---|
| answers_only | 0.1135 | 0.1436 | 0.1151 | 0.1464 | 0.1245 |
| indicator_rho0.3_with_answers | 0.5554 | 0.5652 | 0.5534 | 0.5635 | 0.5413 |
| indicator_rho0.3_only | 0.5447 | 0.5447 | 0.5425 | 0.5425 | 0.5289 |
| indicator_rho0.6_with_answers | 0.7540 | 0.7572 | 0.7531 | 0.7564 | 0.7475 |
| indicator_rho0.6_only | 0.7525 | 0.7525 | 0.7515 | 0.7515 | 0.7457 |

## S1|N=1000  (1 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1004 | 0.1306 | 0.889 |
| full_known | 0.1006 | 0.1310 | 0.900 |
| ind_full_rho0.3 | 0.5502 | 0.5594 | 0.897 |
| ind_only_rho0.3 | 0.5390 | 0.5390 | 0.898 |
| ind_full_rho0.6 | 0.7532 | 0.7558 | 0.900 |
| ind_only_rho0.6 | 0.7514 | 0.7514 | 0.897 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00028 [nan, nan] | 0.00028 [0.00001, 0.00055] | 0.00083 [nan, nan] | 0.00031 [nan, nan] |
| full_fit over B1_fit | 0.00383 [nan, nan] | 0.00383 [0.00275, 0.00490] | 0.00187 [nan, nan] | -0.00172 [nan, nan] |
| full_fit over F0_fit | 0.00411 [nan, nan] | 0.00411 [0.00301, 0.00521] | 0.00270 [nan, nan] | -0.00142 [nan, nan] |
| full_fit over priorF_fit | 0.00336 [nan, nan] | 0.00336 [0.00233, 0.00440] | 0.00191 [nan, nan] | -0.00000 [nan, nan] |
| full_fit over white_fit | 0.00356 [nan, nan] | 0.00356 [0.00253, 0.00458] | 0.00246 [nan, nan] | -0.00091 [nan, nan] |
| full_known over F0_known | 0.00397 [nan, nan] | 0.00397 [0.00288, 0.00507] | 0.00188 [nan, nan] | -0.00160 [nan, nan] |
| full_known over full_fit | 0.00030 [nan, nan] | 0.00030 [0.00009, 0.00052] | -0.00017 [nan, nan] | 0.00068 [nan, nan] |
| full_known over priorF_known | 0.00316 [nan, nan] | 0.00316 [0.00214, 0.00417] | 0.00154 [nan, nan] | -0.00000 [nan, nan] |
| ind_full_rho0.3 over full_known | 0.01106 [nan, nan] | 0.01106 [0.00965, 0.01247] | 0.01076 [nan, nan] | 0.00884 [nan, nan] |
| ind_full_rho0.3 over ind_only_rho0.3 | 0.10351 [nan, nan] | 0.10351 [0.09376, 0.11326] | 0.13416 [nan, nan] | 0.08189 [nan, nan] |
| ind_full_rho0.6 over full_known | 0.01652 [nan, nan] | 0.01652 [0.01479, 0.01825] | 0.01788 [nan, nan] | 0.02655 [nan, nan] |
| ind_full_rho0.6 over ind_only_rho0.6 | 0.10359 [nan, nan] | 0.10359 [0.09383, 0.11335] | 0.13539 [nan, nan] | 0.09092 [nan, nan] |
| oracle_fit over full_fit | 0.02231 [nan, nan] | 0.02231 [0.02012, 0.02451] | 0.02335 [nan, nan] | 0.02848 [nan, nan] |
| oracle_known over full_known | 0.02228 [nan, nan] | 0.02228 [0.02011, 0.02445] | 0.02401 [nan, nan] | 0.02836 [nan, nan] |
| priorF_fit over B1_fit | 0.00046 [nan, nan] | 0.00046 [-0.00035, 0.00127] | -0.00004 [nan, nan] | -0.00172 [nan, nan] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1686 | 0.00208 | 0.01778 | 0.872 |
| B1_fit | 0.1704 | 0.00213 | 0.01768 | 0.864 |
| full_known | 0.1677 | 0.00200 | 0.01641 | 0.892 |
| ind_full_rho0.3 | 0.1511 | 0.00185 | 0.01609 | 0.891 |
| ind_only_rho0.3 | 0.9193 | 0.00256 | 0.01899 | 0.888 |
| ind_full_rho0.6 | 0.1481 | 0.00183 | 0.01609 | 0.892 |
| ind_only_rho0.6 | 0.9193 | 0.00256 | 0.01899 | 0.888 |

## S2|N=300  (1 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00017 [nan, nan] | 0.008 | NA | 0.00000 |
| full_known | 0.00000 [nan, nan] | NA | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00002 [nan, nan] | -0.00002 [-0.00005, 0.00001] | -0.00003 [nan, nan] | 0.00017 [nan, nan] |
| full_fit over B1_fit | 0.00005 [nan, nan] | 0.00005 [-0.00002, 0.00012] | 0.00013 [nan, nan] | -0.00024 [nan, nan] |
| full_fit over F0_fit | 0.00003 [nan, nan] | 0.00003 [-0.00003, 0.00009] | 0.00010 [nan, nan] | -0.00008 [nan, nan] |
| full_fit over priorF_fit | -0.00000 [nan, nan] | -0.00000 [-0.00000, 0.00000] | -0.00000 [nan, nan] | 0.00000 [nan, nan] |
| full_fit over white_fit | -0.00000 [nan, nan] | -0.00000 [-0.00000, 0.00000] | 0.00000 [nan, nan] | 0.00000 [nan, nan] |
| full_known over F0_known | 0.00000 [nan, nan] | 0.00000 [0.00000, 0.00000] | 0.00000 [nan, nan] | 0.00000 [nan, nan] |
| full_known over full_fit | 0.00027 [nan, nan] | 0.00027 [-0.00002, 0.00055] | 0.00004 [nan, nan] | 0.00009 [nan, nan] |
| full_known over priorF_known | 0.00000 [nan, nan] | 0.00000 [-0.00000, 0.00000] | -0.00000 [nan, nan] | 0.00000 [nan, nan] |
| oracle_fit over full_fit | -0.00003 [nan, nan] | -0.00003 [-0.00009, 0.00003] | -0.00010 [nan, nan] | 0.00008 [nan, nan] |
| oracle_known over full_known | 0.00000 [nan, nan] | 0.00000 [0.00000, 0.00000] | 0.00000 [nan, nan] | 0.00000 [nan, nan] |
| priorF_fit over B1_fit | 0.00005 [nan, nan] | 0.00005 [-0.00002, 0.00012] | 0.00013 [nan, nan] | -0.00024 [nan, nan] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1367 | 0.00211 | 0.01678 | 0.932 |
| B1_fit | 0.1369 | 0.00213 | 0.01706 | 0.933 |
| full_known | 0.1347 | 0.00205 | 0.01648 | 0.923 |

## S8n|N=300  (1 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00002 [nan, nan] | -0.002 | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00000 [nan, nan] | -0.00000 [-0.00001, 0.00000] | -0.00003 [nan, nan] | -0.00006 [nan, nan] |
| full_fit over B1_fit | 0.00002 [nan, nan] | 0.00002 [-0.00000, 0.00004] | 0.00010 [nan, nan] | 0.00007 [nan, nan] |
| full_fit over F0_fit | 0.00001 [nan, nan] | 0.00001 [-0.00001, 0.00003] | 0.00006 [nan, nan] | 0.00001 [nan, nan] |
| full_fit over priorF_fit | -0.00000 [nan, nan] | -0.00000 [-0.00000, 0.00000] | 0.00000 [nan, nan] | 0.00000 [nan, nan] |
| full_fit over white_fit | -0.00000 [nan, nan] | -0.00000 [-0.00000, 0.00000] | 0.00000 [nan, nan] | 0.00000 [nan, nan] |
| oracle_fit over full_fit | -0.00001 [nan, nan] | -0.00001 [-0.00003, 0.00001] | -0.00006 [nan, nan] | -0.00001 [nan, nan] |
| priorF_fit over B1_fit | 0.00002 [nan, nan] | 0.00002 [-0.00000, 0.00004] | 0.00010 [nan, nan] | 0.00007 [nan, nan] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1753 | 0.00625 | 0.04097 | 0.924 |
| B1_fit | 0.1754 | 0.00625 | 0.04124 | 0.923 |

## Null safety (R3): spurious tracking gain of B2-full over B2-priorF

- **S2|N=300**: -0.00000 [nan, nan] nats/response -> spurious tracking gain: **False**
- **S8n|N=300**: -0.00000 [nan, nan] nats/response -> spurious tracking gain: **False**; sensitivity excluding flagged fit(s) {'excluded': [0], 'n_reps_kept': 0, 'gain_full_over_priorF_practice': {'mean': nan, 'se': nan, 'lo': nan, 'hi': nan, 'R': 0}, 'spurious_tracking_gain': False}

## Production reference (all S1 N=1000 evaluation learners): gap decomposition

- 300 learners, 1 replications, 32768 particles, min ESS 7517
- **R0 (implementation validity)**: passed = **True**  {'R2_ref_pre': {'excess_over_bound': -0.012891167163461947, 'learner_se': 0.02034282759789413, 'ok': True}, 'R2_adf_known_pre': {'excess_over_bound': -0.01283520478018163, 'learner_se': 0.020334167607069745, 'ok': True}, 'R2_ref_post': {'excess_over_bound': -0.012538789305685749, 'learner_se': 0.020116517336638346, 'ok': True}, 'R2_adf_known_post': {'excess_over_bound': -0.012500154132515595, 'learner_se': 0.02010506891414484, 'ok': True}, 'track_S1|N=1000_full_known_pre': {'excess_over_bound': -0.012872273117209176, 'learner_se': 0.020334167607069745, 'ok': True}, 'track_S1|N=1000_full_known_post': {'excess_over_bound': -0.012530414531575107, 'learner_se': 0.02010506891414484, 'ok': True}}
- **R2 (ADF approximation, production learners)**: {'mean_abs_dp_adf_known_practice': 0.0028836063373139814, 'mean_abs_dp_adf_fit_practice': 0.00594549943780182, 'logloss_gain_ref_over_adf_known_practice': {'mean': 0.00010962861416620222, 'se': 6.391747834426877e-05, 'lo': -1.5649643388564565e-05, 'hi': 0.000234906871720969, 'n': 300}, 'mean_abs_dp_le_0.005': True, 'logloss_gain_ci_within_pm_5e-4': True, 'adf_approximation_negligible_for_forecasting': True}

R^2 = 1 - MSE/sigma2_F. Order expected: bound >= reference >= ADF(known) >= ADF(fitted). Learner CIs.

| phase | bin | bound | reference | ADF known | ADF fitted | approx. loss (ref - ADF known) | estimation loss (ADF known - fitted), learner CI | estimation loss, replication CI |
|---|---|---|---|---|---|---|---|---|
| pre | practice | 0.1134 | 0.1006 [0.0607, 0.1404] | 0.1006 [0.0608, 0.1405] | 0.1004 [0.0605, 0.1402] | -0.00006 [-0.00044, 0.00033] | 0.00026 [-0.00108, 0.00161] | 0.00026 [nan, nan] |
| pre | first | 0.0000 | -0.0302 [-0.1225, 0.0621] | -0.0302 [-0.1225, 0.0621] | -0.0302 [-0.1225, 0.0621] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [nan, nan] |
| pre | j1_4 | 0.0782 | 0.0401 [-0.0381, 0.1183] | 0.0401 [-0.0382, 0.1184] | 0.0398 [-0.0386, 0.1182] | -0.00001 [-0.00039, 0.00038] | 0.00030 [-0.00073, 0.00132] | 0.00030 [nan, nan] |
| pre | j5_15 | 0.1238 | 0.0864 [0.0284, 0.1444] | 0.0864 [0.0285, 0.1444] | 0.0873 [0.0295, 0.1452] | -0.00002 [-0.00058, 0.00053] | -0.00090 [-0.00237, 0.00056] | -0.00090 [nan, nan] |
| pre | j16_31 | 0.1222 | 0.1336 [0.0846, 0.1826] | 0.1337 [0.0847, 0.1826] | 0.1326 [0.0834, 0.1817] | -0.00009 [-0.00060, 0.00041] | 0.00107 [-0.00116, 0.00331] | 0.00107 [nan, nan] |
| pre | probe | 0.1246 | 0.1004 [0.0218, 0.1789] | 0.1002 [0.0216, 0.1789] | 0.0980 [0.0191, 0.1769] | 0.00013 [-0.00060, 0.00086] | 0.00225 [-0.00029, 0.00478] | 0.00225 [nan, nan] |
| post | practice | 0.1435 | 0.1310 [0.0916, 0.1704] | 0.1310 [0.0916, 0.1704] | 0.1306 [0.0912, 0.1700] | -0.00004 [-0.00047, 0.00039] | 0.00044 [-0.00101, 0.00190] | 0.00044 [nan, nan] |
| post | first | 0.0559 | 0.0152 [-0.0724, 0.1029] | 0.0153 [-0.0724, 0.1029] | 0.0156 [-0.0721, 0.1033] | -0.00003 [-0.00039, 0.00034] | -0.00033 [-0.00197, 0.00131] | -0.00033 [nan, nan] |
| post | j1_4 | 0.1150 | 0.0821 [0.0075, 0.1567] | 0.0821 [0.0074, 0.1567] | 0.0813 [0.0064, 0.1563] | 0.00005 [-0.00043, 0.00053] | 0.00075 [-0.00072, 0.00221] | 0.00075 [nan, nan] |
| post | j5_15 | 0.1520 | 0.1109 [0.0533, 0.1684] | 0.1109 [0.0534, 0.1684] | 0.1117 [0.0543, 0.1691] | -0.00003 [-0.00065, 0.00059] | -0.00084 [-0.00256, 0.00088] | -0.00084 [nan, nan] |
| post | j16_31 | 0.1503 | 0.1643 [0.1165, 0.2121] | 0.1644 [0.1166, 0.2121] | 0.1631 [0.1151, 0.2110] | -0.00007 [-0.00061, 0.00048] | 0.00130 [-0.00106, 0.00365] | 0.00130 [nan, nan] |
| post | probe | 0.1636 | 0.1334 [0.0581, 0.2088] | 0.1334 [0.0580, 0.2088] | 0.1310 [0.0552, 0.2068] | 0.00005 [-0.00078, 0.00088] | 0.00242 [-0.00046, 0.00530] | 0.00242 [nan, nan] |

Causal log-loss gains on the production learners, nats per response (practice; positive = first arm better):

- ref over adf_known: learner CI 0.00011 [-0.00002, 0.00023]; replication CI 0.00011 [nan, nan]
- adf_known over adf_fit: learner CI 0.00030 [0.00009, 0.00052]; replication CI 0.00030 [nan, nan]
- adf_fit over B1_fit: learner CI 0.00383 [0.00275, 0.00490]; replication CI 0.00383 [nan, nan]

- provenance: {'jobs_with_hashes': 5, 'numpy': ['2.4.6'], 'scipy': ['1.17.1']}

## SMC reference: gates (R1) and ADF approximation (R2)

- 16 learners from 1 replications, 10 independent seeds, 32768 particles; min ESS 9739
- **R1** {'R2_single_run_mc_sd_le_0.002': True, 'p_single_run_mc_rms_le_0.001': True, 'doubling_within_2se': True, 'orthant_check': 'unit test test_smc_matches_orthant (tests/test_transient_filtering.py)', 'passed': True}
- R2 on this validation subset (indicative only): {'mean_abs_dp_le_0.005': True, 'logloss_gain_ci_within_pm_5e-4': False, 'adf_approximation_negligible_for_forecasting': False}
- single-run MC SD of R^2: pre 0.00025, post 0.00030; single-run RMS MC SD of p: 0.00082
- R^2 (practice, these learners) post: reference 0.0891, ADF 0.0878, bound 0.1436 (ref - bound -0.0545, learner-sampling SE 0.0850); pre: ref 0.0612, ADF 0.0601, bound 0.1135
- ADF vs reference: mean |dp| (practice) 0.00308; log-loss gain of reference over ADF -0.000085 [-0.000724, 0.000555] nats/response; delta R^2 post (ref - ADF) {'mean': 0.0012906142202608818, 'se': 0.0006953101162817581}
- B1 (fitted) ADF vs reference: mean |dp| 0.00362; gain -0.000041 [-0.000855, 0.000774]

