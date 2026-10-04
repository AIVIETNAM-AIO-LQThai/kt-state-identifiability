"""Exact-environment guard for steps that regenerate Experiment-1 data (fingerprint, addendum).

Experiment 1 ran on one specific numpy/scipy/python build; the generating Sigma_M has a repeated eigenvalue, so the SVD-based
sampler, and the near-null optimiser endpoints, can differ in other builds. These steps therefore refuse to run elsewhere."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import scipy

from kt_trial.runner import read_json

EXIT_ENV_MISMATCH = 6


def live_env() -> dict:
    return {"executable": sys.executable, "python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__}


def expected_env(exp1_results: str) -> dict:
    e = read_json(Path(exp1_results) / "manifest.json")["env"]
    return {k: e[k] for k in ("python", "numpy", "scipy")}


def env_mismatches(expected: dict, actual: dict) -> list[str]:
    return [f"{k}: Experiment 1 used {expected[k]}, this interpreter has {actual[k]}" for k in ("python", "numpy", "scipy") if expected[k] != actual[k]]


def require_exact_environment(exp1_results: str, out=print) -> bool:
    """Print the interpreter and return True iff its python/numpy/scipy equal the Experiment-1 manifest. No override."""
    act, exp = live_env(), expected_env(exp1_results)
    out(f"interpreter: {act['executable']}  python {act['python']}  numpy {act['numpy']}  scipy {act['scipy']}")
    diffs = env_mismatches(exp, act)
    if diffs:
        out("REFUSED: this is not the Experiment-1 environment (needed to regenerate its data bit for bit):")
        for d in diffs:
            out("  " + d)
        out("Run the command with the interpreter of the environment that produced Experiment 1 (the .venv12 python.exe).")
        return False
    return True
