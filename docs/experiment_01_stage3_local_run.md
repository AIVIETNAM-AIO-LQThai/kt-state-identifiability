# Stage 3 (confirmatory) — how to run it on your Windows machine

**You run this; nothing here has been run.** Approved protocol: decisions D23–D25 (`docs/experiment_01_decisions.md`), plan addendum
"H3 OPUS REVIEW" (`docs/experiment_01_plan.md`). The configuration is frozen; the runner refuses to start unless the hash below matches.

| item | value |
|---|---|
| frozen config | `configs/experiment_01/stage_confirmatory.yaml` |
| sha256 of that file | `da9c7d9a1aa20dabded1485d13494ad016d110ae9bfe9abc12edfec5fb118857` |
| frozen code commit | `9ded7a7afaf7eb42f986ec7cfa009bc58a786183` (later commits change docs only) |
| code hash (`kt_trial/*.py`) | `9369a71c895819c295143c279d7671ba446d5b5b9626eef1c602e96e66916efc` |
| results directory | `results\experiment_01\confirmatory\1b1307a48a` |
| matrix | S1, S2, S8, S8n × N ∈ {300, 1000} × 20 replications = 160 fit jobs; 4,720 null-bootstrap + 50 learner-bootstrap replicates |
| estimated cost | about 108 CPU-hours (≈ 27 h wall on 4 workers, ≈ 14 h on 8; N = 1000 not yet timed, ±30 %) |

Requirements: about 1 GB RAM per worker, roughly 30 MB of disk, no GPU. Keep the machine awake for the whole run.

## Steps (PowerShell, from the repository root)

```powershell
# 1. Get the frozen state
git fetch origin
git checkout exp/transient-state-recoverability
git pull origin exp/transient-state-recoverability
git diff 9ded7a7 --stat -- kt_trial configs          # must print nothing (code and configs unchanged since the freeze)

# 2. Environment (your existing .venv12)
& "<path>\.venv12\Scripts\Activate.ps1"
python -m pip install -r bootstrap-requirements.txt   # only if something is missing
python -m kt_trial check-env                          # note numpy/scipy versions; they are recorded in the manifest

# 3. Verify the frozen file (must print the same hash as in the table above)
(Get-FileHash configs\experiment_01\stage_confirmatory.yaml -Algorithm SHA256).Hash.ToLower()

# 4. Tests must pass BEFORE the run (3-10 min). If anything fails: STOP, do not run, and tell me the output.
python -m pytest -q

# 5. Dry run: prints the job matrix and cost; no fitting
python -m kt_trial run --config configs/experiment_01/stage_confirmatory.yaml --dry-run `
    --frozen-sha256 da9c7d9a1aa20dabded1485d13494ad016d110ae9bfe9abc12edfec5fb118857
#    expect: {'fit': 160, 'null_rep': 4720, 'lboot_rep': 50}, total starts 49700, config_hash=1b1307a48a5a

# 6. The confirmatory run. Use at most (physical cores - 1) workers.
powercfg /change standby-timeout-ac 0                 # keep the PC awake on mains power (optional)
python -m kt_trial run --config configs/experiment_01/stage_confirmatory.yaml `
    --frozen-sha256 da9c7d9a1aa20dabded1485d13494ad016d110ae9bfe9abc12edfec5fb118857 `
    --workers 6 2>&1 | Tee-Object -FilePath confirmatory_run.log
```

**If the run is interrupted** (sleep, reboot, Ctrl+C): run the same command again. Finished jobs are kept, and corrupt or unfinished ones are rerun.
**If the runner prints `REFUSED`** (code, package-version or config mismatch), do not pass `--allow-mismatch`; send me the message.
**If jobs report `error`**, the log shows the count. Do not edit any code or config; send me the log. (`--retry-errors` only re-attempts failed jobs; it does not change the protocol.)

```powershell
# 7. When the log ends with "stage confirmatory finished":
python -m kt_trial summarize --results results\experiment_01\confirmatory\1b1307a48a
#    writes summary.json / summary.md (includes the pre-registered PH1-PH6 verdicts)

# 8. Send the results back (about 25 MB)
git add results/experiment_01/confirmatory
git commit -m "Stage 3 confirmatory results (frozen config sha256 da9c7d9a...)"
git push origin exp/transient-state-recoverability
```

Then, in this session: select **Opus 5.5**, **High** effort, **Plan Mode**, and reply `Switched to Opus; final interpretation`.
Do not modify `kt_trial\`, `configs\`, or the results while the run is in progress, and do not start any other Stage.

## What the run computes
Fits B0/B1/B2 to each of the 160 datasets (fit N = 300 or 1000 learners, plus 300 separate held-out learners), the learner-score sandwich for B1/B2, the boundary-aware parametric-bootstrap composite-likelihood-ratio test of σ²_F = 0 on 10 datasets per cell
(B = 99 for S2/S8n, B = 19 for S1/S8), and one learner bootstrap (B = 50) on S1, N = 1000, rep 0. The summary reports PH1–PH6 exactly as pre-registered.
Claims are limited to statistical recovery under the simulated assumptions: F is a statistical component, not a psychological construct.
