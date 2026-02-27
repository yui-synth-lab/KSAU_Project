import sys
from pathlib import Path
import json
import pandas as pd

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()

    # Rule Definition (from Roadmap H55 and SSoT assignment_rules)
    K = consts.get("mathematical_constants", {}).get("k_resonance", 24)
    N_THRESHOLD = K / 3  # 8

    results = {
        "iteration": 1,
        "hypothesis_id": "H55",
        "task": "24-cell Symmetry Rule Formulation and Application",
        "K": K,
        "n_threshold": N_THRESHOLD,
        "evaluations": {},
        "summary": {
            "lepton_rule_match": 0,
            "boson_rule_match": 0,
            "quark_rule_match": 0,
            "stable_rule_match": 0
        }
    }

    # Define Sectors
    leptons = ["Electron", "Muon", "Tau"]
    quarks = ["Up", "Down", "Strange", "Charm", "Bottom", "Top"]
    bosons = ["W", "Z", "Higgs"]

    # Rule 1: Leptons (c=1, n < 8, Det = 2^g + 1)
    for name in leptons:
        data = assignments.get(name)
        g = data["generation"]
        c = data["components"]
        n = data["crossing_number"]
        det = data["determinant"]
        
        det_target = 2**g + 1
        rule_match = (c == 1) and (n < N_THRESHOLD) and (det == det_target)
        
        results["evaluations"][name] = {
            "sector": "Lepton",
            "c": c, "n": n, "det": det, "g": g,
            "det_target": det_target,
            "rule_match": rule_match,
            "violations": []
        }
        if not (c == 1): results["evaluations"][name]["violations"].append("c != 1")
        if not (n < N_THRESHOLD): results["evaluations"][name]["violations"].append(f"n >= {N_THRESHOLD}")
        if not (det == det_target): results["evaluations"][name]["violations"].append(f"det != 2^g + 1 ({det_target})")
        
        if rule_match: results["summary"]["lepton_rule_match"] += 1

    # Rule 2: Bosons (c >= 2, n >= 8, Brunnian)
    for name in bosons:
        data = assignments.get(name)
        c = data["components"]
        n = data["crossing_number"]
        det = data["determinant"]
        is_brunnian = data.get("is_brunnian", False)
        
        rule_match = (c >= 2) and (n >= N_THRESHOLD) and is_brunnian
        
        results["evaluations"][name] = {
            "sector": "Boson",
            "c": c, "n": n, "det": det,
            "is_brunnian": is_brunnian,
            "rule_match": rule_match,
            "violations": []
        }
        if not (c >= 2): results["evaluations"][name]["violations"].append("c < 2")
        if not (n >= N_THRESHOLD): results["evaluations"][name]["violations"].append(f"n < {N_THRESHOLD}")
        if not is_brunnian: results["evaluations"][name]["violations"].append("not brunnian")
        
        if rule_match: results["summary"]["boson_rule_match"] += 1

    # Rule 3: Quarks (c >= 2, n >= 8)
    for name in quarks:
        data = assignments.get(name)
        c = data["components"]
        n = data["crossing_number"]
        det = data["determinant"]
        
        rule_match = (c >= 2) and (n >= N_THRESHOLD)
        
        results["evaluations"][name] = {
            "sector": "Quark",
            "c": c, "n": n, "det": det,
            "rule_match": rule_match,
            "violations": []
        }
        if not (c >= 2): results["evaluations"][name]["violations"].append("c < 2")
        if not (n >= N_THRESHOLD): results["evaluations"][name]["violations"].append(f"n < {N_THRESHOLD}")
        
        if rule_match: results["summary"]["quark_rule_match"] += 1

    # Rule 4: Stable Particles (Det % 24 == 0)
    # Note: Electron and Proton (Up/Down) are stable.
    stable_particles = ["Electron", "Up", "Down"]
    for name in stable_particles:
        det = assignments[name]["determinant"]
        is_stable_geometric = (det % K == 0)
        results["evaluations"][name]["is_stable_geometric"] = is_stable_geometric
        if is_stable_geometric:
            results["summary"]["stable_rule_match"] += 1

    # Save results
    output_path = Path("E:/Obsidian/KSAU_Project/cycles/cycle_22/iterations/iter_01/results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
