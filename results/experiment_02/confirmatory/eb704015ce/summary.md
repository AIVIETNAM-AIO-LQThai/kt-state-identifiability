# Experiment 2 summary: individual tracking of the shared transient latent state F

- stage `confirmatory`, config hash `eb704015cee8`, code hash `1ee7e3d9acff`, git `77edb75743` (dirty: False)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v64-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: {'jobs': 191, 'ok': 191, 'errors': 0}

## Information bound (S1 generating parameters, Gaussian prior; expected R^2 upper bound for ANY estimator)

| channel | pre-answer (practice) | post-answer (practice) | pre (all 112) | post (all 112) | pre (probe) |
|---|---|---|---|---|---|
| answers_only | 0.1135 | 0.1436 | 0.1151 | 0.1464 | 0.1245 |
| indicator_rho0.3_with_answers | 0.5554 | 0.5652 | 0.5534 | 0.5635 | 0.5413 |
| indicator_rho0.3_only | 0.5447 | 0.5447 | 0.5425 | 0.5425 | 0.5289 |
| indicator_rho0.6_with_answers | 0.7540 | 0.7572 | 0.7531 | 0.7564 | 0.7475 |
| indicator_rho0.6_only | 0.7525 | 0.7525 | 0.7515 | 0.7515 | 0.7457 |

## S1|N=1000  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1118 | 0.1402 | 0.904 |
| full_known | 0.1128 | 0.1420 | 0.900 |
| ind_full_rho0.3 | 0.5557 | 0.5653 | 0.901 |
| ind_only_rho0.3 | 0.5454 | 0.5454 | 0.901 |
| ind_full_rho0.6 | 0.7543 | 0.7575 | 0.900 |
| ind_only_rho0.6 | 0.7528 | 0.7528 | 0.900 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00003 [-0.00006, 0.00012] | 0.00003 [-0.00002, 0.00008] | 0.00071 [0.00041, 0.00101] | 0.00021 [-0.00004, 0.00045] |
| full_fit over B1_fit | 0.00341 [0.00310, 0.00372] | 0.00341 [0.00315, 0.00366] | 0.00407 [0.00327, 0.00486] | 0.00145 [0.00071, 0.00219] |
| full_fit over F0_fit | 0.00343 [0.00310, 0.00377] | 0.00343 [0.00317, 0.00369] | 0.00478 [0.00383, 0.00573] | 0.00165 [0.00084, 0.00246] |
| full_fit over priorF_fit | 0.00291 [0.00262, 0.00319] | 0.00291 [0.00268, 0.00313] | 0.00350 [0.00289, 0.00412] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00314 [0.00283, 0.00344] | 0.00314 [0.00289, 0.00338] | 0.00430 [0.00350, 0.00510] | 0.00080 [0.00012, 0.00149] |
| full_known over F0_known | 0.00343 [0.00313, 0.00373] | 0.00343 [0.00317, 0.00368] | 0.00449 [0.00374, 0.00523] | 0.00147 [0.00075, 0.00220] |
| full_known over full_fit | 0.00019 [0.00011, 0.00026] | 0.00019 [0.00013, 0.00024] | 0.00011 [0.00003, 0.00020] | 0.00022 [-0.00015, 0.00059] |
| full_known over priorF_known | 0.00289 [0.00265, 0.00313] | 0.00289 [0.00267, 0.00311] | 0.00340 [0.00282, 0.00398] | -0.00000 [-0.00000, 0.00000] |
| ind_full_rho0.3 over full_known | 0.00946 [0.00915, 0.00978] | 0.00946 [0.00912, 0.00980] | 0.01184 [0.01044, 0.01324] | 0.01133 [0.00882, 0.01384] |
| ind_full_rho0.3 over ind_only_rho0.3 | 0.10116 [0.09902, 0.10329] | 0.10116 [0.09897, 0.10334] | 0.13202 [0.12833, 0.13571] | 0.07714 [0.07118, 0.08310] |
| ind_full_rho0.6 over full_known | 0.01450 [0.01407, 0.01494] | 0.01450 [0.01409, 0.01492] | 0.01809 [0.01674, 0.01943] | 0.02207 [0.01885, 0.02530] |
| ind_full_rho0.6 over ind_only_rho0.6 | 0.10189 [0.09970, 0.10407] | 0.10189 [0.09969, 0.10409] | 0.13322 [0.12990, 0.13655] | 0.07973 [0.07341, 0.08605] |
| oracle_fit over full_fit | 0.02127 [0.02075, 0.02179] | 0.02127 [0.02077, 0.02177] | 0.02480 [0.02294, 0.02666] | 0.03554 [0.03183, 0.03924] |
| oracle_known over full_known | 0.02126 [0.02074, 0.02178] | 0.02126 [0.02076, 0.02176] | 0.02494 [0.02311, 0.02676] | 0.03557 [0.03190, 0.03925] |
| priorF_fit over B1_fit | 0.00050 [0.00030, 0.00070] | 0.00050 [0.00033, 0.00067] | 0.00057 [0.00010, 0.00103] | 0.00145 [0.00071, 0.00219] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1640 | 0.00224 | 0.02011 | 0.894 |
| B1_fit | 0.1684 | 0.00251 | 0.02186 | 0.877 |
| full_known | 0.1619 | 0.00205 | 0.01862 | 0.897 |
| ind_full_rho0.3 | 0.1484 | 0.00196 | 0.01843 | 0.897 |
| ind_only_rho0.3 | 0.8965 | 0.00245 | 0.02239 | 0.903 |
| ind_full_rho0.6 | 0.1463 | 0.00194 | 0.01837 | 0.897 |
| ind_only_rho0.6 | 0.8965 | 0.00245 | 0.02239 | 0.903 |

