# Experiment 6 protocol: recovering and testing F when outcome feedback is modelled

Opus 5.5, 2026-10-11; approved by the owner, who chose this question ("Adjust for feedback"). Decision log: `docs/experiment_06_decisions.md`
(prefix X6). Handoffs: `docs/experiment_06_handoff.md`. Branch `exp/feedback-adjusted-F`, package `feedback_model/`.

> **Scope.** Statistical results for the simulated Experiment-1 process only. F is a covariance component of that simulation. The outcome feedback is a
> statistical mechanism (state dependence). Neither is fatigue, stress, mood, attention, emotion or any psychological construct. No real learners are used.

## 0. Why this experiment
Experiment 5 (X5-D09) found that the 2PL F test detects within-session dependence of any origin:
- feedback without F is declared "F" in 30/30 datasets at S7 strength, and in 98 % at N = 1000 for weak, short feedback (H5a);
- with F and feedback together, σ̂²_F\* is inflated by +0.24 (H5e);
- the carry-over score diagnostic flags strong feedback (H5b), but it only diagnoses.

Experiment 6 asks whether a fitted model that **contains** feedback:
1. recovers σ²_F\* when F and feedback coexist;
2. stops declaring F when only feedback is present;
3. keeps the F test calibrated and powerful when there is no feedback.

The Experiment-5 protocol (§0) noted that a joint feedback model has no closed-form pairwise marginals. This protocol proposes an **analytic
approximation** (L0, §1.3). Stage 0 measures the approximation's error at population level before any finite-sample work. Simulated or indirect
inference stays the fallback after L1 (§1.4).

## 1. Theory
### 1.1 Data-generating process (unchanged from Experiment 5)
Z_t = −b_q + λ_q (M0_k + α H^s_t + r H^f_t + F_t + D_t) + ε_t, ε_t ~ N(0, 1), with
D_t = κ Σ_{s < t, same session, practice s} 1{Y_s = 0} w_st and w_st = exp(−(time_t − time_s)/τ_D).
- D resets at the start of each session.
- Only errors on practice attempts count.
- The code is `state_dependence.simulator.simulate_feedback`.
- The data have λ ≡ 1, 8 templates assigned at random, and 48 items.

### 1.2 Why a schedule term alone is not enough (prediction)
The Experiment-5 covariate x (`state_dependence/diagnostic.py`) is **schedule-based**: it is built from item-level expected error rates (1 − p̂), not from
each learner's own errors. Adding η·x to the fitted mean ("B2+η") can therefore remove only the **marginal-mean** footprint of feedback, that is, the
template-specific success rates.

Feedback also creates **within-session covariance**: an error at s lowers the success probability at t, so errors cluster within a session. This
positive within-session dependence is what F absorbs. **Prediction:** under B2+η, σ²_F\* stays well above 0 in E3 and above 0.16 in E5. Gate G0-2 tests this
prediction cheaply.

### 1.3 The feedback-aware pairwise model, approximation L0
The fitted models are B2-FB and B1-FB: the 2PL models B2 and B1 (free b and λ, as in Experiments 4 and 5) plus two coordinates, κ ∈ [−1, 1] and
τ_D ∈ [0.5, 50]. Write E_r = 1{Y_r = 0}. The latent moments of the 2PL model, μ_t, V_tt and V_st, are those of `discrimination_free.twopl.core`
before standardisation.

**(a) Mean-field moments.** Run a forward recursion over the positions of each template:
- e_r = 1 − Φ(a_r), with a_r the standardised mean of r from the already-updated moments;
- m_t = κ Σ_{r<t} w_rt e_r;
- v_t = κ² Σ_{r<t} w_rt² e_r(1 − e_r);
- c_st = κ² Σ_{r<s} w_rs w_rt e_r(1 − e_r) for s < t.

Then set:
- μ̃_t = μ_t + λ_t m_t;
- Ṽ_tt = V_tt + λ_t² v_t;
- Ṽ_st = V_st + λ_s λ_t c_st.

Here w_rt = 0 unless r < t, r is practice, and r and t are in the same session.

**(b) Pair (s, t), s < t, direct effect exact.** Conditional on Y_s, the outcome at t is shifted by its own direct term, and its share of the variance
v_t is removed:
- μ_t⁽ʸ⁾ = μ̃_t + λ_t κ w_st (1{y = 0} − e_s);
- Ṽ_tt|s = Ṽ_tt − λ_t² κ² w_st² e_s(1 − e_s);
- a_t⁽ʸ⁾ = μ_t⁽ʸ⁾ / √Ṽ_tt|s;
- ρ_st = Ṽ_st / √(Ṽ_ss Ṽ_tt|s), the same for both values of y;
- a_s = μ̃_s / √Ṽ_ss.

