# Experiment 3: final report

**Recovering the shared transient latent state F when item difficulties are unknown**

Final interpretation: Opus, 2026-10-06 (protocol `docs/experiment_03_protocol.md`; decisions X3-D01–X3-D14).
Frozen evaluation: `results/experiment_03/confirmatory/38c681a770/` (branch `exp/unknown-difficulty-recoverability`, commit `2fac473`).

> **Scope.** Statistical results for the simulated Experiment-1 process: a probit model with baseline mastery, slow and fast learning
> gains, and a session-resetting OU state F with σ²_F = 0.16 and τ_F = 10 min unless stated, under an exogenous 4-skill interleaved
> schedule with 48 items. F is a covariance component of that simulation. It is not fatigue, stress, mood, attention, emotion or any
> psychological construct. No real learners were used.

## 1. Question and design (ADEMP)

**Question.** Does the Experiment-1 recovery of σ²_F, and its null test, survive when item difficulties are:
- **(free)** estimated jointly from the same data;
- **(cal)** taken from an external calibration with error (SD 0.2) and treated as known;
- or when items have **unequal discriminations** (λ_q lognormal, mean 1, CV 0.3)?

The known-difficulty Experiment-1 estimator (**known**) is the reference.

**Theory before simulation (protocol §1).** With b free, a white-noise F is exactly confounded with the overall probit scale. So σ²_F
should be identified only through the time-structured covariance, i.e. when τ_F is well above the response spacing (about 0.4–1 min).

**Stage 0 (analytic audit).** With b free, full rank holds at τ_F = 10, with design SE of σ²_F equal to 0.012 at N = 1000. The SE degrades
toward short τ_F and reaches 2.1 at τ_F = 0.2. The free-b SE is *below* the known-b SE for τ_F ≥ 3 because of composite-likelihood pair
dependence (X3-F05, X3-F07): with b known, 97.8 % of the variance of the σ²_F score is item-marginal noise, and freeing b projects it out.

**Confirmatory matrix** (X3-D12; N ∈ {300, 1000}; 20 replications per cell; all arms fitted to the **same** datasets; master seed 20262002):

| cell | process | arms | null bootstrap (free arm) |
|---|---|---|---|
| U1 | F present (τ_F = 10) | known, cal, free | power: 5 per N, B = 19 |
| U2 | F absent | known, cal, free | false positives: 10 per N, B = 39 |
| U3 | F present, τ_F = 1 min | known, free | none |
| U4 | F absent + discrimination misfit | known, free | false positives: 10 per N, B = 39 |
| U5 | F present + discrimination misfit | known, free | power: 5 per N, B = 19 |
| A02 (appendix) | F present, τ_F = 0.2 min | known, free | none; 5 replications at N = 1000 |

