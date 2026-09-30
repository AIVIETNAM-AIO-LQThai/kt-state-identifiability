# Experiment 1 — Stage 2 (diagnostic) report

**Status:** Stage 2 executed as approved (D20: null bootstrap B = 49). This is a **diagnostic**: 3 replications per scenario at N = 300 fitting
learners (+ 300 held-out learners each, 600 generated per dataset). Nothing here is confirmatory evidence, and the provisional thresholds
are descriptive only. Descriptive results with 3 replications carry large Monte Carlo uncertainty (MCSEs shown).
Results: `results/experiment_01/diagnostic/eeb188ecc6/` (`manifest.json`, `jobs/`, `summary.json`, `summary.md`); code hash and versions are in the manifest.
Code: git `444e7e2` lineage (D19 stopping rule, D22 Newton certificate); environment as in the smoke report.

## 1. Execution
521/521 jobs ok (30 fit, 441 null-bootstrap replicates, 50 learner-bootstrap replicates), 0 errors, 0 failed fits, 0 failed replicates.
Wall 162 min on 4 workers; CPU 10.75 h (projection 15.2 CPU-h; caps 20 CPU-h / 6 h met). Per-job means: fit 110 s (0.92 CPU-h total), null replicate 78 s (9.5 CPU-h), learner-bootstrap replicate 23 s (0.32 CPU-h).

## 2. Estimator health (all 10 scenarios, B2)
- Convergence rate 1.00 in every scenario; 0 failed fits.
- Newton decrement (D22) at most 2.0e-4 (S8n), otherwise ≤ 1e-7, always below the 1e-3 tolerance; 0 non-PD Hessians; 0 `newton_decrement_large` flags.
- Start agreement: 0 % single-start-at-best and 0 % secondary optima in every scenario (all 5 starts reach the best), including S2. So the H1 concern about
  multiple τ_F optima under the null did not appear at these seeds.
- Boundary behaviour: σ²_r on its lower bound in 33–100 % of B2 fits depending on scenario (S4b 100 %); σ²_α on its lower bound in some S6/S7 fits.
  σ²_F on its lower bound in 100 % of S2 fits and 33 % of S8n fits. τ_R hit its upper bound in all three S7 fits.

## 3. Primary estimand σ²_F (B2)

| scenario | truth | bias | MCSE | RMSE | share σ̂²_F = 0 | comment (3 reps) |
|---|---|---|---|---|---|---|
| S1 clean | 0.16 | +0.002 | 0.022 | 0.032 | 0 | bias vs 0.04 tolerance: inconclusive (MCSE too large) |
| S2 null | 0 | NA (boundary) | — | — | 1.00 | mean estimate 0.000 |
| S3 no fast recency | 0.16 | −0.034 | 0.005 | 0.034 | 0 | near tolerance |
| S4a τ_F = 0.2 min | 0.16 | −0.015 | 0.009 | 0.020 | 0 | within tolerance; τ_F recovered (bias ≈ 0) |
| S4b τ_F = 60 min | 0.16 | +0.028 | 0.034 | 0.055 | 0 | inconclusive; τ_F biased +26 min |
| S5 blocked | 0.16 | −0.015 | 0.012 | 0.023 | 0 | inconclusive |
| S6 correlated start | 0.16 | +0.019 | 0.036 | 0.054 | 0 | inconclusive |
| S7 endogenous context | 0.16 | **+0.145** | 0.003 | 0.145 | 0 | violation inflates σ²_F; τ_F biased +82 min |
| S8 lognormal gains | 0.16 | −0.039 | 0.008 | 0.040 | 0 | at the tolerance edge; σ²_F underestimated |
| S8n gains, F absent | 0 | NA (boundary) | — | — | 0.33 | mean estimate 0.016 (max 0.046) |

τ_F (secondary): S1 bias +1.8 ± 3.1 min (3 reps); it is interpretable only where σ̂²_F is clearly positive (L2) and is very poorly determined at long τ_F (S4b, S7).

