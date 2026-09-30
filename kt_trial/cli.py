"""Command-line entry points: check-env, audit-design, simulate, fit, run, summarize."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")


def cmd_check_env(a) -> int:
    from .manifest import provenance
    p = provenance()
    print(json.dumps(p, indent=2))
    try:
        import numpy, scipy, pandas, yaml  # noqa: F401
        print("imports: OK")
        return 0
    except Exception as e:
        print("imports FAILED:", e)
        return 1


def cmd_audit(a) -> int:
    from .config import load_scenario
    from .identifiability import run_identifiability
    from .schedule import audit_design, build_templates
    from .runner import write_json_atomic
    cfg = load_scenario(a.scenario)
    ts = build_templates(cfg)
    sched = audit_design(cfg, ts)
    print(json.dumps(sched, indent=1))
    out = {"scenario": a.scenario, "schedule_audit": sched}
    if not a.no_identifiability:
        ident = run_identifiability(cfg, ts, a.seed, n_score_learners=a.score_learners)
        out["identifiability"] = ident
        for k, v in ident["points"].items():
            print(f"[{k}] rank {v['numerical_rank']}/{v['n_params']} cond {v['condition_number']:.0f} "
                  f"pred SE(sigma2_F) N=300: {v['predicted_godambe_se']['300']['sigma2_F']:.4f}, N=1000: {v['predicted_godambe_se']['1000']['sigma2_F']:.4f}")
        d = ident.get("deficient_single_session_constant_F")
        if d:
            print(f"[deficient control] rank {d['numerical_rank']}/{d['n_params']} (must be < {d['n_params']})")
    write_json_atomic(Path(a.out) / "design_audit.json", out)
    print("wrote", Path(a.out) / "design_audit.json")
    return 0


def cmd_simulate(a) -> int:
    import numpy as np
    from .config import load_scenario
    from .schedule import build_templates
    from .simulator import simulate
    cfg = load_scenario(a.scenario)
    ds = simulate(cfg, a.N, ("cli", a.scenario, a.N, a.rep), a.seed, build_templates(cfg))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, Y=ds.Y, template_id=ds.template_id, meta=json.dumps(ds.meta))
    print(f"wrote {a.out}: Y{ds.Y.shape} mean success {ds.Y.mean():.3f}; realised {ds.meta['realised']}")
    return 0


def cmd_fit(a) -> int:
    from .composite_likelihood import pair_counts
    from .config import load_scenario
    from .fit import fit_model
    from .moments import Theta
    from .schedule import build_templates
    from .simulator import simulate
    cfg = load_scenario(a.scenario)
    cfg["fit"]["n_starts"] = a.starts
    ts = build_templates(cfg)
    ds = simulate(cfg, a.N, ("cli", a.scenario, a.N, a.rep), a.seed, ts)
    pc = pair_counts(ds.Y, ds.template_id, len(ts))
    K = cfg["design"]["n_skills"]
    fits = {}
    for m in a.models.split(","):
        b1 = fits.get("B1")
        fits[m] = fit_model(m, ts, pc, cfg["fit"], K, ("cli", a.scenario, a.N, a.rep), a.seed,
                            warm=Theta.from_dict(b1["theta"]) if (m == "B2" and b1 and b1["status"] != "failed") else None,
                            null_fit=b1 if m == "B2" else None)
        f = fits[m]
        print(m, f["status"], "ll", round(f.get("ll", float("nan")), 1), "flags", f["flags"], f"{f['runtime']:.0f}s")
        if "theta" in f:
            print("   ", {k: round(v, 4) for k, v in f["theta"].items() if k != "Sigma_M"})
    return 0


def cmd_run(a) -> int:
    from .runner import run_stage
    return run_stage(a.config, a.results_root, a.workers, a.dry_run, a.retry_errors, a.allow_mismatch, a.frozen_sha256)


def cmd_summarize(a) -> int:
    from .summarize import summarize
    s = summarize(a.results)
    print((Path(a.results) / "summary.md").read_text(encoding="utf-8"))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m kt_trial", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-env").set_defaults(fn=cmd_check_env)
    p = sub.add_parser("audit-design"); p.set_defaults(fn=cmd_audit)
    p.add_argument("--scenario", default="S1"); p.add_argument("--out", default="results/experiment_01/audit")
    p.add_argument("--seed", type=int, default=20261001); p.add_argument("--score-learners", type=int, default=None)
    p.add_argument("--no-identifiability", action="store_true")
    p = sub.add_parser("simulate"); p.set_defaults(fn=cmd_simulate)
    p.add_argument("--scenario", default="S1"); p.add_argument("--N", type=int, default=64); p.add_argument("--rep", type=int, default=0)
    p.add_argument("--seed", type=int, default=20261001); p.add_argument("--out", default="results/experiment_01/sim/data.npz")
    p = sub.add_parser("fit"); p.set_defaults(fn=cmd_fit)
    p.add_argument("--scenario", default="S1"); p.add_argument("--N", type=int, default=64); p.add_argument("--rep", type=int, default=0)
    p.add_argument("--seed", type=int, default=20261001); p.add_argument("--models", default="B0,B1,B2"); p.add_argument("--starts", type=int, default=5)
    p = sub.add_parser("run"); p.set_defaults(fn=cmd_run)
    p.add_argument("--config", required=True); p.add_argument("--results-root", default="results/experiment_01")
    p.add_argument("--workers", type=int, default=None); p.add_argument("--dry-run", action="store_true")
    p.add_argument("--retry-errors", action="store_true"); p.add_argument("--allow-mismatch", action="store_true")
    p.add_argument("--frozen-sha256", default=None, help="required for the confirmatory stage")
    p = sub.add_parser("summarize"); p.set_defaults(fn=cmd_summarize)
    p.add_argument("--results", required=True)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
