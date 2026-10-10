"""python -m state_dependence audit  --config configs/experiment_05/stage0.yaml [--out DIR] [--workers n]
python -m state_dependence report --config configs/experiment_05/stage0.yaml [--out DIR] [--md FILE]
python -m state_dependence run    --config configs/experiment_05/stage_pilot.yaml [--dry-run] [--workers n] [--retry-errors] [--allow-mismatch] [--frozen-sha256 SHA]
python -m state_dependence summarize --results DIR [--rules]"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):     # before numpy loads (X2-F15)
    os.environ[_v] = "1"

import argparse
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="state_dependence")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("audit", "report"):
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--out", default="results/experiment_05/stage0")
        if name == "audit":
            p.add_argument("--workers", type=int, default=4)
        else:
            p.add_argument("--md", default=None)
    r = sub.add_parser("run")
    r.add_argument("--config", required=True)
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--workers", type=int, default=None)
    r.add_argument("--retry-errors", action="store_true")
    r.add_argument("--allow-mismatch", action="store_true")
    r.add_argument("--frozen-sha256", default=None)
    sm = sub.add_parser("summarize")
    sm.add_argument("--results", required=True)
    sm.add_argument("--rules", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "run":
        from .runner import run_stage
        return run_stage(args.config, workers=args.workers, dry_run=args.dry_run, retry_errors=args.retry_errors,
                         allow_mismatch=args.allow_mismatch, frozen_sha256=args.frozen_sha256)
    if args.cmd == "summarize":
        from .summarize import summarize
        summarize(args.results, with_rules=args.rules)
        print("wrote summary.json / summary.md in", args.results)
        return 0
    from kt_trial.config import load_yaml
    from . import audit
    ac = load_yaml(args.config)
    if args.cmd == "audit":
        threads = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
        print("threads", threads)
        return audit.run_audit(ac, args.out, workers=args.workers)
    S = audit.summarize(ac, args.out)
    md = audit.markdown(S)
    Path(args.out, "summary.md").write_text(md, encoding="utf-8", newline="\n")
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8", newline="\n")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
