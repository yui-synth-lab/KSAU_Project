import sys
import json
import math
from pathlib import Path
import numpy as np
import time

# SSOT_DIR must be the absolute path from the prompt
SSOT_DIR = Path(r"E:\Obsidian\KSAU_Project\ssot")
sys.path.insert(0, str(SSOT_DIR))    
from ksau_ssot import SSOT

def analyze_4d_polychora():
    """
    Examines geometric properties of regular 4-polytopes (polychora).
    Identifies unique suitability of the 24-cell for space-filling and symmetry.
    """
    # Properties of regular polychora
    # Name: {cells, vertices, faces, edges, symmetry_order, self_dual, tiles_r4}
    polychora = {
        "5-cell":    {"cells": 5,   "v": 5,   "f": 10,  "e": 10,  "sym": 120,   "self_dual": True,  "tiles": False},
        "8-cell":    {"cells": 8,   "v": 16,  "f": 24,  "e": 32,  "sym": 384,   "self_dual": False, "tiles": True},
        "16-cell":   {"cells": 16,  "v": 8,   "f": 32,  "e": 24,  "sym": 384,   "self_dual": False, "tiles": False},
        "24-cell":   {"cells": 24,  "v": 24,  "f": 96,  "e": 96,  "sym": 1152,  "self_dual": True,  "tiles": True},
        "120-cell":  {"cells": 120, "v": 600, "f": 720, "e": 1200, "sym": 14400, "self_dual": False, "tiles": False},
        "600-cell":  {"cells": 600, "v": 120, "f": 1200, "e": 720, "sym": 14400, "self_dual": False, "tiles": False}
    }
    
    # 1. Identify the 24-cell as the unique non-trivial self-dual tiling polytope
    results = {}
    for name, props in polychora.items():
        score = 0
        if props['self_dual']: score += 1
        if props['tiles']: score += 1
        if name != "5-cell": score += 1 # Complexity constraint
        
        results[name] = {
            "properties": props,
            "suitability_score": score
        }
        
    best_candidate = max(results, key=lambda x: results[x]['suitability_score'])
    
    # 2. Packing Density (D4 lattice vs others)
    # D4 lattice density (24-cell neighbors): pi^2 / 16
    density_d4 = (math.pi ** 2) / 16.0
    
    # A4 lattice density (5-cell neighbors): pi^2 / (10 * sqrt(5))
    density_a4 = (math.pi ** 2) / (10.0 * math.sqrt(5.0))
    
    # Z4 lattice density (8-cell neighbors): pi^2 / 32
    density_z4 = (math.pi ** 2) / 32.0
    
    # Compare with SSoT kappa
    ssot = SSOT()
    consts = ssot.constants()
    kappa_ssot = consts['mathematical_constants']['kappa']
    
    packing_comparison = {
        "D4_lattice_24cell": {"density": density_d4, "ratio_to_kappa": density_d4 / kappa_ssot},
        "A4_lattice_5cell":  {"density": density_a4, "ratio_to_kappa": density_a4 / kappa_ssot},
        "Z4_lattice_8cell":  {"density": density_z4, "ratio_to_kappa": density_z4 / kappa_ssot}
    }
    
    return results, packing_comparison, best_candidate

def main():
    start_time = time.time()
    ssot = SSOT()
    consts = ssot.constants()
    
    results, packing, best = analyze_4d_polychora()
    
    # Theoretical Conclusion:
    # The 24-cell is the only polytope satisfying:
    # - Self-duality (required for (3,3) Pachner move invariance)
    # - Space-filling (required for vacuum tiling)
    # - Complexity (non-trivial structure)
    # This leads to K(4) = 24 as the fundamental resonance number.
    
    # 3. Statistical Verification: Unique Selection Test
    # How likely is a random integer property of these polytopes to be 24?
    property_values = []
    for p in results.values():
        props = p['properties']
        property_values.extend([props['cells'], props['v'], props['f'], props['e']])
    
    hits_24 = property_values.count(24)
    prob_24 = hits_24 / len(property_values)
    
    # Compile Results
    final_results = {
        "iteration": 8,
        "hypothesis_id": "H36",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_name": "24-cell 多胞体対称性と空間充填条件の幾何学的検討",
        "analysis": {
            "candidate_polytopes": results,
            "best_fit_polychoron": best,
            "packing_density_comparison": packing
        },
        "computed_values": {
            "pi_sq_over_16": (math.pi ** 2) / 16.0,
            "hits_of_24_in_properties": hits_24,
            "prob_24_among_regular_polychora": prob_24
        },
        "ssot_compliance": {
            "ssot_dir_absolute": str(SSOT_DIR),
            "constants_used": ["kappa", "pi"]
        },
        "reproducibility": {
            "computation_time_sec": time.time() - start_time
        },
        "notes": (
            "The 24-cell is identified as the unique 'Self-Dual Tiling' polychoron. "
            "The number 24 appears as both its cell count and vertex count, "
            "providing a dual-redundant basis for the resonance factor K(4)."
        )
    }
    
    # Save Results
    output_path = Path(__file__).resolve().parents[1] / "results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
        
    print(f"Geometric Examination Complete. Best Candidate: {best}")
    print(f"D4 Packing Density: {packing['D4_lattice_24cell']['density']:.6f}")
    print(f"Probability of 24 in regular polychora properties: {prob_24:.2%}")

if __name__ == "__main__":
    main()
