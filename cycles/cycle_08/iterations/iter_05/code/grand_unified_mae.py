import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path
from scipy.stats import linregress
from sklearn.metrics import r2_score

# SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_dir = project_root / "ssot"
sys.path.insert(0, str(ssot_dir))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    params = ssot.parameters()
    
    # Correction constant from v6.2
    dv_binding = 3.32 
    
    data = []
    # Quarks
    for q, p in params['quarks'].items():
        v = topo[q]['volume']
        c = topo[q]['components']
        # Apply Volume Defect for C=3 (Down-type)
        if c == 3:
            v_eff = v - dv_binding
        else:
            v_eff = v
        data.append({"name": q, "ln_m": np.log(p['observed_mass_mev']), "V": v_eff, "C": c, "sector": "Quark"})
    # Leptons
    for l, p in params['leptons'].items():
        data.append({"name": l, "ln_m": np.log(p['observed_mass_mev']), "V": topo[l]['volume'], "C": topo[l]['components'], "sector": "Lepton"})
    # Bosons
    for b, p in params['bosons'].items():
        if b in ['W', 'Z', 'Higgs']:
            data.append({"name": b, "ln_m": np.log(p['observed_mass_mev']), "V": topo[b]['volume'], "C": topo[b]['components'], "sector": "Boson"})

    # Calibration
    y_true, y_pred = [], []
    sector_results = {}
    
    for sector in ["Lepton", "Quark", "Boson"]:
        subset = [d for d in data if d['sector'] == sector]
        if sector == "Quark":
            # For quarks, we use sectoral slopes (Phase Viscosity)
            for c in [2, 3]:
                c_subset = [d for d in subset if d['C'] == c]
                X = np.array([d['V'] for d in c_subset])
                y = np.array([d['ln_m'] for d in c_subset])
                slope, intercept, _, _, _ = linregress(X, y)
                preds = slope * X + intercept
                y_true.extend(y)
                y_pred.extend(preds)
                sector_results[f"Quark_C{c}"] = {"mae": np.mean(np.abs(np.exp(preds) - np.exp(y)) / np.exp(y)) * 100}
        else:
            X = np.array([d['V'] for d in subset])
            y = np.array([d['ln_m'] for d in subset])
            slope, intercept, _, _, _ = linregress(X, y)
            preds = slope * X + intercept
            y_true.extend(y)
            y_pred.extend(preds)
            sector_results[sector] = {"mae": np.mean(np.abs(np.exp(preds) - np.exp(y)) / np.exp(y)) * 100}
            
    total_mae = np.mean(np.abs(np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)) * 100
    print(f"Total MAE (12 particles): {total_mae:.4f}%")
    print("Sector MAEs:", sector_results)

if __name__ == "__main__":
    main()
