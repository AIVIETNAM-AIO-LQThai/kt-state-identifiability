# Experiment 6: handoff log

Newest entry first. Each entry is self-contained.

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
