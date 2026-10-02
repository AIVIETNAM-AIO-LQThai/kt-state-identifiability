# Experiment 1 — Handoff log

Newest entry first. Each entry is self-contained so the next model can resume from the files alone.

---

## MODEL HANDOFF — H6: final interpretation complete; Experiment 1 closed (2026-10-02)

```text
MODEL HANDOFF — Experiment 1 complete (no further model work pending)
Completed: Opus final interpretation of the Stage 3 confirmatory results (user's local run, commit 97d67a9;
  results/experiment_01/confirmatory/1b1307a48a). 4,930/4,930 jobs ok, 0 errors. Provenance adjudicated (D29: the code hash
  differs only by CRLF line endings, reproduced exactly; dirty flag from untracked files), one certificate flag immaterial
  (D30), S8 nuisance reference note (D31). Verdict D32: H1 supported for sigma2_F under the simulated assumptions
  (PH1 pass, PH2 20/20, PH3/PH4 0/20 each, PH5 inconclusive/pass with 13-15 % attenuation, PH6 improvement / no spurious
  superiority); tau_F weakly determined. Report: docs/experiment_01_final_report.md.
Next task: none. Any extension (MDE power, S7-type processes, unknown difficulties, real data) needs a new approved protocol.
Target: none (user decides).
Reason: Experiment 1 scope is exhausted; the confirmatory evidence has been interpreted.
Switch: none.
Approval: no code, config or result was changed in H6; docs only.
Resume action: none.
```

---

## MODEL HANDOFF — H5b: cloud attempt stopped → user runs Stage 3 locally from scratch (2026-10-01)

```text
MODEL HANDOFF — Stage 3 cloud attempt aborted (D28); user runs the frozen matrix locally
Completed: Stage 3 started in the cloud at the user's request (frozen command, sha256 da9c7d9a…8857); 649/4,930 jobs done, 0 job errors;
  container reclaimed twice when the session was idle, so progress only occurred while active; user chose to finish locally from scratch.
  Cloud run stopped, keep-alive triggers deleted, partial outputs archived to results/experiment_01/archive_cloud_partial_stage3/
  (not summarised, not inspected, not mixed). Protocol, code and config unchanged.
Next task: NOT for a model. The user runs docs/experiment_01_stage3_local_run.md in full (~27 h on 4 workers) and pushes
  results/experiment_01/confirmatory/. Afterwards Opus reads summary.json/summary.md (PH1–PH6), failure accounting and manifest and
  writes the final interpretation and limitations (docs/experiment_01_final_report.md).
Target: Opus 5.5, High, Plan Mode (after the results are pushed)
Reason: Final scientific interpretation; evaluate exactly which claims the results support.
Switch: Manual (no session control for changing the model is exposed).
Approval: Stage 3 protocol approved (D23–D25); venue per D28. No protocol change after seeing results.
Resume action: When the user has pushed the results: `Switched to Opus; final interpretation`.
```

---

## MODEL HANDOFF — H5: Stage 3 frozen → user runs locally → Opus final interpretation (2026-09-30)

```text
MODEL HANDOFF — Stage 3 frozen and ready for the user to run locally
Completed: C6–C8 (D26), 61 tests pass, frozen config stage_confirmatory.yaml (sha256 da9c7d9a1aa20dabded1485d13494ad016d110ae9bfe9abc12edfec5fb118857,
  commit 9ded7a7, code hash 9369a71c…), dry-run 108.5 CPU-h; local PowerShell instructions in docs/experiment_01_stage3_local_run.md.
Next task: NOT for a model yet. The USER runs the confirmatory matrix on their Windows machine (~27 h on 4 workers) and pushes
  results/experiment_01/confirmatory/. Afterwards Opus reads summary.json/summary.md (PH1–PH6 verdicts), the failure accounting and the
  manifest, and writes the final interpretation and limitations (docs/experiment_01_final_report.md).
Target: Opus 5.5, High, Plan Mode (after the results are pushed)
Reason: Evaluate exactly which claims the results support; final scientific interpretation.
Switch: Manual (no session control for changing the model is exposed).
Approval: Stage 3 protocol approved (D23–D25); no further Stage 3 approval is needed to run the frozen config. No protocol change is
  permitted after seeing results; any failure that needs a scientific revision returns to Opus and the user.
Resume action: When the user has pushed the results: `Switched to Opus; final interpretation`.
```

---

## MODEL HANDOFF — H4: Stage 3 approved → pre-freeze corrections, freeze, local-run instructions (2026-09-30)

