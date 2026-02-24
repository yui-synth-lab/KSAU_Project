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

    kappa = consts["mathematical_constants"]["kappa"]
    
    etas = {"quarks": 10.0, "leptons": 20.0, "bosons": 3.0}
    
    particles = []
    for sector, eta in etas.items():
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                particles.append({
                    "name": name,
                    "sector": sector,
                    "mass": data["observed_mass_mev"],
                    "v": topologies[name]["volume"],
                    "eta": eta
                })
    
    df = pd.DataFrame(particles)
    df["ln_m"] = np.log(df["mass"])
    df["kappa_v_eta"] = df["eta"] * kappa * df["v"]
    
    # ln(m) = eta*kappa*v + C_sector
    def fit_sector(sector):
        sector_df = df[df["sector"] == sector].copy()
        c = np.mean(sector_df["ln_m"] - sector_df["kappa_v_eta"])
        pred = sector_df["kappa_v_eta"] + c
        mae_pct = np.mean(np.abs(np.exp(pred - sector_df["ln_m"]) - 1)) * 100
        return c, mae_pct

    print("Sector FITS (Cycle 10 assignments):")
    c_q, e_q = fit_sector("quarks")
    print(f"  Quarks:  C = {c_q:.4f}, MAE = {e_q:.4f}%")
    
    c_l, e_l = fit_sector("leptons")
    print(f"  Leptons: C = {c_l:.4f}, MAE = {e_l:.4f}%")
    
    c_b, e_b = fit_sector("bosons")
    print(f"  Bosons:  C = {c_b:.4f}, MAE = {e_b:.4f}%")
    
    total_mae = (e_q*6 + e_l*3 + e_b*3) / 12
    print(f"\nTotal MAE: {total_mae:.4f}%")

if __name__ == "__main__":
    main()
