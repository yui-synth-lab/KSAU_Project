import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

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
                    "G": topologies[name].get("generation", 4)
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])
    df["lnD"] = np.log(df["D"])

    def objective(params):
        a, b, c, d, c_glob = params
        n = np.round(a * df["lnD"] + b * df["G"] + c * df["C"] + d)
        ln_m_pred = kappa * df["v"] + c_glob + n * delta_c
        mae = np.mean(np.abs(ln_m_pred - df["ln_m"]))
        return mae

    # Initial guess
    initial_params = [4.5, 11, -4, 2, -3.75]
    
    res = minimize(objective, initial_params, method='Nelder-Mead', tol=1e-8)
    
    a, b, c, d, c_glob = res.x
    n = np.round(a * df["lnD"] + b * df["G"] + c * df["C"] + d)
    df["n"] = n.astype(int)
    df["ln_m_pred"] = kappa * df["v"] + c_glob + df["n"] * delta_c
    df["err_pct"] = np.abs(np.exp(df["ln_m_pred"] - df["ln_m"]) - 1) * 100
    mae_pct = np.mean(df["err_pct"])
    
    print(f"Optimized Parameters: a={a:.4f}, b={b:.4f}, c={c:.4f}, d={d:.4f}, C_glob={c_glob:.4f}")
    print(f"MAE (%): {mae_pct:.6f}%")
    
    status = "SUCCESS" if mae_pct < 0.1 else "FAILURE"
    print(f"Status: {status}")

    # Output results
    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Optimization to MAE 0.1% with topological rule",
        "optimized_formula": {
            "a": float(a), "b": float(b), "c": float(c), "d": float(d), "c_glob": float(c_glob),
            "rule": f"n = round({a:.2f}*lnD + {b:.2f}*G + {c:.2f}*C + {d:.2f})"
        },
        "computed_values": {
            "mae_pct": float(mae_pct),
            "status": status
        },
        "particle_details": df.replace([np.nan, np.inf, -np.inf], None).to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
