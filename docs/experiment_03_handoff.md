# Experiment 3: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H8: calibration addendum approved -> Sonnet implements, pilots, freezes, runs after the owner's go-ahead (2026-10-06)

```text
MODEL HANDOFF — Experiment 3 addendum: calibration of the free-difficulty null test (X3-D15)
Next task (Sonnet 5.5):
  1. runner.py: stage `calibration`, job kind `warp` per (scenario, N, rep); ENFORCED CPU-h cap (sum of job runtimes; stop submitting at
     budget.max_cpu_hours; resumable).
  2. jobs.py: run_warp_job = make_dataset + fit_free (B1, B2) -> T; null_free_replicate(b = 0, addendum seed keys) -> T*; record sigma2_F/tau_F
     of both, flags, runtimes, env.
  3. calibration.py: alpha-hat (T_r > q95 of T*, ties at 0 as registered), pairs-bootstrap CI (2,000), rules X3-D15, descriptives, markdown; wire into summarize.
  4. Tests: alpha-hat ~ 0.05 when T and T* are i.i.d.; liberal when T is stochastically larger; rule outcomes; cap stop; tiny end-to-end run.
  5. Pilot: 3 datasets per cell (timing only). Then configs/experiment_03/addendum_calibration.yaml (frozen: true, seed 20262101, C2/C4 x
     N {300, 1000} x R = 100, cap 100 CPU-h); dry-run <= 100 CPU-h; record sha256 (X3-D16); full pytest.
  6. Give the owner the run command and WAIT for the go-ahead (machine idle). After the run: summarize, list git commands, STOP for Opus.
Escalate: pilot timings > 30 % above the estimate, any rule/estimator question. Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H7: Experiment 3 interpreted and closed (2026-10-06)

```text
MODEL HANDOFF — no pending model task
Completed (Opus): provenance check, pre-registered verdicts X3-D14, deviation X3-F14 (167 CPU-h vs 150 cap), docs/experiment_03_final_report.md.
Key results: joint difficulty estimation recovers sigma2_F (PH3a pass) more precisely than known difficulties (SD ratio 0.46); external
  difficulties with SD-0.2 error inflate sigma2_F-hat by about +0.2 everywhere (PH3e); free-b robust to discrimination misfit with F present (PH3d);
  free-b sigma2_F-hat meaningless on the white-noise ridge; free-b null test 3/20 + 3/20 rejections: calibration not established.
Open (recommended next): calibration study of the free-difficulty null test (>= 100 null datasets, B >= 99); a 2PL extension needs its own protocol.
Git: the owner runs it. Resume for new work: `Switched to Opus; plan <next>`.
```

---

## MODEL HANDOFF — H6: config frozen; waiting for the owner's go-ahead to run Experiment 3 (2026-10-05)

```text
MODEL HANDOFF — Experiment 3 confirmatory run is READY, not started
Completed (Sonnet 5.5): U4/U5 mini-pilot (8/8 ok, all converged; X3-F12), rules and gates implemented and tested, frozen config
  configs/experiment_03/stage_confirmatory.yaml sha256 69ddc7f7c1243c28803366586354e9448a9f0edf42a45b0d98b4c8c9cea38c98 (X3-D13), dry-run 130.1 CPU-h, full pytest 109 passed / 1 known failure.
Open flag (X3-F13): mini-pilot timings were 1.5-1.9x the main pilot's while an unrelated project's job kept the CPU at ~95 %. Not established
  as a property of the misfit scenarios. Recommend running with the machine otherwise idle; if the first jobs run much slower than ~280 s per
  known+free fit job, stop and reassess (wall time would double; CPU-h cap still applies).
Run command (PowerShell, repo root; owner go-ahead required):
  $env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'
  & "<venv12>\Scripts\python.exe" -m difficulty_free run --config configs/experiment_03/stage_confirmatory.yaml --frozen-sha256 69ddc7f7c1243c28803366586354e9448a9f0edf42a45b0d98b4c8c9cea38c98 --workers 18
  then: -m difficulty_free summarize --results results\experiment_03\confirmatory\38c681a770   (resumable; re-run the same command if interrupted)
