# Experiment 2 summary: individual tracking of the shared transient latent state F

- stage `pilot`, config hash `0cc472d76b9b`, code hash `38add5993f73`, git `dd958ac9a2` (dirty: False)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v64-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: {'jobs': 13, 'ok': 13, 'errors': 0}

## Information bound (S1 generating parameters, Gaussian prior; expected R^2 upper bound for ANY estimator)

| channel | pre-answer (practice) | post-answer (practice) | pre (all 112) | post (all 112) | pre (probe) |
|---|---|---|---|---|---|
| answers_only | 0.1135 | 0.1436 | 0.1151 | 0.1464 | 0.1245 |
| indicator_rho0.3_with_answers | 0.5554 | 0.5652 | 0.5534 | 0.5635 | 0.5413 |
| indicator_rho0.3_only | 0.5447 | 0.5447 | 0.5425 | 0.5425 | 0.5289 |
| indicator_rho0.6_with_answers | 0.7540 | 0.7572 | 0.7531 | 0.7564 | 0.7475 |
| indicator_rho0.6_only | 0.7525 | 0.7525 | 0.7515 | 0.7515 | 0.7457 |

## S1|N=1000  (2 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1258 | 0.1546 | 0.896 |
| full_known | 0.1262 | 0.1552 | 0.903 |
| ind_full_rho0.3 | 0.5503 | 0.5598 | 0.899 |
| ind_only_rho0.3 | 0.5405 | 0.5405 | 0.898 |
| ind_full_rho0.6 | 0.7556 | 0.7585 | 0.900 |
| ind_only_rho0.6 | 0.7540 | 0.7540 | 0.899 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00005 [-0.00289, 0.00300] | 0.00005 [-0.00011, 0.00021] | 0.00068 [-0.00129, 0.00264] | -0.00004 [-0.00449, 0.00441] |
| full_fit over B1_fit | 0.00381 [0.00356, 0.00406] | 0.00381 [0.00307, 0.00454] | 0.00262 [-0.00688, 0.01211] | -0.00019 [-0.01967, 0.01929] |
| full_fit over F0_fit | 0.00386 [0.00066, 0.00705] | 0.00386 [0.00311, 0.00461] | 0.00329 [-0.00424, 0.01082] | -0.00023 [-0.01526, 0.01480] |
| full_fit over priorF_fit | 0.00317 [0.00069, 0.00565] | 0.00317 [0.00246, 0.00388] | 0.00199 [0.00095, 0.00302] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00343 [0.00177, 0.00508] | 0.00343 [0.00272, 0.00414] | 0.00293 [-0.00310, 0.00897] | -0.00018 [-0.00950, 0.00914] |
| full_known over F0_known | 0.00387 [0.00255, 0.00519] | 0.00387 [0.00311, 0.00463] | 0.00296 [-0.01078, 0.01670] | -0.00053 [-0.01414, 0.01309] |
| full_known over full_fit | 0.00018 [-0.00146, 0.00181] | 0.00018 [0.00003, 0.00032] | 0.00010 [-0.00331, 0.00351] | 0.00042 [-0.00278, 0.00363] |
| full_known over priorF_known | 0.00315 [0.00307, 0.00323] | 0.00315 [0.00243, 0.00387] | 0.00185 [-0.00208, 0.00579] | 0.00000 [-0.00000, 0.00000] |
| ind_full_rho0.3 over full_known | 0.01014 [-0.00152, 0.02180] | 0.01014 [0.00912, 0.01117] | 0.01071 [0.01005, 0.01136] | 0.01227 [-0.03133, 0.05587] |
| ind_full_rho0.3 over ind_only_rho0.3 | 0.10071 [0.06512, 0.13630] | 0.10071 [0.09350, 0.10792] | 0.12799 [0.04951, 0.20646] | 0.08381 [0.05942, 0.10819] |
| ind_full_rho0.6 over full_known | 0.01552 [0.00278, 0.02825] | 0.01552 [0.01426, 0.01677] | 0.01760 [0.01415, 0.02106] | 0.02515 [0.00744, 0.04287] |
| ind_full_rho0.6 over ind_only_rho0.6 | 0.10113 [0.06988, 0.13238] | 0.10113 [0.09389, 0.10837] | 0.13028 [0.06527, 0.19528] | 0.08997 [0.07797, 0.10198] |
| oracle_fit over full_fit | 0.02163 [0.01297, 0.03029] | 0.02163 [0.02007, 0.02319] | 0.02320 [0.02125, 0.02515] | 0.03524 [-0.05067, 0.12115] |
| oracle_known over full_known | 0.02167 [0.01393, 0.02942] | 0.02167 [0.02012, 0.02323] | 0.02351 [0.01707, 0.02994] | 0.03513 [-0.05097, 0.12124] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1796 | 0.00216 | 0.01845 | 0.877 |
| B1_fit | 0.1843 | 0.00235 | 0.02011 | 0.863 |
| full_known | 0.1760 | 0.00201 | 0.01713 | 0.885 |
| ind_full_rho0.3 | 0.1589 | 0.00195 | 0.01673 | 0.881 |
| ind_only_rho0.3 | 0.9197 | 0.00248 | 0.01956 | 0.882 |
| ind_full_rho0.6 | 0.1550 | 0.00193 | 0.01675 | 0.885 |
| ind_only_rho0.6 | 0.9197 | 0.00248 | 0.01956 | 0.882 |

