# Experiment 6 final report: adjusting the F model for outcome feedback

Opus 5.5, 2026-10-11. Records: `docs/experiment_06_decisions.md` (X6-F01 to X6-F12, X6-D01 to X6-D08). Protocol: `docs/experiment_06_protocol.md` and its
addendum. F is a statistical component throughout; nothing here identifies it with any psychological construct.

**Status: closed at the population stage under the pre-registered stop rule (X6-D07, X6-D08).** No finite-sample (Stage 1) data were generated.
Hypotheses H6a–H6e were therefore **not tested**. Everything below is a population-level (pseudo-true) result for N_big = 200,000 simulated learners,
not a Monte Carlo verdict.

## 1. Question
Experiment 5 showed that outcome feedback alone is declared F by the 2PL F test, and that F and feedback together inflate σ̂²_F\* by about
+0.24. Experiment 6 asked whether a fitted model that **contains** feedback,
D_t = κ Σ_{s<t, same session, practice} 1{Y_s = 0} exp(−(time_t − time_s)/τ_D) inside the λ bracket, can:
- recover σ²_F\* when F and feedback coexist (E5);
- stop declaring F when only feedback is present (E3, E4);
- keep the F test calibrated and powerful without feedback (E1, E2).

Exact pairwise probabilities under feedback have no closed form. The model therefore uses approximations to the pair-cell probabilities:
- **L0** (X6-D02): mean-field moments, with the direct effect of answer s on answer t exact.
- **L1** (X6-D07): probit linearisation of every earlier error indicator, with the joint latent covariance carried through a row recursion. The direct effect stays exact.

Both are exactly the 2PL model at κ = 0.

## 2. Provenance
- **Code:** `feedback_model/` (fbmodel, fbmodel_l1, etamodel, fit, audit, cli). Tests in `tests/test_feedback_model.py` (7) and `tests/test_feedback_model_l1.py` (15). The full suite has 181 passed, with X3-F06 deselected.
- **Config:** `configs/experiment_06/stage0.yaml`, master seed 20266001, N_big = 200,000, N_J = 6,000, 5 starts, tolerances × 100.
- **Results:**
  - Stage 0 (L0): `results/experiment_06/stage0/`, report `docs/experiment_06_stage0_report.md`, git `f626e93`; 1.7 CPU-h.
  - Stage 0b (L1): `results/experiment_06/stage0b/`, report `docs/experiment_06_stage0b_report.md`; about 2.5 CPU-h. The same datasets were regenerated, and the L0 numbers reproduce exactly.
