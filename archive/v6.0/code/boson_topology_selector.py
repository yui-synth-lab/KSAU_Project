"""
Algorithmic Boson Topology Selector for KSAU v6.0

This module replaces the hard-coded boson assignments in topology_official_selector.py
with a principle-driven selection algorithm.

Physical Principles:
1. Gauge bosons (W, Z) emerge from 3-component Brunnian links (topological gauge invariance)
2. Higgs emerges from 3-component non-Brunnian link (symmetry-breaking sector)
3. Mass ordering: W < Z < Higgs (observed hierarchy)
4. Volume scaling law: ln(m) = A * V + C (same form as fermions)

Selection Strategy:
- Search 11-crossing links (empirically optimal crossing number)
- Filter by component count (C=3 for weak sector)
- Identify Brunnian links (W, Z candidates)
- Select by mass-volume proximity
"""

import numpy as np
import pandas as pd
import ksau_config
from pathlib import Path
import json

# ============================================================================
# BRUNNIAN LINK DETECTION
# ============================================================================

def is_brunnian_link(row):
    """
    Determine if a link is Brunnian (removing any component makes it trivial).

    Current implementation: Check if name contains known Brunnian families.
    TODO: Implement rigorous check via Alexander polynomial or component deletion.
    """
    name = str(row['name'])

    # Known Brunnian families from LinkInfo
    brunnian_patterns = [
        'L6a4',    # Borromean rings
        'L8n',     # Some 8-crossing Brunnian links
        'L9n',     # Some 9-crossing Brunnian links
        'L11n',    # Some 11-crossing Brunnian links
    ]

    # Heuristic: Name contains Brunnian pattern
    for pattern in brunnian_patterns:
        if name.startswith(pattern):
            return True

    return False

# ============================================================================
# BOSON SELECTION ENGINE
# ============================================================================

