# Experiment 5 final report: outcome-driven dynamics versus the transient state F

Opus 5.5, 2026-10-11. Records: `docs/experiment_05_decisions.md` (X5-F08 to X5-F10, X5-D09). Protocol: `docs/experiment_05_protocol.md`.
F is a statistical component throughout; nothing here identifies it with any psychological construct.

## 1. Question
Experiments 1–4 test for a session-resetting latent state F with T = 2(ℓ_B2 − ℓ_B1). Within-session dependence can also arise from
**outcome feedback**: an error shifts the following answers, D_t = κ Σ_{s<t, same session, practice} 1{Y_s = 0} exp(−(t−s)/τ_D)
inside the λ bracket. Experiment 5 asks:
- **H5a.** Does the F test "detect F" when only feedback is present?
- **H5b–H5d.** Can a carry-over score test detect feedback with power and at the right level? It uses random template assignment as the identifying contrast, and is a Godambe-adjusted composite-likelihood score test of η = 0 for the covariate "recent error load", τ_x = 2.
- **H5e.** How much is σ̂²_F\* inflated when F and feedback coexist?

## 2. Provenance
- **Run:** `results/experiment_05/confirmatory/5a3afdf728/`, run by the owner from 2026-10-10 10:15 UTC.
  - 620/620 jobs ok, 0 errors.
  - 533 min wall, **158.6 CPU-h** (cap 210; dry-run projection 193.9 with ×1.4).
- **Config:** `configs/experiment_05/stage_confirmatory.yaml`, frozen, sha256 `64a7b402…b730ee`, master seed 20265101.
- **Code:** hash `70990fcf…46fe` (equals the freeze, X5-D08). Git `1ff4ad2`, manifest `dirty: false`.
- **Environment:** `.venv12` (python 3.12.10, numpy 2.5.3, scipy 1.18.1), OMP/OPENBLAS/MKL threads = 1.
- **Matrix** (λ ≡ 1, 2PL fits with the X4-D08/D09 polish and ridge rule, N ∈ {300, 1000}, rep-major):

  | Cell | Generating model | Datasets per N |
  |---|---|---|
  | E1 | F, no feedback | 75 |
  | E2 | null | 75 |
  | E3 | no F, κ −0.25, τ_D 10 | 30 |
  | E4 | no F, κ −0.10, τ_D 2; warp units with one bootstrap T\* each | 50 |
  | E5 | F + κ −0.25, τ_D 10 (= S7) | 30 |
  | E6 | no F, lognormal gains (S8n) | 50 |

- **Summary files:** `summary.md`, `summary.json` and `rules.json` (frozen rules version X5-D06+D07). The heading "Provisional rules (X5-D06)" in `summary.md` is a stale label from the summarizer. The verdicts were computed by the frozen rules.

## 3. Frozen rules (X5-D06 + X5-D07)
- **Gates:**
  - G1: ≤ 5 % failed or non-converged B2 fits, failed bootstrap replicates, or diagnostic errors per cell and N.
  - G2: single code hash and frozen sha.
  - G3: single-thread BLAS.
- **H5a:** E3 N = 1000, share of T above the Experiment-4 V2 2PL q95. "Supported" if the CP 95 % lower bound is > 0.5; "not supported" if the CP upper bound is < 0.5. E3 N = 300 is secondary and E4 descriptive.
- **H5b:** E3 and E5 at N = 1000, diagnostic rejection share ≥ 0.8 with CP lower > 0.5.
- **H5c:** E1 + E2 pooled; "consistent with 5 %" if the CP CI contains 0.05 and has an upper limit ≤ 0.10; "liberal" if the lower limit is > 0.05; otherwise "inconclusive".
- **H5d:** E6, with the H5c rule.
- **H5e:** E5 bias of σ̂²_F\* against 0.16, descriptive.

## 4. Results
### Gates and fit health
G1 holds in all 12 cells, with 0 bad fits and 0 bad bootstrap replicates. G2 and G3 hold. Every B2 fit converged.
- **Ridge-converged fits:** 14, all in cells without feedback signal: E2 6 + 5, E4 N = 300 1, E6 N = 300 2.
- **Bound hits:** τ_R sits at its upper bound in 60/60 E3/E5 fits. τ̂_F is at the 1000 bound in 16/30 and 15/30 E3 fits.

