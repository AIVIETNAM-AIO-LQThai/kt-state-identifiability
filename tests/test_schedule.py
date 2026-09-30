import numpy as np

from kt_trial.config import load_scenario, rng_for, seed_sequence
from kt_trial.schedule import audit_design, build_template, build_templates


def test_deterministic(cfg):
    a, b = build_template(cfg, 3), build_template(cfg, 3)
    for f in ("skill", "item", "time", "b"):
        assert np.array_equal(getattr(a, f), getattr(b, f))
    assert not np.array_equal(build_template(cfg, 4).time, a.time)


def test_counts_and_order(cfg, templates):
    for t in templates:
        assert t.T == 3 * 32 + 16 and t.practice.sum() == 96
        assert np.all(np.diff(t.time) >= 0.4 - 1e-12)                 # chronological, min gap
        for s in range(3):
            m = t.practice & (t.session == s)
            assert m.sum() == 32 and np.all(np.bincount(t.skill[m], minlength=4) == 8)
            assert len(set(zip(t.skill[m], t.item[m]))) == 32          # no repeated item in a session
        pr = ~t.practice
        assert pr.sum() == 16 and np.all(np.bincount(t.skill[pr], minlength=4) == 4)
        assert t.session[pr].min() == 3 and t.time[pr].min() >= 10080.0


def test_exposure_strictly_before_and_no_probes(templates):
    for t in templates:
        for i in range(t.T):
            e = np.flatnonzero(t.expo[i])
            assert np.all(t.time[e] < t.time[i]) and np.all(t.practice[e]) and np.all(t.skill[e] == t.skill[i])
        assert t.n_prior[0] == 0
        # first attempt per skill has zero exposures; probes never count as exposures
        for k in range(4):
            first = np.flatnonzero(t.skill == k)[0]
            assert t.n_prior[first] == 0
        assert t.n_prior[t.practice].max() == 24 - 1 + 0 or t.n_prior.max() == 24
        last_probe_of_skill = [np.flatnonzero((t.skill == k) & ~t.practice)[-1] for k in range(4)]
        assert all(t.n_prior[i] == 24 for i in last_probe_of_skill)


def test_blocked_and_seed_isolation(cfg):
    c = load_scenario("S5")
    t = build_template(c, 0)
    for s in range(3):
        sk = t.skill[t.practice & (t.session == s)]
        assert all(len(set(sk[i:i + 8])) == 1 for i in range(0, 32, 8))
    assert seed_sequence(1, "a", 1).generate_state(2).tolist() != seed_sequence(1, "a", 2).generate_state(2).tolist()
    assert rng_for(1, "x").random() == rng_for(1, "x").random()


def test_audit_content(cfg, templates):
    a = audit_design(cfg, templates)
    assert a["pairs_per_template"] == 6216
    assert min(a["pre_exposure_obs_per_template"]) >= 4
    assert a["cross_session_pairs"] > 10000 and a["within_session_pairs"] > 5000
    assert sum(a["within_session_lag_hist"].values()) == a["within_session_pairs"]
    assert a["cross_skill_comparable_history_pairs"]["within_session"] > 0
    assert a["pair_regressor_condition_number"] < 50 and abs(a["obs_corr_Hs_Hf"]) < 0.5
