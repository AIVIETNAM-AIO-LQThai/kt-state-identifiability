# Experiment 1 — Shared transient latent state `F`: synthetic identifiability & recovery

**Status:** approved by the user on 2026-09-30 (plan-mode approval, including kernel, S6/S7/S8/S8n constructions, Stage 1 and the bounded Stage 2 budget). Stage 3 approved 2026-09-30 (addendum H3), run locally and interpreted 2026-10-02 (addendum H6). **Experiment 1 is complete**; see `docs/experiment_01_final_report.md`.

## Context

The repository (`kt-state-identifiability`, currently on `claude/sharp-carson-en32pf`; work will move to
`exp/transient-state-recoverability`) is essentially empty: `README.md`,
`bootstrap-requirements.txt` (the user's local Windows `.venv12`, Python 3.12.10, numpy 2.5.3, scipy 1.18.1,
pandas, PyYAML, pytest, joblib, matplotlib, torch-cpu) and `environment_check.txt`. There is **no** `AGENTS.md`,
`CLAUDE.md`, prior docs, or previously approved kernel equations — so the kernel family, schedule and the
ambiguous robustness scenarios were proposed and then approved in this plan.

Goal: test whether a skill-general, session-resetting OU state `F` (variance `σ_F²`, time constant `τ_F`) is
recoverable, separately from baseline mastery `M0`, slow exposure (`α_u H^s`) and fast recency (`r_u H^f`),
under the frozen probit DGP (H1: `F` affects the current response only). Claims are limited to statistical
recoverability under simulated assumptions; `F` is never given a psychological label.

## Session facts (verified via `get_session`)

- Interface: Claude Code cloud session (remote container), launched from the Claude desktop app; CLI 2.1.285.
- Model: `claude-opus-5-5` (configured and last served); effort `high`; permission mode `plan`.
- No tool is exposed that lets me change this session's model → **every Opus↔Sonnet handoff is manual** (model picker
  in the app). `opusplan` is documented for the CLI (`/model opusplan`); whether this cloud session's picker offers it is
  **unknown** — please check. Even with `opusplan`, approval gates stay in force.
- Container: 4 vCPU, 15 GB RAM, ephemeral; system Python 3.11 without numpy; `python3.12` + `uv` present; package mirror
  offers numpy ≤ 2.4.6, scipy ≤ 1.17.1 (your local pins 2.5.3/1.18.1 are not available here — versions go in every manifest).

## Frozen model (as given) + approved kernel/schedule specification

Per template `g`, observation `t` (chronological), session `s_t`, absolute time `T_t` (minutes), skill `k_t`, item `q_t`.

**Exposure rule.** Only *practice* attempts are exposures (feedback given). An attempt at `T_e` counts for responses with
`T_e < T_t` strictly (updated after the response). **Delayed probes are not exposures** (no feedback). Absolute clock;
session reset applies to `F` only, never to exposure history. `E_t = {e: practice, k_e = k_t, T_e < T_t}`, `n_t = |E_t|`.

**Slow kernel (approved):** geometrically-saturating exposure count
`H^s_t = Σ_{j=0}^{n_t−1} (1−φ)^j = (1 − (1−φ)^{n_t})/φ`, φ ∈ (0,1), dimensionless "exposure-equivalents".
φ = 0.20 = fractional loss of marginal gain per additional exposure; `H^s=0` before first exposure; φ→0 gives the raw
count, φ→1 gives `1{n_t≥1}`; asymptote 1/φ = 5 → max mean gain ᾱ/φ = 0.75 probit. No temporal forgetting.
(Rejected alternative: time forgetting, `log(1+Σ exp(−φΔ_days))`, leaves φ nearly unidentified at ᾱ = 0.15.)

**Fast kernel:** exponential recency trace `H^f_t = Σ_{e∈E_t} exp(−(T_t−T_e)/τ_R)`, τ_R in minutes (5).
Limits: τ_R→0 ⇒ 0; τ_R→∞ ⇒ n_t. Cross-session terms are included by formula (≈e^{−288}, i.e. 0).

