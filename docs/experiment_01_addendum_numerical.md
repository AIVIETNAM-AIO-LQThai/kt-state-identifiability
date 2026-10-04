# Experiment 1: numerical-validation addendum

**Saved near-null certificate warnings in the bootstrap null test**

Opus interpretation, 2026-10-05. Protocol: `docs/experiment_02_protocol.md` §7. Decisions: X2-D07, X2-D17–X2-D19, X2-F13–X2-F15.

This addendum **does not replace** any registered Experiment-1 result, rule or verdict. It checks the 140 certificate warnings
saved among the 4,720 null-bootstrap replicates (109 `newton_decrement_large` and 31 `hessian_not_pd`, all on B2, none on B1).
It does so on a fixed, deterministic selection of 53 datasets. This is a targeted validation, **not** a new estimate of warning
prevalence or test size.

## 1. What was checked

**Selection** (deterministic, `results/experiment_01_addendum/run3/selection.json`):
- **Tier A:** all 32 warned S1/S8 replicates. These are the only ones that could bear on a registered verdict (PH2).
- **Tier B:** 20 S2/S8n datasets:
  - the 5 warned replicates with the highest saved CLR;
  - 5 non-PD replicates, stratified by cell;
  - 5 unwarned near-null controls;
  - 5 unwarned controls with the largest σ̂²_F.
- **Tier C:** the main fit S8n N=1000 rep 13, which missed the decrement tolerance.

**Per dataset:**
1. Regenerate the data from the recorded B1 parameters and seed keys, and re-run the registered B1/B2 searches (reproduction check).
2. Check the projected gradient and active bounds (KKT).
3. Compute Hessian eigenvalues at finite-difference steps 1e-4, 1e-5 and 1e-6.
4. Profile τ_F over 11 log-spaced values in [0.05, 1000], re-optimising everything else from 2 starts.
5. Re-check B1 from 2 jittered starts.
6. Record the attained improvement and its effect on the affected p-value.

A finite profile gives an **attained** improvement, not a bound on the global one.

## 2. Provenance: three runs, one valid

| run | interpreter | BLAS threads | reproduces registered fits | status |
|---|---|---|---|---|
| 1 (commit `584ac96`) | system Python, numpy 2.5.1 | multithreaded (default) | 2/53 | record only (X2-F13) |
| 2 (`run2/`) | `.venv12`, numpy 2.5.3, exact Experiment-1 versions | multithreaded (default) | 2/53, **bitwise identical to run 1** | record only (X2-F15) |
| **3 (`run3/`)** | `.venv12`, numpy 2.5.3 | **single-threaded** (set before Python starts) | **53/53, exact** | **the result interpreted here** |

The data always reproduced: the fingerprints of 4 datasets match exactly in runs 2 and 3. What differed was the optimiser endpoint.

**Root cause (X2-F15).** Experiment 1 ran through `kt_trial/cli.py`, which sets `OMP/OPENBLAS/MKL_NUM_THREADS=1` at import time,
before numpy loads, so every worker used single-threaded BLAS. The Experiment-2 CLI (`transient_filtering/cli.py`) does not. Setting
the variables inside a worker process happens after BLAS has initialised, so it has no effect.

Multithreaded BLAS changes floating-point summation order. In well-identified directions that only moves results at about the 1e-7
level. Along the flat near-null τ_F direction, it moves L-BFGS to a different endpoint: up to 0.2 in CLR, and from 0.024 to 0.094 in one replicate.

A direct check confirmed the cause. One replicate (`S8 N=300 rep 8 b13`) re-run through the original Experiment-1 code gives:
- CLR 0.02423751074820757 (registered: identical) with single-threaded BLAS;
- CLR 0.0944 with the default.

My earlier diagnosis in H13 (numpy 2.5.1 against 2.5.3) was **wrong**. Runs 1 and 2 differ only in the numpy version, and they are bitwise identical.

