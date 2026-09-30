# Experiment 1 summary — stage `smoke`

- config hash `0e7ec61e6f97`, code hash `dd1c3c835d74`, git `444e7e210a` (dirty: False)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v50-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: 4/4 fit jobs ok; 0 errors; total CPU 1.26 h

> Smoke stage: verifies the pipeline. It is **not** evidence for the research claim.

## S1|N=64  (fit N=64, held-out N=64, generated 128; 2 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 2 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 8.67e-11 | 0 (0) | 18 |
| B1 | 2 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.24e-09 | 0 (0) | 30 |
| B2 | 2 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 3.19e-09 | 0 (0) | 49 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1804 | 0.0108 | 0.1807 | 2 |
| B0 | phi | 0.2000 | 0.1565 | 0.0024 | 0.1566 | 2 |
| B0 | sigma2_alpha | 0.0025 | 0.0040 | 0.0065 | 0.0077 | 2 |
| B1 | alpha_bar | 0.1500 | 0.0024 | 0.0007 | 0.0025 | 2 |
| B1 | phi | 0.2000 | 0.0103 | 0.0047 | 0.0113 | 2 |
| B1 | sigma2_alpha | 0.0025 | 0.0001 | 0.0026 | 0.0026 | 2 |
| B1 | r_bar | 0.3500 | 0.0435 | 0.0185 | 0.0473 | 2 |
| B1 | tau_R | 5.0000 | -0.5163 | 0.5364 | 0.7445 | 2 |
| B1 | sigma2_r | 0.0225 | -0.0214 | 0.0011 | 0.0215 | 2 |
| B2 | alpha_bar | 0.1500 | 0.0042 | 0.0004 | 0.0042 | 2 |
| B2 | phi | 0.2000 | 0.0108 | 0.0052 | 0.0120 | 2 |
| B2 | sigma2_alpha | 0.0025 | -0.0003 | 0.0022 | 0.0022 | 2 |
| B2 | r_bar | 0.3500 | 0.0481 | 0.0195 | 0.0519 | 2 |
| B2 | tau_R | 5.0000 | -0.5071 | 0.5371 | 0.7387 | 2 |
| B2 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | sigma2_F | 0.1600 | -0.0452 | 0.0016 | 0.0452 | 2 |
| B2 | tau_F | 10.0000 | 5.6864 | 5.4148 | 7.8520 | 2 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_alpha@lower': 0.5, 'sigma2_r@lower': 1.0}
B2: tau_F error when sigma2_F > 0: {'n': 2, 'bias': 5.686351063452893, 'mcse_bias': np.float64(5.4147575349036465), 'sd': 7.657623542822645, 'rmse': 7.852018057711511}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 2/2 [2/2]; phi: 2/2 [2/2]; sigma2_alpha: 1/1 [1/2]; r_bar: 2/2 [2/2]; tau_R: 2/2 [2/2]; sigma2_r: 0/0 [0/2]; sigma2_F: 2/2 [2/2]; tau_F: 2/2 [2/2]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00284 (MCSE 0.00034; positive in 2/2)
- marginal_bernoulli_log_score:B2-B1: 0.00008 (MCSE 0.00006; positive in 2/2)
- pairwise_composite_log_score:B1-B0: 35.86357 (MCSE 3.99302; positive in 2/2)
- pairwise_composite_log_score:B2-B1: 0.65289 (MCSE 0.69910; positive in 1/2)

## S2|N=64  (fit N=64, held-out N=64, generated 128; 2 reps; violations: none)

