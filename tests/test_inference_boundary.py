import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import load_scenario
from kt_trial.fit import fit_model
from kt_trial.inference import learner_bootstrap, null_test, sandwich
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


@pytest.fixture(scope="module")
def setup():
    cfg = load_scenario("S2")
    cfg["design"]["n_templates"] = 2
    ts = build_templates(cfg)
    cfg["fit"] = dict(cfg["fit"], n_starts=2)
    ds = simulate(cfg, 400, ("inf",), 31, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    f = {}
    f["B0"] = fit_model("B0", ts, pc, cfg["fit"], 4, ("inf",), 31)
    f["B1"] = fit_model("B1", ts, pc, cfg["fit"], 4, ("inf",), 31)
    f["B2"] = fit_model("B2", ts, pc, cfg["fit"], 4, ("inf",), 31, null_fit=f["B1"])
    return cfg, ts, ds, f


@pytest.mark.slow
def test_sandwich_close_to_learner_bootstrap_b0(setup):
    cfg, ts, ds, f = setup
    sw = sandwich(f["B0"], ts, ds, cfg["fit"], 4)
    assert sw["status"] == "ok" and sw["H_min_eig"] > 0
    bt = learner_bootstrap(f["B0"], ts, ds, cfg["fit"], 4, 24, ("inf",), 31)
    assert bt["n_ok"] >= 20
    for name in ("alpha_bar", "phi"):
        ratio = sw["params"][name]["se"] / bt["sd"][name]
        assert 0.5 < ratio < 2.0, (name, ratio)


@pytest.mark.slow
def test_null_test_structure_and_boundary(setup):
    cfg, ts, ds, f = setup
    out = null_test(f["B1"], f["B2"], ts, cfg, 400, 3, ("inf",), 31)
    assert out["clr_observed"] >= -1e-8 and out["n_ok"] + out["n_failed"] == 3
    assert all(r["clr"] >= -1e-8 for r in out["replicates"] if not r["failed"])          # nesting => CLR >= 0
    assert 1.0 / (out["n_ok"] + 1) <= out["p_value"] <= 1.0
    again = null_test(f["B1"], f["B2"], ts, cfg, 400, 3, ("inf",), 31)
    assert [r.get("clr") for r in again["replicates"]] == [r.get("clr") for r in out["replicates"]]   # deterministic


def test_sandwich_skips_boundary_parameters(setup):
    cfg, ts, ds, f = setup
    sw = sandwich(f["B2"], ts, ds, cfg["fit"], 4)
    if f["B2"]["theta"]["sigma2_F"] <= cfg["fit"]["boundary_tol"]:
        assert "sigma2_F" not in sw["params"] and "tau_F" not in sw["params"]
