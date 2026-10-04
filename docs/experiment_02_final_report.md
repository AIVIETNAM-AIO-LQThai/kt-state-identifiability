# Experiment 2: final report

**Individual tracking of the shared transient latent state F**

Final interpretation: Opus, 2026-10-04 (protocol `docs/experiment_02_protocol.md`; decisions X2-D01–X2-D16).
Frozen evaluation: `results/experiment_02/confirmatory/eb704015ce/` (branch `exp/transient-state-filtering`).

> **Scope.** These are statistical results for the simulated Experiment-1 process: a probit model with known item difficulties;
> baseline mastery, slow and fast learning gains; a session-resetting OU state F with σ²_F = 0.16 and τ_F = 10 min; and an exogenous
> 4-skill interleaved schedule. F is a covariance component of that simulation. It is not fatigue, stress, mood, attention, emotion or
> any other psychological construct. No real learners or real measurements were used. The "indicators" are ideal synthetic
> measurements of F, i.e. positive controls.

## Design (ADEMP)

**Aims.**
- E1: how much of a learner's current F is recoverable, separating information, approximation and estimation.
- E2: the causal next-answer forecasting value of transient information.
- E3: null safety.
- E4: persistent-state recovery (secondary).

**Data-generating mechanisms.**
- S1 (F present), S2 (F absent), S8n (F absent, lognormal gains correlated with mastery), S8 (F present, same gains; descriptive).
- Each fitted replication is evaluated on 300 **fresh held-out learners** from the unchanged generator (master seed 20261402, X2-D10).
- Population parameters are the frozen Experiment-1 fits (20 replications × N ∈ {300, 1000}), never refitted.

**Estimands.** Per position, averaged within learners, practice positions (96) are the headline; probes and session-position bins are also reported.
- R² = 1 − MSE(F̂)/σ²_F, before and after each answer.
- Paired causal log-loss differences, in nats per response.
- Excursion energy of the F estimate in the nulls.

**Methods** (all strictly causal):
- Gaussian assumed-density filter (ADF) with known or fitted parameters.
- B2-priorF: F's prior is used at prediction time (tracking withheld).
- B1, B2-white, B2-F0.
- Oracle-F (the true F supplied; ceiling).
- Ideal indicators (ρ 0.3 / 0.6): indicator-only and indicator + answers.
- A Rao–Blackwellised SMC reference (32,768 particles).
- The posterior Cramér–Rao bound (covariance form, cross-checked by direct inversion).

**Performance measures and uncertainty.**
- Fitted arms: the replication is the unit (t interval over 20 replications), with pooled learner CIs alongside.
- Known-parameter arms: pooled over independent evaluation learners.
- The SMC Monte Carlo error is controlled by gate R1.

## A. Validity of the run
**Provenance.** Everything matches the freeze record (X2-D14):
- config sha256 `c8f8971c…`;
- LF-normalized code hash `1ee7e3d9…`;
- git `77edb75`, clean, with only documentation after the freeze commit `20283e6`;
- numpy 2.4.6 / scipy 1.17.1;
- 191 of 191 jobs ok, 0 errors;
- 190 results carry evaluation-data and fit-envelope hashes (the bound job has none).

**Gates (all passed):**
- **R0:** no estimator exceeds the bound. On 6,000 learners the excess is −0.0006 to −0.0016 against a learner SE of 0.0044; the S1 track cells give the same result.
- **R1:** single-run Monte Carlo SD of p is 0.00081, the R² SD is 0.00006, doubling the particles stays within 2 SE, and the minimum ESS is 7,165.
- **R2:** mean |Δp| between the ADF and the reference is 0.0028. The reference's log-loss gain over the ADF is 6e-5 nats per response [3e-5, 9e-5], inside ±5e-4.
- **R3:** no spurious tracking gain in any of the four null cells, including the S8n rep-13 sensitivity analysis.

Every estimand is therefore interpretable as specified.

## B. Results (practice positions unless stated; S1 known difficulties; generating values of Experiment 1)
**1. Information decomposition** on 6,000 S1 N=1000 evaluation learners (R² = 1 − MSE/σ²_F):

| | before answer | after answer |
|---|---|---|
| information bound (any estimator) | 0.1134 | 0.1435 |
| reference (≈ Bayes-optimal) | 0.1128 | 0.1420 |
| ADF with known parameters | 0.1128 | 0.1420 |
| ADF with fitted parameters | 0.1118 | 0.1402 |

- Bound looseness is ≤ 0.002, within one learner SE, so the bound is essentially attained.
- The ADF approximation loss is about 0 (−0.00001 [−0.0001, 0.0001]).
- Population-estimation loss is 0.0017 [0.0006, 0.0029] after the answer (replication CI).
- **The answers themselves are the binding constraint.** Under this process a learner's transient state is only about 14 % recoverable after an answer and 11 % before it. Neither a better algorithm nor better population estimates can raise that.
- The answers-only R² is similar in the probe session: 0.153 after the answer, bound 0.164.

**2. Causal next-answer forecasting value,** in nats per response, against a baseline log-loss of about 0.46 for the fitted B2 filter:

| comparison | value |
|---|---|
| tracking value: B2-full over B2-priorF, fitted | 0.0029 [0.0026, 0.0032] (N=1000); 0.0030 [0.0026, 0.0034] (N=300) |
| persistent/calibration value of modelling F: priorF over B1 | 0.0005 / 0.0004 |
| total B2 over B1 | 0.0034 |
| perfect knowledge of F (oracle-F over B2-full) | 0.021 |

