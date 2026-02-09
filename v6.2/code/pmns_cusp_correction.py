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

    # 3. Refined Mass Model
    # Previous: m ~ V^1.77
    # Ratio 21 vs 33. We need to increase the gap between m2 and m3, or decrease m2-m1.
    # 4_1 (2.03), 7_2 (3.33), 8_9 (7.59).
    # Power law gives decent fit.
    
    # Hypothesis: Mass depends on "Geometry + Boundary correction".
    # m = V^lambda * (Aspect)^k ?
    # Let's test a correction factor.
    
    print("\n[Testing Cusp-Corrected Mass Model]")
    print("Formula: m = V^1.77 * (Aspect)^k")
    
    # We want Ratio = 33.
    # Current Ratio ~ 21.
    # We need to increase the effective "distance" of 8_9 or decrease 7_2.
    # 4_1 Aspect ~ ?
    # 7_2 Aspect ~ ?
    # 8_9 Aspect ~ ?
    
    # Let's perform a scan for k.
    
    best_k = 0
    best_err = 100
    best_ratio = 0
    
    for k in np.linspace(-2, 2, 100):
        m = []
        for c in candidates:
            mass = (c['vol'] ** 1.767) * (c['aspect'] ** k)
            m.append(mass)
            
        dm21 = abs(m[1]**2 - m[0]**2)
        dm32 = abs(m[2]**2 - m[1]**2)
        
        if dm21 > 0:
            ratio = dm32 / dm21
            err = abs(ratio - 33.0)
            if err < best_err:
                best_err = err
                best_k = k
                best_ratio = ratio
                
    print(f"\nBest Correction Power k: {best_k:.4f}")
    print(f"Resulting Ratio: {best_ratio:.4f} (Target: 33.0)")
    
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
