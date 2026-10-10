# Experiment 5 protocol: outcome-driven dynamics versus a transient state

Opus 5.5, 2026-10-10; approved by the owner, who chose this question. Decision log: `docs/experiment_05_decisions.md` (prefix X5). Handoffs:
`docs/experiment_05_handoff.md`. Branch `exp/outcome-driven-dynamics`, package `state_dependence/`.

> **Scope.** Statistical results for the simulated Experiment-1 process only. F is a covariance component of that simulation. The feedback studied here is
> "outcome-driven dynamics" (state dependence), a statistical mechanism. Neither is fatigue, stress, mood, attention, emotion or any psychological
> construct. No real learners are used.

## 0. Why this experiment
Experiments 1–4 established that the transient component F can be recovered when item parameters are unknown. Experiment 4 recommends 2PL, with free difficulties and discriminations.

The remaining main threat sits on the **process** side, in Experiment 1's limitation L7:
- In Experiment 1's scenario S7, a practice error shifts the latent propensity by −0.25, and the shift decays like F.
- There, σ̂²_F rose from 0.16 to about 0.30 and τ̂_F was biased by about +82 min (3 replications, descriptive).

This is the classic distinction between **true state dependence**, where past outcomes change later responses, and **spurious state dependence**, which is serially correlated heterogeneity (here F). A detected F is read as an exogenous transient state. If outcome-driven dynamics produce the same detection, that reading fails.

**Goals:**
1. Measure how the recommended 2PL pipeline (estimate and bootstrap null test) responds to outcome-driven dynamics, with and without F.
2. Build and validate a **diagnostic** that detects such dynamics from the same data.

The scope is **diagnosis, not correction.** Estimating a joint feedback model is a later experiment: its pairwise marginals are not available in closed form, so it would need simulated or indirect inference.

## 1. Theory before simulation
### 1.1 Data-generating process
Z_t = −b_q + λ_q (M0_k + α H^s_t + r H^f_t + F_t + D_t) + ε_t, ε_t ~ N(0, 1), where

D_t = κ · Σ_{s < t, same session, s a practice attempt} 1{Y_s = 0} · exp(−(time_t − time_s)/τ_D).

- **Reset:** D resets at each session start, like F.
- **Which errors count:** only errors on practice attempts feed back, as in S7. The probe session has no feedback.
- **Sign:** κ < 0 means an error lowers the following answers.
- **Relation to S7:** with τ_D = τ_F, F + D is S7's process, because kt_trial adds the jump to F before the OU decay.

Everything else is the Experiment-1 generator (design.yaml; 8 templates; 48 items; λ ≡ 1 in all Experiment-5 data).

### 1.2 Identifying contrast: an exclusion restriction supplied by the randomised schedule
- **Assignment is random.** Learners are assigned to the 8 fixed templates at random, independently of M0, the gains and F.
- **The same item has different predecessors.** It appears in different templates after different preceding items.
- **Under F alone,** the success rate of an item at an occurrence depends on:
  - its difficulty (and discrimination);
  - the skill history (H^s, H^f);
  - the timing.

  It does **not** depend on how hard the preceding items were.
- **Under outcome feedback,** harder preceding items cause more errors, hence more recent errors, hence lower success.

The difficulty of the preceding items therefore acts as an instrument for past outcomes. The F model, at any parameter value, has no term that can produce this template-specific pattern in the marginal success rates.

There is also a pair-level signature: feedback makes the dependence of later answers on an earlier one depend on the earlier item's difficulty, and makes it time-asymmetric. This is noted but not used. The diagnostic below uses only the marginal signature.

### 1.3 Diagnostic: composite-likelihood score test for a carry-over term
1. **Augmented mean.** Add η·x_{g,t} inside the λ bracket: μ_t = −b_q + λ_q(μ0_t + η x_{g,t}).
2. **Covariate:** the *within-item-centred recent error load*:
   - L_{g,t} = Σ_{s < t, same session, practice} exp(−(time_t − time_s)/τ_x) · (1 − p̂_{q(s)}), where p̂_q is the observed overall success rate of item q (pooled over templates; model-free);
   - x_{g,t} = L_{g,t} minus the mean of L over all occurrences of item q(t);
   - probes get x = 0.
3. **Test.** H0: η = 0, using the generalized score statistic with a Godambe-adjusted variance, evaluated at the fitted 2PL B2 model:

   S = U_η² / V_η, where:
   - U_η = Σ_i u_{iη};
   - V_η = J_ηη − 2 H_ηθ H_θθ⁻¹ J_θη + H_ηθ H_θθ⁻¹ J_θθ H_θθ⁻¹ H_θη;
   - J is the empirical learner-score covariance;
   - H is the expected sensitivity matrix;
   - only active coordinates are used, with boundary nuisances held fixed as in `kt_trial.inference.sandwich`.

   The reference is χ²₁, two-sided, at α = 0.05. η̂ = −U_η / H_ηη|θ is reported as a descriptive one-step estimate.
