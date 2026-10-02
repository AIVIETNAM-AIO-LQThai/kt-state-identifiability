# kt-state-identifiability

Experiment 1: can a **shared transient latent state `F`** (session-resetting Ornstein–Uhlenbeck process) be
separated empirically from baseline mastery, slow learning and short-term recency in a controlled *synthetic*
probit knowledge-tracing process? Population-level recovery only. `F` is a statistical component; nothing here
identifies fatigue, stress, mood, attention or emotion, and nothing uses real learners.

Documents: `docs/experiment_01_plan.md` (approved plan), `docs/experiment_01_decisions.md` (decision log),
`docs/experiment_01_handoff.md` (model handoffs), `docs/experiment_01_smoke_report.md` (Stage 1 evidence).

**Status: complete.** Final interpretation in `docs/experiment_01_final_report.md`. In short: under the simulated
assumptions, σ²_F was recovered without material bias at N = 300 and 1000. The boundary-aware test detected it in 20/20
datasets and produced no false positives in 40 null datasets. Recovery was partly robust to misspecified gains (13–15 %
attenuation). τ_F was only weakly determined. Confirmatory results: `results/experiment_01/confirmatory/1b1307a48a/`.

## Environment

Original local setup: `python -m pip install -r bootstrap-requirements.txt` (Windows, `.venv12`, Python 3.12).
Only NumPy, SciPy, pandas, PyYAML and pytest are used by this experiment (no PyTorch, no GPU).

Windows PowerShell (repo root):

```powershell
& "<path>\.venv12\Scripts\Activate.ps1"
python -m pytest -q                       # fast + slow tests (~3 min)
python -m pytest -q -m "not slow"         # fast tests only
python -m kt_trial check-env
python -m kt_trial audit-design --scenario S1
python -m kt_trial run --config configs/experiment_01/stage_smoke.yaml --dry-run
python -m kt_trial run --config configs/experiment_01/stage_smoke.yaml --workers 4
python -m kt_trial summarize --results results/experiment_01/smoke/<config-hash-prefix>
```

Linux/macOS: replace the activation line with `source .venv/bin/activate`.

## Commands

| command | purpose |
|---|---|
| `check-env` | print versions, code hash, git state; verify imports |
| `audit-design` | schedule audit + local identifiability (Jacobian/SVD, predicted Godambe SEs, deficient control) |
| `simulate` | write one simulated dataset (`.npz`) |
| `fit` | fit B0/B1/B2 to one simulated dataset and print the result |
| `run --config <stage.yaml> [--dry-run] [--workers n] [--retry-errors] [--allow-mismatch]` | run exactly one stage; resumable; refuses on code/config/software mismatch |
| `summarize --results <dir>` | write `summary.json` / `summary.md` |

`run` executes only the stage named in the config. There is no automatic advance from smoke to diagnostic to
confirmatory; the confirmatory stage additionally requires `frozen: true` in its config and
`--frozen-sha256 <sha256 of that config file>`.

## Layout

```
configs/experiment_01/   design.yaml, scenarios/*.yaml, stage_*.yaml
kt_trial/                schedule, kernels, moments, simulator, bvn, composite_likelihood, models, fit,
                         inference, identifiability, evaluate, runner, summarize, manifest, cli
tests/                   unit, Monte-Carlo, derivative, resume and identifiability tests
docs/                    plan, decision log, handoffs, reports
results/experiment_01/   audit/, <stage>/<config-hash>/{manifest.json, jobs/*.json, summary.*}
```
