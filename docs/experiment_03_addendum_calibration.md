# Experiment 3 addendum: calibration of the free-difficulty null test

Opus interpretation, 2026-10-08. Decisions X3-D15 (question, method, rules), X3-D16 (freeze), X3-F17 and X3-D17 (this addendum).
Results: `results/experiment_03/calibration/01f57a2b78/`. **Experiment 3's registered results and verdicts are unchanged.**
F is a statistical component of the simulation, not a psychological construct.

## 1. Question
In Experiment 3, the boundary-aware parametric-bootstrap test of σ²_F = 0 with **free item difficulties** rejected 3/20 null datasets in
U2 (clean) and 3/20 in U4 (discrimination misfit). The pre-registered rule said "no evidence of excess false positives", but with 20
datasets per scenario it could not tell 5 % from 15 %. This addendum estimates the test's actual level at nominal 5 %.

## 2. Method
**Warp-speed Monte Carlo** (Giacomini, Politis & White, 2013). For each of R fresh null datasets:
1. the observed statistic T = CLR = 2(ℓ_B2 − ℓ_B1), from free-difficulty fits;
2. **one** bootstrap statistic T*, from the dataset's fitted B1-free null, using the same code path as the registered test.

The level is estimated as α̂ = the share of T above the 95 % quantile of all T* (strict ">", matching the registered p-value). Its 95 % CI
comes from a pairs bootstrap over datasets (2,000 draws). This estimates the test's level as B → ∞; the registered B = 39 test differs
only by discreteness.

**Cells:**
- C2 = U2 (F absent, clean);
- C4 = U4 (F absent, item discriminations lognormal with CV 0.3);
- N ∈ {300, 1000}, 100 datasets per cell (400 in total), master seed 20262101 (new; the confirmatory datasets are not reused).

**Frozen rules (pooled over N primary; per N secondary):**
- **liberal** if the CI lies entirely above 0.05;
- **consistent with 5 %** if the CI contains 0.05 and its upper limit is ≤ 0.10;
- otherwise **inconclusive**.

**Gate:** a cell is not evaluable if more than 5 % of its jobs failed or did not converge.

## 3. Provenance
| check | result |
|---|---|
| frozen config | `configs/experiment_03/addendum_calibration.yaml`, sha256 `15b17af3…` matches X3-D16 |
| code | one code hash (`cbb3ad29…`) in all 400 envelopes, identical to the committed code at `c9a0786`; no code or config change since |
| environment | `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), single-thread BLAS |
| jobs | 400/400 ok; 0 failed fits; 0 failed bootstrap replicates; all converged; gate passed |
| notes | The run started before the implementation was committed (manifest: git `693f616`, dirty tree). The code that ran is nonetheless identical to `c9a0786`, by code hash. CPU use was 45.1 h against the 33.3 h dry-run (406 s per dataset against 297), under the enforced 100 CPU-h cap. |

## 4. Results
| scenario | cell | α̂ at nominal 5 % | 95 % CI | verdict (frozen rule) |
|---|---|---|---|---|
| C2, clean null | **pooled** | 0.100 | [0.035, 0.155] | **inconclusive** |
| | N = 300 | 0.070 | [0.020, 0.150] | inconclusive |
| | N = 1000 | 0.130 | [0.030, 0.230] | inconclusive |
| C4, discrimination misfit | **pooled** | **0.130** | **[0.085, 0.225]** | **liberal** |
| | N = 300 | 0.140 | [0.030, 0.250] | inconclusive |
| | N = 1000 | **0.170** | **[0.100, 0.280]** | **liberal** |

**Descriptive** (data T against bootstrap T*):
| | KS p | T = 0 share | 95 % quantile | α̂ at 10 % / 1 % |
|---|---|---|---|---|
| C2 pooled | 0.33 | 0.12 / 0.15 | 5.7 / 4.0 | 0.14 / 0.04 |
| C4 pooled | **0.003** | 0.07 / 0.17 | 7.6 / 3.8 | 0.21 / 0.09 |
| C4, N = 1000 | **0.001** | 0.05 / 0.12 | 8.0 / 4.3 | 0.24 / 0.14 |

The ridge share (σ̂²_F > 0 with τ̂_F < 0.4 min) is about 16 % in both the data and the bootstrap.

## 5. Interpretation
1. **Under item-discrimination misfit, the free-difficulty null test is liberal** (frozen rule). It rejects about 13 % of null datasets
   at nominal 5 %, and about 17 % at N = 1000.
   - **Mechanism:** the parametric bootstrap simulates from the fitted model, which assumes equal discriminations. The extra short-lag
     covariance that unequal discriminations create in the data is therefore missing from the null, and part of it is read as F. The
     data statistics are visibly larger than the bootstrap ones (KS p = 0.003).
   - Experiment 3's registered PH3c verdict ("no evidence of excess false positives", 3/20) stands as registered. That test was
     underpowered, and this addendum shows the excess.
2. **Under a correctly specified null, calibration is not established** (inconclusive). The point estimate is 0.10 and the CI includes
   0.05 but extends to 0.155. The test may be mildly liberal in finite samples; this run cannot decide it.
3. **Practical consequence.** A free-difficulty test statistic just above its bootstrap critical value is **not** evidence of F if
   discrimination misfit is plausible.
   - Experiment 3's detections (statistics 150–720) are unaffected: null statistics, even inflated by misfit, stayed below about 10.
   - Marginal results need a misfit-robust null, for example a bootstrap from a model that also estimates item discriminations (2PL).
     That is the natural next experiment.

## 6. Limitations
- 100–200 datasets per cell, so the CIs are wide, especially per N. The clean-null verdict is inconclusive for that reason.
- Only one misfit level (λ CV 0.3) and the Experiment-1 schedule and parameters were tested.
- Warp-speed estimation assumes the bootstrap statistic's distribution varies smoothly across datasets. That is standard, but it is an assumption.
