# Experiment 2 — Handoff log

Newest entry first. Each entry is self-contained so the next model can resume from the files alone.

---

## MODEL HANDOFF — H12: Experiment 2 interpreted and closed; Experiment-1 addendum pending on the owner's PC (2026-10-04)

```text
MODEL HANDOFF — no model task until the owner pushes the addendum results
Completed (Opus): final interpretation (X2-D16), docs/experiment_02_final_report.md, docs/experiment_01_errata.md (E1-E4; registered report unchanged).
Pending (owner, PC): docs/experiment_02_pc_instructions.md -> fingerprint (4 datasets) -> addendum-run (53 datasets, ~2 CPU-h) -> addendum-summarize -> push.
Next task (Opus 5.5, Plan Mode) after the push: interpret results/experiment_01_addendum/summary.{json,md} and write
  docs/experiment_01_addendum_numerical.md (no registered result is replaced). If the fingerprint fails, interpret that as a provenance finding.
Later (needs a new protocol discussion): Experiment 3, unknown item difficulties with item misfit.
Resume: `Switched to Opus; interpret addendum` (or `Switched to Opus; plan Experiment 3`).
```

---

## MODEL HANDOFF — H11: Experiment 2 run complete -> Opus interpretation (2026-10-04)

```text
MODEL HANDOFF — frozen Experiment-2 run finished; interpretation and addendum review are Opus tasks
Completed (Sonnet 5.5): C1-C8 of the H9 review; full pytest 84 passed; freeze X2-D14 (config sha256 c8f8971c...2556, code commit 20283e6,
  master seed 20261402, fresh evaluation learners); cloud run 191/191 jobs ok, 0 errors, 31 min wall; results/experiment_02/confirmatory/eb704015ce
  (summary.json / summary.md). Gates: R0 passed (nothing exceeds the information bound by > 2 learner-SE, incl. S1 track cells); R1 passed
  (32,768 particles: p MC RMS 0.00082, R2 sd 0.0003, doubling within 2 SE, min ESS ok); R2 passed on 6,000 production learners
  (mean |dp| ADF-known vs reference 0.0028; log-loss gain of reference over ADF-known 6e-5 nats [3e-5, 9e-5]).
Headline numbers (practice positions; NOT yet interpreted): R2 pre/post: bound 0.1134/0.1435, reference 0.1128/0.1420, ADF known 0.1128/0.1420,
  ADF fitted 0.1118/0.1402. Tracking value (full over priorF, fitted, nats/response) 0.0030 (N=300) and 0.0029 (N=1000); oracle-F over full ~0.021;
  ideal indicator over full: 0.0096 (rho 0.3), 0.0145 (rho 0.6). Null scenarios (S2, S8n): no spurious tracking gain (R3 False in all four cells;
  S8n N=1000 rep-13 sensitivity: also False).
Open for the owner (PC): docs/experiment_02_pc_instructions.md (fingerprint -> addendum-run -> addendum-summarize -> push). Not run yet.
Next task (Opus 5.5, High, Plan Mode): (1) final interpretation of Experiment 2 against the protocol (claims, limits: known b, exogenous schedule,
  reset-by-session, Gaussian DGP, indicators are ideal positive controls); write docs/experiment_02_final_report.md; (2) after the PC addendum is pushed,
  interpret it and write the Experiment-1 addendum + errata (marginal-score units, Newton-decrement wording). Decide whether to open Experiment 3 (unknown b).
Target: Opus 5.5. Switch: manual (owner). Resume: `Switched to Opus; interpret` (Exp 2 can be interpreted before the addendum arrives).
```

---

## MODEL HANDOFF — H10: review approved -> Sonnet closes the gaps, freezes and runs Experiment 2 in the cloud (2026-10-04)

