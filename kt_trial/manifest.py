"""Run provenance: software versions, code hash and git state."""
from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
REPO_DIR = PKG_DIR.parent


def code_hash() -> str:
    h = hashlib.sha256()
    for f in sorted(PKG_DIR.glob("*.py")):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def git_info() -> dict:
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=REPO_DIR, capture_output=True, text=True, timeout=20).stdout.strip()
        except Exception:
            return ""
    sha = run("rev-parse", "HEAD")
    return {"sha": sha or None, "branch": run("rev-parse", "--abbrev-ref", "HEAD") or None,
            "dirty": bool(run("status", "--porcelain")) if sha else None}


def environment_info() -> dict:
    import numpy, pandas, scipy, yaml
    return {"python": sys.version.split()[0], "executable": sys.executable, "platform": platform.platform(),
            "numpy": numpy.__version__, "scipy": scipy.__version__, "pandas": pandas.__version__,
            "pyyaml": yaml.__version__, "cpu_count": __import__("os").cpu_count()}


VERSION_KEYS = ("python", "numpy", "scipy", "pandas", "pyyaml")


def provenance() -> dict:
    return {"code_hash": code_hash(), "git": git_info(), "env": environment_info()}
