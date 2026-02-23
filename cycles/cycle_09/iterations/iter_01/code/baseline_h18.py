import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path
from sklearn.metrics import r2_score

# SSoT Loader Setup
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def parse_val(val, default=0.0):
    if pd.isnull(val): return default
    s = str(val).strip()
    if s == "" or s == "undefined" or s == "Not Hyperbolic": return default
    import re
    nums = re.findall(r'-?\d+', s)
    if nums: return float(nums[0])
    return default

def main():
    ssot = SSOT()
    topo = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()
    params = ssot.parameters()
    consts = ssot.constants()
    
    kappa = consts['mathematical_constants']['kappa']
    model_config = consts['phase_viscosity_model']
    alpha = model_config['alpha_twist']
    beta = model_config['beta_sig']
    
    data = []
    for sector_name in ['quarks', 'leptons', 'bosons']:
        for p_name, p_data in params[sector_name].items():
            if p_name not in topo: continue
            info = topo[p_name]
            topo_name = info['topology']
            
            # Find in CSV for signature
            if "L" in topo_name: 
                match = links_df[links_df['name'] == topo_name]
            else: 
                match = knots_df[knots_df['name'] == topo_name]
            
            sig = parse_val(match.iloc[0]['signature']) if not match.empty else 0.0
            twist = (2 - info.get('generation', 2)) * ((-1) ** info['components'])
            
            mass = p_data.get('observed_mass_mev') or p_data.get('observed_mass')
            if not mass: continue
            
            s_key = sector_name
            if sector_name == "quarks":
                s_key = f"quarks_c{info['components']}"
            
            data.append({
                "name": p_name,
                "ln_m_obs": np.log(mass),
                "m_obs": mass,
                "V": info['volume'],
                "C": info['components'],
                "K": info['crossing_number'], # Crossing Number
                "S": sig,
                "T": twist,
                "s_key": s_key
            })

    print(f"{'Particle':<12} | {'Obs Mass':<10} | {'Pred Mass':<10} | {'Error %':<8}")
    print("-" * 50)
    
    results = []
    y_true, y_pred = [], []
    for d in data:
        cfg = model_config['sectors'][d['s_key']]
        eta = cfg['eta']
        B = cfg['intercept']
        
        # ln_m_pred = eta * kappa * (V + alpha*T + beta*S) + B
        ln_m_pred = eta * kappa * (d['V'] + alpha * d['T'] + beta * d['S']) + B
        m_pred = np.exp(ln_m_pred)
        
        err = abs(m_pred - d['m_obs']) / d['m_obs'] * 100
        print(f"{d['name']:<12} | {d['m_obs']:<10.3f} | {m_pred:<10.3f} | {err:<8.2f}%")
        
        y_true.append(d['ln_m_obs'])
        y_pred.append(ln_m_pred)
        results.append(err)
        
    print("-" * 50)
    print(f"Total MAE: {np.mean(results):.2f}%")
    print(f"Total R2:  {r2_score(y_true, y_pred):.6f}")

if __name__ == "__main__":
    main()
