import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

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
    
    # Sector Bases (from v6.0 simulator and report)
    bases = {
        "quarks": 10.0,
        "leptons": 20.0,
        "bosons": 3.0
    }
    
    particles = []
    for sector, base in bases.items():
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                particles.append({
                    "name": name,
                    "sector": sector,
                    "mass": data["observed_mass_mev"],
                    "v": topologies[name]["volume"],
                    "base": base,
                    "N": topologies[name].get("crossing_number", 0),
                    "D": topologies[name].get("determinant", 1)
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])

    # Formula: ln(m) = kappa * v + C_sector + n * delta_c
    # where n = round( ( (base-1)*kappa*v + b_sector ) / delta_c )
    
    def evaluate(c_glob):
        df_copy = df.copy()
        
        # Sector-specific intercepts from v6.0 config
        # Quarks: bq = -(7 + 7*kappa)
        # Leptons: cl = ln(me)
        # Bosons: cb = 5.54 (from bosons scaling C)
        
        bq = -(7 + 7 * kappa)
        cl = np.log(0.511)
        cb = 5.5414
        
        sector_intercepts = {
            "quarks": bq,
            "leptons": cl,
            "bosons": cb
        }
        
        total_err = 0
        df_copy["ln_m_pred"] = 0.0
        df_copy["n"] = 0
        
        for sector, b in sector_intercepts.items():
            mask = df_copy["sector"] == sector
            base = bases[sector]
            v = df_copy.loc[mask, "v"]
            
            # Phase discretization of the (Base-1)*kappa*v + b term
            # n_exact = ( (base-1)*kappa*v + b - c_glob ) / delta_c
            n_exact = ((base - 1) * kappa * v + b - c_glob) / delta_c
            n = np.round(n_exact).astype(int)
            df_copy.loc[mask, "n"] = n
            df_copy.loc[mask, "ln_m_pred"] = kappa * v + c_glob + n * delta_c
            
        df_copy["err"] = df_copy["ln_m_pred"] - df_copy["ln_m"]
        mae = np.mean(np.abs(df_copy["err"]))
        return mae, df_copy

    # Scan c_glob
    best_mae = 100
    best_c = 0
    for c in np.linspace(-5, 5, 2001):
        mae, _ = evaluate(c)
        if mae < best_mae:
            best_mae = mae
            best_c = c
            
    final_mae, final_df = evaluate(best_c)
    final_df["err_pct"] = np.abs(np.exp(final_df["err"]) - 1) * 100
    mae_pct = np.mean(final_df["err_pct"])
    
    print(f"Best C_global: {best_c:.6f}")
    print(f"MAE (ln): {final_mae:.6f}")
    print(f"MAE (%): {mae_pct:.6f}%")
    print(f"R^2: {1 - np.sum(final_df['err']**2) / np.sum((final_df['ln_m'] - np.mean(final_df['ln_m']))**2):.8f}")
    
    status = "SUCCESS" if mae_pct < 0.1 else "FAILURE"
    print(f"Status: {status}")

    # Results
    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Verification of 0.1% MAE with sector-based phase discretization",
        "computed_values": {
            "mae_pct": float(mae_pct),
            "c_glob": float(best_c),
            "status": status
        },
        "particle_details": final_df.replace([np.nan, np.inf, -np.inf], None).to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