## S1|N=300  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1075 | 0.1349 | 0.877 |
| full_known | 0.1110 | 0.1399 | 0.900 |
| ind_full_rho0.3 | 0.5555 | 0.5647 | 0.900 |
| ind_only_rho0.3 | 0.5455 | 0.5455 | 0.900 |
| ind_full_rho0.6 | 0.7536 | 0.7566 | 0.900 |
| ind_only_rho0.6 | 0.7521 | 0.7521 | 0.900 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00006 [-0.00002, 0.00014] | 0.00006 [0.00002, 0.00010] | 0.00056 [0.00026, 0.00086] | 0.00012 [-0.00011, 0.00035] |
| full_fit over B1_fit | 0.00339 [0.00307, 0.00371] | 0.00339 [0.00314, 0.00364] | 0.00449 [0.00384, 0.00514] | 0.00110 [0.00058, 0.00161] |
| full_fit over F0_fit | 0.00345 [0.00310, 0.00380] | 0.00345 [0.00320, 0.00370] | 0.00505 [0.00430, 0.00580] | 0.00122 [0.00067, 0.00177] |
| full_fit over priorF_fit | 0.00299 [0.00260, 0.00338] | 0.00299 [0.00277, 0.00321] | 0.00414 [0.00360, 0.00469] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00319 [0.00287, 0.00352] | 0.00319 [0.00296, 0.00343] | 0.00483 [0.00409, 0.00558] | 0.00059 [0.00018, 0.00100] |
| full_known over F0_known | 0.00340 [0.00309, 0.00371] | 0.00340 [0.00315, 0.00366] | 0.00498 [0.00432, 0.00564] | 0.00122 [0.00074, 0.00171] |
| full_known over full_fit | 0.00054 [0.00040, 0.00067] | 0.00054 [0.00045, 0.00062] | 0.00036 [0.00009, 0.00063] | 0.00058 [0.00006, 0.00110] |
| full_known over priorF_known | 0.00297 [0.00273, 0.00322] | 0.00297 [0.00275, 0.00320] | 0.00412 [0.00363, 0.00462] | -0.00000 [-0.00000, 0.00000] |
| ind_full_rho0.3 over full_known | 0.00960 [0.00935, 0.00984] | 0.00960 [0.00926, 0.00994] | 0.01179 [0.01066, 0.01291] | 0.01293 [0.01022, 0.01563] |
| ind_full_rho0.3 over ind_only_rho0.3 | 0.10176 [0.09942, 0.10410] | 0.10176 [0.09956, 0.10396] | 0.13537 [0.13233, 0.13840] | 0.07749 [0.07160, 0.08339] |
| ind_full_rho0.6 over full_known | 0.01435 [0.01385, 0.01485] | 0.01435 [0.01393, 0.01477] | 0.01831 [0.01688, 0.01974] | 0.01979 [0.01577, 0.02381] |
| ind_full_rho0.6 over ind_only_rho0.6 | 0.10215 [0.09984, 0.10447] | 0.10215 [0.09995, 0.10436] | 0.13600 [0.13279, 0.13920] | 0.07814 [0.07220, 0.08408] |
| oracle_fit over full_fit | 0.02091 [0.02034, 0.02148] | 0.02091 [0.02040, 0.02142] | 0.02591 [0.02413, 0.02770] | 0.03091 [0.02625, 0.03556] |
| oracle_known over full_known | 0.02090 [0.02035, 0.02146] | 0.02090 [0.02040, 0.02140] | 0.02591 [0.02415, 0.02768] | 0.03089 [0.02620, 0.03558] |
| priorF_fit over B1_fit | 0.00040 [0.00018, 0.00062] | 0.00040 [0.00024, 0.00056] | 0.00035 [-0.00006, 0.00075] | 0.00110 [0.00058, 0.00161] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1684 | 0.00255 | 0.02213 | 0.883 |
| B1_fit | 0.1709 | 0.00268 | 0.02515 | 0.868 |
| full_known | 0.1639 | 0.00210 | 0.01892 | 0.895 |
| ind_full_rho0.3 | 0.1494 | 0.00201 | 0.01875 | 0.896 |
| ind_only_rho0.3 | 0.9089 | 0.00255 | 0.02257 | 0.899 |
| ind_full_rho0.6 | 0.1479 | 0.00199 | 0.01868 | 0.895 |
| ind_only_rho0.6 | 0.9089 | 0.00255 | 0.02257 | 0.899 |

