# Experiment 1 numerical addendum: what to run on your Windows PC

The addendum regenerates Experiment-1 bootstrap datasets, so it must run in the environment that produced them (your `.venv12`:
numpy 2.5.3, scipy 1.18.1). Step 2 checks that. **If any fingerprint does not match, stop and send me `fingerprint_pc.json`.**
The container could not reproduce the data (decision X2-F7), so the addendum cannot be run there.
Config sha256 (audit record, X2-D15): `a4815bf4b1c29419ac0dbd3ce32449d7494af9024bc3f9e90f235259aa641ac7`. About 2 CPU-h in total.

```powershell
# 1. Get the branch (repository root)
git fetch origin
git checkout exp/transient-state-filtering
git pull origin exp/transient-state-filtering
& "<path>\.venv12\Scripts\Activate.ps1"

# 2. Provenance check (about 1 minute): must print match=True for all four
python -m transient_filtering fingerprint --config configs/experiment_02/stage_confirmatory.yaml `
    --dataset S1:300:0 --dataset S2:1000:3 --dataset S8n:1000:13 --dataset S8:300:8 `
    --out results/experiment_01_addendum/fingerprint_pc.json
#    exit code 5 / any match=False  ->  STOP, send fingerprint_pc.json

# 3. Select the 53 datasets (deterministic) and run them (use at most physical cores - 1 workers; resumable)
python -m transient_filtering addendum-select --config configs/experiment_01_addendum/addendum.yaml
python -m transient_filtering addendum-run --config configs/experiment_01_addendum/addendum.yaml --workers 6 2>&1 | Tee-Object addendum_run.log
#    if interrupted, run the same command again

# 4. Summarise and send the results back
python -m transient_filtering addendum-summarize --config configs/experiment_01_addendum/addendum.yaml
git add results/experiment_01_addendum
git commit -m "Experiment 1 numerical addendum: PC results"
git push origin exp/transient-state-filtering
```

Do not edit code or configs. Original Experiment-1 results are never modified: outputs go to `results/experiment_01_addendum/`.
Then, in this session: Opus 5.5, Plan Mode, `Switched to Opus; interpret`.
