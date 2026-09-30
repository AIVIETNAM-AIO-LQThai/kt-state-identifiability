# Experiment 1 — Stage 1 (smoke) report

**Purpose:** verify the pipeline (generation, fitting, determinism, artifacts, failure handling, resume, direction of
recovery). Two seeds at N = 64 are **not** evidence for the research claim.
Results: `results/experiment_01/smoke/494d1072b9/` (`manifest.json`, `jobs/*.json`, `summary.json`, `summary.md`). Design audit: `results/experiment_01/audit/design_audit.json`.
Environment: Python 3.12.3, numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, PyYAML 6.0.3 (local pins 2.5.3/1.18.1 unavailable in the container).
Run from a clean, committed tree (git 64f00bd), config hash `494d1072b9`.

## 1. Implemented model and estimator (short)
Probit latent response with known item difficulties; slow kernel `H^s=(1-(1-phi)^n)/phi` over prior practice exposures, fast kernel
`H^f=sum exp(-age/tau_R)`, learner-specific Gaussian gains, unstructured `Sigma_M`, and a session-resetting stationary OU state `F`
(B2). Population-level estimator: all-pairs equal-weight pairwise composite likelihood from per-template pair-count tables (8 templates x 6216 pairs),
BVN by tetrachoric series / Gauss-Legendre, analytic gradient, L-BFGS-B with variance coordinates bounded at exactly 0, 5 deterministic starts per fit
(tau_R grid for B1, tau_F grid for B2, embedded-null candidate so CLR >= 0). Inference: learner-score sandwich (interior parameters only), learner
bootstrap, and a parametric-bootstrap composite-LR test of sigma2_F = 0 that repeats the full B1 and B2 searches in every replicate.

## 2. Commands (PowerShell or bash, repo root; see README)
`python -m pytest -q` · `python -m kt_trial audit-design` · `python -m kt_trial run --config configs/experiment_01/stage_smoke.yaml --dry-run` ·
`python -m kt_trial run --config configs/experiment_01/stage_smoke.yaml --workers 4` · `python -m kt_trial summarize --results results/experiment_01/smoke/494d1072b9`

## 3. Tests
51 tests, all passing (`pytest -q`, 2 min 36 s including slow Monte-Carlo/optimisation tests). Coverage: schedule/exposure indexing, kernels and limits,
analytic mean/covariance vs 400k-learner Monte Carlo, session reset (clean and S6), S7 jump, S8 gain distribution, PSD, Jacobians vs finite differences,
BVN vs scipy (< 1e-11), pair-probabilities vs scipy, gradient vs finite differences, scores sum to gradient, nesting B2(sigma2_F=0)=B1 and B1(r,sigma2_r=0)=B0,
transform round trips, fit recovery on a small case, null-boundary behaviour, failed-fit recording, sandwich vs learner bootstrap, null-test determinism,
identifiability on the real (full rank) and deliberately deficient (rank 16/18) designs, runner resume/idempotency/corruption/mismatch/error/frozen-gate.
Additional acceptance checks: a fit job and a null replicate re-executed in a fresh directory reproduce the stored results exactly (excluding timestamps/runtimes).

## 4. Smoke run
52 jobs (4 fit, 38 null-bootstrap replicates, 10 learner-bootstrap replicates): 52 ok, 0 errors, 0 failed fits, all fits converged, none flagged.
Wall 10.3 min on 4 workers; CPU 0.66 h (cap 1 h / 30 min: met). Mean seconds: fit job 60, null replicate 53, learner-bootstrap replicate 15.

Direction of recovery (2 reps per scenario, N = 64 — descriptive only):
- B1/B2 recover `alpha_bar, phi, r_bar, tau_R` within ~0.5 SE; B0 (fast recency omitted) is strongly biased (`alpha_bar` +0.18/+0.10), as expected under misspecification.
- S1: `sigma2_F` = 0.115 and 0.115 (truth 0.16; bias -0.045), `tau_F` overestimated (large variance). S2: `sigma2_F` estimate exactly 0 in 1 of 2 fits (boundary flagged, `tau_F` reported unidentified).
- `sigma2_r` (truth 0.0225) is at its lower bound 0 in every B2 fit, and `sigma2_alpha` (0.0025) in half: gain-variance parameters are not recovered at N = 64.
- Null test (B = 19): S1 dataset CLR = 105, p = 0.05 (the minimum attainable) -> reject; S2 dataset CLR = 0, p = 1 -> not reject.
- Sandwich vs learner-bootstrap SD (S1 dataset, B2): ratios 0.5–0.9 for most parameters (sandwich smaller; 10 replicates only) — to be examined at Stage 2 with B = 50.
- Held-out pairwise composite score: B1−B0 strongly positive; B2−B1 small (+0.65 ± 0.70 per learner in S1, +0.19 ± 0.19 in S2).

## 5. Design audit and identifiability (see audit JSON)
Schedule: 8 templates x 112 observations; 4 pre-exposure anchors per learner (+4 more at H^s <= 1); 36,864 cross-session pairs over 216 exposure-count profiles;
12,864 within-session pairs (lags 0–40 min; 496 < 1 min, 4,127 in 10–20 min); 960 within-session probe pairs (no fast-recency contamination);
4,512 cross-skill comparable-history pairs; pair-regressor condition number 5.8; corr(H^s, H^f) = 0.05.
Local identifiability (Jacobian of Phi(a_t) and Phi2 pair probabilities, Bernoulli-sd weighted, 18 free coordinates, all templates jointly):

