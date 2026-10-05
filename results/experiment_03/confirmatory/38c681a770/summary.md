# Experiment 3 summary: recovery of the shared transient latent state F with unknown item difficulties

- stage `confirmatory`, config hash `38c681a770cc`, code hash `f6ba8c2d030d`
- env: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20, 'threads': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}}
- job accounting: {'jobs': 2145, 'ok': 2145, 'errors': 0}

## A02|N=1000  (5 replications; true sigma2_F 0.16000000000000003, tau_F 0.2)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 5 | 0.1553 | -0.0047 (0.0051) | 0.0115 | 0.0113 | 0.00 | 0.25 | 1.00 | 0.00 | 0.00000 | 41, 64 | NA |
| free | 5 | 0.4889 | 0.3289 (0.3997) | 0.8937 | 0.8644 | 0.00 | 2.57 | 1.00 | 0.00 | 0.00000 | 69, 81 | 0.132 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 77.76 (n = 5; bootstrap CI [2.5829170169332625, 458.8263713884573]); design ratio about 0.57 at tau_F = 10.

## U1|N=1000  (20 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.1539 | -0.0061 (0.0049) | 0.0217 | 0.0221 | 0.00 | 10.84 | 1.00 | 0.00 | 0.00000 | 87, 141 | NA |
| cal | 20 | 0.3843 | 0.2243 (0.0309) | 0.1382 | 0.2616 | 0.00 | 3.86 | 1.00 | 0.00 | 0.00000 | 99, 140 | 0.196 |
| free | 20 | 0.1582 | -0.0018 (0.0022) | 0.0100 | 0.0099 | 0.00 | 10.26 | 1.00 | 0.00 | 0.00000 | 212, 315 | 0.052 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 0.46 (n = 20; bootstrap CI [0.338735139384975, 0.6455099734330225]); design ratio about 0.57 at tau_F = 10.

## U1|N=300  (20 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.1666 | 0.0066 (0.0075) | 0.0337 | 0.0335 | 0.00 | 9.16 | 1.00 | 0.00 | 0.00000 | 90, 137 | NA |
| cal | 20 | 0.4046 | 0.2446 (0.0285) | 0.1274 | 0.2743 | 0.00 | 3.14 | 1.00 | 0.00 | 0.00000 | 95, 130 | 0.205 |
| free | 20 | 0.1673 | 0.0073 (0.0048) | 0.0213 | 0.0220 | 0.00 | 9.03 | 1.00 | 0.00 | 0.00000 | 212, 313 | 0.099 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 0.63 (n = 20; bootstrap CI [0.4372861423147791, 0.9872499066627066]); design ratio about 0.57 at tau_F = 10.

## U2|N=1000  (20 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.0094 | 0.0094 (0.0042) | 0.0188 | 0.0206 | 0.60 | 7.07 | 1.00 | 0.00 | 0.00683 | 87, 108 | NA |
| cal | 20 | 0.2152 | 0.2152 (0.0206) | 0.0923 | 0.2333 | 0.00 | 0.14 | 1.00 | 0.00 | 0.00000 | 89, 153 | 0.197 |
| free | 20 | 0.1365 | 0.1365 (0.1239) | 0.5543 | 0.5572 | 0.35 | 110.83 | 1.00 | 0.00 | 0.04707 | 213, 248 | 0.080 |

## U2|N=300  (20 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.0070 | 0.0070 (0.0025) | 0.0113 | 0.0131 | 0.50 | 15.60 | 1.00 | 0.00 | 0.00132 | 92, 109 | NA |
| cal | 20 | 0.1832 | 0.1832 (0.0209) | 0.0935 | 0.2046 | 0.00 | 0.19 | 1.00 | 0.00 | 0.00000 | 94, 154 | 0.207 |
| free | 20 | 0.3603 | 0.3603 (0.2062) | 0.9221 | 0.9683 | 0.15 | 176.67 | 1.00 | 0.00 | 0.00765 | 213, 274 | 0.174 |

