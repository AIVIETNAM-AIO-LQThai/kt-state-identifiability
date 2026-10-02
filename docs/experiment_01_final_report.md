# Experiment 1: final report

**Can a shared transient latent state `F` be recovered in a synthetic knowledge-tracing process?**

Final interpretation: Opus, 2026-10-02 (plan addendum H6, decisions D29–D32).
Confirmatory data: `results/experiment_01/confirmatory/1b1307a48a/` (commit `97d67a9`).

> **Scope.** Every result here concerns statistical recovery under simulated assumptions: the frozen probit DGP, the
> schedule of `design.yaml`, known item difficulties, and the equal-weight all-pairs composite likelihood. `F` is a
> covariance component of the simulated latent process. Nothing here identifies fatigue, stress, mood, attention,
> emotion or any other psychological construct. No real learners, facial data or external datasets were used.

## 1. Question and design (recap)

**H1.** A skill-general, session-resetting Ornstein–Uhlenbeck state `F` affects only the current response. Its variance
σ²_F and time constant τ_F are identifiable together with:
- baseline mastery `M0` (unstructured Σ_M);
- slow learning `α_u·H^s` (saturating exposure count, φ);
- fast recency `r_u·H^f` (exponential trace, τ_R).

**Model.** `Z = −b + M0[k] + α_u H^s + r_u H^f + F + ε`, with Var(ε) = 1.

**Generating values.**
- ᾱ = 0.15, φ = 0.2, σ²_α = 0.0025
- r̄ = 0.35, τ_R = 5 min, σ²_r = 0.0225
- **σ²_F = 0.16, τ_F = 10 min**
- Σ_M = 0.8I + 0.1·11ᵀ

**Schedule.**
- 4 skills × 12 items.
- 3 practice sessions (days 0, 1, 3; 32 attempts each), then a 16-probe session on day 7.
- 8 schedule templates.

**Models.** Nested: B0 (M0 + slow) ⊂ B1 (+ recency) ⊂ B2 (+ `F`).

