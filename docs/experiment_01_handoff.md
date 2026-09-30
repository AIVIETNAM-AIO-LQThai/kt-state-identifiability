# Experiment 1 — Handoff log

Newest entry first. Each entry is self-contained so the next model can resume from the files alone.

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
