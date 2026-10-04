# Experiment 2: protocol discussion and approved plan (Opus H7, 2026-10-04)

**Status:** approved by the owner on 2026-10-04 (plan approval). This document is the source specification for H8 (Sonnet implementation). The Experiment 2 config is **not** frozen, and no confirmatory evaluation is authorized until H9.

**Session and scope.**
- Opus 5.5 (`get_session`: configured and last served `claude-opus-5-5`), High effort, Plan Mode, read-only.
- The checkout is at `e17bc07` (= `origin/exp/transient-state-recoverability`); nothing has changed since H6.
- Evidence: saved envelopes and source only. No numerical run, edit or freeze.
- The two read-only tallies below (null-envelope flags, τ̂_F at start values) read saved JSON only.

## 0. Context
The owner and Codex propose Experiment 2, on individual tracking of the transient state F rather than population recovery. This addendum holds:
- my interpretation of Experiment 1;
- an assessment of the synthetic generator;
- my position on the proposed question and the information bound;
- a concrete protocol, a bounded numerical addendum for Experiment 1, the decisions the owner must take, and the handoffs.

Nothing below is authorized until the owner approves it.

## 1. What Experiment 1 supports
**Three levels of evidence.**
1. *Mathematical, under assumptions:* the analytic moment formulas (μ, D, C) are exact for the specified process. Local full rank holds at three parameter points. That is local identifiability at those points only, not a general proof.
2. *Finite-sample support for one estimator under chosen generating processes:* this is what Experiment 1 mainly supplies.
3. *Evidence that real learners follow the process:* none.

**Strongest defensible claim.**
- *Scope:* the specified probit model with a session-resetting OU component, under this 4-skill, interleaved, 8-template schedule, with known difficulties, using the equal-weight all-pairs composite likelihood.
- *Recovery:* the population variance σ²_F = 0.16 is recovered with Monte Carlo mean error inside ±0.04 at N = 300 and 1000. Mean estimates are 0.148 and 0.167, consistent with 0.16 − 0.0119 and 0.16 + 0.0072.
- *Detection:* the boundary-aware bootstrap test detects it in 20/20 tested datasets.
- *False positives:* there were no rejections in 40 null datasets, one family of which has misspecified, baseline-correlated gains.
- *Robustness:* under gain misspecification the estimate is about 13–15 % low.

**Not shown:**
- that the estimate is unbiased, or that any single dataset is accurate;
- a 5 % size (CP upper limit 0.17 per scenario);
- σ²_F = 0.04 detectability or τ_F intervals;
- gain-variance recovery;
- individual state recovery or causal next-answer forecasting;
- any psychological meaning of F.

**Verified figures and corrections** (sources: `summary.md`, saved envelopes, `kt_trial/evaluate.py:35-36`):
- **140 null-bootstrap certificate warnings, all on B2, none on B1.** 109 are `newton_decrement_large` and 31 `hessian_not_pd`. All 31 non-PD cases lie inside the D22 allowance (σ̂²_F < 0.02); they are recorded allowances, not violations.
  - 139/140 warned fits have σ̂²_F < 0.02 (max 0.024).
  - **117/140 have τ̂_F stalled within 0.2 % of a start-grid value** (0.5/2/8/30/120 min), against 31/2,347 among unwarned positive-σ̂²_F replicates.
  - By scenario: S1 18 (300: 6; 1000: 12), S2 62, S8 14, S8n 46.
  - The warnings mark a near-flat τ_F direction when σ̂²_F ≈ 0. That is a weak-identification symptom; whether the fits are also under-optimized is not established.
