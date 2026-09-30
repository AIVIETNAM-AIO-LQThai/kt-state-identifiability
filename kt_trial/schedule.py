"""Schedule generation (templates) and numerical design audit."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import rng_for
from .kernels import fast_kernel, slow_kernel

T_TOL = 1e-9


@dataclass
class Template:
    """One fixed chronological schedule shared by the learners assigned to it (arrays length T)."""
    index: int
    skill: np.ndarray       # int (T,)
    item: np.ndarray        # int (T,) item index within skill
    b: np.ndarray           # known item difficulty (T,)
    session: np.ndarray     # int (T,); practice sessions 0..S-1, probe session S
    time: np.ndarray        # absolute minutes (T,)
    practice: np.ndarray    # bool (T,)  (False = delayed probe)
    n_prior: np.ndarray     # prior same-skill practice exposures (T,)
    expo: np.ndarray        # bool (T,T): expo[t,e] = e is an exposure for t
    lag: np.ndarray         # (T,T) T_t - T_e where expo, else 0
    same_session: np.ndarray  # bool (T,T)
    absdt: np.ndarray       # |T_t - T_t'| (T,T)

    @property
    def T(self) -> int:
        return len(self.skill)


def _interleaved_skills(rng, K, per_skill, max_run, tries=100000):
    base = np.repeat(np.arange(K), per_skill)
    for _ in range(tries):
        s = rng.permutation(base)
        run, ok = 1, True
        for i in range(1, len(s)):
            run = run + 1 if s[i] == s[i - 1] else 1
            if run > max_run:
                ok = False
                break
        if ok:
            return s
    raise RuntimeError("could not draw interleaved order within max_run")


def _blocked_skills(rng, K, per_skill):
    return np.repeat(rng.permutation(K), per_skill)


def _times(rng, start, n, itv):
    gaps = itv["min"] + rng.gamma(itv["gamma_shape"], itv["gamma_scale"], size=n - 1)
    return start + np.concatenate([[0.0], np.cumsum(gaps)])


def build_template(design: dict, index: int, master_seed: int | None = None) -> Template:
    d = design["design"]
    K, I = d["n_skills"], d["items_per_skill"]
    rng = rng_for(d["template_seed"] if master_seed is None else master_seed, "template", index)
    per_skill = d["attempts_per_session"] // K
    b_base = np.linspace(d["difficulty"]["lo"], d["difficulty"]["hi"], I)
    offs = np.asarray(d["difficulty"]["skill_offsets"], float)
    skill, item, sess, time, prac = [], [], [], [], []
    for s, start in enumerate(d["session_start_min"]):
        order = (_interleaved_skills(rng, K, per_skill, d["max_run"]) if d["practice_order"] == "interleaved"
                 else _blocked_skills(rng, K, per_skill))
        its = np.empty(len(order), int)
        for k in range(K):
            slots = np.flatnonzero(order == k)
            its[slots] = rng.permutation(I)[:per_skill]
        skill.append(order); item.append(its)
        sess.append(np.full(len(order), s)); prac.append(np.ones(len(order), bool))
        time.append(_times(rng, start, len(order), d["interval"]))
    # delayed probe session: one item drawn from each quartile of the difficulty range, per skill
    n_pr = d["n_probes"] // K
    order = _interleaved_skills(rng, K, n_pr, d["max_run"])
    groups = np.array_split(np.arange(I), n_pr)
    its = np.empty(len(order), int)
    for k in range(K):
        slots = np.flatnonzero(order == k)
        its[slots] = rng.permutation([rng.choice(g) for g in groups])
    skill.append(order); item.append(its)
    sess.append(np.full(len(order), len(d["session_start_min"])))
    prac.append(np.zeros(len(order), bool))
    time.append(_times(rng, d["probe_start_min"], len(order), d["interval"]))
    skill, item, sess = np.concatenate(skill), np.concatenate(item), np.concatenate(sess)
    time, prac = np.concatenate(time), np.concatenate(prac)
    b = b_base[item] + offs[skill]
    tt = time[:, None] - time[None, :]
    expo = (tt > T_TOL) & prac[None, :] & (skill[:, None] == skill[None, :])
    return Template(index, skill, item, b, sess, time, prac, expo.sum(1), expo,
                    np.where(expo, tt, 0.0), sess[:, None] == sess[None, :], np.abs(tt))


def build_templates(design: dict) -> list[Template]:
    return [build_template(design, g) for g in range(design["design"]["n_templates"])]


def assign_templates(rng, N: int, G: int) -> np.ndarray:
    """Balanced random assignment of learners to templates (independent of latent states)."""
    return rng.permutation(np.arange(N) % G)


# --------------------------------------------------------------------------- audit
def audit_design(design: dict, templates: list[Template], gen: dict | None = None) -> dict:
    """Numerical audit of the realised schedules (see plan: anchors, pairs, lags, cross-skill, collinearity)."""
    from .config import generating_theta_dict
    gen = gen or generating_theta_dict(design)
    G = len(templates)
    T = templates[0].T
    iu, ju = np.triu_indices(T, 1)
    out: dict = {"n_templates": G, "T": int(T), "pairs_per_template": int(len(iu))}
    Hs = [slow_kernel(t.n_prior, gen["phi"]) for t in templates]
    Hf = [fast_kernel(t.lag, t.expo, gen["tau_R"]) for t in templates]
    # 1. anchors
    out["pre_exposure_obs_per_template"] = [int((t.n_prior == 0).sum()) for t in templates]
    out["low_exposure_obs_per_template(Hs<=1)"] = [int((h <= 1.0 + 1e-12).sum()) for h in Hs]
    # 2. cross-session pairs by exposure profile
    prof = {}
    for t, hs, hf in zip(templates, Hs, Hf):
        cs = ~t.same_session[iu, ju]
        for a, b_ in zip(t.n_prior[iu][cs], t.n_prior[ju][cs]):
            prof[(int(a), int(b_))] = prof.get((int(a), int(b_)), 0) + 1
    out["cross_session_pairs"] = int(sum(prof.values()))
    out["cross_session_distinct_exposure_count_profiles"] = len(prof)
    hsv = np.concatenate([h[iu][~t.same_session[iu, ju]] for t, h in zip(templates, Hs)])
    hfv = np.concatenate([h[iu][~t.same_session[iu, ju]] for t, h in zip(templates, Hf)])
    out["cross_session_Hs_first_range"] = [float(hsv.min()), float(hsv.max())]
    out["cross_session_Hf_first_range"] = [float(hfv.min()), float(hfv.max())]
    # 3. within-session lag histogram
    edges = [0.0, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 1e9]
    lags = np.concatenate([t.absdt[iu, ju][t.same_session[iu, ju]] for t in templates])
    hist, _ = np.histogram(lags, bins=edges)
    out["within_session_pairs"] = int(len(lags))
    out["within_session_lag_hist"] = {f"[{edges[i]},{edges[i+1]})": int(h) for i, h in enumerate(hist)}
    # probe-session within-session pairs (Hf ~ 0 anchor for the F covariance)
    pr = np.concatenate([(~t.practice[iu] & ~t.practice[ju] & t.same_session[iu, ju]) for t in templates])
    out["probe_within_session_pairs"] = int(pr.sum())
    # 4. cross-skill pairs at comparable exposure histories (|n - n'| <= 1)
    cross, cross_ws, cross_cs = 0, 0, 0
    for t in templates:
        cs_ = (t.skill[iu] != t.skill[ju]) & (np.abs(t.n_prior[iu] - t.n_prior[ju]) <= 1)
        cross += int(cs_.sum()); sw = t.same_session[iu, ju]
        cross_ws += int((cs_ & sw).sum()); cross_cs += int((cs_ & ~sw).sum())
    out["cross_skill_comparable_history_pairs"] = {"total": cross, "within_session": cross_ws,
                                                  "cross_session": cross_cs}
    # 5. collinearity of the pair-level covariance regressors [Sigma_M same-skill, HsHs', HfHf', OU(tau)]
    rows = []
    for t, hs, hf in zip(templates, Hs, Hf):
        same = (t.skill[iu] == t.skill[ju]).astype(float)
        ou = lambda tau: np.where(t.same_session[iu, ju], np.exp(-t.absdt[iu, ju] / tau), 0.0)
        rows.append(np.column_stack([np.ones(len(iu)), same, hs[iu] * hs[ju], hf[iu] * hf[ju], ou(gen["tau_F"])]))
    X = np.vstack(rows)
    names = ["intercept(common M0)", "same_skill(M0 diag)", "HsHs'", "HfHf'", "OU(tau_F)"]
    Xs = X / np.linalg.norm(X, axis=0)
    sv = np.linalg.svd(Xs, compute_uv=False)
    out["pair_regressors"] = names
    out["pair_regressor_corr"] = np.corrcoef(X[:, 1:].T).round(3).tolist()
    out["pair_regressor_condition_number"] = float(sv[0] / sv[-1])
    # observation-level slow/fast collinearity
    hs_all, hf_all = np.concatenate(Hs), np.concatenate(Hf)
    out["obs_corr_Hs_Hf"] = float(np.corrcoef(hs_all, hf_all)[0, 1])
    out["obs_Hf_summary"] = {"min": float(hf_all.min()), "median": float(np.median(hf_all)),
                             "max": float(hf_all.max()), "share_gt_0.1": float((hf_all > 0.1).mean())}
    out["max_same_skill_run_in_practice_session"] = [max(_max_run(t.skill[t.practice & (t.session == s_)])
                                                         for s_ in range(3)) for t in templates]
    return out


def _max_run(x) -> int:
    best, run = 1, 1
    for i in range(1, len(x)):
        run = run + 1 if x[i] == x[i - 1] else 1
        best = max(best, run)
    return best
