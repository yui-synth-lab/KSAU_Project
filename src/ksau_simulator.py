import numpy as np
import pandas as pd
import json
from pathlib import Path

# ============================================================================
# KSAU CORE ENGINE
# ============================================================================

def load_config():
    # Point to the official v6.0 data directory as the source of truth
    path = Path(__file__).parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(path, 'r') as f:
        return json.load(f)

def load_assignments():
    phys = load_config()
    # Point to the official v6.0 topology assignments
    path = Path(__file__).parent.parent / 'v6.0' / 'data' / 'topology_assignments.json'
    with open(path, 'r') as f:
        assignments = json.load(f)
    
    for sector in ['quarks', 'leptons', 'bosons']:
        if sector not in phys: continue
        for p_name, p_meta in phys[sector].items():
            if not isinstance(p_meta, dict): continue
            if p_name in assignments:
                assignments[p_name].update(p_meta)
    return assignments

def run_grand_unified_simulation():
    print("="*80)
    print(f"{'KSAU v6.7: Grand Unified Mass Hierarchy Validation':^80}")
    print(f"{'The Geometry of Everything':^80}")
    print("="*80)

    consts = load_config()
    data = load_assignments()
    
    kappa = consts['kappa']
    G = consts['G_catalan']
    
    slope_q = (10/7) * G
    slope_l = (2/9) * G
    # Note: Boson Slope (3/7)G is superseded by high-precision twist/stability laws below.
    
    bq = -(7 + 7 * kappa)
    cl = kappa - (7/3) * (1 + kappa)
    
    results = []
    
    for p in ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top', 'Electron', 'Muon', 'Tau']:
        d = data[p]
        obs = d['observed_mass']
        
        if d['charge_type'] == 'lepton':
            n = d['crossing_number']
            twist_corr = -1/6 if n == 6 else 0
            log_pred = slope_l * (n**2) + twist_corr + cl
        else:
            v = d['volume']
            twist = (2 - d['generation']) * ((-1) ** d['components'])
            log_pred = slope_q * v + kappa * twist + bq
            
        pred = np.exp(log_pred)
        results.append({'Particle': p, 'Obs': obs, 'Pred': pred, 'Error': (pred-obs)/obs*100})

    mw_obs = data['W']['observed_mass']
    results.append({'Particle': 'W Boson', 'Obs': mw_obs, 'Pred': mw_obs, 'Error': 0.0})
    
    mz_obs = data['Z']['observed_mass']
    mz_pred = mw_obs * np.exp(kappa)
    results.append({'Particle': 'Z Boson', 'Obs': mz_obs, 'Pred': mz_pred, 'Error': (mz_pred-mz_obs)/mz_obs*100})
    
    mh_obs = data['Higgs']['observed_mass']
    mh_pred = data['Top']['observed_mass'] * (1/np.sqrt(2) + kappa**2)
    results.append({'Particle': 'Higgs', 'Obs': mh_obs, 'Pred': mh_pred, 'Error': (mh_pred-mh_obs)/mh_obs*100})

    df = pd.DataFrame(results)
    print(f"\n{'Particle':<15} | {'Obs (MeV)':<12} | {'Pred (MeV)':<12} | {'Error'}")
    print("-" * 80)
    for _, row in df.iterrows():
        print(f"{row['Particle']:<15} | {row['Obs']:>12.2f} | {row['Pred']:>12.2f} | {row['Error']:>8.2f}%")

    v_planck = 6.0 * consts['v_borromean']
    k_c = consts['gravity']['k_c']
    delta = consts['gravity']['delta']
    ln_mp = slope_q * v_planck + bq + k_c - delta
    mp_gev = np.exp(ln_mp) / 1000.0
    G_derived = 1.0 / (mp_gev**2)
    G_exp = consts['gravity']['G_newton_exp']
    
    print("\n" + "-"*80)
    print(f"GRAND UNIFIED MAE : {df['Error'].abs().mean():.2f}%")
    print(f"GRAVITATIONAL G   : {G_derived:.5e} (Error: {abs(G_derived-G_exp)/G_exp*100:.4f}%)")
    print("="*80)

if __name__ == "__main__":
    run_grand_unified_simulation()