```text
MODEL HANDOFF — Stage 3 protocol approved (D23–D25)
Completed: Opus H3 review of Stage 2 (verdict: ready for Stage 3 with stated limitations L6–L8); Stage 3 protocol with
  pre-registered rules PH1–PH6 approved by the user (plan addendum "H3 OPUS REVIEW"; decisions D23–D25).
Next task:
  (1) C6: in inference.sandwich, no Wald CI for a variance unless estimate > 2*SE (record "NA (near boundary)"; count as
      non-covering in unconditional coverage).
  (2) C7: runner accepts per-dataset B in null_bootstrap.datasets and N in learner_bootstrap.datasets (and in null datasets).
  (3) C8: summarize computes PH1–PH6 exactly as in D24 (1.96*MCSE; CP bounds; pooled over N for PH3/PH4), the near-white
      share (B2 fits with sigma2_F > 0 and tau_F < 0.4 min), and the MDE design-based detectability line (no pass/fail).
  (4) Tests for C6–C8; full suite.
  (5) Write configs/experiment_01/stage_confirmatory.yaml per D23 with frozen: true; commit; record the git commit, code hash
      and config sha256 in the decision log and here; run `--dry-run` with the frozen sha (do NOT run the matrix).
  (6) Give the user exact PowerShell commands: git pull; activate .venv12; python -m pytest -q; check-env; dry-run;
      run --frozen-sha256 <sha> --workers <cores>; summarize; git add/commit/push results/experiment_01/confirmatory.
Target: Sonnet 5.5, Medium (High for C8 decision-rule code and tests), execution mode
Reason: Implementation of approved reporting/runner changes and the freeze; no scientific decisions remain open.
Switch: Manual (no session control for changing the model is exposed).
Approval: Stage 3 protocol approved (D23–D25). The confirmatory matrix is to be run by the USER locally, not in this container.
Resume action: C6–C8, tests, freeze, dry-run, commands. Escalate to Opus if a correction would change any D23/D24 item.
```

---

## MODEL HANDOFF — H3: Stage 2 complete → Opus interpretation and Stage 3 request (2026-09-30)

```text
MODEL HANDOFF — Stage 2 diagnostic complete
Completed: D22 implemented; full suite 57 passed; re-smoke (results/experiment_01/smoke/0e7ec61e6f, all unblock criteria met);
  Stage 2 (results/experiment_01/diagnostic/eeb188ecc6): 521/521 jobs ok, 0 failed fits, wall 162 min, 10.75 CPU-h;
  report docs/experiment_01_diagnostic_report.md.
Next task: Interpret the diagnostic (what it does and does not support), decide the Stage 3 protocol proposal (final hypotheses,
  estimator version, scenarios, N, replications, thresholds incl. the MDE question D21, null-bootstrap B and which datasets get
  it, compute/cost with the measured 78 s per null replicate, deviations from the prompt) and write the concrete Stage 3
  approval request for the user. Draft the frozen configuration but do NOT freeze or run it.
Target: Opus 5.5, High, Plan Mode
Reason: Separate model limitations, estimator problems and sampling uncertainty; freeze the confirmatory protocol before any run.
Switch: Manual (no session control for changing the model is exposed).
Approval: Stage 3 NOT approved; waiting for a Stage 3 request the user must approve explicitly.
Resume action: Read-only review and request drafting only. No confirmatory run.
```

Headlines for the reviewer (see the report for numbers and MCSEs; 3 reps per scenario): estimator healthy (100 % convergence, all 5 starts reach the best,
Newton decrement <= 2e-4); S1 sigma2_F bias +0.002 +- 0.022 (inconclusive vs 0.04); S7 (endogenous context) inflates sigma2_F by +0.145; S8 underestimates by 0.039;
null test: S1 3/3 reject (p = 0.02 = minimum for B = 49), S2 0/3, S8n 0/3 (one S8n dataset with sigma2_F-hat 0.046, CLR 56.7, p = 0.16);
sandwich vs learner-bootstrap SD: 1.07-1.34 for mean/kernel parameters, 0.90 for sigma2_F, 0.46 for tau_F; bootstrap-null CLR heavy-tailed.
Cost inputs: fit 110 s, null replicate 78 s; Stage 3 null bootstrap at B = 199 on 60 datasets ~ 257 CPU-h (~2.7 days on 4 workers).

---

## MODEL HANDOFF — H2c: criterion-2 decision → implementation, re-smoke, Stage 2 (2026-09-30)

