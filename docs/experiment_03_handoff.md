# Experiment 3: handoff log

Newest entry first. Each entry is self-contained.

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
