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
    
    # 2. Candidates
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

    # 3. Unified Mass Model (20*kappa Law)
    consts = utils_v61.load_constants()
    kappa = consts.get('kappa', np.pi/24)
    slope_l = 20 * kappa
    intercept_l = np.log(consts['leptons']['Electron']['observed_mass'])
    
    # Observed Ratios from SSoT (Squared masses)
    dm21_exp = consts['neutrinos']['oscillation']['dm2_21_exp']
    dm31_exp = consts['neutrinos']['oscillation']['dm2_31_exp']
    target_ratio = (dm31_exp - dm21_exp) / dm21_exp
    
    print(f"\n[Testing Cusp-Corrected Unified Law]")
    print(f"Base Formula: ln(m) = {slope_l:.4f} * V + C")
    print(f"Cusp Correction: m = exp(slope*V + C) * (Aspect)^k")
    print(f"Target Ratio (dm32/dm21): {target_ratio:.2f}")
    
    best_k = 0
    best_err = float('inf')
    best_ratio = 0
    
    for k in np.linspace(-5, 5, 200):
        m = []
        for c in candidates:
            # Applying 20*kappa law with cusp correction
            mass = np.exp(slope_l * c['vol'] + intercept_l) * (c['aspect'] ** k)
            m.append(mass)
            
        dm21 = abs(m[1]**2 - m[0]**2)
        dm32 = abs(m[2]**2 - m[1]**2)
        
        if dm21 > 0:
            ratio = dm32 / dm21
            err = abs(ratio - target_ratio)
            if err < best_err:
                best_err = err
                best_k = k
                best_ratio = ratio
                
    print(f"\nBest Correction Power k: {best_k:.4f}")
    print(f"Resulting Ratio: {best_ratio:.4f} (Target: {target_ratio:.2f})")
    
    # Show Masses
    print("\nCorrected Masses (Relative):")
    m_final = []
    for c in candidates:
        mass = (c['vol'] ** 1.767) * (c['aspect'] ** best_k)
        m_final.append(mass)
        print(f"  {c['name']}: {mass:.4f} (Base: {c['vol']**1.767:.4f}, Correction: {c['aspect']**best_k:.4f})")
        
    print("\nPhysical Interpretation:")
    if abs(best_k) < 0.1:
        print("  Cusp shape has little effect.")
    elif best_k > 0:
        print("  Elongated cusps (High Aspect) increase mass.")
    else:
        print("  Elongated cusps decrease mass.")

if __name__ == "__main__":
    refine_pmns_cusp()
