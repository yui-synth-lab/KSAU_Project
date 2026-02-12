import numpy as np
import pandas as pd
import ksau_config

def unified_lepton_law():
    print("="*80)
    print("KSAU v6.1: Lepton Mass Unification (Boundary + Bulk)")
    print("Objective: Solving the Phase Transition Gap (Electron-Muon)")
    print("="*80)

    # 1. Load Data via ksau_config (SSoT)
    topo = ksau_config.load_topology_assignments()
    coeffs = ksau_config.get_kappa_coeffs()
    
    leptons_names = ['Electron', 'Muon', 'Tau']
    
    # 2. Universal Law for Leptons (20*kappa)
    kappa = ksau_config.KAPPA
    slope = 20 * kappa  
    intercept = coeffs['lepton_intercept']
    
    print(f"Derived Constants:")
    print(f"  Lepton Slope (20*kappa): {slope:.4f}")
    print(f"  Lepton Intercept (ln(m_e)): {intercept:.4f}")
    print("-" * 40)

    # 3. Validation
    print(f"{'Particle':<12} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error %':<10}")
    for name in leptons_names:
        data = topo[name]
        obs = data['observed_mass']
        vol = data['volume']
        
        log_pred = intercept + slope * vol
        pred = np.exp(log_pred)
        err = (pred - obs) / obs * 100
        print(f"{name:<12} | {obs:<10.3f} | {pred:<10.3f} | {err:<10.2f}%")

if __name__ == "__main__":
    unified_lepton_law()
