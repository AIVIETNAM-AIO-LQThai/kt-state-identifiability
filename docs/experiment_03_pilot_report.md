# Experiment 3 pilot report (Sonnet; numbers only; interpretation and the confirmatory request are Opus's)

Pilot config `configs/experiment_03/stage_pilot.yaml` (master seed 20262001), results `results/experiment_03/pilot/33bc5fc566/`
(`summary.md`, `summary.json`, 64 job files). Run on the owner's PC: `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), single-thread BLAS,
18 workers. **64/64 jobs ok, 0 errors, 15.4 min wall, 3.95 CPU-h.** Replications are 3 per cell (U3: 2), so every estimate below is indicative only.

## Same datasets, three estimators (B2 estimate of sigma2_F; true 0.16 in U1/U3, 0 in U2)
| cell | known mean (SD) | calibrated (SD 0.2) mean (SD) | free mean (SD) |
|---|---|---|---|
| U1 N=1000 (tau_F 10) | 0.166 (0.006) | 0.262 (0.048) | 0.156 (0.007) |
| U1 N=300 | 0.152 (0.054) | 0.356 (0.071) | 0.162 (0.019) |
| U2 N=1000 (F absent) | 0.014 (0.012); 1 of 3 at 0 | 0.309 (0.180); tau_F-hat 0.05 | 0.008 (0.008); none at 0 |
| U2 N=300 | 0.010 (0.009); 1 of 3 at 0 | 0.167 (0.163); tau_F-hat 0.27 | 0.029 (0.050); 1 of 3 at 0 |
| U3 N=1000 (tau_F 1) | 0.147 (0.002) | not run | 0.158 (0.062) |
| U3 N=300 | 0.094 (0.029) | not run | 0.125 (0.031) |

- tau_F-hat in U1: known 8.9 / 10.1, calibrated 5.1 / 3.4, free 9.7 / 8.7 (N = 1000 / 300).
- Free-difficulty recovery: RMSE of b-hat 0.044 (N=1000) and 0.093 (N=300) in U1; 0.038 / 0.092 in U2; 0.052 / 0.124 in U3. Calibration error RMSE (by construction) 0.19-0.21.
- H3f, SD(free)/SD(known) of sigma2_F-hat on identical datasets (descriptive; n = 3 or 2, no bootstrap CI): U1 N=1000 1.17; U1 N=300 0.36; U3 N=1000 42; U3 N=300 1.06.

## Null tests (parametric bootstrap, B2 vs B1, p = (1+#)/(B+1))
| dataset | arm | observed CLR | B | p | s/replicate |
|---|---|---|---|---|---|
| U2 N=300 rep 0 | free | 1.98 | 19 | 0.150 | 212 |
| U2 N=1000 rep 0 | free | 1.44 | 19 | 0.400 | 204 |
| U2 N=300 rep 0 | known | 9.36 | 5 | 0.500 | 74 |
| U2 N=1000 rep 0 | known | 50.34 | 5 | 0.500 | 67 |

## Convergence and certificates (B1 and B2 fits; known 16, calibrated 12, free 16 per model)
- All B1 and B2 fits converged. B2 flags: known: single start at best 1, secondary optima 2, embedded null selected 1. Free: secondary optima 2,
  single start at best 1, embedded null selected 1, `hessian_not_pd` 1 and `newton_decrement_large` 1 (both in U2 N=300; max decrement 0.054; sigma2_F-hat near 0). No B1 flags.

## Timings (single thread; mean seconds)
| | N=300 | N=1000 |
|---|---|---|
| fit job per arm, B1+B2: known / calibrated / free | 87 / 98 / 193 | 85 / 90 / 193 |
| null replicate: known / free | 74 / 212 | 67 / 204 |
Free-difficulty fits cost about 2.2x a known-difficulty fit; a free null replicate about 3x a known one.

## Cost projection for the protocol section-4 matrix (20 replications per cell; 10 null datasets per null cell; measured times above)
Fits for U1-U5 with all arms: **17.6 CPU-h**. Null bootstraps dominate:
| option | null CPU-h | total CPU-h |
|---|---|---|
| A. as written: free + known nulls, B = 99 (U2, U4), B = 19 (U1, U5), 10 datasets | 364 | **382** |
| B. free-arm nulls only, otherwise as A | 273 | 290 |
| C. free only; B = 49 in null cells; B = 19 power cells; 10 datasets | 157 | 175 |
| D. free only; B = 49 null cells; B = 19 power cells; 5 datasets per cell | 79 | 96 |
| E. free only; null cells only (U2, U4), B = 99, 5 datasets; no power-cell nulls | 114 | 132 |
The planning ceiling is 150 CPU-h (X3-D05), so option A and B exceed it: **escalation trigger (X3-D10).** U4 and U5 (discrimination misfit) were not piloted.
Wall time at 18 workers is the CPU-h figure divided by about 17.