**(c) Cell probabilities** (cell order 11, 10, 01, 00 as in `kt_trial.bvn`):
- P11 = Φ2(a_s, a_t⁽¹⁾; ρ_st);
- P10 = Φ(a_s) − P11;
- P01 = Φ(a_t⁽⁰⁾) − Φ2(a_s, a_t⁽⁰⁾; ρ_st);
- P00 = 1 − Φ(a_s) − P01.

The cells sum to 1. When w_st = 0 (s is a probe, or s and t are in different sessions), a_t⁽¹⁾ = a_t⁽⁰⁾ and the formula reduces to the bivariate
probit with the mean-field moments.

**(d) Properties.**
- At κ = 0 the model equals the 2PL objective exactly.
- The objective uses only the pair counts, so population pseudo-true values can again be computed from N_big = 200,000.

**What L0 ignores:**
- indirect paths s → r → t;
- the correlation between earlier errors and F (and the other latent terms);
- the non-Gaussian shape of the remainder of D.

Each is second order in κ, or in κ·σ_F. Gate G0-3 judges whether the resulting bias matters.

**Known nuisance.** At κ = 0, τ_D is not identified (cells E1 and E2). This is handled with multiple starts and reported. It does not enter the F
estimand.

### 1.4 Fallback L1 (built only after an Opus review, if G0-3 fails)
**Probit linearisation of earlier errors:** E_r ≈ e_r − φ(a_r)(Z_r − μ̃_r)/√Ṽ_rr + u_r, with u_r independent and with variance
e_r(1 − e_r) − φ(a_r)².

With this approximation, the feedback becomes a linear propagation of the latent states. The joint latent covariance is then obtained by a lower-triangular
solve, and it captures the cross-covariance between F and the feedback. The direct pair effect is kept exact as in L0.

If L1 also fails, the remaining routes are simulated or indirect inference, or closing with an informative negative result.

### 1.5 Estimands and tests
- **Estimand:** σ²_F\* = g²σ²_F under the FB model, with the geometric mean of λ fixed to 1.
- **F test:** T_FB = 2(ℓ_B2-FB − ℓ_B1-FB). Its null reference is the warp-speed parametric bootstrap from the fitted B1-FB (X3-D15 machinery). The
  bootstrap replicates are simulated with feedback, using `simulate_feedback` at (κ̂, τ̂_D).
- **Comparison:** the 2PL T and σ̂²_F\* on the same datasets (paired).
- **Residual check:** the Experiment-5 carry-over diagnostic, `state_dependence.diagnostic.eta_test`, evaluated at the B2-FB fit through its
  derivative arrays, if feasible; otherwise at the B2 fit only.

## 2. Hypotheses (provisional; finalised at the Opus Stage-0 and pilot reviews)
| | Hypothesis | Cells | Rule (provisional) |
|---|---|---|---|
| H6a | Under the FB model, feedback alone is no longer declared F | E3, E4 | α̂ of T_FB against its own B1-FB bootstrap T\* (pairs-bootstrap CI) consistent with 5 % |
| H6b | σ²_F\* is recovered when F and feedback coexist | E5 | FB bias within ±0.05 (MC CI inside), against +0.24 under the 2PL model (paired) |
| H6c | Little cost without feedback | E1 | FB bias within ±0.02; RMSE ratio FB/2PL ≤ 1.25 |
| H6d | F-test power kept | E1, E5 at N = 1000 | share of T_FB above the B1-FB null q95 ≥ 0.8, with CP lower bound > 0.5 |
| H6e | Feedback recovery and residual check (descriptive) | E3, E4, E5 | κ̂ and τ̂_D against the truth; rejection share of the carry-over diagnostic at the FB fit |

## 3. Cells
Cells are those of Experiment 5 without E6. E6 (gain misfit) is not a feedback question.

| Cell | F | Feedback (κ, τ_D) | Main use |
|---|---|---|---|
| E1 | 0.16, τ_F 10 (S1) | none | H6c, H6d |
| E2 | none (S2) | none | level of T_FB |
| E3 | none | −0.25, 10 | H6a, H6e |
| E4 | none | −0.10, 2 | H6a, H6e |
| E5 | 0.16, τ_F 10 | −0.25, 10 (= S7) | H6b, H6d, H6e |

