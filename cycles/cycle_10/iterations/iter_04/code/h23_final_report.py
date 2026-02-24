import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression

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
    
    # Calculate ideal n for each particle
    # ln_m = kappa*v + C_glob + n*delta_c
    # We fix C_glob = -3.75
    c_glob = -3.75
    df["n_exact"] = (df["ln_m"] - kappa * df["v"] - c_glob) / delta_c
    df["n_int"] = np.round(df["n_exact"]).astype(int)
    
    # Show correlation with invariants
    features = ["N", "D", "C", "G", "B"]
    X = df[features]
    y = df["n_int"]
    
    reg = LinearRegression().fit(X, y)
    r2_invariants = reg.score(X, y)
    
    df["n_pred_rule"] = np.round(reg.predict(X)).astype(int)
    
    # Calculate MAE with n_int (Optimized Integers)
    df["ln_m_opt"] = kappa * df["v"] + c_glob + df["n_int"] * delta_c
    mae_opt_pct = np.mean(np.abs(np.exp(df["ln_m_opt"] - df["ln_m"]) - 1)) * 100
    
    # Calculate MAE with n_pred_rule (The Rule)
    df["ln_m_rule"] = kappa * df["v"] + c_glob + df["n_pred_rule"] * delta_c
    mae_rule_pct = np.mean(np.abs(np.exp(df["ln_m_rule"] - df["ln_m"]) - 1)) * 100

    print(f"Optimized Integer Model MAE: {mae_opt_pct:.4f}%")
    print(f"Topological Rule R^2: {r2_invariants:.4f}")
    print(f"Rule-based MAE: {mae_rule_pct:.4f}%")

    # Save results
    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Optimization to MAE 0.1% and rule derivation",
        "computed_values": {
            "mae_optimized_pct": float(mae_opt_pct),
            "mae_rule_pct": float(mae_rule_pct),
            "r2_invariants": float(r2_invariants)
        },
        "formula": {
            "features": features,
            "coefs": [float(c) for c in reg.coef_],
            "intercept": float(reg.intercept_)
        },
        "particle_details": df.replace([np.nan, np.inf, -np.inf], None).to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
