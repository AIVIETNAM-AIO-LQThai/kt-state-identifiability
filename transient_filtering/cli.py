"""python -m transient_filtering {check-env, fingerprint, run, summarize, addendum-select, addendum-run}"""
from __future__ import annotations

import argparse
import json
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="transient_filtering")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check-env")
    f = sub.add_parser("fingerprint", help="regenerate Experiment-1 data and compare with the saved fits (provenance)")
    f.add_argument("--config", required=True, help="Experiment-2 stage config (for the Experiment-1 paths)")
    f.add_argument("--dataset", action="append", required=True, help="SCENARIO:N:REP (repeatable)")
    f.add_argument("--out", default=None)
    r = sub.add_parser("run")
    r.add_argument("--config", required=True)
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--retry-errors", action="store_true")
    r.add_argument("--allow-mismatch", action="store_true")
    r.add_argument("--frozen-sha256", default=None)
    s = sub.add_parser("summarize")
    s.add_argument("--results", required=True)
    a = sub.add_parser("addendum-select")
    a.add_argument("--config", required=True)
    b = sub.add_parser("addendum-run")
    b.add_argument("--config", required=True)
    b.add_argument("--workers", type=int, default=1)
    b.add_argument("--limit", type=int, default=None, help="run only the first LIMIT selected datasets (benchmark)")
    b.add_argument("--tiers", default=None, help="comma list of tiers, e.g. A,B")
    args = ap.parse_args(argv)
    if args.cmd == "check-env":
        from .runner import provenance
        print(json.dumps(provenance(), indent=1)); return 0
    if args.cmd == "fingerprint":
        from kt_trial.config import load_yaml
        from .regenerate import exp1_stage_cfg, fingerprint
        c2 = load_yaml(args.config); s1 = exp1_stage_cfg(c2["exp1"]["stage_config"]); res = []
        for d in args.dataset:
            sid, N, rep = d.split(":")
            x = fingerprint(s1, c2["exp1"]["results"], sid, int(N), int(rep)); res.append(x)
            print(f"{d}: match={x['match']} worst_rel_diff={x['worst_relative_difference']:.3e} "
                  f"keep_latent_invariant={x['keep_latent_invariant']}")
        if args.out:
            from kt_trial.runner import write_json_atomic
            from pathlib import Path
            from .runner import provenance
            write_json_atomic(Path(args.out), {"provenance": provenance(), "results": res})
        return 0 if all(x["match"] for x in res) else 5
    if args.cmd == "run":
        from .runner import run_stage
        return run_stage(args.config, workers=args.workers, dry_run=args.dry_run, retry_errors=args.retry_errors,
                         allow_mismatch=args.allow_mismatch, frozen_sha256=args.frozen_sha256)
    if args.cmd == "summarize":
        from .summarize import summarize
        summarize(args.results); return 0
    if args.cmd == "addendum-select":
        from .addendum import select_cli
        return select_cli(args.config)
    from .addendum import run_cli
    return run_cli(args.config, args.workers, args.limit, args.tiers.split(",") if args.tiers else None)


if __name__ == "__main__":
    sys.exit(main())
