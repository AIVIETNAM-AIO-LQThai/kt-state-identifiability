"""Stage-0 population audit (X5-D04): for every point of the (F, kappa, tau_D) grid, fit the 2PL pairwise model (B1 and B2) to N_big simulated
learners, then report

  * pseudo-true sigma2_F*, tau_F and the expected CLR statistic T = N * Tpl  (Tpl = 2 (ll_B2 - ll_B1) / N_big, a per-learner quantity), and
  * for every tau_x, the carry-over diagnostic's per-learner standardised signal delta = mean(u~)/sd(u~) at the fitted model, which gives the
    asymptotic non-centrality N delta^2 and the predicted power at N = 300 and 1000.

Composite-likelihood fits depend on the data only through pair counts, so the cost of the fit does not depend on N_big. Convergence tolerances
(gtol_abs, newton_tol) are scaled by TOL_SCALE = 100: the Newton decrement of a parameter error u (in sampling SEs of an N = 1000 fit) is
(N_big / 1000) u^2 / 2, so the scaled tolerance 0.1 means u of about 0.03 SE. No confirmatory data are involved.
"""
from __future__ import annotations

import copy
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from scipy import stats

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import generating_theta_dict, load_scenario
from kt_trial.moments import Theta
from kt_trial.runner import read_json, write_json_atomic
from kt_trial.schedule import build_templates
from difficulty_free.freeb import item_ids
from discrimination_free.fit import fit_2pl

from . import diagnostic as DG
from .simulator import simulate_feedback

N_ITEMS = 48
TOL_SCALE = 100.0


def point_list(ac: dict) -> list[dict]:
    """Grid: F in {absent, present} x (no feedback | kappa x tau_D), plus S8n."""
    pts = []
    for fname, base in (("Fabs", "S2"), ("Fpres", "S1")):
        pts.append(dict(name=f"{fname}_k0", base=base, feedback=None))
        for kappa in ac["kappas"]:
            for tau_D in ac["tau_Ds"]:
                pts.append(dict(name=f"{fname}_k{abs(kappa):g}_tD{tau_D:g}", base=base, feedback={"kappa": float(kappa), "tau_D": float(tau_D)}))
    pts.append(dict(name="S8n_k0", base="S8n", feedback=None))
    return pts


def _slim(f: dict) -> dict:
    keep = ("model", "status", "ll", "runtime", "flags", "converged", "n_params", "n_polished", "polish_line_search_failures", "certificate",
            "start_agreement", "boundary_hits")
    out = {k: f[k] for k in keep if k in f}
    if f.get("status") != "failed":
        out["theta"] = f["theta"]
        out["lam_sd_log"] = float(np.std(np.log(f["lam"]))); out["n_extreme_lambda"] = f.get("n_extreme_lambda")
    return out


def run_point(pt: dict, ac: dict) -> dict:
    t0 = time.time()
    cfg = copy.deepcopy(load_scenario(pt["base"]))
    cfg_fit = dict(cfg["fit"], n_starts=ac.get("n_starts", 5))
    cfg_fit["gtol_abs"] = cfg_fit["gtol_abs"] * TOL_SCALE
    cfg_fit["newton_tol"] = cfg_fit["newton_tol"] * TOL_SCALE
    ts = build_templates(cfg)
    K, G = cfg["design"]["n_skills"], len(ts)
    ids = item_ids(ts, cfg["design"]["items_per_skill"])
    ms, Nb = ac["master_seed"], int(ac["N_big"])
    ds = simulate_feedback(cfg, Nb, ("pop", pt["name"]), ms, ts, lam=np.ones(N_ITEMS), ids=ids, feedback=pt["feedback"])
    pc = pair_counts(ds.Y, ds.template_id, G)
    skey = ("pop", pt["name"])
    f1 = fit_2pl("B1", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms)
    f2 = fit_2pl("B2", ts, pc, cfg_fit, K, ids, N_ITEMS, skey, ms,
                 warm=(Theta.from_dict(f1["theta"]), f1["b"], f1["lam"]) if f1["status"] != "failed" else None, null_fit=f1)
    res = {"point": pt["name"], "base": pt["base"], "feedback": pt["feedback"], "N_big": Nb, "mean_success": float(ds.Y.mean()),
           "fits": {"B1": _slim(f1), "B2": _slim(f2)}}
    if f1["status"] != "failed" and f2["status"] != "failed":
        res["T_per_learner"] = float(2.0 * (f2["ll"] - f1["ll"]) / Nb)
        res["sigma2_F_star"], res["tau_F"] = f2["theta"]["sigma2_F"], f2["theta"]["tau_F"]
    taus = list(ac["taus_x"])
    res["diagnostic"] = {}
    for label, f in (("B2", f2), ("B1", f1)):
        if f["status"] == "failed":
            continue
        out = DG.eta_test(f, ts, ids, ds.Y, ds.template_id, cfg_fit, taus, N_ITEMS, K)
        d = {}
        for tau in taus:
            r = out[tau]
            d[f"{tau:g}"] = {**r, "z_at_Nbig": r["delta"] * np.sqrt(Nb), "power": {str(N): power(r["delta"], N) for N in ac["N_list"]}}
        res["diagnostic"][label] = {"n_active": out["n_active"], "by_tau_x": d}
    res["runtime"] = time.time() - t0
    return res