## S2|N=1000  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00006 [0.00000, 0.00012] | 0.500 | NA | 0.00003 |
| full_known | 0.00000 [0.00000, 0.00000] | NA | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00001, 0.00001] | 0.00001 [-0.00001, 0.00002] |
| full_fit over B1_fit | -0.00001 [-0.00003, 0.00001] | -0.00001 [-0.00002, 0.00000] | 0.00001 [-0.00001, 0.00003] | 0.00001 [-0.00002, 0.00003] |
| full_fit over F0_fit | -0.00001 [-0.00003, 0.00001] | -0.00001 [-0.00002, 0.00000] | 0.00001 [-0.00002, 0.00003] | 0.00001 [-0.00001, 0.00004] |
| full_fit over priorF_fit | -0.00001 [-0.00003, 0.00001] | -0.00001 [-0.00002, -0.00000] | 0.00000 [-0.00001, 0.00002] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00001 [-0.00004, 0.00001] | -0.00001 [-0.00002, -0.00000] | 0.00001 [-0.00002, 0.00003] | 0.00000 [-0.00001, 0.00001] |
| full_known over F0_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| full_known over full_fit | 0.00015 [0.00012, 0.00019] | 0.00015 [0.00010, 0.00020] | 0.00014 [-0.00000, 0.00028] | -0.00008 [-0.00035, 0.00019] |
| full_known over priorF_known | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | 0.00001 [-0.00001, 0.00003] | 0.00001 [-0.00000, 0.00002] | -0.00001 [-0.00003, 0.00002] | -0.00001 [-0.00004, 0.00001] |
| oracle_known over full_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| priorF_fit over B1_fit | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00001, 0.00002] | 0.00001 [-0.00002, 0.00003] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1481 | 0.00208 | 0.01994 | 0.891 |
| B1_fit | 0.1480 | 0.00207 | 0.01983 | 0.892 |
| full_known | 0.1466 | 0.00197 | 0.01839 | 0.894 |