## S1|N=300  (2 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1232 | 0.1506 | 0.872 |
| full_known | 0.1272 | 0.1565 | 0.903 |
| ind_full_rho0.3 | 0.5551 | 0.5645 | 0.899 |
| ind_only_rho0.3 | 0.5453 | 0.5453 | 0.900 |
| ind_full_rho0.6 | 0.7533 | 0.7564 | 0.899 |
| ind_only_rho0.6 | 0.7518 | 0.7518 | 0.900 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00011 [-0.00092, 0.00114] | 0.00011 [-0.00001, 0.00024] | 0.00081 [-0.00169, 0.00330] | 0.00075 [-0.00772, 0.00922] |
| full_fit over B1_fit | 0.00329 [-0.00077, 0.00735] | 0.00329 [0.00248, 0.00410] | 0.00305 [0.00058, 0.00552] | 0.00031 [-0.00179, 0.00241] |
| full_fit over F0_fit | 0.00340 [0.00037, 0.00643] | 0.00340 [0.00259, 0.00422] | 0.00386 [0.00383, 0.00388] | 0.00106 [-0.00951, 0.01163] |
| full_fit over priorF_fit | 0.00269 [-0.00010, 0.00548] | 0.00269 [0.00201, 0.00337] | 0.00266 [0.00135, 0.00397] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00338 [0.00086, 0.00590] | 0.00338 [0.00262, 0.00415] | 0.00370 [0.00233, 0.00507] | 0.00083 [-0.00615, 0.00781] |
| full_known over F0_known | 0.00313 [0.00050, 0.00577] | 0.00313 [0.00233, 0.00394] | 0.00318 [0.00038, 0.00598] | 0.00078 [-0.00767, 0.00923] |
| full_known over full_fit | 0.00036 [-0.00111, 0.00182] | 0.00036 [0.00009, 0.00062] | 0.00048 [-0.00082, 0.00178] | 0.00065 [-0.01162, 0.01291] |
| full_known over priorF_known | 0.00270 [-0.00084, 0.00625] | 0.00270 [0.00201, 0.00340] | 0.00225 [-0.00014, 0.00464] | 0.00000 [-0.00000, 0.00000] |
| ind_full_rho0.3 over full_known | 0.00933 [-0.00687, 0.02554] | 0.00933 [0.00828, 0.01039] | 0.01299 [-0.00432, 0.03030] | 0.01490 [-0.01425, 0.04405] |
| ind_full_rho0.3 over ind_only_rho0.3 | 0.10044 [0.09333, 0.10756] | 0.10044 [0.09413, 0.10675] | 0.12855 [0.12362, 0.13349] | 0.08909 [0.08580, 0.09238] |
| ind_full_rho0.6 over full_known | 0.01378 [0.00867, 0.01889] | 0.01378 [0.01249, 0.01507] | 0.01911 [0.01765, 0.02056] | 0.02302 [-0.10206, 0.14811] |
| ind_full_rho0.6 over ind_only_rho0.6 | 0.10131 [0.09152, 0.11109] | 0.10131 [0.09491, 0.10770] | 0.12916 [0.12338, 0.13495] | 0.08981 [0.05576, 0.12387] |
| oracle_fit over full_fit | 0.02055 [0.01809, 0.02300] | 0.02055 [0.01896, 0.02214] | 0.02812 [0.01988, 0.03636] | 0.03364 [-0.11901, 0.18630] |
| oracle_known over full_known | 0.02062 [0.01899, 0.02225] | 0.02062 [0.01906, 0.02218] | 0.02816 [0.02258, 0.03374] | 0.03396 [-0.11760, 0.18552] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1771 | 0.00246 | 0.02058 | 0.856 |
| B1_fit | 0.1735 | 0.00237 | 0.02227 | 0.849 |
| full_known | 0.1661 | 0.00207 | 0.01953 | 0.901 |
| ind_full_rho0.3 | 0.1549 | 0.00195 | 0.01944 | 0.894 |
| ind_only_rho0.3 | 0.9115 | 0.00247 | 0.02275 | 0.896 |
| ind_full_rho0.6 | 0.1525 | 0.00191 | 0.01939 | 0.892 |
| ind_only_rho0.6 | 0.9115 | 0.00247 | 0.02275 | 0.896 |

