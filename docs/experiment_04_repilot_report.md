# Experiment 4 re-pilot report (Sonnet; numbers only)

Config `configs/experiment_04/stage_pilot2.yaml` (same matrix and seed 20264001 as the pilot; `tag` only separates the config hash), results
`results/experiment_04/pilot/afe92d87e7/` (`summary.md`, `summary.json`, 24 job files, `run.log`). Code: R6 Newton polish (`discrimination_free/polish.py`,
`fit.polish_starts`). `.venv12`, single-thread BLAS, 18 workers, idle machine. **24/24 jobs ok, 0 errors, 36.7 min wall, 7.42 CPU-h.**

## Gate (X4-D08 (5)): no non-converged 2PL fit except at most 1 of 30 B2 fits certified on the ridge
- 2PL fits checked: 12 recovery jobs x (B1, B2) = 24 fits plus 12 warp units (observed pair, plus the bootstrap replicate) = 36 units. **1 non-converged**:
  V4 N = 1000 rep 1 (the same case as in the pilot), flags `not_converged, newton_decrement_large, single_start_at_best, secondary_optima_present, white_noise_ridge`.
  All other 2PL fits and bootstrap replicates converged (the pilot had 6 of 36).
- That fit is **not certified**: after the polish (8 steps, log-lik +0.035) the Newton decrement is 0.0061 (tolerance 1e-3), Hessian PD (min eigenvalue 0.18).
  Diagnostic (not stored): with 30 polish steps the decrement is 0.0015 (log-lik +0.068 over the L-BFGS point), still above 1e-3. tau_F-hat = 0.21, sigma2_F-hat = 0.46, T = 1.54;
  the four other starts end at tau_F >= 8 with sigma2_F = 0 or 0.01 (log-lik 0.58-0.77 below).
- Recovery fits: all 24 converged, no ridge flags, results identical to the pilot (same errors, same lambda recovery).
- Strict reading of the gate: **not met** (the one non-converged fit is on the ridge but not certified). Escalated (X4-F13); nothing frozen.

## Timings (mean s per job; single thread)
| job | pilot | re-pilot |
|---|---|---|
| fit (1PL-free and 2PL, B1 and B2) | 1,053 | 1,037 |
| warp V2 (2PL) | 1,228 | 1,207 |
| warp V4 (2PL and 1PL-free) | 1,315 | 1,170 |
Projection of the X4-D08 matrix with these means: V1/V5 80 fit jobs 23.0 h, V4 300 jobs 97.5 h, V2 100 jobs 33.5 h = **about 154 CPU-h** (about 8.5 h on 18 workers), under the 200 cap and the 195 trim threshold.
