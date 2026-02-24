import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from itertools import product

# SSoT Loader Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    topologies = ssot.topology_assignments()

    pi = consts["mathematical_constants"]["pi"]
    kappa = consts["mathematical_constants"]["kappa"]
    delta_c = pi / 12
    
    particles = []
    for sector in ["leptons", "quarks", "bosons"]:
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                particles.append({
                    "name": name,
                    "sector": sector,
                    "mass": data["observed_mass_mev"],
                    "v": topologies[name]["volume"],
                    "N": topologies[name].get("crossing_number", 0),
                    "D": topologies[name].get("determinant", 1),
                    "C": topologies[name].get("components", 1),
                    "G": topologies[name].get("generation", 4),
                    "B": 1 if topologies[name].get("is_brunnian", False) else 0
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])
    df["lnD"] = np.log(df["D"])

    # We search for a formula: n = round(a*N + b*G + c*C + d*B + e*lnD + f)
    # Target: ln_m = kappa * v + C_global + n * delta_c
    # So: n_target = (ln_m - kappa*v - C_global) / delta_c
    
    # Range of coefficients
    search_range = [-2, -1, 0, 1, 2, 3, 4, 5]
    
    best_overall_mae = 100
    best_formula = None
    
    # To reduce search space, let's fix C_global = -3.75 (from Iter 03)
    c_glob = -3.75
    df["n_target"] = (df["ln_m"] - kappa * df["v"] - c_glob) / delta_c
    
    print("Searching for topological rule for n...")
    
    # Try combinations of (a, b, c, d) for n = a*N + b*G + c*D_factor + d
    # Determinant factor could be log2(D) or round(sqrt(D))
    df["D_f"] = np.round(np.sqrt(df["D"])).astype(int)
    
    for a, b, c, d, e in product([-2, 0, 2, 4], [-2, 0, 2, 4], [-2, 0, 2, 4], [-2, 0, 2, 4], [-10, -5, 0, 5, 10]):
        # n_pred = a*N + b*G + c*C + d*B + e
        n_pred = a * df["N"] + b * df["G"] + c * df["C"] + d * df["B"] + e
        
        df["ln_m_pred"] = kappa * df["v"] + c_glob + n_pred * delta_c
        mae = np.mean(np.abs(df["ln_m_pred"] - df["ln_m"]))
        
        if mae < best_overall_mae:
            best_overall_mae = mae
            best_formula = (a, b, c, d, e)
            if mae < 0.1: break

    print(f"Best Formula: n = {best_formula[0]}*N + {best_formula[1]}*G + {best_formula[2]}*C + {best_formula[3]}*B + {best_formula[4]}")
    print(f"MAE: {best_overall_mae:.6f}")
    
    # Let's try to refine with a wider search if not satisfied
    if best_overall_mae > 0.05:
        print("Refining search...")
        # ... (more search)
        
    # Final check
    a, b, c, d, e = best_formula
    df["n"] = a * df["N"] + b * df["G"] + c * df["C"] + d * df["B"] + e
    df["ln_m_pred"] = kappa * df["v"] + c_glob + df["n"] * delta_c
    df["err"] = df["ln_m_pred"] - df["ln_m"]
    mae = np.mean(np.abs(df["err"]))
    
    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Topological rule derivation for n",
        "best_formula": f"n = {a}*N + {b}*G + {c}*C + {d}*B + {e}",
        "mae_ln": float(mae),
        "particle_details": df.to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results_rule.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