## S2|N=300  (2 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00017 [0.00011, 0.00022] | 0.161 | NA | 0.00001 |
| full_known | 0.00000 [0.00000, 0.00000] | NA | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00001 [-0.00038, 0.00041] | 0.00001 [-0.00001, 0.00003] | 0.00008 [-0.00132, 0.00148] | 0.00006 [-0.00126, 0.00139] |
| full_fit over B1_fit | -0.00001 [-0.00078, 0.00075] | -0.00001 [-0.00006, 0.00003] | -0.00002 [-0.00194, 0.00190] | -0.00012 [-0.00173, 0.00149] |
| full_fit over F0_fit | -0.00000 [-0.00038, 0.00037] | -0.00000 [-0.00004, 0.00004] | 0.00006 [-0.00046, 0.00058] | -0.00006 [-0.00034, 0.00023] |
| full_fit over priorF_fit | -0.00001 [-0.00012, 0.00010] | -0.00001 [-0.00002, 0.00001] | 0.00000 [-0.00005, 0.00006] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00001 [-0.00017, 0.00014] | -0.00001 [-0.00003, 0.00000] | 0.00001 [-0.00013, 0.00016] | -0.00001 [-0.00018, 0.00015] |
| full_known over F0_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| full_known over full_fit | 0.00043 [-0.00157, 0.00243] | 0.00043 [0.00021, 0.00064] | 0.00071 [-0.00785, 0.00928] | -0.00049 [-0.00789, 0.00691] |
| full_known over priorF_known | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | 0.00000 [-0.00037, 0.00038] | 0.00000 [-0.00004, 0.00004] | -0.00006 [-0.00058, 0.00046] | 0.00006 [-0.00023, 0.00034] |
| oracle_known over full_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1437 | 0.00219 | 0.02071 | 0.909 |
| B1_fit | 0.1437 | 0.00221 | 0.02038 | 0.910 |
| full_known | 0.1414 | 0.00209 | 0.01867 | 0.901 |