## S2|N=300  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00010 [0.00002, 0.00019] | 0.279 | NA | 0.00002 |
| full_known | 0.00000 [0.00000, 0.00000] | NA | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00001 [-0.00002, 0.00000] | -0.00001 [-0.00001, -0.00000] | -0.00001 [-0.00002, 0.00001] | -0.00002 [-0.00007, 0.00003] |
| full_fit over B1_fit | 0.00001 [-0.00001, 0.00003] | 0.00001 [-0.00000, 0.00002] | 0.00002 [-0.00002, 0.00005] | 0.00002 [-0.00006, 0.00009] |
| full_fit over F0_fit | 0.00000 [-0.00001, 0.00002] | 0.00000 [-0.00001, 0.00002] | 0.00001 [-0.00002, 0.00004] | 0.00000 [-0.00003, 0.00003] |
| full_fit over priorF_fit | 0.00000 [-0.00001, 0.00001] | 0.00000 [-0.00001, 0.00001] | -0.00000 [-0.00002, 0.00002] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00000 [-0.00001, 0.00001] | -0.00000 [-0.00001, 0.00001] | -0.00000 [-0.00002, 0.00002] | -0.00001 [-0.00002, 0.00000] |
| full_known over F0_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| full_known over full_fit | 0.00053 [0.00042, 0.00065] | 0.00053 [0.00044, 0.00062] | 0.00048 [0.00028, 0.00069] | 0.00061 [0.00012, 0.00110] |
| full_known over priorF_known | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | -0.00000 [-0.00002, 0.00001] | -0.00000 [-0.00002, 0.00001] | -0.00001 [-0.00004, 0.00002] | -0.00000 [-0.00003, 0.00003] |
| oracle_known over full_known | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| priorF_fit over B1_fit | 0.00001 [-0.00001, 0.00003] | 0.00001 [-0.00000, 0.00002] | 0.00002 [-0.00001, 0.00006] | 0.00002 [-0.00006, 0.00009] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1472 | 0.00232 | 0.02236 | 0.879 |
| B1_fit | 0.1472 | 0.00231 | 0.02243 | 0.879 |
| full_known | 0.1421 | 0.00197 | 0.01838 | 0.899 |

## S8|N=1000  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.0987 | 0.1242 | 0.875 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00018 [-0.00022, -0.00014] | -0.00018 [-0.00021, -0.00016] | -0.00015 [-0.00029, -0.00002] | -0.00029 [-0.00045, -0.00014] |
| full_fit over B1_fit | 0.00288 [0.00271, 0.00304] | 0.00288 [0.00266, 0.00310] | 0.00372 [0.00326, 0.00419] | 0.00133 [0.00069, 0.00197] |
| full_fit over F0_fit | 0.00270 [0.00252, 0.00288] | 0.00270 [0.00248, 0.00291] | 0.00357 [0.00308, 0.00405] | 0.00104 [0.00034, 0.00173] |
| full_fit over priorF_fit | 0.00228 [0.00208, 0.00248] | 0.00228 [0.00210, 0.00246] | 0.00247 [0.00205, 0.00290] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00246 [0.00226, 0.00265] | 0.00246 [0.00226, 0.00265] | 0.00305 [0.00260, 0.00351] | 0.00042 [-0.00007, 0.00090] |
| oracle_fit over full_fit | 0.02036 [0.01988, 0.02083] | 0.02036 [0.01986, 0.02085] | 0.02312 [0.02183, 0.02440] | 0.03103 [0.02774, 0.03432] |
| priorF_fit over B1_fit | 0.00060 [0.00048, 0.00072] | 0.00060 [0.00046, 0.00074] | 0.00125 [0.00109, 0.00142] | 0.00133 [0.00069, 0.00197] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1776 | 0.00489 | 0.03527 | 0.933 |
| B1_fit | 0.1943 | 0.00592 | 0.04089 | 0.905 |

## S8|N=300  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.16000000000000003)

### Transient-state recovery R^2 = 1 - MSE/sigma2_F (practice positions; learner-pooled CI)

| arm | pre-answer | post-answer | 90% coverage post |
|---|---|---|---|
| full_fit | 0.1007 | 0.1241 | 0.857 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00011 [-0.00018, -0.00003] | -0.00011 [-0.00014, -0.00007] | 0.00013 [-0.00014, 0.00040] | -0.00019 [-0.00068, 0.00030] |
| full_fit over B1_fit | 0.00262 [0.00231, 0.00292] | 0.00262 [0.00240, 0.00283] | 0.00313 [0.00244, 0.00382] | 0.00153 [0.00069, 0.00238] |
| full_fit over F0_fit | 0.00251 [0.00225, 0.00277] | 0.00251 [0.00230, 0.00272] | 0.00326 [0.00246, 0.00407] | 0.00134 [0.00039, 0.00230] |
| full_fit over priorF_fit | 0.00217 [0.00196, 0.00239] | 0.00217 [0.00199, 0.00235] | 0.00225 [0.00163, 0.00287] | -0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | 0.00230 [0.00208, 0.00252] | 0.00230 [0.00211, 0.00250] | 0.00284 [0.00211, 0.00357] | 0.00066 [0.00010, 0.00122] |
| oracle_fit over full_fit | 0.02059 [0.02017, 0.02101] | 0.02059 [0.02009, 0.02109] | 0.02483 [0.02367, 0.02598] | 0.03280 [0.02993, 0.03567] |
| priorF_fit over B1_fit | 0.00044 [0.00017, 0.00071] | 0.00044 [0.00030, 0.00058] | 0.00088 [0.00055, 0.00121] | 0.00153 [0.00069, 0.00238] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1785 | 0.00545 | 0.03902 | 0.930 |
| B1_fit | 0.1947 | 0.00639 | 0.04214 | 0.902 |