## U3|N=1000  (20 replications; true sigma2_F 0.16000000000000003, tau_F 1.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.1613 | 0.0013 (0.0056) | 0.0252 | 0.0246 | 0.00 | 1.06 | 1.00 | 0.00 | 0.00000 | 82, 138 | NA |
| free | 20 | 0.1755 | 0.0155 (0.0170) | 0.0760 | 0.0757 | 0.00 | 1.11 | 1.00 | 0.00 | 0.00000 | 204, 375 | 0.059 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 3.01 (n = 20; bootstrap CI [1.7721994348829226, 4.375963851569271]); design ratio about 0.57 at tau_F = 10.

## U3|N=300  (20 replications; true sigma2_F 0.16000000000000003, tau_F 1.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.1659 | 0.0059 (0.0101) | 0.0452 | 0.0445 | 0.00 | 1.02 | 1.00 | 0.00 | 0.00000 | 81, 136 | NA |
| free | 20 | 0.4391 | 0.2791 (0.1227) | 0.5488 | 0.6033 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00000 | 213, 365 | 0.150 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 12.14 (n = 20; bootstrap CI [4.55754749874242, 20.665229574804478]); design ratio about 0.57 at tau_F = 10.

## U4|N=1000  (20 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.0524 | 0.0524 (0.0168) | 0.0751 | 0.0900 | 0.45 | 7.58 | 1.00 | 0.00 | 0.00000 | 86, 118 | NA |
| free | 20 | 0.3692 | 0.3692 (0.2040) | 0.9125 | 0.9630 | 0.15 | 12.53 | 1.00 | 0.00 | 0.00093 | 203, 271 | 0.244 |

## U4|N=300  (20 replications; true sigma2_F 0.0, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.0839 | 0.0839 (0.0208) | 0.0929 | 0.1235 | 0.25 | 59.60 | 1.00 | 0.00 | 0.00000 | 84, 136 | NA |
| free | 20 | 0.2124 | 0.2124 (0.1505) | 0.6729 | 0.6894 | 0.35 | 102.16 | 1.00 | 0.00 | 0.00002 | 197, 260 | 0.223 |

## U5|N=1000  (20 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.2185 | 0.0585 (0.0292) | 0.1305 | 0.1400 | 0.00 | 8.05 | 1.00 | 0.00 | 0.00000 | 42, 65 | NA |
| free | 20 | 0.1461 | -0.0139 (0.0036) | 0.0163 | 0.0211 | 0.00 | 10.23 | 1.00 | 0.00 | 0.00000 | 94, 130 | 0.168 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 0.12 (n = 20; bootstrap CI [0.0809259383989498, 0.21766497683188252]); design ratio about 0.57 at tau_F = 10.

## U5|N=300  (20 replications; true sigma2_F 0.16000000000000003, tau_F 10.0)

| arm | n | sigma2_F mean | bias (MCSE) | SD | RMSE | share at 0 | tau_F mean | B2 converged | B2 flagged | max Newton dec. (B2) | mean s/fit (B1, B2) | b RMSE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 20 | 0.1615 | 0.0015 (0.0200) | 0.0893 | 0.0871 | 0.00 | 17.63 | 1.00 | 0.00 | 0.00000 | 62, 91 | NA |
| free | 20 | 0.1463 | -0.0137 (0.0049) | 0.0219 | 0.0254 | 0.00 | 10.19 | 1.00 | 0.00 | 0.00000 | 118, 152 | 0.183 |

H3f (descriptive): SD(sigma2_F-hat, free) / SD(known) on identical datasets = 0.25 (n = 20; bootstrap CI [0.1736022829366052, 0.35383567810717326]); design ratio about 0.57 at tau_F = 10.

## Boundary-aware null tests (parametric bootstrap, composite LR B2 vs B1)

