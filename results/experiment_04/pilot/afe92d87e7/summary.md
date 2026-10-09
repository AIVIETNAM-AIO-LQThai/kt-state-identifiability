# Experiment 4 summary: recovery of F with unknown item difficulties and discriminations

- stage `pilot`, config hash `afe92d87e752`, code hash `30c082b3cf49`
- env: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20, 'threads': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}}
- job accounting: {'jobs': 24, 'ok': 24, 'errors': 0}; CPU 7.42 h

## V1|N=1000  (3 replications; mean sigma2_F* 0.1600, mean g 1.0000)

| estimator | error vs sigma2_F* (mean / SD) | share at 0 | tau_F mean | b RMSE | lambda RMSE (centred log) | B2 converged / flagged | newton dec. large | not PD | starts<3/5 (B1, B2) | max Newton dec. | s/fit B1, B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free1 | 0.0050 / 0.0076 | 0.00 | 10.47 | 0.050 | NA | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 98, 144 |
| twopl | 0.0013 / 0.0070 | 0.00 | 10.49 | 0.102 | 0.152 | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 283, 397 |

2PL: lambda corr with truth NA; mean items with |log lambda-hat| > log 4: 0.00; fits with many extreme lambda: 0

## V1|N=300  (3 replications; mean sigma2_F* 0.1600, mean g 1.0000)

| estimator | error vs sigma2_F* (mean / SD) | share at 0 | tau_F mean | b RMSE | lambda RMSE (centred log) | B2 converged / flagged | newton dec. large | not PD | starts<3/5 (B1, B2) | max Newton dec. | s/fit B1, B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free1 | 0.0105 / 0.0171 | 0.00 | 9.98 | 0.097 | NA | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 98, 144 |
| twopl | 0.0076 / 0.0178 | 0.00 | 10.12 | 0.184 | 0.244 | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 305, 458 |

2PL: lambda corr with truth NA; mean items with |log lambda-hat| > log 4: 0.00; fits with many extreme lambda: 0

## V5|N=1000  (3 replications; mean sigma2_F* 0.1426, mean g 0.9439)

| estimator | error vs sigma2_F* (mean / SD) | share at 0 | tau_F mean | b RMSE | lambda RMSE (centred log) | B2 converged / flagged | newton dec. large | not PD | starts<3/5 (B1, B2) | max Newton dec. | s/fit B1, B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free1 | -0.0086 / 0.0028 | 0.00 | 10.20 | 0.156 | NA | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 88, 139 |
| twopl | -0.0041 / 0.0090 | 0.00 | 10.02 | 0.113 | 0.154 | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 270, 476 |

2PL: lambda corr with truth 0.87; mean items with |log lambda-hat| > log 4: 0.00; fits with many extreme lambda: 0

## V5|N=300  (3 replications; mean sigma2_F* 0.1473, mean g 0.9593)

| estimator | error vs sigma2_F* (mean / SD) | share at 0 | tau_F mean | b RMSE | lambda RMSE (centred log) | B2 converged / flagged | newton dec. large | not PD | starts<3/5 (B1, B2) | max Newton dec. | s/fit B1, B2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| free1 | 0.0006 / 0.0021 | 0.00 | 10.11 | 0.195 | NA | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 102, 158 |
| twopl | 0.0006 / 0.0089 | 0.00 | 10.87 | 0.229 | 0.303 | 1.00 / 0.00 | 0 | 0 | 0, 0 | 0.00000 | 416, 570 |

2PL: lambda corr with truth 0.78; mean items with |log lambda-hat| > log 4: 1.00; fits with many extreme lambda: 0

## Warp units (observed CLR T and one bootstrap CLR T* per fresh null dataset; pilot, timing only)

| cell | estimator | datasets | T (values) | T* (values) | fit failures | not converged | mean s/dataset-unit (fit, replicate) | mean job s |
|---|---|---|---|---|---|---|---|---|
| V2|N=1000 | twopl | 3 | [3.5, 0.15, 2.05] | [2.93, 0.0, 0.95] | 0 | 0 | 591, 512 | 1103 |
| V2|N=300 | twopl | 3 | [3.41, 0.04, 1.02] | [0.0, 0.0, 0.01] | 0 | 0 | 791, 520 | 1311 |
| V4|N=1000 | twopl | 3 | [0.45, 1.54, 0.0] | [0.85, 4.37, 1.06] | 0 | 1 | 437, 439 | 1111 |
| V4|N=1000 | free1 | 3 | [1.96, 1.01, 0.0] | [0.0, 12.16, 2.39] | 0 | 0 | 119, 116 | 1111 |
| V4|N=300 | twopl | 3 | [0.01, 0.63, 1.64] | [0.0, 0.23, 2.2] | 0 | 0 | 554, 475 | 1229 |
| V4|N=300 | free1 | 3 | [0.0, 1.53, 0.1] | [1.04, 0.0, 0.0] | 0 | 0 | 99, 102 | 1229 |