## S8n|N=1000  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00000 [-0.00000, 0.00000] | 0.001 | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, -0.00000] | -0.00000 [-0.00001, 0.00000] | -0.00000 [-0.00001, 0.00000] |
| full_fit over B1_fit | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] |
| full_fit over F0_fit | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] |
| full_fit over priorF_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00001, 0.00000] | -0.00000 [-0.00001, 0.00000] |
| priorF_fit over B1_fit | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1625 | 0.00459 | 0.03490 | 0.932 |
| B1_fit | 0.1625 | 0.00459 | 0.03492 | 0.931 |

## S8n|N=300  (20 fitted replications, fresh evaluation learners, sigma2_F true 0.0)

### Excursions of the post-answer transient estimate (true F = 0; absolute units)

| arm | energy E[m^2] (practice) | lag-1 autocorr | mean run length (|m|>0.2) | pre-answer energy |
|---|---|---|---|---|
| full_fit | 0.00004 [-0.00000, 0.00008] | 0.030 | NA | 0.00000 |

### Causal log-loss gains, nats per response (positive = first arm better); replication CI | learner CI

| X over Y | practice (rep CI) | practice (learner CI) | probe (rep CI) | first answer (rep CI) |
|---|---|---|---|---|
| B1_fit over F0_fit | -0.00000 [-0.00001, 0.00000] | -0.00000 [-0.00001, -0.00000] | -0.00001 [-0.00003, 0.00001] | -0.00001 [-0.00002, 0.00001] |
| full_fit over B1_fit | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] | 0.00002 [-0.00000, 0.00004] | 0.00001 [-0.00003, 0.00005] |
| full_fit over F0_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00001, 0.00001] | 0.00001 [-0.00001, 0.00002] | 0.00000 [-0.00004, 0.00005] |
| full_fit over priorF_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] |
| full_fit over white_fit | -0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00000, 0.00000] | -0.00000 [-0.00000, 0.00000] |
| oracle_fit over full_fit | 0.00000 [-0.00000, 0.00000] | 0.00000 [-0.00001, 0.00001] | -0.00001 [-0.00002, 0.00001] | -0.00000 [-0.00005, 0.00004] |
| priorF_fit over B1_fit | 0.00000 [-0.00000, 0.00001] | 0.00000 [-0.00000, 0.00001] | 0.00002 [-0.00000, 0.00004] | 0.00001 [-0.00003, 0.00005] |

### Persistent coordinates after the last practice answer (MSE; learner-pooled)

| arm | M0 | alpha | r | M0 90% cover |
|---|---|---|---|---|
| full_fit | 0.1687 | 0.00513 | 0.04188 | 0.924 |
| B1_fit | 0.1685 | 0.00512 | 0.04196 | 0.924 |

## Null safety (R3): spurious tracking gain of B2-full over B2-priorF

- **S2|N=1000**: -0.00001 [-0.00003, 0.00001] nats/response -> spurious tracking gain: **False**
- **S2|N=300**: 0.00000 [-0.00001, 0.00001] nats/response -> spurious tracking gain: **False**
- **S8n|N=1000**: -0.00000 [-0.00000, 0.00000] nats/response -> spurious tracking gain: **False**; sensitivity excluding flagged fit(s) {'excluded': [13], 'n_reps_kept': 19, 'gain_full_over_priorF_practice': {'mean': 2.9033838029338744e-10, 'se': 1.0131040030636172e-09, 'lo': -1.8381141487993902e-09, 'hi': 2.418790909386165e-09, 'R': 19}, 'spurious_tracking_gain': False}
- **S8n|N=300**: -0.00000 [-0.00000, 0.00000] nats/response -> spurious tracking gain: **False**

