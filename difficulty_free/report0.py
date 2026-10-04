"""Write docs/experiment_03_stage0_report.md (numbers only, no interpretation) from results/experiment_03/stage0/audit.json."""
import json
import sys
from pathlib import Path


def main(audit="results/experiment_03/stage0/audit.json", rob="results/experiment_03/stage0/robustness_seed777_n40000.json",
         out="docs/experiment_03_stage0_report.md"):
    A = json.load(open(audit))
    E = json.load(open("results/experiment_01/audit/design_audit.json"))["identifiability"]["points"]["generating"]["predicted_godambe_se"]
    f = lambda x: "NA (singular)" if x is None else f"{x:.4f}"
    L = ["# Experiment 3, Stage 0: identifiability audit with item difficulties known vs free (numbers only)", "",
         "Analytic Jacobian/SVD of the observable map and design-based Godambe SEs of sigma2_F (pairwise composite likelihood), at the "
         "Experiment-1 generating values except tau_F. 48 item difficulties are the extra coordinates (66 free parameters instead of 18). "
         "Local identification at the tested points only. **No interpretation here: the gate review is Opus's (X3-D03).**", "",
         f"Provenance: {A['provenance']['env']}; threads {A['provenance']['threads']}; score learners {A['provenance']['config']['score_learners']}; "
         f"seed {A['provenance']['config']['master_seed']}.", "",
         f"Consistency with the Experiment-1 audit (b known, tau_F = 10): SE(sigma2_F) here {f(A['points']['generating']['godambe_b_known']['se']['300'])} / "
         f"{f(A['points']['generating']['godambe_b_known']['se']['1000'])} (N = 300 / 1000) against {f(E['300']['sigma2_F'])} / {f(E['1000']['sigma2_F'])} in Experiment 1.", "",
         "## Design SE of sigma2_F", "", "| tau_F (min) | b known N=300 | N=1000 | N=3000 | b free N=300 | N=1000 | N=3000 | free/known (N=1000) |", "|---|---|---|---|---|---|---|---|"]
    for name, p in A["points"].items():
        k, fr = p["godambe_b_known"]["se"], p["godambe_b_free"]["se"]
        ratio = "NA" if fr["1000"] is None else f"{fr['1000'] / k['1000']:.2f}"
        L.append(f"| {p['tau_F']:g} | {f(k['300'])} | {f(k['1000'])} | {f(k['3000'])} | {f(fr['300'])} | {f(fr['1000'])} | {f(fr['3000'])} | {ratio} |")
    L += ["", "## Rank, conditioning and the white-noise scale ridge (b free, 66 parameters)", "",
          "| tau_F | numerical rank | cond. of weighted Jacobian | weakest rel. singular value | ridge response (rel.) | cos(ridge, weakest 1/2/3) | top loadings of weakest direction |", "|---|---|---|---|---|---|---|"]
    for name, p in A["points"].items():
        b = p["b_free"]; w = b["weak_directions"][0]
        L.append(f"| {p['tau_F']:g} | {b['numerical_rank']}/66 | {b['condition_number']:.3g} | {w['rel']:.2e} | {b['ridge_response_rel']:.2e} | "
                 f"{', '.join(f'{c:.2f}' for c in b['ridge_cosine_with_weakest'])} | {', '.join(f'{k} {v:.2f}' for k, v in list(w['top_loadings'].items())[:3])} |")
    L += ["", "The ridge is exact only for white-noise F (tau_F -> 0); at larger tau_F the OU covariance breaks it (tested). b known: full rank 18/18 at all points; "
          "condition numbers " + ", ".join(f"{p['b_known']['condition_number']:.3g}" for p in A["points"].values()) + " (same order as tau_F listed above).", ""]
    L += ["## Estimator correlation of sigma2_F (b free)", ""]
    for name, p in A["points"].items():
        ct = p["godambe_b_free"].get("correlation_top")
        L.append(f"- tau_F {p['tau_F']:g}: top correlated coordinates (index: correlation) {ct}; H condition {p['godambe_b_free']['H_condition_number']:.3g}")
    if Path(rob).exists():
        R = json.load(open(rob))
        L += ["", "## Robustness (different seed 777, 40,000 score learners)", ""]
        for tau, r in R.items():
            L.append(f"- tau_F {tau}: b known {r['known']}; b free {r['free']}")
    g = A["gate_numbers"]
    L += ["", "## Gate numbers (X3-D03)", "", f"- design SE of sigma2_F, b free, tau_F = 10, N = 1000: {g['design_se_sigma2_F_b_free_N1000_tauF10']:.4f} (threshold {g['threshold']})",
          f"- rank-deficient at tau_F = 10 with b free: {g['rank_deficient_b_free_tauF10']}", "",
          "Index map for coordinate indices above: 0-7 the eight scalar parameters (alpha_bar, phi, sigma2_alpha, r_bar, tau_R, sigma2_r, sigma2_F, tau_F), "
          "8-17 log-Cholesky of Sigma_M, 18-65 the 48 difficulties b[skill,item]."]
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
