import numpy as np
import os
import sys

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def verify_boson_scaling():
    print("="*60)
    print("KSAU v6.3: Boson Scaling Verification (Refactored)")
    print("="*60)
    
    # 1. Load Constants
    consts = utils_v61.load_constants()
    
    A_boson = consts['bosons']['scaling']['A']
    C_boson = consts['bosons']['scaling']['C']
    v_borr = consts['v_borromean']
    
    print(f"Boson Scaling Parameters: A = {A_boson:.5f}, C = {C_boson:.5f}")
    
    boson_data = consts['bosons']
    
    print("\n" + "="*50)
    print(f"{'Boson':<10} | {'Exp Mass (GeV)':<15} | {'Target V':<10} | {'Pred Mass':<12} | {'Error'}")
    print("-" * 65)
    
    for name in ['W', 'Z', 'Higgs']:
        b = boson_data[name]
        # v = b['volume_factor'] * v_borr  (wait, volume factor might be missing or in assignments)
        # Let's use volume from assignments directly if possible, or check if volume_factor exists
        if 'volume_factor' in b:
            v = b['volume_factor'] * v_borr
        else:
            # Fallback to topology assignments
            topo = utils_v61.load_assignments()
            v = topo[name]['volume']
            
        exp_m = b['observed_mass']
        
        ln_m = A_boson * v + C_boson
        pred_m = np.exp(ln_m)
        error = abs(pred_m - exp_m) / exp_m * 100
        print(f"{name:<10} | {exp_m/1000:<15.2f} | {v:<10.2f} | {pred_m/1000:<12.2f} | {error:.2f}%")

if __name__ == "__main__":
    verify_boson_scaling()