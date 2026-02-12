import numpy as np
import os
import sys

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def verify_boson_scaling():
    print("="*60)
    print("KSAU v6.3: Boson Scaling Verification (SSoT Aligned)")
    print("="*60)
    
    # 1. Load Data from SSoT
    consts = utils_v61.load_constants()
    assignments = utils_v61.load_assignments()
    
    # Using the Bulk Volume Law (10*kappa) for Gauge Bosons
    kappa = consts.get('kappa', np.pi/24)
    bq = -(7 + 7 * kappa)
    slope_bulk = 10 * kappa
    
    print(f"Applying Bulk Volume Law: ln(m) = {slope_bulk:.4f}*V + {bq:.4f}")
    
    print("\n" + "="*50)
    print(f"{'Boson':<10} | {'Exp Mass (GeV)':<15} | {'Volume':<10} | {'Pred Mass':<12} | {'Error'}")
    print("-" * 65)
    
    for name in ['W', 'Z', 'Higgs']:
        topo_data = assignments[name]
        v = topo_data['volume']
        exp_m = consts['bosons'][name]['observed_mass']
        
        ln_m = slope_bulk * v + bq
        pred_m = np.exp(ln_m)
        error = abs(pred_m - exp_m) / exp_m * 100
        print(f"{name:<10} | {exp_m/1000:<15.2f} | {v:<10.2f} | {pred_m/1000:<12.2f} | {error:.2f}%")

if __name__ == "__main__":
    verify_boson_scaling()