```text
MODEL HANDOFF — D22 decided (Newton-decrement certificate replaces the raw-gradient clause)
Completed: Opus decision D22 (docs/experiment_01_decisions.md; plan addendum "H2b OPUS DECISION"), user-approved. Evidence:
  active Hessian PD in 8/8 read-only fits, Newton decrement 7.6e-10 to 6.8e-9, raw-gradient flag spurious at N=300.
Next task:
  (1) Implement D22 in fit.py: compute the certificate on the selected solution only (reuse the B1 certificate for an
      embedded-null B2); record newton_decrement, hessian_min_eig, hessian_not_pd, the active coordinate names and the raw
      gradient; replace the large_projected_gradient flag with newton_decrement_large; surface the max decrement and the
      hessian_not_pd count in summarize.
  (2) Tests: rewrite test_all_b2_starts_reach_the_same_optimum_on_fixed_n300_dataset to assert decrement <= 1e-3; add a
      decrement-vs-actual-ll-gap test (within 20%, small displaced point) and a hessian_not_pd test (monkeypatched H).
  (3) Run the full suite, then the re-smoke (C5) into a fresh results dir; update the smoke report with a before/after table.
  (4) Check unblock criteria 1–5 (criterion 2 as revised in D22). If all pass, run Stage 2
      (configs/experiment_01/stage_diagnostic.yaml, B=49; dry-run 15.2 CPU-h), summarize, write
      docs/experiment_01_diagnostic_report.md, and hand off (H3) to Opus.
Target: Sonnet 5.5, Medium (High for the D22 numerics and tests), execution mode
Reason: Implementing an approved decision and executing the pre-approved bounded Stage 2 batch.
Switch: Manual (no session control for changing the model is exposed).
Approval: D22 approved; Stage 2 approved with B=49 once the criteria pass; Stage 3 NOT approved.
Resume action: Implement D22 and its tests, run the full suite and the re-smoke, check the criteria, then Stage 2.
  Escalate to Opus on any criterion failure, hessian_not_pd outside the allowance, or single-start-best rate > 20% in a cell.
```

---

## MODEL HANDOFF — H2b: escalation to Opus (unblock criterion 2) (2026-09-30)

```text
MODEL HANDOFF — escalation: unblock criterion 2 fails on a numerical precision floor
Completed: C1 (absolute-units stopping rule), C2 (summaries: NA for boundary/inactive truths; conditional + unconditional
  coverage), C3 (absolute start-agreement metric, secondary_optima, single_start_at_best), C4 (regression tests), Stage 2 config
  (configs/experiment_01/stage_diagnostic.yaml; dry-run 15.2 CPU-h, ~3.8 h wall, 4960 starts). Commit 391b46e.
  Tests: full suite = all pass EXCEPT one new slow test that encodes criterion 2's gradient clause.
  C1 evidence (fixed N=300 S1 dataset, seed 20261001): all 5 B2 starts within 0.01 log-lik of the best (previous rule: 79.4
  units apart), 0 secondary optima, sigma2_F = 0.187, tau_F = 7.0.
Not done: C5 (re-smoke) and Stage 2 — held until the question below is settled (a criterion change alters flag semantics and
  therefore the code hash, so the re-smoke should run once, after the decision).
Question for Opus: the gradient clause of criterion 2 ("absolute projected gradient <= 1e-2") cannot be met. Every start ends with
  scipy "CONVERGENCE: RELATIVE REDUCTION OF F" (ftol = 1e-15; ftol = 0 behaves identically) at an absolute projected gradient of
  0.03-0.18 (B1) / 0.04-0.05 (B2). Cause: the log-lik is ~2e6 in magnitude (resolution ~5e-10) and the Hessian spans eigenvalues 80 to
  6.4e7, so the raw gradient in free coordinates is not a scale-aware precision measure. At the terminated B2 point: Newton
  decrement g'H^-1 g / 2 = 6e-8 log-lik units; largest remaining Newton step = 2.4e-5 (log tau_F), all others < 2e-6.
Proposal (needs Opus/user agreement because it changes an unblock criterion and the flag): replace the gradient clause and the
  `large_projected_gradient` flag by the Newton decrement g'H^-1 g / 2 computed on the active coordinates from the FD Hessian of the
  analytic gradient (18 extra gradient evaluations per fit, ~1 s), with threshold 1e-3 log-lik units; keep the raw gradient as a
  recorded diagnostic. Simpler alternative: drop the gradient clause and rely on start agreement (<= 0.01 log-lik) plus convergence.
  The failing test would be edited accordingly only after the decision; it is left unchanged and failing until then.
Target: Opus 5.5, High, Plan Mode (short decision, no batch)
Reason: Changing an approved unblock criterion / convergence flag is a scientific-protocol decision, not a routine bug fix.
Switch: Manual (no session control for changing the model is exposed).
Approval: waiting for a specific change (criterion 2 wording). Stage 2 remains blocked; Stage 3 NOT approved.
Resume action: Opus decides criterion 2; Sonnet then edits the flag/test accordingly, runs the full suite, runs the re-smoke (C5),
  checks all criteria and, if they pass, runs Stage 2 (B=49).
```

