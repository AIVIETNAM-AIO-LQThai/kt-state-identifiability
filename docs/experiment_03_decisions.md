# Experiment 3: decision and findings log

IDs use the prefix X3. F is a statistical component, never a psychological label.

## Approved by the owner (Opus plan approval, 2026-10-05; details in `docs/experiment_03_protocol.md`)
| ID | Decision |
|---|---|
| X3-D01 | **Question:** can σ²_F, and the boundary-aware null test, still be recovered under the Experiment-1 process when item difficulties are estimated jointly (B2-free), taken from an external calibration with error (B2-cal, SD 0.2), or when items have unequal discriminations (λ_q lognormal, mean 1, CV 0.3)? Hypotheses H3a–H3e (protocol §2). They are frozen after Stage 0 and the pilot. |
| X3-D02 | **Theory first (protocol §1).** With b free, a white-noise F is exactly confounded with the overall probit scale. Rescaling locations by c and variances by c², with c² − 1 of added white noise, leaves every observable unchanged. Prediction: σ²_F identified at τ_F well above the response spacing, degrading as τ_F shrinks, lost at τ_F → 0. Stage 0 checks this numerically. |
| X3-D03 | **Stage 0 gate.** An analytic Jacobian/SVD and Godambe audit with the 48 difficulties free, at τ_F ∈ {0.2, 1, 3, 10, 60}. If the design SE of σ²_F at τ_F = 10, N = 1000, exceeds about 0.08, re-scope before building. If rank-deficient at τ_F = 10, stop. |
| X3-D04 | **Scope:** scenarios U1–U5 (protocol §4); estimators known, free and cal. Not included: estimating discriminations (2PL), adaptive schedules, real data. |
| X3-D05 | **Venue and budget:** the owner's PC (`.venv12`, single-thread BLAS, 18 workers), ≤ 150 CPU-h. The final matrix is set from measured costs at the Stage-2 review, before freezing. |
| X3-D06 | **Code and branch:** new package `difficulty_free/` (`kt_trial/` imported, never modified); branch `exp/unknown-difficulty-recoverability`. The owner runs all git. The CLI sets `*_NUM_THREADS=1` at import (X2-F15). |

## Stage 0 results (Sonnet, 2026-10-05; numbers in docs/experiment_03_stage0_report.md; the gate review is Opus's)
| ID | Record |
|---|---|
| X3-F01 | Implementation: `difficulty_free/` (freeb.py: observable Jacobian, pairwise-composite sensitivity and learner scores with the 48 difficulties as extra coordinates; audit.py; cli.py sets `*_NUM_THREADS=1` before numpy; report0.py), `configs/experiment_03/stage0.yaml`, `tests/test_difficulty_free.py` (7 tests: d/db vs finite differences, b-known block equals kt_trial's Jacobian/Fisher/scores, scores centred, exact white-noise scale ridge and its breaking by the OU kernel, ridge tangent null direction, audit smoke). Run in `.venv12` (python 3.12.10 / numpy 2.5.3 / scipy 1.18.1), single-thread BLAS. |
| X3-F02 | **Consistency with Experiment 1:** b-known design SE of sigma2_F at tau_F = 10 is 0.0386 / 0.0211 (N = 300 / 1000) against 0.0385 / 0.0211 in the Experiment-1 audit. |
| X3-F03 | **Gate numbers (X3-D03):** b free, tau_F = 10, N = 1000: rank 66/66, design SE of sigma2_F **0.0121** (threshold 0.08); not rank-deficient. |
| X3-F04 | **tau_F dependence (b free, SE at N = 1000):** 0.2 min: 2.10 (known: 0.023); 1 min: 0.063; 3 min: 0.021; 10 min: 0.012; 60 min: 0.010. At tau_F = 0.2 the b-free estimator of sigma2_F is correlated 0.999 with Sigma_M and b coordinates (the predicted scale ridge); ridge response of the observable map 6.6e-5 (relative). |
| X3-F05 | **Unexpected, flagged for Opus:** for tau_F >= 3 the b-free SE is *below* the b-known SE (ratio 0.92 at 3, 0.57 at 10, 0.53 at 60). The numbers are stable (seed 777, 40,000 score learners: 0.0222 / 0.0121 at tau_F = 10; 3.826 / 2.096 at 0.2). The sandwich of a composite likelihood need not rise when nuisance parameters are freed (estimated nuisance parameters can absorb score noise), but this has not been confirmed empirically; the pilot (free vs known fits on the same data) is the check. |
| X3-F06 | **Test-suite note (not changed):** full suite on the owner's PC (.venv12, single-thread BLAS): 92 passed, 1 failed. The failure is the pre-existing Experiment-1 test `test_all_b2_starts_reach_the_same_optimum_on_fixed_n300_dataset`, last assertion `abs(sigma2_F - 0.187) < 0.01` (observed 0.2061, identical with or without single-thread BLAS). That constant was recorded on the cloud build, whose generated dataset differs from this machine's (X2-F7); all convergence assertions in the test (five starts at the same optimum, certificate) passed. Editing an Experiment-1 test needs an Opus/owner decision; flagged, not edited. |
