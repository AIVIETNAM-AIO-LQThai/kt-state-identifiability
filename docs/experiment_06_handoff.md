# Experiment 6: handoff log

Newest entry first. Each entry is self-contained.

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