## Production reference (all S1 N=1000 evaluation learners): gap decomposition

- 6000 learners, 20 replications, 32768 particles, min ESS 7165
- **R0 (implementation validity)**: passed = **True**  {'R2_ref_pre': {'excess_over_bound': -0.0006316697483766953, 'learner_se': 0.004429403718116775, 'ok': True}, 'R2_adf_known_pre': {'excess_over_bound': -0.0006154462018967966, 'learner_se': 0.004430184177657508, 'ok': True}, 'R2_ref_post': {'excess_over_bound': -0.0015745726396244608, 'learner_se': 0.004347629849337117, 'ok': True}, 'R2_adf_known_post': {'excess_over_bound': -0.001560217975839162, 'learner_se': 0.004348150738514587, 'ok': True}, 'track_S1|N=1000_full_known_pre': {'excess_over_bound': -0.0006525145389241205, 'learner_se': 0.004430184177657508, 'ok': True}, 'track_S1|N=1000_full_known_post': {'excess_over_bound': -0.001590478374898563, 'learner_se': 0.004348150738514587, 'ok': True}, 'track_S1|N=300_full_known_pre': {'excess_over_bound': -0.0024941771408092395, 'learner_se': 0.004456347384290249, 'ok': True}, 'track_S1|N=300_full_known_post': {'excess_over_bound': -0.0036232106975849776, 'learner_se': 0.004379312257898159, 'ok': True}}
- **R2 (ADF approximation, production learners)**: {'mean_abs_dp_adf_known_practice': 0.002818380789951374, 'mean_abs_dp_adf_fit_practice': 0.006571864397523932, 'logloss_gain_ref_over_adf_known_practice': {'mean': 5.963714435910479e-05, 'se': 1.4008363488388101e-05, 'lo': 3.218075192186411e-05, 'hi': 8.709353679634547e-05, 'n': 6000}, 'mean_abs_dp_le_0.005': True, 'logloss_gain_ci_within_pm_5e-4': True, 'adf_approximation_negligible_for_forecasting': True}

R^2 = 1 - MSE/sigma2_F. Order expected: bound >= reference >= ADF(known) >= ADF(fitted). Learner CIs.

