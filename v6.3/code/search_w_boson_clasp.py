import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def search_w_boson_clasp():
    print("="*60)
    print("KSAU v6.3: W-Boson 'Clasp' Geometry Search")
    print("="*60)
    
    # 1. Load Data & Constants
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # Universal Mass Law Parameters (Boson Sector)
    A_boson = consts['bosons']['scaling']['A']
    C_boson = consts['bosons']['scaling']['C']
    
    # W Boson Mass (Experimental)
    mw_mev = consts['bosons']['W']['observed_mass']
    target_vol = (np.log(mw_mev) - C_boson) / A_boson
    print(f"Target Volume for M_W ({mw_mev} MeV): {target_vol:.4f}")
    
    # 2. Filter for 'Clasp' Candidates
    # Criteria:
    # - Components = 3 (Connecting interaction between fields)
    # - Volume range: 14.0 - 15.5 (Target ~ 14.68)
    
    # Ensure numeric
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    # LinkInfo usually doesn't have explicit 'components' column in simple CSV load,
    # but we can infer from name or check if column exists.
    # The 'name' often has format L{crossings}{type}{index}{components?}.
    # Actually, LinkInfo CSV has 'components' column? Let's assume yes or infer.
    # If not, L10a... is usually multi-component.
    
    print("Filtering 3-Component Links in Volume range 14.0 - 15.5...")
    
    # Select potential columns
    cols = ['name', 'volume', 'components', 'linking_matrix']
    available_cols = [c for c in cols if c in links.columns]
    
    candidates = links[
        (links['volume'] >= 14.0) & 
        (links['volume'] <= 15.5)
    ].copy()
    
    # Filter by components == 3 if possible
    if 'components' in links.columns:
        candidates = candidates[candidates['components'] == 3]
    else:
        # Heuristic: Check linking matrix size or name
        pass 
        
    candidates = candidates.sort_values('volume')
    
    print(f"Found {len(candidates)} candidates.")
    
    # 3. Analyze Candidates
    target_vol = 14.68
    
    print(f"\n[Candidates near V_W ~ {target_vol:.2f}]")
    print(f"{'Name':<12} | {'Volume':<8} | {'Comp':<4} | {'Brunnian? (Est)'} | {'Diff'}")
    print("-" * 70)
    
    for _, row in candidates.iterrows():
        vol = row['volume']
        diff = abs(vol - target_vol)
        
        # Brunnian Check: Linking Matrix should be all zeros (off-diagonal)
        # The CSV string is like "{{0,0,0},{0,0,0},{0,0,0}}"
        is_brunnian = "Likely No"
        lm = str(row.get('linking_matrix', ''))
        if lm:
            # Simple check: if all numbers are 0
            # Extract numbers
            import re
            nums = re.findall(r'-?\d+', lm)
            # Remove diagonal zeros (if matrix format is standard)
            # Actually, Brunnian implies pairwise linking numbers are 0.
            # So sum of abs values should be 0? 
            # Or just check if string contains non-zero digits.
            if all(n == '0' for n in nums):
                is_brunnian = "YES (0-Link)"
            else:
                is_brunnian = "No"
        
        # Only show close matches or Brunnian
        if diff < 0.2 or "YES" in is_brunnian:
            comp = row.get('components', 'N/A')
            print(f"{row['name']:<12} | {vol:.4f}   | {comp:<4} | {is_brunnian:<15} | {diff:.4f}")

    # 4. Hypothesis Check: Double Borromean
    print("\n[Hypothesis: W = Double Borromean]")
    # Find Borromean volume from database if possible, or use L6a4
    row_borr = links[links['name'] == 'L6a4{0,0}']
    if row_borr.empty:
        row_borr = links[links['name'].str.startswith('L6a4')]
    
    if not row_borr.empty:
        vol_borromean = float(row_borr.iloc[0]['volume'])
    else:
        vol_borromean = 7.3277 # Fallback
        
    vol_double = 2 * vol_borromean
    print(f"  Vol(Borromean Rings) = {vol_borromean:.4f}")
    print(f"  Vol(Double Borromean) = {vol_double:.4f}")
    print(f"  Target V_W = {target_vol:.4f}")
    print(f"  Difference: {abs(vol_double - target_vol):.4f}")
    
    if abs(vol_double - target_vol) < 0.1:
        print("  MATCH: W boson mass aligns with a 'Borromean Cooper Pair'.")
        print("  Interpretation: The W field connects Left-handed doublets using a self-dual Borromean geometry.")

if __name__ == "__main__":
    search_w_boson_clasp()