- The filter therefore realizes about 14 % of the perfect-information forecasting value, matching its R².
- The earlier rough "≈0.002 nats" figure had the right order of magnitude; the measured value is 0.003, about 0.6 % of the log-loss.
- Using fitted rather than known parameters costs 0.0002 (N=1000) to 0.0005 (N=300) nats.
- Probe sessions behave the same way: tracking 0.0035–0.0041, persistent part 0.0004–0.0006.

**3. Ideal pre-answer indicators** (positive controls that observe F directly):
- R² of the indicator alone is 0.545 / 0.753 (ρ 0.3 / 0.6). Adding answers raises it to 0.565 / 0.758, an increment of +0.020 / +0.005.
- The forecasting gain over answers-only is 0.0095 / 0.0145 nats, i.e. 3–5 times the tracking value available from answers.
- These figures say what an indicator of that reliability would be worth. They say nothing about whether any real measurement achieves it.

**4. Null safety:**
- S2 and S8n produce no spurious forecasting gain (R3).
- Transient-estimate energy is ≤ 1e-4, i.e. an RMS of about 0.01, about 2.5 % of the S1 F scale, and no run ever exceeds |m| > 0.2.
- The lag-1 values (uncentred ratios of tiny estimates) carry no practical meaning.
- The only loss from fitted parameters in the nulls (0.00015–0.0005 nats) comes from persistent-parameter estimation.

**5. Misspecified gains (S8, descriptive):**
- Fitted R² falls to 0.124 after the answer, against 0.140 in S1.
- The tracking value falls to 0.0022 (about 25 % less).
- F-interval coverage drops to 0.86–0.88.
- Gain misspecification degrades tracking but does not reverse it.

**6. Calibration and persistent states:**
- 90 % F intervals cover 0.90 with known parameters, 0.90 at N=1000 fitted and 0.877 at N=300 fitted.
- M0 posterior MSE is about 0.16, against a prior variance of 0.9.
- B1 under-covers M0 (0.87–0.88), consistent with ignoring the within-session correlation.

## C. Interpretation (claims bounded to the simulated assumptions)
**Supported:**
1. With binary answers, known item difficulties, this schedule and σ²_F = 0.16, τ_F = 10 min, the individual transient state is weakly recoverable: R² ≈ 0.11 before and 0.14 after an answer. This is a property of the observation channel, because the information bound is essentially attained.
2. A Gaussian ADF is effectively Bayes-optimal here, both for state estimates and for causal predictive probabilities. Estimating the population parameters costs little, especially at N=1000.
3. The causal forecasting value of tracking F from answers is real but small, about 0.003 nats per response. Perfect state information would be worth about 0.021, and an ideal indicator of reliability 0.3–0.6 about 0.010–0.015.
4. Under the null and under gain misspecification without F, a filter using the frozen fits does not create spurious transient tracking.

**Not supported or out of scope:**
- Any statement about real learners, real indicators, or the psychological meaning of F.
- Generality to other σ²_F, τ_F, response spacing, unknown difficulties, adaptive (non-exogenous) schedules, non-reset or outcome-driven processes. The information available scales with these, so the numbers are conditional on them.
- "Practical usefulness". Whether 0.003 nats (0.6 % of log-loss) matters educationally is the owner's judgement; it is reported continuously as agreed.

**Recommendation for the next step.**
- The algorithm and population side under known b is closed: there is no headroom.
- The open uncertainties are (i) the population claim without known difficulties (L6 near-white pathway, item misfit), which is Experiment 3, and (ii) whether any obtainable observation carries information about F. The indicator arms show what reliability would be needed.
- I recommend Experiment 3: unknown b with item misfit, population recovery and null safety. It is proposed in a separate Opus protocol discussion, not started now.

## Limitations
1. **Conditional numbers.** The recoverable fraction of F depends on σ²_F, τ_F relative to the response spacing (about 1 min), the schedule, the item difficulty range and the gain distribution. The values above hold for the Experiment-1 generating point only.
2. **Known item difficulties and an exogenous schedule.** Unknown difficulties change population identification (Experiment-1 L6). Adaptive item selection would invalidate the template pair-count population estimator, though not the filters themselves.
3. **Clean session reset and a Gaussian process.** The S8 results show that misspecified gains degrade tracking. Outcome-driven or non-resetting context processes were not tested in Experiment 2.
4. **The indicators are ideal.** O = F + Gaussian noise, with known reliability, observed before the answer. Nothing here shows that any real signal measures F.
5. **Evaluation data are build-dependent** (X2-F7). The fresh learners are reproducible bit for bit in the run environment (numpy 2.4.6) and statistically equivalent elsewhere.
6. **Not all statements are rule-based.** The bin-level R² and the lag-1 statistics are descriptive. Only R0–R3 were prespecified decision rules.

## Deviations from the approved protocol (all decided before the confirmatory data existed)
- Fresh evaluation learners instead of the regenerated Experiment-1 held-out sets (X2-D10, owner).
- Cloud venue (X2-D11, owner).
- R0 implementation-validity gate added (X2-D12).
- Production reference on all S1 N=1000 learners, and R2 evaluated there (X2-D13).
- 32,768 particles, sized to R1 (X2-I04).

## Next steps
- The Experiment-1 numerical addendum runs on the owner's PC (`docs/experiment_02_pc_instructions.md`), then Opus interprets it.
- A separate protocol discussion should take up Experiment 3: unknown item difficulties with item misfit, population recovery and null safety.