- **Units.** The "marginal Bernoulli" held-out score is a mean per response, so B2 − B1 ≤ 3e-5 is in **nats per response**. The final report's "per learner" label for it is wrong. The pairwise score is a sum over 6,216 pairs per learner.
- **Two statements in my report were imprecise:**
  - A zero-mean F does change marginal probabilities, through D_t. The fitted B1/B2 marginals nearly coincide because other variances compensate.
  - The Newton decrement is a local quadratic-model estimate, not a rigorous bound (that affects D30's wording only).

  Both go into an Experiment 1 errata addendum. The registered report stays unchanged.
- **The S8/S8n gain-variance truths (0.0081 and 0.0441)** were already corrected in D31.

**Direction-of-effect argument.** This argument reduces the stakes of the warnings:
- p = (1+#{CLR* ≥ CLR_obs})/(B+1). Under-optimizing a replicate's B2 fit can only *understate* its CLR*, while its B1 fit is unwarned and fixed. Better optimization can therefore only raise the p-values.
- So the S2/S8n non-rejections (PH3, PH4) cannot be overturned by these warnings.
- The S1/S8 rejections (PH2) would flip only if a warned replicate's CLR* (currently ≤ 6.3) rose above the observed CLR (≥ 408 in S1, ≥ 188 in S8). That needs a B2 improvement of at least about 90 log-lik units in a fit with σ̂²_F ≤ 0.024.
- The argument assumes the unwarned observed-data fits are correct. It shows which checks matter; it does not prove the warnings harmless.

## 2. Is the synthetic generator adequate for that claim?
**Already validated** (tests and audit):
- Analytic mean and covariance of Z against Monte Carlo on 400k learners. This also checks gains and mastery, because they enter V.
- The OU kernel and session reset, by an independent route: sequential simulation against the matrix formula.
- Stationary start variance, and that clean starts are uncorrelated while S6 starts correlate.
- Marginal P(Y=1) against Φ(μ/√D) for one template.
- Exposure rule: strictly earlier practice of the same skill; probes are not exposures.
- Kernel limits and finite-difference derivatives; BVN against scipy.
- Independent seed keys for `data` and `heldout`. Estimators receive only Y and `template_id` (`runner.py`: `pair_counts(ds.Y, ds.template_id)`); `latent` never reaches them.

**Gaps:**
1. **Shared kernel.** The simulator and the moments both call `moments.histories()`, so a wrong kernel would agree with itself.
2. **No pairwise-probability check.** Empirical P(Y_t=1, Y_t'=1) has never been compared with Φ2 from `latent_moments`.
3. **No S8 gain-moment test.** This is exactly where P4 slipped through.
4. **No test of `keep_latent` invariance.** By inspection, `keep_latent` only stores values and does not touch the RNG.
5. **Reproducibility hazard (new finding).** `Generator.multivariate_normal` defaults to `method='svd'`. The generating Σ_M = 0.8I + 0.1·11ᵀ has a **three-fold repeated eigenvalue (0.8)**, so its eigenvectors, and therefore the M0 draws, can depend on the LAPACK build. Bitwise regeneration of Experiment 1 datasets is guaranteed only in the run environment (the owner's Windows `.venv12`, numpy 2.5.3). It must be verified there, by fingerprint, before reuse.

**Smallest added validation** (after approval, about minutes of CPU):
- (a) A naive loop over raw schedule events that recomputes H^s and H^f without `expo`/`n_prior`, compared with `histories()`.
- (b) Empirical pair probabilities from 200k simulated learners against Φ2 for the four pair classes (same-skill short lag, cross-skill same session, cross-session, probe–probe), with MC SE.
- (c) S8 gain mean, variance and correlation against the analytic values.
- (d) `keep_latent` invariance of Y.
- (e) Dataset fingerprints. A regenerated dataset must reproduce the saved `data_meta.realised` values and the saved `ll` of the B0/B1/B2 fits evaluated at the saved θ̂ (relative tolerance 1e-9). Integer pair counts make a mismatch show up as an error of at least 1 log-lik unit, so it cannot pass as float noise. Held-out sets are checked the same way, through the saved mean held-out scores.

**Empirical support of the design choices.**
- σ²_F = 0.16, τ_F = 10 min, complete session reset, interleaving, independent Gaussian gains, known b and exogenous schedules are all **illustrative conveniences**.
- I know of no calibration of σ²_F or τ_F in this model family against real tutoring data.
- Known b and exogenous schedules are load-bearing for the *population* estimator: the template pair-count composite likelihood requires a schedule that does not depend on responses. Adaptive item selection breaks this, although history-conditioned (filtering) likelihoods remain valid under sequentially ignorable selection.

**Alternative processes that could imitate F.** S8n covers one: gain misspecification.
- (i) **Within-session learner-specific drift** (random slope or warm-up in session time). It is skill-general, resets each session and is smooth, so it is the closest imitator. Its covariance σ_s²·(T−T₀)(T'−T₀) is non-stationary, while OU is stationary.
- (ii) **Outcome-dependent context.** S7 inflated σ̂²_F to about 0.30.
- (iii) **Item misfit, or wrong b.** Fixed templates turn it into position-specific marginal misfit, which the near-white pathway (L6) absorbs.
- (iv) **Session-level learner intercepts.** These are an F with τ_F → ∞, not an imitator.

Priority after Experiment 2: (iii) together with unknown b, then (i).

## 3. Experiment 2 question: agree, with a sharper framing
I agree that individual tracking under the Experiment 1 process is the right next step, but the response-only *upper* side is already essentially known analytically: R² ≤ about 0.115 before an answer and about 0.146 after. An experiment that only "discovers" that tracking from answers is hard would waste effort. Three quantities are genuinely uncertain:
1. **The available information**, defined properly as the Bayes-optimal (MMSE) R², which a validated reference computes. The BCRB is only an analytic upper bound on it and may be loose, since it averages the probit information (Jensen).
2. **The decomposition of the gap:** bound − MMSE (looseness), then MMSE − ADF with known parameters (approximation), then ADF known − ADF fitted (population estimation).
3. **The causal forecasting value of transient information** and the risk of spurious tracking under nulls and misspecification. The held-out pairwise score could not measure either.

**Revised question.** Under the Experiment 1 process with known difficulties:
- What fraction of the transient state's variance is recoverable at prediction time, by an optimal and by a practical filter?
- How much causal next-answer log-loss does that information buy?
- Does a practical filter create spurious transient excursions or forecasting gains when F is absent?
- How do ideal pre-answer indicators of stated reliability change these answers?

**On order (unknown b next).** I agree to postpone it, for two reasons:
- Experiment 2 is cheap and mostly reuses data and fits.
- Its outcome decides whether individual tracking is worth pursuing, which shapes Experiment 3.

**What would change my mind:**
- If the owner intends to apply this to real data soon, unknown b plus item misfit becomes the bottleneck, since it threatens the population claim through L6. Experiment 3 should then come first.
- If the benchmark shows the reference cannot reach its accuracy gate, I would cut Experiment 2 to first-session prefixes.

## 4. The information bound: derivation and scope
**State and model.** x_t = (p, F_t), with static p = (M0 ∈ ℝ⁴, α, r):
- p ~ N(μ_p, Σ_p), with μ_p = (0, 0, 0, 0, ᾱ, r̄) and Σ_p = blockdiag(Σ_M, σ²_α, σ²_r);
- observation: Y_t = 1{h_tᵀx_t − b_t + ε_t > 0}, with h_t = (e_{k_t}, H^s_t, H^f_t, 1);
- dynamics: F_t = a_t F_{t−1} + η_t within a session, and F_t = η_t ~ N(0, σ²_F) at a session start.

**Handling the singular process covariance without inverting it.** Re-parameterize by the innovation vector ξ = (p, F at each session start, η's). Its Gaussian prior is nonsingular for σ²_F > 0, and x_t = L_t ξ is linear.
- Van Trees: E[(F̂_t − F_t)²] ≥ c_tᵀ J_ξ⁻¹ c_t, with J_ξ = Σ_ξ⁻¹ + Σ_s Ī_s L_sᵀ h_s h_sᵀ L_s.
- Ī_s = E[φ(ℓ_s)²/(Φ(ℓ_s)Φ(−ℓ_s))], with ℓ_s ~ N(μ_ℓ,s, h_sᵀ Σ_x h_s) the **prior marginal**, not a filter approximation. It is computed by Gauss–Hermite quadrature.
- Because the dynamics are linear-Gaussian and each observation contributes rank-one information, this inverse equals the covariance of a Kalman filter for the *surrogate* measurement ℓ_t + noise with variance 1/Ī_t. In covariance form:
  - predict: P⁻ = A P⁺ Aᵀ + Q (Q is zero on p; at a reset the F row and column are zeroed and Q_FF = σ²_F);
  - update: P⁺ = P⁻ − P⁻hhᵀP⁻ / (hᵀP⁻h + 1/Ī_t).

  No Q⁻¹ appears. Static coordinates and resets are exact, so this sidesteps the singular-transition issue Tichavský et al. treat.
- The pre-answer bound is P⁻_FF and the post-answer bound is P⁺_FF. An ideal indicator adds an exact linear update with variance R_ν before Y_t.
- The bound is averaged as 1 − mean(bound)/σ²_F over the evaluated positions (all 112, the 96 practice positions, or a session-position bin), always matching the endpoint.

**Scope.**
- The bound is valid for every estimator, but only under S1 with known population parameters and a Gaussian prior.
- In S8/S8n the prior is lognormal, so its prior information differs and the Gaussian computation is not that scenario's bound. In S2 it is degenerate.
- It says nothing about attainment, fitted parameters or other processes.
- Codex's reproduced values (0.1151/0.1464 over all 112 positions, 0.1135/0.1436 over practice; indicators 0.5534/0.5635 and 0.7531/0.7564) are plausible. Experiment 2 re-derives them with a second, independent implementation: a direct J_ξ inversion on short prefixes.

**The "0.002 nats" ceiling.**
- A second-order expansion gives a log-loss gain ≈ ½·Ī·Var(E[ℓ_t | history] from F)/s², which is about 0.5 × 0.3 × (0.12 × 0.16) ≈ 3e-3 nats per response. So the order of magnitude is plausible, but it is an approximation and **not a bound**.
- Experiment 2 replaces it with a measured ceiling: the **oracle-F forecast**, a B2 filter told the true current F_t. Its gain over the B2 filter is the forecasting value of perfect transient information under the same approximation.

## 5. Proposed Experiment 2 specification (ADEMP, Morris et al. 2019)
**Aims.** E1 state information and gap decomposition; E2 causal forecasting value; E3 null safety; E4 persistent-state recovery (secondary).

**Data-generating mechanisms.** No new response data are generated. The protocol reuses the Experiment 1 datasets, regenerated from the recorded seeds, verified by fingerprint and with `keep_latent=True`:

| scenario | role | arms |
|---|---|---|
| S1 | F present (core) | all arms |
| S2 | clean null (core) | fitted-parameter arms only; the known-parameter B2 equals B1 and serves only as an implementation check |
| S8n | misspecified null (core) | fitted-parameter arms |
| S8 | misspecified, F present | fitted-parameter ADF arms only; **descriptive** (cheap; tests whether the −14 % attenuation degrades tracking); no reference, no decision rule |

- Evaluation learners are the **held-out** learners of every dataset: 20 reps × 300 per cell. Fits come from disjoint training learners.
- Indicator noise uses a new namespace: `rng_for(seed_exp2, "indicator", sid, N, rep, ρ)`, so response data are untouched.

**Estimands.** All are per response position, averaged first within a learner and then over learners. Positions are summarized in practice-session bins (first answer, 1–4, 5–15, 16–31) and the delayed probes are reported separately. The primary summary is the 96 practice positions.
- E1: R²_F = 1 − MSE(F̂_t)/σ²_F before and after each answer; bound, reference (MMSE), ADF-known and ADF-fitted, plus the three gaps.
- E2: paired causal log-loss differences in nats per response:
  - B2-full against B2-priorF (tracking withheld; defined below);
  - B2-full against B1-fitted (the practical comparison);
  - oracle-F against B2-full (the ceiling);
  - indicator arms against the response-only filter;
  - B2-F0 as a factor-removal diagnostic.
- E3, nulls: excursion energy E[m_F,t²] in absolute units, its persistence (lag-1 autocorrelation of m_F,t, and the mean run length of |m_F,t| > 0.2, i.e. half the declared S1 scale σ_ref = 0.4), and spurious forecasting gains.
- E4: RMSE of the posterior means of M0, α and r at the end of practice; probe log-loss; 90 % interval coverage and width for F and M0.

**Methods.** Every predictive probability is causal: it uses Y_<t and the schedule, plus indicators up to t where the arm has them.
- **B2-known:** ADF with the generating population θ.
- **B2-fitted:** ADF with each replicate's frozen B2 θ̂. All 20 replicates per cell are used, with no selection. S8n N=1000 rep 13 is included as is, with a prespecified sensitivity analysis: results without it, and with the addendum's improved fit if one is found.
- **B1-fitted:** its own frozen θ̂ and its own 6-dim ADF.
- **B2-priorF (tracking withheld, my proposal).** Run the full B2 filter. At prediction time only, replace F's posterior by its prior N(0, σ²_F), independent of the persistent marginal (m_P, P_PP):
  p = Φ((h_Pᵀm_P − b)/√(1 + h_PᵀP_PPh_P + σ²_F)).
  - This preserves the variance contribution and correct persistent inference, and withholds exactly the current-state information.
  - Limitation: the predictive does not belong to any coherent information set, and the persistent marginal was itself shaped by tracking.
  - At a session start it equals B2-full.
- **B2-white** (F i.i.d. per response, same σ²_F): a secondary diagnostic. It over-trusts persistent updates because correlated errors are treated as independent.
- **B2-F0:** removes the factor, which changes D_t as well, so it is not a test of tracking.
- **Oracle-F:** the persistent ADF given the true F path up to t. This is the ρ = 1 indicator limit.
- **Indicator arms**, S1 only, ρ ∈ {0.3, 0.6}:
  - O_t = F_t + ν_t with R_ν = σ²_F(1−ρ)/ρ (0.373 and 0.107), known, and observed **before** answer t.
  - Arms: indicator-only (exact Kalman filter on F) and indicator plus answers. The incremental R² and log-loss of the answers are reported.
  - I recommend **not** running indicator arms in S2/S8n: reliability is undefined there, and what a real instrument measures when F is absent is a separate measurement-model question.
- **Timing per step:** propagate or reset; take the indicator, if available; predict p_t; observe Y_t; update. The pre-answer estimate is taken before Y_t and the post-answer estimate after it. No smoothing, no future data, no latent truth in any prediction.
- **ADF numerics:**
  - the analytic probit update with κ = 2y − 1, computing λ = exp(log φ(u) − log Φ(u)) via `scipy.special.log_ndtr`;
  - covariance symmetrized after each step, with λ(λ+u) ∈ (0, 1) guaranteeing P⁺ ⪰ 0;
  - OU propagation of Var(F) and Cov(F, p); at a reset the F mean is set to 0, its variance to σ²_F and its cross-covariances to 0, and the persistent block is kept. The probe session is treated the same way.

**Reference (my proposal, replacing prefix-only GHK).** A **Rao–Blackwellized, fully adapted SMC over latent utilities**, which is GHK with resampling.
- Each particle samples Z_t from its Kalman predictive N(hᵀm − b, hᵀPh + 1), truncated to the sign of y_t. The incremental weight is that particle's predictive probability, so the proposal is optimal.
- Given Z, x is linear-Gaussian. **The covariance P_t is identical across particles** and only the means differ, so the method is cheap.
- E[F_t | y_≤t] and P(y_t = 1 | y_<t) are weighted averages of exact conditional quantities (Rao–Blackwell). Resampling happens when ESS < N_p/2.
- It covers complete histories, including post-reset and probe prefixes, with no need to treat a persistent posterior as a fresh prior. The same code with σ²_F = 0 gives a B1 reference.

**Reference validation.**
- 10 independent seeds, giving MC SEs of the state means and predictive probabilities.
- ESS traces.
- N_p doubling stability (4k → 16k).
- Exact orthant checks for prefixes of t ≤ 3 against `scipy.stats.multivariate_normal.cdf` (an independent algorithm).
- The reference R² must not exceed the bound beyond its MC error.
- Validation subset: S1 N=1000 held-out learners, reps 0–9, **2 learners per template per rep** (the first by index), giving 160 learners and balanced template coverage with full sequences.
- Production: all 6,000 S1 N=1000 held-out learners at the validated N_p. If the budget benchmark fails, fall back to the subset.
- A failed gate is preserved and reported. No decomposition claim is made for that subset.

**Uncertainty.**
- Known-parameter arms: learners are the unit (clustered by learner, since the 112 responses within a learner are dependent). Replications differ only in held-out data and are pooled.
- Fitted arms: the **replication** is the unit (n = 20 per cell; the mean of per-rep means with a t-interval). The within-rep learner SE is reported separately, because more responses do not mean more training replications.
- Every comparison is paired on the same learners and prefixes.

**Expected failure modes.**
- The ADF can be overconfident in the persistent block after many answers. This would show as interval under-coverage and a drift of the ADF away from the reference in later sessions.
- Spurious excursions can arise in the fits with σ̂²_F > 0 under the null (about half of S2).
- B2-priorF can beat B2-full when the fitted σ̂²_F or τ̂_F is wrong (negative tracking value).
- The reference can lose ESS at long prefixes with extreme ℓ.
- Regeneration can mismatch outside the run environment.

## 6. Positions on the three comparison questions
- **Indicator-only baseline: required.**
  - By construction the ideal indicator dominates: indicator-only reaches R² of about 0.54 and 0.75, so answers add only about 0.01–0.02.
  - These arms are positive controls of a direct measurement of F. They carry no evidence about any real instrument.
  - Their decision-relevant output is the **forecasting value of an ideal measurement of given reliability**, which bounds what any later context-measurement effort could buy.
- **Factor removal versus tracking.** B2-F0 confounds variance with tracking. B2-priorF is the primary tracking contrast, with B2-white secondary, each with its stated limitation.
- **Known difficulty.** Experiment 2's conclusions are conditional on known b. With N ≥ 300, unknown b is mostly a population-estimation error for filtering; its main threat is to the population identification of a near-white F (L6). That makes it Experiment 3's core question, not Experiment 2's.

## 7. Numerical addendum for Experiment 1 (separate document; preserves all registered outputs)
**Selection.** Deterministic, sorted by job id, deduplicated; 53 datasets.
- **Tier A** (the only datasets that bear on a registered verdict, by §1's argument): all **32 warned S1/S8 replicates** (S1: 18, S8: 14).
- **Tier B** (characterization):
  - the 5 highest-CLR warned S2/S8n replicates;
  - 5 non-PD S2/S8n replicates, stratified by cell (first by job id, excluding those already chosen);
  - 5 unwarned near-null controls with 0 < σ̂²_F ≤ 0.02, matched by cell;
  - 5 unwarned controls with the largest σ̂²_F.
- **Tier C:** the main fit S8n N=1000 rep 13.

**Per dataset:**
1. Regenerate it from the fitted B1 θ̂ and the seed keys `(sid, N, rep, "null", b)`, then refit B1 and B2 with the registered code and check reproduction of CLR, σ̂²_F and τ̂_F (relative ll 1e-9). Any failure is reported as a provenance finding.
2. Compute projected-gradient and KKT checks with active bounds.
3. Compute Hessian eigenpairs at finite-difference steps of 1e-4, 1e-5 and 1e-6.
4. Profile τ_F over 11 log-spaced values in [0.05, 1000], re-optimizing everything else from 2 starts (warm and jittered).
5. Report the attained improvement, the recomputed CLR* and the effect on each affected p-value. This is the attained gain, not an upper bound.

**Cost and venue.** About 3–4.5 CPU-h; 2 datasets are benchmarked first. It runs on the owner's PC (regeneration requires it).

**Output.** `docs/experiment_01_addendum_numerical.md` plus the errata (§1). No registered result is replaced.

## 8. Decisions for the owner
| # | Decision | My recommendation | Why it matters |
|---|---|---|---|
| 1 | Experiment 2 question | the §3 framing: MMSE-defined information, gap decomposition, causal forecasting value, null safety | it avoids re-deriving a known ceiling and gives a quantity that decides the next step |
| 2 | Scenarios | S1, S2, S8n core; S8 ADF-only, descriptive | S8 costs nothing and checks whether the attenuation harms tracking |
| 3 | Tracking contrast | B2-priorF primary; B2-white and B2-F0 as diagnostics | B2-F0 alone confounds variance and tracking |
| 4 | Indicators | S1 only, ρ ∈ {0.3, 0.6} plus oracle-F (ρ = 1); not in the nulls | reliability is undefined under the null |
| 5 | Reference | RB-SMC: validation subset of 160 learners, production on 6,000 S1 N=1000 held-out learners | gives "available information" exactly, up to MC error |
| 6 | Prespecified rules | **R1** reference gate (below); **R2** ADF-approximation statement; **R3** null safety (below); everything else continuous and descriptive | see below |
| 7 | Exp-1 numerical addendum | 53 datasets, about 3–4.5 CPU-h, run alongside Experiment 2 | Tier A settles the only verdict-relevant question |
| 8 | Compute and venue | cap of **12 CPU-h** in total (Experiment 2 about 1–3 CPU-h plus the addendum), benchmarks first; owner's PC | bitwise regeneration requires the run environment |
| 9 | Code placement | a new package `kt_exp2/`; `kt_trial/` is untouched, imported only | `code_hash()` hashes `kt_trial/*.py`, so new files there would break Experiment 1's provenance check |
| 10 | Order after Experiment 2 | Experiment 3 = unknown b with item misfit; then within-session drift | the main threats to the population claim |

**R1 (reference gate).** The reference passes if, on the validation subset:
- the MC SE of R²_ref is ≤ 0.002;
- the MC SE of predictive probabilities is ≤ 0.001 (RMS);
- N_p doubling changes R² by ≤ 2 SE;
- all t ≤ 3 orthant checks are within 3 MC SE.

**R2 (ADF approximation).** The approximation is "negligible for forecasting" if the mean |p_ADF − p_ref| ≤ 0.005 and the paired log-loss difference's CI lies within ±5e-4 nats per response.
- Consequence of the threshold: a probability error of 0.005 costs about 5e-5 nats, under 5 % of the expected tracking gain (about 1e-3), so it cannot mask the effect being measured.
- State approximation is reported as ΔR² = R²_ref − R²_ADF with its CI.
- **I advise against the proposed "efficiency ≥ 0.9" rule.** With R² of about 0.12, the MSE ratio MSE_ref/MSE_ADF stays above 0.9 even when the ADF captures only a quarter of the available information. If a ratio is wanted, use R²_ADF/R²_ref, and only when R²_ref ≥ 10 × its SE.

**R3 (null safety).** In S2 and S8n separately: "spurious tracking gain" if the replication-level CI of the log-loss gain of B2-full over B2-priorF is entirely above 0 (PH6 style). Excursion energy is reported in absolute units. **I advise against the "10 % of S1" ratio**: S1's own excursion energy is only about R²·σ²_F ≈ 0.02, so the ratio is noisy and arbitrary.

**What needs the owner's substantive judgment:** whether any achieved R² or log-loss gain is *educationally* useful. I recommend reporting both continuously, with no "useful" cutoff.

**What I or Sonnet handle within scope:** module layout, tests, job ids and checkpoints, file formats, batching, numerics, and the selection code that implements the stated rules.

## 9. Handoffs and provisional implementation plan
- **H8 → Sonnet 5.5 (Medium; High for the ADF, SMC and bound).** Manual switch by the owner.
  1. Write `docs/experiment_02_plan.md`, `experiment_02_decisions.md` and `experiment_02_handoff.md` from this addendum.
  2. Build `kt_exp2/`:
     - `regenerate.py` (regeneration plus fingerprints, using `kt_trial.simulator.simulate` and `kt_trial.composite_likelihood`);
     - `adf.py` (B2, B1, priorF, white, F0, oracle-F and indicator filters);
     - `reference.py` (RB-SMC);
     - `bound.py` (covariance-form BCRB plus a direct J_ξ inversion as a cross-check);
     - `addendum.py` (§7);
     - `runner.py` (deterministic job ids, atomic writes, resume, dry-run, LF-normalized code hash of `kt_trial` and `kt_exp2`, environment manifest);
     - `summarize.py`.
  3. Write focused tests:
     - the one-step probit moments against 2-D quadrature;
     - the indicator update against the closed form;
     - the reset and cross-covariance handling;
     - causality (perturbing future y or O leaves earlier predictions unchanged);
     - B2(σ²_F = 0) ≡ B1;
     - `keep_latent` invariance;
     - the §2 generator checks (a)–(d);
     - SMC against orthant probabilities for t ≤ 3;
     - the bound against the direct inversion, and against Codex's figures within the quadrature tolerance.
  4. Run a bounded pilot (pre-approved by this plan, ≤ 0.5 CPU-h): fingerprints on 4 datasets, R1 on 20 learners, benchmarks. Stop.
- **H9 → Opus.** Review scientific correctness and the pilot, freeze `configs/experiment_02/*.yaml` (sha256), and request run approval.
- **H10 → Sonnet, owner's PC.** Run the addendum and Experiment 2. They are resumable, and progress is printed by the runner, not by agent heartbeats.
- **H11 → Opus.** Interpret the results.

**Setup on the owner's PC (after approval).**
- `git pull`
- activate `.venv12`
- `python -m pip freeze > results/experiment_02/env_freeze.txt`
- `python -m pytest -q`

No new dependencies (NumPy and SciPy only).
