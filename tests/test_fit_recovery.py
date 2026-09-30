import numpy as np
import pytest

from kt_trial.composite_likelihood import pair_counts
from kt_trial.config import load_scenario
from kt_trial.fit import fit_model
from kt_trial.schedule import build_templates
from kt_trial.simulator import simulate


@pytest.fixture(scope="module")
def s1_fits():
    cfg = load_scenario("S1")
    ts = build_templates(cfg)[:2]
    fit_cfg = dict(cfg["fit"], n_starts=2)
    ds = simulate(cfg, 3000, ("rec",), 21, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    fits = {}
    for m in ("B0", "B1", "B2"):
        fits[m] = fit_model(m, ts, pc, fit_cfg, 4, ("rec",), 21, null_fit=fits.get("B1"))
    return fits


@pytest.mark.slow
def test_recovery_small_case(s1_fits):
    f = s1_fits["B2"]
    assert f["status"] == "ok" and f["converged"]
    th = f["theta"]
    assert abs(th["alpha_bar"] - 0.15) < 0.03 and abs(th["phi"] - 0.20) < 0.06
    assert abs(th["r_bar"] - 0.35) < 0.06 and abs(th["tau_R"] - 5.0) < 1.5
    assert abs(th["sigma2_F"] - 0.16) < 0.06 and 4.0 < th["tau_F"] < 25.0


@pytest.mark.slow
def test_nested_likelihood_ordering_and_result_fields(s1_fits):
    assert s1_fits["B0"]["ll"] < s1_fits["B1"]["ll"] <= s1_fits["B2"]["ll"] + 1e-6
    for k in ("ll", "grad_norm", "converged", "boundary_hits", "flags", "runtime", "start_agreement", "seed_keys"):
        assert k in s1_fits["B2"]


@pytest.mark.slow
def test_null_fit_hits_boundary_or_is_small():
    cfg = load_scenario("S2")
    ts = build_templates(cfg)[:2]
    fit_cfg = dict(cfg["fit"], n_starts=2)
    ds = simulate(cfg, 3000, ("null",), 22, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    f1 = fit_model("B1", ts, pc, fit_cfg, 4, ("null",), 22)
    f2 = fit_model("B2", ts, pc, fit_cfg, 4, ("null",), 22, null_fit=f1)
    assert f2["ll"] >= f1["ll"] - 1e-9                      # CLR >= 0 by construction
    assert f2["theta"]["sigma2_F"] < 0.04
    if f2["theta"]["sigma2_F"] <= 1e-6:
        assert any("tau_F_not_identified" in x for x in f2["flags"])


def test_failed_fit_is_recorded_as_data():
    cfg = load_scenario("S1")
    ts = build_templates(cfg)[:2]
    ds = simulate(cfg, 50, ("bad",), 1, ts)
    pc = pair_counts(ds.Y, ds.template_id, 2)
    pc.counts[:] = np.nan
    f = fit_model("B0", ts, pc, dict(cfg["fit"], n_starts=2), 4, ("bad",), 1)
    assert f["status"] == "failed" and "all_starts_failed" in f["flags"] and f["runs"]
