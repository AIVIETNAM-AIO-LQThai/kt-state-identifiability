"""Rule tests on synthetic job envelopes (X4-D08 (4)): verdict branches, gates, paired delta."""
import json
import numpy as np
import pytest

from discrimination_free import rules

H = "a" * 64


def _fit_arm(err, conv=True, ll=-100.0):
    b = {"status": "ok" if conv else "flagged", "converged": conv, "sigma2_F_error_vs_star": err, "theta": {"sigma2_F": 0.16 + err},
         "ll": ll, "flags": [], "boundary_hits": [], "start_agreement": {"n_starts_at_best": 5}, "n_polished": 1, "polish_line_search_failures": 0,
         "lambda_recovery": {"rmse_centred_log_lambda": 0.2}}
    return {"B1": dict(b, ll=ll - 50), "B2": b}


def _write(rd, name, job, result, status="ok"):
    (rd / "jobs").mkdir(parents=True, exist_ok=True)
    (rd / "jobs" / f"{name}.json").write_text(json.dumps({"job_id": name, "job": job, "status": status, "result": result, "code_hash": H}))


def _fits(rd, bias=None, rng=None):
    rng = rng or np.random.default_rng(0)
    for sid in ("V1", "V5"):
        for N in rules.NS:
            for rep in range(20):
                b2 = (bias or {}).get((sid, N), 0.0)
                e2, e1 = b2 + rng.normal(0, 0.01), 0.005 + rng.normal(0, 0.01)
                _write(rd, f"fit__{sid}__N{N}__r{rep}", dict(kind="fit", scenario=sid, N=N, rep=rep),
                       {"scenario": sid, "N": N, "rep": rep, "arms": {"twopl": _fit_arm(e2), "free1": _fit_arm(e1)}})


def _warps(rd, scale2=1.0, scale1=1.0, bad_share=0.0, R=150, rng=None):
    rng = rng or np.random.default_rng(1)
    draw = lambda s: float(0.0 if rng.random() < 0.5 else s * rng.chisquare(1))
    for sid, ests in (("V2", {"twopl": scale2}), ("V4", {"twopl": scale2, "free1": scale1})):
        for N in rules.NS:
            for rep in range(R // 2 if sid == "V4" else 25):
                res = {"scenario": sid, "N": N, "rep": rep}
                for est, sc in ests.items():
                    bad = est == "twopl" and rng.random() < bad_share
                    res[est] = {"fit_failed": False, "T": draw(sc), "T_star": draw(1.0), "sigma2_F": 0.0, "tau_F": 5.0, "sigma2_F_star_boot": 0.0,
                                "tau_F_star": 5.0, "converged": not bad, "star_converged": True, "star_failed": False}
                _write(rd, f"warp__{sid}__N{N}__r{rep}", dict(kind="warp", scenario=sid, N=N, rep=rep), res)


def _run(tmp_path, **kw):
    rd = tmp_path / "res"
    _fits(rd, bias=kw.pop("bias", None))
    _warps(rd, **kw)
    (rd / "manifest.json").write_text(json.dumps({"code_hash": H, "env": {"numpy": "2.5.3", "threads": {"OMP_NUM_THREADS": "1"}}}))
    return rules.evaluate(rd)


def test_ph4a_supported_and_not_supported(tmp_path):
    R = _run(tmp_path, scale2=1.0, scale1=1.0)
    assert R["rules"]["PH4a"]["verdict"] == "supported" and all(g["ok"] for g in R["gates"].values())
    R2 = _run(tmp_path / "b", bias={("V5", 1000): 0.10})
    assert R2["rules"]["PH4a"]["verdict"] == "not supported"


def test_ph4b_liberal_is_not_supported_and_calibrated_is_not_liberal(tmp_path):
    R = _run(tmp_path / "lib", scale2=6.0, scale1=6.0)
    assert R["rules"]["PH4b"]["twopl_pooled"]["verdict"] == "liberal" and R["rules"]["PH4b"]["verdict"] == "not supported"
    R = _run(tmp_path / "cal", scale2=1.0, scale1=1.0)
    assert R["rules"]["PH4b"]["twopl_pooled"]["verdict"] != "liberal" and R["rules"]["PH4c"]["V2_pooled"]["verdict"] != "liberal"


def test_g1_blocks_ph4b_and_ph4c_when_more_than_5_percent_fail(tmp_path):
    R = _run(tmp_path, bad_share=0.2)
    assert R["gates"]["G1 V4 twopl"]["ok"] is False and R["rules"]["PH4b"]["verdict"] == "not evaluable (gate)"
    assert R["rules"]["PH4c"]["verdict"] == "not evaluable (gate)"


def test_paired_delta_detects_a_liberal_comparator_and_not_equal_ones():
    rng = np.random.default_rng(5)
    n = 300
    mk = lambda T: [dict(fit_failed=False, star_failed=False, converged=True, T=float(t), T_star=float(s), N=300, rep=i)
                    for i, (t, s) in enumerate(zip(T, rng.chisquare(1, n) * (rng.random(n) < 0.5)))]
    Tlib = rng.chisquare(1, n) * 6 * (rng.random(n) < 0.5)
    Tok = rng.chisquare(1, n) * (rng.random(n) < 0.5)
    rows_free = mk(Tlib)
    Ts = np.array([r["T_star"] for r in rows_free])
    rows_2pl = [dict(r, T=float(t)) for r, t in zip(rows_free, Tok)]
    assert rules.paired_delta(rows_free, rows_2pl)["ci_above_zero"] is True
    assert rules.paired_delta(rows_2pl, rows_2pl)["ci_above_zero"] is False


def test_markdown_and_summarize_with_rules(tmp_path):
    R = _run(tmp_path)
    md = "\n".join(rules.markdown(R))
    assert "PH4a" in md and "PH4b" in md and "Gates" in md