```text
MODEL HANDOFF — Experiment 2 freeze and production (cloud); addendum on the owner's PC
Completed (Opus, H9): scientific review of transient_filtering at a65fe4f (ADF update, timing, reset, priorF, SMC, bound, generator checks:
  correct). Owner decisions X2-D10 (fresh learners, master seed 20261402), X2-D11 (Exp-2 in the cloud, addendum on the PC), X2-D12 (R0 gate).
Next task (Sonnet 5.5; Medium, High for C1/C3) — protocol addendum H9, sections B and C.1:
  C1 ref_prod job (all 300 held-out learners x S1 N=1000 reps 0-19; one SMC run at 32,768 particles + ADF-known, ADF-fitted, B1 ADF; paired
     gap summaries; bound for the template mix). C2 R1 validation at 32,768 particles (reps 0-9, 2 per template, 10 seeds, x4 doubling, B1 3 seeds).
  C3 summary: gap-decomposition table, R0 gate, R2 on production learners, S8n rep-13 sensitivity, pair priorF_fit over B1_fit.
  C4 provenance hashes (evaluation Y/template_id sha256, Exp-1 fit-envelope sha256, numpy/scipy). C5 addendum-summarize.
  C6 configs/experiment_02/stage_confirmatory.yaml (frozen: true, data_source fresh, master_seed 20261402, track S1/S2/S8n/S8 x {300,1000} x
     reps 0-19, known arms S1/S2, indicators S1 rho 0.3/0.6); record its sha256 (and the addendum config sha256) in the decision log.
  C7 tests; full pytest. C8 re-pilot <= 0.1 CPU-h, then dry-run; STOP if projected > 3 CPU-h.
  Then run the frozen config in the cloud (--frozen-sha256, 4 workers), summarize, commit and push.
  STOP and escalate to Opus if R0 or R1 fails, any job errors persist, or anything would change the question, generator, estimands,
  comparisons, rules or budget. Write PC instructions for the owner: fingerprint (4 datasets) -> addendum-run -> addendum-summarize -> push.
Target: Sonnet 5.5. Switch: manual (owner). Approval: changes C1-C8 and the cloud production run are approved (H9); the addendum is approved
  to run on the owner's PC once fingerprint matches.
Resume action: owner switches the model and replies `Switched to Sonnet; continue`.
```

---

## MODEL HANDOFF — H9: implementation and pilot complete -> Opus scientific review and freeze (2026-10-04)

```text
MODEL HANDOFF — Experiment 2 tooling built and piloted; needs Opus review
Completed (Sonnet 5.5): package transient_filtering/ (filters, SMC reference, bound, regenerate, metrics, jobs, runner, summarize,
  addendum), configs/experiment_02/stage_pilot.yaml, configs/experiment_01_addendum/addendum.yaml, tests/test_transient_filtering.py
  (21 tests, fast + 2 slow), decision log docs/experiment_02_decisions.md. Pilot: 13/13 jobs ok (~0.1 CPU-h), results/experiment_02/pilot/0cc472d76b.
Verified: bound recursion = direct inversion (1e-16) and reproduces the independent figures; probit moments vs quadrature; reset and
  cross-covariance; causality (future y/O perturbation); B2(sigma2_F=0) == B1; keep_latent invariance; SMC vs exact orthant
  probabilities; naive-loop kernels; pair probabilities and S8 gain moments vs analytic; resumable runner, manifest refusal, frozen gate.
Key findings for Opus (docs/experiment_02_decisions.md): X2-F7 container cannot reproduce Exp-1 data (build-dependent SVD basis of the
  repeated-eigenvalue Sigma_M); X2-F10 pilot magnitudes; X2-F11 R1 p-gate failed at 16,384 particles (0.0012) -> 32,768 proposed (I04); R2 undecided on 32 learners.
Open questions needing Opus/owner (not decided by Sonnet):
  1. Evaluation data source for production: (a) owner runs `fingerprint` on the PC; if it matches, regenerate the Exp-1 held-out sets there and
     run production on the PC, or (b) fresh Exp-2 namespace (container-reproducible only if Sigma_M sampling is made build-independent, which
     changes the generator procedure) -> protocol-level choice.
  2. Review the ADF/SMC/bound mathematics and the metric definitions (bins, R3 rule, persistence statistics) before freezing.
  3. Freeze configs/experiment_02/stage_confirmatory.yaml (sha256) and approve the production run (budget <= 12 CPU-h; estimate: Exp-2 ~1-2 CPU-h incl. 32,768-particle reference for all
     S1 N=1000 held-out learners, addendum ~2.1 CPU-h).
Next task (Opus 5.5, High, Plan Mode): scientific review of the code and pilot; decide data source; freeze the Experiment-2 and addendum configs; request approval of the runs.
Target: Opus 5.5. Switch: manual (owner). Approval: no confirmatory or addendum production run is authorised yet.
Resume action: owner switches the model and replies `Switched to Opus; review`.
```
---

