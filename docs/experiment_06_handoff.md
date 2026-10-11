# Experiment 6: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H3: Stage 0 reviewed -> Sonnet builds L1 in two gated steps (2026-10-11)

```text
MODEL HANDOFF — Experiment 6 L1 fallback (Step 1 forward-only gate; Step 2 only if Step 1 passes)
Completed (Opus 5.5): Stage-0 review X6-F07; erratum X6-D06 (error-latent covariance is first order in kappa); X6-D07 (L1 spec + rules); protocol addendum.
  Owner chose: build L1, cheap check first. G0-3 thresholds unchanged.
Next task (Sonnet 5.5):
 STEP 1 (forward only):
  1. feedback_model/fbmodel_l1.py: forward_template_l1(st, mu0, L, lt, bt, kappa, tau_D, iu, ju, beta_on=True) per the protocol addendum
     (Sigma_X = (lt lt')*L + I; row recursion A[t,:] = e_t' + B[t,:t] A[:t,:], B[t,r] = lt_t U[r,t] beta_r, G = A diag(lt) U', sigma_t^2 = A[t] Sigma_X A[t]' + sum_r G[t,r]^2 s_r,
     m_t, mut_t, a_t, e_t, beta_t = -phi(a_t)/sigma_t, s_t = e_t(1-e_t) - phi(a_t)^2; Sigma_z = A Sigma_X A' + G diag(s) G';
     pair: CovR = Sigma_z[s,t] - lt_t U_st beta_s sigma_s^2, VarR = sigma_t^2 - 2 lt_t U_st (beta_s Sigma_z[s,t] + s_s G[t,s]) + lt_t^2 U_st^2 e_s(1-e_s),
     a_s, a1, a0, rho as in the addendum); ObjectiveFB1 (ParamFB coordinates) with intermediates(); reuse _Static, cell_prob_table, cell_loglik.
  2. Tests: beta_on=False gives L0's intermediates exactly (fbmodel.forward_template); kappa = 0 gives the 2PL exactly; cells sum to 1; VarR > 0 and sigma^2 > 0
     on a grid (kappa in {-0.6, -0.25, 0.3}, several tau_D); full suite (X3-F06 known).
  3. audit.approx_check: add label "L1" (keep "L0" and "no_feedback_term" for comparison) incl. marginals; CLI `python -m feedback_model approx --config
     configs/experiment_06/stage0.yaml --out results/experiment_06/stage0b` (same datasets as Stage 0: seed 20266001, keys ("pop", cell)); approx.json + approx.md.
  4. Apply the G0-1b rule (X6-D07) and record X6-F08. If it FAILS: STOP (handoff H4 to Opus).
 STEP 2 (only if Step 1 passes): analytic reverse-mode gradient of L1 (finite-difference tests on all coordinate types; beta-off = L0 gradient; kappa = 0 = 2PL gradient);
  fit_ext(kind="fb1"); audit with the L1 arm (B1-FB1, B2-FB1) on the same seeds (keep the Stage-0 results; write results/experiment_06/stage0b/points);
  G0-3 (unchanged thresholds) and G0-4 for L1; report docs/experiment_06_stage0b_report.md; X6-F09+; handoff H4. STOP for the Opus review.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H2: Stage 0 done, G0-3 NOT met -> Opus reviews (2026-10-11)

```text
MODEL HANDOFF — Experiment 6: STAGE-0 GATE REVIEW (G0-3 failed: stop per X6-D04)
Completed (Sonnet 5.5): feedback_model/ (fbmodel, etamodel, fit, audit, cli), tests (7 new; full suite 166 passed, X3-F06 deselected), Stage-0 audit (5 cells, N_big = 200,000, 1.7 CPU-h), docs/experiment_06_stage0_report.md, X6-F01..F06.
Results: G0-1 met (kappa = 0 identity, gradients, cells); G0-2 B2+eta fails to remove the misattribution (sigma2_F* 0.143 E3, 0.408 E5); G0-3 NOT met: E3 sigma2_F* 0.0204 (limit 0.02), E3 E[T_FB] N = 1000 = 29.0 (reference q95 5.16, coarse), E5 sigma2_F* 0.201 (|error| 0.041 > 0.03); passed E1 and kappa within 20 %.
  The FB model removes 86 % (E3) and 84 % (E5) of the 2PL misattribution, is exact for E4 (sigma2_F* 0, kappa* -0.1006, tau_D* 2.01), recovers kappa* -0.262 / -0.257 and tau_D* 10.97 / 10.69 (truth -0.25, 10); precision cost nil (SE ratio 0.97-1.04 in E1, E5). A smoke fit at N = 1000 (E3-type, one dataset) gave kappa-hat -0.258, T_FB = 0.
  Approximation check: L0 is exact in E1/E2, nearly exact in E4 (chi2/df 1.3-1.4), not in E3/E5 (95-160; marginals of later practice positions off by 0.017). The neglected covariance between earlier errors and the latent state is FIRST order in kappa (protocol 1.3 (d) said second order - wrong).