**Inference.**
- Godambe sandwich.
- Boundary-aware parametric-bootstrap composite-LR test of σ²_F = 0, with p = (1+#)/(B+1).
- One learner bootstrap.

**Confirmatory matrix (D23).**
- Scenarios: S1 (clean), S2 (σ²_F = 0), S8 (lognormal gains, CV 0.6, correlated 0.5 with baseline, `F` present) and S8n (S8 gains, σ²_F = 0).
- N_fit ∈ {300, 1000} plus 300 held-out learners per dataset; 20 replications per cell, giving 160 fit jobs.
- Null tests on reps 0–9 of each cell: B = 99 for S2/S8n and B = 19 for S1/S8.
- One learner bootstrap with B = 50.

The pre-registered rules PH1–PH6 (D24) were fixed before any confirmatory data existed and are applied here unchanged.

## 2. Provenance and integrity

| check | result |
|---|---|
| frozen config | `configs/experiment_01/stage_confirmatory.yaml`, sha256 `da9c7d9a…8857` (matches D27); config hash `1b1307a48a5a` |
| jobs | 160 fit + 4,720 null replicates + 50 learner-bootstrap replicates = **4,930 / 4,930 ok, 0 errors, 0 failed replicates** |
| code and config history | the last commit touching `kt_trial/` or `configs/` is the freeze commit `9ded7a7`; the results commit adds results only |
| venue | user's Windows 11 machine (D25/D28): Python 3.12.10, numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, PyYAML 6.0.3 |
| compute | 65.8 CPU-h, against the 108 CPU-h estimate |
| convergence | 480 / 480 model fits converged; every S1/S8 B2 fit had 5/5 starts at the best; 1 certificate flag (P3) |

**P1: the code hash differs, but only by line endings (D29).** The manifest records code hash `3b2ff1fd…`, not the
frozen `9369a71c…`. Re-hashing the frozen `kt_trial/*.py` from commit `9ded7a7` reproduces both values exactly: with LF
line endings it gives `9369a71c…`, and with CRLF line endings it gives `3b2ff1fd…` (Appendix A). Git on Windows
checked out the Python files with CRLF; `.gitattributes` pins LF only for the frozen YAML configs. Line endings do not
change Python semantics. **The run therefore used the frozen code.** All 4,930 job envelopes carry the same hash.
The runner's mismatch check compares a resumed run against that run's own first manifest, not against the freeze
record, so it could not catch this. The confirmatory gate enforced only the config sha256. This is recorded as a gate
weakness and was not changed after the run.

**P2: `git.dirty = true` (D29).** The runner computes dirty state from `git status --porcelain`, which also lists
untracked files. The results directory and the tee'd `confirmatory_run.log` existed during the run, which explains
the flag. P1 and the path-filtered history show that no tracked code or config differed from the freeze.

**P3: one certificate flag (D30).** S8n, N = 1000, rep 13, B2 has a Newton decrement of 0.044 (tolerance 1e-3). Its
Hessian is positive definite (minimum eigenvalue 0.020), σ̂²_F = 0.0008, τ̂_F = 0.49998, and one start reached the best
(log-lik range across starts 0.033). τ_F stalled at its 0.5-min start value in a direction made nearly flat by
σ̂²_F ≈ 0. The decrement bounds the remaining log-lik gain at about 0.04 units, and rep 13 is outside the null-test
reps 0–9. **It is immaterial:**
- PH4's rejection count is unaffected.
- The effect on the PH4 σ̂²_F distribution and on PH6 is negligible.

It was not refitted, because a refit would deviate from the protocol. Single-start-best rates are ≤ 0.10 in every
cell, below the 20 % escalation rule.

**P4: reference values for nuisance gain variances in S8/S8n (D31).** The summary measures σ²_α and σ²_r in S8 and S8n
against the nominal Gaussian values 0.0025 and 0.0225. The actual lognormal variances are (0.6·ᾱ)² = **0.0081** and
(0.6·r̄)² = **0.0441**, so those summary rows are not biases. Section 4 gives the corrected comparison. No pre-registered
rule uses these parameters, and `summary.md` is left as generated.

**Archive.** The partial cloud attempt in `results/experiment_01/archive_cloud_partial_stage3/` (D28) was neither
used nor inspected.

## 3. Pre-registered results (D24)

Bias verdicts compare the 95 % Monte Carlo CI (bias ± 1.96·MCSE) with the margin [−0.04, 0.04]. Rates carry
Clopper–Pearson (CP) 95 % limits.

| ID | claim tested (B2 vs B1) | cell | result | verdict |
|---|---|---|---|---|
| PH1 | σ²_F recovered without material bias, clean process | S1, N = 300 | bias −0.012 (MCSE 0.008), MC CI [−0.028, 0.004]; SD 0.036, RMSE 0.037 | **pass** |
| PH1 | | S1, N = 1000 | bias +0.007 (MCSE 0.005), MC CI [−0.003, 0.018]; SD 0.024, RMSE 0.024 | **pass** |
| PH2 | boundary-aware test detects σ²_F = 0.16 | S1, N = 300 | 10 / 10 rejections, CP [0.69, 1.00]; observed CLR 408–927 against a bootstrap-null maximum of 278 | power, reported |
| PH2 | | S1, N = 1000 | 10 / 10, CP [0.69, 1.00]; observed CLR 2,072–3,487 against a bootstrap-null maximum of 346 | power, reported |
| PH3 | no excess false positives when `F` is absent | S2 (10 + 10 datasets) | 0 / 20, CP [0, 0.17]; σ̂²_F = 0 in 50 % of 40 fits, mean 0.008, p90 0.023, max 0.041 | **no evidence of excess false positives** |
| PH4 | misspecified, correlated gains not attributed to `F` | S8n (10 + 10) | 0 / 20, CP [0, 0.17]; σ̂²_F = 0 in 68 %, mean 0.003, p90 0.009, max 0.032; near-white 10 / 40 | **no evidence of excess false positives** |
| PH5 | robustness of σ²_F recovery to non-Gaussian, correlated gains (secondary) | S8, N = 300 | bias −0.024 (MCSE 0.011), MC CI [−0.046, −0.002] | **inconclusive** |
| PH5 | | S8, N = 1000 | bias −0.021 (MCSE 0.006), MC CI [−0.032, −0.010] | **pass** (inside the margin; bias ≠ 0) |
| PH6 | B2 improves the held-out population-marginal pairwise composite score | S1, N = 300 / 1000 | +1.28 (MC CI [1.11, 1.45]) / +1.38 ([1.17, 1.59]) per learner | **improvement** |
| PH6 | no spurious superiority without `F` | S2, N = 300 / 1000 | −0.007 [−0.030, 0.016] / +0.001 [−0.018, 0.020] | **not shown** |
| PH6 | | S8n, N = 300 / 1000 | −0.016 [−0.034, 0.002] / −0.003 [−0.006, 0.001] | **not shown** |

Notes on reading the table:
- **PH2.** With B = 19 the smallest attainable p is 0.05, so every S1 rejection is at p = 0.05. Every observed S1 CLR
  nevertheless exceeds every bootstrap-null CLR of its cell (pooled over 190 replicates). Pooled over both N, 20/20
  gives CP [0.83, 1.00]. This is power at a large effect (σ²_F = 0.16), not at the MDE.
- **PH3 and PH4.** The rule can detect only gross excess (≥ 4/20). The data exclude false-positive rates above about
  0.17 per scenario, or about 0.09 pooled over the 40 null datasets (descriptive). They do **not** demonstrate a nominal
  5 % size.
- **Near-white.** "Near-white" means σ̂²_F > 0 with τ̂_F < 0.4 min, below the shortest design lag.

## 4. Secondary and descriptive results

**τ_F (S1, fits with σ̂²_F > 0; all 20 per N).** At N = 300: bias +2.5 min (MCSE 0.9), SD 4.1, RMSE 4.7, right-skewed.
At N = 1000: bias −0.2 (MCSE 0.4), SD 1.8, RMSE 1.7. τ_F is determined only roughly at N = 300, and no τ_F interval
claim is made (D24, L2).

**Sandwich coverage of σ²_F (nominal 95 %).** S1: 20/20 (N = 300) and 18/20 (N = 1000). S8: 19/20 and 18/20. Twenty
replications only bound coverage loosely (18/20 has CP [0.68, 0.99]).

**Learner bootstrap vs sandwich (S1, N = 1000, rep 0, B = 50).** Ratio of sandwich SE to bootstrap SD:

| param | ᾱ | φ | σ²_α | r̄ | τ_R | σ²_r | σ²_F | τ_F |
|---|---|---|---|---|---|---|---|---|
| ratio | 1.05 | 1.02 | 1.01 | 1.14 | 1.04 | 1.50 | 0.96 | 1.04 |

On this one dataset at N = 1000, the Stage 2 under-estimation of the τ_F SE (ratio 0.46 at N = 300) does not recur.

**Calibration of the null test.**
- **S2.** Bootstrap p-values are roughly uniform: 9/20 below 0.5, minimum 0.08.
- **S8n.** All p-values are ≥ 0.37. The observed CLR is ≤ 4.8, against a bootstrap-null q90 of about 68, because the
  bootstrap simulates from a Gaussian-gain B1 fit. **Under gain misspecification the test is conservative**, so its size
  is not nominal there, in the safe direction.
- **Bootstrap-null CLR\* distributions.** About 25–35 % are exactly 0, with q95 of about 70–130: far from χ² (L4).

**Near-white pathway (L6).** Near-white fits occur in 9/40 (S2) and 10/40 (S8n) null fits. Their magnitudes are small
(max σ̂²_F 0.041 in S2 and 0.032 in S8n), and none was rejected by the null test. The pathway Stage 2 identified is
still present in point estimates, but it did not produce false detections here.

**Gain misspecification (S8, S8n; corrected references, P4).** B2 means over 20 reps, with the actual variances
σ²_α = 0.0081 and σ²_r = 0.0441:

| cell | σ̂²_α | σ̂²_r |
|---|---|---|
| S8, N = 300 | 0.0119 | 0.083 |
| S8, N = 1000 | 0.0109 | 0.085 |
| S8n, N = 300 | 0.0115 | 0.082 |
| S8n, N = 1000 | 0.0106 | 0.084 |

- The gain-variance terms over-absorb the misspecification, by roughly ×1.3 for σ²_α and ×1.9 for σ²_r. The model has
  no gain–baseline covariance and assumes Gaussian gains, so this was expected.
- In S8, σ̂²_F is attenuated by about 13–15 % (PH5). Part of `F`'s short-lag covariance is attributed to fast-recency
  heterogeneity.
- In S8n the reverse transfer, gain misfit absorbed into σ²_F, stays small (mean σ̂²_F 0.003).

**Nested-model contrasts.**
- B0, which omits recency, is strongly biased in every cell (ᾱ +0.17 to +0.19, φ +0.15 to +0.17).
- B1 inflates σ²_r when `F` is present (S1: +0.032 at N = 300). B2 removes most of that inflation (+0.008).
- Held-out B1 − B0 pairwise composite: +35 to +49 per learner.

**Marginal Bernoulli score.** B2 − B1 is ≤ 3e-5 per learner in every cell, i.e. essentially zero. `F` has mean zero
and alters response dependence, not population-marginal success probabilities. Its predictive value lies in the joint
(pairwise) structure. Next-response, history-conditioned prediction was not evaluated (filtering is out of scope).

**MDE (descriptive only, D24).**
- Design-based predicted SE of σ̂²_F at σ²_F = 0.04: 0.034 (N = 300) and 0.019 (N = 1000).
- Empirical SD at σ²_F = 0.16: 0.036 and 0.024.
- An effect of 0.04 is therefore about 1.2 SE at N = 300 and about 2 SE at N = 1000. Its detectability is not
  demonstrated empirically (L3).

## 5. Interpretation

**H1 verdict (D32): supported for the variance σ²_F, under the simulated assumptions. τ_F is weakly determined.**

Supported claims, each bounded by the scope statement and by L1–L8 and P1–P4:

1. **Recoverability.** The variance of a skill-general, session-resetting OU shared transient latent state `F` can be
   recovered without material bias (MC-CI within ±0.04 around the truth 0.16). It is recovered jointly with baseline
   mastery, slow learning and fast recency at N = 300 and N = 1000 fitting learners, under this schedule and known
   item difficulties (PH1). Separating `F` requires the fast-recency term to be modelled.
2. **Detection.** The boundary-aware parametric-bootstrap composite-LR test detected σ²_F = 0.16 in all 20 tested
   datasets (PH2).
3. **False positives.** With `F` absent, under Gaussian gains or under lognormal gains correlated with baseline, the
   test rejected in 0 of 40 datasets (PH3, PH4). The design rules out only false-positive rates above about 0.17 per
   scenario. Under gain misspecification the test is conservative.
4. **Partial robustness.** Under non-Gaussian, baseline-correlated gains, σ²_F stays within the ±0.04 margin at
   N = 1000 (PH5 pass) and is inconclusive at N = 300. The attenuation of about 13–15 % is systematic.
5. **Held-out score.** Adding `F` improves the held-out population-marginal pairwise composite score when `F` exists
   (PH6) and gives no spurious improvement when it does not.

**Not supported, or outside what Experiment 1 tested:**
- interval inference for τ_F, and detectability of σ²_F = 0.04 (MDE dropped, D24);
- recovery of the gain variances σ²_α and σ²_r (L1; biased under S8/S8n);
- global identifiability (L5: local Jacobian rank only, at three interior points);
- robustness to the Stage 2-only scenarios: near-white `F` (S4a, L6), outcome-driven context (S7, L7), absent
  recency (S3, L8), session-correlated starts (S6), slow `F` (S4b) and blocked practice (S5). These are descriptive
  findings from 3 replications;
- any statement about real learners, other schedules, unknown item difficulties, or next-response prediction;
- **any psychological meaning of `F`.** A positive σ̂²_F in data would show a shared transient covariance component,
  not its cause. L7 shows that outcome-driven processes also produce it.

## 6. Limitations

| ID | limitation | evidence |
|---|---|---|
| L1 | σ²_α and σ²_r are weakly identified at N ≤ 300 (often on the lower bound) and biased under gain misspecification; the sandwich conditions on boundary nuisances | smoke; Stage 3 boundary rates; §4 |
| L2 | τ_F is the weakest direction; it is interpretable only when σ²_F is clearly positive, and has no interval claims | design audit (smallest singular value); τ_F RMSE 4.7 min at N = 300 |
| L3 | MDE σ²_F = 0.04 is not demonstrated empirically | design-based z ≈ 1.2 / 2.1 |
| L4 | under the null the composite LR is not χ²; only bootstrap-calibrated p-values are valid | CLR\* q95 ≈ 70–130, 25–35 % exact zeros |
| L5 | identification is local, at the tested points only | design audit |
| L6 | a near-white `F` is identified only through the marginal scale and can absorb marginal misfit | Stage 2 S8n; Stage 3 near-white 19/80 null fits (small) |
| L7 | outcome-driven context inflates σ̂²_F (≈ 0.30 against 0.16) with a long τ̂_F | Stage 2 S7 |
| L8 | when recency is absent, the recency terms absorb part of `F` (−0.034) | Stage 2 S3 |
| L9 (new) | gain misspecification attenuates σ̂²_F by about 13–15 % and inflates the gain variances; the null test is conservative under it | Stage 3 S8/S8n |
| L10 (new) | 20 replications and 10 null tests per cell support only coarse rate statements (CP half-widths 0.15–0.3) | design of D23 |

## 7. Deviations from the original prompt

All deviations were recorded and approved before the corresponding data existed:
- D19: stopping rule in absolute log-lik units.
- D20: Stage 2 B = 49.
- D22: Newton-decrement certificate replacing the raw-gradient clause.
- D23: null-test B = 99 / 19 instead of the provisional 199; null tests on 10 of the 20 datasets per cell; 20
  replications instead of the minimum 10.
- D24: MDE dropped as a criterion.
- S8n added (user choice).
- D25/D28: venue is the user's local machine, run from scratch after the cloud attempt was abandoned.

Recorded after the run, none changing a result or rule: P1–P4 (D29–D31).

## 8. Recommendations for any later experiment (not acted on)

- Pin `*.py text eol=lf` in `.gitattributes`, and make the confirmatory gate check the code hash against the freeze
  record, not just against the run's own first manifest.
- Count only tracked changes in `dirty`, and record untracked files separately.
- In `summarize`, measure gain variances in non-Gaussian scenarios against the actual moments.
- If size claims are wanted, run more null datasets per cell (e.g. ≥ 100) with B ≥ 99. Extending to σ²_F = 0.04
  power, the S7-type outcome-driven processes, or unknown difficulties would each need its own approved protocol.

## Appendix A. Verification output (read-only script, 2026-10-02)

```text
frozen code (9ded7a7), LF  : 9369a71c895819c295143c279d7671ba446d5b5b9626eef1c602e96e66916efc
frozen code (9ded7a7), CRLF: 3b2ff1fd9f348c0b8cabe4ba5770d5afafc59c686b4bba90056e19b6a9c846df
manifest code_hash         : 3b2ff1fd9f348c0b8cabe4ba5770d5afafc59c686b4bba90056e19b6a9c846df
frozen config sha256       : da9c7d9a1aa20dabded1485d13494ad016d110ae9bfe9abc12edfec5fb118857
jobs by kind/status        : {('null_rep', 'ok'): 4720, ('lboot_rep', 'ok'): 50, ('fit', 'ok'): 160}
code hashes in jobs        : {'3b2ff1fd9f34': 4930}

fit certificates outside tolerance (Newton decrement > 1e-3 or H not PD):
  fit__S8n__N1000__r13 B2 decrement 0.0445 min eig 0.0202 sigma2_F 0.0008 tau_F 0.49998 {'n_starts_at_best': 1, 'secondary_optima': 0, 'max_scalar_param_gap': 0.0, 'll_range': 0.03307439759373665} ['newton_decrement_large', 'single_start_at_best']

bootstrap-null CLR* per cell (B2 vs B1):
   S1 N=300  n= 190 share0=0.33 q90=  55.9 q95= 104.5 max= 277.9
   S1 N=1000 n= 190 share0=0.27 q90=  82.0 q95= 131.4 max= 345.7
   S2 N=300  n= 990 share0=0.30 q90=  72.1 q95= 115.7 max= 320.4
   S2 N=1000 n= 990 share0=0.28 q90=  59.0 q95=  96.5 max= 307.5
   S8 N=300  n= 190 share0=0.29 q90=  43.8 q95=  72.2 max= 321.5
   S8 N=1000 n= 190 share0=0.35 q90=  63.7 q95=  86.9 max= 180.7
  S8n N=300  n= 990 share0=0.26 q90=  67.9 q95= 119.9 max= 317.7
  S8n N=1000 n= 990 share0=0.25 q90=  68.8 q95= 117.0 max= 379.4

null-scenario B2 estimates (all 20 reps per cell):
   S2 N=300  positive 9/20, near-white 4/20, max sigma2_F 0.0406
   S2 N=1000 positive 11/20, near-white 5/20, max sigma2_F 0.0288
  S8n N=300  positive 9/20, near-white 7/20, max sigma2_F 0.0321
  S8n N=1000 positive 4/20, near-white 3/20, max sigma2_F 0.0072

S8/S8n gain-variance estimates vs actual lognormal variances (0.0081, 0.0441):
   S8 N=300  sigma2_alpha mean 0.0119 (MCSE 0.0008); sigma2_r mean 0.0834 (MCSE 0.0108)
   S8 N=1000 sigma2_alpha mean 0.0109 (MCSE 0.0004); sigma2_r mean 0.0852 (MCSE 0.0051)
  S8n N=300  sigma2_alpha mean 0.0115 (MCSE 0.0008); sigma2_r mean 0.0824 (MCSE 0.0097)
  S8n N=1000 sigma2_alpha mean 0.0106 (MCSE 0.0005); sigma2_r mean 0.0839 (MCSE 0.0058)
```

All other numbers are quoted from `results/experiment_01/confirmatory/1b1307a48a/summary.md` / `summary.json`.
