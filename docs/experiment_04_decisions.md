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

## Stage 0 results (Sonnet, 2026-10-08; numbers in docs/experiment_04_stage0_report.md; the gate review is Opus's)
| ID | Record |
|---|---|
| X4-F01 | Implementation: `discrimination_free/` (twopl.py: 2PL observable map mu = -b + lambda mu0, V = (lambda lambda') L + I with derivatives in the 18 model coordinates, 48 difficulties and 47 sum-zero log-lambda coordinates; audit.py; cli.py sets `*_NUM_THREADS=1` before numpy), `configs/experiment_04/stage0.yaml`, `tests/test_discrimination_free.py` (8 tests: sum-zero basis; lambda == 1 reproduces difficulty_free's Jacobian and Fisher; finite-difference checks of the derivatives in lambda, b and the model parameters; exact scale invariance; normalisation to geometric mean one; scores centred at the truth). `.venv12`, single-thread BLAS. |
| X4-F02 | **Consistency:** with lambda == 1 and lambda fixed, the design SE of sigma2_F at tau_F = 10 is 0.0221 / 0.0121 / 0.0070 (N = 300 / 1000 / 3000), identical to the Experiment-3 1PL-free audit. Scale invariance holds to 4e-16. |
| X4-F03 | **Gate numbers (X4-D03):** 2PL, tau_F = 10, N = 1000: rank 113/113 at both audit points; design SE of sigma2_F* **0.0122** (lambda == 1; ratio 1.01 to lambda fixed) and **0.0114** (a lambda draw with CV 0.27, g = 0.947, sigma2_F* = 0.143); threshold 0.08. Two further seeds/draws: SE 0.0128 and 0.0116, rank 113/113. |
| X4-F04 | **Flagged for Opus:** at the lambda CV 0.3 point the SE with lambda FIXED at its true values is 0.034 (N = 1000), three times the SE with lambda free (0.0114); same in two more draws (0.035, 0.035 vs 0.013, 0.012). Not an error of the code (the lambda == 1 point matches Experiment 3); the same composite-likelihood mechanism as X3-F07 is the likely cause but is not verified. Design SE of the log-discriminations: mean 0.14-0.15 (N = 1000), 0.26-0.28 (N = 300). |
| X4-F05 | Weakest direction (rel. singular value 6e-4) is tau_F with sigma2_F, as in Experiment 3; the estimator correlation of sigma2_F is -0.5 with tau_F. No new near-null direction from the 47 log-lambda coordinates. |
