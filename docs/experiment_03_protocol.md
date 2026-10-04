# Experiment 3: recovering F when item difficulties are unknown

**Status:** approved by the owner on 2026-10-05 (Opus plan approval). Branch `exp/unknown-difficulty-recoverability`. Nothing frozen; Stage 0 is next.


## Context
Experiments 1 and 2 are closed.
- **Experiment 1** recovered the population variance σ²_F of the shared transient latent state F. It did so only with **known item
  difficulties b**. Its limitation L6 noted that a near-white F is identified only through the marginal probit scale, which known b
  anchors, and that it can absorb marginal misfit.
- **Experiment 2** showed that individual tracking of F is limited by the observation channel. It too assumed known b.

Real item difficulties are always estimated, and items rarely fit a single-slope model. Experiment 3 asks whether the
population-level claim of Experiment 1 survives when b is unknown and items misfit. Without it, the Experiment-1 claim stays
conditional on an assumption that no application meets. F remains a statistical component throughout; no psychological label is used.

## 1. A result derived before simulating: a white-noise F is exactly non-identified when b is free
The latent moments are a_t = μ_t/√D_t and ρ_tt' = C_tt'/√(D_t D_t').

**Rescaling.** Replace every location parameter (b, ᾱ, r̄) by c times its value and every variance (Σ_M, σ²_α, σ²_r, σ²_F) by c² times
its value, and add white noise of variance c² − 1 to the unit residual. Then μ, D and C all scale by c and c², so a_t and ρ_tt' are
unchanged. All observable probabilities are therefore unchanged.

**Consequences:**
- **With b known,** this rescaling is blocked (b cannot scale), so the probit scale is fixed. That is exactly how Experiment 1 identified a near-white F (L6).
- **With b free,** a white-noise component is exactly confounded with the overall probit scale: a one-dimensional ridge.
- **An OU F with τ_F > 0** adds covariance only between same-session pairs, decaying with the time lag. Its variance is then identified only by
  extrapolating the short-lag covariance to lag 0. The shortest lag in the design is 0.4 min.
- **Prediction:**
  - with b free, σ²_F stays identified when τ_F is well above the response spacing (τ_F = 10);
  - it degrades as τ_F shrinks toward the spacing;
  - it is lost at τ_F → 0.

Stage 0 below verifies this numerically before any simulation is run.

## 2. Question and hypotheses
**Question.** Under the Experiment-1 generating process, can σ²_F (and the null test for σ²_F = 0) still be recovered when item
difficulties are (a) estimated jointly from the same data, or (b) taken from an external calibration with error? And does a common
item misfit, unequal item discriminations, create a spurious F or bias σ̂²_F?

**Hypotheses** (to be frozen after Stage 0 and the pilot):
- **H3a.** With b free (B2-free estimator), σ²_F = 0.16 at τ_F = 10 is recovered within the Experiment-1 tolerance: Monte Carlo CI of the bias within ±0.04, at N = 1000 (and N = 300, reported).
- **H3b.** With b free, the boundary-aware bootstrap test shows no excess false positives when F is absent (Experiment-1 PH3 rule).
- **H3c (predicted failure, descriptive).** With b free and a near-white F (τ_F = 0.2, the Experiment-1 S4a scenario), σ̂²_F is not recoverable. Estimates spread along the scale ridge, while the known-b estimator still recovers it.
- **H3d.** Unequal item discriminations with F absent do not produce false detections (PH3 rule). With F present they keep σ̂²_F within ±0.04.
- **H3e (practical arm).** A known-b estimator fed difficulties with calibration error (SD 0.2) over-estimates σ̂²_F through the near-white pathway (L6). The bias is reported continuously.

## 3. Stages (each ends in a handoff; nothing advances automatically)
**Stage 0: analytic identifiability audit with b free.** About 1 CPU-h or less; no simulation.
- Extend the Experiment-1 Jacobian/SVD audit (`kt_trial/identifiability.py`: `observable_jacobian`, `fisher_pairwise`) with the 48 item difficulties as free coordinates.
- Evaluate at τ_F ∈ {0.2, 1, 3, 10, 60} with the other parameters at their generating values.
- Report rank, the weakest singular vectors (do they align with the predicted scale ridge?), and predicted Godambe SEs of σ²_F at N = 300/1000/3000, against known b.
- **Gate (Opus review):**
  - if the design-based SE of σ²_F at τ_F = 10 with b free is above about 0.08 at N = 1000 (half the effect), the simulation matrix is re-scoped (larger N, or only the known-b and calibration arms) before any build;
  - if rank-deficient at τ_F = 10, stop and rethink.

**Stage 1: implementation (Sonnet).** New package `difficulty_free/` (purpose name). `kt_trial/` is untouched and only imported.
- **Estimators:**
  - B1-free and B2-free: b_q per item (48 parameters, skill-offset structure not imposed), M0 mean fixed at 0 for location.
  - B2-known: Experiment 1 unchanged.
  - B2-cal: b̂ = b + N(0, 0.2²) treated as known, with its own RNG namespace.
- **Likelihood:** reuse `composite_loglik` with each template's `b` replaced by the parameter values. The gradient with respect to b_q is −Σ over positions of item q of the μ-adjoint (`g_mu = wa/sd` in `_adjoint_gradient`), recomputed in the new package.
- **Multi-start:** b starts from the logit of each item's marginal proportion correct, scaled. Uses the τ_F grid of Experiment 1.
- **Misfit generator:** a new simulator with Z_t = −b_q + λ_q·(M0 + αH^s + rH^f + F) + ε, where λ_q is lognormal with mean 1 and CV 0.3, fixed per item and drawn once per replication in its own namespace. With λ ≡ 1 it must reproduce `kt_trial.simulator.simulate` bitwise (test).
- **Null test:** the bootstrap from the fitted B1 (free or known as appropriate) repeats the full B1+B2 search, as in Experiment 1.
- **Reproducibility (lesson X2-F15):** the CLI sets `OMP/OPENBLAS/MKL_NUM_THREADS=1` at import, before numpy loads. Every result records its interpreter and versions. The runner keeps resume, dry-run, manifest refusal and the frozen-config gate.
- **Focused tests:**
  - gradient against finite differences, including b;
  - B2-free with b fixed at the truth equals the `kt_trial` objective;
  - the white-noise scale ridge (σ²_F with τ_F → 0 and rescaled parameters give an identical objective; numeric check of §1);
  - small-N recovery;
  - simulator λ ≡ 1 equivalence;
  - B1/B2 nesting.

**Stage 2: pilot** (3 replications per cell, B = 19), then Opus review, the confirmatory request, freeze and the owner's approval.

**Stage 3: confirmatory run** on the owner's PC (`.venv12`, single-thread BLAS, 18 workers). Then Opus interpretation.

## 4. Proposed confirmatory matrix (final version set at the Stage-2 review, with measured costs)
| scenario | DGP | estimators | role |
|---|---|---|---|
| U1 | Experiment-1 S1 (F present, τ_F = 10) | known, free, cal | H3a, H3e |
| U2 | S2 (F absent) | known, free, cal | H3b, H3e |
| U3 | S4a (F present, τ_F = 0.2) | known, free | H3c (descriptive) |
| U4 | discrimination misfit, F absent | known, free | H3d, false attribution |
| U5 | discrimination misfit, F present | known, free | H3d, robustness |

- N ∈ {300, 1000}, 20 replications per cell, with null tests on 10 datasets per null cell (B = 99) and power cells (B = 19), as in Experiment 1.
- **Cost is unknown until the benchmark.** Each free-b fit has 66 parameters instead of 18, so it is expected to be 2–4× slower. Null bootstraps dominate.
- Planning ceiling: **≤ 150 CPU-h**, which is about 8 h wall on 18 workers. If the pilot projects more, B or the null cells are reduced before freezing, never after.

## 5. Decisions for the owner (my recommendation first)
| # | decision | recommendation | why |
|---|---|---|---|
| 1 | Scope | free-b + external calibration error + discrimination misfit, with U3 as the predicted failure | one experiment covers the realistic difficulty problem; U3 tests the §1 theory directly |
| 2 | Stage 0 before any build | yes; the gate as in §3 | cheap, and it can save the whole simulation if σ²_F turns out to be weakly identified |
| 3 | Venue and budget | owner's PC, ≤ 150 CPU-h, set at the Stage-2 review | 20 cores; the cloud container was reclaimed on long runs before |
| 4 | Branch | `exp/unknown-difficulty-recoverability`, created by the owner from `exp/transient-state-filtering` | purpose-named; the owner runs all git |
| 5 | Not included | unknown discrimination estimation (2PL), adaptive schedules, real data | each would be its own experiment |

## 6. Verification
- Stage 0: the predicted ridge appears as a near-null singular vector at τ_F → 0. The known-b SEs reproduce the Experiment-1 design audit (consistency check).
- Stage 1: the full `pytest` suite passes, including the new tests. A tiny end-to-end run, resume and dry-run work.
- Stages 2 and 3: the gates and rules are frozen before the confirmatory data exist. Provenance hashes and environment are in every result.

## 7. Model handoffs (the owner switches models manually; git is run by the owner)
1. **Now:** Opus discussion, which is this plan. After approval, Opus writes `docs/experiment_03_protocol.md` and the decision and handoff logs, and lists the git commands for the owner.
2. Switch to **Sonnet 5.5**: build Stage 0 (audit code and tests) and run it.
3. Switch to **Opus**: gate review.
4. Switch to **Sonnet**: Stage-1 estimators and tests, then the pilot.
5. Switch to **Opus**: pilot review and the confirmatory request.
6. Owner approval → **Sonnet**: freeze and run on the PC.
7. **Opus**: interpretation.
