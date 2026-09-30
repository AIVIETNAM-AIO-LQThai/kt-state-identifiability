"""Versioned configuration loading, scenario merging, hashing and deterministic seeding."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs" / "experiment_01"


def _deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def load_yaml(path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_design(path=None) -> dict:
    return load_yaml(path or CONFIG_DIR / "design.yaml")


def load_scenario(scenario_id: str, design: dict | None = None, config_dir=None) -> dict:
    """Return the full config for one scenario: design.yaml with scenario overrides applied."""
    cdir = Path(config_dir) if config_dir else CONFIG_DIR
    design = design if design is not None else load_design(cdir / "design.yaml")
    sc = load_yaml(cdir / "scenarios" / f"{scenario_id}.yaml")
    cfg = copy.deepcopy(design)
    for key in ("design", "generating", "dgp", "fit"):
        cfg[key] = _deep_merge(cfg.get(key, {}), sc.get(key, {}))
    cfg["scenario"] = {"id": sc["id"], "description": sc.get("description", ""),
                       "violations": list(sc.get("violations", []))}
    return cfg


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def config_hash(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def file_sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def seed_sequence(master_seed: int, *keys) -> np.random.SeedSequence:
    """Deterministic child seed keyed by arbitrary labels (stage, scenario, N, rep, purpose...)."""
    digest = hashlib.sha256("|".join(str(k) for k in keys).encode("utf-8")).digest()
    ints = [int.from_bytes(digest[i:i + 4], "little") for i in range(0, 16, 4)]
    return np.random.SeedSequence([int(master_seed), *ints])


def rng_for(master_seed: int, *keys) -> np.random.Generator:
    return np.random.default_rng(seed_sequence(master_seed, *keys))


def generating_theta_dict(cfg: dict) -> dict:
    """Natural-scale generating parameters (variances, not sds) from a scenario config."""
    g = cfg["generating"]
    K = cfg["design"]["n_skills"]
    sm = g["sigma_M"]
    Sigma_M = sm["ind"] * np.eye(K) + sm["common"] * np.ones((K, K))
    return dict(alpha_bar=g["alpha_bar"], phi=g["phi"], sigma2_alpha=g["sigma_alpha"] ** 2,
                r_bar=g["r_bar"], tau_R=g["tau_R"], sigma2_r=g["sigma_r"] ** 2,
                sigma2_F=g["sigma_F"] ** 2, tau_F=g["tau_F"], Sigma_M=Sigma_M)
