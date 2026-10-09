"""Stage-1 tests for discrimination_free: objective and gradient, equivalence with difficulty_free at lambda == 1, nesting, constraint,
estimand bookkeeping, recovery smoke, and the runner."""
import numpy as np
import pytest
import yaml

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import load_yaml
from kt_trial.moments import Theta
from difficulty_free.audit import difficulties
from difficulty_free.freeb import item_ids
from difficulty_free.model import FreeObjective, FreeParamMap
from difficulty_free.simulator import draw_lambda, simulate_lambda
from discrimination_free import twopl
from discrimination_free.fit import fit_2pl
from discrimination_free.model import Objective2PL, Param2PL, contract

NI = 48


@pytest.fixture(scope="module")
def ids(templates):
    return item_ids(templates, 12)


@pytest.fixture(scope="module")
def b_true(templates, ids):
    return difficulties(templates, ids, NI)


@pytest.fixture(scope="module")
def lam_misfit():
    return draw_lambda(11, "t", 300, 0, 0.3, NI)


@pytest.fixture(scope="module")
def data(cfg, templates, theta, ids, lam_misfit):
    ds = simulate_lambda(cfg, 1200, ("f2",), 13, templates, lam=lam_misfit, ids=ids, theta=theta)
    return ds, pair_counts(ds.Y, ds.template_id, len(templates))


def test_objective_equals_difficulty_free_when_lambda_is_one(templates, theta, ids, b_true, data):
    ds, pc = data
    p2, p1 = Param2PL("B2", 4, NI), FreeParamMap("B2", 4, NI)
    o2, o1 = Objective2PL(p2, templates, pc, ids), FreeObjective(p1, templates, pc, ids)
    x2, x1 = p2.pack(theta, b_true), p1.theta_b_to_x(theta, b_true)
    assert abs(o2.loglik(x2) - o1.loglik(x1)) < 1e-9 * abs(o1.loglik(x1))
    f2, g2 = o2(x2); f1, g1 = o1(x1)
    assert abs(f2 - f1) < 1e-12 and np.allclose(g2[:p2.nt + NI], g1, atol=1e-9)


def test_objective_matches_twopl_core(templates, theta, ids, b_true, data, lam_misfit):
    """The hand-rolled moments of the objective agree with the audit's twopl.core (an independent implementation of the same map)."""
    from kt_trial.bvn import weighted_cell_loglik_obs
    from kt_trial.composite_likelihood import P_FLOOR
    from difficulty_free.model import with_difficulties
    ds, pc = data
    th_n, lam_n, g = twopl.normalise(theta, lam_misfit)
    pm = Param2PL("B2", 4, NI)
    ob = Objective2PL(pm, templates, pc, ids)
    c = twopl.core(th_n, with_difficulties(templates, ids, b_true), ids, lam_n, pc.iu, pc.ju, need_jac=False)
    ref, _, _ = weighted_cell_loglik_obs(c["a"], pc.iu, pc.ju, c["rho"], pc.counts, P_FLOOR, grad=False)
    assert abs(ob.loglik(pm.pack(th_n, b_true, lam_n)) - ref) < 1e-9 * abs(ref)


def test_gradient_matches_finite_differences_in_all_blocks(templates, theta, ids, b_true, data, lam_misfit):
    ds, pc = data
    th_n, lam_n, g = twopl.normalise(theta, lam_misfit)
    pm = Param2PL("B2", 4, NI)
    ob = Objective2PL(pm, templates, pc, ids)
    x = pm.pack(th_n, b_true, lam_n) + np.random.default_rng(1).normal(0, 0.02, pm.n)
    x = np.clip(x, pm.lb + 1e-3, pm.ub - 1e-3)
    f0, g0 = ob(x)
    idx = list(range(pm.nt)) + list(range(pm.nt, pm.nt + NI, 6)) + list(range(pm.nt + NI, pm.n, 5))
    for j in idx:
        h = 1e-6 * max(1.0, abs(x[j]))
        xp, xm = x.copy(), x.copy(); xp[j] += h; xm[j] -= h
        fd = (ob(xp)[0] - ob(xm)[0]) / (2 * h)
        assert abs(fd - g0[j]) < 2e-6 * max(1.0, abs(g0[j])) + 1e-9, (pm.names[j], fd, g0[j])


