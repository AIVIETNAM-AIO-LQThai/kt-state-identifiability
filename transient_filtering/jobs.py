"""Job bodies for Experiment 2: `bound` (information bound), `track` (filter arms on held-out learners), `ref` (SMC reference).

Evaluation data are held-out learners (never used for fitting): either the regenerated Experiment-1 held-out set
(data_source = exp1_heldout, needs a fingerprint-verified build) or a fresh namespace under the Experiment-2 master seed
(data_source = fresh). Frozen Experiment-1 fitted parameters (B1, B2) are read from the saved fit envelopes.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import scipy

from kt_trial.config import file_sha256, rng_for
from kt_trial.moments import Theta
from kt_trial.runner import scenario_cfg
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate

from . import metrics as M
from .bound import bcrb_path
from .filters import run_full, run_persistent
from .reference import run_smc
from .regenerate import exp1_stage_cfg, load_fit_result, regenerate, true_theta


def heldout(cfg2: dict, sid: str, N: int, rep: int):
    """Evaluation learners with retained latent truth. Returns (cfg, templates, dataset)."""
    if cfg2["data_source"] == "exp1_heldout":
        return regenerate(exp1_stage_cfg(cfg2["exp1"]["stage_config"]), sid, N, rep, "heldout", True)
    s1 = exp1_stage_cfg(cfg2["exp1"]["stage_config"])
    cfg = scenario_cfg(s1, sid)
    ts = build_templates(cfg)
    ds = simulate(cfg, cfg2["heldout_N"], ("exp2_heldout", sid, N, rep), cfg2["master_seed"], ts, keep_latent=True)
    return cfg, ts, ds


def _assemble(ds, ts, fn):
    """Run fn(template, learner_index_array) -> dict of arrays (n_g, ...) and place them in learner order."""
    out = {}
    for g, tpl in enumerate(ts):
        idx = np.flatnonzero(ds.template_id == g)
        if not len(idx):
            continue
        r = fn(g, tpl, idx)
        for k, v in r.items():
            if k not in out:
                out[k] = np.zeros((ds.Y.shape[0],) + v.shape[1:])
            out[k][idx] = v
    return out


def _prov(cfg2: dict, ds, sid: str, N: int, rep: int) -> dict:
    """Hashes that identify exactly which evaluation data and which frozen Experiment-1 fit a result used."""
    f = Path(cfg2["exp1"]["results"]) / "jobs" / f"fit__{sid}__N{N}__r{rep}.json"
    return {"eval_sha256": hashlib.sha256(ds.Y.tobytes() + ds.template_id.tobytes()).hexdigest(),
            "exp1_fit_sha256": file_sha256(f), "numpy": np.__version__, "scipy": scipy.__version__}


def run_bound(cfg2: dict) -> dict:
    s1 = exp1_stage_cfg(cfg2["exp1"]["stage_config"])
    cfg = scenario_cfg(s1, cfg2["bound"]["scenario"])
    ts = build_templates(cfg)
    th = true_theta(cfg)
    s2F = th.sigma2_F
    masks = M.bin_masks(ts[0])
    res = {"sigma2_F": s2F, "arms": {}}
    arms = {"answers_only": {}}
    for rho in cfg2["track"]["indicator"]["rho"]:
        Rn = s2F * (1 - rho) / rho
        arms[f"indicator_rho{rho}_with_answers"] = dict(Rnu=Rn)
        arms[f"indicator_rho{rho}_only"] = dict(Rnu=Rn, use_answers=False)
    for name, kw in arms.items():
        pre = np.mean([bcrb_path(th, t, **kw)["pre"] for t in ts], 0)
        post = np.mean([bcrb_path(th, t, **kw)["post"] for t in ts], 0)
        res["arms"][name] = {"R2_pre": {b: float(1 - pre[m].mean() / s2F) for b, m in masks.items()},
                             "R2_post": {b: float(1 - post[m].mean() / s2F) for b, m in masks.items()}}
        if name == "answers_only":
            res["pre_var_by_position"] = pre.tolist(); res["post_var_by_position"] = post.tolist()
    return res


def _arm_logloss(arms: dict, Y, masks) -> dict:
    return {k: M.per_bin(M.logloss(a["p"], Y), masks) for k, a in arms.items()}


PAIRS = [  # (X, Y): gain of arm X over arm Y in nats per response
    ("full_fit", "priorF_fit"), ("full_fit", "B1_fit"), ("full_fit", "F0_fit"), ("full_fit", "white_fit"),
    ("oracle_fit", "full_fit"), ("full_known", "priorF_known"), ("full_known", "F0_known"), ("oracle_known", "full_known"),
    ("full_known", "full_fit"), ("priorF_fit", "B1_fit"), ("ind_full_rho0.3", "full_known"), ("ind_full_rho0.6", "full_known"),
    ("ind_full_rho0.3", "ind_only_rho0.3"), ("ind_full_rho0.6", "ind_only_rho0.6"), ("B1_fit", "F0_fit")]


def run_track(cfg2: dict, sid: str, N: int, rep: int) -> dict:
    cfg, ts, ds = heldout(cfg2, sid, N, rep)
    s1 = exp1_stage_cfg(cfg2["exp1"]["stage_config"])
    fit = load_fit_result(cfg2["exp1"]["results"], sid, N, rep)
    th2 = Theta.from_dict(fit["fits"]["B2"]["theta"]); th1 = Theta.from_dict(fit["fits"]["B1"]["theta"])
    thT = true_theta(cfg)
    Y, F = ds.Y.astype(float), ds.latent["F"]
    masks = M.bin_masks(ts[0])
    for t in ts:
        assert all((M.bin_masks(t)[k] == masks[k]).all() for k in masks)
    known = sid in cfg2["track"]["known_scenarios"]
    ind = cfg2["track"]["indicator"]
    do_ind = known and sid in ind["scenarios"]
    s2F = thT.sigma2_F
    O = {}
    if do_ind:
        for rho in ind["rho"]:
            nu = rng_for(cfg2["master_seed"], "indicator", sid, N, rep, rho).standard_normal(F.shape)
            O[rho] = F + np.sqrt(s2F * (1 - rho) / rho) * nu

    def fn(g, tpl, idx):
        y, f = Y[idx], F[idx]
        r = {}
        def put(name, o):
            for k, v in o.items():
                if k in ("p", "mF_pre", "vF_pre", "mF_post", "vF_post", "mp_post", "vp_post"):
                    r[f"{name}|{k}"] = v
        f2 = run_full(th2, tpl, y)
        put("full_fit", f2); r["priorF_fit|p"] = f2["p_priorF"]
        put("B1_fit", run_persistent(th1, tpl, y))
        r["F0_fit|p"] = run_persistent(th2.copy(sigma2_F=0.0), tpl, y)["p"]
        r["white_fit|p"] = run_persistent(th2, tpl, y, extra_var=th2.sigma2_F)["p"]
        r["oracle_fit|p"] = run_persistent(th2, tpl, y, F_known=f)["p"]
        if known:
            fk = run_full(thT, tpl, y)
            put("full_known", fk); r["priorF_known|p"] = fk["p_priorF"]
            r["F0_known|p"] = run_persistent(thT.copy(sigma2_F=0.0), tpl, y)["p"]
            r["oracle_known|p"] = run_persistent(thT, tpl, y, F_known=f)["p"]
        for rho, Oi in O.items():
            Rn = s2F * (1 - rho) / rho
            put(f"ind_full_rho{rho}", run_full(thT, tpl, y, O=Oi[idx], Rnu=Rn))
            put(f"ind_only_rho{rho}", run_full(thT, tpl, y, O=Oi[idx], Rnu=Rn, use_answers=False))
        return r
    flat = _assemble(ds, ts, fn)
    arms = {}
    for k, v in flat.items():
        a, f = k.split("|")
        arms.setdefault(a, {})[f] = v
    t_last = int(np.flatnonzero(ts[0].practice)[-1])
    res = {"scenario": sid, "N": N, "rep": rep, "data_source": cfg2["data_source"], "n_eval": int(Y.shape[0]),
           "provenance": _prov(cfg2, ds, sid, N, rep),
           "sigma2_F_true": s2F, "fitted": {"B2": {k: fit["fits"]["B2"]["theta"][k] for k in ("sigma2_F", "tau_F")},
                                              "flags_B2": fit["fits"]["B2"]["flags"]},
           "logloss": _arm_logloss(arms, Y, masks), "gain": {}, "state": {}, "excursion": {}, "persistent": {}}
    for x, y in PAIRS:
        if x in arms and y in arms:
            res["gain"][f"{x}__over__{y}"] = M.paired(M.logloss(arms[x]["p"], Y), M.logloss(arms[y]["p"], Y), masks)
    for a, d in arms.items():
        if "mF_post" in d:
            res["state"][a] = {"pre": M.state_metrics(d["mF_pre"], d["vF_pre"], F, masks),
                               "post": M.state_metrics(d["mF_post"], d["vF_post"], F, masks)}
            res["excursion"][a] = {"post": M.excursion(d["mF_post"], ts[0])}
            res["excursion"][a]["pre_energy"] = M.per_bin(d["mF_pre"] ** 2, masks)
        if "mp_post" in d:
            res["persistent"][a] = M.persistent_recovery(d["mp_post"], d["vp_post"], ds.latent, t_last)
    return res


def _select(ds, per_template: int):
    sel = []
    for g in range(int(ds.template_id.max()) + 1):
        sel += list(np.flatnonzero(ds.template_id == g)[:per_template])
    return np.array(sel)


def run_ref(cfg2: dict, rep: int) -> dict:
    rc = cfg2["ref"]
    sid, N = rc["scenario"], rc["N"]
    cfg, ts, ds = heldout(cfg2, sid, N, rep)
    fit = load_fit_result(cfg2["exp1"]["results"], sid, N, rep)
    th1 = Theta.from_dict(fit["fits"]["B1"]["theta"])
    thT = true_theta(cfg)
    s2F = thT.sigma2_F
    sel = _select(ds, rc["per_template"])
    sub_tid = ds.template_id[sel]
    Y, F = ds.Y[sel].astype(float), ds.latent["F"][sel]
    masks = M.bin_masks(ts[0])
    n = len(sel)

    def per_template(fn):
        out = {}
        for g, tpl in enumerate(ts):
            idx = np.flatnonzero(sub_tid == g)
            if not len(idx):
                continue
            for k, v in fn(g, tpl, idx).items():
                out.setdefault(k, np.zeros((n,) + v.shape[1:]))[idx] = v
        return out
    adf = per_template(lambda g, t, i: {k: v for k, v in run_full(thT, t, Y[i]).items()
                                        if k in ("p", "mF_pre", "mF_post", "vF_pre", "vF_post")})
    adf1 = per_template(lambda g, t, i: {"p": run_persistent(th1, t, Y[i])["p"]})
    n_seeds, Np = rc["n_seeds"], rc["n_particles"]

    def smc(theta, Np_, seed_key):
        def fn(g, tpl, idx):
            rng = rng_for(cfg2["master_seed"], "smc", sid, N, rep, g, *seed_key)
            r = run_smc(theta, tpl, Y[idx], Np_, rng)
            return {k: r[k] for k in ("p", "mF_pre", "mF_post", "vF_pre", "vF_post", "ess")}
        return per_template(fn)
    runs = [smc(thT, Np, ("B2known", Np, s)) for s in range(n_seeds)]
    big = smc(thT, Np * rc["doubling_factor"], ("B2known", Np * rc["doubling_factor"], 0))
    runs1 = [smc(th1.copy(sigma2_F=0.0), Np, ("B1fit", Np, s)) for s in range(rc.get("n_seeds_b1", 3))]
    P = np.stack([r["p"] for r in runs]); pbar = P.mean(0)
    bnd_pre = np.mean([bcrb_path(thT, ts[g])["pre"] for g in sub_tid], 0)
    bnd_post = np.mean([bcrb_path(thT, ts[g])["post"] for g in sub_tid], 0)
    def mse_bins(mF):
        return {b: float(((mF - F) ** 2)[:, m].mean()) for b, m in masks.items()}
    res = {"scenario": sid, "N": N, "rep": rep, "data_source": cfg2["data_source"], "n_learners": int(n),
           "provenance": _prov(cfg2, ds, sid, N, rep),
           "learner_index": sel.tolist(), "template_of_learner": sub_tid.tolist(), "n_seeds": n_seeds, "n_particles": Np, "doubling_factor": rc["doubling_factor"],
           "sigma2_F": s2F,
           "bound_mse_pre": {b: float(bnd_pre[m].mean()) for b, m in masks.items()},
           "bound_mse_post": {b: float(bnd_post[m].mean()) for b, m in masks.items()},
           "mse_pre_by_seed": [mse_bins(r["mF_pre"]) for r in runs], "mse_post_by_seed": [mse_bins(r["mF_post"]) for r in runs],
           "mse_pre_big": mse_bins(big["mF_pre"]), "mse_post_big": mse_bins(big["mF_post"]),
           "mse_pre_adf": mse_bins(adf["mF_pre"]), "mse_post_adf": mse_bins(adf["mF_post"]),
           "p_seed_sd_rms": float(np.sqrt((P.var(0, ddof=1)).mean())),
           "p_big_minus_mean_rms": float(np.sqrt(((big["p"] - pbar) ** 2).mean())),
           "p_adf_minus_ref": {b: {"mean_abs": float(np.abs(adf["p"] - pbar)[:, m].mean()),
                                   "mean": float((adf["p"] - pbar)[:, m].mean())} for b, m in masks.items()},
           "logloss_ref": M.per_bin(M.logloss(pbar, Y), masks), "logloss_adf": M.per_bin(M.logloss(adf["p"], Y), masks),
           "gain_ref_over_adf": M.per_bin(M.logloss(adf["p"], Y) - M.logloss(pbar, Y), masks),
           "learner_mse_practice": {
               k: {src: (((np.mean([r[f"mF_{k}"] for r in runs], 0) if src == "ref" else adf[f"mF_{k}"]) - F) ** 2)[:, masks["practice"]].mean(1).tolist()
                   for src in ("ref", "adf")} for k in ("pre", "post")},
           "ess_min": float(min(r["ess"].min() for r in runs)), "ess_mean": float(np.mean([r["ess"].mean() for r in runs])),
           "B1fit": {"p_adf_minus_ref_mean_abs": {b: float(np.abs(adf1["p"] - np.stack([r['p'] for r in runs1]).mean(0))[:, m].mean())
                                                  for b, m in masks.items()},
                     "p_seed_sd_rms": float(np.sqrt(np.stack([r["p"] for r in runs1]).var(0, ddof=1).mean())),
                     "gain_ref_over_adf": M.per_bin(M.logloss(adf1["p"], Y) - M.logloss(np.stack([r['p'] for r in runs1]).mean(0), Y), masks)}}
    return res


def run_ref_prod(cfg2: dict, rep: int) -> dict:
    """Production reference: ALL held-out learners of S1 N=1000 replication `rep`, one SMC pass at the validated particle
    count, with the ADF arms (known and fitted parameters) and the B1 filter on the very same learners and prefixes."""
    rc = cfg2["ref_prod"]
    sid, N = rc["scenario"], rc["N"]
    cfg, ts, ds = heldout(cfg2, sid, N, rep)
    fit = load_fit_result(cfg2["exp1"]["results"], sid, N, rep)
    th1, th2 = Theta.from_dict(fit["fits"]["B1"]["theta"]), Theta.from_dict(fit["fits"]["B2"]["theta"])
    thT = true_theta(cfg)
    Y, F = ds.Y.astype(float), ds.latent["F"]
    masks = M.bin_masks(ts[0])
    keys = ("p", "mF_pre", "mF_post")
    adfK = _assemble(ds, ts, lambda g, t, i: {k: v for k, v in run_full(thT, t, Y[i]).items() if k in keys})
    adfF = _assemble(ds, ts, lambda g, t, i: {k: v for k, v in run_full(th2, t, Y[i]).items() if k in keys})
    b1 = _assemble(ds, ts, lambda g, t, i: {"p": run_persistent(th1, t, Y[i])["p"]})
    Np = rc["n_particles"]

    def smc_fn(g, tpl, idx):
        r = run_smc(thT, tpl, Y[idx], Np, rng_for(cfg2["master_seed"], "smcprod", sid, N, rep, g))
        return {k: r[k] for k in ("p", "mF_pre", "mF_post", "ess")}
    ref = _assemble(ds, ts, smc_fn)
    cnt = np.bincount(ds.template_id, minlength=len(ts)).astype(float)
    bnd = {ph: sum(c * bcrb_path(thT, ts[g])[ph] for g, c in enumerate(cnt)) / cnt.sum() for ph in ("pre", "post")}
    e2 = lambda mF: (mF - F) ** 2
    ll = lambda p: M.logloss(p, Y)
    res = {"scenario": sid, "N": N, "rep": rep, "data_source": cfg2["data_source"], "n_learners": int(Y.shape[0]),
           "provenance": _prov(cfg2, ds, sid, N, rep), "n_particles": Np, "sigma2_F": thT.sigma2_F,
           "bound_mse": {ph: {b: float(bnd[ph][m].mean()) for b, m in masks.items()} for ph in ("pre", "post")},
           "mse": {a: {ph: M.per_bin(e2(d[f"mF_{ph}"]), masks) for ph in ("pre", "post")}
                   for a, d in (("ref", ref), ("adf_known", adfK), ("adf_fit", adfF))},
           "mse_diff": {"adf_known_minus_ref": {ph: M.per_bin(e2(adfK[f"mF_{ph}"]) - e2(ref[f"mF_{ph}"]), masks) for ph in ("pre", "post")},
                        "adf_fit_minus_adf_known": {ph: M.per_bin(e2(adfF[f"mF_{ph}"]) - e2(adfK[f"mF_{ph}"]), masks) for ph in ("pre", "post")}},
           "logloss": {a: M.per_bin(ll(d["p"]), masks) for a, d in (("ref", ref), ("adf_known", adfK), ("adf_fit", adfF), ("B1_fit", b1))},
           "gain": {"ref__over__adf_known": M.per_bin(ll(adfK["p"]) - ll(ref["p"]), masks),
                    "adf_known__over__adf_fit": M.per_bin(ll(adfF["p"]) - ll(adfK["p"]), masks),
                    "adf_fit__over__B1_fit": M.per_bin(ll(b1["p"]) - ll(adfF["p"]), masks)},
           "dp_abs": {a: {b: float(np.abs(d["p"] - ref["p"])[:, m].mean()) for b, m in masks.items()} for a, d in (("adf_known", adfK), ("adf_fit", adfF))},
           "ess_min": float(ref["ess"].min()), "ess_mean": float(ref["ess"].mean())}
    return res
