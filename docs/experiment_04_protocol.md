# Experiment 4: recovering F when items have unknown discriminations

**Status:** approved by the owner on 2026-10-08 (Opus plan approval). Branch `exp/discrimination-robust-recoverability`, package `discrimination_free/`. Nothing frozen; Stage 0 is next.

## Context
**From Experiment 3 and its calibration addendum (X3-D14, X3-D17):**
- With free item difficulties, σ²_F is recovered well.
- The bootstrap null test is **liberal under item-discrimination misfit**: about 13 % at nominal 5 %, and 17 % at N = 1000. The bootstrap simulates from a model with equal discriminations, so misfit-induced covariance is partly read as F.
- Under a correctly specified null, the test's level stayed inconclusive (0.10, CI [0.035, 0.155]).

Real items always differ in discrimination, so the free-difficulty test cannot yet be trusted for marginal results.

**Experiment 4's question:** if discriminations are estimated too (a 2PL-type model), does σ²_F stay recoverable, and does the null test become calibrated?

**Outcome sought:** a model and test that are usable when items both misfit and have unknown parameters, or a clear statement that they are not. Synthetic data only; F is a statistical component, never a psychological label.

## 1. Model and identification (derived before simulating)
**The 2PL-type model:** Z_t = −b_q + λ_q·(M0[k] + α_u H^s + r_u H^f + F_t) + ε_t, with ε ~ N(0, 1), item difficulty b_q and discrimination λ_q > 0.

**Moments** (computable from `kt_trial.moments.latent_moments` evaluated with b = 0):
- μ_t = −b_q + λ_q·μ⁰_t;
- V_tt' = λ_q λ_q'·L_tt' + δ_tt';
- here μ⁰ and L are the Experiment-1 latent mean and covariance without the residual.

**Scale invariance:** (λ·c, latent/c) leaves every observable unchanged. Identification therefore needs one constraint: **geometric mean of λ = 1** (Σ log λ_q = 0), giving 47 free log-λ coordinates. The model has 18 + 48 + 47 = **113 parameters**.

**Consequence for the truth (estimand).** Under this normalisation, the estimand is σ²_F* = σ²_F · g², where g is the geometric mean of the dataset's true λ. g is computed per replication from the realised λ. For lognormal λ with CV 0.3, g ≈ 0.958 in expectation, so σ²_F* ≈ 0.147 rather than 0.16. Without this, a 2PL fit would show a spurious −8 % "bias".

**Expectations:**
- **The white-noise ridge** of Experiment 3 (§1 there) still applies, since b is free. F is identified only through its time-structured covariance, so the primary cell keeps τ_F = 10.
- **λ_q cannot mimic F's time-decaying covariance.** Items are randomised across positions and templates, so λ_q acts on all pairs involving item q regardless of lag. F should stay identified, at some cost in precision. **Stage 0 checks this numerically.**

## 2. Hypotheses (frozen after Stage 0 and the pilot)
- **H4a:** with 2PL estimation, σ²_F* at τ_F = 10 is recovered within ±0.04 (Monte Carlo CI of the bias) under discrimination misfit (λ CV 0.3), and also with equal discriminations (no overfitting penalty in bias).
- **H4b:** the 2PL bootstrap null test is **calibrated under discrimination misfit**: warp-speed α̂ "consistent with 5 %" (X3-D15 rule). This is the case where the free-difficulty 1PL test was liberal.
- **H4c:** the 2PL null test is calibrated under the clean null (λ ≡ 1).
- **H4d** (descriptive): the price of 2PL is the SD ratio SD(2PL)/SD(1PL-free) of σ̂²_F on identical datasets with λ ≡ 1, plus λ recovery (RMSE of log λ̂).
- **H4e** (descriptive): under misfit with F present, the bias of 1PL-free against 2PL on the same data (Experiment 3 found −0.014 for 1PL-free).

## 3. Stages (each ends with a handoff; nothing advances automatically)
**Stage 0, analytic audit** (Sonnet; under 1 CPU-h; no fitting):
- Extend the Experiment-3 audit (`difficulty_free/freeb.py`, `audit.py`) with 47 log-λ coordinates under the geometric-mean constraint.
- At τ_F = 10, report:
  - rank (113/113?), condition number and the weakest directions;
  - the design Godambe SE of σ²_F at N = 300/1000/3000, for 2PL against 1PL-free, at λ ≡ 1 and at a λ CV 0.3 draw.
- Check the scale invariance numerically (rescaling λ and the latent variances leaves a and ρ unchanged).
- **Gate (Opus):**
  - if the 2PL design SE at N = 1000 exceeds 0.08, or the model is rank-deficient, re-scope before building;
  - if the SE is more than 3× the 1PL-free SE, the N values are reconsidered.

