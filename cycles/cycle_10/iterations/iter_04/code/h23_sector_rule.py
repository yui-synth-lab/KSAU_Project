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
    
    particles = []
    for sector in ["leptons", "quarks", "bosons"]:
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                particles.append({
                    "name": name,
                    "sector": sector,
                    "mass": data["observed_mass_mev"],
                    "v": topologies[name]["volume"],
                    "D": topologies[name].get("determinant", 1),
                    "G": topologies[name].get("generation", 4)
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])
    df["lnD"] = np.log(df["D"])

    def fit_sector(sector, slope):
        sector_df = df[df["sector"] == sector].copy()
        best_mae = 100
        best_off = 0
        
        for off in np.linspace(-30, 30, 601):
            n = np.round(slope * sector_df["lnD"] + off)
            ln_m_pred = kappa * sector_df["v"] - 3.75 + n * delta_c 
            mae = np.mean(np.abs(ln_m_pred - sector_df["ln_m"]))
            if mae < best_mae:
                best_mae = mae
                best_off = off
        
        # Recalculate best predictions
        best_n = np.round(slope * sector_df["lnD"] + best_off)
        best_ln_m_pred = kappa * sector_df["v"] - 3.75 + best_n * delta_c
        err_pct = np.mean(np.abs(np.exp(best_ln_m_pred - sector_df["ln_m"]) - 1)) * 100
        return mae, best_off, err_pct

    print("Sector rules (C_glob = -3.75):")
    m1, o1, e1 = fit_sector("quarks", 4.5)
    print(f"  Quarks:  MAE {m1:.4f} ln ({e1:.4f}%), Offset {o1:.2f}")
    
    m2, o2, e2 = fit_sector("leptons", 10.0)
    print(f"  Leptons: MAE {m2:.4f} ln ({e2:.4f}%), Offset {o2:.2f}")
    
    m3, o3, e3 = fit_sector("bosons", 1.5)
    print(f"  Bosons:  MAE {m3:.4f} ln ({e3:.4f}%), Offset {o3:.2f}")

    total_mae_pct = (e1*6 + e2*3 + e3*3) / 12
    print(f"\nTotal MAE (%): {total_mae_pct:.4f}%")

if __name__ == "__main__":
    main()