| dataset | arm | CLR obs | B ok/failed | p | min p | reject | s/replicate |
|---|---|---|---|---|---|---|---|
| U1 N=300 rep=0 | free | 175.21 | 19/0 | 0.050 | 0.050 | True | 250 |
| U1 N=300 rep=1 | free | 153.72 | 19/0 | 0.050 | 0.050 | True | 245 |
| U1 N=300 rep=2 | free | 166.67 | 19/0 | 0.050 | 0.050 | True | 222 |
| U1 N=300 rep=3 | free | 179.11 | 19/0 | 0.050 | 0.050 | True | 185 |
| U1 N=300 rep=4 | free | 208.75 | 19/0 | 0.050 | 0.050 | True | 212 |
| U1 N=1000 rep=0 | free | 545.12 | 19/0 | 0.050 | 0.050 | True | 214 |
| U1 N=1000 rep=1 | free | 516.93 | 19/0 | 0.050 | 0.050 | True | 230 |
| U1 N=1000 rep=2 | free | 534.92 | 19/0 | 0.050 | 0.050 | True | 247 |
| U1 N=1000 rep=3 | free | 547.30 | 19/0 | 0.050 | 0.050 | True | 216 |
| U1 N=1000 rep=4 | free | 719.02 | 19/0 | 0.050 | 0.050 | True | 219 |
| U2 N=300 rep=0 | free | 0.76 | 39/0 | 0.500 | 0.025 | False | 238 |
| U2 N=300 rep=1 | free | 0.41 | 39/0 | 0.375 | 0.025 | False | 228 |
| U2 N=300 rep=2 | free | 0.34 | 39/0 | 0.575 | 0.025 | False | 243 |
| U2 N=300 rep=3 | free | 6.04 | 39/0 | 0.050 | 0.025 | True | 252 |
| U2 N=300 rep=4 | free | 0.66 | 39/0 | 0.425 | 0.025 | False | 311 |
| U2 N=300 rep=5 | free | 0.04 | 39/0 | 0.650 | 0.025 | False | 247 |
| U2 N=300 rep=6 | free | 2.47 | 39/0 | 0.225 | 0.025 | False | 237 |
| U2 N=300 rep=7 | free | 4.72 | 39/0 | 0.025 | 0.025 | True | 218 |
| U2 N=300 rep=8 | free | 1.95 | 39/0 | 0.200 | 0.025 | False | 194 |
| U2 N=300 rep=9 | free | 0.00 | 39/0 | 0.575 | 0.025 | False | 230 |
| U2 N=1000 rep=0 | free | 4.83 | 39/0 | 0.025 | 0.025 | True | 208 |
| U2 N=1000 rep=1 | free | 1.59 | 39/0 | 0.250 | 0.025 | False | 221 |
| U2 N=1000 rep=2 | free | 0.00 | 39/0 | 1.000 | 0.025 | False | 224 |
| U2 N=1000 rep=3 | free | 0.30 | 39/0 | 0.600 | 0.025 | False | 230 |
| U2 N=1000 rep=4 | free | 0.97 | 39/0 | 0.450 | 0.025 | False | 249 |
| U2 N=1000 rep=5 | free | 1.23 | 39/0 | 0.200 | 0.025 | False | 206 |
| U2 N=1000 rep=6 | free | 0.70 | 39/0 | 0.450 | 0.025 | False | 231 |
| U2 N=1000 rep=7 | free | 1.41 | 39/0 | 0.475 | 0.025 | False | 238 |
| U2 N=1000 rep=8 | free | 0.00 | 39/0 | 1.000 | 0.025 | False | 222 |
| U2 N=1000 rep=9 | free | 0.00 | 39/0 | 1.000 | 0.025 | False | 222 |
| U4 N=300 rep=0 | free | 0.48 | 39/0 | 0.450 | 0.025 | False | 209 |
| U4 N=300 rep=1 | free | 0.57 | 39/0 | 0.575 | 0.025 | False | 195 |
| U4 N=300 rep=2 | free | 0.00 | 39/0 | 1.000 | 0.025 | False | 250 |
| U4 N=300 rep=3 | free | 0.00 | 39/0 | 0.975 | 0.025 | False | 278 |
| U4 N=300 rep=4 | free | 0.53 | 39/0 | 0.425 | 0.025 | False | 281 |
| U4 N=300 rep=5 | free | 2.55 | 39/0 | 0.125 | 0.025 | False | 258 |
| U4 N=300 rep=6 | free | 0.59 | 39/0 | 0.475 | 0.025 | False | 306 |
| U4 N=300 rep=7 | free | 0.00 | 39/0 | 0.875 | 0.025 | False | 264 |
| U4 N=300 rep=8 | free | 4.11 | 39/0 | 0.050 | 0.025 | True | 251 |
| U4 N=300 rep=9 | free | 0.00 | 39/0 | 1.000 | 0.025 | False | 270 |
| U4 N=1000 rep=0 | free | 0.00 | 39/0 | 0.850 | 0.025 | False | 219 |
| U4 N=1000 rep=1 | free | 1.99 | 39/0 | 0.150 | 0.025 | False | 217 |
| U4 N=1000 rep=2 | free | 0.73 | 39/0 | 0.375 | 0.025 | False | 207 |
| U4 N=1000 rep=3 | free | 0.05 | 39/0 | 0.675 | 0.025 | False | 256 |
| U4 N=1000 rep=4 | free | 2.10 | 39/0 | 0.300 | 0.025 | False | 188 |
| U4 N=1000 rep=5 | free | 4.82 | 39/0 | 0.025 | 0.025 | True | 199 |
| U4 N=1000 rep=6 | free | 4.82 | 39/0 | 0.125 | 0.025 | False | 220 |
| U4 N=1000 rep=7 | free | 3.25 | 39/0 | 0.100 | 0.025 | False | 232 |
| U4 N=1000 rep=8 | free | 0.65 | 39/0 | 0.475 | 0.025 | False | 213 |
| U4 N=1000 rep=9 | free | 3.48 | 39/0 | 0.025 | 0.025 | True | 214 |
| U5 N=300 rep=0 | free | 224.87 | 19/0 | 0.050 | 0.050 | True | 222 |
| U5 N=300 rep=1 | free | 214.79 | 19/0 | 0.050 | 0.050 | True | 237 |
| U5 N=300 rep=2 | free | 154.48 | 19/0 | 0.050 | 0.050 | True | 244 |
| U5 N=300 rep=3 | free | 149.41 | 19/0 | 0.050 | 0.050 | True | 235 |
| U5 N=300 rep=4 | free | 168.57 | 19/0 | 0.050 | 0.050 | True | 195 |
| U5 N=1000 rep=0 | free | 706.30 | 19/0 | 0.050 | 0.050 | True | 221 |
| U5 N=1000 rep=1 | free | 538.72 | 19/0 | 0.050 | 0.050 | True | 217 |
| U5 N=1000 rep=2 | free | 495.77 | 19/0 | 0.050 | 0.050 | True | 233 |
| U5 N=1000 rep=3 | free | 531.99 | 19/0 | 0.050 | 0.050 | True | 211 |
| U5 N=1000 rep=4 | free | 649.46 | 19/0 | 0.050 | 0.050 | True | 175 |
## Pre-registered rules (X3-D12)

