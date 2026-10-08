# Experiment 3 summary: recovery of the shared transient latent state F with unknown item difficulties

- stage `calibration`, config hash `01f57a2b7880`, code hash `cbb3ad29b7e8`
- env: {'python': '3.12.10', 'executable': 'C:\\Users\\Dell ProMax Tower T2\\Downloads\\code\\.venv12\\Scripts\\python.exe', 'platform': 'Windows-11-10.0.26200-SP0', 'numpy': '2.5.3', 'scipy': '1.18.1', 'pandas': '3.0.6', 'pyyaml': '6.0.3', 'cpu_count': 20, 'threads': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}}
- job accounting: {'jobs': 400, 'ok': 400, 'errors': 0}

## Calibration of the free-difficulty null test (warp-speed Monte Carlo, X3-D15)

| scenario | cell | datasets (ok) | alpha-hat (5 %) | 95 % CI | verdict | alpha-hat at 10 % / 1 % | T zero share (data / bootstrap) | ridge share (data / bootstrap) | KS p |
|---|---|---|---|---|---|---|---|---|---|
| C2 | pooled | 200 (200) | 0.100 | [0.035, 0.155] | **inconclusive** | 0.14 / 0.04 | 0.12 / 0.15 | 0.16 / 0.14 | 0.328 |
| C2 | N=300 | 100 (100) | 0.070 | [0.020, 0.150] | **inconclusive** | 0.11 / 0.05 | 0.13 / 0.20 | 0.19 / 0.14 | 0.368 |
| C2 | N=1000 | 100 (100) | 0.130 | [0.030, 0.230] | **inconclusive** | 0.19 / 0.04 | 0.11 / 0.10 | 0.13 / 0.15 | 0.368 |
| C4 | pooled | 200 (200) | 0.130 | [0.085, 0.225] | **liberal** | 0.21 / 0.09 | 0.07 / 0.17 | 0.17 / 0.17 | 0.003 |
| C4 | N=300 | 100 (100) | 0.140 | [0.030, 0.250] | **inconclusive** | 0.19 / 0.05 | 0.08 / 0.21 | 0.16 / 0.16 | 0.211 |
| C4 | N=1000 | 100 (100) | 0.170 | [0.100, 0.280] | **liberal** | 0.24 / 0.14 | 0.05 / 0.12 | 0.18 / 0.19 | 0.001 |

