# Experiment 4: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H3: Stage-0 gate passed -> Sonnet builds the 2PL estimator and runs the pilot (2026-10-09)

```text
MODEL HANDOFF — Experiment 4 Stage 1 (estimator) and pilot
Completed (Opus): gate review X4-D07 (passed), X4-F06 (lambda-fixed SE larger than lambda-free: X3-F07 mechanism; no lambda-fixed arm).
Next task (Sonnet 5.5; High for the objective/gradient), all in discrimination_free/ (difficulty_free/ and kt_trial/ imported only):
  1. Parameter map [ParamMap(B1|B2) | b (48, [-4, 4]) | w (47, log lambda = P w, |log lambda| <= log 5)]; objective from twopl.core moments +
     kt_trial.bvn.weighted_cell_loglik_obs; analytic gradient via the per-observation/per-pair adjoint weights chained through twopl.core Jacobians.
  2. fit (mirror difficulty_free.fit.fit_free: grids, jitter, D19, D22 on all active coords, embedded null, start agreement; starts w = 0, b from
     start_difficulties; B2 warm from B1); 2PL null replicate (simulate_lambda with lambda-hat); warp job (2PL and 1PL-free, same dataset);
     results store g and sigma2_F* = g^2 sigma2_F (estimand guard); lambda recovery on centred log lambda.
  3. runner/summarize/rules following difficulty_free (calibration stage, enforced cap, frozen gate); CLI sets *_NUM_THREADS=1 at import.
  4. Tests: gradient (113 coords) vs FD; w = 0 equals difficulty_free; nesting; geometric mean of lambda-hat = 1; lambda recovery smoke; g bookkeeping;
     tiny end-to-end run, resume, cap stop. Full pytest (X3-F06 known).
  5. Pilot (X4-D07 R4) on the idle PC; report timings, certificates, start agreement, projected cost. Escalate per R5. STOP for the Opus pilot review.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H2: Stage 0 complete -> Opus gate review (2026-10-08)

```text
MODEL HANDOFF — Experiment 4 Stage 0 finished; needs the Opus gate review (X4-D03)
Completed (Sonnet 5.5, .venv12, single-thread BLAS): discrimination_free/ (2PL audit), configs/experiment_04/stage0.yaml, 8 new tests (pass),
  results/experiment_04/stage0/{audit.json, robustness_n40000.json}, docs/experiment_04_stage0_report.md (numbers only), X4-F01..F05.
Gate numbers: 2PL at tau_F = 10, N = 1000: rank 113/113; SE(sigma2_F*) 0.0122 (lambda == 1; 1.01x the lambda-fixed SE, equal to the Experiment-3 1PL-free value)
  and 0.0114 (lambda CV 0.27 draw; sigma2_F* = g^2 sigma2_F with g = 0.947); threshold 0.08; two more draws 0.0128 / 0.0116. Scale invariance 4e-16.
For Opus: (1) apply the gate (all figures are far below the threshold); (2) judge X4-F04 (lambda-fixed SE 3x the lambda-free SE under misfit: likely the
  X3-F07 mechanism; matters for H4d wording and for whether a lambda-fixed arm is worth running); (3) approve Stage 1 scope (estimator, 2PL null, warp job,
  pilot) and the cell list V1/V2/V4/V5; (4) decide whether the estimand sigma2_F* = g^2 sigma2_F needs further guarding (g is per replication).
Next task (Opus 5.5, Plan Mode): gate review and Stage-1 approval. Git: the owner runs it (commands in the reply). Resume: `Switched to Opus; review Stage 0`.
```

---

## MODEL HANDOFF — H1: protocol approved -> Sonnet builds and runs the Stage-0 audit (2026-10-08)

```text
MODEL HANDOFF — Experiment 4, Stage 0 (analytic, no fitting)
Completed (Opus): docs/experiment_04_protocol.md (approved), decisions X4-D01..D06.
Next task (Sonnet 5.5; High for the Jacobian):
  1. New package discrimination_free/ (imports difficulty_free/ and kt_trial/, modifies neither); cli.py sets *_NUM_THREADS=1 before numpy.
  2. Stage-0 audit extending difficulty_free/freeb.py + audit.py: observable map with mu = -b + lambda * mu0, V = (lambda lambda') * L + I
     (mu0, L from kt_trial.moments.latent_moments with b = 0); coordinates = 18 model + 48 b + 47 log-lambda (geometric-mean constraint).
     At tau_F = 10: rank, condition number, 3 weakest directions (named), design Godambe SE of sigma2_F at N = 300/1000/3000 for 2PL vs
     1PL-free, at lambda == 1 and at one lambda CV 0.3 draw (record g). Scale-invariance check (lambda*c, latent/c leaves a and rho unchanged to 1e-10).
  3. Tests: d/dlambda and d/db vs finite differences; lambda == 1 block equals difficulty_free's; scale invariance; full pytest (X3-F06 known).
  4. results/experiment_04/stage0/audit.json and docs/experiment_04_stage0_report.md (numbers only). STOP for the Opus gate review.
  Run in .venv12 with single-thread BLAS. Do not run git: list the commands.
Target: Sonnet 5.5. Switch: manual (owner). Resume: `Switched to Sonnet; continue`.
```