## MODEL HANDOFF — H8: protocol approved → Sonnet implements Experiment 2 tooling and the Exp-1 numerical addendum (2026-10-04)

```text
MODEL HANDOFF — Experiment 2 protocol approved (H7); implementation and bounded pilot
Completed (Opus, H7): read-only review of Experiment 1 at e17bc07; protocol in docs/experiment_02_protocol.md (approved).
  Verified: 140 null-bootstrap certificate warnings, all on B2 (109 decrement, 31 non-PD inside the D22 allowance); 117/140 have tau_F stalled at
  a start-grid value; direction-of-effect argument (only the 32 warned S1/S8 replicates can bear on a registered verdict). Found: the
  multivariate_normal(svd) reproducibility hazard (Sigma_M has a 3-fold repeated eigenvalue), the marginal-score unit label (nats per
  response), the shared-kernel gap in generator validation.
Question: under the Exp-1 process with known b, the MMSE-recoverable fraction of F (pre/post answer), the gap decomposition
  (BCRB looseness | ADF approximation | population estimation), the causal next-answer log-loss value of transient information,
  null safety (S2, S8n), and ideal pre-answer indicators (rho 0.3/0.6, oracle-F); S8 ADF-only descriptive.
Equations: protocol §4 (covariance-form BCRB with surrogate noise 1/Ibar_t, innovation parameterisation), §5 (ADF probit update,
  OU propagation and reset, B2-priorF, B2-white, B2-F0, oracle-F, indicator arms, RB-SMC reference).
Branch: exp/transient-state-filtering (created from f2cf8fe; owner-requested purpose name). Experiment 1 stays frozen on
  exp/transient-state-recoverability. Package: transient_filtering/ (owner asked for a purpose name instead of kt_exp2).
Next task (Sonnet 5.5; Medium, High for adf/reference/bound):
  1. docs/experiment_02_plan.md, experiment_02_decisions.md (record approved decisions 1-10, R1-R3) from the protocol.
  2. New package transient_filtering/ (regenerate, adf, reference, bound, addendum, runner, summarize). Do NOT modify kt_trial/ (its code hash
     is part of the Exp-1 freeze); the manifest records an LF-normalised hash of kt_trial and transient_filtering.
  3. Focused tests per protocol §9; full pytest must pass.
  4. Bounded pilot (pre-approved, <= 0.5 CPU-h): fingerprint check on 4 datasets (report whether the container reproduces the
     owner-run data; if not, regeneration moves to the owner's PC), R1 reference gate on 20 learners, benchmarks for the
     Exp-2 and addendum cost estimates. Then STOP and hand off to Opus (H9). No confirmatory evaluation, no config freeze.
Escalate to Opus: fingerprint mismatch on the owner's PC, bound reproduction disagreeing with the Codex figures beyond the
  quadrature tolerance, reference failing R1, ADF numerics (non-PSD covariance), or anything changing the question, generator,
  estimands, comparisons, rules or the 12 CPU-h cap.
Target: Sonnet 5.5, Medium (High for numerics). Switch: manual (owner switches the model in the app).
Approval: protocol approved 2026-10-04; pilot <= 0.5 CPU-h pre-approved; full runs need H9 approval.
Resume action: owner switches the model and replies `Switched to Sonnet; continue`.
```