def test_contract_equals_kt_trial_adjoint_when_lambda_is_one(templates, theta, data):
    from kt_trial.composite_likelihood import _adjoint_gradient
    from kt_trial.moments import latent_moments
    ds, pc = data
    tpl = templates[2]
    mu, V = latent_moments(tpl, theta)
    rng = np.random.default_rng(2)
    T = tpl.T
    wa, w_rho = rng.normal(size=T), rng.normal(size=len(pc.iu))
    ref = _adjoint_gradient(theta, tpl, mu, V, wa, w_rho, pc.iu, pc.ju)
    d = np.diag(V); sd = np.sqrt(d); rho = V[pc.iu, pc.ju] / (sd[pc.iu] * sd[pc.ju])
    g_mu = wa / sd
    g_D = -wa * mu / (2 * d * sd) - np.bincount(pc.iu, weights=w_rho * rho, minlength=T) / (2 * d) - np.bincount(pc.ju, weights=w_rho * rho, minlength=T) / (2 * d)
    G = np.zeros((T, T)); G[pc.iu, pc.ju] = 0.5 * w_rho / (sd[pc.iu] * sd[pc.ju]); G = G + G.T; G[np.diag_indices(T)] = g_D
    assert np.allclose(contract(theta, tpl, g_mu, G), ref, rtol=1e-10, atol=1e-10)


def test_b2_with_zero_variance_equals_b1(templates, theta, ids, b_true, data, lam_misfit):
    ds, pc = data
    th_n, lam_n, g = twopl.normalise(theta.copy(sigma2_F=0.0, tau_F=1.0), lam_misfit)
    p1, p2 = Param2PL("B1", 4, NI), Param2PL("B2", 4, NI)
    l1 = Objective2PL(p1, templates, pc, ids).loglik(p1.pack(th_n, b_true, lam_n))
    l2 = Objective2PL(p2, templates, pc, ids).loglik(p2.pack(th_n, b_true, lam_n))
    assert abs(l1 - l2) < 1e-8 * abs(l1)


def test_lambda_parametrisation_has_geometric_mean_one():
    pm = Param2PL("B1", 4, NI)
    x = np.random.default_rng(3).normal(0, 0.4, pm.n)
    lam = pm.lam(x)
    assert abs(np.mean(np.log(lam))) < 1e-12 and (lam > 0).all()
    assert np.allclose(pm.P.T @ np.log(lam), x[pm.nt + NI:], atol=1e-12)


def test_truth_bookkeeping_g_and_sigma2_F_star():
    from discrimination_free.jobs import truth_2pl
    from kt_trial.config import load_scenario
    stage = {"master_seed": 5}
    cfg = load_scenario("S1")
    t0 = truth_2pl(cfg, stage, {"id": "V1"}, 300, 0)
    assert t0["g"] == 1.0 and abs(t0["sigma2_F_star"] - 0.16) < 1e-12
    t1 = truth_2pl(cfg, stage, {"id": "V5", "lambda_cv": 0.3}, 300, 0)
    assert abs(t1["sigma2_F_star"] - t1["g"] ** 2 * 0.16) < 1e-12 and abs(np.mean(np.log(t1["lam_star"]))) < 1e-12
    t2 = truth_2pl(cfg, stage, {"id": "V5", "lambda_cv": 0.3}, 300, 0)
    assert np.array_equal(t1["lam"], t2["lam"])                     # deterministic per (scenario, N, rep)