Questions for Opus / the owner: (1) accept L0 with its residual (E3 0.020, E5 +0.041 at population level) or build L1 (probit linearisation of earlier errors, X6-D02) - the strong-feedback cells are the S7 strength; (2) if L0: how to read G0-3 (the failed E3 limit is 0.0004 over, E5 0.011 over; the T_FB null is uncalibrated, so the E[T_FB] check needs a warp bootstrap, which Stage 1 will give) and whether the hypotheses H6a/H6b thresholds should be relaxed (e.g. bias within 0.05 in E5 would pass: 0.041); (3) the H6e residual diagnostic at the FB fit is not built (needs an eta column in the FB derivative arrays; finite-difference route available); (4) sizes: FB fits take 0.65-2.2 x a 2PL fit, Godambe SEs in the report; (5) E2/E1 FB fits have tau_D unidentified (flag, secondary optima, one hessian_not_pd) - how Stage 1 should treat it.
Not done: Stage 1 (jobs, runner, rules, pilot); nothing beyond Stage 0.
Next (Opus 5.5, Plan Mode): Stage-0 review. Git: the owner runs it. Resume: `Switched to Opus; review stage 0`.
```

---

## MODEL HANDOFF — H1: protocol approved -> Sonnet builds Stage 0 (2026-10-11)

```text
MODEL HANDOFF — Experiment 6 Stage 0 (implementation checks and population audit; no confirmatory data)
Completed (Opus 5.5): protocol docs/experiment_06_protocol.md; decisions X6-D01..X6-D05 (owner chose "Adjust for feedback").
Before starting: the owner has created branch exp/feedback-adjusted-F (from exp/outcome-driven-dynamics after the Experiment-5 closure commit).
Next task (Sonnet 5.5):
  1. Package feedback_model/ (imports kt_trial, difficulty_free, discrimination_free, state_dependence; modifies none):
     model.py  FB parameter map = Param2PL coordinates + kappa [-1, 1] + tau_D [0.5, 50]; objective with approximation L0 (protocol 1.3):
               forward mean-field recursion per template (e_r = 1 - Phi(a_r); m_t, v_t, c_st with w_rt = exp(-(time_t - time_r)/tau_D) for r < t,
               r practice, same session); pair cells with the exact direct effect (a_t^(1), a_t^(0), conditional variance, rho_st);
               P11 = Phi2(a_s, a_t1; rho), P10 = Phi(a_s) - P11, P01 = Phi(a_t0) - Phi2(a_s, a_t0; rho), P00 = 1 - Phi(a_s) - P01; pair counts only;
               analytic gradient (reuse kt_trial.bvn, discrimination_free.model.contract and twopl patterns). Also B2+eta: the 2PL objective with a free
               eta x mean term (x = state_dependence.diagnostic.carry_covariate, tau_x = 2).
     fit.py    fit_fb(model in {B1-FB, B2-FB}, ...) following discrimination_free.fit.fit_2pl (starts incl. kappa 0 / -0.2 and several tau_D, Newton
               polish, D22 certificate, ridge rule); fit for B2+eta likewise.
     audit.py  population audit at N_big = 200,000 (pair counts; seed 20266001): cells E1-E5 (state_dependence.simulator.simulate_feedback);
               per cell pseudo-true sigma2_F*, tau_F, kappa*, tau_D* under B2-FB, B1-FB, B2+eta and B2 (2PL, for reference); expected T_FB at N 300/1000;
               Godambe SEs (sigma2_F, kappa, tau_D) and corr(sigma2_F-hat, kappa-hat) at N 300/1000; predicted power of T_FB (E1, E5);
               runtime of one FB fit against one 2PL fit.
     cli.py    `python -m feedback_model audit|report`; set thread env vars before numpy loads.
  2. Tests (G0-1): kappa = 0 equals the 2PL objective and gradient (1e-12); gradient against finite differences (relative 1e-6) at kappa != 0 for
     B1-FB and B2-FB; cells sum to 1 and lie in (0, 1); L0 cell probabilities against empirical pair frequencies at N = 200,000 at the true E3 and E5
     parameters (report max abs error and KL by lag; this is a measurement, not a pass/fail beyond sanity); full suite (X3-F06 known).
  3. Gates G0-2 (B2+eta, descriptive), G0-3 (FB at population level) and G0-4 (identifiability, sizes) as in X6-D04; expected cost 5-15 CPU-h, idle machine,
     .venv12, single-thread BLAS.
  4. docs/experiment_06_stage0_report.md (numbers only), results/experiment_06/stage0/, records X6-F01+, handoff H2.
  5. STOP: Opus reviews Stage 0 (G0-3 failure -> L1 decision or closure) before any pilot.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```