Kernels depend on the schedule only (not on responses), so μ, D, C are per-template quantities:
`μ_t = −b_{q_t} + ᾱH^s_t + r̄H^f_t`;
`D_t = 1 + Σ_M[k_t,k_t] + σ_α²(H^s_t)² + σ_r²(H^f_t)² + σ_F²`;
`C_tt' = Σ_M[k_t,k_t'] + σ_α²H^s_tH^s_t' + σ_r²H^f_tH^f_t' + 1{s_t=s_t'}σ_F² exp(−|T_t−T_t'|/τ_F)` (t≠t').
Gains `α_u, r_u` are learner-level (shared across skills), so the H-product terms also act across skills; the OU term is
exact because `F_start ~ N(0,σ_F²)` makes the within-session OU stationary. Every latent covariance is a sum of PSD pieces
+ identity ⇒ PD, |ρ|<1 guaranteed. Negative gain draws are kept.

**Schedule (approved; all values in versioned YAML):**
- Sessions (absolute minutes): S1 at 0 (day 0), S2 at 1440 (day 1), S3 at 4320 (day 3), probe session at 10080 (day 7).
- Practice: 32 attempts/session, 8 per skill; interleaved order = seeded permutation with max same-skill run 2
  (yields both same-skill short lags and cross-skill short lags). Probe session: 16 probes, 4 per skill, interleaved.
- Inter-attempt interval: `0.4 + Gamma(shape 2, scale 0.3)` min (mean 1.0, lags ≈0.4–35 min within session).
- Items: 12 per skill, `b = linspace(−1,1,12) + c_k`, `c = (−0.2, 0, 0.2, 0.4)`; practice items drawn without replacement
  within a session; probes use 4 items spanning each skill's range. Start-of-practice success ≈ 0.25–0.75, end ≈ 0.5–0.9.
- **G = 8 schedule templates**, learners assigned balanced/randomly (independent of latent states). Rationale: more
  exposure-age/lag profiles than one fixed schedule, while the pairwise likelihood depends on the data only through
  per-template pair-pattern counts ⇒ objective cost independent of N (critical for bootstrap budgets).
- S5 (blocked): practice in 4 blocks of 8 same-skill attempts, block order permuted per session; probes unchanged
  (single-factor change).

Pre-exposure anchoring: every learner has 4 observations with `H^s = H^f = 0` (first attempt per skill) plus low-exposure
early attempts; the probe session gives within-session, cross-skill pairs with `H^f ≈ 0` — a clean anchor for `σ_F², τ_F`.
Cross-session pairs (zero F covariance) separate F from Σ_M and gain variance.

## Models

Shared interface, nested: B0 (M0 + slow; θ = ᾱ, φ, σ_α², Σ_M) — 13 params; B1 (+ r̄, τ_R, σ_r²) — 16; B2 (+ σ_F², τ_F) — 18.
Σ_M unstructured (log-Cholesky, 10 params; generating value is compound symmetric) so F cannot absorb misfit of an
over-restricted Σ_M. Item difficulties known and fixed everywhere.

## Estimation & inference

- **Objective:** all-pairs, equal-weight pairwise composite log-likelihood
  `ℓ = Σ_g Σ_{t<t'} Σ_{ab} n_{g,tt',ab} log p_{g,tt',ab}`, `p11 = Φ2(μ_t/√D_t, μ_t'/√D_t'; C_tt'/√(D_tD_t'))`, other cells
  by differencing. All 6216 within-learner pairs/template (practice, probes, cross-session) retained, fixed for every fit.
- **BVN:** vectorised Genz/Drezner–Wesolowsky in NumPy, validated vs `scipy.stats.multivariate_normal.cdf`.
  **Analytic gradient** via `∂Φ2/∂a = φ(a)Φ((b−ρa)/√(1−ρ²))`, `∂Φ2/∂ρ = φ2(a,b;ρ)` and chain rule through kernels.
- **Coordinates / constraints (L-BFGS-B boxes):** ᾱ, r̄ free; logit φ; log τ_R ∈ [log 0.1, log 120];
  log τ_F ∈ [log 0.05, log 1000]; variances σ_α², σ_r², σ_F² as *variances* with lower bound exactly 0 (admits the null
  boundary; sd-coordinates have zero gradient at 0); log-Cholesky for Σ_M. Flags: non-finite objective, p ≤ 1e-300,
  box/boundary hits (variance < 1e-6), failed convergence, projected-gradient norm > 1e-4. Inactive decay params
  (τ_F when σ̂_F²=0; τ_R when r̄≈0 and σ̂_r²=0) are reported NA and excluded from inference.
- **Multi-start (5 per fit):** truth-independent default + seeded jitter; B1 warm-starts from B0, B2 from B1 with
  τ_F starts on grid {0.5, 2, 8, 30, 120} min (the "approved τ_F search"); the B1 solution with σ_F²=0 is also evaluated
  so CLR ≥ 0. Start-agreement recorded (# starts within 1e-4 of best; max parameter gap) → conflict ⇒ Opus escalation.
- **Sandwich (interior fits only):** `Ĥ` = numerical Jacobian of analytic gradient; `Ĵ = (1/N)Σ_u s_u s_uᵀ` from
  learner-level composite scores; `V = Ĥ⁻¹ĴĤ⁻¹/N`; Wald 95% in log/logit coordinates, back-transformed.
- **Learner bootstrap (diagnostic, small):** resample whole learners (their count contributions), refit B2 (warm + 1 jitter), compare SD to sandwich SE.
- **Boundary-aware null test for σ_F² = 0:** statistic `CLR = 2[ℓ(B2) − ℓ(B1)]`; parametric bootstrap from fitted B1
  (same N, templates), each replicate repeats the full B1 and B2 searches incl. τ_F grid; `p = (1+#{CLR*≥CLR})/(B+1)`,
  α = 0.05; B = 99 (diagnostic), 199 (confirmatory, MC SE of p near 0.05 ≈ 0.015). No confidence bound for σ_F² at the
  null unless separately approved; no Wald inference at the boundary.
- **Prediction (frozen):** separate held-out N_test = 300 learners per dataset (own seed stream); scores = held-out
  *population-marginal* Bernoulli log score and *population-marginal pairwise composite* log score, B2−B1 and B1−B0
  paired per learner with SE across learners. N always means fitting learners; N_test reported separately. History-conditioned
  next-response prediction requires filtering, which is out of scope (M9 declined).

## Scenarios (separate YAML; violations tagged in metadata)

S1 clean · S2 σ_F² = 0 · S3 r̄ = σ_r² = 0 · S4a τ_F = 0.2 min (known b keeps the white-noise variance identified via
marginals) · S4b τ_F = 60 min · S5 blocked practice.
- **S6 (approved):** session starts exchangeable across a learner's 4 sessions: `F_start,s = σ_F(√ρ_S G_u + √(1−ρ_S) ε_s)`,
  ρ_S = 0.5; marginal stationarity preserved; only the reset assumption is violated.
- **S7 (approved):** response-contingent shift: after a *practice* attempt with Y = 0, F jumps by δ = −0.25,
  then evolves by the same OU transitions (decays with τ_F); resets at session start as usual; probes don't trigger jumps.
- **S8 (approved):** lognormal gains, `α_u = ᾱ exp(σ_ℓZ_α − σ_ℓ²/2)`, same for r_u, CV = 0.6 (σ_ℓ = 0.555);
  `Z_α = 0.5Z_m + √0.75 e1`, `Z_r = 0.5Z_m + √0.75 e2`, `Z_m` = standardized learner mean of M0 (latent corr 0.5 with
  baseline, 0.25 between gains); realized Pearson correlations reported. F as in S1.

- **S8n (approved addition):** S8 gain construction with σ_F² = 0 — direct false-attribution test of misspecified gain
  heterogeneity; fitted with the same B0/B1/B2 and null bootstrap as S2.

## User decisions recorded at plan time (2026-09-30)

- Slow kernel = saturating count (above). S7 = error-contingent jump. S8n added. S1m (MDE power) **not** added, so
  the MDE σ_F² = 0.04 is assessed only by design-based predicted SEs from M5, not by an empirical power run.
  M9 filtering **not** in scope (S1's "posterior uncertainty" endpoint is out of Experiment 1 unless approved later).
- Execution in this cloud container with a gitignored `.venv`; commit + push at each milestone/handoff (no PR);
  commit small result JSON/summaries, not datasets.
- **Branch:** work on a purpose-named branch **`exp/transient-state-recoverability`** (no owner/tool prefix), created
  from the current HEAD (`6886865`), replacing `claude/sharp-carson-en32pf` per your instruction. Push with
  `git push -u origin exp/transient-state-recoverability`; if the remote/proxy refuses that name I stop and report
  rather than falling back silently. (Name chosen to keep `F` neutrally labelled; your `exp/context-recoverability`
  works equally if you prefer it.)

## Repository layout (new files)

```
pyproject.toml                 # minimal; `python -m kt_trial` from repo root, no install required
.gitignore                     # .venv/, caches, results/**/datasets
configs/experiment_01/         # design.yaml, scenarios/*.yaml, stage_smoke.yaml, stage_diagnostic.yaml, (stage_confirmatory.yaml later)
kt_trial/ __init__.py __main__.py cli.py config.py schedule.py kernels.py moments.py simulator.py
          models.py bvn.py composite_likelihood.py fit.py inference.py identifiability.py
          evaluate.py runner.py summarize.py manifest.py
tests/  test_schedule, test_kernels, test_moments_mc, test_simulator, test_bvn, test_composite_likelihood,
        test_models_nesting, test_transforms, test_fit_recovery, test_identifiability, test_inference_boundary, test_runner_resume
docs/   experiment_01_plan.md, experiment_01_decisions.md, experiment_01_handoff.md, experiment_01_smoke_report.md
results/experiment_01/<stage>/<config_hash>/ manifest.json, jobs/*.json, summary.{json,md}
```

## Implementation order (Sonnet) and validation per milestone

1. **M1 config + schedule + design audit tables** — tests: determinism, counts/times/sessions invariants, strict-before exposure indexing.
2. **M2 kernels, moments, simulator (all scenarios as hooks)** — tests: kernel limits & derivatives vs FD, analytic μ/D/C vs
   Monte-Carlo Z moments (200k learners), session reset (zero cross-session F cov; S6 non-zero), PSD, seed determinism.
3. **M3 BVN + composite likelihood + analytic gradient** — BVN vs scipy (1e-8), 2-obs hand-checkable case, gradient vs FD,
   count-table likelihood == raw-data likelihood.
4. **M4 models/transforms/fit/multistart** — B2(σ_F²=0) ≡ B1 and B1(r̄=σ_r²=0) ≡ B0 exactly; transform round trips;
   recovery on a small large-N case; boundary fit returns σ_F² = 0 exactly with flag.
5. **M5 identifiability** — Jacobian of the standardized map (all P_t and P11_tt' for all templates, all active params
   jointly), rows weighted by Bernoulli SD, columns in unit-scaled log/logit coordinates; analytic vs central-difference at 2
   step sizes; SVD, condition numbers, weakest right-singular vectors + expected-KL profile along them; evaluated at the
   generating point and a second interior point (σ_F²=0.04, τ_F=20, τ_R=3, φ=0.3); predicted Godambe SEs at N=300/1000
   (Ĵ from 20k simulated learners); deliberately deficient case (single session, τ_F fixed huge ⇒ F ≡ learner intercept ⇒
   singular value ≈ 0 against Σ_M's common direction) must be flagged. **If the approved schedule fails, stop and ask.**
6. **M6 inference** — sandwich, learner bootstrap, null CLR bootstrap; tests on tiny budgets incl. boundary behaviour.
7. **M7 runner/CLI/summaries** — commands `check-env`, `audit-design`, `simulate`, `fit`, `run --stage {smoke,diagnostic,confirmatory} [--dry-run]`,
   `summarize`; deterministic SeedSequence seeds from a recorded master seed keyed by (stage, scenario, N, rep, purpose);
   atomic JSON writes (tmp + `os.replace`); resume skips valid jobs, reruns corrupt/incomplete, records failures as data;
   manifest mismatch (config hash / git revision / dirty tree / package versions) ⇒ refuse and report;
   confirmatory requires `--frozen-sha256 <hash>` matching the frozen config — nothing auto-advances.
8. **M8 Stage 1 smoke** — full `pytest`, then one clean end-to-end smoke into a fresh results dir; smoke report.
(M9 filtering declined for now; `filtering.py` is not created.)

## Stages, budgets, acceptance

| Stage | Matrix | Budget cap | Acceptance |
|---|---|---|---|
| 1 smoke | N=64, 2 seeds, S1+S2, B0/B1/B2 × 5 starts (60 starts); null bootstrap B=19 on 1 S1 + 1 S2 dataset (~380 starts); learner bootstrap B=10 on 1 S1 | ≤ 1 CPU-h, ≤ 30 min wall, 4 workers | all tests pass; deterministic rerun byte-identical; resume works; failures recorded; audit passes; recovery direction sane |
| Opus audit | inspect kernels, covariance, likelihood, constraints, inference, audit, smoke outputs | — | `pass` / `pass with stated limitations` / `blocked` |
| 2 diagnostic (pre-approved if audit passes and nothing changes) | N=300 (+300 held-out), 3 reps, S1–S8 + S8n (10 scen.) × 3 models × 5 starts (450 starts); null bootstrap B=99 on S1, S2, S8n × 3 reps (~8,900 starts); learner bootstrap B=50 on 1 S1 dataset | ≤ 20 CPU-h, ≤ 6 h wall, 4 workers; if smoke-measured projection exceeds the cap I stop and ask | bias, MCSE, RMSE, coverage (interior only, Clopper–Pearson), convergence, boundary rate, start agreement, predictive scores, runtime; frozen-config draft + diagnostic report |
| 3 confirmatory | provisional S1, S2, S8 × N∈{300,1000} × ≥10 reps × 3 models × 5 starts = 180 fits / 900 starts + null bootstraps (60 × 199 × ~10 starts ≈ 119k starts) | set at Stage 3 approval from measured timings | needs your explicit approval; checksum-frozen |

Rough speed guess (to be measured in smoke): ~50k pair-rows per objective ⇒ ~10–30 ms per objective+gradient ⇒
~2–10 s per start. Stage 3's bootstrap dominates and may need B or search-policy decisions at the Stage 3 request.
Provisional thresholds (restated, not used until Stage 3): |bias σ_F²| ≤ 0.04; MDE σ_F² = 0.04; 10 reps are a procedural
minimum and pass/fail rates will carry Clopper–Pearson intervals ("inconclusive" when they straddle).

## Model handoffs

- **H0 (Opus/Plan, done):** plan approved. After approval (execution mode, still Opus) I write only
  `docs/experiment_01_plan.md`, `docs/experiment_01_decisions.md`, `docs/experiment_01_handoff.md`, then emit
  `MODEL HANDOFF — plan approved` → Sonnet 5.5, Medium (High for M3/M5/M6), execution mode; manual switch; I stop.
- **H1 (Sonnet → Opus, after M8):** smoke/audit checkpoint → Opus, High, Plan Mode; stop.
- **H2 (Opus → Sonnet):** if audit passes, Stage 2 (pre-approved) → Sonnet, Medium; stop for switch.
- **H3 (Sonnet → Opus):** after Stage 2 → Opus, High, Plan Mode: diagnostic interpretation + Stage 3 approval request.
- **H4/H5:** approved Stage 3 → Sonnet, Medium; then Opus, High for final interpretation.
- Escalations Sonnet→Opus per your list (rank deficiency, conflicting optima, moment mismatch, boundary-inference questions, …).

## Commands (your Windows machine, PowerShell, repo root)

```powershell
& "<path>\.venv12\Scripts\Activate.ps1"
python -m pytest -q
python -m kt_trial check-env
python -m kt_trial audit-design --config configs/experiment_01/design.yaml
python -m kt_trial run --stage smoke --config configs/experiment_01/stage_smoke.yaml --workers 4
python -m kt_trial run --stage diagnostic --config configs/experiment_01/stage_diagnostic.yaml --dry-run
python -m kt_trial summarize --results results/experiment_01/smoke
```
Cloud container equivalent uses `.venv/bin/python` (Python 3.12, numpy 2.4.6, scipy 1.17.1, pandas, PyYAML, pytest).

## Assumptions / choices that could change conclusions

1. Slow-kernel family (saturating count chosen). 2. Probes are not exposures. 3. Σ_M unstructured. 4. G = 8 templates, all pairs, equal
weights. 5. S6/S7/S8 constructions. 6. `σ_α²` (true 0.0025) and `σ_r²` may be weakly identified at N=300 — nuisance; M5
will quantify before any batch. 7. Bootstrap null test is the only S2 inference; no confidence bound unless approved.

## Verification (end of implementation)

`pytest -q` all green; `audit-design` report with singular values/condition numbers at two points and the deficient case
flagged; one clean smoke run from an empty results dir + byte-identical rerun + interrupted-resume check; smoke report
with runtime and projected Stage 2/3 cost; decision log updated.

---

## Addendum — H1 OPUS REVIEW — smoke/audit checkpoint (2026-09-30)

Reviewer: Opus 5.5, xhigh effort, Plan Mode (verified via `get_session`). Inputs: code at `147035b`,
`results/experiment_01/audit/design_audit.json`, `results/experiment_01/smoke/494d1072b9/`, plus read-only re-fits.

## Verdict: **BLOCKED — implementation defect (C1)**. It is unblocked by the coding corrections below, which preserve the approved design

The mathematics is implemented as approved. The optimizer stopping rule, however, is mis-scaled, so B2 fits terminate early.
The fix changes no model, DGP, scenario, hypothesis, threshold or sample size. Stage 2 stays blocked until the corrections
pass the unblock criteria below, and its budget needs your decision (question asked separately).

## Audit results — pass
- **Kernels.** `kernels.py` matches D01/D02. Exposures are strictly earlier practice attempts of the same skill; probes never count (tested); the clock is absolute.
- **Moments.** μ, D and C in `moments.py:80-87` match the frozen formulas, including the cross-skill gain products, the session-indicator OU term and the unit residual variance. They agree with Monte Carlo on 400k learners, and V = I + PSD by construction.
- **Simulator.** `simulator.py:63-79` uses the exact OU transition `a=exp(-Δ/τ_F)` with innovation variance `σ_F²(1-a²)` and a stationary session start. S6, S7 and S8 match D08, and negative Gaussian gains are kept.
- **Likelihood.** Cell probabilities match scipy to 1e-10. Count tables are sufficient. The adjoint gradient matches finite differences, learner scores sum to the gradient, and scores are mean-zero at the truth (|t| ≤ 1.4 over 18 parameters, 4000 learners).
- **Constraints.** Variance coordinates admit an exact 0, and log-Cholesky keeps Σ_M positive definite. Nesting is exact: B2 with σ²_F=0 equals B1, and B1 with r̄=σ²_r=0 equals B0. Inactive τ parameters are handled.
- **Inference.** The sandwich uses learner-level scores and excludes boundary parameters. The bootstrap resamples whole learners. The null test simulates from the fitted B1 under the clean DGP, repeats the full B1+B2 search in each replicate, and uses p=(1+#)/(B+1).
- **Identifiability.** Full rank 18/18 at three interior points, with FD vs analytic singular values agreeing to 1e-6. The deficient control is detected (rank 16/18).
- **Runner.** Resume, corrupt-job rerun, error recording, manifest refusal and the frozen-confirmatory gate are all tested, and reruns are deterministic.

## Defects to correct (Sonnet, within the approved design; no user approval needed)
**C1 (blocking): optimizer stopping rule.** `fit.py:30` divides the objective by N·pairs, so `gtol=1e-5` equals roughly 4
(N=64) to 19 (N=300) log-lik units per coordinate. Read-only re-fits of the same starts:

| dataset | current rule: spread of B2 start log-liks | tight rule (ftol 1e-15, gtol 1e-9): spread | interpretation |
|---|---|---|---|
| smoke S1 rep0 (N=64) | 25.0 (start at τ_F=0.5 stopped at τ_F=0.5) | 0.000 | premature stop |
| smoke S1 rep1 (N=64) | 18.7 | 0.000 | premature stop |
| S1 N=300 | **79.4** | 0.000 | premature stop |
| S2 N=64 / N=300 | 1.9 / 1.4 | 2.05 / 1.38 (one start) | genuine secondary τ_F optimum under the null |

Fix: define the stopping rule in absolute log-lik units, independent of N. Set `gtol_eff = gtol_abs / obj.scale` with
`gtol_abs = 1e-3`, `ftol = 1e-15` and `max_iter = 3000`. Keep the per-pair objective scaling, which is numerically well-behaved
(the per-learner scaling produced one erratic start at −912 units). Record the absolute projected-gradient norm, and flag
`large_projected_gradient` when it exceeds 1e-2 absolute. D12 is superseded (new decision D19).
**C2 (blocking for reports): reporting on the boundary or with inactive truth.** `summarize.py:76-101` reports bias and Wald
coverage for parameters whose true value is on the boundary or does not exist. Examples in the smoke summary: "σ²_F coverage 0/1" in S2, and τ_F bias in S2. The same would happen for r̄, σ²_r and τ_R in S3, and for σ²_F and τ_F in S8n. Fix: report those as NA, and give coverage only for
interior-truth parameters. Report both conditional coverage (interior fits) and unconditional coverage (boundary fits count as not covering), with counts.
**C3: start-agreement metric.** Use an absolute tolerance of 0.01 log-lik units. Report `n_starts_at_best` and `secondary_optima`
(starts converged at least 0.5 units below the best), as information rather than error. Escalate to Opus if, in more than 20% of
a cell's B2 fits, the best was reached by only one start.
**C4: tests.** On a fixed N=300 S1 dataset, all five B2 starts must reach within 0.01 of the best. Add a test that the stopping
rule is N-invariant in absolute units, and a test that the summary never reports coverage or bias for boundary or inactive truths.
**C5: re-smoke.** Rerun smoke into a fresh results directory (the code hash changes). Re-verify determinism, and update the
smoke report with a before/after table. Minor: remove the unused `ndtri` import and the unused `allow_mismatch` parameter in `check_manifest`.

**Unblock criteria for Stage 2** (Sonnet checks them mechanically; if any fails, escalate to Opus):
1. The full test suite passes.
2. In the re-smoke, 0 job errors; every fit converged; the absolute projected gradient is ≤ 1e-2 in all fits; and in every S1 B2 fit at least 3 of 5 starts are within 0.01 of the best.
3. Deterministic rerun is identical.
4. The summary contains no boundary or inactive-truth coverage or bias.
5. The Stage 2 dry-run cost is within the approved budget (question below).

## Stated limitations (not blocking; carry into Stage 2/3 reports)
- **L1.** σ²_α (true 0.0025) and σ²_r (true 0.0225) are not identifiable at N ≤ 300: predicted SEs are 0.002 and 0.033, and in the smoke run 6 of 8 B1/B2 fits put σ²_r on its lower bound. The sandwich conditions on boundary nuisance parameters, so it can understate the SEs of ᾱ, φ, r̄ and τ_R. The smoke bootstrap/sandwich SD ratios of 0.5–0.9 for these fit that explanation. Stage 2's learner bootstrap (B=50, N=300) is the check.
- **L2.** τ_F is the weakest direction and is secondary. Interpret it only when σ²_F is clearly positive, and always with its uncertainty (predicted SE: 3 min at τ_F=10, 28 min at τ_F=20).
- **L3.** Provisional MDE σ²_F = 0.04: the design-based z is about 1.2 at N=300 and 2.1 at N=1000. With S1m declined, Experiment 1 cannot demonstrate this MDE empirically. It must be reframed or dropped in the Stage 3 request, not after the results.
- **L4.** Under the null, the composite LR is not χ²: one S2 N=300 dataset gives CLR = 11.4 with σ̂²_F = 0.019 and τ̂_F = 0.7 min. Only the bootstrap-calibrated p-value is meaningful.
- **L5.** Full rank shows local identification at the tested points only.

## Re-costing with the corrected stopping rule (measured, single core, N-independent)
A B0/B1/B2 5-start fit takes about 22 / 45 / 66 s. A fit job with sandwich and held-out scoring takes about 150 s, and a null replicate (B1+B2) about 110 s.
- **Stage 2 as approved (B=99 on S1, S2, S8n):** 891 × 110 s + 30 × 150 s + learner bootstrap ≈ **29 CPU-h, about 7.3 h wall on 4 workers**. This exceeds the approved 20 CPU-h / 6 h caps.
- **With B=49:** about 15 CPU-h, about 3.8 h wall.
- **Stage 3 provisional:** null bootstraps 60 × 199 × 110 s ≈ **365 CPU-h** (about 3.8 days on 4 workers), plus about 2.5 CPU-h of fits. Decided at the Stage 3 request.

## User decisions at this review (2026-09-30)
- **D20: Stage 2 null bootstrap B = 49**, down from 99. It applies to S1, S2 and S8n × 3 reps. Scenarios, N (300 + 300 held-out), reps, models and 5 starts are unchanged. The learner bootstrap stays at B = 50 on S1 rep 0. Caps stay at ≤ 20 CPU-h and ≤ 6 h wall with 4 workers, and the projection is about 15 CPU-h / 3.8 h. B for Stage 3 is still open (provisionally 199).
- **D21: MDE unchanged now.** The Stage 3 request will propose dropping the MDE σ²_F = 0.04 as a confirmatory criterion or reframing it as design-based detectability, before any confirmatory data exist. S1m is not added.

## Stage 2 config to create (`configs/experiment_01/stage_diagnostic.yaml`)
Settings: `stage: diagnostic`, new master seed, scenarios [S1, S2, S3, S4a, S4b, S5, S6, S7, S8, S8n], `N_list: [300]`,
`replications: 3`, models B0/B1/B2, `n_starts: 5`, `heldout_N: 300`, `sandwich: true`, `null_bootstrap: {B: 49}` on S1/S2/S8n
reps 0–2, `learner_bootstrap: {B: 50, model: B2}` on S1 rep 0, cost model from the measured per-start seconds,
`budget: {max_cpu_hours: 20, max_wall_minutes: 360, workers: 4}`. The runner's wall cap stops submission and allows resume.
Sonnet stops and reports if a dry-run projection exceeds 20 CPU-h.

## Next steps after approval
0. Opus (now in execution mode) persists this review: an H1 entry in `docs/experiment_01_handoff.md` (verdict, C1–C5, unblock criteria), D19–D21 in the decision log, and the review into `docs/experiment_01_plan.md`. Then Opus commits, pushes and emits the H2 handoff.
1. Hand off to Sonnet (Medium; High for C1/C4) and implement C1–C5.
2. Sonnet checks the unblock criteria. If all pass, Stage 2 runs as approved or as budget-amended, followed by the H3 handoff to Opus. If any fails, Sonnet escalates to Opus.

---

## Addendum — H2b OPUS DECISION — unblock criterion 2, gradient clause (2026-09-30)

**Problem.** My H1 criterion "absolute projected gradient ≤ 1e-2" is not scale-aware. The log-likelihood is about 2e6, and
the Hessian eigenvalues on the free coordinates span roughly 1e0–1e3 (weak directions such as τ_F) up to about 7e7 (Σ_M
Cholesky coordinates). Double-precision resolution of the objective, about 5e-10 log-lik, therefore leaves raw gradients of
0.02–0.18 even at the optimum. Sonnet correctly escalated rather than weakening the test.

**Evidence (read-only, 8 fits: S1/S2 × N=64/300 × B1/B2, current code 5d1f4ea).**
- **Hessian:** positive definite on the active coordinates in all 8 fits. The smallest eigenvalue is 0.16, on a null B2 fit with a weak τ_F.
- **Newton decrement:** g′H⁻¹g/2 between 7.6e-10 and 6.8e-9 log-lik units.
- **False alarms:** the raw-gradient flag fires on every N=300 fit (|g| 0.017–0.052).
- **Null-case optima:** under the null, 3 of 5 B2 starts reach the best and the others are genuine secondary τ_F optima, as expected (L4).

**Decision D22.**
1. **Replace the flag.** Remove the `large_projected_gradient` flag and its gradient clause. Add a **Newton-decrement certificate**
   on the selected solution only, not every start: `newton_decrement = ½ gᵀH⁻¹g` in absolute log-lik units. It is computed on
   the active free coordinates (inside bounds; τ_F excluded when σ²_F = 0, τ_R excluded when inactive). H is the symmetrised
   central-difference Jacobian of the analytic gradient (step 1e-5·max(1,|x|)), about one gradient per active coordinate.
   The flag is `newton_decrement_large` if the decrement exceeds **1e-3**. If H on the active set is not positive definite,
   record `hessian_not_pd` and report the decrement as NA. The raw absolute projected gradient stays as a recorded diagnostic.
   For an embedded-null B2, reuse the B1 certificate.
2. **Revised unblock criterion 2 (re-smoke):**
   - 0 job errors, and every fit converged (scipy CONVERGENCE message, or embedded null).
   - Newton decrement ≤ 1e-3 in every fit with a positive-definite active Hessian.
   - `hessian_not_pd` is allowed only for B2 fits with σ̂²_F < 0.02, where τ_F may be flat. Any other occurrence escalates to Opus.
   - In every S1 B2 fit, at least 3 of 5 starts are within 0.01 log-lik of the best.
3. **Tests.** Rewrite the failing slow test to assert decrement ≤ 1e-3, not the raw gradient. Add a unit test: at a point displaced
   slightly from an optimum, the decrement matches the actual log-lik gap within 20% on a small dataset. Add a test that
   `hessian_not_pd` is set when H is made indefinite (monkeypatched H).
4. **Unchanged:** criteria 1, 3, 4 and 5, D19 (stopping rule), Stage 2 as approved (B=49), and every scientific setting.
5. **Cost:** about 18 gradient evaluations (~1 s) per selected fit. That is negligible against the ~66 s B2 fit, and the 15.2 CPU-h Stage 2 projection stands.

This changes a numerical diagnostic, not the model, estimator, inference or thresholds. Opus decides it within the
routing policy, and it is shown here for your approval. Next: Opus persists D22 and the H2c handoff, then hands off to
Sonnet, which implements D22, runs the full suite, the re-smoke (C5) and the criteria check, then Stage 2.

---

## Addendum — H3 OPUS REVIEW OF STAGE 2 + STAGE 3 APPROVAL REQUEST (2026-09-30)

Reviewer: Opus 5.5 in Plan Mode, High effort (verified via `get_session`; Plan Mode entered with EnterPlanMode).
Inputs: `results/experiment_01/diagnostic/eeb188ecc6/` (every job envelope and the summary), `docs/experiment_01_diagnostic_report.md`, and code at `38c0531`.

## A. What Stage 2 does and does not support (3 replications per scenario at N=300; descriptive only)
**The estimator works as intended.**
- Fits: 521/521 jobs ok, 100 % convergence, and all 5 starts reach the same optimum in every cell. The Newton decrement is at most 2e-4, and no Hessian is non-positive-definite.
- Clean-scenario recovery: in S1, σ̂²_F is 0.140, 0.138 and 0.206 (truth 0.16; bias +0.002 ± 0.022). The mean and kernel parameters recover within about 1 MCSE.
- Nested models: B0 is biased (ᾱ +0.18), which is the expected cost of omitting fast recency. B1 − B0 held-out scores are +33 to +127 per learner.
- Null test: it separates S1 (CLR 622–1114, far above the bootstrap-null 99 % quantiles of 127–189) from S2 (CLR 0 in 3/3).

**Limitations found in Stage 2** (these carry into Stage 3 and the final report):
- **L6, the near-white pathway.** In S8n rep 2 there is no F, yet σ̂²_F = 0.046 with τ̂_F = 0.05 min, at the lower bound and below the shortest design lag of 0.4 min. A near-white F is identified only through the marginal probit scale, which the known difficulties anchor. It can therefore absorb misspecification of the latent marginal distribution, such as non-Gaussian gains. S4a shows the same pathway recovering a genuine near-white F (τ̂_F 0.06–0.32 against a true 0.2). **The estimator cannot tell a genuine white-noise transient from marginal misfit.**
- **L7, outcome-driven context (S7).** σ̂²_F is about 0.30 (truth 0.16) with τ̂_F 64–109 min, a negative r̄, and τ_R at its 120-min bound. Error-triggered shifts look to B2 like a large, persistent F. **A positive σ̂²_F does not show that the state is exogenous to practice.**
- **L8, trade-off with recency when recency is absent (S3).** σ̂²_F is 0.134, 0.118 and 0.128 (bias −0.034, about 7 MCSE). The unused recency terms absorb part of F's short-lag covariance: r̄ goes negative, and in one fit σ²_r hits its upper bound of 2.
- **Gain misspecification (S8).** σ²_F is attenuated (−0.039) while σ²_r is inflated. Correlated session starts (S6) and a near-session-intercept F (S4b) increase the spread of σ̂²_F, and τ_F is poorly determined when τ_F = 60.
- **τ_F inference.** The sandwich SE for τ_F is about half the learner-bootstrap SD (ratio 0.46), and for σ²_F it is about 10 % too small (0.90). There will be no τ_F interval claims.
- **Reporting defect (C6).** Wald intervals for σ²_F near 0 are meaningless: S8n rep 0 gives an upper limit of 5e70. Coverage for S1 was unaffected.

**Verdict: ready for Stage 3 with stated limitations.** No estimator defect remains. C6–C8 below are reporting and runner changes only.

## B. Corrections before freezing (Sonnet; within the approved design)
- **C6.** Report a Wald CI for a variance only when estimate > 2·SE. Otherwise record `NA (near boundary)`, and count such fits as non-covering in unconditional coverage.
- **C7.** Allow a per-dataset `B` in `null_bootstrap.datasets` (B = 99 for S2/S8n, B = 19 for S1/S8) and an `N` per learner-bootstrap dataset.
- **C8.** Make `summarize` compute the pre-registered decision rules PH1–PH6 below automatically, plus a near-white indicator: the share of B2 fits with σ̂²_F > 0 and τ̂_F < 0.4 min.
- **Tests and freeze.** Add tests for C6–C8 and run the full suite. Then write `configs/experiment_01/stage_confirmatory.yaml` with `frozen: true`, record its sha256 and the git commit, and dry-run it. Do not run it.

## C. Stage 3 protocol requested for approval (frozen; the confirmatory run is local, on your Windows machine)

**Hypotheses and decision rules.** All are fixed now, before any Stage 3 data exist. The 95 % Monte Carlo CI is bias ± 1.96·MCSE, and rates carry Clopper–Pearson (CP) 95 % limits.

| ID | Claim tested (B2 vs B1, under the simulated assumptions only) | Cells | Rule |
|---|---|---|---|
| PH1 | σ²_F is recovered without material bias in the clean process | S1, each N | pass: MC CI of bias ⊂ [−0.04, 0.04]; fail: MC CI disjoint from it; otherwise inconclusive |
| PH2 | The boundary-aware test detects σ²_F = 0.16 | S1, 10 datasets per N | reported rejection rate with CP limits (power) |
| PH3 | The test does not produce excess false positives when F is absent | S2, 20 datasets (10 per N) | "evidence of excess false positives" if the pooled CP lower bound > 0.05 (≥ 4/20); otherwise "no evidence", reporting the upper bound (e.g. 0/20 → 0.14). The distribution of σ̂²_F is reported (share = 0, mean, 90th percentile) |
| PH4 | Misspecified, correlated gains are not falsely attributed to F | S8n, same as PH3 | PH3 rule, plus the near-white share |
| PH5 | Robustness of σ²_F recovery to non-Gaussian, correlated gains | S8, each N | PH1 rule, labelled secondary robustness |
| PH6 | B2 improves the held-out population-marginal pairwise composite score | S1 (improvement); S2/S8n (spurious superiority) | S1: improvement if the MC CI of the mean per-learner difference > 0. S2/S8n: spurious if the MC CI > 0 |

**Secondary, descriptive only:**
- τ_F bias, RMSE and SD in S1 where σ̂²_F > 0. No τ_F coverage claim.
- Sandwich coverage of σ²_F in S1, conditional and unconditional.
- One learner bootstrap (B = 50) on S1, N = 1000, rep 0, as a sandwich check.
- **MDE (resolves D21):** dropped as a confirmatory criterion. It is reported as design-based detectability only: predicted SE at σ²_F = 0.04 is 0.034 (N=300) and 0.019 (N=1000), shown with the empirical SD of σ̂²_F in S1. No empirical claim is made at 0.04.

**Matrix.**
- **Scenarios:** S1, S2, S8, S8n.
- **Sample sizes:** N_fit ∈ {300, 1000} fitting learners, plus 300 held-out learners per dataset. Totals are reported separately.
- **Replications:** R = 20 per cell, giving 160 fit jobs (B0/B1/B2 × 5 starts = 2,400 starts, sandwich for B1/B2).
- **Null tests:** on reps 0–9 of each cell. B = 99 for S2/S8n (40 datasets → 3,960 replicates) and B = 19 for S1/S8 (40 → 760 replicates), about 47,200 starts. With B = 19 the minimum p is 0.05; α = 0.05.
- **Seed and estimator:** master seed 20261201. Estimator = code at the post-C6–C8 commit, with D13/D19/D22 and the Stage 2 settings. The config sha256 is recorded before handoff.

**Cost (measured: fit job 110 s, null replicate 78 s, per core; N=1000 not yet timed, ±30 %):**
- Fits: about 5.3 CPU-h. Null replicates: about 102 CPU-h. Learner bootstrap: about 0.3 CPU-h. **Total about 108 CPU-h.**
- Wall time on your machine is about 108 / workers hours: roughly 27 h on 4 workers, 14 h on 8. The run resumes after interruption, and nothing auto-advances.

**Deviations from your prompt.**
- The null tests use B = 99 and B = 19 rather than the provisional B = 199. The tests run on 10 of the 20 datasets per cell, not all.
- S8n is added (your choice). There are 20 replications instead of the minimum 10.
- The MDE is dropped as a criterion (D21).
- Earlier method decisions still apply: the D19 stopping rule, the D22 certificate, the D13 start policy, and a stopping-rule tolerance of 1e-3.

**Local execution procedure** (Sonnet provides the exact commands):
1. `git pull` the frozen commit.
2. In `.venv12`, run `python -m pytest -q`. It must pass; if anything fails, stop and report.
3. Run `python -m kt_trial run --config configs/experiment_01/stage_confirmatory.yaml --frozen-sha256 <sha> --workers <cores>`.
4. Run `summarize` on the results directory.
5. Commit and push `results/experiment_01/confirmatory/` (about 25 MB) to the branch, or tell me its location.

Your local numpy 2.5.3 / scipy 1.18.1 differ from the container's 2.4.6 / 1.17.1. The versions are recorded in the manifest, and they do not change the protocol.

**Handoffs after approval.**
- H4: Opus (execution) persists this request as D23–D25 and hands off to Sonnet. Sonnet does C6–C8, the tests, the freeze and the dry-run, then gives you the commands. Opus does not run the confirmatory matrix.
- H5: after your local run, you switch to Opus in Plan Mode for the final interpretation.

**Status: Stage 3 protocol APPROVED by the user on 2026-09-30 (plan approval). Frozen config not yet written.**

---

## Addendum — H6 OPUS FINAL INTERPRETATION OF STAGE 3 (2026-10-02)

Input: the user's local confirmatory run (commit `97d67a9`, `results/experiment_01/confirmatory/1b1307a48a/`), with 4,930/4,930 jobs ok and 0 errors.

**Provenance (D29–D31).**
- The code-hash difference is reproduced exactly as CRLF line endings of the frozen `kt_trial/*.py`, so the code is unchanged.
- The dirty flag comes from untracked files.
- One immaterial certificate flag (S8n N=1000 rep 13).
- The nuisance gain-variance references in S8/S8n were corrected in the report only.

**Verdict (D32).** H1 is supported for σ²_F under the simulated assumptions; τ_F is weakly determined.
- **PH1:** pass at N=300 and N=1000.
- **PH2:** 20/20 rejections.
- **PH3/PH4:** no evidence of excess false positives (0/20 each, CP upper 0.17).
- **PH5:** inconclusive at N=300 and pass at N=1000, with a systematic 13–15 % attenuation.
- **PH6:** held-out improvement in S1 and no spurious superiority in S2/S8n.

Claims, limitations L1–L10, deviations and recommendations are in `docs/experiment_01_final_report.md`. No code, config or result was changed.