def power(delta: float, N: int, alpha: float = 0.05) -> float:
    """Asymptotic power of the chi2_1 score test with non-centrality N delta^2."""
    c = stats.norm.isf(alpha / 2.0)
    s = abs(delta) * np.sqrt(N)
    return float(stats.norm.sf(c - s) + stats.norm.cdf(-c - s))


def run_audit(ac: dict, out_dir, workers: int = 4, log=print) -> int:
    out = Path(out_dir); (out / "points").mkdir(parents=True, exist_ok=True)
    todo = [p for p in point_list(ac) if not (out / "points" / f"{p['name']}.json").exists()]
    log(f"{len(todo)} points to run")
    if not todo:
        return 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_point, p, ac): p for p in todo}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                r = fut.result()
                write_json_atomic(out / "points" / f"{p['name']}.json", r)
                log(f"  {p['name']} done in {r['runtime']:.0f}s")
            except Exception as e:                                    # recorded, not silent
                log(f"  {p['name']} FAILED: {e!r}")
    return 0


def null_reference(path, N_list) -> dict:
    """q95 of Experiment 4's registered V2 2PL bootstrap statistics T* per N (X5-D03)."""
    out = {}
    for N in N_list:
        ts = []
        for f in sorted(Path(path, "jobs").glob(f"warp__V2__N{N}__r*.json")):
            e = read_json(f)
            r = e["result"].get("twopl", {}) if e["status"] == "ok" else {}
            if r.get("T_star") is not None and not r.get("star_failed") and r.get("star_converged", False):
                ts.append(r["T_star"])
        out[str(N)] = {"n": len(ts), "q95": float(np.quantile(ts, 0.95)) if ts else None}
    return out