Next (Opus 5.5, Plan Mode): interpret the confirmatory results against X3-D12 (gates first). Git: the owner runs it.
Resume: `Switched to Opus; interpret Experiment 3` (after the run and push).
```

---

## MODEL HANDOFF — H5: confirmatory design approved -> Sonnet: U4/U5 mini-pilot, rules, freeze, owner go-ahead, run (2026-10-05)

```text
MODEL HANDOFF — Experiment 3 freeze and confirmatory run (owner's PC)
Completed (Opus): pilot review and confirmatory design X3-D12 (cap 150 CPU-h kept by the owner; matrix about 130 CPU-h; PH3a-PH3f, power, H3c; gates G1-G3).
Next task (Sonnet 5.5):
  1. U4/U5 mini-pilot (seed 20262001; 2 reps x N {300, 1000}; known + free fits only). Escalate if any fit fails to converge or timings exceed
     the pilot's by > 50 %.
  2. difficulty_free/summarize.py: implement PH3a-PH3f, power, G1-G2, appendix table exactly as X3-D12; tests on synthetic inputs (pass/fail/inconclusive, CP).
  3. configs/experiment_03/stage_confirmatory.yaml (frozen: true; X3-D12 matrix; U4/U5 lambda_cv 0.3; appendix cell; measured cost model;
     budget max 150 CPU-h, 18 workers). Dry-run must be <= 150 CPU-h. Record sha256 as X3-D13. Full pytest (X3-F06 exception documented).
  4. Give the owner the exact run command and WAIT for the owner's go-ahead before running it. After the run: summarize, list git commands, STOP.
Then Opus: interpretation. Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H4: Stage 1 built and piloted -> Opus review, matrix decision and freeze (2026-10-05)

```text
MODEL HANDOFF — Experiment 3 pilot finished; escalation: projected cost above the 150 CPU-h ceiling
Completed (Sonnet 5.5, .venv12, single-thread BLAS, owner's PC): difficulty_free/ (free-b estimators, simulator, jobs, runner, summarize), pilot config,
  11 new tests, pilot run 64/64 ok (3.95 CPU-h, 15.4 min), docs/experiment_03_pilot_report.md (numbers only), X3-F08..F11.
Headline (3 reps/cell; indicative): known and free estimators near the truth; the calibrated-difficulty estimator is strongly biased upward
  (0.26 / 0.36 at U1 N = 1000 / 300; 0.31 / 0.17 with F absent; tau_F-hat near white). Free fits cost 2.2x known; free null replicate about 208 s.
  Free-b b-hat RMSE 0.04-0.09 (N = 1000 / 300).
ESCALATION (X3-F10): section-4 matrix as written = 382 CPU-h (> 150). Options priced: free-only nulls B = 49 with 10 datasets 175 h; 5 datasets 96 h;
  null cells only (U2, U4) B = 99, 5 datasets 132 h. U4/U5 (discrimination misfit) not piloted.
For Opus: (1) choose the null-test design and the final matrix within 150 CPU-h (or approve a higher cap); (2) decide whether to pilot U4/U5 first
  (cheap: fits only); (3) write and freeze the confirmatory hypotheses H3a-H3f and decision rules (PH-style: bias MC CI vs +-0.04; false-positive
  rule; H3e/H3f continuous); (4) check the heavy-tail cases (U2 N = 300 free: one hessian_not_pd / decrement 0.054).
Next task (Opus 5.5, Plan Mode): review, matrix decision, freeze plan. Git: owner runs it (commands in the reply). Resume: `Switched to Opus; review pilot`.
```

---

## MODEL HANDOFF — H3: Stage-0 gate passed -> Sonnet builds Stage 1 and runs the pilot (2026-10-05)

```text
MODEL HANDOFF — Experiment 3 Stage 1 (estimators) and pilot
Completed (Opus): gate review X3-D07 (passed), X3-F07 (why free b lowers the design SE: composite-likelihood pair dependence; known-b
  sigma2_F score is 97.8 % item-marginal noise), X3-D08 (U3 = tau_F 1 min; tau_F 0.2 appendix only), X3-D09 (H3f paired SD ratio),
  X3-D10 (pilot content), X3-D11 (leave the Experiment-1 test unchanged).
Next task (Sonnet 5.5; High for the objective/gradient):
  difficulty_free/: free-b objective (templates with b replaced; reuse kt_trial latent_moments, weighted_cell_loglik_obs, _adjoint_gradient;
  d ll/d b_q = - sum over positions of item q of wa_t / sd_t), ParamMap + 48 b coordinates in [-4, 4], starts from item marginals,
  D19 stopping rule and D22 certificate on all active coordinates, B1-free/B2-free with the embedded null, free-b null bootstrap
  (simulate from fitted B1-free via templates with b-hat), calibration arm (b + N(0, 0.2^2), own RNG namespace, kt_trial fit_model),
  discrimination-misfit simulator (lambda_q lognormal mean 1 CV 0.3; lambda == 1 reproduces kt_trial.simulate bitwise), runner like
  transient_filtering/runner.py (CLI sets *_NUM_THREADS=1 at import; env + data hashes recorded), tests (protocol review section 4).
  Then the pilot (X3-D10) on the owner's PC (.venv12), summary with timings and the paired known/free/cal table. STOP for the Opus review.
  Escalate on non-convergence, poor start agreement, or a projected cost > 150 CPU-h. Do not run git: list the commands.
Target: Sonnet 5.5. Switch: manual. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H2: Stage 0 complete -> Opus gate review (2026-10-05)

```text
MODEL HANDOFF — Experiment 3 Stage 0 finished; needs the Opus gate review (X3-D03)
Completed (Sonnet 5.5, .venv12, single-thread BLAS): difficulty_free/ (audit), configs/experiment_03/stage0.yaml, 7 new tests (pass),
  results/experiment_03/stage0/{audit.json, robustness_seed777_n40000.json}, docs/experiment_03_stage0_report.md (numbers only), X3-F01..F05.
Headline numbers: b-known SEs reproduce Experiment 1 (0.0386/0.0211). Gate: b free, tau_F = 10, N = 1000 -> rank 66/66, SE(sigma2_F) 0.0121 (< 0.08).
  tau_F dependence (b free, N = 1000): 0.2 -> 2.10; 1 -> 0.063; 3 -> 0.021; 10 -> 0.012; 60 -> 0.010. tau_F = 0.2: estimator correlation 0.999 with
  Sigma_M/b coordinates (scale ridge). Surprise (X3-F05): b-free SE below b-known SE for tau_F >= 3.
For Opus: (1) apply the gate and decide the matrix (is U3 at tau_F = 0.2 worth running as a descriptive failure demonstration, or replace by tau_F = 1?);
  (2) judge X3-F05 and whether the pilot must compare free vs known on identical data to confirm it; (3) approve Stage 1 scope.
Next task (Opus 5.5, Plan Mode): gate review, then hand off to Sonnet for Stage 1 (estimators, misfit simulator, tests, pilot).
Git: the owner runs it (commands listed in the reply). Resume: `Switched to Opus; review Stage 0`.
```

---

## MODEL HANDOFF — H1: protocol approved -> Sonnet builds and runs the Stage-0 identifiability audit (2026-10-05)

```text
MODEL HANDOFF — Experiment 3, Stage 0 (analytic, no simulation)
Completed (Opus): protocol docs/experiment_03_protocol.md (approved), decisions X3-D01..D06. Key theory (protocol §1): with b free, a
  white-noise F is exactly confounded with the probit scale; prediction: identified at tau_F = 10, degrading toward the spacing, lost at tau_F -> 0.
Next task (Sonnet 5.5; High for the Jacobian):
  1. New package difficulty_free/ (kt_trial imported, never modified). cli.py sets OMP/OPENBLAS/MKL_NUM_THREADS=1 at import, before numpy.
  2. Stage-0 audit, reusing kt_trial/identifiability.py (observable_jacobian, fisher_pairwise, analyse_point patterns): add the 48 item
     difficulties as free coordinates (d a_t / d b_q = -1/sqrt(D_t) at the positions of item q). Evaluate at tau_F in {0.2, 1, 3, 10, 60},
     other parameters generating, for b known vs b free. Report numerical rank, condition number, the 3 weakest right-singular vectors
     (name the coordinates; check alignment with the predicted scale ridge: b, alpha_bar, r_bar scaled by c; variances by c^2), and
     design-based Godambe SE of sigma2_F at N = 300/1000/3000 (J from simulated learner scores as in kt_trial/identifiability.py).
  3. Tests: d/db against finite differences; with b fixed at the truth, the known-b Jacobian columns equal kt_trial's; the scale-ridge check
     (white noise + rescaling leaves a_t and rho unchanged to 1e-10); the full pytest suite passes.
  4. Write results/experiment_03/stage0/audit.json and a short docs/experiment_03_stage0_report.md (numbers only; no interpretation).
  Run with .venv12 and single-thread BLAS. Do NOT run git: list the git commands for the owner. STOP after Stage 0 for the Opus gate review.
Target: Sonnet 5.5. Switch: manual (owner). Resume: `Switched to Sonnet; continue`.
```