**Stage 1, estimator and pilot** (Sonnet). The new package **`discrimination_free/`** imports `difficulty_free/` and `kt_trial/` and modifies neither (both are frozen with their experiments).
- **Objective:** 2PL pairwise composite likelihood. The analytic gradient is obtained by mapping the adjoints through μ = −b + λ∘μ⁰ and V = (λλᵀ)∘L + I:
  - ∂/∂μ⁰ = λ∘g_μ;
  - ∂/∂L = (λλᵀ)∘G;
  - ∂/∂λ_q gets the μ and V terms of the positions of item q;
  - the kernel and Σ_M contractions are as in `kt_trial.composite_likelihood._adjoint_gradient`.
- **Starts and stopping:** λ starts at 1 and b from item marginals (`difficulty_free.model.start_difficulties`). The D19 stopping rule and D22 certificate apply on all active coordinates.
- **Null test:** the bootstrap simulates from the fitted B1-2PL with its λ̂ and b̂ (`difficulty_free.simulator.simulate_lambda` already supports λ).
- **Warp job:** as in `difficulty_free/jobs.run_warp_job`, for both the 2PL and the 1PL-free estimator on the same dataset.
- **Tests:**
  - the gradient (including λ) against finite differences;
  - with λ ≡ 1 fixed, the objective equals `difficulty_free`;
  - scale invariance;
  - nesting (B2-2PL with σ²_F = 0 equals B1-2PL);
  - recovery of λ on a large-N smoke dataset;
  - the estimand normalisation g.
- **Reproducibility:** the CLI sets `*_NUM_THREADS=1` before numpy loads. Results record the environment and data hashes. The runner keeps resume, dry-run, frozen gate and the **enforced CPU cap**.
- **Pilot:** 3 replications per cell for the recovery fits and 3 warp datasets per null cell, giving timings and certificates.

**Stage 2:** Opus reviews the pilot, sets the final matrix within the budget and freezes the rules. The owner gives the go-ahead.

**Stage 3:** confirmatory run on the owner's idle PC (`.venv12`, single-thread BLAS, 18 workers). Then Opus interprets.

## 4. Proposed confirmatory matrix (final sizes set from measured pilot costs)
| cell | process (τ_F = 10) | estimators on identical datasets | purpose |
|---|---|---|---|
| V1 | λ ≡ 1, F present | 1PL-free, 2PL | H4a (no misfit), H4d |
| V2 | λ ≡ 1, F absent | 2PL (warp) | H4c |
| V4 | λ CV 0.3, F absent | 2PL and 1PL-free (warp, paired) | H4b; replicates X3-D17 on fresh data |
| V5 | λ CV 0.3, F present | 1PL-free, 2PL | H4a (misfit), H4e |

- **Recovery cells (V1, V5):** N ∈ {300, 1000}, 20 replications, fits only. Free-difficulty power was already 20/20 in Experiment 3; a 2PL power check uses 3 datasets per cell, descriptive only.
- **Calibration cells (V2, V4):** warp-speed with 100 datasets per N.
- **Rough cost** (assuming a 2PL fit about 2.5× a 1PL-free fit; verified in the pilot): recovery about 30 CPU-h, warp about 100 CPU-h. **Planning cap 150 CPU-h, enforced by the runner.** If the pilot projects more, the warp datasets are reduced to 75 per N (pooled SE then about 0.025) before freezing.

## 5. Decisions for the owner (my recommendation first)
| # | decision | recommendation |
|---|---|---|
| 1 | Scope | the V1/V2/V4/V5 matrix above, τ_F = 10 only (τ_F dependence was settled in Experiment 3) |
| 2 | Identification | geometric mean of λ = 1, with the estimand σ²_F* = σ²_F·g² computed per replication |
| 3 | Budget and venue | ≤ 150 CPU-h enforced, set at the Stage-2 review; owner's PC, idle, 18 workers |
| 4 | Branch and package | `exp/discrimination-robust-recoverability` (created by the owner from `exp/unknown-difficulty-recoverability`); package `discrimination_free/` |
| 5 | Not included | guessing or slipping parameters (3PL/4PL), multidimensional items, real data, adaptive schedules |

## 6. Verification
- **Stage 0:** the scale-invariance check holds exactly. Under λ ≡ 1 with λ fixed, the audit reproduces Experiment 3's 1PL-free SE at τ_F = 10 (0.0221 / 0.0121).
- **Stage 1:** the full `pytest` suite passes (X3-F06 remains the only known failure), and a tiny end-to-end run, resume, dry-run and cap stop all work.
- **Stages 2–3:** rules and the frozen sha are recorded before the run, then gates are checked before any rule.

## 7. Model handoffs (the owner switches models; the owner runs git)
1. **Now (Opus):** after approval, write `docs/experiment_04_protocol.md`, `experiment_04_decisions.md` (X4-D01…) and `experiment_04_handoff.md`, and list the git commands, including branch creation.
2. **Switch to Sonnet 5.5:** Stage 0 audit.
3. **Switch to Opus:** gate review.
4. **Switch to Sonnet:** Stage 1 and the pilot.
5. **Switch to Opus:** pilot review and freeze plan.
6. **Sonnet:** freeze, then the run after the owner's go-ahead.
7. **Opus:** interpretation.