N ∈ {300, 1000}. Sizes are set after Stage 0 and the pilot. Seeds: Stage 0 20266001, pilot 20266002, confirmatory 20266101.

## 4. Stages and gates
**Stage 0 (Sonnet; no confirmatory data).**
1. **Package `feedback_model/`.** It imports kt_trial, difficulty_free, discrimination_free and state_dependence, and modifies none of them.
   - `model.py`: FB parameter map and objective with analytic gradient, reusing `discrimination_free.model` and `kt_trial.bvn`;
   - `fit.py`: `fit_fb`, following `discrimination_free.fit.fit_2pl` (starts, Newton polish, D22 certificate, ridge rule);
   - B2+η: the 2PL objective with a free η·x mean term, using `state_dependence.diagnostic.carry_covariate` at τ_x = 2;
   - `audit.py`: population audit modelled on `state_dependence.audit`;
   - `cli.py`.
2. **G0-1, implementation:**
   - at κ = 0 the FB objective and gradient equal the 2PL ones to 1e-12;
   - the analytic gradient matches finite differences to a relative 1e-6;
   - the cells sum to 1 and lie in (0, 1);
   - L0 cell probabilities at the true E3 and E5 parameters are compared with empirical pair frequencies at N = 200,000 (maximum absolute error, and KL by lag and by session position);
   - the full test suite passes, with the known X3-F06 failure.
3. **G0-2, η-mean route (descriptive):** pseudo-true σ²_F\* of B2+η in E3 and E5.
   - If E3 gives ≤ 0.02 and E5 is within 0.03 of 0.16, the prediction in §1.2 is wrong and the design is reconsidered at the Opus review.
4. **G0-3, the FB route at population level** (B1-FB and B2-FB at N_big = 200,000):
   - E3: σ²_F\* ≤ 0.02, and the expected T_FB at N = 1000 is below 5.16, the Experiment-4 V2 q95;
   - E5: |σ²_F\* − 0.16| ≤ 0.03;
   - E1: |σ²_F\* − 0.16| ≤ 0.01 and |κ\*| ≤ 0.02;
   - E3 and E5: κ\* within ±20 % of the true κ (E4 reported).

   **If G0-3 fails, STOP for the Opus review** (L1, or close).
5. **G0-4, identifiability and sizes:**
   - Godambe SEs of σ²_F\*, κ and τ_D at N = 300 and 1000;
   - corr(σ̂²_F, κ̂);
   - predicted power of T_FB in E1 and E5;
   - expected T_FB in E2, E3 and E4;
   - runtime of an FB fit against a 2PL fit.
6. **Records:** `docs/experiment_06_stage0_report.md` (numbers only), `results/experiment_06/stage0/`, X6-F01 onward, handoff H2. **STOP** for the Opus Stage-0 review.

Stage 0 is expected to cost 5–15 CPU-h.

**Stage 1 (Sonnet, after the Opus review).**
- **Fit jobs:** simulate, then fit B1, B2, B1-FB and B2-FB, then run the diagnostic.
- **Warp jobs** in E2, E3 and E4 add one bootstrap replicate from the fitted B1-FB.
- **Runner, rules and summarizer** follow the Experiment-5 pattern: rep-major order, per-scenario `rep_range` and cost model, CPU cap enforced, frozen-sha256 and code-hash gate, G1–G3.
- **Pilot:** 3 datasets per cell and N, then STOP for the Opus pilot review. The owner sets the cap there; sizes and rules are frozen there.

**Stage 2:**
- Sonnet freezes the configuration and runs the dry-run.
- The owner commits, gives an explicit go-ahead, and runs on an idle machine.
- Sonnet audits and summarizes; Opus interprets.

The rough total is 150–250 CPU-h, because an FB fit costs about twice a 2PL fit.

