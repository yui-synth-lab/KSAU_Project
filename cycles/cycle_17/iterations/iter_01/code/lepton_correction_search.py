import sys
import numpy as np
import pandas as pd
from pathlib import Path
import json

# AIRDP SSoT Loader setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def calculate_v_eff(v, n, det, a, b, c):
    return v + a * n + b * np.log(det) + c

def main():
    ssot = SSOT()
    consts = ssot.constants()
    kappa = consts['mathematical_constants']['kappa']
    v_eff_params = consts['effective_volume_model']
    a, b, c = v_eff_params['a'], v_eff_params['b'], v_eff_params['c']
    
    leptons = consts['particle_data']['leptons']
    quarks = consts['particle_data']['quarks']
    topo = ssot.topology_assignments()
    
    data = []
    for name, pdata in leptons.items():
        t = topo[name]
        data.append({
            "name": name, "type": "lepton", "v": t['volume'], "n": t['crossing_number'], 
            "det": t['determinant'], "obs_ln_m": np.log(pdata['observed_mass']), "gen": pdata['generation']
        })
    for name, pdata in quarks.items():
        t = topo[name]
        data.append({
            "name": name, "type": "quark", "v": t['volume'], "n": t['crossing_number'], 
            "det": t['determinant'], "obs_ln_m": np.log(pdata['observed_mass']), "gen": pdata['generation']
        })
    
    df = pd.DataFrame(data)
    df['v_eff_base'] = df.apply(lambda row: calculate_v_eff(row['v'], row['n'], row['det'], a, b, c), axis=1)
    
    # Correction for leptons only
    alpha = 2.3 # As per report
    df['v_eff_final'] = df['v_eff_base']
    df.loc[df['type'] == 'lepton', 'v_eff_final'] += alpha * np.log(df['det'])
    
    # Unified scaling K=20
    df['v_scaled'] = 20 * df['v_eff_final']
    
    res = df['obs_ln_m'] - kappa * df['v_scaled']
    intercept = np.mean(res)
    df['pred_ln_m'] = kappa * df['v_scaled'] + intercept
    df['error_pct'] = np.abs(np.exp(df['pred_ln_m']) - np.exp(df['obs_ln_m'])) / np.exp(df['obs_ln_m']) * 100
    
    unified_r2 = 1 - (np.sum((df['obs_ln_m'] - df['pred_ln_m'])**2) / np.sum((df['obs_ln_m'] - np.mean(df['obs_ln_m']))**2))
    print(f"Unified R2 (alpha={alpha}, K=20): {unified_r2:.6f}")
    
    # Lepton only R2
    ldf = df[df['type'] == 'lepton']
    l_res = ldf['obs_ln_m'] - kappa * ldf['v_scaled']
    l_intercept = np.mean(l_res)
    l_pred = kappa * ldf['v_scaled'] + l_intercept
    l_r2 = 1 - (np.sum((ldf['obs_ln_m'] - l_pred)**2) / np.sum((ldf['obs_ln_m'] - np.mean(ldf['obs_ln_m']))**2))
    print(f"Lepton R2: {l_r2:.6f}")
    
    print(df[['name', 'v_scaled', 'obs_ln_m', 'pred_ln_m', 'error_pct']])

if __name__ == "__main__":
    main()
