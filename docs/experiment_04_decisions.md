# Experiment 4: decision and findings log

IDs use the prefix X4. F is a statistical component, never a psychological label.

## Approved by the owner (Opus plan approval, 2026-10-08; details in `docs/experiment_04_protocol.md`)
| ID | Decision |
|---|---|
| X4-D01 | **Question:** with item discriminations estimated as well as difficulties (2PL-type pairwise model), is sigma2_F recoverable and is the bootstrap null test calibrated, in particular under discrimination misfit where the free-difficulty 1PL test was liberal (X3-D17)? Hypotheses H4a-H4e (protocol section 2), frozen after Stage 0 and the pilot. |
| X4-D02 | **Identification:** Z = -b_q + lambda_q (M0 + alpha H^s + r H^f + F) + eps; scale fixed by geometric mean of lambda = 1 (47 free log-lambda coordinates; 113 parameters). **Estimand** sigma2_F* = sigma2_F * g^2, with g the geometric mean of the replication's realised true lambda (about 0.958 at CV 0.3). |
| X4-D03 | **Stage 0 gate:** analytic audit at tau_F = 10, lambda == 1 and a lambda CV 0.3 draw. Re-scope if the 2PL design SE of sigma2_F at N = 1000 exceeds 0.08 or the model is rank-deficient; reconsider N if it exceeds 3x the 1PL-free SE. |
| X4-D04 | **Scope:** cells V1 (lambda == 1, F), V2 (lambda == 1, no F), V4 (lambda CV 0.3, no F), V5 (lambda CV 0.3, F); tau_F = 10; recovery fits on V1/V5 (N in {300, 1000}, 20 replications), warp-speed calibration on V2/V4 (100 datasets per N; 2PL, plus paired 1PL-free on V4). Not included: 3PL/4PL, multidimensional items, real data, adaptive schedules. |
| X4-D05 | **Budget and venue:** <= 150 CPU-h, enforced by the runner; final sizes set from measured pilot costs at the Stage-2 review; owner's PC, idle machine, `.venv12`, single-thread BLAS, 18 workers. |
| X4-D06 | **Code and branch:** new package `discrimination_free/` (imports `difficulty_free/` and `kt_trial/`, modifies neither); branch `exp/discrimination-robust-recoverability`. The owner runs all git. |
