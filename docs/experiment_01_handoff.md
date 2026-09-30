# Experiment 1 — Handoff log

Newest entry first. Each entry is self-contained so the next model can resume from the files alone.

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
