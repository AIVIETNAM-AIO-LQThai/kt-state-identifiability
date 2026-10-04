# Experiment 1: errata (2026-10-04)

The registered Experiment-1 report (`docs/experiment_01_final_report.md`), its decisions and its results are **not modified**.
This page lists the wording corrections found during the Experiment-2 discussion (Opus H7). None of them changes any
pre-registered verdict (PH1–PH6).

| ID | Location in the registered report | Correction |
|---|---|---|
| E1 | §4, "Marginal Bernoulli score: B2 − B1 is ≤ 3e-5 **per learner**" | The held-out marginal Bernoulli score is a **mean per response** (`kt_trial/evaluate.py:35`), so the value is ≤ 3e-5 **nats per response**. The pairwise composite score, by contrast, is a sum over the 6,216 pairs of a learner. |
| E2 | §4, "F has mean zero and alters response dependence, **not** population-marginal success probabilities" | Imprecise. A zero-mean F does change the marginal probability Φ(μ_t/√D_t), because σ²_F enters D_t. The fitted B1 and B2 marginal probabilities nearly coincide because the other variance components compensate. |
| E3 | §2 P3 and decision D30, "the decrement **bounds** the remaining log-lik gain at about 0.04 units" | The Newton decrement is a local quadratic-model estimate of the remaining gain, not a rigorous bound. The adjudication of P3 (immaterial: replication 13 lies outside the null-test replications) is unchanged. A profile check of that fit is part of the numerical addendum. |
| E4 | §4, S8/S8n gain-variance "biases" | Already corrected in the report itself (P4, D31): the actual generating variances are 0.0081 and 0.0441. Listed here for completeness. |

The numerical-validation addendum covering the 140 null-bootstrap certificate warnings, and its write-up, follow after the owner's PC run.
