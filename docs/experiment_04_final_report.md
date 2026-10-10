# Experiment 4 final report: recovery of F and calibration of the null test with unknown item discriminations (2PL)

Opus 5.5, 2026-10-10. Decision records X4-F16 and X4-D11 in `docs/experiment_04_decisions.md`. F is a statistical component, not a psychological construct.

## 1. Question
Experiment 3's calibration addendum found the free-difficulty (1PL-free) null test of σ²_F = 0 **liberal** under item-discrimination misfit: α̂ 0.130 [0.085, 0.225] from 200 datasets.

Experiment 4 estimates the discriminations instead (2PL):

Z = −b_q + λ_q(M0 + αH^s + rH^f + F) + ε, with the geometric mean of λ fixed at 1 (113 parameters).

It asks whether this:
- (a) recovers the scaled variance σ²_F\* = g²σ²_F without bias;
- (b) calibrates the null test.

## 2. Provenance
| check | result |
|---|---|
| frozen config | `configs/experiment_04/stage_confirmatory.yaml`, sha256 `4d3704f9…ecce8` (X4-D10), master seed 20264101 |
| code | one code hash, `824f77ed3217`, in all 435 envelopes, identical to the freeze; committed as `4c01948` |
| environment | `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), single-thread BLAS |
| jobs | 435 of 480 ran: **435 ok, 0 errors**. The enforced 200 CPU-h cap stopped the run at 209.6 CPU-h; jobs already in flight finished |
| coverage | V1 and V5 recovery: 20 replications × N {300, 1000}, complete. V2: 50 per N, complete. **V4: 128 (N = 300) + 127 (N = 1000) of 150 + 150.** The rep-major order kept N balanced |

**Notes:**
- The run started from a dirty tree (manifest git `ae73782`). By code hash, the code that ran is identical to `4c01948`.
- The projection of 154 CPU-h underestimated the full-load cost by about 35 %.

Results: `results/experiment_04/confirmatory/88d74ed991/` (`summary.md`, `summary.json`, `rules.json`).

## 3. Frozen rules (X4-D08 + X4-D09)
| gate / rule | result |
|---|---|
| G1: ≤ 5 % failed or non-converged per cell and estimator | pass everywhere (recovery 0 %; V2 2PL 1/100; V4 2PL 2/255; V4 1PL-free 0/255) |
| G2 (single code hash), G3 (single-thread BLAS), no job errors | pass |
| **PH4a**: 2PL bias against σ²_F\* within ±0.04 | **supported** |
| **PH4b**: V4 (misfit null) 2PL calibration, paired Δ | **inconclusive** |
| **PH4c**: V2 (clean null) 2PL calibration | **inconclusive** |
| PH4d, PH4e | descriptive |
| ridge sensitivity (X4-D09, δ = 0.25) | no verdict and no α̂ changes; nothing "fragile" |

## 4. Results
### Recovery (PH4a, PH4d, PH4e)
Bias of σ̂²_F against σ²_F\* (mean [MC CI]):

| cell | 2PL | 1PL-free |
|---|---|---|
| V1 (λ ≡ 1), N = 300 | −0.004 [−0.013, 0.005] | +0.005 [−0.005, 0.016] |
| V1, N = 1000 | −0.002 [−0.008, 0.003] | −0.000 [−0.006, 0.005] |
| V5 (λ CV 0.3), N = 300 | −0.017 [−0.024, −0.011] | −0.009 [−0.016, −0.002] |
| V5, N = 1000 | +0.002 [−0.003, 0.007] | −0.001 [−0.007, 0.004] |

- **Spread (V1):** SD(2PL)/SD(1PL-free) of σ̂²_F is 0.86 [0.79, 0.96] at N = 300 and 1.06 [0.95, 1.17] at N = 1000.
- **Paired error difference, 1PL-free − 2PL (V5):** +0.009 [0.003, 0.014] at N = 300; −0.003 [−0.005, −0.001] at N = 1000.
- **Discrimination recovery:** RMSE of centred log λ is 0.28 (V1) and 0.30 (V5) at N = 300, and 0.15 and 0.16 at N = 1000, matching the Stage-0 design SEs.
- **Power:** in the F-present recovery datasets the 2PL test rejected in 80 / 80 (T above the same-N null 95 % quantile).

### Calibration (PH4b, PH4c)
α̂ at nominal 5 % (pairs-bootstrap 95 % CI):

| set | datasets (ok) | 2PL | 1PL-free |
|---|---|---|---|
| V4 pooled (primary) | 255 (253 / 255) | 0.075 [0.040, 0.119] | 0.075 [0.031, 0.129] |
| V4, N = 300 | 128 | 0.086 [0.039, 0.195] | 0.086 [0.031, 0.211] |
| V4, N = 1000 | 127 | 0.056 [0.024, 0.120] | 0.063 [0.008, 0.157] |
| V2 pooled | 100 (99) | 0.111 [0.010, 0.202] | – |
| V2 + V4 pooled (2PL, descriptive) | 355 (352) | 0.082 [0.048, 0.122] | – |

- **Paired Δ = α̂(1PL-free) − α̂(2PL), V4:** **+0.004 [−0.051, +0.051]** (253 datasets).
- **Descriptive, V4 pooled (2PL / 1PL-free):**

  | statistic | 2PL | 1PL-free |
  |---|---|---|
  | α̂ at 10 % | 0.119 | 0.137 |
  | α̂ at 1 % | 0.032 | 0.020 |
  | KS p, T vs T\* | 0.003 | 0.004 |
  | T = 0 share (data / T\*) | 0.19 / 0.29 | 0.11 / 0.15 |

- **Descriptive, V2:** KS p = 0.58; α̂ 0.15 at 10 % and 0.02 at 1 %.
- **Ridge fits (2PL, `converged_on_ridge`):**
  - V4: 18 of 255 units (11 observed fits, 8 bootstrap fits);
  - V2: 4 of 100;
  - none in the recovery fits, and none for 1PL-free.

## 5. Interpretation
1. **Recovery: supported.** Under discrimination misfit (λ CV 0.3), **both** estimators recover σ²_F\* without material bias.
   - 2PL costs nothing in bias or variance at N ≥ 300, despite 47 extra parameters.
   - It recovers the discriminations at design precision.
   - Its largest bias (V5, N = 300, −0.017) is well inside ±0.04.
2. **Calibration: unresolved for both estimators, and 2PL is not shown to help.** Neither test is shown to be liberal on fresh data, and the paired difference is essentially zero. The claim "2PL removes 1PL-free's miscalibration" cannot be made.
3. **The Experiment 3 finding that motivated this experiment does not replicate at its strength.**
   - The generator and estimator are identical (C4 = V4; `fit_free` unchanged).
   - 1PL-free gives 0.075 [0.031, 0.129] on 255 fresh datasets, against 0.130 [0.085, 0.225] in the X3 addendum. At N = 1000 it is 0.063 against 0.170.
   - The CIs overlap. A descriptive count over both runs gives about 45 / 455 = 0.10.

   The most plausible reading: the test is **mildly** liberal (true level roughly 0.07–0.10), and the X3 estimate sat at the high end of sampling variation. That result triggered this experiment, which is a winner's-curse pattern. The X3 addendum is frozen and unchanged; this report is the cross-reference.
4. **A common, mild pattern (descriptive only).** Every α̂ point estimate exceeds its nominal level, for both estimators and both nulls, and in V4 the observed T is stochastically larger than T\*.
   - This suggests a slight anti-conservativeness of the parametric-bootstrap CLR test that is **not specific to discriminations**.
   - One candidate cause: the fitted-null plug-in ignores the estimation error of 100+ nuisance parameters.
   - The frozen rules do not establish it.
5. **The ridge rule drove no verdict, but it did decide evaluability.**
   - Both sensitivity analyses leave every verdict and every α̂ unchanged.
   - Without X4-D09, 7.8 % of V4 2PL units would have been non-converged, and PH4b would have been "not evaluable" under G1.
   - X4-D09's threshold (0.01) was set after the re-pilot case and before this run.

## 6. Conclusion and recommendation
- **2PL is a safe default for estimating σ²_F when item discriminations may vary.** It has no bias or variance cost at N ≥ 300.
- **For testing σ²_F = 0, treat bootstrap p-values near 0.05 as weak evidence under either estimator.** The actual level is plausibly 7–10 %. In this design the F-present signal is far from that margin (power 100 %).
- **No top-up run (X4-D11).** Completing V4 to 300 per N would leave both calibration verdicts inconclusive. A decisive calibration study needs roughly 1,000+ datasets per estimator (500+ CPU-h); it is recorded as a possible future item only.

## 7. Limitations
- τ_F = 10 only and λ CV 0.3 only; a larger discrimination spread is untested.
- 20 recovery replications per cell (bias CIs about ±0.006–0.01).
- Calibration power is limited by the X3-D15 rule (X4-F12): P("consistent" | exactly calibrated) is about 0.5–0.6 at this size.
- V4 reached 255 of the planned 300 datasets. The cap stop is ignorable because it was not driven by outcomes.