## 4. Boundary-aware null test (composite LR, B = 49, parametric bootstrap; minimum attainable p = 0.02)
- S1 (F present): 3/3 datasets reject (p = 0.02 each, the minimum attainable); CLR 622–1114, well above the bootstrap-null 99 % quantiles (127–189).
- S2 (F absent): 0/3 reject (p = 0.60, 0.66, 0.98); observed CLR 0.00; bootstrap-null share of σ̂²_F = 0 about 0.41–0.55 (boundary mass as expected). The bootstrap-null CLR distribution is heavy-tailed (95 % quantile 54–175, 99 % quantile 118–222 across datasets), far from a χ² reference (95 % point ≈ 3.8), which is why only bootstrap p-values are used (L4).
- S8n (F absent, non-Gaussian correlated gains): 0/3 reject (p = 0.50, 0.96, 0.16), but one dataset gave σ̂²_F = 0.046 and CLR = 56.7 (p = 0.16, not rejected).
  This is a descriptive warning that misspecified gain heterogeneity can move mass towards σ²_F; the bootstrap test calibrated under the Gaussian-gain B1 null did not reject it, but 3 datasets cannot estimate a false-positive rate (Clopper–Pearson 95 % upper bound 0.71).
- Held-out pairwise composite score, B2 − B1 (per learner, mean over 3 reps): S1 +1.08 ± 0.56 (positive 2/3); S2 0.00; S8n −0.07 ± 0.07; S7 +6.1 ± 0.7.
  B1 − B0 is +33 to +127 in every scenario, i.e. omitting fast recency is strongly penalised.
  These are population-marginal composite scores on held-out learners, not next-response predictions.

## 5. Other parameters and inference
- S1 B2 biases (3 reps): ᾱ +0.007 ± 0.007, φ +0.004 ± 0.001, σ²_α +0.0004 ± 0.0009, r̄ +0.006 ± 0.009, τ_R −0.26 ± 0.19, σ²_r +0.001 ± 0.013.
  B0 (fast recency omitted) is biased in ᾱ by +0.18 in S1.
- Sandwich coverage of the truth (S1, B2; conditional on interior fits; unconditional in the summary): 3/3 for every parameter except σ²_r 2/2 (one fit on the bound). With 3 fits this says only that no gross failure appeared.
- Learner bootstrap (B = 50, S1 rep 0) versus the sandwich SE: ratios sandwich/bootstrap = 1.12 (ᾱ), 1.27 (φ), 1.34 (σ²_α), 1.21 (r̄), 1.07 (τ_R), 1.24 (σ²_r), **0.90 (σ²_F)**, **0.46 (τ_F)**.
  So at N = 300 the sandwich is mildly conservative for the mean/kernel parameters (the smoke concern L1 did not materialise), but for σ²_F it is about 10 % too small and for τ_F it is about half the bootstrap SD.

## 6. Reading against the H1 limitations
- L1 (gain variances): σ²_r on its bound in a third to all of the fits; the sandwich is not too small for the other parameters (ratios ≥ 1.07).
- L2 (τ_F weak): confirmed; sandwich SE for τ_F is not trustworthy (ratio 0.46).
- L3 (MDE): unchanged; S1 σ²_F RMSE = 0.032 at N = 300 is of the size of the tolerance (0.04); no scenario at σ²_F = 0.04 was run.
- L4: CLR values under S2/S8n are ≈ 0 with about half the bootstrap-null mass at the boundary; only bootstrap p-values are used.

## 7. Failures, deviations, uncertainty
No job errors and no failed fits or replicates. Deviations from the original prompt/plan (all recorded): B = 49 instead of 99 (D20), stopping rule D19, Newton certificate D22, B1 start policy D13.
All statements above rest on 3 replications per scenario and 3 datasets per null-test scenario; pass/fail rates are inconclusive and are reported with MCSE / Clopper–Pearson limits, never as findings.

## 8. Stage 3 — inputs for the Opus approval request (not decided here)
- Measured cost: fit job ≈ 110 s; null replicate ≈ 78 s (B1+B2 searches). Provisional matrix S1, S2, S8 × N ∈ {300, 1000} × 10 reps: fits ≈ 180 fit-jobs ≈ 5.5 CPU-h at these rates (N = 1000 not yet timed; per-start cost is N-independent); null bootstrap with B = 199 on 60 datasets = 11,940 replicates ≈ 257 CPU-h (≈ 2.7 days on 4 workers). Alternatives to consider: null tests on fewer datasets, B = 99, or S2/S8n-only null tests plus S1 power on a subset.
- Design-based SE(σ²_F) at N = 1000 ≈ 0.02; the MDE 0.04 criterion needs a decision (D21).
- Open scientific questions for Opus: S7 shows endogenous context inflates σ²_F (+0.145) — what claim does the confirmatory scope make; S8 under-estimates σ²_F (−0.039) and S8n shows the null test's exposure to non-Gaussian gains; whether σ²_F bias tolerance 0.04 is meaningful given S1 MCSE ≈ 0.02 with 3 reps and RMSE ≈ 0.03; τ_F's role.