4. **Existing parts:**
   - `discrimination_free.twopl.learner_scores` already forms each learner's derivatives with respect to the standardised means a_t (`wobs`), so u_{iη} = Σ_t wobs_{it} · λ_q x_t / √D_t;
   - `twopl.fisher` gives H once a column ∂a_t/∂η = λ_q x_t/√D_t (with ∂ρ/∂η = 0) is appended;
   - no extra fits are needed.
5. **Generated regressor.** Using p̂ inside x does not change the null distribution to first order: the score has mean zero under H0, so the cross term is O_p(1) against U's O_p(√N) scale.

**Limitations, stated in advance:**
- **(i)** The diagnostic detects *carry-over from preceding items*, whether driven by outcomes or by the items themselves. Both contradict the exogenous-F reading, but this test cannot tell them apart.
- **(ii)** It is valid only when the rest of the fitted model is correct. Cell E6 checks robustness to gain misspecification (S8n).
- **(iii)** With 8 templates, the within-item variation of x is limited. Stage 0 measures whether the design gives the power required.

## 2. Hypotheses (provisional; the rules are frozen after the pilot review)
| | claim | cells | provisional rule |
|---|---|---|---|
| **H5a** misattribution | with no F but outcome feedback, the 2PL test still "detects F" | E3, E4 | share of T = 2(ℓ_B2 − ℓ_B1) above the same-N null q95 (X5-D03), with a CP 95 % CI; pseudo-true σ²_F\* and τ̂_F reported |
| **H5b** diagnostic power | the diagnostic detects feedback | E3, E4, E5 | rejection share with CP CI; at κ = −0.25 and N = 1000, supported if the point estimate is ≥ 0.8 and the CP lower bound is > 0.5 |
| **H5c** diagnostic level | the diagnostic holds 5 % without feedback | E1 + E2 pooled over N (primary); per cell and N (secondary) | rejection share with CP CI: "consistent with 5 %" if the CI contains 0.05 and its upper limit is ≤ 0.10; "liberal" if the lower limit is > 0.05; otherwise inconclusive |
| **H5d** specificity under non-feedback misfit | the diagnostic does not fire under gain misspecification | E6 | same rule as H5c, reported separately |
| **H5e** bias with both | σ̂²_F\* is inflated when F and feedback coexist | E5 | bias against σ²_F\* with MC CI (descriptive; S7 found +0.145) |

**Gates (as in Experiment 4):**
- G1: more than 5 % failed or non-converged B2 fits per cell and N makes that cell not evaluable. Ridge-converged fits (X4-D09) count as converged.
- G2: a single code hash and the frozen sha.
- G3: single-thread BLAS.

**Descriptives:**
- distributions of τ̂_F and η̂;
- ridge shares;
- the diagnostic's p-value histogram under E1/E2;
- per cell, the 2 × 2 table of F-test decision × diagnostic decision;
- polish statistics.

## 3. Cells (provisional; Stage 0 fixes the amplitudes and τ_x)
λ ≡ 1 in all data, so the 2PL estimator is correctly specified when there is no feedback.

| cell | F (σ²_F, τ_F) | feedback (κ, τ_D) | purpose |
|---|---|---|---|
| E1 | 0.16, 10 | none | diagnostic level (F present); F recovery reference |
| E2 | absent | none | diagnostic level (null) |
| E3 | absent | −0.25, 10 (S7 amplitude, no F) | H5a, H5b |
| E4 | absent | the hardest Stage-0 grid point that the F test still flags (e.g. κ −0.10 or τ_D 2) | H5a, H5b |
| E5 | 0.16, 10 | −0.25, 10 (= S7) | H5b, H5e |
| E6 | absent | none; lognormal gains (S8n) | H5d |

**Sizes and cost:**
- N ∈ {300, 1000}; master seed 20265101.
- Provisional sizes:
  - E1 and E2: 75–100 datasets per N each, giving a pooled level CI of about ±0.025;
  - E3–E5: 30 per N;
  - E6: 50 per N.
- About 650 s per dataset (2PL B1 + B2 fits plus scores) × 1.4 load factor (X4-D11), giving roughly 120–170 CPU-h.
- The owner sets the cap after the pilot.