---

## MODEL HANDOFF — H2: Opus review → corrections + Stage 2 (2026-09-30)

```text
MODEL HANDOFF — H1 review complete (BLOCKED on implementation defect; defined unblock path)
Completed: Opus audit of kernels, moments, simulator (S6/S7/S8), BVN/likelihood/adjoint, constraints, nesting, sandwich,
  learner bootstrap, null CLR test, identifiability, runner (verdict and evidence: docs/experiment_01_plan.md addendum
  "H1 OPUS REVIEW"). Read-only re-fits found C1: B2 fits stop early because the stopping rule is scaled per pair (up to 79
  log-lik units short at N=300). Decisions D19 (fix), D20 (Stage 2 null B=49, user-approved), D21 (MDE deferred to Stage 3,
  user-approved) recorded in docs/experiment_01_decisions.md.
Next task: Implement corrections C1–C5 (stopping rule in absolute units; summary excludes boundary/inactive-truth bias and
  coverage and reports conditional + unconditional coverage; absolute start-agreement metric with secondary_optima; new
  regression tests; re-smoke into a fresh results dir with before/after table). Check the unblock criteria. If all pass,
  create configs/experiment_01/stage_diagnostic.yaml (per the addendum), dry-run it, and run Stage 2 if the projection is
  <= 20 CPU-h. Then summarize, write docs/experiment_01_diagnostic_report.md, and hand off (H3) to Opus.
Target: Sonnet 5.5, Medium (High for C1/C4 numerical work), execution mode
Reason: Coding corrections within the approved design, plus execution of a pre-approved, bounded diagnostic batch.
Switch: Manual (no session control for changing the model is exposed).
Approval: C1–C5 are within the approved design. Stage 2 is approved with B=49 (D20) once the unblock criteria pass.
  Stage 3 NOT approved.
Resume action: Implement C1–C5 in order, then check the unblock criteria. Escalate to Opus if any criterion fails,
  if B2 best-start uniqueness exceeds 20% in a cell, or if the Stage 2 dry-run exceeds 20 CPU-h.
```

Unblock criteria (all required before Stage 2):
1. The full test suite passes, including the new C4 tests.
2. Re-smoke: 0 job errors; every fit converged; absolute projected gradient <= 1e-2 in all fits; in every S1 B2 fit at least
   3 of 5 starts are within 0.01 log-lik of the best.
3. Deterministic rerun reproduces a stored job result exactly.
4. The smoke summary shows no bias or coverage for boundary or inactive truths (S2 sigma2_F/tau_F).
5. The Stage 2 dry-run projection is <= 20 CPU-h and <= 6 h wall on 4 workers.

Limitations to carry into all reports: L1 (sigma2_alpha and sigma2_r not identifiable at N <= 300; the sandwich conditions on
boundary nuisance parameters), L2 (tau_F is secondary and weak), L3 (the MDE is not demonstrable), L4 (CLR is not chi-square;
use bootstrap p only), L5 (local identification only).

---

## MODEL HANDOFF — H1: smoke/audit checkpoint (2026-09-30)

```text
MODEL HANDOFF — smoke/audit checkpoint
Completed: M1–M8 implemented and pushed (branch exp/transient-state-recoverability); 51 tests pass;
  design audit + identifiability (results/experiment_01/audit/design_audit.json);
  Stage 1 smoke run (results/experiment_01/smoke/494d1072b9/, 52/52 jobs ok, 10.3 min wall, 0.66 CPU-h);
  report docs/experiment_01_smoke_report.md; decision log D12–D18 + findings F1–F3.
Next task: Audit kernels, moments/covariance, likelihood/BVN, parameter constraints, inference code, schedule audit and
  smoke outputs; return pass / pass with stated limitations / blocked, with evidence. Interpret F1–F2 (SE of sigma2_F ~ MDE at N=300;
  tau_F weakly identified) and say whether any scientific change (thresholds, N, schedule) should be proposed to the user.
Target: Opus 5.5, High, Plan Mode
Reason: Coding success can conceal weak identification or invalid inference; larger batches wait for this review.
Switch: Manual (no session control for changing the model is exposed).
Approval: Stage 1 done. Stage 2 (pre-approved, unchanged) is BLOCKED until this review passes. Stage 3 NOT approved.
Resume action: Review only (read-only). No larger batch, no confirmatory run.
```

