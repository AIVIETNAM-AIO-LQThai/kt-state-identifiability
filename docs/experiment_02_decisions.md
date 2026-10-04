# Experiment 2: decision and findings log

IDs use the prefix X2 so they cannot be confused with Experiment 1's D-series. F is a statistical component, never a psychological label.

## Approved by the owner (Opus H7 plan approval, 2026-10-04; details in `docs/experiment_02_protocol.md` section 8)
| ID | Decision |
|---|---|
| X2-D01 | Question: MMSE-defined information in F at prediction time, gap decomposition (bound looseness | ADF approximation | estimated population parameters), causal next-answer value of transient information, null safety, ideal pre-answer indicators. Known item difficulties (unknown b is Experiment 3). |
| X2-D02 | Scenarios: S1, S2, S8n core; S8 ADF-only, descriptive. Known-parameter arms only where the model is exact (S1, S2). |
| X2-D03 | Primary tracking contrast B2-full vs B2-priorF (F replaced at prediction time by its prior N(0, sigma2_F), persistent block untouched). B2-white and B2-F0 are diagnostics; B2-F0 alone confounds variance with tracking. Oracle-F is the ceiling. |
| X2-D04 | Indicators O = F + nu, reliability 0.3 and 0.6, known noise, observed before the answer; S1 only; indicator-only baseline required; not run in S2/S8n (reliability undefined when var F = 0). |
| X2-D05 | Reference: Rao-Blackwellised fully adapted SMC over latent utilities (not prefix GHK); validation subset 2 learners per template per replication, S1 N=1000; production all S1 N=1000 held-out learners at a validated particle count. |
| X2-D06 | Rules R1 (reference gate), R2 (ADF approximation), R3 (null safety); everything else continuous and descriptive. The proposed "efficiency >= 0.9" and "10% of S1" rules are not used. |
| X2-D07 | Experiment-1 numerical addendum: 53 datasets, original outputs preserved, separate document. |
| X2-D08 | Total compute cap 12 CPU-h, benchmarks first, owner's PC for the production runs. |
| X2-D09 | Code in the new package `transient_filtering/` on branch `exp/transient-state-filtering` (owner-requested purpose names); `kt_trial/` untouched. |

## Implementation-level decisions (Sonnet, within the approved scope)
| ID | Decision | Why |
|---|---|---|
| X2-I01 | Position bins use the 0-based within-session index j: first answer j=0, j=1..4, j=5..15, j=16..31, probes separate; "practice" (96) and "all" (112) are the headline aggregates. Each value is a learner-level mean over bin positions (equal position weights); template weights follow the learner mix. | Stated in the protocol as positions 1-4, 5-15, 16-31 after the first answer; made explicit and 0-based. |
| X2-I02 | Uncertainty units: fitted arms use the replication as the unit (t interval over replications); pooled learner CIs (cluster on learner) are reported alongside; known-parameter arms are pooled over independent evaluation learners. | Protocol section 5. |
| X2-I03 | Null persistence statistics: lag-1 autocorrelation of the post-answer estimate over consecutive same-session positions and run length of |m| > 0.2 (half the S1 scale 0.4). Energy is in absolute units. | Replaces the unspecified threshold in the protocol with an explicit one. |
| X2-I04 | Reference particle count is a tuning parameter chosen to satisfy R1. In the pilot 16,384 particles gave a single-run RMS MC SD of p of 0.0012 (> 0.001); because the error scales as 1/sqrt(Np), 32,768 particles is expected to meet the gate (about 0.00085). Production run cost at 32,768 particles stays under 1 CPU-h. | R1 is not weakened; the sample size is set from the measured error. |
| X2-I05 | The runner's LF-normalised code hash covers `kt_trial/*.py` and `transient_filtering/*.py`; Experiment 1's own code hash and freeze record are unchanged. | Avoids the CRLF provenance issue found in Experiment 1 (P1). |
| X2-I06 | Pilot evaluation learners come from a fresh namespace under the Experiment-2 master seed (data_source = fresh). The production source is an open decision for the owner (see F7). | The container cannot reproduce the Experiment-1 data. |

