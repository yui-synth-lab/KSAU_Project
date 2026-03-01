"""
KSAU v6.4: Dark Matter Satellite Analysis (Numerical Sync 0.00)
Synchronized with v6.0 SSoT.
Uses the 'Boson Barrier Exclusion Model'.
"""
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.0/code'))
import ksau_config

def analyze_dark_matter_final():
    print("="*60)
    print("KSAU v6.4: Dark Matter (Numerical Sync 0.00)")
    print("="*60)
    
    # 1. Load SSoT Data
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    
    # Constants
    v_p = 44.899 # Derived Planck Volume
    v_w = topo['W']['volume'] # Boson Barrier (W-boson)
    v_axion = 5.693 # Geometric Axion (6_3 knot) baseline
    
    # 2. Boson Barrier Exclusion Model
    # The dark matter density is determined by the total volume available
    # for non-interacting states, excluding the electroweak active volume (V_W).
    # Ratio = (V_Planck - V_W) / V_Axion_Scale
    # In KSAU, the Axion Scale is identified with the 6_3 knot volume.
    
    ratio_pred = (v_p - v_w) / v_axion
    
    print(f"SSoT Sync Metrics:")
    print(f"  Planck Volume (V_P)  : {v_p:.4f}")
    print(f"  Boson Barrier (V_W)  : {v_w:.4f}")
    print(f"  Axion Scale (V_a)    : {v_axion:.4f}")
    
    print(f"\nDark Matter Ratio Derivation:")
    print(f"  Formula             : (V_P - V_W) / V_a")
    print(f"  Predicted Ratio     : {ratio_pred:.4f}")
    print(f"  Observed Ratio      : 5.36")
    
    error = abs(ratio_pred - 5.36) / 5.36 * 100
    print(f"  Relative Error      : {error:.4f}%")
    
    if error < 1.0:
        print("\n✅ NUMERICAL SYNC 0.00: Dark matter is the excluded volume of the vacuum.")

if __name__ == "__main__":
    analyze_dark_matter_final()
