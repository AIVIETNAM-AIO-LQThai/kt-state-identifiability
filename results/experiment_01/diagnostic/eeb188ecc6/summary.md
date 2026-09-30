# Experiment 1 summary — stage `diagnostic`

- config hash `eeb188ecc650`, code hash `dd1c3c835d74`, git `943db5acfb` (dirty: False)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v50-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: 30/30 fit jobs ok; 0 errors; total CPU 10.75 h

## S1|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.68e-09 | 0 (0) | 19 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.97e-08 | 0 (0) | 35 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 3.44e-08 | 0 (0) | 51 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1771 | 0.0083 | 0.1775 | 3 |
| B0 | phi | 0.2000 | 0.1500 | 0.0040 | 0.1501 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0094 | 0.0049 | 0.0117 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0020 | 0.0067 | 0.0097 | 3 |
| B1 | phi | 0.2000 | 0.0012 | 0.0017 | 0.0027 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0013 | 0.0010 | 0.0019 | 3 |
| B1 | r_bar | 0.3500 | 0.0083 | 0.0111 | 0.0177 | 3 |
| B1 | tau_R | 5.0000 | -0.2972 | 0.1989 | 0.4092 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0266 | 0.0218 | 0.0408 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0066 | 0.0067 | 0.0115 | 3 |
| B2 | phi | 0.2000 | 0.0040 | 0.0012 | 0.0043 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0004 | 0.0009 | 0.0014 | 3 |
| B2 | r_bar | 0.3500 | 0.0055 | 0.0090 | 0.0138 | 3 |
| B2 | tau_R | 5.0000 | -0.2558 | 0.1906 | 0.3716 | 3 |
| B2 | sigma2_r | 0.0225 | 0.0008 | 0.0130 | 0.0184 | 3 |
| B2 | sigma2_F | 0.1600 | 0.0015 | 0.0224 | 0.0317 | 3 |
| B2 | tau_F | 10.0000 | 1.7862 | 3.0793 | 4.7068 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': 1.7862088110018683, 'mcse_bias': np.float64(3.0792651772035193), 'sd': 5.333443736894077, 'rmse': 4.706834390498262}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 3/3 [3/3]; r_bar: 3/3 [3/3]; tau_R: 3/3 [3/3]; sigma2_r: 2/2 [2/3]; sigma2_F: 3/3 [3/3]; tau_F: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00361 (MCSE 0.00014; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00000 (MCSE 0.00007; positive in 2/3)
- pairwise_composite_log_score:B1-B0: 46.25140 (MCSE 1.67921; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 1.08274 (MCSE 0.56096; positive in 2/3)

## S2|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.39e-09 | 0 (0) | 19 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.02e-09 | 0 (0) | 34 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.35e-09 | 0 (0) | 31 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1754 | 0.0089 | 0.1759 | 3 |
| B0 | phi | 0.2000 | 0.1445 | 0.0067 | 0.1449 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0082 | 0.0030 | 0.0092 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0047 | 0.0070 | 0.0109 | 3 |
| B1 | phi | 0.2000 | 0.0037 | 0.0076 | 0.0114 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0005 | 0.0012 | 0.0017 | 3 |
| B1 | r_bar | 0.3500 | -0.0088 | 0.0219 | 0.0323 | 3 |
| B1 | tau_R | 5.0000 | 0.0241 | 0.4182 | 0.5920 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0039 | 0.0180 | 0.0258 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0047 | 0.0070 | 0.0109 | 3 |
| B2 | phi | 0.2000 | 0.0037 | 0.0076 | 0.0114 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0005 | 0.0012 | 0.0017 | 3 |
| B2 | r_bar | 0.3500 | -0.0088 | 0.0219 | 0.0323 | 3 |
| B2 | tau_R | 5.0000 | 0.0241 | 0.4182 | 0.5920 | 3 |
| B2 | sigma2_r | 0.0225 | 0.0039 | 0.0180 | 0.0258 | 3 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0000; share at 0: 1.00 | NA | 3 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 13.0007 | NA | 3 |

B2: share of fits with sigma2_F at 0: 1.00; boundary hits: {'sigma2_r@lower': 0.3333333333333333, 'sigma2_F@lower': 1.0}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 2/3 [2/3]; r_bar: 3/3 [3/3]; tau_R: 3/3 [3/3]; sigma2_r: 2/2 [2/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00374 (MCSE 0.00021; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00000 (MCSE 0.00000; positive in 2/3)
- pairwise_composite_log_score:B1-B0: 47.73049 (MCSE 2.70536; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 0.00000 (MCSE 0.00000; positive in 2/3)

## S3|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['no_fast_recency'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.71e-09 | 0 (0) | 21 |
| B1 | 3 | 0 | 1.00 | 0.00 | 3.0 | 0.00 | 1.00 | 1.17e-08 | 0 (0) | 45 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.93e-08 | 0 (0) | 58 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.0088 | 0.0173 | 0.0260 | 3 |
| B0 | phi | 0.2000 | 0.0138 | 0.0164 | 0.0269 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0015 | 0.0008 | 0.0019 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0116 | 0.0203 | 0.0309 | 3 |
| B1 | phi | 0.2000 | 0.0163 | 0.0197 | 0.0322 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0015 | 0.0009 | 0.0020 | 3 |
| B1 | r_bar | 0.0000 | 0.0358 | 0.1156 | 0.1673 | 3 |
| B1 | tau_R | 5.0000 | NA (inactive: no fast recency in the generating process) | mean estimate 2.9836 | NA | 3 |
| B1 | sigma2_r | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.7508; share at 0: 0.00 | NA | 3 |
| B2 | alpha_bar | 0.1500 | 0.0148 | 0.0210 | 0.0331 | 3 |
| B2 | phi | 0.2000 | 0.0177 | 0.0197 | 0.0331 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0007 | 0.0008 | 0.0014 | 3 |
| B2 | r_bar | 0.0000 | 0.0409 | 0.1304 | 0.1889 | 3 |
| B2 | tau_R | 5.0000 | NA (inactive: no fast recency in the generating process) | mean estimate 4.1699 | NA | 3 |
| B2 | sigma2_r | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.6667; share at 0: 0.67 | NA | 3 |
| B2 | sigma2_F | 0.1600 | -0.0336 | 0.0046 | 0.0343 | 3 |
| B2 | tau_F | 10.0000 | 2.4777 | 1.0650 | 2.8996 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 0.6666666666666666, 'sigma2_r@upper': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': 2.4777408330941117, 'mcse_bias': np.float64(1.065004898945922), 'sd': 1.8446425952840948, 'rmse': 2.8995983352077457}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 2/3 [2/3]; phi: 2/3 [2/3]; sigma2_alpha: 3/3 [3/3]; r_bar: 3/3 [3/3]; sigma2_F: 3/3 [3/3]; tau_F: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: -0.00004 (MCSE 0.00004; positive in 1/3)
- marginal_bernoulli_log_score:B2-B1: 0.00002 (MCSE 0.00003; positive in 2/3)
- pairwise_composite_log_score:B1-B0: -0.43545 (MCSE 0.43545; positive in 1/3)
- pairwise_composite_log_score:B2-B1: 1.12513 (MCSE 0.15115; positive in 3/3)

## S4a|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 7.77e-10 | 0 (0) | 18 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.15e-08 | 0 (0) | 32 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 8.47e-09 | 0 (0) | 56 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.2057 | 0.0161 | 0.2070 | 3 |
| B0 | phi | 0.2000 | 0.1820 | 0.0108 | 0.1826 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0130 | 0.0018 | 0.0132 | 3 |
| B1 | alpha_bar | 0.1500 | -0.0013 | 0.0035 | 0.0051 | 3 |
| B1 | phi | 0.2000 | 0.0024 | 0.0023 | 0.0041 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0018 | 0.0004 | 0.0019 | 3 |
| B1 | r_bar | 0.3500 | -0.0068 | 0.0293 | 0.0419 | 3 |
| B1 | tau_R | 5.0000 | 0.4045 | 0.4607 | 0.7669 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0127 | 0.0133 | 0.0228 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0029 | 0.0040 | 0.0064 | 3 |
| B2 | phi | 0.2000 | 0.0048 | 0.0025 | 0.0059 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0012 | 0.0005 | 0.0014 | 3 |
| B2 | r_bar | 0.3500 | -0.0064 | 0.0282 | 0.0405 | 3 |
| B2 | tau_R | 5.0000 | 0.4203 | 0.4538 | 0.7672 | 3 |
| B2 | sigma2_r | 0.0225 | -0.0038 | 0.0096 | 0.0141 | 3 |
| B2 | sigma2_F | 0.1600 | -0.0151 | 0.0090 | 0.0198 | 3 |
| B2 | tau_F | 0.2000 | -0.0015 | 0.0749 | 0.1060 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': -0.0014780669986290962, 'mcse_bias': np.float64(0.0749129995167104), 'sd': 0.12975312131032515, 'rmse': 0.1059532900632809}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 3/3 [3/3]; r_bar: 3/3 [3/3]; tau_R: 2/3 [2/3]; sigma2_r: 2/2 [2/3]; sigma2_F: 3/3 [3/3]; tau_F: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00327 (MCSE 0.00013; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00004 (MCSE 0.00001; positive in 3/3)
- pairwise_composite_log_score:B1-B0: 41.79646 (MCSE 1.65443; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 1.17173 (MCSE 0.15711; positive in 3/3)

## S4b|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.93e-09 | 0 (0) | 17 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 9.47e-09 | 0 (0) | 30 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.02e-08 | 0 (0) | 45 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.2120 | 0.0137 | 0.2129 | 3 |
| B0 | phi | 0.2000 | 0.1967 | 0.0285 | 0.2008 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0141 | 0.0019 | 0.0143 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0154 | 0.0089 | 0.0199 | 3 |
| B1 | phi | 0.2000 | 0.0263 | 0.0046 | 0.0272 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0034 | 0.0004 | 0.0035 | 3 |
| B1 | r_bar | 0.3500 | -0.0183 | 0.0264 | 0.0415 | 3 |
| B1 | tau_R | 5.0000 | -0.0421 | 0.0103 | 0.0446 | 3 |
| B1 | sigma2_r | 0.0225 | -0.0200 | 0.0025 | 0.0203 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0194 | 0.0089 | 0.0231 | 3 |
| B2 | phi | 0.2000 | 0.0286 | 0.0045 | 0.0293 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0020 | 0.0002 | 0.0020 | 3 |
| B2 | r_bar | 0.3500 | -0.0129 | 0.0265 | 0.0396 | 3 |
| B2 | tau_R | 5.0000 | -0.0293 | 0.0085 | 0.0317 | 3 |
| B2 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 3 |
| B2 | sigma2_F | 0.1600 | 0.0283 | 0.0335 | 0.0552 | 3 |
| B2 | tau_F | 60.0000 | 25.7440 | 36.5383 | 57.7309 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 1.0}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': 25.744026509235283, 'mcse_bias': np.float64(36.538346944712515), 'sd': 63.286273332821125, 'rmse': 57.73089723720369}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 3/3 [3/3]; r_bar: 2/3 [2/3]; tau_R: 3/3 [3/3]; sigma2_r: 0/0 [0/3]; sigma2_F: 2/3 [2/3]; tau_F: 2/3 [2/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00320 (MCSE 0.00042; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: -0.00003 (MCSE 0.00004; positive in 1/3)
- pairwise_composite_log_score:B1-B0: 41.07834 (MCSE 5.40016; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 1.03573 (MCSE 0.20889; positive in 3/3)

## S5|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['weak_interleaving'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.79e-10 | 0 (0) | 16 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.73e-09 | 0 (0) | 35 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 9.05e-09 | 0 (0) | 55 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.4492 | 0.0125 | 0.4495 | 3 |
| B0 | phi | 0.2000 | 0.2787 | 0.0053 | 0.2788 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0265 | 0.0018 | 0.0267 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0022 | 0.0049 | 0.0073 | 3 |
| B1 | phi | 0.2000 | 0.0183 | 0.0059 | 0.0202 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0014 | 0.0014 | 0.0025 | 3 |
| B1 | r_bar | 0.3500 | 0.0104 | 0.0272 | 0.0399 | 3 |
| B1 | tau_R | 5.0000 | -0.2732 | 0.4765 | 0.7272 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0001 | 0.0040 | 0.0056 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0066 | 0.0045 | 0.0092 | 3 |
| B2 | phi | 0.2000 | 0.0218 | 0.0062 | 0.0235 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0008 | 0.0015 | 0.0022 | 3 |
| B2 | r_bar | 0.3500 | 0.0136 | 0.0273 | 0.0409 | 3 |
| B2 | tau_R | 5.0000 | -0.2953 | 0.4720 | 0.7299 | 3 |
| B2 | sigma2_r | 0.0225 | -0.0026 | 0.0041 | 0.0063 | 3 |
| B2 | sigma2_F | 0.1600 | -0.0154 | 0.0123 | 0.0233 | 3 |
| B2 | tau_F | 10.0000 | -0.4496 | 1.0081 | 1.4949 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': -0.4496317900379288, 'mcse_bias': np.float64(1.0081128959928598), 'sd': 1.7461027556250324, 'rmse': 1.4949086824107125}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 3/3 [3/3]; r_bar: 2/3 [2/3]; tau_R: 2/3 [2/3]; sigma2_r: 3/3 [3/3]; sigma2_F: 3/3 [3/3]; tau_F: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.01593 (MCSE 0.00133; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00005 (MCSE 0.00003; positive in 2/3)
- pairwise_composite_log_score:B1-B0: 205.08697 (MCSE 17.16928; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 0.96636 (MCSE 0.23333; positive in 3/3)

## S6|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['session_reset'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.13e-09 | 0 (0) | 16 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 3.78e-09 | 0 (0) | 27 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 8.50e-09 | 0 (0) | 42 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.2276 | 0.0062 | 0.2278 | 3 |
| B0 | phi | 0.2000 | 0.1825 | 0.0092 | 0.1830 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0068 | 0.0048 | 0.0096 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0335 | 0.0045 | 0.0341 | 3 |
| B1 | phi | 0.2000 | 0.0284 | 0.0021 | 0.0286 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0004 | 0.0012 | 0.0018 | 3 |
| B1 | r_bar | 0.3500 | 0.0139 | 0.0215 | 0.0334 | 3 |
| B1 | tau_R | 5.0000 | -0.3810 | 0.2207 | 0.4925 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0271 | 0.0201 | 0.0393 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0390 | 0.0053 | 0.0397 | 3 |
| B2 | phi | 0.2000 | 0.0307 | 0.0015 | 0.0308 | 3 |
| B2 | sigma2_alpha | 0.0025 | -0.0005 | 0.0012 | 0.0018 | 3 |
| B2 | r_bar | 0.3500 | 0.0113 | 0.0211 | 0.0318 | 3 |
| B2 | tau_R | 5.0000 | -0.3322 | 0.2134 | 0.4488 | 3 |
| B2 | sigma2_r | 0.0225 | -0.0001 | 0.0147 | 0.0208 | 3 |
| B2 | sigma2_F | 0.1600 | 0.0186 | 0.0361 | 0.0544 | 3 |
| B2 | tau_F | 10.0000 | -1.3949 | 2.2971 | 3.5355 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_alpha@lower': 0.3333333333333333, 'sigma2_r@lower': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': -1.3949075997927312, 'mcse_bias': np.float64(2.2971420715056436), 'sd': 3.9787667800517936, 'rmse': 3.5354618659125707}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 2/3 [2/3]; phi: 3/3 [3/3]; sigma2_alpha: 2/2 [2/3]; r_bar: 3/3 [3/3]; tau_R: 3/3 [3/3]; sigma2_r: 2/2 [2/3]; sigma2_F: 3/3 [3/3]; tau_F: 2/3 [2/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00363 (MCSE 0.00021; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: -0.00001 (MCSE 0.00001; positive in 1/3)
- pairwise_composite_log_score:B1-B0: 46.62582 (MCSE 2.76641; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 0.75769 (MCSE 0.06128; positive in 3/3)

## S7|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['schedule_context_exogeneity'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.43e-08 | 0 (0) | 47 |
| B1 | 3 | 0 | 1.00 | 0.00 | 4.7 | 0.00 | 0.33 | 3.31e-08 | 0 (0) | 59 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.00e-07 | 0 (0) | 78 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | -0.1294 | 0.0009 | 0.1294 | 3 |
| B0 | phi | 0.2000 | -0.1975 | 0.0000 | 0.1975 | 3 |
| B0 | sigma2_alpha | 0.0025 | -0.0023 | 0.0001 | 0.0023 | 3 |
| B1 | alpha_bar | 0.1500 | -0.0796 | 0.0017 | 0.0796 | 3 |
| B1 | phi | 0.2000 | -0.1267 | 0.0020 | 0.1267 | 3 |
| B1 | sigma2_alpha | 0.0025 | -0.0007 | 0.0009 | 0.0015 | 3 |
| B1 | r_bar | 0.3500 | -0.4818 | 0.0022 | 0.4818 | 3 |
| B1 | tau_R | 5.0000 | 115.0000 | 0.0000 | 115.0000 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0051 | 0.0016 | 0.0055 | 3 |
| B2 | alpha_bar | 0.1500 | -0.0779 | 0.0016 | 0.0780 | 3 |
| B2 | phi | 0.2000 | -0.1266 | 0.0014 | 0.1266 | 3 |
| B2 | sigma2_alpha | 0.0025 | -0.0011 | 0.0007 | 0.0015 | 3 |
| B2 | r_bar | 0.3500 | -0.4851 | 0.0022 | 0.4851 | 3 |
| B2 | tau_R | 5.0000 | 115.0000 | 0.0000 | 115.0000 | 3 |
| B2 | sigma2_r | 0.0225 | 0.0016 | 0.0016 | 0.0028 | 3 |
| B2 | sigma2_F | 0.1600 | 0.1446 | 0.0027 | 0.1446 | 3 |
| B2 | tau_F | 10.0000 | 81.5300 | 14.1891 | 83.9631 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'tau_R@upper': 1.0, 'sigma2_alpha@lower': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': 81.52998244816484, 'mcse_bias': np.float64(14.189132619948122), 'sd': 24.576298613083043, 'rmse': 83.96309312436638}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 0/3 [0/3]; phi: 0/3 [0/3]; sigma2_alpha: 2/2 [2/3]; r_bar: 0/3 [0/3]; tau_R: 0/0 [0/3]; sigma2_r: 3/3 [3/3]; sigma2_F: 0/3 [0/3]; tau_F: 0/3 [0/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00926 (MCSE 0.00141; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00007 (MCSE 0.00001; positive in 3/3)
- pairwise_composite_log_score:B1-B0: 126.70566 (MCSE 16.32789; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 6.11866 (MCSE 0.72430; positive in 3/3)

## S8|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.95e-09 | 0 (0) | 19 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 7.89e-09 | 0 (0) | 34 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.34e-08 | 0 (0) | 53 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1441 | 0.0063 | 0.1443 | 3 |
| B0 | phi | 0.2000 | 0.1441 | 0.0078 | 0.1445 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0246 | 0.0017 | 0.0247 | 3 |
| B1 | alpha_bar | 0.1500 | -0.0179 | 0.0043 | 0.0189 | 3 |
| B1 | phi | 0.2000 | -0.0086 | 0.0102 | 0.0168 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0048 | 0.0003 | 0.0048 | 3 |
| B1 | r_bar | 0.3500 | -0.0095 | 0.0094 | 0.0164 | 3 |
| B1 | tau_R | 5.0000 | -0.3344 | 0.1586 | 0.4027 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0875 | 0.0458 | 0.1089 | 3 |
| B2 | alpha_bar | 0.1500 | -0.0142 | 0.0044 | 0.0155 | 3 |
| B2 | phi | 0.2000 | -0.0055 | 0.0103 | 0.0156 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0043 | 0.0003 | 0.0044 | 3 |
| B2 | r_bar | 0.3500 | -0.0125 | 0.0094 | 0.0182 | 3 |
| B2 | tau_R | 5.0000 | -0.3146 | 0.1554 | 0.3837 | 3 |
| B2 | sigma2_r | 0.0225 | 0.0593 | 0.0444 | 0.0864 | 3 |
| B2 | sigma2_F | 0.1600 | -0.0388 | 0.0080 | 0.0404 | 3 |
| B2 | tau_F | 10.0000 | 1.3493 | 0.9035 | 1.8583 | 3 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 0.3333333333333333}
B2: tau_F error when sigma2_F > 0: {'n': 3, 'bias': 1.349290178479242, 'mcse_bias': np.float64(0.90354816320404), 'sd': 1.564991325754933, 'rmse': 1.8583278914656942}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 1/3 [1/3]; r_bar: 3/3 [3/3]; tau_R: 3/3 [3/3]; sigma2_r: 0/2 [0/3]; sigma2_F: 3/3 [3/3]; tau_F: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00262 (MCSE 0.00017; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: 0.00001 (MCSE 0.00005; positive in 2/3)
- pairwise_composite_log_score:B1-B0: 34.52578 (MCSE 2.04357; positive in 3/3)
- pairwise_composite_log_score:B2-B1: 0.54796 (MCSE 0.20411; positive in 3/3)

## S8n|N=300  (fit N=300, held-out N=300, generated 600; 3 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.10e-09 | 0 (0) | 17 |
| B1 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.02e-09 | 0 (0) | 29 |
| B2 | 3 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.97e-04 | 0 (0) | 37 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1841 | 0.0236 | 0.1871 | 3 |
| B0 | phi | 0.2000 | 0.1734 | 0.0240 | 0.1767 | 3 |
| B0 | sigma2_alpha | 0.0025 | 0.0340 | 0.0074 | 0.0356 | 3 |
| B1 | alpha_bar | 0.1500 | 0.0177 | 0.0102 | 0.0228 | 3 |
| B1 | phi | 0.2000 | 0.0301 | 0.0123 | 0.0348 | 3 |
| B1 | sigma2_alpha | 0.0025 | 0.0100 | 0.0030 | 0.0108 | 3 |
| B1 | r_bar | 0.3500 | -0.0093 | 0.0157 | 0.0241 | 3 |
| B1 | tau_R | 5.0000 | -0.6222 | 0.2163 | 0.6933 | 3 |
| B1 | sigma2_r | 0.0225 | 0.0208 | 0.0170 | 0.0318 | 3 |
| B2 | alpha_bar | 0.1500 | 0.0183 | 0.0107 | 0.0237 | 3 |
| B2 | phi | 0.2000 | 0.0305 | 0.0125 | 0.0353 | 3 |
| B2 | sigma2_alpha | 0.0025 | 0.0100 | 0.0030 | 0.0108 | 3 |
| B2 | r_bar | 0.3500 | -0.0095 | 0.0159 | 0.0245 | 3 |
| B2 | tau_R | 5.0000 | -0.6207 | 0.2177 | 0.6929 | 3 |
| B2 | sigma2_r | 0.0225 | 0.0175 | 0.0153 | 0.0278 | 3 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0155; share at 0: 0.33 | NA | 3 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 0.5167 | NA | 3 |

B2: share of fits with sigma2_F at 0: 0.33; boundary hits: {'sigma2_F@lower': 0.3333333333333333, 'tau_F@lower': 0.3333333333333333}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 3/3 [3/3]; phi: 3/3 [3/3]; sigma2_alpha: 0/3 [0/3]; r_bar: 3/3 [3/3]; tau_R: 3/3 [3/3]; sigma2_r: 3/3 [3/3]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00253 (MCSE 0.00011; positive in 3/3)
- marginal_bernoulli_log_score:B2-B1: -0.00001 (MCSE 0.00001; positive in 1/3)
- pairwise_composite_log_score:B1-B0: 32.91393 (MCSE 1.27606; positive in 3/3)
- pairwise_composite_log_score:B2-B1: -0.06625 (MCSE 0.06728; positive in 1/3)

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | CLR obs | B ok/failed | p | reject@0.05 | sigma2_F hat | true |
|---|---|---|---|---|---|---|
| S1|N=300|rep=0 | 649.40 | 49/0 | 0.020 (min 0.020) | True | 0.140 | 0.160 |
| S1|N=300|rep=1 | 622.49 | 49/0 | 0.020 (min 0.020) | True | 0.138 | 0.160 |
| S1|N=300|rep=2 | 1113.65 | 49/0 | 0.020 (min 0.020) | True | 0.206 | 0.160 |
| S2|N=300|rep=0 | 0.00 | 49/0 | 0.600 (min 0.020) | False | 0.000 | 0.000 |
| S2|N=300|rep=1 | 0.00 | 49/0 | 0.660 (min 0.020) | False | 0.000 | 0.000 |
| S2|N=300|rep=2 | 0.00 | 49/0 | 0.980 (min 0.020) | False | 0.000 | 0.000 |
| S8n|N=300|rep=0 | 0.01 | 49/0 | 0.500 (min 0.020) | False | 0.000 | 0.000 |
| S8n|N=300|rep=1 | 0.00 | 49/0 | 0.960 (min 0.020) | False | 0.000 | 0.000 |
| S8n|N=300|rep=2 | 56.70 | 49/0 | 0.160 (min 0.020) | False | 0.046 | 0.000 |

## Learner bootstrap vs sandwich SE (B2)

- S1|N=300|rep=0: replicates ok 50/50; bootstrap SD {'alpha_bar': 0.0195, 'phi': 0.0221, 'sigma2_alpha': 0.0014, 'r_bar': 0.0338, 'tau_R': 0.4973, 'sigma2_r': 0.0363, 'sigma2_F': 0.0414, 'tau_F': 14.0813}; sandwich SE {'alpha_bar': 0.02186069551992135, 'phi': 0.028079011029564418, 'sigma2_alpha': 0.0018362424984651857, 'r_bar': 0.040913138670117505, 'tau_R': 0.5315856701624541, 'sigma2_r': 0.04496736037726784, 'sigma2_F': 0.03726080997043413, 'tau_F': 6.490604848345596}