## Findings
| ID | Finding | Evidence |
|---|---|---|
| X2-F7 | **The cloud container does not reproduce the Experiment-1 datasets.** Template assignment, the RNG stream, alpha and r and the learners' mean mastery regenerate exactly (corr_alpha_r, corr_alpha_meanM0, cv_alpha, cv_r agree to ~1e-16), while the per-skill baseline mastery differs, so responses and log-likelihoods differ (B0 by ~900, B1 by ~1,560 at S1 N=300 rep 0). Cause: the generating Sigma_M = 0.8 I + 0.1 11' has the eigenvalue 0.8 three times, and numpy's `multivariate_normal(method="svd")` chooses a build-dependent basis of that eigenspace. Container: numpy 2.4.6; Experiment 1 ran on numpy 2.5.3 / Windows. | `python -m transient_filtering fingerprint` (container) and the check `tests/test_transient_filtering.py::test_regeneration_build_independent_quantities_match_saved`. **Not yet checked on the owner's PC**, which is the environment that produced the data. |
| X2-F8 | Information bound reproduced independently: the covariance-form recursion equals the direct inversion of the joint information matrix to ~1e-16, and reproduces the earlier figures: answers only 0.1151 / 0.1464 (pre / post, 112 positions), 0.1135 / 0.1436 (practice only); indicators 0.5534 / 0.5635 (rho 0.3), 0.7531 / 0.7564 (rho 0.6); indicator-only 0.5425 / 0.7515. | tests `test_bound_*` |
| X2-F9 | Generator checks independent of the shared kernel pass: a naive event loop recomputes H^s and H^f; empirical pair probabilities (four pair classes, 320k learners) match the analytic bivariate probabilities within 4.5 MC SE; S8 gain mean, variance and correlation with mastery match their analytic values; `keep_latent=True` changes no draw. | tests (two are marked slow) |
| X2-F10 | Pilot (container, fresh namespace, 2 replications per cell, indicative only): ADF with known parameters reaches post-answer R^2 0.155 against the bound 0.144-0.146 expected (sampling noise on 600 learners); the fitted ADF is at most 0.01 lower. Tracking value of F (full over priorF) is about 0.003 nats per response; oracle-F adds about 0.021; ideal indicators add 0.010 (rho 0.3) to 0.014-0.016 (rho 0.6) over the answers-only filter. In S2 and S8n the filter produces no tracking gain and near-zero excursion energy. | `results/experiment_02/pilot/0cc472d76b/summary.md` |
| X2-F11 | Reference gate in the pilot (32 learners, 16,384 particles, 10 seeds): R^2 single-run MC SD 0.0002 (pass), doubling stable (pass), min ESS 4,782, but p MC RMS 0.0012 (fails 0.001; see X2-I04). The ADF-minus-reference mean |dp| is 0.0031 and the reference-over-ADF log-loss gain is 0.0002 nats per response with a CI [-0.0002, 0.0006] too wide to decide R2 on 32 learners. | same summary |
| X2-F12 | Addendum benchmark (container, 2 datasets, single thread): about 145 s per dataset, so 53 datasets ~ 2.1 CPU-h (estimate was 3-4.5). Reproduction of the registered CLR is impossible in this container (F7); the benchmark validates the code path only. | scratchpad benchmark log |

## Opus H9 review decisions (2026-10-04; approved by the owner)
| ID | Decision |
|---|---|
| X2-D10 | **Evaluation data: fresh held-out learners** drawn from the unchanged Experiment-1 generator under a **new master seed 20261402** (data_source = fresh), never seen by the pilot. Independent of the frozen fits (trained on other learners). Reproducible bit-for-bit within the same numpy/LAPACK build; on another build an equally valid, different draw (X2-F7). Supersedes X2-I06 for production. Owner choice. |
| X2-D11 | **Venue:** Experiment-2 production runs in the cloud session, monitored by Sonnet (about 1.5 CPU-h). The Experiment-1 numerical addendum runs on the owner's PC, after `fingerprint` matches there. Supersedes the venue part of X2-D08; the 12 CPU-h cap stands. Owner choice. |
| X2-D12 | **R0 implementation-validity gate (new):** R^2 of the SMC reference and of the known-parameter ADF must not exceed the information bound by more than 2 learner-SE (S1, practice, pre and post). If R0 fails, no scientific claims are made; stop and escalate. Motivated by the pilot's ADF R^2 0.155-0.157 against a bound of 0.1436 (within 1.3 SE, so plausibly noise). |
| X2-D13 | Pre-freeze gaps G1-G8 and changes C1-C8 (protocol addendum H9): production reference on all S1 N=1000 held-out learners, R2 on those learners, dataset/fit provenance hashes, addendum summarizer (interprets only reproduced datasets), S8n rep-13 sensitivity, priorF-over-B1 pair, R1 at 32,768 particles. |

## Freeze record (Sonnet, 2026-10-04)
| ID | Record |
|---|---|
| X2-D14 | **Frozen Experiment-2 configuration**: `configs/experiment_02/stage_confirmatory.yaml`, sha256 `c8f8971c1475e8d9b4368476ea3b723e6faa1567a5bc9c9f4b19a8e6872a2556`; code commit `20283e6580be513c76f98be98eb6db7263c61df9` (docs-only commits follow); LF-normalised code hash (kt_trial + transient_filtering) `1ee7e3d9acff742a699ec9ebf4a5938241c19a7e0f2c2470b1e929f173bcf19e`; master seed 20261402; fresh evaluation learners (X2-D10). Matrix: 160 track jobs (S1, S2, S8n, S8 x N {300, 1000} x 20 reps), 10 R1 validation jobs, 20 production-reference jobs, 1 bound job; 32,768 particles. Dry-run: 191 jobs, 1.87 CPU-h (stop threshold 3 CPU-h; cap 12). Tests: 84 passed (full suite). Re-pilot (`results/experiment_02/pilot/5cc61cdae2`): 6/6 jobs ok, R0 passed, R1 passed at 32,768 particles (p MC RMS 0.00082). |
| X2-D15 | Experiment-1 addendum configuration `configs/experiment_01_addendum/addendum.yaml` sha256 `a4815bf4b1c29419ac0dbd3ce32449d7494af9024bc3f9e90f235259aa641ac7` (audit record; the addendum is run on the owner's PC after `fingerprint` matches). |
