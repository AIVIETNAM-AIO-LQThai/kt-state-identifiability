# Experiment 4: handoff log

Newest entry first. Each entry is self-contained.

---

## MODEL HANDOFF — H6: polish and rules built; re-pilot gate not strictly met -> Opus (2026-10-09)

```text
MODEL HANDOFF — Experiment 4: ESCALATION before the freeze
Completed (Sonnet 5.5): R6 polish, rules.py (PH4a-PH4e, G1-G3), tests (all pass; X3-F06 only), re-pilot 24/24 ok (7.42 CPU-h); X4-F13; docs/experiment_04_repilot_report.md.
Result: 2PL non-converged units 6/36 -> 1/36. The one left is the ridge case V4 N = 1000 rep 1: not certified (decrement 0.0061 after 8 steps; 0.0015 after 30; tol 1e-3).
Question for Opus (not changed by Sonnet): (a) accept as the "ridge" exception (the plan said <= 1 of 30 B2 fits certified on the ridge), (b) raise polish steps / relax the certificate on the ridge
  (e.g. treat white_noise_ridge fits with decrement < 0.01 as converged-on-ridge, reported), or (c) change the G1 handling of ridge fits (they affect T by < 0.1). In the full run ~1/36 units -> ~3% of
  ~500 units: under the 5% G1 limit if it stays at that rate, but the pilot has only 36 units.
Cost: re-pilot means give ~154 CPU-h for the X4-D08 matrix (cap 200; trim threshold 195 not triggered).
Not done (waiting for the decision): stage_confirmatory.yaml, rep-major job order in expand_jobs, freeze (X4-D09).
Next (Opus 5.5, Plan Mode): decide (a)-(c); then Sonnet writes/freeze the confirmatory config. Git: the owner runs it. Resume: `Switched to Opus; review re-pilot`.
```

---

## MODEL HANDOFF — H5: pilot reviewed -> Sonnet implements the polish, re-pilots, writes the rules and freezes (2026-10-09)

```text
MODEL HANDOFF — Experiment 4 Stage 2 implementation (stop before the confirmatory run)
Completed (Opus): pilot review X4-F11 (iteration cap: Newton polish fixes it; white-noise ridge), X4-F12 (rule power), X4-D08 (decisions; owner set cap 200 CPU-h).
Next task (Sonnet 5.5; High for the polish):
  1. R6 polish for 2PL only (X4-D08 (1)); tests: polish from a max_iter = 200 truncated fit reaches decrement < 1e-6; cap-stopped but certified start counts as
     converged; start agreement on polished values; 1PL-free output bit-identical to difficulty_free.fit.fit_free; ridge flag. Full pytest (X3-F06 known).
  2. Re-pilot: configs/experiment_04/stage_pilot2.yaml (pilot matrix, seed 20264001). Gate: no non-converged 2PL fit except <= 1 of 30 B2 fits certified on the ridge.
     Report polish counts and the new cost model. If the gate fails: STOP and escalate.
  3. discrimination_free/rules.py (PH4a-PH4e, G1/G2, X4-D08 (4)) wired into summarize; rule tests on synthetic summaries.
  4. configs/experiment_04/stage_confirmatory.yaml (X4-D08 (3); seed 20264101; cap 200 enforced; rep-major order in runner.expand_jobs; cost model from the re-pilot);
     dry-run; trim rule if > 195 CPU-h; set frozen: true; record the sha256 (X4-D09).
  5. STOP: no confirmatory start without the owner's explicit go-ahead on an idle machine. Records X4-F13+, handoff H6, git commands.
Git: the owner runs it. Resume: `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H4: Stage 1 built and piloted -> Opus review; two escalations (2026-10-09)

```text
MODEL HANDOFF — Experiment 4 pilot finished; escalation R5 (non-convergence at the iteration cap; projected cost above 150 CPU-h)
Completed (Sonnet 5.5, .venv12, single-thread BLAS, owner's PC): discrimination_free/ estimator, null bootstrap, warp job, runner, summarize; 10 new tests (pass);
  pilot 24/24 ok (7.75 CPU-h, 40 min); docs/experiment_04_pilot_report.md (numbers only); X4-F07..F10.
Headline (3 reps/cell; indicative): 2PL and 1PL-free both near sigma2_F* (errors within +-0.011); lambda recovery RMSE 0.15 (N = 1000) / 0.24-0.30 (N = 300).
ESCALATION 1 (X4-F09): 2PL B2 hits the 3000-iteration cap in 2/12 recovery fits and 4/18 warp fits (optimum reached to ~0.01 log-lik; B1 needs ~1,800-1,900 iterations).
  Question for Opus: raise fit.max_iter for the 2PL estimator (e.g. 8000) and re-pilot the non-converged cells, or accept? Not changed by Sonnet.
ESCALATION 2 (X4-F10): protocol matrix projects to ~163 CPU-h (cap 150); 2PL fits cost 3-4x 1PL-free. Options priced in the pilot report (75 warp datasets per N -> ~128 h).
For Opus: (1) decide max_iter and the cost-saving option; (2) write and freeze the confirmatory hypotheses/rules (PH4a-PH4e, power, gates incl. non-convergence share);
  (3) check the heavy cases (V5 N = 300 2PL lambda RMSE 0.30; extreme-lambda items).
Next task (Opus 5.5, Plan Mode): review, matrix decision, freeze plan. Git: the owner runs it. Resume: `Switched to Opus; review pilot`.
```

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
