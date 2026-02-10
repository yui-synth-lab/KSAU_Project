import pandas as pd
import re

def find_boson_candidates():
    # Load link data
    # Use sep='|' and skip the second descriptive header line
    links = pd.read_csv('data/linkinfo_data_complete.csv', sep='|', skiprows=[1])
    
    # Ensure numeric volume and components
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    links['components'] = pd.to_numeric(links['components'], errors='coerce')
    
    # Target 1: Z Boson (V ~ 15.0)
    print("--- Searching for Z candidates (V ~ 15.0, 3 components) ---")
    z_cands = links[
        (links['volume'] >= 14.5) & 
        (links['volume'] <= 15.5) &
        (links['components'] == 3)
    ].sort_values('volume')
    
    for _, row in z_cands.iterrows():
        lm = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm)
        is_brunnian = all(n == '0' for n in nums) if nums else False
        
        # We are looking for something near 14.777 or 15.0
        if is_brunnian or abs(row['volume'] - 15.0) < 0.1:
            print(f"{row['name']:<12} | Vol: {row['volume']:.4f} | Brunnian: {is_brunnian}")

    # Target 2: Higgs candidates (V ~ 15.8)
    print("\n--- Searching for Higgs candidates (V ~ 15.8) ---")
    knots = pd.read_csv('data/knotinfo_data_complete.csv', sep='|', skiprows=[1])
    knots['volume'] = pd.to_numeric(knots['volume'], errors='coerce')
    
    # Higgs is a scalar, so we look for Amphicheiral knots (CS=0)
    h_knots = knots[
        (knots['volume'] >= 15.0) & 
        (knots['volume'] <= 16.5)
    ].sort_values('volume')
    
    for _, row in h_knots.iterrows():
         cs = pd.to_numeric(row.get('chern_simons_invariant', 0), errors='coerce')
         if abs(cs) < 1e-5:
             # Check name or other properties if needed
             print(f"{row['name']:<12} | Vol: {row['volume']:.4f} | CS: {cs:.6f}")

if __name__ == "__main__":
    find_boson_candidates()
