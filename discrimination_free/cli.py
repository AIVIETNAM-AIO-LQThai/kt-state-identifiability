"""python -m discrimination_free audit --config configs/experiment_04/stage0.yaml [--out DIR]"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):     # before numpy loads (X2-F15)
    os.environ[_v] = "1"

import argparse
import json
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="discrimination_free")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit")
    a.add_argument("--config", required=True)
    a.add_argument("--out", default="results/experiment_04/stage0")
    a.add_argument("--score-learners", type=int, default=None)
    a.add_argument("--tag", default="audit")
    sub.add_parser("check-env")
    args = ap.parse_args(argv)
    from kt_trial.config import load_scenario, load_yaml
    from kt_trial.manifest import environment_info, git_info
    from kt_trial.runner import write_json_atomic
    from kt_trial.schedule import build_templates
    threads = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
    if args.cmd == "check-env":
        print(json.dumps({"env": environment_info(), "threads": threads}, indent=1))
        return 0
    from .audit import gate, run_audit
    ac = load_yaml(args.config)
    if args.score_learners:
        ac["score_learners"] = args.score_learners
    cfg = load_scenario(ac["scenario"])
    ts = build_templates(cfg)
    res = run_audit(cfg, ts, ac)
    res["gate_numbers"] = gate(res, ac)
    res["provenance"] = {"env": environment_info(), "git": git_info(), "config": ac, "threads": threads}
    out = Path(args.out)
    write_json_atomic(out / f"{args.tag}.json", res)
    print("wrote", out / f"{args.tag}.json")
    print(json.dumps(res["gate_numbers"], indent=1))
    print("scale invariance:", res["scale_invariance"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
