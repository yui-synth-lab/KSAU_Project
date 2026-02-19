#!/usr/bin/env python3
"""
KSAU v24.0 Utilities: SSoT Data Access
======================================
Centralized access to Leech Shell configurations and cosmological benchmarks.
Enforces no-hard-coding rule for physical constants.
"""

import json
from pathlib import Path
import numpy as np

BASE = Path("e:/Obsidian/KSAU_Project")
LEECH_CFG = BASE / "v24.0" / "data" / "leech_shell_config.json"
BENCHMARK_CFG = BASE / "v24.0" / "data" / "cosmological_benchmarks.json"

def load_leech_shells():
    """Returns a dictionary of shell_index -> magnitude from SSoT."""
    with open(LEECH_CFG, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    shells = {}
    for key, val in data["leech_shell_distances"].items():
        if key.startswith("shell_"):
            try:
                idx = int(key.split("_")[1])
                shells[idx] = val["magnitude"]
            except (ValueError, IndexError):
                continue
    return shells

def load_cosmological_benchmarks():
    """Returns benchmark data from SSoT."""
    with open(BENCHMARK_CFG, "r", encoding="utf-8") as f:
        return json.load(f)

def get_z_transition_threshold():
    """
    Returns the redshift transition threshold from benchmarks.
    Note: This is currently a phenomenological adjustment parameter 
    to match high-z CMB lensing data, not a first-principles derivation.
    """
    bench = load_cosmological_benchmarks()
    return bench.get("leech_shells", {}).get("z_high", 1.0)

def get_shell_assignment(epoch="z0"):
    """Returns the shell index assignment for a given epoch."""
    bench = load_cosmological_benchmarks()
    return bench.get("leech_shells", {}).get(epoch, 2)
