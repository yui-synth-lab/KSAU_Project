import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def search_root_link():
    print("="*60)
    print("KSAU v6.2 Phase 3: Grand Unification (Root Link Search)")
    print("="*60)
    
    # 1. Load Data
    _, links = utils_v61.load_data()
    
    # 2. Target Volume for "Root Link"
    # Load quark volumes from SSoT (v6.0 final topology assignments)
    # Updated 2026-02-13: Use SSoT instead of hardcoded values
    assignments = utils_v61.load_assignments()

    # Extract volumes
    v_up = assignments['Up']['volume']
    v_down = assignments['Down']['volume']
    v_strange = assignments['Strange']['volume']
    v_charm = assignments['Charm']['volume']
    v_bottom = assignments['Bottom']['volume']
    v_top = assignments['Top']['volume']

    print(f"\nQuark Volumes (from v6.0 SSoT):")
    print(f"  Up: {v_up:.4f}, Down: {v_down:.4f}")
    print(f"  Charm: {v_charm:.4f}, Strange: {v_strange:.4f}")
    print(f"  Top: {v_top:.4f}, Bottom: {v_bottom:.4f}")

    # GUT Scale is usually high energy.
    # But geometrically, unification might mean "Decomposition".
    # A single complex link that decomposes into quarks + leptons.

    # Generational Root Links (Sum of quark pairs)
    gen1_root = v_up + v_down
    gen2_root = v_charm + v_strange
    gen3_root = v_top + v_bottom

    print(f"\nGenerational Root Volumes:")
    print(f"  Gen 1: Up+Down = {gen1_root:.4f}")
    print(f"  Gen 2: Charm+Strange = {gen2_root:.4f}")
    print(f"  Gen 3: Top+Bottom = {gen3_root:.4f}")

    targets = {
        "Gen1_Root": gen1_root,
        "Gen2_Root": gen2_root,
        "Gen3_Root": gen3_root
    }
    
    print("Searching for Generational Root Links...")
    
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    
    for gen, target in targets.items():
        print(f"\n[Target: {gen} (Vol ~ {target:.2f})]")
        
        candidates = links[
            (links['volume'] >= target - 0.5) & 
            (links['volume'] <= target + 0.5)
        ].sort_values('volume')
        
        if candidates.empty:
            print("  No direct matches found.")
        else:
            # Show top 5 matches
            print(f"  {'Name':<12} | {'Volume':<8} | {'Components'}")
            for _, row in candidates.head(5).iterrows():
                # Extract component count if available, else infer from name (L8a6 = ?)
                # LinkInfo usually has 'components' column? No, we didn't load it strictly.
                # In previous steps we saw 'components' in quarks dict manually.
                # Let's check columns.
                comp = row['components'] if 'components' in row else "?"
                print(f"  {row['name']:<12} | {row['volume']:.4f}   | {comp}")

    # 3. GUT Monopole Candidate
    # A single knot with huge volume? Or a specific non-hyperbolic geometry?
    # 't Hooft-Polyakov Monopole ~ topological defect.
    # In KSAU, maybe it's the "Unknot" at high energy? No.
    
    # Let's look for "L10n113" (famous for volume ~ ??) or similar large links.
    # The database goes up to 14 crossings or so?
    # Largest volume in database?
    
    max_vol_row = links.loc[links['volume'].idxmax()]
    print(f"\n[Largest Link in Database (GUT Candidate?)]")
    print(f"  Name: {max_vol_row['name']}")
    print(f"  Volume: {max_vol_row['volume']}")
    print(f"  Components: {max_vol_row.get('components', 'N/A')}")
    
    # 4. Prediction for 6_3 Axion
    # Calculate mass of 6_3 knot (Amphicheiral)
    print("\n[Prediction: 'Second Axion' (6_3 Knot)]")
    # Need to find 6_3 in Knots data (not Links)
    knots, _ = utils_v61.load_data()
    row_63 = knots[knots['name'] == '6_3']
    if not row_63.empty:
        vol_63 = float(row_63.iloc[0]['volume'])
        
        # Mass Formula from config
        consts = utils_v61.load_constants()
        kappa = consts['kappa']
        slope = 10 * kappa
        intercept = -(7 + 7 * kappa)
        mass_mev = np.exp(slope * vol_63 + intercept)
        
        print(f"  Knot: 6_3")
        print(f"  Volume: {vol_63:.4f}")
        print(f"  Predicted Mass: {mass_mev:.4f} MeV")
        print(f"  Properties: Amphicheiral (CS=0). Heavier than 4_1.")
        print("  This particle would be a 'Heavy Axion' or 'Dark Sector Scalar'.")
    else:
        print("  Error: 6_3 not found in database.")

if __name__ == "__main__":
    search_root_link()
