"""
MUON KNOT REASSIGNMENT INVESTIGATION

Search for better alternatives to 6_1 knot for Muon.

The formula predicts N = 5.93 for Muon's mass.
Current assignment: 6_1 (N=6) gives 17.31% error.

Hypothesis: A knot with Det=odd and N closer to 5.93 might exist.
"""

import pandas as pd
import numpy as np
import ksau_config
from pathlib import Path

def find_better_muon_knot():
    """
    Search for knots that better match Muon's requirements:
    1. Det = odd (lepton rule)
    2. Crossing number N close to 5.93
    """
    
    print("="*80)
    print("MUON KNOT REASSIGNMENT SEARCH")
    print("="*80)
    
    phys = ksau_config.load_physical_constants()
    coeffs = ksau_config.get_kappa_coeffs()
    
    muon_mass = phys['leptons']['Muon']['observed_mass']
    slope_l = (2/9) * phys['G_catalan']
    cl = coeffs['lepton_intercept']
    
    # Calculate optimal crossing number for Muon
    ln_m = np.log(muon_mass)
    target_n2 = (ln_m - cl) / slope_l
    target_n = np.sqrt(target_n2)
    
    print(f"\nMuon optimization target:")
    print(f"  Observed mass: {muon_mass:.2f} MeV")
    print(f"  Optimal crossing number: {target_n:.4f}")
    print(f"  Optimal N^2: {target_n2:.4f}")
    
    # Load knot database
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)
    df_k['crossing_number'] = pd.to_numeric(df_k['crossing_number'], errors='coerce').fillna(0)
    df_k['determinant'] = pd.to_numeric(df_k['determinant'], errors='coerce').fillna(0)
    
    # Filter: Det = odd (lepton rule)
    lepton_candidates = df_k[(df_k['determinant'] % 2 != 0) & 
                             (df_k['crossing_number'] > 0) &
                             (df_k['crossing_number'] <= 12)].copy()
    
    print(f"\nSearching {len(lepton_candidates)} knots with Det=odd and N <= 12...")
    
    # Calculate error for each candidate
    lepton_candidates['distance_to_target_n'] = (lepton_candidates['crossing_number'] - target_n).abs()
    lepton_candidates['predicted_ln_m'] = slope_l * (lepton_candidates['crossing_number'] ** 2) + cl
    lepton_candidates['predicted_m'] = np.exp(lepton_candidates['predicted_ln_m'])
    lepton_candidates['mass_error_percent'] = \
        (lepton_candidates['predicted_m'] - muon_mass).abs() / muon_mass * 100
    
    # Sort by mass prediction error
    best_candidates = lepton_candidates.nsmallest(20, 'mass_error_percent')
    
    print("\n" + "-"*80)
    print("Top 20 candidates (sorted by mass prediction error):")
    print("-"*80)
    print(f"{'Rank':<4} {'Name':<12} {'N':<4} {'Det':<5} {'Dist to 5.93':<12} {'Mass Error %':<15}")
    print("-"*80)
    
    for idx, (i, row) in enumerate(best_candidates.iterrows(), 1):
        print(f"{idx:<4} {row['name']:<12} {row['crossing_number']:<4.0f} {row['determinant']:<5.0f} "
              f"{row['distance_to_target_n']:<12.4f} {row['mass_error_percent']:<15.2f}")
    
    # Compare with current assignment (6_1)
    current_6_1 = df_k[df_k['name'] == '6_1']
    if not current_6_1.empty:
        current = current_6_1.iloc[0]
        current_pred_m = np.exp(slope_l * (6 ** 2) + cl)
        current_error = abs(current_pred_m - muon_mass) / muon_mass * 100
        
        print("\n" + "="*80)
        print("CURRENT ASSIGNMENT COMPARISON:")
        print("="*80)
        print(f"Current knot: 6_1")
        print(f"  N: 6")
        print(f"  Det: {int(current['determinant'])}")
        print(f"  Predicted mass: {current_pred_m:.3f} MeV")
        print(f"  Mass error: {current_error:.2f}%")
        
        best = best_candidates.iloc[0]
        print(f"\nBest alternative: {best['name']}")
        print(f"  N: {best['crossing_number']:.0f}")
        print(f"  Det: {int(best['determinant'])}")
        print(f"  Predicted mass: {best['predicted_m']:.3f} MeV")
        print(f"  Mass error: {best['mass_error_percent']:.2f}%")
        
        improvement = current_error - best['mass_error_percent']
        print(f"\nImprovement: {improvement:.2f} percentage points")
        
        if improvement > 0:
            print(f"✓ {best['name']} is BETTER than 6_1 by {improvement:.2f}%")
            print(f"  Reduction: {current_error:.2f}% -> {best['mass_error_percent']:.2f}%")
            
            # Check if new candidate satisfies rules
            if best['determinant'] % 2 != 0:
                print(f"✓ {best['name']} satisfies Det=odd rule")
            else:
                print(f"✗ WARNING: {best['name']} does NOT satisfy Det=odd rule!")
            
            return best
        else:
            print(f"✗ {best['name']} is NOT better than 6_1")
            print(f"  Both are poor fits, but 6_1 is still used due to simplicity (crossing number)")
            return None
    
    return None

if __name__ == "__main__":
    better_knot = find_better_muon_knot()
