# Experiment 1 — Shared transient latent state `F`: synthetic identifiability & recovery

**Status:** approved by the user on 2026-09-30 (plan-mode approval, including kernel, S6/S7/S8/S8n constructions, Stage 1 and the bounded Stage 2 budget). Stage 3 is **not** approved.

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