- **Environment:** `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), OMP/OPENBLAS/MKL threads = 1.
- **Cells:**

  | Cell | F (σ²_F, τ_F) | Feedback (κ, τ_D) |
  |---|---|---|
  | E1 | 0.16, 10 | none |
  | E2 | none | none |
  | E3 | none | −0.25, 10 |
  | E4 | none | −0.10, 2 |
  | E5 | 0.16, 10 | −0.25, 10 |

## 3. Pre-registered gates
- **G0-1 / G0-1b, implementation and approximation accuracy:** the identities, gradients and cells; and, for L1, an excess χ²/df at most ¼ of L0's in E3 and E5 plus a later-practice marginal error ≤ 0.0085.
- **G0-2, schedule-term route (B2+η):** descriptive.
- **G0-3, FB route at population level:**
  - E3: σ²_F\* ≤ 0.02, and E[T_FB] at N = 1000 < 5.16 (the Experiment-4 V2 2PL null q95);
  - E5: |σ²_F\* − 0.16| ≤ 0.03;
  - E1: |σ²_F\* − 0.16| ≤ 0.01 and |κ\*| ≤ 0.02;
  - κ\* within ±20 % in E3 and E5.
- **Stop rule (X6-D04, X6-D07):** if L0 fails G0-3, L1 is built in two gated steps. If L1 also fails, stop and close unless the owner chooses otherwise. The thresholds were never changed.

## 4. Results
### Gates
| Gate | L0 (Stage 0) | L1 (Stage 0b) |
|---|---|---|
| G0-1 / G0-1b | met | met (excess χ²/df ratio L1/L0 0.014–0.023, limit 0.25) |
| G0-2 (B2+η) | removes none of the misattribution (σ²_F\* 0.143 in E3, 0.408 in E5) | — |
| G0-3 | not met (3 of 7 checks fail) | **not met (1 of 7 fails: E3 E[T_FB] at N = 1000 is 27.9 > 5.16)** |

### Approximation accuracy at the true parameters (χ²/df per pair; 1 = exact; feedback-active / cross-session pairs)
| Cell | No feedback term | L0 | L1 |
|---|---|---|---|
| E3 | 5,628 / 4,306 | 156.6 / 115.7 | 4.16 / 2.62 |
| E4 | 14.7 / 12.2 | 1.40 / 1.33 | 0.95 / 0.95 |
| E5 | 4,968 / 3,837 | 159.6 / 94.9 | 4.58 / 2.54 |

E1 and E2 give 0.95–1.04 under every model.

Mean absolute error of the later-practice success rates in E3 / E5:
- without a feedback term: 0.195;
- L0: 0.017;
- L1: 0.004.

### Pseudo-true values (B2 arms)
| Cell | truth σ²_F | 2PL | B2+η | L0 | L1 |
|---|---|---|---|---|---|
| E1 | 0.16 | 0.160 | 0.160 | 0.1596 | 0.1597 |
| E2 | 0 | 0.001 | — | 0.000 | 0.001 |
| E3 | 0 | 0.145 | 0.143 | 0.0204 | **0.0085** |
| E4 | 0 | 0.066 | 0.066 | 0.000 | 0.0014 |
| E5 | 0.16 | 0.415 | 0.408 | 0.2012 | **0.1489** |

| Quantity | Truth | L0 | L1 |
|---|---|---|---|
| κ\* E3 / E5 | −0.25 | −0.262 / −0.257 | −0.252 / −0.251 |
| κ\* E4 | −0.10 | −0.101 | −0.098 |
| τ_D\* E3 / E5 / E4 | 10 / 10 / 2 | 10.97 / 10.69 / 2.01 | 10.35 / 10.30 / 1.99 |
| τ_F\* E5 | 10 | 60.5 | 15.4 |
| τ_F\* E3 (where σ²_F\* > 0) | — | 1000 (bound) | 1000 (bound) |
| σ²_r\* E3 / E5 | 0.0225 | 0.16–0.19 | 0.034 / 0.035 |
| τ_R\* E3 / E5 | 5 | 7.28 / 6.96 | 5.37 / 5.40 |
| sd log λ\* E3 / E5 | 0 | 0.07–0.08 | 0.014 / 0.014 |

### Expected F-test statistic E[T] at N = 1000 (population value × N)
| Cell | 2PL | L0 | L1 |
|---|---|---|---|
| E1 | 587 | 576 | 580 |
| E2 | 0 | 0 | 0 |
| E3 | 1,352 | 29.0 | 27.9 |
| E4 | 21.7 | 0 | 0.03 |
| E5 | 5,716 | 1,989 | 2,291 |

### Precision (Godambe; N = 1000)
- **SE of σ²_F, FB model against 2PL:**
  - L0: 1.04 (E1) and 0.97 (E5);
  - L1: 1.09 (E1), 1.23 (E2) and 1.09 (E5).
- **SE of κ:** L1 0.014 (E3, E5) and 0.047 (E4); L0 0.015 (E3, E5).
- **corr(σ̂²_F, κ̂), L1:** +0.23 to +0.58.
- **Fit cost:** an L1 fit takes 1.7–4.5× a 2PL fit; an L0 fit takes 0.65–2.2×.
- **Identification:** τ_D is not identified when κ ≈ 0 (E1, E2), and the E2 B2-FB fit has a non-positive-definite Hessian under both approximations.

## 5. Interpretation
1. **Modelling feedback removes most of the misattribution; a schedule term removes none.**
   - B2+η leaves σ²_F\* at the 2PL value. This confirms X6-D03: a covariate built from the schedule fits the mean footprint of feedback, not the within-session covariance that F absorbs.
   - Feedback inside the likelihood removes 86 % (L0) and 94 % (L1) of the E3 misattribution.
   - In E5 the bias moves from +0.255 (2PL) to +0.041 (L0) and −0.011 (L1).
   - κ and τ_D are recovered to within 1–4 % (L1) at population level.
2. **The approximation, not the idea, limits the method.**
   - L0's residual came from the covariance it dropped between earlier errors and the latent level. That covariance is first order in κ (erratum X6-D06).
   - The residual showed up as learner-level distortions (σ²_r about 8× the truth, τ_R +40 %, a spread in λ). L1 removes these.
   - What L1 leaves is a small, nearly constant learner-level component in E3: σ²_F\* 0.0085 at τ_F = 1000.
   - **Hypothesis, not tested:** this is the footprint of the correlations L1 ignores between the remainders of earlier errors. These remainders share the learner's level.
   - At N = 1000 this residual is still detectable against the 2PL null: E[T_FB] is 27.9, against 1,352 for the 2PL.
3. **Whether the F test would be calibrated in practice is open.**
   - The pre-registered test (H6a) calibrates T_FB with a warp bootstrap from the fitted no-F model, simulated with the exact feedback generator. The bootstrap would likely carry the same offset, but this was not run.
   - The gate used the 2PL null as a conservative stand-in (X6-F07), and the pre-registered rule closes the experiment on it.
4. **There is a modest precision cost.** L1 costs 9–23 % in the SE of σ²_F without feedback (E1, E2) and in E5. L0 cost none.
5. **Population audits predicted the Experiment 5 numbers.** Here they also located the defect, and a cheap forward-only check graded the next approximation before any fitting.

## 6. Conclusion
**Within this simulation design, fitting outcome feedback inside the pairwise likelihood largely separates feedback from F at population level.**
- **E3 (feedback, no F):** σ²_F\* falls from 0.145 to 0.0085.
- **E5 (F and feedback):** the bias in σ²_F\* falls from +0.255 to −0.011.
- **E1 (F, no feedback):** F is recovered unbiased, at a 9 % SE cost.
- **Parameters:** κ and τ_D are recovered.

The remaining approximation misfit is small in variance but detectable by the F test at N = 1000 against the 2PL null. Under the pre-registered rule this ends Experiment 6 before any finite-sample run. Calibration of the adjusted F test (H6a) and finite-sample bias and power (H6b–H6d) were not tested.

**Recommendation (X6-D08):**
- Experiment 5's recommendation stands for applied use: report the carry-over diagnostic with any F, and do not read a detected F as a latent state.
- A candidate Experiment 7 is the L1 model with a bootstrap-calibrated F test. Its gates would have to be designed for that test, not for the 2PL null. It would be planned by Opus as a fresh protocol, and only if the owner wants it.
- The cost estimate for that experiment must use 1.7–4.5× a 2PL fit per FB fit, not 2×.

## 7. Limitations
- **No finite-sample evidence.** All numbers are pseudo-true values or Godambe predictions at N_big = 200,000, from one dataset per cell. H6a–H6e are untested.
- **Design scope:**
  - λ ≡ 1 in the data;
  - eight templates;
  - exponential feedback driven by errors on practice items inside the λ bracket, with the fitted form equal to the generating form;
  - one (κ, τ_D) per feedback cell.

  Misspecified feedback forms would add bias that this study does not measure.
- **The E[T_FB] gate was a proxy.** It compared T_FB with the 2PL null rather than with its own bootstrap null. X6-F07 noted this before L1 was run and kept the gate unchanged.
- **Approximation residuals are properties of the method.** L1's remaining excess χ²/df is 1.5–3.6 in E3 and E5. It also biases τ_F upward in E5 (15.4 against 10), which no gate tested.
- **Identification:** τ_D is unidentified at κ ≈ 0, which affects the E1/E2 fits and certificates.