Exact commands executed since H0 (repo root, `.venv`): `uv venv --python 3.12 .venv`;
`uv pip install numpy==2.4.6 scipy==1.17.1 pandas PyYAML pytest`; `python -m pytest tests` (full, 51 passed);
`python -m kt_trial audit-design --scenario S1`; `python -m kt_trial run --config configs/experiment_01/stage_smoke.yaml --workers 4`;
`python -m kt_trial summarize --results results/experiment_01/smoke/494d1072b9`; determinism re-execution of
`fit__S2__N64__r1` and `null_rep__S2__N64__r0__b3` (both identical to stored results).

Files to inspect first: `kt_trial/moments.py` (mu, V, Jacobians), `kernels.py`, `simulator.py` (S6/S7/S8), `bvn.py`,
`composite_likelihood.py` (adjoint gradient), `models.py` (coordinates/bounds), `fit.py` (starts, embedded null, flags),
`inference.py` (sandwich, bootstrap, CLR test), `identifiability.py`, `runner.py`.

Unresolved questions for Opus: (1) sandwich vs bootstrap SD ratio 0.5–0.9 at N=64 (10 replicates); (2) sigma2_r / sigma2_alpha at
their lower bounds; (3) findings F1/F2; (4) Stage 2/3 cost (smoke report section 6: Stage 2 central ~15 CPU-h, pessimistic ~27 > 20 cap;
Stage 3 null bootstraps ~175–330 CPU-h); (5) start-policy deviation D13 and adequacy of the tau_F grid; (6) whether the null test needs an
extra calibration check under S8n.

---

## MODEL HANDOFF — H0: plan approved → implementation (2026-09-30)

```text
MODEL HANDOFF — plan approved
Completed: Repository inspection (empty apart from README, bootstrap-requirements.txt, environment_check.txt);
  approved plan persisted to docs/experiment_01_plan.md; decision log docs/experiment_01_decisions.md (D01–D11);
  branch exp/transient-state-recoverability created from 6886865.
Next task: Implement milestones M1–M8 of docs/experiment_01_plan.md (config, schedule, kernels, moments, simulator,
  BVN + pairwise composite likelihood with analytic gradient, models B0/B1/B2, fit/multistart, identifiability audit,
  inference, runner/CLI, summaries, tests), then run the Stage 1 smoke from a fresh results dir.
Target: Sonnet 5.5, Medium effort (High for M3 BVN/gradient, M5 Jacobian, M6 inference), execution mode
Reason: Implementation of an approved specification with test-driven verification.
Switch: Manual. No session control for changing the model is exposed; whether opusplan is offered in this
  cloud session's model picker is unknown.
Approval: Plan approved (incl. Stage 1 and the bounded Stage 2 after an Opus audit). Stage 3 NOT approved.
Resume action: Read docs/experiment_01_plan.md + this file; set up .venv (python3.12, numpy 2.4.6, scipy 1.17.1, pandas,
  PyYAML, pytest; gitignored); implement M1 onward; commit + push at each milestone to
  exp/transient-state-recoverability (no PR).
```

**State at handoff**

- Phase: implementation not started. No code, no configs, no results.
- Commands executed so far: read-only inspection only (`git status`, `git log`, `pip index versions numpy/scipy`,
  interpreter discovery), then `git checkout -b exp/transient-state-recoverability`.
- Environment facts: 4 vCPU, 15 GB RAM; `/usr/bin/python3.12` and `uv` present; system Python 3.11 lacks numpy.
- Stop points for the implementer:
  - Stop after M8 and hand off to Opus (H1: smoke/audit, Plan Mode).
  - Escalate earlier on rank deficiency, conflicting optima, analytic-vs-MC moment mismatch, boundary-inference
    questions, or persistent numerical failures.
  - If the M5 schedule audit fails, stop and request a schedule revision.
- Unresolved: none blocking. Known risk: σ_α² (true 0.0025) and σ_r² may be weakly identified; M5 must quantify this.