| phase | bin | bound | reference | ADF known | ADF fitted | approx. loss (ref - ADF known) | estimation loss (ADF known - fitted), learner CI | estimation loss, replication CI |
|---|---|---|---|---|---|---|---|---|
| pre | practice | 0.1134 | 0.1128 [0.1041, 0.1215] | 0.1128 [0.1042, 0.1215] | 0.1118 [0.1031, 0.1205] | -0.00002 [-0.00010, 0.00007] | 0.00105 [0.00064, 0.00146] | 0.00105 [0.00033, 0.00178] |
| pre | first | -0.0000 | -0.0008 [-0.0217, 0.0200] | -0.0008 [-0.0217, 0.0200] | -0.0008 [-0.0217, 0.0200] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] | 0.00000 [0.00000, 0.00000] |
| pre | j1_4 | 0.0782 | 0.0862 [0.0702, 0.1023] | 0.0861 [0.0701, 0.1022] | 0.0854 [0.0693, 0.1014] | 0.00011 [0.00002, 0.00020] | 0.00077 [0.00015, 0.00138] | 0.00077 [0.00003, 0.00150] |
| pre | j5_15 | 0.1238 | 0.1250 [0.1123, 0.1376] | 0.1250 [0.1123, 0.1376] | 0.1238 [0.1112, 0.1365] | -0.00002 [-0.00014, 0.00009] | 0.00113 [0.00055, 0.00172] | 0.00113 [0.00031, 0.00195] |
| pre | j16_31 | 0.1222 | 0.1182 [0.1070, 0.1294] | 0.1183 [0.1071, 0.1294] | 0.1171 [0.1060, 0.1283] | -0.00005 [-0.00017, 0.00008] | 0.00114 [0.00051, 0.00176] | 0.00114 [0.00024, 0.00203] |
| pre | probe | 0.1246 | 0.1160 [0.0966, 0.1354] | 0.1160 [0.0966, 0.1354] | 0.1143 [0.0948, 0.1337] | 0.00000 [-0.00016, 0.00017] | 0.00173 [0.00088, 0.00258] | 0.00173 [0.00061, 0.00286] |
| post | practice | 0.1435 | 0.1420 [0.1334, 0.1505] | 0.1420 [0.1335, 0.1505] | 0.1402 [0.1317, 0.1488] | -0.00001 [-0.00011, 0.00008] | 0.00172 [0.00123, 0.00222] | 0.00172 [0.00056, 0.00289] |
| post | first | 0.0559 | 0.0596 [0.0399, 0.0792] | 0.0595 [0.0398, 0.0791] | 0.0589 [0.0392, 0.0785] | 0.00008 [-0.00001, 0.00016] | 0.00061 [-0.00029, 0.00151] | 0.00061 [-0.00024, 0.00146] |
| post | j1_4 | 0.1150 | 0.1205 [0.1050, 0.1359] | 0.1203 [0.1048, 0.1358] | 0.1186 [0.1032, 0.1341] | 0.00014 [0.00002, 0.00025] | 0.00168 [0.00083, 0.00253] | 0.00168 [0.00021, 0.00314] |
| post | j5_15 | 0.1520 | 0.1520 [0.1397, 0.1643] | 0.1520 [0.1397, 0.1644] | 0.1504 [0.1380, 0.1627] | -0.00004 [-0.00016, 0.00009] | 0.00170 [0.00098, 0.00242] | 0.00170 [0.00041, 0.00299] |
| post | j16_31 | 0.1503 | 0.1456 [0.1346, 0.1565] | 0.1456 [0.1347, 0.1566] | 0.1438 [0.1329, 0.1547] | -0.00004 [-0.00018, 0.00010] | 0.00183 [0.00110, 0.00255] | 0.00183 [0.00056, 0.00309] |
| post | probe | 0.1636 | 0.1533 [0.1346, 0.1721] | 0.1533 [0.1346, 0.1721] | 0.1508 [0.1320, 0.1696] | 0.00002 [-0.00017, 0.00021] | 0.00252 [0.00145, 0.00359] | 0.00252 [0.00067, 0.00436] |

Causal log-loss gains on the production learners, nats per response (practice; positive = first arm better):

- ref over adf_known: learner CI 0.00006 [0.00003, 0.00009]; replication CI 0.00006 [0.00003, 0.00009]
- adf_known over adf_fit: learner CI 0.00019 [0.00013, 0.00024]; replication CI 0.00019 [0.00011, 0.00026]
- adf_fit over B1_fit: learner CI 0.00341 [0.00315, 0.00366]; replication CI 0.00341 [0.00310, 0.00372]

- provenance: {'jobs_with_hashes': 190, 'numpy': ['2.4.6'], 'scipy': ['1.17.1']}

## SMC reference: gates (R1) and ADF approximation (R2)

- 160 learners from 10 replications, 10 independent seeds, 32768 particles; min ESS 7485
- **R1** {'R2_single_run_mc_sd_le_0.002': True, 'p_single_run_mc_rms_le_0.001': True, 'doubling_within_2se': True, 'orthant_check': 'unit test test_smc_matches_orthant (tests/test_transient_filtering.py)', 'passed': True}
- R2 on this validation subset (indicative only): {'mean_abs_dp_le_0.005': True, 'logloss_gain_ci_within_pm_5e-4': True, 'adf_approximation_negligible_for_forecasting': True}
- single-run MC SD of R^2: pre 0.00006, post 0.00006; single-run RMS MC SD of p: 0.00081
- R^2 (practice, these learners) post: reference 0.1414, ADF 0.1411, bound 0.1436 (ref - bound -0.0021, learner-sampling SE 0.0288); pre: ref 0.1145, ADF 0.1142, bound 0.1135
- ADF vs reference: mean |dp| (practice) 0.00271; log-loss gain of reference over ADF 0.000122 [-0.000030, 0.000273] nats/response; delta R^2 post (ref - ADF) {'mean': 0.000377662535188733, 'se': 0.0003296246723075962}
- B1 (fitted) ADF vs reference: mean |dp| 0.00320; gain 0.000068 [-0.000119, 0.000255]

