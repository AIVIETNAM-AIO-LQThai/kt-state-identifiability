# Experiment 2: implementation plan (Sonnet, H8)

Source specification: `docs/experiment_02_protocol.md` (Opus H7, approved 2026-10-04). Branch `exp/transient-state-filtering`.
This plan only says how the approved protocol is realised in code; scientific changes go to Opus and the owner.

**Question.** Under the Experiment-1 generating process with known item difficulties: how much individual transient-state
information F is available at prediction time (MMSE), how much a practical Gaussian filter uses, what it is worth for causal
next-answer prediction, whether tracking is spuriously produced when F is absent, and what ideal pre-answer indicators add.
F is a statistical component; nothing here is a psychological construct.

## Layout (new files only; `kt_trial/` and every Experiment-1 result are untouched)
| file | purpose |
|---|---|
| `transient_filtering/model.py` | state-space form: state (M0 x4, alpha, r, F), observation rows h_t, OU propagation and session reset |
| `transient_filtering/filters.py` | causal ADF: `run_full` (7-state; B2, priorF, indicator arms), `run_persistent` (6-state: B1, F0, white, oracle-F) |
| `transient_filtering/reference.py` | Rao-Blackwellised fully adapted SMC over latent utilities (the high-accuracy causal reference) |
| `transient_filtering/bound.py` | posterior Cramer-Rao bound in covariance form, plus an independent direct information-matrix inversion |
| `transient_filtering/regenerate.py` | regeneration of Experiment-1 data from recorded seeds and fingerprint checks against the saved fits |
| `transient_filtering/metrics.py`, `jobs.py` | endpoints (per-learner bin means summarised as n/mean/var) and the `bound`, `track`, `ref` job bodies |
| `transient_filtering/runner.py`, `cli.py` | resumable runner (deterministic job ids, atomic writes, dry-run, manifest-mismatch refusal, frozen gate) |
| `transient_filtering/summarize.py` | pooled results, R1/R2/R3 evaluation, markdown summary |
| `transient_filtering/addendum.py` | selection and per-dataset checks for the Experiment-1 numerical addendum |
| `configs/experiment_02/stage_pilot.yaml`, `configs/experiment_01_addendum/addendum.yaml` | pilot and addendum configurations (nothing frozen) |
| `tests/test_transient_filtering.py` | focused tests (below) |

## Verification
- `python -m pytest -q` (all of Experiment 1 plus the new file; the slow marker holds the Monte Carlo generator checks).
- Pilot (<= 0.5 CPU-h): `python -m transient_filtering run --config configs/experiment_02/stage_pilot.yaml` then `summarize`.
- On the owner's PC: `python -m transient_filtering fingerprint ...` (provenance of regenerated Experiment-1 data), then the addendum.
