# Experiment 4: handoff log

Newest entry first. Each entry is self-contained.

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