def summarize(ac: dict, out_dir) -> dict:
    out = Path(out_dir)
    pts = {f.stem: read_json(f) for f in sorted((out / "points").glob("*.json"))}
    ref = null_reference(ac["null_reference"], ac["N_list"])
    taus = [f"{t:g}" for t in ac["taus_x"]]
    rows = {}
    for name, r in pts.items():
        row = {"feedback": r["feedback"], "base": r["base"], "sigma2_F_star": r.get("sigma2_F_star"), "tau_F": r.get("tau_F"),
               "T_per_learner": r.get("T_per_learner"),
               "E_T": {str(N): (None if r.get("T_per_learner") is None else r["T_per_learner"] * N) for N in ac["N_list"]}}
        row["E_T_over_q95"] = {str(N): (None if row["E_T"][str(N)] is None or not ref[str(N)]["q95"] else row["E_T"][str(N)] / ref[str(N)]["q95"])
                               for N in ac["N_list"]}
        for lab in ("B2", "B1"):
            d = r["diagnostic"].get(lab)
            if d:
                row[f"diag_{lab}"] = {t: {"delta": d["by_tau_x"][t]["delta"], "z_at_Nbig": d["by_tau_x"][t]["z_at_Nbig"],
                                          "eta_hat": d["by_tau_x"][t]["eta_hat"], "power": d["by_tau_x"][t]["power"]} for t in taus}
        row["fit_flags"] = {m: r["fits"][m].get("flags") for m in ("B1", "B2")}
        row["fit_converged"] = {m: r["fits"][m].get("converged") for m in ("B1", "B2")}
        rows[name] = row
    # G0-2: tau_x maximising the minimum |delta| (B2) over the kappa = -0.25 points
    strong = [n for n, r in rows.items() if r["feedback"] and abs(r["feedback"]["kappa"]) == 0.25]
    sel = None
    if strong and all("diag_B2" in rows[n] for n in strong):
        score = {t: min(abs(rows[n]["diag_B2"][t]["delta"]) for n in strong) for t in taus}
        sel = max(score, key=score.get)
        g02 = {"min_abs_delta_by_tau_x": score, "selected_tau_x": float(sel)}
    else:
        g02 = {"selected_tau_x": None}
    gate = {}
    if sel is not None:
        pw = {n: rows[n]["diag_B2"][sel]["power"]["1000"] for n in strong if rows[n]["feedback"]["tau_D"] == 10.0}
        zs = {n: rows[n]["diag_B2"][sel]["z_at_Nbig"] for n in rows if rows[n]["feedback"] is None}
        gate = {"power_N1000_kappa0.25_tauD10": pw, "G0-3_power_ok": bool(pw and all(v >= 0.8 for v in pw.values())),
                "z_at_Nbig_no_feedback_points": zs, "S8n_predicted_rejection_N1000": rows.get("S8n_k0", {}).get("diag_B2", {}).get(sel, {}).get("power", {}).get("1000")}
    summary = {"null_reference_q95": ref, "G0-2": g02, "G0-3": gate, "points": rows, "N_big": ac["N_big"], "taus_x": ac["taus_x"]}
    write_json_atomic(out / "summary.json", summary)
    return summary


def markdown(S: dict) -> str:
    f = lambda x, d=3: "NA" if x is None else f"{x:.{d}f}"
    L = ["# Experiment 5 Stage 0: population audit (numbers only)", "",
         f"N_big = {S['N_big']}; fits B1/B2 (2PL), tolerances scaled x{TOL_SCALE:g}; tau_x grid {S['taus_x']}.", "",
         f"Null reference (Experiment 4 V2 2PL T*, X5-D03): {S['null_reference_q95']}", "",
         "## Pseudo-true values and expected T", "",
         "| point | sigma2_F* | tau_F | T/N x 1000 | E[T] N=300 (x q95) | E[T] N=1000 (x q95) | B2 converged | B2 flags |", "|---|---|---|---|---|---|---|---|"]
    for n, r in S["points"].items():
        L.append(f"| {n} | {f(r['sigma2_F_star'])} | {f(r['tau_F'], 2)} | {f(None if r['T_per_learner'] is None else 1000 * r['T_per_learner'], 3)} | "
                 f"{f(r['E_T']['300'], 2)} ({f(r['E_T_over_q95']['300'], 2)}) | {f(r['E_T']['1000'], 2)} ({f(r['E_T_over_q95']['1000'], 2)}) | "
                 f"{r['fit_converged']['B2']} | {', '.join(r['fit_flags']['B2'] or [])} |")
    for lab in ("B2", "B1"):
        L += ["", f"## Diagnostic signal at the {lab} fit: delta (per-learner standardised mean), z = delta sqrt(N_big), eta-hat, predicted power at N = 300 / 1000", "",
              "| point | " + " | ".join(f"tau_x {t}" for t in map(lambda t: f"{t:g}", S["taus_x"])) + " |", "|---|" + "---|" * len(S["taus_x"])]
        for n, r in S["points"].items():
            d = r.get(f"diag_{lab}")
            if not d:
                continue
            L.append(f"| {n} | " + " | ".join(f"d {f(d[t]['delta'], 4)}, z {f(d[t]['z_at_Nbig'], 1)}, eta {f(d[t]['eta_hat'], 3)}, P {f(d[t]['power']['300'], 2)} / {f(d[t]['power']['1000'], 2)}"
                                              for t in map(lambda t: f"{t:g}", S["taus_x"])) + " |")
    L += ["", f"## G0-2: {S['G0-2']}", "", f"## G0-3: {S['G0-3']}", ""]
    return "\n".join(L)
