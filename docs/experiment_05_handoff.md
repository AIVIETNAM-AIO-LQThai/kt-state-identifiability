# Experiment 5: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H7: Experiment 5 closed -> Opus plans Experiment 6 (2026-10-11)

```text
MODEL HANDOFF — Experiment 5 CLOSED
Completed (Opus 5.5): run audit X5-F08 (valid: 620/620 ok, clean manifest, code hash = freeze, 158.6 CPU-h); verdicts X5-F09 (H5a supported,
  H5b supported, H5c inconclusive 0.073 [0.047, 0.109], H5d inconclusive 0.070 [0.029, 0.139], H5e bias +0.24); exploratory level check X5-F10
  (excess confined to E1 with F present: 0.107; scripts/experiment_05_level_check.py); closure X5-D09; docs/experiment_05_final_report.md; README.
Conclusion: the F test detects within-session dependence, not a latent state; the carry-over diagnostic catches strong feedback (power 1.00)
  but is weaker than the F test for weak short feedback (64 % vs 98 % at N = 1000).
Optional Sonnet chore (no rerun, results unchanged): change the stale "Provisional rules (X5-D06)" heading in state_dependence/summarize.py's markdown.
Next (Opus 5.5, Plan Mode): choose and plan Experiment 6 (candidates in X5-D09: joint model with eta; bootstrap calibration of the diagnostic;
  wider feedback grid). Git: the owner runs it. Resume: `Switched to Opus; plan the next experiment`.
```

---

## MODEL HANDOFF — H6: confirmatory config frozen -> owner go-ahead, then run, then Opus (2026-10-10)

```text
MODEL HANDOFF — Experiment 5: READY TO RUN (not started)
Completed (Sonnet 5.5): H5a verdict and extra descriptives in rules.py (X5-F07), full suite passes except X3-F06, stage_confirmatory.yaml frozen (X5-D08), dry-run 193.87 CPU-h (~646 min / 18 workers), wrong-sha refusal checked.
Frozen sha256: 64a7b40214d60409ae067e7b62975b9bbe0c4a7d952c0ca6ebb59eade2b730ee
Code hash at freeze: 70990fcf9fa7eda7fdbd9beaffc194b6f4bf6a6fd22540153aa5e829897946fe
Before starting: COMMIT the code and config (so the manifest is not dirty); idle machine; .venv12; run from this working copy (LF line endings, the sha is of the working-copy file).
Command (owner, repo root):
  $env:OMP_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1; $env:MKL_NUM_THREADS=1
  & "C:\Users\Dell ProMax Tower T2\Downloads\code\.venv12\Scripts\python.exe" -m state_dependence run --config configs/experiment_05/stage_confirmatory.yaml --frozen-sha256 64a7b40214d60409ae067e7b62975b9bbe0c4a7d952c0ca6ebb59eade2b730ee
Resumable (re-run the same command); cap 210 CPU-h enforced. Afterwards: python -m state_dependence summarize --results results/experiment_05/confirmatory/5a3afdf728 --rules
Next: owner's explicit go-ahead -> run (the owner, or Sonnet on request) -> Sonnet audits and summarizes -> Opus 5.5 (Plan Mode) interprets H5a-H5e. Resume after the run: `Switched to Opus; interpret results`.
```

---

## MODEL HANDOFF — H5: pilot accepted, rules frozen -> Sonnet freezes the confirmatory config (2026-10-10)

```text
MODEL HANDOFF — Experiment 5 freeze (stop before the confirmatory run)
Completed (Opus 5.5): pilot review X5-F06; X5-D07 (matrix as X5-D06, cap 210 CPU-h set by the owner, H5a thresholds, frozen rules, operating characteristics).
Next task (Sonnet 5.5):
  1. rules.py: H5a verdict (E3 N = 1000 primary: CP lower > 0.5 -> supported, CP upper < 0.5 -> not supported, else inconclusive; E3 N = 300
     secondary; E4 descriptive); tau_R-at-bound and near-white (tau_F-hat < 0.4) shares in _fit_summary; frozen_rules_version "X5-D06+D07";
     a test of the H5a branches on synthetic envelopes; full suite (X3-F06 known).
  2. configs/experiment_05/stage_confirmatory.yaml: stage confirmatory, frozen: true, seed 20265101; fit E1, E2 [0, 75], E3, E5 [0, 30], E6 [0, 50];
     warp E4 [0, 50]; N [300, 1000]; job_order rep_major; taus_x [2, 5, 10]; null_reference and stage0_summary as in the pilot;
     cost_model_sec {E1: 1023, E2: 993, E3: 1351, E4: 1715, E5: 1296, E6: 652, default: 1351}; budget 210 CPU-h enforced, 18 workers, no wall limit.
  3. Dry-run (expect ~194 CPU-h; trim order only if > 205); record sha256 and code hash as X5-D08; check the wrong-sha refusal.
  4. Records X5-F07, X5-D08, handoff H6 with the exact run command. Remind the owner to commit before starting (clean manifest).
  5. STOP: no confirmatory start without the owner's explicit go-ahead on an idle machine.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H4: pilot done -> Opus pilot review and freeze decisions (2026-10-10)

```text
MODEL HANDOFF — Experiment 5: PILOT REVIEW
Completed (Sonnet 5.5): Stage 1 infrastructure (jobs, runner, summarize, rules, CLI), tests (full suite passes except X3-F06), pilot 36/36 ok (8.37 CPU-h, 35 min wall); X5-F04, X5-F05; docs/experiment_05_pilot_report.md; results/experiment_05/pilot/bf9ceeeae2/.
Result: all B2 fits converged, the diagnostic ran at every fit, G1-G3 pass; predictions of Stage 0 reproduced (E3 sigma2_F-hat ~0.14, E5 bias +0.27/+0.25, diagnostic 6/6 in E3 and E5; E4 diagnostic 0/3 and 2/3; E1/E2 0/12).
Cost: X5-D06 matrix 138.5 CPU-h at pilot means, 193.9 with the x1.4 factor (7.7 / 10.8 h on 18 workers).
Questions for Opus / the owner: (1) the CPU cap (trim order in X5-D06 saves ~22 / 6 / 12 CPU-h before the factor); (2) final sizes; (3) H5a verdict thresholds (X5-D06 gives none); (4) confirm the provisional rules H5b-H5e, the primary tau_x = 2 and the E4 warp design; (5) then Sonnet writes configs/experiment_05/stage_confirmatory.yaml (seed 20265101, per-scenario rep_range, rep-major, cost model from the pilot, cap enforced), dry-runs, freezes (sha256 + code hash) and stops for the owner's go-ahead.
Next (Opus 5.5, Plan Mode): pilot review. Git: the owner runs it. Resume: `Switched to Opus; review pilot`.
```

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