- all gates ok: **True**

| rule | result |
|---|---|
| PH3a U1 N=300 | verdict: pass; bias: 0.00725138351261112; mcse: 0.00475669313382826; mc_ci: [-0.0020717350296922694, 0.01657450205491451]; n: 20 |
| PH3a U1 N=1000 | verdict: pass; bias: -0.0018418790067802893; mcse: 0.002230481707983986; mc_ci: [-0.006213623154428902, 0.002529865140868323]; n: 20 |
| PH3b U2 free | verdict: no evidence of excess false positives (CP upper bound 0.38); rejections: 3; n: 20; cp95: [0.0320709371854637, 0.37892682654531396] |
| PH3c U4 free | verdict: no evidence of excess false positives (CP upper bound 0.38); rejections: 3; n: 20; cp95: [0.0320709371854637, 0.37892682654531396]; sigma2_F_hat_distribution: {'N=300': {'share_at_zero': 0.35, 'mean': 0.2124217906302816, 'p90': 0.49515569907696666, 'n': 20}, 'N=1000': {'share_at_zero': 0.15, 'mean': 0.36917634234050284, 'p90': 0.8753536692533419, 'n': 20}} |
| PH3d U5 N=300 | verdict: pass; bias: -0.013676984418422189; mcse: 0.004899736300725621; mc_ci: [-0.023280467567844406, -0.004073501268999972]; n: 20 |
| PH3d U5 N=1000 | verdict: pass; bias: -0.013869561773341393; mcse: 0.0036378531598668; mc_ci: [-0.020999753966680322, -0.006739369580002466]; n: 20 |
| PH3e U1 N=300 | verdict: inflation; mc_ci: [0.18485557961991816, 0.2912638208990418]; mean_difference: 0.23805970025947998 |
| PH3e U1 N=1000 | verdict: inflation; mc_ci: [0.1678056965066664, 0.2929655504525708]; mean_difference: 0.2303856234796186 |
| PH3e U2 N=300 | verdict: inflation; mc_ci: [0.13359499093167487, 0.21865430766026955]; mean_difference: 0.1761246492959722 |
| PH3e U2 N=1000 | verdict: inflation; mc_ci: [0.16362829025188402, 0.24804567863786098]; mean_difference: 0.2058369844448725 |
| PH3f U1 N=300 | sd_ratio_free_over_known: 0.6318283145259327; bootstrap_ci95: [0.4277823599474701, 0.9709297084245324]; bias_free: 0.007251383512611148; bias_known: 0.0065667596220540525 |
| PH3f U1 N=1000 | sd_ratio_free_over_known: 0.4586779492882892; bootstrap_ci95: [0.3341724434744234, 0.6376789929487531]; bias_free: -0.0018418790067802893; bias_known: -0.006105790456053473 |
| power U1 N=300 | rejections: 5; n: 5; cp95: [0.4781762498950185, 1.0] |
| power U1 N=1000 | rejections: 5; n: 5; cp95: [0.4781762498950185, 1.0] |
| power U5 N=300 | rejections: 5; n: 5; cp95: [0.4781762498950185, 1.0] |
| power U5 N=1000 | rejections: 5; n: 5; cp95: [0.4781762498950185, 1.0] |
| H3c U3 N=300 | arms: {'known': {'n': 20, 'bias': 0.005917966896988092, 'mcse': 0.010108131265727491, 'mc_ci': [-0.01389397038383779, 0.025729904177813973], 'sd': 0.045204937271315325, 'rmse': 0.04445598236696859, 'verdict': 'pass'}, 'free': {'n': 20, 'bias': 0.279122254545782, 'mcse': 0.12270919939250843, 'mc_ci': [0.03861222373646547, 0.5196322853550985], 'sd': 0.5487722226124495, 'rmse': 0.6033263111104784, 'verdict': 'inconclusive'}} |
| H3c U3 N=1000 | arms: {'known': {'n': 20, 'bias': 0.0013226368125976995, 'mcse': 0.005638074615061783, 'mc_ci': [-0.009727989432923394, 0.012373263058118793], 'sd': 0.025214236202988214, 'rmse': 0.02461136302753498, 'verdict': 'pass'}, 'free': {'n': 20, 'bias': 0.015520730023739493, 'mcse': 0.016991579792091205, 'mc_ci': [-0.017782766368759265, 0.04882422641623825], 'sd': 0.07598865492045535, 'rmse': 0.07567334374308335, 'verdict': 'inconclusive'}} |
| H3c A02 N=1000 | arms: {'known': {'n': 5, 'bias': -0.004721804662993184, 'mcse': 0.005139735150090444, 'mc_ci': [-0.014795685557170453, 0.005352076231184085], 'sd': 0.011492797181947317, 'rmse': 0.011312070938946818, 'verdict': 'pass'}, 'free': {'n': 5, 'bias': 0.32892501245698613, 'mcse': 0.3996605398795889, 'mc_ci': [-0.45440964570700804, 1.1122596706209804], 'sd': 0.8936681350950264, 'rmse': 0.8643528517724728, 'verdict': 'inconclusive'}} |