## 5. Reproducibility and process rules
- Use `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), with OMP_NUM_THREADS, OPENBLAS_NUM_THREADS and MKL_NUM_THREADS set to 1 before Python starts.
- `kt_trial/` and the registered results of Experiments 1–5 are frozen.
- The owner runs every `git add`, `git commit` and `git push`.
- Any change to the protocol, generator, estimands, rules or budget needs the owner's approval. So does any confirmatory start.
- Model routing:
  - Opus: Stage-0 review, pilot review, interpretation;
  - Sonnet: code, tests, configs and runs.

## 6. Limitations stated in advance
- L0 and L1 are approximations. If they leave a pseudo-true bias, that bias is a property of the method and is reported as such.
- The fitted feedback form (exponential, inside the λ bracket, driven by errors on practice attempts) matches the generator. Misspecified feedback forms, such as success-driven or item-specific feedback, are outside scope.
- With 8 templates, the information about κ and τ_D comes from limited schedule variation and from the within-session pair structure. G0-4 quantifies it.

## Addendum (2026-10-11, X6-D06 and X6-D07; Opus Stage-0 review, approved by the owner)
**Erratum to 1.3(d) (X6-D06).** The covariance between earlier errors and the latent state is not second order. Cov(E_r, M0) is O(1), so the
term it induces in Var(Z_t) and in Cov(Z_s, Z_t) is **first order in κ**. Stage 0 confirms this: L0 is exact without feedback and nearly exact
for weak feedback (E4), but at κ = −0.25, τ_D = 10 it misses later practice success rates by 0.017 on average (χ²/df 95–160 per pair). Its fits
there absorb the gap into σ²_r (0.16–0.19 against 0.0225), τ_R, the spread of λ, and σ²_F (0.020 in E3, a bias of +0.041 in E5).
The text of 1.3(d) above is left as approved; this addendum supersedes it.

**Fallback L1 (X6-D07): probit linearisation, direct effect exact.** Per template:
- **Latent core:** X with zero mean and Σ_X = (λλ')∘L + I.
- **Mean:** μ̃_t = −b_t + λ_t(mu0_t + m_t), with m_t = Σ_r U_rt e_r and U = κW (as L0).
- **Linearised errors:** E_r = e_r + β_r z_r + u_r, with
  - β_r = −φ(a_r)/σ_r;
  - Var(u_r) = s_r = e_r(1 − e_r) − φ(a_r)²;
  - e_r = Φ(−a_r), a_r = μ̃_r/σ_r, σ_r² = Var(z_r);
  - u_r uncorrelated with z (exact for Gaussian z).
- **Linear system:** z = X + ΛUᵀ(diag(β) z + u). So:
  - B[t,r] = λ_t U_rt β_r (strictly lower-triangular);
  - A = (I − B)⁻¹;
  - G = AΛUᵀ;
  - Σ_z = AΣ_XAᵀ + G diag(s) Gᵀ.
- **Forward recursion, row by row:**
  1. A[t,:] = e_tᵀ + B[t,:t]A[:t,:];
  2. G[t,:] = A[t,:]ΛUᵀ;
  3. σ_t² = A[t,:]Σ_XA[t,:]ᵀ + Σ_r G[t,r]² s_r;
  4. then m_t, μ̃_t, a_t, e_t, β_t, s_t.
- **Pair s < t, direct effect exact.** Write Z_t = μ̃_t + R_t + λ_tU_st(E_s − e_s), with R_t linear. Then:
  - Cov(R_t, z_s) = Σ_z[s,t] − λ_tU_stβ_sσ_s²;
  - Var(R_t) = σ_t² − 2λ_tU_st(β_sΣ_z[s,t] + s_sG[t,s]) + λ_t²U_st²e_s(1 − e_s);
  - a_s = μ̃_s/σ_s;
  - a_t⁽ʸ⁾ = (μ̃_t + λ_tU_st(1{y = 0} − e_s))/√Var(R_t);
  - ρ = Cov(R_t, z_s)/(σ_s√Var(R_t)).

  The L0 cell formulas apply unchanged.
- **Special cases:** with β ≡ 0, L1 is exactly L0; with κ = 0, it is exactly the 2PL.
- **Still ignored:** u–u correlations and the non-Gaussian remainder.

**Two steps with fixed rules (X6-D07).**
- **Step 1, forward only.** Approximation check G0-1b on the Stage-0 datasets (same seeds). It passes only if, in **both E3 and E5**:
  - L1's excess χ²/df is at most ¼ of L0's, on the feedback-active pairs and on the cross-session pairs;
  - the mean absolute marginal error of later practice positions is ≤ 0.0085;
  - E1 and E2 are unchanged, and E4 is no worse than L0.
- **Step 2, only if Step 1 passes.** Analytic gradient, fits, and G0-3 re-run with **unchanged** thresholds, plus G0-4.
  - If L1 passes G0-3, L1 becomes the primary FB model for Stage 1.
- **Failure at either step:** STOP. Experiment 6 then closes with the population findings of L0 and L1, unless the owner chooses a descriptive L0 continuation. No further approximation levels are built in Experiment 6.
- **The G0-3 check E[T_FB] < 5.16 is a conservative proxy.** H6a calibrates T_FB with a warp bootstrap simulated with the exact feedback generator, and that reproduces approximation artefacts in T\*. The check is kept as written.