@pytest.mark.slow
def test_2pl_fit_recovers_difficulties_discriminations_and_constraint(cfg, templates, theta, ids, b_true):
    lam = draw_lambda(21, "smoke", 300, 0, 0.3, NI)
    th_n, lam_n, g = twopl.normalise(theta, lam)
    ds = simulate_lambda(cfg, 3000, ("smoke",), 21, templates, lam=lam, ids=ids, theta=theta)
    pc = pair_counts(ds.Y, ds.template_id, len(templates))
    f = fit_2pl("B1", templates, pc, dict(cfg["fit"], n_starts=2), 4, ids, NI, ("smoke",), 21)
    assert f["status"] == "ok" and f["converged"]
    lh = np.array(f["lam"])
    assert abs(np.mean(np.log(lh))) < 1e-9
    e = (np.log(lh) - np.log(lh).mean()) - (np.log(lam_n) - np.log(lam_n).mean())
    assert np.sqrt((e ** 2).mean()) < 0.25 and np.corrcoef(np.log(lh), np.log(lam_n))[0, 1] > 0.8
    assert np.sqrt(((np.array(f["b"]) - b_true) ** 2).mean()) < 0.2
    assert f["certificate"]["newton_decrement"] <= cfg["fit"]["newton_tol"] or f["certificate"]["hessian_not_pd"]


def test_frozen_gate_and_job_expansion(tmp_path):
    from discrimination_free import runner
    st = load_yaml("configs/experiment_04/stage_pilot.yaml")
    jl = runner.expand_jobs(st)
    assert len(jl) == 24 and sum(j["kind"] == "fit" for j in jl) == 12 and {j["scenario"] for j in jl if j["kind"] == "warp"} == {"V2", "V4"}
    cfg = dict(st, stage="confirmatory"); p = tmp_path / "c.yaml"; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, out=lambda m: None) == 2
    cfg["frozen"] = True; p.write_text(yaml.safe_dump(cfg))
    assert runner.run_stage(p, results_root=str(tmp_path / "r"), dry_run=True, frozen_sha256="bad", out=lambda m: None) == 2


@pytest.mark.slow
def test_runner_end_to_end_resume_refusal_cap_and_summary(tmp_path):
    import json
    from discrimination_free import runner
    from discrimination_free.summarize import summarize
    st = load_yaml("configs/experiment_04/stage_pilot.yaml")
    st.update(n_starts=1, fit={"scenarios": ["V5"], "N_list": [150], "rep_range": [0, 1]},
              warp={"scenarios": ["V4"], "N_list": [150], "rep_range": [0, 1], "estimators": {"V4": ["twopl", "free1"]}},
              cost_model_sec={"fit": 100, "warp_twopl": 100, "warp_free1": 100})
    p = tmp_path / "tiny.yaml"; p.write_text(yaml.safe_dump(st)); root = tmp_path / "res"; msgs = []
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0
    rd = next((root / "pilot").iterdir())
    assert len(list((rd / "jobs").glob("*.json"))) == 2 and not list((rd / "jobs").glob("*.tmp"))
    fr = json.loads((rd / "jobs" / "fit__V5__N150__r0.json").read_text())["result"]
    assert set(fr["arms"]) == {"free1", "twopl"} and abs(np.mean(np.log(fr["arms"]["twopl"]["B2"]["lam"]))) < 1e-9
    assert abs(fr["sigma2_F_star"] - fr["g"] ** 2 * fr["sigma2_F_true"]) < 1e-12
    wr = json.loads((rd / "jobs" / "warp__V4__N150__r0.json").read_text())["result"]
    assert {"twopl", "free1"} <= set(wr) and np.isfinite(wr["twopl"]["T"]) and np.isfinite(wr["free1"]["T_star"])
    msgs.clear()
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 0 and any("0 jobs to run" in m for m in msgs)
    man = json.loads((rd / "manifest.json").read_text()); man["code_hash"] = "0" * 64
    (rd / "manifest.json").write_text(json.dumps(man))
    assert runner.run_stage(p, results_root=str(root), workers=2, out=msgs.append) == 3
    S = summarize(str(rd))
    assert S["accounting"]["errors"] == 0 and "V5|N=150" in S["cells"] and "V4|N=150" in S["warp"] and (rd / "summary.md").exists()
    capped = dict(st, budget={"max_cpu_hours": 1e-9, "enforce_cpu_cap": True, "workers": 1}); p2 = tmp_path / "cap.yaml"; p2.write_text(yaml.safe_dump(capped))
    assert runner.run_stage(p2, results_root=str(tmp_path / "res2"), workers=1, out=msgs.append) in (0, 5)
