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

## Opus Stage-0 gate review (2026-10-05; approved by the owner)
| ID | Decision / finding |
|---|---|
| X3-F07 | **X3-F05 explained.** The lower free-b SE is a composite-likelihood effect, not a property of correctly specified likelihoods. With J replaced by H, the order reverses (free 0.0104 >= known 0.0034 at tau_F = 10, N = 1000), and J/H = 502 for sigma2_F, reflecting strong dependence among a learner's 6,216 pairs. 97.8 % of the per-learner variance of the known-b sigma2_F score is explained by the 48 difficulty scores (item-marginal sampling noise). With b known, sigma2_F is pinned largely through the marginal probit scale (Experiment-1 L6 channel); freeing b projects that noise out. Asymptotic and design-based; finite-sample check in H3f. |
| X3-D07 | **Gate passed** (X3-D03): b free, tau_F = 10, N = 1000: rank 66/66, design SE 0.012 < 0.08. Proceed to Stage 1. |
| X3-D08 | **U3 redefined:** tau_F = 1 min (design SE free 0.063 vs known 0.023), fits only, known vs free, no null test. tau_F = 0.2 is dropped as a confirmatory cell (non-identified by the section-1 theorem; Stage-0 SE 2.1) and kept as a 5-replicate N = 1000 fits-only appendix illustration. |
| X3-D09 | **New descriptive hypothesis H3f (paired):** in U1 (tau_F = 10), report SD(sigma2_F-hat, free)/SD(sigma2_F-hat, known) on identical datasets with a replication-bootstrap CI, against the design ratio 0.57, alongside the mean bias of both estimators. |
| X3-D10 | **Pilot content:** U1 and U2 at N = 300 and 1000, 3 replications each, known/free/cal on the same datasets; one free-b null bootstrap (B = 19) per null cell; U3 (tau_F = 1) 2 replications; per-fit and per-null-replicate timings; certificates on all 66 coordinates and start agreement. Escalate if free-b fits fail to converge, start agreement is poor, or the projected cost exceeds 150 CPU-h. |
| X3-D11 | **X3-F06:** the Experiment-1 test with the cloud-build constant 0.187 stays unchanged (Experiment 1 frozen); documented as a known build-dependent assertion. |

## Stage 1 and pilot (Sonnet, 2026-10-05; numbers in docs/experiment_03_pilot_report.md; the review is Opus's)
| ID | Record |
|---|---|
| X3-F08 | Stage-1 implementation in `difficulty_free/`: model.py (free-b objective, d ll/d b_q = - sum wa_t / sd_t, starts from item marginals), fit.py (`fit_free`, D19/D22, embedded null), simulator.py (misfit lambda_q, lambda == 1 reproduces kt_trial), jobs.py (known/cal/free arms on the same dataset; free-b null replicate), runner.py, summarize.py; `configs/experiment_03/stage_pilot.yaml`; tests `test_difficulty_free_fit.py` (8) and `test_difficulty_free_runner.py` (3). Gradient matches finite differences including the 48 difficulties; free objective equals kt_trial at the true difficulties; B2-free(sigma2_F = 0) equals B1-free. |
| X3-F09 | **Pilot: 64/64 jobs ok, 0 errors, 15.4 min wall on 18 workers, 3.95 CPU-h.** Same-dataset comparison (3 replications): the calibrated-difficulty estimator is strongly biased upward (sigma2_F-hat 0.26 / 0.36 at U1 N = 1000 / 300; 0.31 / 0.17 with F absent), the known and free estimators are close to the truth. |
| X3-F10 | **Cost projection exceeds the ceiling (escalation per X3-D10):** protocol section-4 matrix as written projects to **382 CPU-h** (fits 17.6; null bootstraps 364, dominated by free-b null replicates at about 208 s each). Alternatives priced in the pilot report (96-290 CPU-h). Needs an Opus/owner decision before freezing. |
| X3-F11 | Full suite on the owner's PC: Experiment-3 tests pass; the only failure remains the pre-existing Experiment-1 constant (X3-F06). |