def select_boson_topologies(phys, df_links, target_crossing=11, verbose=True):
    """
    Select W, Z, Higgs topologies from LinkInfo database.

    Args:
        phys (dict): Physical constants from ksau_config
        df_links (DataFrame): LinkInfo database
        target_crossing (int): Crossing number to search (default 11)
        verbose (bool): Print selection process

    Returns:
        dict: {boson_name: topology_data}
    """
    if verbose:
        print("="*80)
        print("KSAU v6.0: Algorithmic Boson Topology Selection")
        print("="*80)

    # Extract observed masses
    bosons_meta = phys['bosons']
    m_W = bosons_meta['W']['observed_mass']  # MeV
    m_Z = bosons_meta['Z']['observed_mass']
    m_H = bosons_meta['Higgs']['observed_mass']

    # Get boson scaling law from config (or fit from data)
    # For now, use empirical fit: ln(m) = A*V + C
    # We'll fit A and C from the 3 boson masses

    # Filter candidates: 3-component links at target crossing
    candidates = df_links[
        (df_links['components'] == 3) &
        (df_links['crossing_number'] == target_crossing) &
        (df_links['volume'] > 0)
    ].copy()

    if len(candidates) == 0:
        raise ValueError(f"No 3-component links found at crossing {target_crossing}")

    if verbose:
        print(f"\nSearching {len(candidates)} 3-component links at N={target_crossing}...")

    # Annotate Brunnian property
    candidates['is_brunnian'] = candidates.apply(is_brunnian_link, axis=1)

    if verbose:
        n_brun = candidates['is_brunnian'].sum()
        print(f"  Brunnian candidates: {n_brun}")
        print(f"  Non-Brunnian candidates: {len(candidates) - n_brun}")

    # Split into Brunnian (W, Z) and Non-Brunnian (Higgs) pools
    brunnian = candidates[candidates['is_brunnian'] == True].copy()
    non_brunnian = candidates[candidates['is_brunnian'] == False].copy()

    if len(brunnian) < 2:
        raise ValueError("Insufficient Brunnian candidates for W and Z")
    if len(non_brunnian) < 1:
        raise ValueError("No non-Brunnian candidates for Higgs")

    # Strategy: Minimize MAE to observed masses under volume law
    # We iterate over candidate triples (W_cand, Z_cand, H_cand) and find best fit

    best_mae = float('inf')
    best_assignment = None

    # Limit search to top candidates by volume proximity
    brunnian_sorted = brunnian.sort_values('volume')
    non_brunnian_sorted = non_brunnian.sort_values('volume')

    top_n = min(10, len(brunnian_sorted), len(non_brunnian_sorted))

    if verbose:
        print(f"\nEvaluating {top_n}² × {top_n} = {top_n**3} candidate combinations...")

    for i, w_row in brunnian_sorted.head(top_n).iterrows():
        for j, z_row in brunnian_sorted.head(top_n).iterrows():
            if w_row['name'] == z_row['name']:
                continue  # W and Z must be distinct

            for k, h_row in non_brunnian_sorted.head(top_n).iterrows():
                # Extract volumes
                v_w, v_z, v_h = w_row['volume'], z_row['volume'], h_row['volume']

                # Enforce mass ordering via volume ordering (since m ∝ exp(A*V))
                # Required: V_W < V_Z < V_H (since m_W < m_Z < m_H)
                if not (v_w < v_z < v_h):
                    continue

                # Fit slope and intercept: ln(m) = A*V + C
                volumes = np.array([v_w, v_z, v_h])
                ln_masses = np.log([m_W, m_Z, m_H])

                # Linear regression
                A = np.corrcoef(volumes, ln_masses)[0, 1] * np.std(ln_masses) / np.std(volumes)
                C = np.mean(ln_masses) - A * np.mean(volumes)

                # Predict masses
                pred_masses = np.exp(A * volumes + C)
                obs_masses = np.array([m_W, m_Z, m_H])

                # Calculate MAE
                mae = np.mean(np.abs((pred_masses - obs_masses) / obs_masses * 100))

                if mae < best_mae:
                    best_mae = mae
                    best_assignment = {
                        'W': w_row,
                        'Z': z_row,
                        'Higgs': h_row,
                        'A': A,
                        'C': C,
                        'mae': mae
                    }

    if best_assignment is None:
        raise ValueError("No valid boson assignment found")

    # Format results
    results = {}
    for b_name in ['W', 'Z', 'Higgs']:
        row = best_assignment[b_name]
        results[b_name] = {
            'topology': row['name'],
            'volume': float(row['volume']),
            'crossing_number': int(row['crossing_number']),
            'components': int(row['components']),
            'determinant': int(row['determinant']),
            'is_brunnian': (b_name != 'Higgs')
        }

    if verbose:
        print(f"\n{'='*80}")
        print(f"BEST ASSIGNMENT (MAE: {best_mae:.2f}%)")
        print(f"{'='*80}")
        print(f"{'Boson':<10} | {'Topology':<15} | {'Volume':<8} | {'Obs (MeV)':<12} | {'Pred (MeV)':<12}")
        print("-" * 80)

        A, C = best_assignment['A'], best_assignment['C']
        for b_name in ['W', 'Z', 'Higgs']:
            row = best_assignment[b_name]
            obs = phys['bosons'][b_name]['observed_mass']
            pred = np.exp(A * row['volume'] + C)
            print(f"{b_name:<10} | {row['name']:<15} | {row['volume']:<8.2f} | {obs:<12.0f} | {pred:<12.0f}")

        print(f"\nScaling Law: ln(m) = {A:.4f} * V + {C:.4f}")
        print(f"Comparison to physical_constants.json:")
        stored_A = phys['bosons']['scaling']['A']
        stored_C = phys['bosons']['scaling']['C']
        print(f"  Stored: A={stored_A:.4f}, C={stored_C:.4f}")
        print(f"  Fitted: A={A:.4f}, C={C:.4f}")

    return results, {'A': A, 'C': C, 'mae': best_mae}

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Load data
    phys = ksau_config.load_physical_constants()
    df_links = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])

    # Clean data
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_links[c] = pd.to_numeric(df_links[c], errors='coerce').fillna(0)

    # Run selection
    boson_topologies, scaling_params = select_boson_topologies(phys, df_links, target_crossing=11)

    # Save results
    output_path = Path(__file__).parent.parent / 'data' / 'boson_assignments_algorithmic.json'
    with open(output_path, 'w') as f:
        output = {
            'topologies': boson_topologies,
            'scaling': scaling_params
        }
        json.dump(output, f, indent=2)

    print(f"\n✓ Algorithmic selection complete. Saved to: {output_path}")