| model | fits | failed | converged | flagged | starts at best (mean) | single-start-best rate | secondary-optima rate | max Newton decrement | H not PD (outside allowance) | mean s/fit |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 2 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 5.49e-10 | 0 (0) | 20 |
| B1 | 2 | 0 | 1.00 | 0.00 | 5.0 | 0.00 | 0.00 | 1.22e-09 | 0 (0) | 35 |
| B2 | 2 | 0 | 1.00 | 0.00 | 4.5 | 0.00 | 0.50 | 2.04e-09 | 0 (0) | 40 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.0981 | 0.0033 | 0.0982 | 2 |
| B0 | phi | 0.2000 | 0.0734 | 0.0197 | 0.0760 | 2 |
| B0 | sigma2_alpha | 0.0025 | 0.0031 | 0.0056 | 0.0063 | 2 |
| B1 | alpha_bar | 0.1500 | -0.0173 | 0.0077 | 0.0190 | 2 |
| B1 | phi | 0.2000 | -0.0296 | 0.0024 | 0.0297 | 2 |
| B1 | sigma2_alpha | 0.0025 | -0.0000 | 0.0025 | 0.0025 | 2 |
| B1 | r_bar | 0.3500 | -0.0375 | 0.0064 | 0.0381 | 2 |
| B1 | tau_R | 5.0000 | -0.6751 | 0.1707 | 0.6963 | 2 |
| B1 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | alpha_bar | 0.1500 | -0.0171 | 0.0079 | 0.0189 | 2 |
| B2 | phi | 0.2000 | -0.0296 | 0.0024 | 0.0297 | 2 |
| B2 | sigma2_alpha | 0.0025 | -0.0000 | 0.0025 | 0.0025 | 2 |
| B2 | r_bar | 0.3500 | -0.0369 | 0.0070 | 0.0376 | 2 |
| B2 | tau_R | 5.0000 | -0.6733 | 0.1690 | 0.6942 | 2 |
| B2 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | sigma2_F | 0.0000 | NA (true value on the boundary (0)) | mean estimate 0.0168; share at 0: 0.50 | NA | 2 |
| B2 | tau_F | 10.0000 | NA (inactive: no transient state in the generating process) | mean estimate 23.8200 | NA | 2 |

B2: share of fits with sigma2_F at 0: 0.50; boundary hits: {'sigma2_r@lower': 1.0, 'sigma2_F@lower': 0.5, 'sigma2_alpha@lower': 0.5}
B2 sandwich coverage, conditional on an interior fit (unconditional in brackets): alpha_bar: 2/2 [2/2]; phi: 2/2 [2/2]; sigma2_alpha: 1/1 [1/2]; r_bar: 2/2 [2/2]; tau_R: 2/2 [2/2]; sigma2_r: 0/0 [0/2]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00376 (MCSE 0.00054; positive in 2/2)
- marginal_bernoulli_log_score:B2-B1: 0.00003 (MCSE 0.00003; positive in 2/2)
- pairwise_composite_log_score:B1-B0: 47.13381 (MCSE 6.41753; positive in 2/2)
- pairwise_composite_log_score:B2-B1: 0.14401 (MCSE 0.14400; positive in 2/2)

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | CLR obs | B ok/failed | p | reject@0.05 | sigma2_F hat | true |
|---|---|---|---|---|---|---|
| S1|N=64|rep=0 | 105.02 | 19/0 | 0.050 (min 0.050) | True | 0.113 | 0.160 |
| S2|N=64|rep=0 | -0.00 | 19/0 | 0.950 (min 0.050) | False | 0.000 | 0.000 |

## Learner bootstrap vs sandwich SE (B2)

- S1|N=64|rep=0: replicates ok 10/10; bootstrap SD {'alpha_bar': 0.0687, 'phi': 0.0918, 'sigma2_alpha': 0.0023, 'r_bar': 0.1315, 'tau_R': 0.9823, 'sigma2_r': 0.023, 'sigma2_F': 0.0572, 'tau_F': 310.6633}; sandwich SE {'alpha_bar': 0.046220964935479836, 'phi': 0.0573061555400888, 'r_bar': 0.07379274050780493, 'tau_R': 0.7335790116839634, 'sigma2_F': 0.07786006753836358, 'tau_F': 21.3819543983952}
