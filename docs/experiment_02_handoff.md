# Experiment 2 — Handoff log

Newest entry first. Each entry is self-contained so the next model can resume from the files alone.

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
