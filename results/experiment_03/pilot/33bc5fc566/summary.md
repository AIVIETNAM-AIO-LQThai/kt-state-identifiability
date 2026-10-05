# Experiment 3 summary: recovery of the shared transient latent state F with unknown item difficulties

- stage `pilot`, config hash `33bc5fc56650`, code hash `0e175b32e066`
- env: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20, 'threads': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}}
- job accounting: {'jobs': 64, 'ok': 64, 'errors': 0}

## U1|N=1000  (3 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 3 | 0.1660 | 0.0060 (0.0036) | 0.0062 | 0.0079 | 0.00 | 8.94 | 1.00 | 0.00 | 0.00000 | 32, 53 | NA |
| cal | 3 | 0.2618 | 0.1018 (0.0275) | 0.0477 | 0.1089 | 0.00 | 5.13 | 1.00 | 0.00 | 0.00000 | 34, 51 | 0.206 |
| free | 3 | 0.1560 | -0.0040 (0.0042) | 0.0073 | 0.0072 | 0.00 | 9.68 | 1.00 | 0.00 | 0.00000 | 80, 107 | 0.044 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 1.17 (n = 3; bootstrap CI None); design ratio about 0.57 at tau_F = 10.

## U1|N=300  (3 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 3 | 0.1519 | -0.0081 (0.0313) | 0.0543 | 0.0450 | 0.00 | 10.06 | 1.00 | 0.00 | 0.00000 | 32, 51 | NA |
| cal | 3 | 0.3561 | 0.1961 (0.0412) | 0.0714 | 0.2045 | 0.00 | 3.35 | 1.00 | 0.00 | 0.00000 | 38, 53 | 0.191 |
| free | 3 | 0.1620 | 0.0020 (0.0112) | 0.0194 | 0.0159 | 0.00 | 8.73 | 1.00 | 0.00 | 0.00000 | 85, 104 | 0.093 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 0.36 (n = 3; bootstrap CI None); design ratio about 0.57 at tau_F = 10.

## U2|N=1000  (3 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 3 | 0.0138 | 0.0138 (0.0069) | 0.0120 | 0.0169 | 0.33 | 0.37 | 1.00 | 0.00 | 0.00000 | 30, 53 | NA |
| cal | 3 | 0.3090 | 0.3090 (0.1036) | 0.1795 | 0.3420 | 0.00 | 0.05 | 1.00 | 0.00 | 0.00000 | 35, 60 | 0.205 |
| free | 3 | 0.0081 | 0.0081 (0.0045) | 0.0078 | 0.0103 | 0.00 | 42.75 | 1.00 | 0.00 | 0.00000 | 83, 87 | 0.038 |

## U2|N=300  (3 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 3 | 0.0104 | 0.0104 (0.0053) | 0.0092 | 0.0128 | 0.33 | 3.67 | 1.00 | 0.00 | 0.00000 | 33, 54 | NA |
| cal | 3 | 0.1668 | 0.1668 (0.0942) | 0.1632 | 0.2135 | 0.00 | 0.27 | 1.00 | 0.00 | 0.00000 | 37, 68 | 0.193 |
| free | 3 | 0.0293 | 0.0293 (0.0286) | 0.0496 | 0.0500 | 0.33 | 40.57 | 1.00 | 0.00 | 0.05418 | 96, 79 | 0.092 |

## U3|N=1000  (2 replications; true sigma2_F 0.16000000000000003, tau_F 1.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 2 | 0.1469 | -0.0131 (0.0010) | 0.0015 | 0.0131 | 0.00 | 1.22 | 1.00 | 0.00 | 0.00000 | 33, 54 | NA |
| free | 2 | 0.1577 | -0.0023 (0.0439) | 0.0621 | 0.0440 | 0.00 | 1.24 | 1.00 | 0.00 | 0.00000 | 85, 153 | 0.052 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 42.11 (n = 2; bootstrap CI None); design ratio about 0.57 at tau_F = 10.

## U3|N=300  (2 replications; true sigma2_F 0.16000000000000003, tau_F 1.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 2 | 0.0937 | -0.0663 (0.0208) | 0.0294 | 0.0695 | 0.00 | 1.26 | 1.00 | 0.00 | 0.00000 | 33, 60 | NA |
| free | 2 | 0.1247 | -0.0353 (0.0220) | 0.0310 | 0.0416 | 0.00 | 1.05 | 1.00 | 0.00 | 0.00000 | 85, 143 | 0.124 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 1.06 (n = 2; bootstrap CI None); design ratio about 0.57 at tau_F = 10.

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | arm | CLR obs | B ok/failed | p | min p | reject | s/replicate |
|---|---|---|---|---|---|---|---|
| U2 N=300 rep=0 | free | 1.98 | 19/0 | 0.150 | 0.050 | False | 212 |
| U2 N=300 rep=0 | known | 9.36 | 5/0 | 0.500 | 0.167 | False | 74 |
| U2 N=1000 rep=0 | free | 1.44 | 19/0 | 0.400 | 0.050 | False | 204 |
| U2 N=1000 rep=0 | known | 50.34 | 5/0 | 0.500 | 0.167 | False | 67 |