## 4. Stages
### Stage 0: implementation checks and population audit (Sonnet builds, Opus reviews; no confirmatory data)
1. **Package `state_dependence/`.** It imports `discrimination_free`, `difficulty_free` and `kt_trial` and modifies none of them.
   - **`simulator.py`:** `simulate_feedback(cfg, N, seed_keys, master_seed, templates=None, lam=None, ids=None, theta=None, feedback=None, keep_latent=False)`.
     - feedback = {kappa, tau_D};
     - D inside the λ bracket, practice errors only, reset at session start;
     - consumes the RNG stream exactly like `difficulty_free.simulator.simulate_lambda`;
     - supports S8n gains through `kt_trial.simulator._gains`.
   - **`diagnostic.py`:** the covariate x (with τ_x as a parameter), the learner scores u_η, and the generalized score statistic and p-value from a fitted 2PL B2 result.
   - **`audit.py`:** the population analysis (item 3).
2. **Tests (gate G0-1):**
   - **No-feedback equivalence:** with κ = 0, `simulate_feedback` reproduces `simulate_lambda` bit for bit.
   - **S7 equivalence:** with τ_D = τ_F and λ ≡ 1 it reproduces `kt_trial.simulate` under S7. Responses must be identical on a fixed-seed check with N = 20,000, and the latent F + D must be within 1e-12 of kt_trial's F. The summation order differs, so bitwise equality of the latent is not required.
   - **Score correctness:** u_η summed over learners equals the finite-difference derivative of the composite log-lik with the latent mean shifted by ε·λ·x. The η column of H matches a finite-difference check.
   - **Invariances:** S is invariant to rescaling x; with x ≡ 0 the statistic is undefined and is refused cleanly.
   - **Full suite:** the full pytest suite passes; X3-F06 is the known failure.
3. **Population audit (gates G0-2, G0-3).** Composite-likelihood fits depend on the data only through pair counts, so pseudo-true values come from 2PL fits to N_big = 200,000 simulated learners, at a cost that does not depend on N.
   - **Grid:** F ∈ {absent, present} × κ ∈ {0, −0.10, −0.25} × τ_D ∈ {2, 10}, plus S8n (F absent, no feedback).
   - **Per point:** the pseudo-true σ²_F\*, τ_F, b and λ; T/N, giving expected T at N = 300 and 1000; and, for τ_x ∈ {2, 5, 10}, the diagnostic's per-learner noncentrality δ, giving predicted power 1 − Φ(1.96 − δ√N) + Φ(−1.96 − δ√N).
   - **G0-2:** τ_x is fixed a priori as the value that maximises the minimum predicted power across the κ = −0.25 points. No pilot data are used.
   - **G0-3 (gate):**
     - predicted power ≥ 0.8 at N = 1000 for κ = −0.25, τ_D = 10;
     - |score mean| about 0 at the κ = 0 points;
     - the predicted false-alarm rate under S8n is reported.

     If the gate fails, escalate to Opus. Options are more templates (a design change needing the owner's approval) or a multi-df covariate.
   - **Expected E[T]:** if Stage 0 predicts E[T] < 3 × q95 (X5-D03) in a feedback cell, warp bootstrap replicates are added for that cell.
   - **Cost:** a few CPU-h.
   - **Output:** `docs/experiment_05_stage0_report.md` (numbers only) and `results/experiment_05/stage0/`.

**Opus Stage-0 review:** choose E4, finalise the cells, and confirm or replace the H5 rules.

### Stage 1: pilot (Sonnet)
- The cell matrix at 3 replications per cell and N, about 10 CPU-h, outside the cap.
- **Checks:**
  - timings;
  - convergence and polish counts;
  - the G1 gate;
  - the diagnostic's runtime;
  - the full per-dataset output: σ̂²_F\*, τ̂_F, T, η̂, S and p.
- **Infrastructure:** a runner, CLI and summarize with rules, modelled on `discrimination_free.runner` (enforced CPU cap, frozen gate, rep-major order).

### Then
1. **Opus pilot review:** final sizes, the cap (the owner's call, using the ×1.4 load factor) and the frozen rules.
2. **Sonnet freeze:** the confirmatory config, with its sha256 and code hash.
3. **Owner:** gives the go-ahead and runs it on an idle machine.
4. **Sonnet:** audits and summarises the run.
5. **Opus:** interprets the results.

## 5. Venue and reproducibility
- `.venv12`, with single-thread BLAS set before Python starts (X2-F15).
- The owner's PC, an idle machine, 18 workers.
- The owner runs all git.
- `kt_trial`, `difficulty_free`, `discrimination_free` and every registered result stay unchanged.