### Verdicts
| Rule | Verdict | Evidence |
|---|---|---|
| **H5a** misattribution | **supported** | E3: 30/30 above the q95 at N = 1000 (CP [0.884, 1]) and at N = 300. T ranges from 941 to 1661 (N = 1000) and from 176 to 527 (N = 300), against q95 of 5.16 and 4.23 |
| **H5b** diagnostic power | **supported** | 30/30 in E3 and in E5 at both N (CP [0.884, 1]); also 30/30 at the secondary τ_x 5 and 10 |
| **H5c** diagnostic level | **inconclusive** | E1 + E2: 22/300 = 0.073, CP [0.047, 0.109] |
| **H5d** level under gain misfit | **inconclusive** | E6: 7/100 = 0.070, CP [0.029, 0.139] |
| **H5e** bias with both | descriptive | E5 bias **+0.241** (MC CI [0.222, 0.259]) at N = 300 and **+0.244** ([0.234, 0.253]) at N = 1000; Stage-0 prediction +0.25 |

### Per cell (primary τ_x = 2, diagnostic at the B2 fit)
| Cell | σ²_F\* (true) | Mean σ̂²_F | Median τ̂_F | F test: share T > q95 | Diagnostic rejections | Mean η̂ |
|---|---|---|---|---|---|---|
| E1 N=300 | 0.16 | 0.153 | 10.3 | 75/75 | 8/75 | +0.001 |
| E1 N=1000 | 0.16 | 0.155 | 10.4 | 75/75 | 8/75 | −0.007 |
| E2 N=300 | 0 | 0.087 | 6.2 | 6/75 | 4/75 | −0.012 |
| E2 N=1000 | 0 | 0.115 | 4.2 | 5/75 | 2/75 | +0.002 |
| E3 N=300 | 0 | 0.145 | 1000 | 30/30 | 30/30 | −0.276 |
| E3 N=1000 | 0 | 0.147 | 769 | 30/30 | 30/30 | −0.275 |
| E4 N=300 | 0 | 0.107 | 2.1 | 40/50 | 17/50 = 0.34 [0.21, 0.49] | −0.095 |
| E4 N=1000 | 0 | 0.075 | 2.2 | 49/50 | 32/50 = 0.64 [0.49, 0.77] | −0.083 |
| E5 N=300 | 0.16 | 0.401 | 38.1 | 30/30 | 30/30 | −0.287 |
| E5 N=1000 | 0.16 | 0.404 | 37.1 | 30/30 | 30/30 | −0.252 |
| E6 N=300 | 0 | 0.104 | 2.0 | 1/50 | 3/50 | −0.006 |
| E6 N=1000 | 0 | 0.003 | 2.0 | 0/50 | 4/50 | +0.008 |

The "F test" column counts datasets with T above the Experiment-4 V2 q95; the per-cell figures come from the 2×2 tables in `rules.json`.

- **E2 σ̂²_F:** the means are pulled up by near-white ridge fits (τ̂_F < 0.4 in 15/75 at each N), while the median T is 0.79 and 0.61.
- **E4 against its own bootstrap T\*** (warp-speed, pairs-bootstrap CI): α̂ is 0.72 [0.50, 0.98] at N = 300, 0.96 [0.90, 1.00] at N = 1000, and 0.83 [0.72, 0.93] pooled. The T\* q95 is 5.43 and 6.15, close to the Experiment-4 reference values of 4.23 and 5.16.

### E4: F test × diagnostic (datasets)
| | F only | Diagnostic only | Both | Neither |
|---|---|---|---|---|
| N = 300 | 26 | 3 | 14 | 7 |
| N = 1000 | 18 | 1 | 31 | 0 |

### Stage-0 predictions against the confirmatory run
| Quantity | Predicted (population audit, X5-F02) | Observed |
|---|---|---|
| E3 σ²_F\* | 0.144 | 0.145 / 0.147 |
| E4 E[T] (N = 1000) | 20.7 | median 23.5 |
| E4 diagnostic power | 0.27 / 0.68 | 0.34 / 0.64 |
| E5 σ²_F\* | 0.413 (bias +0.25) | 0.401 / 0.404 (bias +0.24) |
| E1/E2/E6 diagnostic noncentrality | ≈ 0 | see H5c, H5d |

## 5. Interpretation
1. **A significant F test is not evidence of a latent transient state** (H5a).
   - Feedback with no F at all is declared F in every dataset at S7 strength.
   - The weakest pre-registered feedback (κ −0.10, τ_D 2) is declared F in 98 % of datasets at N = 1000 against the reference q95, and in 96 % against its own bootstrap null.
   - The F component absorbs positive within-session serial dependence of any origin. Its fitted time constant follows the feedback rather than revealing a separate state: τ̂_F ≈ 2.1 ≈ τ_D in E4, and τ̂_F at the bound in E3, which is a session-level shift. The recency kernel τ_R is pushed to its bound in every feedback fit.
   - This extends the Experiment 1 S7 finding (a 3-replication bias of +0.145) from bias of σ̂²_F to false detection of F.
