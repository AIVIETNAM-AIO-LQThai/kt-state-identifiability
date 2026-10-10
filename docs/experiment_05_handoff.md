# Experiment 5: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H1: protocol approved -> Sonnet builds Stage 0 (2026-10-10)

```text
MODEL HANDOFF — Experiment 5 Stage 0 (implementation checks and population audit; no confirmatory data)
Completed (Opus 5.5): protocol docs/experiment_05_protocol.md; decisions X5-D01..X5-D05 (owner chose outcome-driven dynamics).
Next task (Sonnet 5.5):
  1. Package state_dependence/ (imports discrimination_free, difficulty_free, kt_trial; modifies none):
     simulator.py  simulate_feedback(cfg, N, seed_keys, master_seed, templates=None, lam=None, ids=None, theta=None, feedback=None,
                   keep_latent=False): D_t = kappa sum_{s<t, same session, practice} 1{Y_s=0} exp(-(t-s)/tau_D) inside the lambda bracket,
                   reset at session start; RNG stream exactly as difficulty_free.simulate_lambda; S8n gains via kt_trial.simulator._gains.
     diagnostic.py covariate x (within-item-centred recent error load, parameter tau_x; probes 0), learner scores u_eta from
                   twopl.learner_scores' wobs (u = sum_t wobs_t lambda_q x_t / sqrt(D_t)), H with an appended eta column (twopl.fisher),
                   Godambe-adjusted score statistic (active coordinates; boundary nuisances fixed, as kt_trial.inference.sandwich), chi2_1 p,
                   one-step eta-hat.
     audit.py      population audit (protocol 4, item 3).
  2. Tests (G0-1): kappa = 0 == simulate_lambda bit for bit; tau_D = tau_F, lambda == 1 reproduces kt_trial S7 (Y identical at N = 20,000,
     latent F + D within 1e-12); u_eta and the eta column of H vs finite differences; scale invariance of S; x == 0 refused. Full suite (X3-F06 known).
  3. Population audit, N_big = 200,000, 2PL B1/B2 fits: grid F {absent, present} x kappa {0, -0.10, -0.25} x tau_D {2, 10} + S8n; per point
     pseudo-true sigma2_F*, tau_F, T/N (expected T at N 300/1000), diagnostic noncentrality and predicted power for tau_x {2, 5, 10}.
     G0-2: fix tau_x (max-min power over kappa = -0.25 points). G0-3: power >= 0.8 at N = 1000 (kappa -0.25, tau_D 10); score mean ~ 0 at
     kappa = 0; S8n predicted false-alarm rate. Flag cells with E[T] < 3 x q95 of Experiment 4's V2 2PL T* (X5-D03).
  4. docs/experiment_05_stage0_report.md (numbers only), results/experiment_05/stage0/, records X5-F01+, handoff H2.
  5. STOP: Opus reviews Stage 0 (choose E4, finalise cells and rules) before any pilot.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```
