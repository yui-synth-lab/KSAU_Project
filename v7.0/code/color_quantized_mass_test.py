import numpy as np
from ksau_config_v7 import load_data, load_physical_constants

def run_color_quantized_test():
    print("="*80)
    print("KSAU v7.0: Color-Quantized Coupling Test (The Casimir Model)")
    print("Hypothesis: k_eff is quantized by Gauge Representation (Singlet/Triplet/Adjoint)")
    print("  Leptons : k = 24 (Singlet)")
    print("  Quarks  : k = 18 (Triplet, 24 / (4/3))")
    print("  Bosons  : k = 80 (Hierarchical Phase)")
    print("="*80)

    data = load_data()
    phys = load_physical_constants()
    
    # Sector Scaling Definitions
    # We use N_q=8 (E8) and N_l=20 (v6 baseline)
    sectors = {
        'leptons': {'k': 24.0, 'N': 20.0, 'particles': phys['leptons']},
        'quarks':  {'k': 18.0, 'N': 8.0,  'particles': phys['quarks']},
        'bosons':  {'k': 80.0, 'N': 20.0, 'particles': phys['bosons']}
    }
    
    results = {}
    total_errors = []

    for s_name, s_meta in sectors.items():
        print(f"\nSector: {s_name.upper()} (k={s_meta['k']}, N={s_meta['N']})")
        kappa = np.pi / s_meta['k']
        N = s_meta['N']
        slope = N * kappa
        
        # Optimize Intercept for this sector
        residuals = []
        for name in s_meta['particles']:
            if name == 'Electron' and s_name == 'leptons': continue
            if name == 'scaling': continue
            p = data[name]
            obs_ln_m = np.log(p['observed_mass'])
            
            twist = 0
            if s_name == 'quarks':
                twist = (2 - p['generation']) * ((-1)**p['components'])
            
            res = obs_ln_m - (slope * p['volume'] + kappa * twist)
            residuals.append(res)
            
        # Intercept anchor
        if s_name == 'leptons':
            C = np.log(0.511) # Anchor to Electron
        else:
            C = np.mean(residuals)
            
        print(f"  Optimized Intercept C: {C:.4f}")
        print(f"  {'Particle':<12} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Err %':<8}")
        print(f"  {'-'*45}")
        
        for name in s_meta['particles']:
            if name == 'scaling': continue
            p = data[name]
            obs = p['observed_mass']
            
            twist = 0
            if s_name == 'quarks':
                twist = (2 - p['generation']) * ((-1)**p['components'])
            
            pred_ln_m = slope * p['volume'] + C + kappa * twist
            pred = np.exp(pred_ln_m)
            err = abs(pred - obs) / obs * 100
            total_errors.append(err)
            print(f"  {name:<12} | {obs:<10.3f} | {pred:<10.3f} | {err:<8.2f}%")

    mae = np.mean(total_errors)
    print("\n" + "="*80)
    print(f"FINAL COLOR-QUANTIZED MAE: {mae:.4f}%")
    print("="*80)

if __name__ == "__main__":
    run_color_quantized_test()
