"""python -m feedback_model audit  --config configs/experiment_06/stage0.yaml [--out DIR] [--workers n]
python -m feedback_model approx --config configs/experiment_06/stage0.yaml [--out results/experiment_06/stage0b] [--workers n]   (L1 step 1, G0-1b)
python -m feedback_model audit_l1 --config configs/experiment_06/stage0.yaml [--out results/experiment_06/stage0b] [--workers n]   (L1 step 2: fits, G0-3, G0-4)
python -m feedback_model report --config configs/experiment_06/stage0.yaml [--out DIR] [--md FILE]"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):     # before numpy loads (X2-F15)
    os.environ[_v] = "1"

import argparse
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="feedback_model")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("audit", "report", "approx", "audit_l1"):
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--out", default="results/experiment_06/stage0b" if name in ("approx", "audit_l1") else "results/experiment_06/stage0")
        if name in ("audit", "approx", "audit_l1"):
            p.add_argument("--workers", type=int, default=5)
        else:
            p.add_argument("--md", default=None)
    args = ap.parse_args(argv)
    from kt_trial.config import load_yaml
    from . import audit
    ac = load_yaml(args.config)
    if args.cmd == "audit_l1":
        return audit.run_audit_l1(ac, args.out, workers=args.workers)
    if args.cmd == "approx":
        return audit.run_approx(ac, args.out, workers=args.workers)
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
