# Experiment 1 numerical addendum, RUN 2: what to run on your Windows PC

**Why a second run.** Run 1 (commit `584ac96`) executed under the system Python (`...\AppData\Local\Programs\Python\Python312\python.exe`, numpy 2.5.1),
not under the environment that produced Experiment 1 (`.venv12`, numpy 2.5.3). Its data reproduced, but optimiser endpoints differ across numpy
versions. Run 2 must use `.venv12`'s python. The commands below now **refuse to run** (exit code 6) with any other numpy/scipy/python.

Config sha256 of run 2 (decision X2-D18): `2714bca1f16ba70fe706ffebe930e457cf75ca97ece957483b19b9643d1c34af`. About 2 CPU-h.

**Call the interpreter explicitly in every command** (do not rely on `python` or on activation). Replace `<venv12>` with the folder of your
Experiment-1 environment, e.g. `C:\Users\Dell ProMax Tower T2\Downloads\code\.venv12`.

```powershell
$py = "<venv12>\Scripts\python.exe"

# 0. Get the branch
git fetch origin
git checkout exp/transient-state-filtering
git pull origin exp/transient-state-filtering

# 1. Check the interpreter: must print numpy 2.5.3 and scipy 1.18.1
& $py -c "import sys, numpy, scipy; print(sys.executable, numpy.__version__, scipy.__version__)"
#    if numpy is not 2.5.3, STOP and send me the output (the commands below would refuse anyway)

# 2. Save run 1's per-dataset files, which .gitignore had hidden (force-add; they are a record of run 1)
git add -f results/experiment_01_addendum/datasets
git commit -m "Addendum run 1: per-dataset files (numpy 2.5.1 interpreter; kept as a record)"

# 3. Provenance check (about 1 minute): must print match=True for all four
& $py -m transient_filtering fingerprint --config configs/experiment_02/stage_confirmatory.yaml `
    --dataset S1:300:0 --dataset S2:1000:3 --dataset S8n:1000:13 --dataset S8:300:8 `
    --out results/experiment_01_addendum/run2/fingerprint_pc.json
#    exit code 6 = wrong environment; exit code 5 / any match=False = STOP and send me the output

# 4. Select and run the 53 datasets (at most physical cores - 1 workers; resumable: run again if interrupted)
& $py -m transient_filtering addendum-select --config configs/experiment_01_addendum/addendum_run2.yaml
& $py -m transient_filtering addendum-run --config configs/experiment_01_addendum/addendum_run2.yaml --workers 6 2>&1 | Tee-Object addendum_run2.log

# 5. Summarise and push everything (outputs are in results/experiment_01_addendum/run2/, not ignored)
& $py -m transient_filtering addendum-summarize --config configs/experiment_01_addendum/addendum_run2.yaml
git add results/experiment_01_addendum/run2
git commit -m "Experiment 1 numerical addendum: run 2 (.venv12, numpy 2.5.3)"
git push origin exp/transient-state-filtering
```

Do not edit code or configs, and do not delete run 1's files. Original Experiment-1 and Experiment-2 results are never modified.
Then, in this session: Opus 5.5, Plan Mode, `Switched to Opus; interpret addendum`.
