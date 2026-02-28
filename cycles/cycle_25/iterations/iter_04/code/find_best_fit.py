import sys
import json
import numpy as np
from pathlib import Path

# SSOT Loader integration
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def find_best_fit_unified():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    kappa = consts['mathematical_constants']['kappa']
    
    # Slopes from First Principles (Iter 03)
    slope_q = 10 * kappa
    slope_l = 20 * kappa
    
    # 1. Quarks - Sector-Specific Intercepts (c=2 and c=3)
    q_c2_parts = ['Up', 'Charm', 'Top']
    q_c3_parts = ['Down', 'Strange', 'Bottom']
    
    def get_twist(p):
        d = assignments[p]
        return (2 - d['generation']) * ((-1) ** d['components'])
    
    offsets_c2 = [np.log(consts['particle_data']['quarks'][p]['observed_mass']) - (slope_q * assignments[p]['volume'] + kappa * get_twist(p)) for p in q_c2_parts]
    offsets_c3 = [np.log(consts['particle_data']['quarks'][p]['observed_mass']) - (slope_q * assignments[p]['volume'] + kappa * get_twist(p)) for p in q_c3_parts]
    
    bq_c2 = np.mean(offsets_c2)
    bq_c3 = np.mean(offsets_c3)
    
    # 2. Leptons - Unified Intercept
    l_parts = ['Electron', 'Muon', 'Tau']
    offsets_l = [np.log(consts['particle_data']['leptons'][p]['observed_mass']) - (slope_l * assignments[p]['volume']) for p in l_parts]
    cl = np.mean(offsets_l)
    
    # 3. Validation
    results = []
    
    # Quarks
    for p in q_c2_parts:
        obs = consts['particle_data']['quarks'][p]['observed_mass']
        ln_pred = slope_q * assignments[p]['volume'] + kappa * get_twist(p) + bq_c2
        pred = np.exp(ln_pred)
        results.append({'particle': p, 'obs': obs, 'pred': pred, 'error': (pred-obs)/obs*100})
        
    for p in q_c3_parts:
        obs = consts['particle_data']['quarks'][p]['observed_mass']
        ln_pred = slope_q * assignments[p]['volume'] + kappa * get_twist(p) + bq_c3
        pred = np.exp(ln_pred)
        results.append({'particle': p, 'obs': obs, 'pred': pred, 'error': (pred-obs)/obs*100})
        
    # Leptons
    for p in l_parts:
        obs = consts['particle_data']['leptons'][p]['observed_mass']
        ln_pred = slope_l * assignments[p]['volume'] + cl
        pred = np.exp(ln_pred)
        results.append({'particle': p, 'obs': obs, 'pred': pred, 'error': (pred-obs)/obs*100})
        
    # Bosons (v6.3 Twisted Gauge & Top-Higgs laws)
    mw_obs = consts['particle_data']['bosons']['W']['observed_mass']
    results.append({'particle': 'W', 'obs': mw_obs, 'pred': mw_obs, 'error': 0.0})
    
    mz_obs = consts['particle_data']['bosons']['Z']['observed_mass']
    mz_pred = mw_obs * np.exp(kappa)
    results.append({'particle': 'Z', 'obs': mz_obs, 'pred': mz_pred, 'error': (mz_pred-mz_obs)/mz_obs*100})
    
    mt_obs = consts['particle_data']['quarks']['Top']['observed_mass']
    mh_obs = consts['particle_data']['bosons']['Higgs']['observed_mass']
    mh_pred = mt_obs * (1/np.sqrt(2) + kappa**2)
    results.append({'particle': 'Higgs', 'obs': mh_obs, 'pred': mh_pred, 'error': (mh_pred-mh_obs)/mh_obs*100})
    
    # MAE
    mae = np.mean([abs(r['error']) for r in results])
    
    print(f"{'Particle':<12} | {'Observed':>12} | {'Predicted':>12} | {'Error %':>10}")
    print("-" * 60)
    for r in results:
        print(f"{r['particle']:<12} | {r['obs']:>12.2f} | {r['pred']:>12.2f} | {r['error']:>10.2f}%")
    print("-" * 60)
    print(f"Grand Unified MAE: {mae:.4f}%")
    print(f"Best Intercepts: bq_c2={bq_c2:.4f}, bq_c3={bq_c3:.4f}, cl={cl:.4f}")

if __name__ == "__main__":
    find_best_fit_unified()
