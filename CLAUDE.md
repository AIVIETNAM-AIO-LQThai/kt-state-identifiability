# Working rules for this repository

## Model routing (remind the owner at every transition)
- **Opus 5.5** (High effort, Plan Mode): planning the procedure, protocol design, scientific review, and interpreting results.
- **Sonnet 5.5**: writing and implementing code, tests, configs, and executing approved runs.

At the end of every step whose next step belongs to the other model, **remind the owner to switch models** and give the exact
resume phrase, for example `Switched to Sonnet; continue` or `Switched to Opus; review`. Never claim the model has changed without
checking. If the current model is the wrong one for the requested task, say so before starting.

## Git
- **The owner runs every `git add`, `git commit` and `git push` personally.** Do not run these. At the end of a step, list the exact
  commands to run: files to add (with `-f` where `.gitignore` would hide them), the commit message, and the push.
- Everything else, such as tests, runs and analysis scripts, may be run automatically within an approved plan.

## Reproducibility
- Experiment-1 regeneration and fits must use `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1) **and** single-threaded BLAS:
  set `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` to 1 **before** starting Python (X2-F15).
- `kt_trial/` and all registered Experiment-1/2 results are frozen. Corrections go into addenda or errata.
- F is a statistical component. Never call it fatigue, stress, mood, attention or emotion.
