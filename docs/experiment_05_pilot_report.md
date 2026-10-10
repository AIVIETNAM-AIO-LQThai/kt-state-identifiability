# Experiment 5 pilot report (Sonnet; numbers only)

Config `configs/experiment_05/stage_pilot.yaml` (master seed 20265002, not confirmatory, nothing frozen), results `results/experiment_05/pilot/bf9ceeeae2/`
(`summary.md`, `summary.json`, `rules.json`, 36 job files). Code: `state_dependence/` (jobs, runner, summarize, rules), `.venv12`, single-thread BLAS, 18 workers.
**36/36 jobs ok, 0 errors, 35.0 min wall, 8.37 CPU-h.** 3 replications per cell and N (E4 as warp units with one bootstrap replicate each).

## Gates (provisional rules, X5-D06)
- G1: no failed or non-converged B2 fit and no failed bootstrap replicate in any cell (36/36 valid); the carry-over score test ran at every B2 and B1 fit for all three tau_x (no `error` entries).
- G2 (one code hash `5a7eae8695fb`), G3 (single-thread BLAS), no job errors: all ok.

## Per cell (mean sigma2_F-hat, median tau_F-hat, diagnostic rejection share at tau_x = 2 / 5 / 10, mean eta-hat at tau_x = 2; 3 datasets each)
| cell | sigma2_F* | mean sigma2_F-hat | median tau_F-hat | reject share (2 / 5 / 10) | eta-hat | mean job s | T values |
|---|---|---|---|---|---|---|---|
| E1 N=300 | 0.160 | 0.175 | 11.0 | 0 / 0 / 0 | +0.009 | 815 | 250, 201, 183 |
| E1 N=1000 | 0.160 | 0.157 | 9.4 | 0 / 0 / 0 | 0.000 | 647 | 637, 512, 500 |
| E2 N=300 | 0 | 0.228 | 0.3 | 0 / 0 / 0 | +0.004 | 834 | 1.73, 3.22, 0.0 |
| E2 N=1000 | 0 | 0.007 | 1.0 | 0 / 0 / 0 | -0.013 | 584 | 0.0, 4.08, 0.0 |
| E3 N=300 | 0 | 0.162 | 59.5 | 1 / 1 / 1 | -0.285 | 955 | 296, 505, 379 |
| E3 N=1000 | 0 | 0.141 | 232.5 | 1 / 1 / 1 | -0.264 | 976 | 1170, 1057, 1433 |
| E4 N=300 (warp) | 0 | 0.064 | 5.2 | 0 / 0 / 0 | -0.003 | 1352 | 17.1, 10.3, 3.6 (T*: 0.69, 2.35, 0.44) |
| E4 N=1000 (warp) | 0 | 0.038 | 4.0 | 0.67 / 0.33 / 0 | -0.077 | 1097 | 17.4, 8.5, 22.4 (T*: 0.06, 5.35, 1.81) |
| E5 N=300 | 0.160 | 0.431 | 39.2 | 1 / 1 / 1 | -0.301 | 928 | 1853, 1978, 1842 |
| E5 N=1000 | 0.160 | 0.406 | 31.7 | 1 / 1 / 1 | -0.255 | 924 | 5104, 5001, 5793 |
| E6 N=300 | 0 | 0.047 | 1.3 | 0.33 / 0.33 / 0 | -0.056 | 525 | 0.23, 0.89, 0.13 |
| E6 N=1000 | 0 | 0.000 | 29.6 | 0 / 0 / 0 | +0.016 | 408 | 0, 0, 0 |

## Against the Stage-0 predictions
- E3: sigma2_F-hat 0.14-0.20 (predicted 0.144), tau_F-hat 54-1000 (predicted 1000 at the bound; one dataset at 1000), diagnostic 6/6 (predicted power 0.99 / 1.00).
- E5: sigma2_F-hat bias +0.27 (N = 300, MC CI [0.24, 0.30]) and +0.25 (N = 1000, [0.21, 0.28]); predicted +0.25.
- E4: diagnostic 0/3 (N = 300) and 2/3 (N = 1000) rejections at tau_x = 2 (predicted power 0.27 / 0.68); T above the Experiment 4 V2 q95 in 2/3 (N = 300, q95 4.23) and 3/3 (N = 1000, q95 5.16); T above the own bootstrap T* in 6/6 units.
- E1, E2: 0/12 diagnostic rejections (predicted 0.05); E6: 1/6 (the dataset E6 N=300 r1, p = 0.0044, sigma2_F-hat 0.113, tau_F-hat 0.5).

## Fit health
- All 36 B2 fits converged (B1 too); polish used 1-5 times per fit (`n_polished`); one polish line-search failure in 72 fits (B1 and B2), none `converged_on_ridge`.
- White-noise ridge (tau_F-hat 0.3): E2 N=300 r0 and r1 (sigma2_F-hat 0.33 and 0.35; T 1.73 and 3.22); `converged_on_ridge` was not needed. E2 N=300 r1 also has a b-or-w bound hit and secondary optima.
- Boundary flags: tau_R at its upper bound in all E3 and E5 fits; sigma2_alpha at its lower bound in some E1, E3, E5, E4 fits; tau_F at 1000 in one E3 fit (N = 1000, r2).

## Timings (mean s per job, 18 workers busy) and projection
| cell | E1 | E2 | E3 | E4 (warp) | E5 | E6 |
|---|---|---|---|---|---|---|
| mean job s | 731 | 709 | 965 | 1,225 | 926 | 466 |
| E4 warp: fit / bootstrap replicate | | | | 661 / 429 (N = 1000), 759 / 586 (N = 300) | | |

Projection of the X5-D06 matrix (E1, E2 75 per N; E3, E5 30; E4 50; E6 50) with these means: 150 x 731 + 150 x 709 + 60 x 965 + 100 x 1,225 + 60 x 926 + 100 x 466 =
**138.5 CPU-h** (about 7.7 h on 18 workers); with the x1.4 load factor of X4-D11, **193.9 CPU-h** (about 10.8 h). The pilot ran 36 jobs on 18 workers (two waves) at full load.
Trim steps in X5-D06 (E1/E2 to 60 per N, E6 to 40, E4 to 40) would save about 22, 6 and 12 CPU-h at the pilot means (before the factor).
