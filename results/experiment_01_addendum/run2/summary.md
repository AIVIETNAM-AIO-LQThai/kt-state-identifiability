# Experiment 1 numerical addendum: summary

- environments recorded in the per-dataset results: ['{"executable": "C:\\\\Users\\\\Dell ProMax Tower T2\\\\Downloads\\\\code\\\\.venv12\\\\Scripts\\\\python.exe", "numpy": "2.5.3", "python": "3.12.10", "scipy": "1.18.1"}']
- datasets 53; reproduced the registered result 2; NOT reproduced 51 (provenance failures, not interpreted); errors 0

**Provenance failure**: the regenerated dataset does not reproduce the registered CLR for 51 dataset(s); these are not evidence about the registered fits. First: {'job_id': 'null_rep__S1__N1000__r1__b4', 'clr_recomputed': 0.012226667255163193, 'registered_clr': 0.012226399034261703}

- by tier (reproduced datasets only): {'C': {'n': 1, 'max_attained_B2': 0.03034166619181633, 'p_changed': 0}, 'B': {'n': 1, 'max_attained_B2': 0.0, 'p_changed': 0}}

| tier | dataset | registered CLR | B2 flags | KKT inf-norm | min Hessian eig (steps) | attained B2 gain | attained B1 gain | p registered -> with improved fits |
|---|---|---|---|---|---|---|---|---|
| C | main__S8n__N1000__r13 | NA | ['newton_decrement_large', 'single_start_at_best'] | 0.8992 | {'0.0001': 0.02020389375780896, '1e-05': 0.020203901891303774, '1e-06': 0.020203902043299266} | 0.03034 | 2.794e-09 | NA -> NA |
| B | null_rep__S8n__N300__r6__b40 | 295.4 | [] | 0.02621 | {'0.0001': 2.1102707622719783, '1e-05': 2.110270759956641, '1e-06': 2.1102707601169395} | 0 | 0 | 0.44 -> 0.44 |
