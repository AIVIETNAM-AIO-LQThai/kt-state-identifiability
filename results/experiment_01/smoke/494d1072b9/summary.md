# Experiment 1 summary — stage `smoke`

- config hash `494d1072b906`, code hash `ec136536216a`, git `64f00bdb22` (dirty: False)
- env: {'python': '3.12.3', 'executable': '/home/user/kt-state-identifiability/.venv/bin/python', 'platform': 'Linux-6.18.44-fc-v50-x86_64-with-glibc2.39', 'numpy': '2.4.6', 'scipy': '1.17.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 4}
- job accounting: 4/4 fit jobs ok; 0 errors; total CPU 0.66 h

> Smoke stage: verifies the pipeline. It is **not** evidence for the research claim.

## S1|N=64  (fit N=64, held-out N=64, generated 128; 2 reps; violations: none)

| model | fits | failed | converged | flagged | mean s/fit |
|---|---|---|---|---|---|
| B0 | 2 | 0 | 1.00 | 0.00 | 13 |
| B1 | 2 | 0 | 1.00 | 0.00 | 21 |
| B2 | 2 | 0 | 1.00 | 0.00 | 26 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.1804 | 0.0108 | 0.1807 | 2 |
| B0 | phi | 0.2000 | 0.1565 | 0.0024 | 0.1566 | 2 |
| B0 | sigma2_alpha | 0.0025 | 0.0040 | 0.0065 | 0.0077 | 2 |
| B1 | alpha_bar | 0.1500 | 0.0024 | 0.0007 | 0.0025 | 2 |
| B1 | phi | 0.2000 | 0.0103 | 0.0047 | 0.0113 | 2 |
| B1 | sigma2_alpha | 0.0025 | 0.0001 | 0.0026 | 0.0026 | 2 |
| B1 | r_bar | 0.3500 | 0.0435 | 0.0186 | 0.0473 | 2 |
| B1 | tau_R | 5.0000 | -0.5164 | 0.5360 | 0.7444 | 2 |
| B1 | sigma2_r | 0.0225 | -0.0214 | 0.0011 | 0.0214 | 2 |
| B2 | alpha_bar | 0.1500 | 0.0043 | 0.0003 | 0.0043 | 2 |
| B2 | phi | 0.2000 | 0.0109 | 0.0053 | 0.0121 | 2 |
| B2 | sigma2_alpha | 0.0025 | -0.0003 | 0.0022 | 0.0022 | 2 |
| B2 | r_bar | 0.3500 | 0.0480 | 0.0196 | 0.0518 | 2 |
| B2 | tau_R | 5.0000 | -0.5073 | 0.5358 | 0.7379 | 2 |
| B2 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | sigma2_F | 0.1600 | -0.0452 | 0.0014 | 0.0452 | 2 |
| B2 | tau_F | 10.0000 | 5.6963 | 5.3771 | 7.8333 | 2 |

B2: share of fits with sigma2_F at 0: 0.00; boundary hits: {'sigma2_alpha@lower': 0.5, 'sigma2_r@lower': 1.0}
B2: tau_F error when sigma2_F > 0: {'n': 2, 'bias': 5.696304033619784, 'mcse_bias': np.float64(5.377106344520777), 'sd': 7.6043767187436995, 'rmse': 7.83333596137167}
B2 sandwich coverage (interior fits): alpha_bar: 2/2 CP[0.16, 1.0]; phi: 2/2 CP[0.16, 1.0]; r_bar: 2/2 CP[0.16, 1.0]; tau_R: 2/2 CP[0.16, 1.0]; sigma2_F: 2/2 CP[0.16, 1.0]; tau_F: 2/2 CP[0.16, 1.0]; sigma2_alpha: 1/1 CP[0.03, 1.0]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00284 (MCSE 0.00034; positive in 2/2)
- marginal_bernoulli_log_score:B2-B1: 0.00008 (MCSE 0.00006; positive in 2/2)
- pairwise_composite_log_score:B1-B0: 35.86240 (MCSE 3.99643; positive in 2/2)
- pairwise_composite_log_score:B2-B1: 0.64878 (MCSE 0.70056; positive in 1/2)

## S2|N=64  (fit N=64, held-out N=64, generated 128; 2 reps; violations: none)

| model | fits | failed | converged | flagged | mean s/fit |
|---|---|---|---|---|---|
| B0 | 2 | 0 | 1.00 | 0.00 | 14 |
| B1 | 2 | 0 | 1.00 | 0.00 | 23 |
| B2 | 2 | 0 | 1.00 | 0.00 | 17 |

| model | param | truth | bias | MCSE(bias) | RMSE | n |
|---|---|---|---|---|---|---|
| B0 | alpha_bar | 0.1500 | 0.0981 | 0.0033 | 0.0982 | 2 |
| B0 | phi | 0.2000 | 0.0734 | 0.0197 | 0.0760 | 2 |
| B0 | sigma2_alpha | 0.0025 | 0.0031 | 0.0056 | 0.0063 | 2 |
| B1 | alpha_bar | 0.1500 | -0.0174 | 0.0077 | 0.0190 | 2 |
| B1 | phi | 0.2000 | -0.0296 | 0.0024 | 0.0297 | 2 |
| B1 | sigma2_alpha | 0.0025 | -0.0000 | 0.0025 | 0.0025 | 2 |
| B1 | r_bar | 0.3500 | -0.0376 | 0.0065 | 0.0381 | 2 |
| B1 | tau_R | 5.0000 | -0.6739 | 0.1709 | 0.6953 | 2 |
| B1 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | alpha_bar | 0.1500 | -0.0172 | 0.0079 | 0.0189 | 2 |
| B2 | phi | 0.2000 | -0.0296 | 0.0024 | 0.0297 | 2 |
| B2 | sigma2_alpha | 0.0025 | -0.0000 | 0.0025 | 0.0025 | 2 |
| B2 | r_bar | 0.3500 | -0.0372 | 0.0068 | 0.0378 | 2 |
| B2 | tau_R | 5.0000 | -0.6698 | 0.1667 | 0.6902 | 2 |
| B2 | sigma2_r | 0.0225 | -0.0225 | 0.0000 | 0.0225 | 2 |
| B2 | sigma2_F | 0.0000 | 0.0160 | 0.0160 | 0.0226 | 2 |
| B2 | tau_F | 10.0000 | 5.4812 | 14.4812 | 15.4838 | 2 |

B2: share of fits with sigma2_F at 0: 0.50; boundary hits: {'sigma2_r@lower': 1.0, 'sigma2_F@lower': 0.5, 'sigma2_alpha@lower': 0.5}
B2: tau_F error when sigma2_F > 0: {'n': 1, 'bias': 19.96241097796573, 'mcse_bias': nan, 'sd': nan, 'rmse': 19.96241097796573}
B2 sandwich coverage (interior fits): alpha_bar: 2/2 CP[0.16, 1.0]; phi: 2/2 CP[0.16, 1.0]; sigma2_alpha: 1/1 CP[0.03, 1.0]; r_bar: 2/2 CP[0.16, 1.0]; tau_R: 2/2 CP[0.16, 1.0]; sigma2_F: 0/1 CP[0.0, 0.97]; tau_F: 1/1 CP[0.03, 1.0]

Held-out (population-marginal; not next-response) score differences, mean over reps:
- marginal_bernoulli_log_score:B1-B0: 0.00376 (MCSE 0.00054; positive in 2/2)
- marginal_bernoulli_log_score:B2-B1: 0.00003 (MCSE 0.00003; positive in 1/2)
- pairwise_composite_log_score:B1-B0: 47.12338 (MCSE 6.44332; positive in 2/2)
- pairwise_composite_log_score:B2-B1: 0.19036 (MCSE 0.19036; positive in 1/2)

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | CLR obs | B ok/failed | p | reject@0.05 | sigma2_F hat | true |
|---|---|---|---|---|---|---|
| S1|N=64|rep=0 | 105.02 | 19/0 | 0.050 (min 0.050) | True | 0.113 | 0.160 |
| S2|N=64|rep=0 | 0.00 | 19/0 | 1.000 (min 0.050) | False | 0.000 | 0.000 |

## Learner bootstrap vs sandwich SE (B2)

- S1|N=64|rep=0: replicates ok 10/10; bootstrap SD {'alpha_bar': 0.0687, 'phi': 0.0918, 'sigma2_alpha': 0.0023, 'r_bar': 0.1316, 'tau_R': 0.9826, 'sigma2_r': 0.023, 'sigma2_F': 0.0652, 'tau_F': 40.0091}; sandwich SE {'alpha_bar': 0.04623375843845855, 'phi': 0.057322140233459766, 'r_bar': 0.07375675371064284, 'tau_R': 0.7336292237433837, 'sigma2_F': 0.07783398799304515, 'tau_F': 21.280872593683867}