| point | rank | cond. number | weakest direction (loading) | pred. SE sigma2_F (N=300 / 1000) | pred. SE tau_F (N=300) |
|---|---|---|---|---|---|
| generating | 18/18 | 1,185 | log tau_F (-1.00) | 0.0385 / 0.0211 | 3.1 min |
| alt interior (sigma2_F .04, tau_F 20, tau_R 3, phi .3) | 18/18 | 3,347 | log tau_F (-1.00) | 0.0318 / 0.0174 | 28 min |
| MDE point (sigma2_F .04) | 18/18 | 4,654 | log tau_F (-1.00) | 0.0338 / 0.0185 | 11.5 min |
| deficient control (F = learner intercept) | **16/18** | 1e18 | tau_F; sigma2_F vs common Sigma_M shift | — | — |

Finite-difference vs analytic Jacobian: max relative singular-value difference 9e-7 (h = 1e-4), 9e-9 (h = 1e-5). Sigma2_F if all nuisance parameters were known: SE 0.0043 (N=300) —
about 9x smaller than with nuisance uncertainty; its estimator is correlated -0.77 to -0.92 with tau_F and about 0.3 with Sigma_M diagonals and sigma2_r.
Full rank supports **local** identification only; it is not global uniqueness or finite-sample recovery.

## 6. Projected cost (measured; per-start cost is N-independent, iterations similar at N = 300)
- Stage 2 (N = 300, 3 reps, 10 scenarios, B = 99 null tests on S1, S2, S8n, B = 50 learner bootstrap): fits ~30 x 1.5–2 min ≈ 1 CPU-h; null replicates 891 x ~53–100 s ≈ 13–25 CPU-h; learner bootstrap ≈ 0.2 CPU-h.
  Central ≈ 15 CPU-h (≈ 4 h wall on 4 workers); pessimistic ≈ 27 CPU-h (≈ 7 h) — pessimistic case exceeds the 20 CPU-h / 6 h caps, so Stage 2 should be dry-run costed before launch.
- Stage 3 (provisional S1, S2, S8 x N in {300, 1000} x 10 reps): 180 fits ≈ 4–6 CPU-h; null bootstraps 60 datasets x 199 x ~53–100 s ≈ 175–330 CPU-h (≈ 2–3.5 days wall on 4 workers). Requires a decision on B, on which cells get null tests, or on compute at the Stage 3 request.

## 7. Known weaknesses, failed checks, open decisions
- No check failed. `tau_F` (and `sigma2_r`, `sigma2_alpha`) are weakly identified; at N = 300 the design-based SE of sigma2_F (0.03–0.04) is about the size of the provisional MDE/bias tolerance 0.04 (finding F1/F2 in the decision log). Whether thresholds, N, or the schedule should change is a scientific decision for the Opus review / user, not made here.
- Smoke sandwich-vs-bootstrap ratio (~0.5–0.9) suggests small-N under-coverage risk; only 10 bootstrap replicates.
- Deviations from plan wording: D13 (B1 start policy independent of B0), D14 (series BVN), D12 (solver tolerances) — content-preserving; see decision log.
- Fits use PairCounts (sufficient), so N is the number of fitting learners; held-out learners are separate (64 here).
- Machine differs from the user's local numpy/scipy versions; versions are stored in each manifest.

## 8. Recommendation
Pipeline is ready for the Opus smoke/audit review. Ready for Stage 2 **subject to** that review (`pass`, `pass with stated limitations`, or `blocked`) and to a dry-run cost check of the Stage 2 config.


## 9. Re-smoke after the H1 corrections (C1–C5, D19, D22)
Results: `results/experiment_01/smoke/0e7ec61e6f/` (code hash changed; the first smoke in `.../494d1072b9/` is kept for the record).
52/52 jobs ok, 0 errors, wall 19.2 min, 1.26 CPU-h (estimate 1.40; the plan's 1.0 CPU-h smoke cap was exceeded, as flagged in F3).
Full suite: 57 tests pass. Deterministic re-execution of `fit__S2__N64__r1` and `null_rep__S2__N64__r0__b3`: identical.

| B2 fit | start log-lik spread before | after | sigma2_F / tau_F before | after | starts at best | Newton decrement |
|---|---|---|---|---|---|---|
| S1 N64 r0 | 24.98 | 0.000 | 0.1133 / 21.07 | 0.1133 / 21.10 | 5 | 3.2e-09 |
| S1 N64 r1 | 18.70 | 0.000 | 0.1162 / 10.32 | 0.1164 / 10.27 | 5 | 1.6e-09 |
| S2 N64 r0 | 0.01 | 0.000 | 0.0000 / 1.00 | 0.0000 / 30.04 | 5 | 2.0e-09 |
| S2 N64 r1 | 1.94 | 2.050 | 0.0320 / 29.96 | 0.0336 / 17.60 | 4 | 1.1e-09 |

Unblock criteria (H2c/D22): (1) suite passes; (2) 0 job errors, all fits converged, max Newton decrement 3.2e-9 (<= 1e-3), 0 non-PD Hessians,
S1 B2 fits reach the best with 5/5 starts; (3) deterministic rerun identical; (4) S2 sigma2_F / tau_F reported as NA with no coverage entries;
(5) Stage 2 dry-run 15.2 CPU-h, ~3.8 h wall. All five met. Null tests are unchanged in direction (S1 p = 0.05 = minimum attainable with B = 19; S2 p = 0.95).
