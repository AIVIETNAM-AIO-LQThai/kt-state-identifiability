# Experiment 1 summary — stage `confirmatory`

- config hash `1b1307a48a5a`, code hash `3b2ff1fd9f34`, git `8bae8bc822` (dirty: True)
- env: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20}
- job accounting: 160/160 fit jobs ok; 0 errors; total CPU 65.81 h

## S1|N=300  (fit N=300, held-out N=300, generated 600; 20 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.99e-09 | 0 (0) | 11 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.92e-08 | 0 (0) | 21 |
| B2 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 4.42e-08 | 0 (0) | 33 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1681 | 0.0054 | 0.1697 | 20 |
| B0 | phi | 0.2000 | 0.1470 | 0.0059 | 0.1493 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0074 | 0.0010 | 0.0087 | 20 |
| B1 | alpha_bar | 0.1500 | -0.0085 | 0.0038 | 0.0186 | 20 |
| B1 | phi | 0.2000 | -0.0085 | 0.0047 | 0.0223 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0002 | 0.0003 | 0.0014 | 20 |
| B1 | r_bar | 0.3500 | 0.0022 | 0.0073 | 0.0320 | 20 |
| B1 | tau_R | 5.0000 | -0.0877 | 0.1274 | 0.5624 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0321 | 0.0071 | 0.0445 | 20 |
| B2 | alpha_bar | 0.1500 | -0.0043 | 0.0039 | 0.0177 | 20 |
| B2 | phi | 0.2000 | -0.0057 | 0.0048 | 0.0215 | 20 |
| B2 | sigma2_alpha | 0.0025 | -0.0006 | 0.0003 | 0.0014 | 20 |
| B2 | r_bar | 0.3500 | 0.0001 | 0.0072 | 0.0316 | 20 |
| B2 | tau_R | 5.0000 | -0.0672 | 0.1274 | 0.5594 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0075 | 0.0058 | 0.0266 | 20 |
| B2 | sigma2_F | 0.1600 | -0.0119 | 0.0079 | 0.0366 | 20 |
| B2 | tau_F | 10.0000 | 2.4565 | 0.9075 | 4.6564 | 20 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_alpha@lower': 0.1, 'sigma2_r@lower': 0.15}
B2: tau_F error when sigma2_F > 0: {'n': 20, 'bias': 2.456476640795628, 'mcse_bias': np.float64(0.9075177601146257), 'sd': 4.058542804809301, 'rmse': 4.6564427087982585}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 20/20 [20/20]; phi: 19/20 [19/20]; sigma2_alpha: 0/0 [0/20]; r_bar: 20/20 [20/20]; tau_R: 20/20 [20/20]; sigma2_r: 0/0 [0/20]; sigma2_F: 20/20 [20/20]; tau_F: 20/20 [20/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00341 (MCSE 0.00013; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: 0.00003 (MCSE 0.00001; positive in 15/20)
- pairwise_composite_log_score:B1-B0: 43.73192 (MCSE 1.64059; positive in 20/20)
- pairwise_composite_log_score:B2-B1: 1.27853 (MCSE 0.08854; positive in 20/20)

## S1|N=1000  (fit N=1000, held-out N=300, generated 1300; 20 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.71e-08 | 0 (0) | 12 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.10e-08 | 0 (0) | 21 |
| B2 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 8.57e-08 | 0 (0) | 33 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1763 | 0.0037 | 0.1771 | 20 |
| B0 | phi | 0.2000 | 0.1514 | 0.0039 | 0.1524 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0094 | 0.0006 | 0.0098 | 20 |
| B1 | alpha_bar | 0.1500 | -0.0067 | 0.0024 | 0.0125 | 20 |
| B1 | phi | 0.2000 | -0.0072 | 0.0029 | 0.0145 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0011 | 0.0003 | 0.0015 | 20 |
| B1 | r_bar | 0.3500 | 0.0004 | 0.0038 | 0.0165 | 20 |
| B1 | tau_R | 5.0000 | 0.0495 | 0.0524 | 0.2339 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0226 | 0.0039 | 0.0282 | 20 |
| B2 | alpha_bar | 0.1500 | -0.0017 | 0.0025 | 0.0111 | 20 |
| B2 | phi | 0.2000 | -0.0038 | 0.0029 | 0.0133 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0002 | 0.0003 | 0.0012 | 20 |
| B2 | r_bar | 0.3500 | -0.0021 | 0.0037 | 0.0165 | 20 |
| B2 | tau_R | 5.0000 | 0.0795 | 0.0522 | 0.2410 | 20 |
| B2 | sigma2_r | 0.0225 | -0.0033 | 0.0035 | 0.0158 | 20 |
| B2 | sigma2_F | 0.1600 | 0.0072 | 0.0053 | 0.0241 | 20 |
| B2 | tau_F | 10.0000 | -0.2165 | 0.3947 | 1.7342 | 20 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_r@lower': 0.2}
B2: tau_F error when sigma2_F > 0: {'n': 20, 'bias': -0.2165480068312986, 'mcse_bias': np.float64(0.39474559690011624), 'sd': 1.7653559769747804, 'rmse': 1.7342291308910598}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 19/20 [19/20]; phi: 19/20 [19/20]; sigma2_alpha: 11/12 [11/20]; r_bar: 20/20 [20/20]; tau_R: 20/20 [20/20]; sigma2_r: 2/3 [2/20]; sigma2_F: 18/20 [18/20]; tau_F: 19/20 [19/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00355 (MCSE 0.00012; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: 0.00002 (MCSE 0.00001; positive in 13/20)
- pairwise_composite_log_score:B1-B0: 45.55927 (MCSE 1.58914; positive in 20/20)
- pairwise_composite_log_score:B2-B1: 1.37690 (MCSE 0.10662; positive in 20/20)

## S2|N=300  (fit N=300, held-out N=300, generated 600; 20 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 4.47e-09 | 0 (0) | 10 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.08e-08 | 0 (0) | 19 |
| B2 | 20 | 0 | 1.00 | 0.00 | 4.6 | 0.05 | 0.05 | 6.11e-08 | 0 (0) | 25 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1894 | 0.0046 | 0.1905 | 20 |
| B0 | phi | 0.2000 | 0.1589 | 0.0042 | 0.1600 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0054 | 0.0010 | 0.0070 | 20 |
| B1 | alpha_bar | 0.1500 | 0.0029 | 0.0029 | 0.0128 | 20 |
| B1 | phi | 0.2000 | 0.0037 | 0.0037 | 0.0166 | 20 |
| B1 | sigma2_alpha | 0.0025 | -0.0008 | 0.0003 | 0.0015 | 20 |
| B1 | r_bar | 0.3500 | 0.0067 | 0.0075 | 0.0333 | 20 |
| B1 | tau_R | 5.0000 | 0.0492 | 0.1190 | 0.5210 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0032 | 0.0067 | 0.0295 | 20 |
| B2 | alpha_bar | 0.1500 | 0.0032 | 0.0029 | 0.0129 | 20 |
| B2 | phi | 0.2000 | 0.0038 | 0.0037 | 0.0166 | 20 |
| B2 | sigma2_alpha | 0.0025 | -0.0008 | 0.0003 | 0.0015 | 20 |
| B2 | r_bar | 0.3500 | 0.0066 | 0.0075 | 0.0332 | 20 |
| B2 | tau_R | 5.0000 | 0.0513 | 0.1191 | 0.5215 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0019 | 0.0065 | 0.0283 | 20 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0090; share at 0: 0.55 | NA | 20 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 60.5024 | NA | 20 |

B2: share of fits with sigma2_F at 0: 0.55; boundary hits: {'sigma2_r@lower': 0.3, 'sigma2_F@lower': 0.55, 'tau_F@lower': 0.05, 'tau_F@upper': 0.05, 'sigma2_alpha@lower': 0.05}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 20/20 [20/20]; phi: 19/20 [19/20]; sigma2_alpha: 2/2 [2/20]; r_bar: 19/20 [19/20]; tau_R: 18/20 [18/20]; sigma2_r: 0/1 [0/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00389 (MCSE 0.00011; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: -0.00000 (MCSE 0.00000; positive in 5/20)
- pairwise_composite_log_score:B1-B0: 49.44596 (MCSE 1.44695; positive in 20/20)
- pairwise_composite_log_score:B2-B1: -0.00693 (MCSE 0.01174; positive in 7/20)

## S2|N=1000  (fit N=1000, held-out N=300, generated 1300; 20 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.57e-08 | 0 (0) | 11 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 7.35e-08 | 0 (0) | 19 |
| B2 | 20 | 0 | 1.00 | 0.00 | 4.2 | 0.10 | 0.20 | 1.27e-07 | 0 (0) | 28 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1849 | 0.0039 | 0.1856 | 20 |
| B0 | phi | 0.2000 | 0.1569 | 0.0032 | 0.1576 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0069 | 0.0006 | 0.0074 | 20 |
| B1 | alpha_bar | 0.1500 | 0.0009 | 0.0020 | 0.0087 | 20 |
| B1 | phi | 0.2000 | 0.0007 | 0.0021 | 0.0093 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0001 | 0.0002 | 0.0008 | 20 |
| B1 | r_bar | 0.3500 | -0.0082 | 0.0041 | 0.0197 | 20 |
| B1 | tau_R | 5.0000 | 0.0780 | 0.0560 | 0.2564 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0041 | 0.0037 | 0.0166 | 20 |
| B2 | alpha_bar | 0.1500 | 0.0011 | 0.0020 | 0.0089 | 20 |
| B2 | phi | 0.2000 | 0.0008 | 0.0021 | 0.0094 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0000 | 0.0002 | 0.0008 | 20 |
| B2 | r_bar | 0.3500 | -0.0083 | 0.0041 | 0.0197 | 20 |
| B2 | tau_R | 5.0000 | 0.0796 | 0.0560 | 0.2569 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0032 | 0.0038 | 0.0169 | 20 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0065; share at 0: 0.45 | NA | 20 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 15.3334 | NA | 20 |

B2: share of fits with sigma2_F at 0: 0.45; boundary hits: {'sigma2_F@lower': 0.45, 'sigma2_r@lower': 0.05, 'tau_F@lower': 0.1}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 19/20 [19/20]; phi: 19/20 [19/20]; sigma2_alpha: 15/15 [15/20]; r_bar: 19/20 [19/20]; tau_R: 20/20 [20/20]; sigma2_r: 5/7 [5/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00383 (MCSE 0.00009; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: 0.00000 (MCSE 0.00000; positive in 7/20)
- pairwise_composite_log_score:B1-B0: 48.85348 (MCSE 1.13644; positive in 20/20)
- pairwise_composite_log_score:B2-B1: 0.00122 (MCSE 0.00975; positive in 7/20)

## S8|N=300  (fit N=300, held-out N=300, generated 600; 20 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.84e-09 | 0 (0) | 13 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.07e-08 | 0 (0) | 22 |
| B2 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 2.14e-08 | 0 (0) | 32 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1889 | 0.0082 | 0.1923 | 20 |
| B0 | phi | 0.2000 | 0.1700 | 0.0068 | 0.1725 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0391 | 0.0022 | 0.0403 | 20 |
| B1 | alpha_bar | 0.1500 | 0.0038 | 0.0044 | 0.0197 | 20 |
| B1 | phi | 0.2000 | 0.0093 | 0.0050 | 0.0236 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0097 | 0.0007 | 0.0102 | 20 |
| B1 | r_bar | 0.3500 | 0.0006 | 0.0090 | 0.0392 | 20 |
| B1 | tau_R | 5.0000 | -0.0703 | 0.1369 | 0.6007 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0897 | 0.0099 | 0.0996 | 20 |
| B2 | alpha_bar | 0.1500 | 0.0088 | 0.0045 | 0.0217 | 20 |
| B2 | phi | 0.2000 | 0.0132 | 0.0051 | 0.0257 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0094 | 0.0008 | 0.0100 | 20 |
| B2 | r_bar | 0.3500 | -0.0032 | 0.0091 | 0.0397 | 20 |
| B2 | tau_R | 5.0000 | -0.0423 | 0.1391 | 0.6080 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0609 | 0.0108 | 0.0771 | 20 |
| B2 | sigma2_F | 0.1600 | -0.0240 | 0.0111 | 0.0538 | 20 |
| B2 | tau_F | 10.0000 | 1.3648 | 0.9705 | 4.4450 | 20 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {}
B2: tau_F error when sigma2_F > 0: {'n': 20, 'bias': 1.3647640428255894, 'mcse_bias': np.float64(0.9705020468786902), 'sd': 4.340217098246878, 'rmse': 4.445018687194517}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 20/20 [20/20]; phi: 20/20 [20/20]; sigma2_alpha: 0/19 [0/20]; r_bar: 19/20 [19/20]; tau_R: 19/20 [19/20]; sigma2_r: 0/10 [0/20]; sigma2_F: 19/20 [19/20]; tau_F: 19/20 [19/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00269 (MCSE 0.00008; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: 0.00001 (MCSE 0.00001; positive in 13/20)
- pairwise_composite_log_score:B1-B0: 35.26930 (MCSE 1.08078; positive in 20/20)
- pairwise_composite_log_score:B2-B1: 0.78241 (MCSE 0.11199; positive in 18/20)

## S8|N=1000  (fit N=1000, held-out N=300, generated 1300; 20 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 9.48e-09 | 0 (0) | 13 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.01e-07 | 0 (0) | 23 |
| B2 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.44e-07 | 0 (0) | 32 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1793 | 0.0037 | 0.1800 | 20 |
| B0 | phi | 0.2000 | 0.1627 | 0.0030 | 0.1632 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0369 | 0.0012 | 0.0373 | 20 |
| B1 | alpha_bar | 0.1500 | -0.0024 | 0.0023 | 0.0104 | 20 |
| B1 | phi | 0.2000 | 0.0028 | 0.0023 | 0.0106 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0087 | 0.0004 | 0.0089 | 20 |
| B1 | r_bar | 0.3500 | -0.0022 | 0.0049 | 0.0213 | 20 |
| B1 | tau_R | 5.0000 | -0.0661 | 0.0650 | 0.2909 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0923 | 0.0051 | 0.0949 | 20 |
| B2 | alpha_bar | 0.1500 | 0.0026 | 0.0023 | 0.0104 | 20 |
| B2 | phi | 0.2000 | 0.0067 | 0.0023 | 0.0121 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0084 | 0.0004 | 0.0086 | 20 |
| B2 | r_bar | 0.3500 | -0.0058 | 0.0049 | 0.0220 | 20 |
| B2 | tau_R | 5.0000 | -0.0429 | 0.0639 | 0.2818 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0627 | 0.0051 | 0.0665 | 20 |
| B2 | sigma2_F | 0.1600 | -0.0207 | 0.0055 | 0.0318 | 20 |
| B2 | tau_F | 10.0000 | -0.4039 | 0.5102 | 2.2604 | 20 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {}
B2: tau_F error when sigma2_F > 0: {'n': 20, 'bias': -0.4039183160840382, 'mcse_bias': np.float64(0.5102262065623789), 'sd': 2.281800963550657, 'rmse': 2.2604059063508566}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 20/20 [20/20]; phi: 19/20 [19/20]; sigma2_alpha: 0/20 [0/20]; r_bar: 19/20 [19/20]; tau_R: 19/20 [19/20]; sigma2_r: 2/20 [2/20]; sigma2_F: 18/20 [18/20]; tau_F: 18/20 [18/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00281 (MCSE 0.00008; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: 0.00000 (MCSE 0.00001; positive in 11/20)
- pairwise_composite_log_score:B1-B0: 36.96299 (MCSE 1.02889; positive in 20/20)
- pairwise_composite_log_score:B2-B1: 0.66600 (MCSE 0.08220; positive in 19/20)

## S8n|N=300  (fit N=300, held-out N=300, generated 600; 20 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.75e-09 | 0 (0) | 12 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.37e-08 | 0 (0) | 22 |
| B2 | 20 | 0 | 1.00 | 0.00 | 4.2 | 0.00 | 0.25 | 2.86e-08 | 0 (0) | 26 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1945 | 0.0080 | 0.1976 | 20 |
| B0 | phi | 0.2000 | 0.1742 | 0.0058 | 0.1760 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0367 | 0.0023 | 0.0380 | 20 |
| B1 | alpha_bar | 0.1500 | 0.0076 | 0.0043 | 0.0203 | 20 |
| B1 | phi | 0.2000 | 0.0134 | 0.0042 | 0.0226 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0090 | 0.0008 | 0.0096 | 20 |
| B1 | r_bar | 0.3500 | -0.0119 | 0.0093 | 0.0422 | 20 |
| B1 | tau_R | 5.0000 | 0.0665 | 0.1257 | 0.5520 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0612 | 0.0097 | 0.0743 | 20 |
| B2 | alpha_bar | 0.1500 | 0.0079 | 0.0044 | 0.0206 | 20 |
| B2 | phi | 0.2000 | 0.0135 | 0.0042 | 0.0228 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0090 | 0.0008 | 0.0096 | 20 |
| B2 | r_bar | 0.3500 | -0.0120 | 0.0093 | 0.0422 | 20 |
| B2 | tau_R | 5.0000 | 0.0681 | 0.1255 | 0.5514 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0599 | 0.0097 | 0.0733 | 20 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0060; share at 0: 0.55 | NA | 20 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 12.8488 | NA | 20 |

B2: share of fits with sigma2_F at 0: 0.55; boundary hits: {'tau_F@lower': 0.25, 'sigma2_F@lower': 0.55}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 20/20 [20/20]; phi: 20/20 [20/20]; sigma2_alpha: 2/20 [2/20]; r_bar: 18/20 [18/20]; tau_R: 19/20 [19/20]; sigma2_r: 0/10 [0/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00276 (MCSE 0.00010; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: -0.00000 (MCSE 0.00000; positive in 4/20)
- pairwise_composite_log_score:B1-B0: 35.97696 (MCSE 1.28946; positive in 20/20)
- pairwise_composite_log_score:B2-B1: -0.01604 (MCSE 0.00909; positive in 5/20)

## S8n|N=1000  (fit N=1000, held-out N=300, generated 1300; 20 reps; violations: ['gain_distribution', 'gain_baseline_correlation'])

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 9.47e-09 | 0 (0) | 13 |
| B1 | 20 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.02e-08 | 0 (0) | 22 |
| B2 | 20 | 0 | 1.00 | 0.00 | 4.3 | 0.10 | 0.10 | 4.45e-02 | 0 (0) | 21 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1770 | 0.0042 | 0.1780 | 20 |
| B0 | phi | 0.2000 | 0.1630 | 0.0031 | 0.1636 | 20 |
| B0 | sigma2_alpha | 0.0025 | 0.0344 | 0.0013 | 0.0349 | 20 |
| B1 | alpha_bar | 0.1500 | -0.0005 | 0.0026 | 0.0114 | 20 |
| B1 | phi | 0.2000 | 0.0069 | 0.0025 | 0.0128 | 20 |
| B1 | sigma2_alpha | 0.0025 | 0.0081 | 0.0005 | 0.0084 | 20 |
| B1 | r_bar | 0.3500 | -0.0105 | 0.0050 | 0.0243 | 20 |
| B1 | tau_R | 5.0000 | -0.0828 | 0.0527 | 0.2440 | 20 |
| B1 | sigma2_r | 0.0225 | 0.0616 | 0.0058 | 0.0666 | 20 |
| B2 | alpha_bar | 0.1500 | -0.0005 | 0.0026 | 0.0114 | 20 |
| B2 | phi | 0.2000 | 0.0069 | 0.0025 | 0.0128 | 20 |
| B2 | sigma2_alpha | 0.0025 | 0.0081 | 0.0005 | 0.0084 | 20 |
| B2 | r_bar | 0.3500 | -0.0106 | 0.0050 | 0.0243 | 20 |
| B2 | tau_R | 5.0000 | -0.0827 | 0.0526 | 0.2439 | 20 |
| B2 | sigma2_r | 0.0225 | 0.0614 | 0.0058 | 0.0664 | 20 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0007; share at 0: 0.80 | NA | 20 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 14.5719 | NA | 20 |

B2: share of fits with sigma2_F at 0: 0.80; boundary hits: {'sigma2_F@lower': 0.8, 'tau_F@lower': 0.05}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 19/20 [19/20]; phi: 18/20 [18/20]; sigma2_alpha: 0/20 [0/20]; r_bar: 18/20 [18/20]; tau_R: 20/20 [20/20]; sigma2_r: 1/20 [1/20]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00281 (MCSE 0.00008; positive in 20/20)
- marginal_bernoulli_log_score:B2-B1: -0.00000 (MCSE 0.00000; positive in 4/20)
- pairwise_composite_log_score:B1-B0: 36.55049 (MCSE 1.05096; positive in 20/20)
- pairwise_composite_log_score:B2-B1: -0.00275 (MCSE 0.00167; positive in 4/20)

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | CLR obs | B ok/failed | p | reject@0.05 | sigma2_F hat | true |
|---|---|---|---|---|---|---|
| S1|N=300|rep=0 | 429.79 | 19/0 | 0.050 (min 0.050) | True | 0.113 | 0.160 |
| S1|N=300|rep=1 | 814.14 | 19/0 | 0.050 (min 0.050) | True | 0.165 | 0.160 |
| S1|N=300|rep=2 | 927.15 | 19/0 | 0.050 (min 0.050) | True | 0.185 | 0.160 |
| S1|N=300|rep=3 | 706.44 | 19/0 | 0.050 (min 0.050) | True | 0.150 | 0.160 |
| S1|N=300|rep=4 | 743.28 | 19/0 | 0.050 (min 0.050) | True | 0.156 | 0.160 |
| S1|N=300|rep=5 | 865.44 | 19/0 | 0.050 (min 0.050) | True | 0.171 | 0.160 |
| S1|N=300|rep=6 | 408.07 | 19/0 | 0.050 (min 0.050) | True | 0.107 | 0.160 |
| S1|N=300|rep=7 | 438.12 | 19/0 | 0.050 (min 0.050) | True | 0.118 | 0.160 |
| S1|N=300|rep=8 | 882.70 | 19/0 | 0.050 (min 0.050) | True | 0.166 | 0.160 |
| S1|N=300|rep=9 | 620.11 | 19/0 | 0.050 (min 0.050) | True | 0.142 | 0.160 |
| S1|N=1000|rep=0 | 2300.07 | 19/0 | 0.050 (min 0.050) | True | 0.151 | 0.160 |
| S1|N=1000|rep=1 | 2442.82 | 19/0 | 0.050 (min 0.050) | True | 0.157 | 0.160 |
| S1|N=1000|rep=2 | 2961.99 | 19/0 | 0.050 (min 0.050) | True | 0.178 | 0.160 |
| S1|N=1000|rep=3 | 3486.56 | 19/0 | 0.050 (min 0.050) | True | 0.191 | 0.160 |
| S1|N=1000|rep=4 | 3320.34 | 19/0 | 0.050 (min 0.050) | True | 0.187 | 0.160 |
| S1|N=1000|rep=5 | 2072.44 | 19/0 | 0.050 (min 0.050) | True | 0.143 | 0.160 |
| S1|N=1000|rep=6 | 2770.53 | 19/0 | 0.050 (min 0.050) | True | 0.170 | 0.160 |
| S1|N=1000|rep=7 | 2122.53 | 19/0 | 0.050 (min 0.050) | True | 0.147 | 0.160 |
| S1|N=1000|rep=8 | 2183.43 | 19/0 | 0.050 (min 0.050) | True | 0.147 | 0.160 |
| S1|N=1000|rep=9 | 2107.05 | 19/0 | 0.050 (min 0.050) | True | 0.145 | 0.160 |
| S2|N=300|rep=0 | 15.97 | 99/0 | 0.350 (min 0.010) | False | 0.023 | 0.000 |
| S2|N=300|rep=1 | 14.28 | 99/0 | 0.270 (min 0.010) | False | 0.021 | 0.000 |
| S2|N=300|rep=2 | 0.00 | 99/0 | 0.990 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=300|rep=3 | 28.85 | 99/0 | 0.280 (min 0.010) | False | 0.030 | 0.000 |
| S2|N=300|rep=4 | 0.00 | 99/0 | 0.650 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=300|rep=5 | 0.00 | 99/0 | 0.650 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=300|rep=6 | 0.00 | 99/0 | 0.680 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=300|rep=7 | 1.45 | 99/0 | 0.450 (min 0.010) | False | 0.006 | 0.000 |
| S2|N=300|rep=8 | 0.00 | 99/0 | 0.980 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=300|rep=9 | 5.54 | 99/0 | 0.320 (min 0.010) | False | 0.013 | 0.000 |
| S2|N=1000|rep=0 | 0.00 | 99/0 | 1.000 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=1000|rep=1 | 0.00 | 99/0 | 0.560 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=1000|rep=2 | 1.17 | 99/0 | 0.510 (min 0.010) | False | 0.003 | 0.000 |
| S2|N=1000|rep=3 | 33.56 | 99/0 | 0.200 (min 0.010) | False | 0.017 | 0.000 |
| S2|N=1000|rep=4 | 86.87 | 99/0 | 0.080 (min 0.010) | False | 0.029 | 0.000 |
| S2|N=1000|rep=5 | 0.00 | 99/0 | 0.610 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=1000|rep=6 | 0.00 | 99/0 | 0.990 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=1000|rep=7 | 9.98 | 99/0 | 0.310 (min 0.010) | False | 0.010 | 0.000 |
| S2|N=1000|rep=8 | 0.00 | 99/0 | 0.520 (min 0.010) | False | 0.000 | 0.000 |
| S2|N=1000|rep=9 | 48.75 | 99/0 | 0.130 (min 0.010) | False | 0.021 | 0.000 |
| S8|N=300|rep=0 | 764.23 | 19/0 | 0.050 (min 0.050) | True | 0.168 | 0.160 |
| S8|N=300|rep=1 | 1512.05 | 19/0 | 0.050 (min 0.050) | True | 0.248 | 0.160 |
| S8|N=300|rep=2 | 365.59 | 19/0 | 0.050 (min 0.050) | True | 0.121 | 0.160 |
| S8|N=300|rep=3 | 817.90 | 19/0 | 0.050 (min 0.050) | True | 0.185 | 0.160 |
| S8|N=300|rep=4 | 578.42 | 19/0 | 0.050 (min 0.050) | True | 0.142 | 0.160 |
| S8|N=300|rep=5 | 439.45 | 19/0 | 0.050 (min 0.050) | True | 0.122 | 0.160 |
| S8|N=300|rep=6 | 236.22 | 19/0 | 0.050 (min 0.050) | True | 0.091 | 0.160 |
| S8|N=300|rep=7 | 503.88 | 19/0 | 0.050 (min 0.050) | True | 0.140 | 0.160 |
| S8|N=300|rep=8 | 188.19 | 19/0 | 0.050 (min 0.050) | True | 0.081 | 0.160 |
| S8|N=300|rep=9 | 1041.78 | 19/0 | 0.050 (min 0.050) | True | 0.209 | 0.160 |
| S8|N=1000|rep=0 | 1788.93 | 19/0 | 0.050 (min 0.050) | True | 0.141 | 0.160 |
| S8|N=1000|rep=1 | 905.87 | 19/0 | 0.050 (min 0.050) | True | 0.098 | 0.160 |
| S8|N=1000|rep=2 | 1444.36 | 19/0 | 0.050 (min 0.050) | True | 0.124 | 0.160 |
| S8|N=1000|rep=3 | 2035.55 | 19/0 | 0.050 (min 0.050) | True | 0.153 | 0.160 |
| S8|N=1000|rep=4 | 1489.64 | 19/0 | 0.050 (min 0.050) | True | 0.132 | 0.160 |
| S8|N=1000|rep=5 | 1812.70 | 19/0 | 0.050 (min 0.050) | True | 0.144 | 0.160 |
| S8|N=1000|rep=6 | 1268.32 | 19/0 | 0.050 (min 0.050) | True | 0.119 | 0.160 |
| S8|N=1000|rep=7 | 2259.00 | 19/0 | 0.050 (min 0.050) | True | 0.165 | 0.160 |
| S8|N=1000|rep=8 | 1376.32 | 19/0 | 0.050 (min 0.050) | True | 0.125 | 0.160 |
| S8|N=1000|rep=9 | 1564.84 | 19/0 | 0.050 (min 0.050) | True | 0.134 | 0.160 |
| S8n|N=300|rep=0 | 2.06 | 99/0 | 0.590 (min 0.010) | False | 0.009 | 0.000 |
| S8n|N=300|rep=1 | 1.59 | 99/0 | 0.500 (min 0.010) | False | 0.008 | 0.000 |
| S8n|N=300|rep=2 | 0.00 | 99/0 | 0.990 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=300|rep=3 | 0.83 | 99/0 | 0.500 (min 0.010) | False | 0.005 | 0.000 |
| S8n|N=300|rep=4 | 1.21 | 99/0 | 0.370 (min 0.010) | False | 0.007 | 0.000 |
| S8n|N=300|rep=5 | 0.00 | 99/0 | 0.750 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=300|rep=6 | 2.23 | 99/0 | 0.440 (min 0.010) | False | 0.009 | 0.000 |
| S8n|N=300|rep=7 | 0.00 | 99/0 | 0.730 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=300|rep=8 | 2.77 | 99/0 | 0.370 (min 0.010) | False | 0.010 | 0.000 |
| S8n|N=300|rep=9 | 0.00 | 99/0 | 0.980 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=0 | 4.79 | 99/0 | 0.470 (min 0.010) | False | 0.007 | 0.000 |
| S8n|N=1000|rep=1 | 0.00 | 99/0 | 0.990 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=2 | 1.17 | 99/0 | 0.440 (min 0.010) | False | 0.004 | 0.000 |
| S8n|N=1000|rep=3 | 0.00 | 99/0 | 0.670 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=4 | 0.00 | 99/0 | 0.990 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=5 | 0.00 | 99/0 | 0.610 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=6 | 0.00 | 99/0 | 0.720 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=7 | 0.00 | 99/0 | 1.000 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=8 | 0.00 | 99/0 | 1.000 (min 0.010) | False | 0.000 | 0.000 |
| S8n|N=1000|rep=9 | 0.00 | 99/0 | 1.000 (min 0.010) | False | 0.000 | 0.000 |

## Learner bootstrap vs sandwich SE (B2)

- S1|N=1000|rep=0: replicates ok 50/50; bootstrap SD {'alpha_bar': 0.0109, 'phi': 0.0129, 'sigma2_alpha': 0.001, 'r_bar': 0.0156, 'tau_R': 0.2754, 'sigma2_r': 0.0113, 'sigma2_F': 0.0216, 'tau_F': 1.7522}; sandwich SE {'alpha_bar': 0.011440284724464345, 'phi': 0.013196792192898174, 'sigma2_alpha': 0.0010084728026574132, 'r_bar': 0.017750220354683707, 'tau_R': 0.28630253950318063, 'sigma2_r': 0.016968287577598145, 'sigma2_F': 0.0207655212519246, 'tau_F': 1.8145812937750199}

## Pre-registered decision rules (D24)

Bias verdicts use the 95 % Monte Carlo CI (bias +- 1.96 MCSE) against +-0.04; rates use Clopper-Pearson 95 % limits.

- **PH1** (S1 N=300, 20 fits): bias -0.0119, MCSE 0.0079, MC CI [-0.0275, 0.0037] -> **pass** (RMSE 0.0366, SD 0.0355)
- **PH1** (S1 N=1000, 20 fits): bias 0.0072, MCSE 0.0053, MC CI [-0.0031, 0.0176] -> **pass** (RMSE 0.0241, SD 0.0236)
- **PH5** (S8 N=300, 20 fits): bias -0.0240, MCSE 0.0111, MC CI [-0.0457, -0.0024] -> **inconclusive** (RMSE 0.0538, SD 0.0494)
- **PH5** (S8 N=1000, 20 fits): bias -0.0207, MCSE 0.0055, MC CI [-0.0315, -0.0098] -> **pass** (RMSE 0.0318, SD 0.0248)
- **PH2** (S1 N=300): boundary-aware test rejects 10/10 (CP95 [0.69, 1.00])
- **PH2** (S1 N=1000): boundary-aware test rejects 10/10 (CP95 [0.69, 1.00])
- **PH3** (S2, sigma2_F = 0): rejects 0/20 (CP95 [0.00, 0.17]) -> **no evidence of excess false positives (CP upper bound 0.17)**; sigma2_F-hat at 0 in 0.50, mean 0.0078, p90 0.0234; near-white (sigma2_F-hat > 0 and tau_F-hat < 0.4 min) 9/40
- **PH4** (S8n, sigma2_F = 0): rejects 0/20 (CP95 [0.00, 0.17]) -> **no evidence of excess false positives (CP upper bound 0.17)**; sigma2_F-hat at 0 in 0.68, mean 0.0034, p90 0.0091; near-white (sigma2_F-hat > 0 and tau_F-hat < 0.4 min) 10/40
- **PH6** (S1|N=300): held-out pairwise composite B2-B1 = 1.279 per learner, MCSE 0.089, MC CI [1.105, 1.452] -> improvement: yes
- **PH6** (S1|N=1000): held-out pairwise composite B2-B1 = 1.377 per learner, MCSE 0.107, MC CI [1.168, 1.586] -> improvement: yes
- **PH6** (S2|N=300): held-out pairwise composite B2-B1 = -0.007 per learner, MCSE 0.012, MC CI [-0.030, 0.016] -> spurious superiority: not shown
- **PH6** (S2|N=1000): held-out pairwise composite B2-B1 = 0.001 per learner, MCSE 0.010, MC CI [-0.018, 0.020] -> spurious superiority: not shown
- **PH6** (S8n|N=300): held-out pairwise composite B2-B1 = -0.016 per learner, MCSE 0.009, MC CI [-0.034, 0.002] -> spurious superiority: not shown
- **PH6** (S8n|N=1000): held-out pairwise composite B2-B1 = -0.003 per learner, MCSE 0.002, MC CI [-0.006, 0.001] -> spurious superiority: not shown

MDE (descriptive only): MDE sigma2_F = 0.04 is NOT a confirmatory criterion (D21/D24). Design-based predicted SE at sigma2_F = 0.04: {'300': 0.0338, '1000': 0.0185}; empirical SD of sigma2_F-hat in S1: {'N=300': 0.03551423157045341, 'N=1000': 0.02355677828442312}
