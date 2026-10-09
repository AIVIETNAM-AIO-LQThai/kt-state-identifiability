# Experiment 4 pilot report (Sonnet; numbers only; interpretation and the confirmatory request are Opus's)

Pilot config `configs/experiment_04/stage_pilot.yaml` (master seed 20264001), results `results/experiment_04/pilot/a7d89b76c5/`
(`summary.md`, `summary.json`, 24 job files). Run on the owner's PC: `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), single-thread
BLAS, 18 workers, idle machine. **24/24 jobs ok, 0 errors, 40.2 min wall, 7.75 CPU-h.** Three replications per cell: indicative only.
(The PowerShell tool failed with "Access is denied" at launch; the pilot was run through the Bash tool with the same environment variables.)

## Recovery fits, same datasets (error = B2 estimate of sigma2_F minus sigma2_F* = g^2 sigma2_F)
| cell | true sigma2_F* | 1PL-free error (mean, SD) | 2PL error (mean, SD) |
|---|---|---|---|
| V1 N=1000 (lambda == 1, F) | 0.160 | +0.0050 (0.0076) | +0.0013 (0.0070) |
| V1 N=300 | 0.160 | +0.0105 (0.0171) | +0.0076 (0.0178) |
| V5 N=1000 (misfit, F; mean g 0.944) | 0.143 | -0.0086 (0.0028) | -0.0041 (0.0090) |
| V5 N=300 (mean g 0.959) | 0.147 | +0.0006 (0.0021) | +0.0006 (0.0089) |

- tau_F-hat means 10.0-10.9 in all cells. Difficulty RMSE: 1PL-free 0.05 / 0.10 / 0.16 / 0.20, 2PL 0.10 / 0.18 / 0.11 / 0.23 (V1 N = 1000 / 300, V5 N = 1000 / 300).
- 2PL discrimination recovery (RMSE of centred log lambda): V1 0.15 (N = 1000), 0.24 (N = 300); V5 0.15 and 0.30; correlation with the truth 0.87 (V5 N = 1000), 0.78 (V5 N = 300). Items with |log lambda-hat| > log 4: 0 except 1.0 per fit in V5 N = 300.

## Convergence and certificates
- 1PL-free: all 12 B1 and 12 B2 fits converged, no flags.
- 2PL recovery fits: all B1 converged. **B2: 2 of 12 flagged `not_converged`, both in V5 N = 300** (reps 0 and 2); their Newton decrements are 6.7e-5 and 1.8e-5 (below the 1e-3 tolerance), Hessians positive definite. No start-agreement problems (0 fits with fewer than 3 of 5 starts at the best).
- 2PL warp units (18 B2 fits): **4 not converged** (V2 N = 300: 2 of 3; V4 N = 1000: 1 of 3; V4 N = 300: 1 of 3), of which 3 also have `newton_decrement_large`, 3 `single_start_at_best`, 2 `secondary_optima_present`. 1PL-free warp units (6): all converged.
- Cause of the non-convergence: **under investigation** (optimizer messages and iteration counts are not stored in the job summaries; a diagnostic re-run of V5 N = 300 rep 0 is in `diag4.log`, result in the decision log X4-F09).

## Warp units (observed CLR T and one bootstrap CLR T* per fresh null dataset; timing only)
| cell | estimator | T | T* |
|---|---|---|---|
| V2 N=1000 | 2PL | 3.50, 0.14, 2.05 | 2.93, 0.00, 0.95 |
| V2 N=300 | 2PL | 3.41, 0.13, 1.02 | 0.00, 0.00, 0.01 |
| V4 N=1000 | 2PL | 0.44, 1.54, 0.00 | 0.85, 4.36, 1.06 |
| V4 N=1000 | 1PL-free | 1.96, 1.01, 0.00 | 0.00, 12.16, 2.39 |
| V4 N=300 | 2PL | 0.00, 0.63, 1.64 | 0.00, 0.23, 2.20 |
| V4 N=300 | 1PL-free | 0.00, 1.53, 0.10 | 1.04, 0.00, 0.00 |

## Timings (single thread; mean seconds)
| | N=300 | N=1000 |
|---|---|---|
| fit job (1PL-free B1+B2 plus 2PL B1+B2) | 1,053 mean over all four cells | |
| 1PL-free fit, B1 / B2 | 102-106 / 150-162 | 90-101 / 143-149 |
| 2PL fit, B1 / B2 | 307-426 / 454-578 | 268-282 / 392-500 |
| warp unit, 2PL: fit, replicate (V2) | 799, 553 | 565, 539 |
| warp job (V2 2PL only / V4 2PL + 1PL-free) | 1,352 / 1,379 | 1,104 / 1,251 |
2PL fits cost about 3-4 times the 1PL-free fits (the objective itself is as fast per evaluation, 0.020 s, but the fits need more iterations).

## Cost projection for the protocol matrix (X4-D04), from the measured times
- Warp cells V2 and V4, 100 datasets per N (400 datasets): V2 about 1,230 s, V4 about 1,320 s per dataset (job means) = **about 140 CPU-h**.
- Recovery cells V1 and V5, 20 replications at N = 300 and 1000 (80 fit jobs at about 1,050 s) = **about 23 CPU-h**.
- Total **about 163 CPU-h, above the 150 CPU-h cap** (escalation R5). With 75 warp datasets per N the total is about 128 CPU-h; with the V4 1PL-free comparison dropped from the warp cell about 150.
