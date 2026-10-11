# Experiment 6, Step 1 of L1: approximation check G0-1b (X6-D07)

**G0-1b: PASSED** (complete: True). Rule: in E3 and E5, excess chi2/df of L1 <= 1/4 of L0's on the feedback-active and cross-session pairs, later-practice marginal error <= 0.0085; E1/E2 unchanged; E4 no worse than L0 (strict).

## chi2/df per pair (expected 1 for an exact model)

| cell | model | fb_active | within_session_other | cross_session |
|---|---|---|---|---|
| E1 | no_feedback_term | 0.972 | 0.995 | 0.975 |
| E1 | L0 | 0.972 | 0.995 | 0.975 |
| E1 | L1 | 0.972 | 0.995 | 0.975 |
| E2 | no_feedback_term | 0.948 | 1.044 | 0.970 |
| E2 | L0 | 0.948 | 1.044 | 0.970 |
| E2 | L1 | 0.948 | 1.044 | 0.970 |
| E3 | no_feedback_term | 5628.140 | 0.976 | 4306.345 |
| E3 | L0 | 156.593 | 0.976 | 115.713 |
| E3 | L1 | 4.157 | 0.976 | 2.618 |
| E4 | no_feedback_term | 14.653 | 0.918 | 12.233 |
| E4 | L0 | 1.396 | 0.918 | 1.333 |
| E4 | L1 | 0.950 | 0.918 | 0.948 |
| E5 | no_feedback_term | 4968.130 | 1.076 | 3836.938 |
| E5 | L0 | 159.575 | 1.076 | 94.879 |
| E5 | L1 | 4.578 | 1.076 | 2.542 |

## Marginal success-rate error by position category (mean |empirical - model|; RMS z)

| cell | model | later practice | session start | probe |
|---|---|---|---|---|
| E1 | L0 | 0.0021; 1.0 | 0.0017; 0.8 | 0.0023; 1.0 |
| E1 | L1 | 0.0021; 1.0 | 0.0017; 0.8 | 0.0023; 1.0 |
| E2 | L0 | 0.0021; 1.0 | 0.0023; 0.9 | 0.0022; 1.0 |
| E2 | L1 | 0.0021; 1.0 | 0.0023; 0.9 | 0.0022; 1.0 |
| E3 | L0 | 0.0171; 8.4 | 0.0017; 0.7 | 0.0020; 1.0 |
| E3 | L1 | 0.0040; 1.7 | 0.0017; 0.7 | 0.0020; 1.0 |
| E4 | L0 | 0.0023; 1.1 | 0.0020; 1.0 | 0.0022; 0.9 |
| E4 | L1 | 0.0021; 1.0 | 0.0020; 1.0 | 0.0022; 0.9 |
| E5 | L0 | 0.0177; 8.5 | 0.0026; 1.1 | 0.0024; 1.0 |
| E5 | L1 | 0.0040; 1.7 | 0.0026; 1.1 | 0.0024; 1.0 |

## Gate evaluation

- **E3**: excess_fb_active: {'L0': 155.59250691289176, 'L1': 3.1573406032085325, 'ratio': 0.020292369252564103, 'ok': True}; excess_cross_session: {'L0': 114.71318795112178, 'L1': 1.6176290117820842, 'ratio': 0.014101508646689697, 'ok': True}; marginal_later_practice: {'L0': 0.017148940444896562, 'L1': 0.003973941161223086, 'limit': 0.0085, 'ok': True}
- **E5**: excess_fb_active: {'L0': 158.5749561442216, 'L1': 3.578472508470009, 'ratio': 0.022566441735070955, 'ok': True}; excess_cross_session: {'L0': 93.87945057329655, 'L1': 1.5422431257005123, 'ratio': 0.016427909582794192, 'ok': True}; marginal_later_practice: {'L0': 0.017714764544769307, 'L1': 0.003963561081087083, 'limit': 0.0085, 'ok': True}
- **E1**: max_abs_change_chi2_per_df: 0.0; ok: True
- **E2**: max_abs_change_chi2_per_df: 0.0; ok: True
- **E4**: L1_minus_L0: {'fb_active': -0.4462369128572641, 'within_session_other': 0.0, 'cross_session': -0.3849072465779837}; ok: True

Stage-0 L0 numbers reproduced by the regenerated datasets (max |diff| of chi2/df): {'E1': 0.0, 'E2': 0.0, 'E3': 0.0, 'E4': 0.0, 'E5': 0.0}
