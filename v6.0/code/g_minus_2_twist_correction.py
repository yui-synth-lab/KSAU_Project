import pandas as pd
import numpy as np
import ksau_config
from pathlib import Path

def analyze_g2_twist_csv():
    # ---------------------------------------------------------
    # 1. Constants and Config
    # ---------------------------------------------------------
    ALPHA_GEOM = ksau_config.ALPHA_GEOM
    
    try:
        phys = ksau_config.load_physical_constants()
        g2 = phys['g_minus_2']
    except FileNotFoundError:
        print("Error loading config.")
        return
        
    # Load experimental data
    A_E_EXP = g2['a_e_exp']
    A_MU_EXP = g2['a_mu_exp']
    DELTA_MU_EXP = A_MU_EXP - A_E_EXP

    # Load knot data (for Muon)
    knot_csv = ksau_config.load_knotinfo_path()
    if not knot_csv.exists():
        print(f"Error: {knot_csv} not found.")
        return
    
    df_k = pd.read_csv(knot_csv, sep='|', skiprows=[1])
    
    # 2. Extract Muon Link (6_1)
    muon_row = df_k[df_k['name'] == '6_1'].iloc[0]
    vol_mu = float(muon_row['volume'])
    
    # 3. Calculation
    
    # Base Geometric Contribution (Volume Only)
    base_term = (ALPHA_GEOM / (2 * np.pi))**2 * vol_mu
    
    print("="*80)
    print("KSAU v6.0 Data-Driven: Muon g-2 Twist Torque Analysis")
    print("="*80)
    print(f"Muon Link                : 6_1 (Stevedore's Knot)")
    print(f"Hyperbolic Volume (Data) : {vol_mu:.5f}")
    print(f"Experimental Excess      : {DELTA_MU_EXP:.9e}")
    print(f"Base Volume Term         : {base_term:.9e}")
    print(f"Ratio (Exp / Base)       : {DELTA_MU_EXP / base_term:.4f}")
    print("-" * 80)
    
    # Twist Correction (v5.0 Theory: T = -1/6)
    twist_mu = -1.0 / 6.0
    torque_factor = 1.0 + abs(3 * twist_mu)
    pred_twist = base_term * torque_factor
    
    print("Twist Torque Hypothesis:")
    print(f"  Muon Twist T = {twist_mu:.4f}")
    print(f"  Torque Factor F = 1 + |3 * T| = {torque_factor:.2f}")
    print(f"  Predicted Excess (Base * F)   : {pred_twist:.9e}")
    print(f"  Error relative to Exp         : {(pred_twist - DELTA_MU_EXP)/DELTA_MU_EXP:.2%}")
    print("="*80)

if __name__ == "__main__":
    analyze_g2_twist_csv()
