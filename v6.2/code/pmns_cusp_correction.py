import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def refine_pmns_cusp():
    print("="*60)
    print("KSAU v6.2: PMNS Mass Refinement (Cusp Shape)")
    print("="*60)
    
    # 1. Load Data
    knots, _ = utils_v61.load_data()
    
    # 2. Candidates (Corrected 2026-02-13)
    # nu_1: 4_1 (Fully Amphicheiral, V=2.03)
    # nu_2: 7_2 (Reversible/Chiral, V=3.33) - drives large PMNS mixing
    # nu_3: 8_9 (Fully Amphicheiral, V=7.59)
    # Note: Phase 1 Report had typos (7_1, 8_19), but these have no hyperbolic volume data
    # The correct triplet is [4_1, 7_2, 8_9] as originally coded
    triplet_names = ['4_1', '7_2', '8_9']
    
    candidates = []
    print("Retrieving Cusp Data...")
    for name in triplet_names:
        row = knots[knots['name'] == name].iloc[0]
        
        # Extract Cusp Parameters
        # Try Maximum Cusp Volume
        try:
            cusp_vol = float(row['maximum_cusp_volume'])
        except:
            cusp_vol = 0.0
            
        vol = float(row['volume'])
        
        # Calculate Shape Factor
        # Ratio of Cusp Volume to Hyperbolic Volume
        if vol > 0 and cusp_vol > 0:
            aspect = cusp_vol / vol
        else:
            aspect = 1.0 # Default if missing
            
        candidates.append({
            'name': name,
            'vol': vol,
            'aspect': aspect,
            'cusp_vol': cusp_vol
        })
        print(f"  {name}: Vol={vol:.4f}, CuspVol={cusp_vol:.4f}, Ratio={aspect:.4f}")

    # 3. Unified Mass Model (v6.1/v6.2 Hybrid)
    consts = utils_v61.load_constants()
    pi_val = consts.get('pi', np.pi)
    
    # Scaling Constant from Paper II: lambda = 9pi/16
    lam = (9 * pi_val) / 16
    
    # Observed Ratios from SSoT (Squared masses)
    dm21_exp = consts['neutrinos']['oscillation']['dm2_21_exp']
    dm31_exp = consts['neutrinos']['oscillation']['dm2_31_exp']
    target_ratio = (dm31_exp - dm21_exp) / dm21_exp
    
    print(f"\n[Testing Cusp-Corrected Power Law]")
    print(f"Base Formula: m = V^{lam:.4f}")
    print(f"Cusp Correction: m = V^lambda * (Aspect)^k")
    print(f"Target Ratio (dm32/dm21): {target_ratio:.2f}")
    
    best_k = 0
    best_err = float('inf')
    best_ratio = 0
    
    for k in np.linspace(-2, 2, 1000):
        m = []
        for c in candidates:
            # Applying Power Law with cusp correction
            mass = (c['vol'] ** lam) * (c['aspect'] ** k)
            m.append(mass)
            
        dm21 = m[1]**2 - m[0]**2
        dm32 = m[2]**2 - m[1]**2
        
        if dm21 > 0:
            ratio = dm32 / dm21
            err = abs(ratio - target_ratio)
            if err < best_err:
                best_err = err
                best_k = k
                best_ratio = ratio
                
    print(f"\nBest Correction Power k: {best_k:.4f}")
    print(f"Resulting Ratio: {best_ratio:.4f} (Target: {target_ratio:.2f})")
    print(f"Residual Error: {best_err/target_ratio*100:.4f}%")

    # Show Masses
    print("\nCorrected Masses (Relative):")
    for c in candidates:
        mass = (c['vol'] ** lam) * (c['aspect'] ** best_k)
        base_mass = (c['vol'] ** lam)
        print(f"  {c['name']}: {mass:.4f} (Base: {base_mass:.4f}, Correction: {c['aspect']**best_k:.4f})")
        
    print("\nPhysical Interpretation:")
    if abs(best_k) < 0.1:
        print("  Cusp shape has little effect.")
    elif best_k > 0:
        print("  Elongated cusps (High Aspect) increase mass.")
    else:
        print("  Elongated cusps decrease mass.")

if __name__ == "__main__":
    refine_pmns_cusp()