## 2. Provenance and validity
| check | result |
|---|---|
| frozen config | sha256 `69ddc7f7c1243c28…` matches X3-D13; no code or config change after the freeze commit `2c087a3` |
| jobs | 205 fits + 1,940 null replicates = **2,145/2,145 ok**, 0 errors, 0 failed replicates; 560 min wall |
| environment | `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), single-thread BLAS, one code hash (`f6ba8c2d…`) in every envelope |
| gates G1–G3 | all ok |

**Deviation X3-F14.** The run used **167 CPU-h**, against the 130 estimate and the 150 cap. Fit jobs averaged 739 s and null replicates
232 s (planned about 374 and 208 s). The frozen matrix ran unchanged; the cap was a planning ceiling that the runner does not enforce.
Contributors cannot be separated from the envelopes: slower free fits at τ_F = 1 and under misfit, and other load on the machine (X3-F13).

**Test suite.** One pre-existing Experiment-1 test fails on this machine because of a build-dependent constant (X3-F06). It is unrelated to these results.

## 3. Pre-registered results (X3-D12, applied exactly as frozen)
| rule | result | verdict |
|---|---|---|
| **PH3a** free-b recovery, U1 | bias +0.007 (MC CI [−0.002, 0.017]) at N = 300; −0.002 ([−0.006, 0.003]) at N = 1000 | **pass**, both N |
| **PH3b** free-b false positives, U2 | 3/20 rejections, CP [0.03, 0.38] | no evidence of excess false positives (rule) |
| **PH3c** misfit, F absent, U4 free | 3/20, CP [0.03, 0.38]; σ̂²_F at 0 in 35 % / 15 % (N = 300 / 1000) | no evidence of excess false positives (rule) |
| **PH3d** misfit, F present, U5 free | bias −0.014 at both N (MC CI excludes 0: attenuation of about 9 %) | **pass**, both N |
| **PH3e** calibration error, paired cal − known | +0.24 / +0.23 (U1, N = 300 / 1000); +0.18 / +0.21 (U2); all MC CIs above 0 | **inflation**, all four cells |
| **PH3f** SD(free)/SD(known), U1 (descriptive) | 0.63 [0.43, 0.97] (N = 300); **0.46 [0.33, 0.64]** (N = 1000); design ratio 0.57 | free more precise; design value inside the CI at N = 1000 |
| **power** (descriptive) | 5/5 in each of U1 and U5 at each N (CP lower bound 0.48 per cell) | detected in 20/20 tested datasets |
| **H3c** (descriptive) | τ_F = 1: free SD 0.076 vs known 0.025 (N = 1000); free bias +0.28, SD 0.55 at N = 300. τ_F = 0.2: free SD 0.89 vs known 0.011 | degradation as predicted |

**Mean σ̂²_F, known / cal / free** (true value 0.16 in U1 and 0 in U2):
- U1: 0.167 / 0.405 / 0.167 (N = 300); 0.154 / 0.384 / 0.158 (N = 1000).
- U2: 0.007 / 0.183 / 0.360 (N = 300); 0.009 / 0.215 / 0.137 (N = 1000).

The free-arm null means are driven by ridge outliers (§4).

## 4. Interpretation

**Supported** (under the simulated assumptions):
1. **Unknown difficulties do not prevent recovering σ²_F when F evolves slowly relative to the answer spacing.** Estimated jointly, σ²_F at
   τ_F = 10 is recovered without material bias, and it is estimated more precisely than with the true difficulties fixed. That is the
   Stage-0 prediction, confirmed (PH3a, PH3f). Detection is 20/20.
2. **Fixing difficulties from an imperfect external calibration manufactures a transient state.** An error SD of 0.2 adds about +0.2 to
   σ̂²_F in every cell (PH3e):
   - with no F at all, σ̂²_F is about 0.2 and τ̂_F near white (0.14–0.19 min);
   - with F present, σ̂²_F is about 0.39 and τ̂_F shrinks to 3–4 min.

   This is the Experiment-1 L6 channel (marginal misfit absorbed by a near-white F) acting at full strength.
3. **With F present, the free-difficulty estimator is robust to unequal item discriminations** (PH3d; bias −0.014). The known-difficulty
   estimator is not: its bias is +0.059 at N = 1000, with SD 0.13.
4. **The §1 non-identification is visible empirically.** With free difficulties, near-white F and F-absent data give ridge solutions:
   τ̂_F 0.2–0.3 min, σ̂²_F up to the 3.0 bound, CLR ≤ 6. The CLR stays small, so the test is not misled by these estimates. A
   free-difficulty σ̂²_F on its own is not interpretable; it needs τ̂_F well above the spacing and the bootstrap test.

**Not established, or open:**
- **Calibration of the free-difficulty null test.** By the pre-registered rule there is "no evidence of excess false positives" in U2 and
  U4 separately. But the observed rate is 15 % in both, and pooled over the two null scenarios it is 6/40, CP [0.057, 0.30]. That pooled
  view was not pre-registered and is exploratory. The test is **not** shown to hold its 5 % level and may be liberal at these N and B.
- **The known-difficulty estimator under discrimination misfit with F absent (U4-known; descriptive, no test run).** 12 of 40 fits give
  σ̂²_F > 0.1 (8 at N = 300, 4 at N = 1000), with CLR 389–6,316 and τ̂_F 0.05–0.47 min. Experiment-1 known-difficulty null distributions
  have q95 of about 100, so these would very likely be false detections. A known-difficulty F model cannot tell this misfit from a
  genuine near-white F (compare appendix A02).
- **Scope.** Only λ CV 0.3, calibration SD 0.2, τ_F ∈ {0.2, 1, 10} and this schedule were tested. Nothing about real learners or any
  psychological meaning of F.

## 5. Limitations
- Twenty replications per cell. Null tests ran on 20 datasets per null scenario, with B = 39 (minimum p 0.025) and a discrete p-value.
- No known-difficulty null tests (cut for cost). The U4-known finding is therefore descriptive.
- Pairwise composite likelihood only. Discriminations were not estimated (no 2PL model). Item misfit was limited to discrimination.
- The cost overrun (X3-F14) did not change the design.

## 6. Recommendations (not acted on)
1. Before any applied use, check the free-difficulty null test's calibration: more null datasets (e.g. ≥ 100) with B ≥ 99 at N = 300/1000.
2. Estimate difficulties jointly rather than fixing external values.
3. Treat any known-difficulty or near-white (τ̂_F below the answer spacing) F finding as uninterpretable without misfit checks.
4. A model with item discriminations (2PL) is the natural next extension; it would need its own protocol.

---

**Addendum note (2026-10-08; the registered text above is unchanged).** The calibration study (`docs/experiment_03_addendum_calibration.md`,
X3-D17) shows that the free-difficulty null test is **liberal under item-discrimination misfit** (about 13 % at nominal 5 % pooled, 17 % at
N = 1000). Under the clean null its level is inconclusive (0.10, CI [0.035, 0.155]). Large detections are unaffected.