## S8|N=300  (2 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.0845 | 0.1087 | 0.930 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00017 [-0.00147, 0.00181] | 0.00017 [-0.00003, 0.00038] | 0.00043 [-0.00397, 0.00483] | 0.00002 [-0.00368, 0.00372] |
| full_fit over B1_fit | 0.00260 [-0.00414, 0.00935] | 0.00260 [0.00182, 0.00338] | 0.00367 [0.00001, 0.00733] | 0.00110 [-0.01016, 0.01235] |
| full_fit over F0_fit | 0.00277 [-0.00233, 0.00788] | 0.00277 [0.00199, 0.00355] | 0.00409 [-0.00397, 0.01215] | 0.00112 [-0.01385, 0.01608] |
| full_fit over priorF_fit | 0.00308 [-0.00030, 0.00646] | 0.00308 [0.00238, 0.00378] | 0.00298 [-0.00150, 0.00747] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00284 [-0.00249, 0.00816] | 0.00284 [0.00211, 0.00357] | 0.00349 [-0.00207, 0.00906] | 0.00083 [-0.01131, 0.01296] |
| oracle_fit over full_fit | 0.02116 [0.00699, 0.03534] | 0.02116 [0.01969, 0.02264] | 0.02448 [0.02382, 0.02515] | 0.03004 [-0.01124, 0.07132] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1674 | 0.00389 | 0.04279 | 0.942 |
| B1_fit | 0.1840 | 0.00475 | 0.03915 | 0.910 |

## S8n|N=300  (2 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00002 [-0.00001, 0.00006] | -0.006 | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00001 [-0.00005, 0.00003] | -0.00001 [-0.00001, -0.00000] | -0.00002 [-0.00015, 0.00010] | -0.00004 [-0.00032, 0.00025] |
| full_fit over B1_fit | 0.00001 [-0.00009, 0.00011] | 0.00001 [-0.00000, 0.00002] | 0.00007 [-0.00031, 0.00045] | 0.00004 [-0.00038, 0.00046] |
| full_fit over F0_fit | 0.00000 [-0.00014, 0.00015] | 0.00000 [-0.00001, 0.00001] | 0.00004 [-0.00022, 0.00030] | 0.00000 [-0.00014, 0.00014] |
| full_fit over priorF_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | -0.00000 [-0.00015, 0.00014] | -0.00000 [-0.00001, 0.00001] | -0.00004 [-0.00030, 0.00022] | -0.00000 [-0.00014, 0.00014] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1729 | 0.00510 | 0.04499 | 0.924 |
| B1_fit | 0.1730 | 0.00510 | 0.04527 | 0.923 |

## Null safety (R3): spurious tracking gain of B2-full over B2-priorF

- **S2|N=300**: -0.00001 [-0.00012, 0.00010] nats/response -> spurious tracking gain: **False**
- **S8n|N=300**: -0.00000 [-0.00000, 0.00000] nats/response -> spurious tracking gain: **False**

## SMC reference: gates (R1) and ADF approximation (R2)

- 32 learners from 2 replications, 10 independent seeds, 16384 particles; min ESS 4782
- **R1** {'R2_single_run_mc_sd_le_0.002': True, 'p_single_run_mc_rms_le_0.001': False, 'doubling_within_2se': True, 'orthant_check': 'unit test test_smc_matches_orthant (tests/test_transient_filtering.py)', 'passed': False}
- **R2** {'mean_abs_dp_le_0.005': True, 'logloss_gain_ci_within_pm_5e-4': False, 'adf_approximation_negligible_for_forecasting': False}
- single-run MC SD of R^2: pre 0.00019, post 0.00023; single-run RMS MC SD of p: 0.00120
- R^2 (practice, these learners) post: reference 0.0751, ADF 0.0743, bound 0.1436 (ref - bound -0.0684, learner-sampling SE 0.0579); pre: ref 0.0417, ADF 0.0410, bound 0.1135
- ADF vs reference: mean |dp| (practice) 0.00307; log-loss gain of reference over ADF 0.000185 [-0.000243, 0.000614] nats/response; delta R^2 post (ref - ADF) {'mean': 0.0008159298788421968, 'se': 0.0005616435691488092}
- B1 (fitted) ADF vs reference: mean |dp| 0.00339; gain 0.000265 [-0.000192, 0.000723]

