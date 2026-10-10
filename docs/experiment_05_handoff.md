# Experiment 5: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H3: Stage 0 accepted -> Sonnet builds Stage 1 and runs the pilot (2026-10-10)

```text
MODEL HANDOFF — Experiment 5 Stage 1 (pilot infrastructure and pilot; stop before any freeze)
Completed (Opus 5.5): Stage-0 review X5-F03 (accepted; tau_x = 2 kept); X5-D06 (cells E1-E6, sizes, provisional rules, E4 with warp replicates).
Next task (Sonnet 5.5):
  1. state_dependence/ infrastructure modelled on discrimination_free (runner: enforced cap, frozen gate, rep-major order, per-scenario rep_range,
     per-scenario cost model, code_hash over kt_trial + difficulty_free + discrimination_free + state_dependence):
     jobs.py  fit job: simulate_feedback -> fit_2pl B1, B2 -> eta_test at B2 (and B1) for tau_x {2, 5, 10}; store sigma2_F*, tau_F, T, flags,
              eta-hat, S, p, delta. warp job (E4): the same plus one replicate from the fitted B1 null (simulate_feedback without feedback,
              as discrimination_free.jobs.null_2pl_replicate) and its T*.
     runner.py, summarize.py, rules.py (H5a-H5e, G1-G3 per X5-D06; reuse difficulty_free.calibration and difficulty_free.rules.bias_rule;
     CP CIs), cli run / summarize --rules.
  2. Tests: job envelope round-trip on tiny N; rules on synthetic envelopes (H5c verdict branches, H5b rule, G1); rep-major order;
     frozen-sha refusal; full suite (X3-F06 known).
  3. Pilot: configs/experiment_05/stage_pilot.yaml (E1-E6, 3 replications per cell and N, E4 warp, seed 20265002), ~15 CPU-h, idle machine,
     .venv12, single-thread BLAS. Report unit times per cell (fit, scores, replicate), G1 counts, polish counts, diagnostic ran on every fit,
     first-look numbers (no verdicts).
  4. docs/experiment_05_pilot_report.md, X5-F04+, handoff H4. STOP for the Opus pilot review (the owner sets the cap; rules frozen there).
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H2: Stage 0 done -> Opus reviews (2026-10-10)

```text
MODEL HANDOFF — Experiment 5: Stage-0 GATE REVIEW
Completed (Sonnet 5.5): state_dependence/ (simulator, diagnostic, audit, cli), tests (G0-1 met: 6 pass; full suite passes except X3-F06), population audit (11 points, N_big = 200,000, 1.87 CPU-h), docs/experiment_05_stage0_report.md, X5-F01, X5-F02.
Result: G0-2 tau_x = 2 (a-priori rule); G0-3 met (predicted power 1.00 at N = 1000, kappa -0.25, tau_D 10; no-feedback and S8n signals ~ 0, predicted S8n rejection 0.052).
  Feedback without F is fitted as F (sigma2_F* 0.065-0.18; E[T]/q95 from 1.5 to 95). Weakest feedback point: kappa -0.10, tau_D 2 (E[T]/q95 1.5 at N = 300, 4.0 at N = 1000; diagnostic power 0.27 / 0.68 at tau_x = 2).
Questions for Opus: (1) confirm tau_x = 2 or switch (the a-priori rule gave 2, driven by the tau_D = 2 points); (2) choose E4 and finalise cells, sizes and the H5 rules (X5-D01); (3) whether the weak points need more than the planned 30 datasets per N;
  (4) whether the E[T]/q95 margins mean the F-test power cells need warp bootstrap replicates (X5-D03: only where E[T] is close to q95).
Not done: runner / CLI / summarize / rules for the pilot (Stage 1); nothing beyond Stage 0.
Next (Opus 5.5, Plan Mode): Stage-0 review. Git: the owner runs it. Resume: `Switched to Opus; review stage 0`.
```

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