2. **The carry-over diagnostic separates feedback from F when feedback is strong** (H5b).
   - Power is 1.00 at both N and at all three τ_x, and η̂ tracks κ (−0.28 at κ −0.25; −0.09 at κ −0.10).
   - In E5 the diagnostic flags all 30/30 datasets where σ̂²_F is inflated about 2.5× (+0.24, H5e). So it signals exactly when σ̂²_F must not be read as the variance of a latent state.
3. **The two tests are asymmetric when feedback is weak.**
   - In E4 the F test fires far more often than the diagnostic: 98 % vs 64 % at N = 1000, and 80 % vs 34 % at N = 300.
   - At N = 300, 26/50 datasets show "F only".
   - A non-rejecting diagnostic therefore does not rule out feedback as the source of a detected F, least of all at N = 300.
4. **The diagnostic's level is not established** (H5c inconclusive).
   - The pooled rate is 0.073. The pre-registered operating characteristics predicted "inconclusive" for a true level near 0.07.
   - **Exploratory (X5-F10, not pre-registered; `scripts/experiment_05_level_check.py`):** the excess is confined to E1, where F is present: 16/150 = 0.107, CP [0.062, 0.167]; P(X ≥ 16 | 0.05) = 0.004. E2 has 6/150 = 0.040 and is mildly conservative (mean S 0.89 and 0.81).
   - In E1 the mean S is 1.36 and 1.17 and its variance about 3.3, against 1 and 2 for χ²₁. Yet the p-values are not grossly non-uniform (KS p = 0.38), and p < 0.01 occurs 2/150 times.
   - The rejection count does not grow with N (8/75 at both), and η̂ has no consistent sign (3−/5+ at N = 300, 7−/1+ at N = 1000).
   - The most plausible reading is a finite-sample overdispersion of the Godambe-adjusted statistic when F's nuisance parameters are estimated, not a population confound. The Stage-0 noncentrality was ≈ 0.
   - Practical consequence: in data with a real F, diagnostic p-values between 0.01 and 0.05 are weak evidence of feedback. Strong feedback gives S in the hundreds and is unaffected.
5. **Gain misfit (S8n) does not trigger the F test** (1/50 and 0/50 datasets above the q95). The diagnostic's false-alarm rate there is 0.07 and cannot be told apart from 0.05.
   - The H5d rule had little resolution at 100 datasets: "consistent" requires k ≤ 4, while the expected k at a true level of 0.05 is 5.
   - Operating characteristics were pre-computed for H5c only. This is a protocol lesson, not a finding.
6. **The Stage-0 population audit predicted every headline number.** It is validated as a planning tool for this model class, as it was in Experiment 4.

## 6. Conclusion and recommendation
Within this simulation design, **the F test detects within-session dependence, not a latent state.** Outcome feedback alone produces a "significant F" with a plausible variance and a time constant that mimics the feedback decay. When F and feedback coexist, σ̂²_F\* is inflated by about +0.24 (2.5×).

The schedule-based carry-over score test identifies strong feedback reliably. It is weaker than the F test for weak, short feedback. Its level is close to nominal without F and somewhat liberal (≈ 0.10) with F at these sample sizes.

**Recommendation (X5-D09):**
- Any reported F should be accompanied by the carry-over diagnostic, and requires a design with randomised item order.
- A detected F should not be interpreted as a latent state unless the diagnostic is clearly non-significant and N is large.
- Even then, weak feedback of the E4 type cannot be excluded.

## 7. Limitations
- **Design scope.** The results come from one simulated design:
  - λ ≡ 1 in the data with 2PL fits;
  - eight randomly assigned templates;
  - exponential feedback inside the λ bracket with a single (κ, τ_D) per cell;
  - N ∈ {300, 1000}.

  Other feedback forms, such as success-driven feedback, item-specific feedback or feedback outside the λ bracket, were not studied.
- **Rule resolution.** H5c and H5d could not resolve levels between 0.05 and 0.10 with 300 and 100 datasets. The E1 level analysis is exploratory.
- **E3 and E5 sizes.** Each has 30 datasets per N, which suffices for the power statements (CP lower 0.884) but gives only moderate precision for the bias. The MC half-width of the E5 bias is about 0.02 at N = 300.
- **Reference null for H5a.** H5a uses the Experiment-4 V2 q95. E4's own bootstrap T\* gives similar quantiles, which supports the choice for these cells.
- **No adjustment model.** No adjustment was tested: the fitted model never contained η, so whether F is recovered once feedback is modelled remains open. That is a natural Experiment 6.