## 3. Results (run 3; all 53 datasets reproduce the registered values exactly)

| group | n | attained B2 improvement (log-lik): max / median | n > 0.01 | B1 improvement (max) | non-PD at some FD step | p-values changed |
|---|---|---|---|---|---|---|
| A: warned S1/S8 replicates | 32 | 0.120 / 0.010 | 16 | 3e-8 | 6 | **0** |
| B: highest-CLR warned S2/S8n | 5 | 0.102 / 0.064 | 4 | 3e-8 | 2 | **0** |
| B: non-PD S2/S8n | 5 | 0.019 / 0.009 | 2 | — | 5 | **0** |
| B: unwarned near-null controls | 5 | **0** / 0 | 0 | — | 0 | **0** |
| B: unwarned, largest σ̂²_F | 5 | **0** / 0 | 0 | — | 0 | **0** |
| C: main fit S8n N=1000 rep 13 | 1 | 0.030 | 1 | 1e-8 | 0 | n/a |

What the table shows:
- **The warnings were informative.** Every attained improvement occurs in a warned fit. The 10 unwarned controls could not be improved at all.
- **The improvements are small.** The largest is 0.12 log-lik units, i.e. a change in CLR\* of at most 0.24. They sit along the flat τ_F direction, with the best profile τ_F at a bound (0.05 or 1000 min) in 22 of 32 Tier-A and 11 of 20 Tier-B datasets, and σ̂²_F ≤ 0.024.
- **B1 is correctly optimised.** The largest B1 improvement is 3e-8. Under-optimising B2 only can make CLR\* too small, never too large, so the p-values could only rise.
- **No registered verdict changes.**
  - The largest improved CLR\* in Tier A is 6.3, while the smallest observed CLR in any S1/S8 cell is 188. Every PH2 rejection stands.
  - In Tier B the p-values of the affected S2/S8n datasets are unchanged (for example 0.61 → 0.61), so PH3 and PH4 stand.
  - 0 of 52 p-values changed.
- **The Newton decrement is not a bound.** In Tier A the attained improvement **exceeded** the decrement estimate in 13 of 26 fits with a finite decrement. This confirms errata E3. In Tier C the attained gain was 0.030 against an estimate of 0.044; σ̂²_F = 0.0008. The D30 adjudication (immaterial) stands.

## 4. Conclusion

The 140 saved warnings mark B2 null-bootstrap fits that stopped slightly short along a nearly flat τ_F direction when σ̂²_F ≈ 0.
The under-optimisation is real but tiny: at most 0.12 log-lik in this sample. It has no effect on any registered p-value or verdict
of Experiment 1. The registered data and fits are reproduced exactly, provided the computation uses single-threaded BLAS.

**Reproducibility requirement (new).** Bitwise reproduction of Experiment-1 fits needs the Experiment-1 environment **and**
single-threaded BLAS (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` and `MKL_NUM_THREADS` all set to 1 before Python starts).

**Recommendation (not acted on).** `transient_filtering/cli.py` should set the same thread variables at import, as
`kt_trial/cli.py` does. The Experiment-2 cloud run used multithreaded BLAS. Its frozen results are statistically unaffected
(filters and SMC involve no optimisation), but bitwise re-execution of them needs the same thread setting. This is a code change for a later Sonnet step.

## 5. Files
- `results/experiment_01_addendum/run3/`: `selection.json`, `per_dataset/*.json` (each records its interpreter and versions), `summary.{json,md}`.
- Records: run 1 (`results/experiment_01_addendum/{datasets/, summary.*, fingerprint_pc.json}`) and run 2 (`run2/`).
- Configs: `configs/experiment_01_addendum/addendum.yaml` (run 1), `addendum_run2.yaml` (sha256 `2714bca1…34af`) and `addendum_run3.yaml` (sha256 `5b1d0a7c…d66a`). They differ only in `out_dir` and the header comment.
