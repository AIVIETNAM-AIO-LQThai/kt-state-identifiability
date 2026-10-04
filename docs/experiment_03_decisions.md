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
