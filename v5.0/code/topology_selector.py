"""
KSAU v5.0: Automated Topology Assignment System

This script implements the deterministic selection protocol described in
Supplementary Material Appendix C. It reads particle data from mass_data.csv 
and knot/link databases, applies the three geometric selection rules, 
and outputs topology assignments.

Principle: "Data drives code, not code drives data."

Usage:
    python topology_selector.py

Output:
    ../data/topology_assignments.json - Selected topologies for all 9 fermions
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict


# ============================================================================
# CONSTANTS
# ============================================================================

KAPPA = np.pi / 24  # Master constant from Chern-Simons theory


# ============================================================================
# DATABASE LOADING
# ============================================================================

def load_databases(base_path: Path = None):
    """Load KnotInfo, LinkInfo, and particle data."""
    if base_path is None:
        # Auto-detect base path (two levels up from this script)
        base_path = Path(__file__).parent.parent.parent

    # Paths
    link_path = base_path / 'data' / 'linkinfo_data_complete.csv'
    knot_path = base_path / 'data' / 'knotinfo_data_complete.csv'

    print(f"Loading databases from: {base_path / 'data'}")

    # Load LinkInfo (skip second header row)
    links = pd.read_csv(link_path, sep='|', low_memory=False)
    links = links[links['name'] != 'Name']  # Remove duplicate header
    links['crossing_number'] = pd.to_numeric(links['crossing_number'], errors='coerce')
    links['components'] = pd.to_numeric(links['components'], errors='coerce')
    links['determinant'] = pd.to_numeric(links['determinant'], errors='coerce')
    links['volume'] = pd.to_numeric(links['volume'], errors='coerce')
    links = links.dropna(subset=['crossing_number', 'components', 'determinant', 'volume'])

    # Load KnotInfo (skip second header row)
    knots = pd.read_csv(knot_path, sep='|', low_memory=False)
    knots = knots[knots['name'] != 'Name']
    knots['crossing_number'] = pd.to_numeric(knots['crossing_number'], errors='coerce')
    knots['determinant'] = pd.to_numeric(knots['determinant'], errors='coerce')
    knots['volume'] = pd.to_numeric(knots['volume'], errors='coerce').fillna(0.0)
    knots['components'] = 1  # All knots have C=1
    knots = knots.dropna(subset=['crossing_number', 'determinant'])

    # Load Particle data from mass_data.csv
    mass_csv_path = base_path / 'v5.0' / 'data' / 'mass_data.csv'
    mass_df = pd.read_csv(mass_csv_path)
    
    particles = {}
    for _, row in mass_df.iterrows():
        name = row['particle']
        particles[name] = {
            'mass': float(row['mass']),
            'gen': int(row['generation']),
            'type': row['charge_type'],
            'group': row['group'].lower() # 'quark' or 'lepton'
        }

    print(f"  Links: {len(links)} entries")
    print(f"  Knots: {len(knots)} entries")
    print()

    return links, knots, particles


# ============================================================================
# SELECTION RULES
# ============================================================================

def apply_selection_rules(particle_name: str, particle_data: Dict,
                         links: pd.DataFrame, knots: pd.DataFrame) -> pd.DataFrame:
    """
    Apply KSAU v5.0 selection rules to filter candidate topologies.

    Rule 1: Confinement-Component Correspondence
    Rule 2: Charge-Determinant Law
    Rule 3: Geometric Mass Scaling (minimize crossing, optimize volume)
    """
    gen = particle_data['gen']
    ptype = particle_data['type']
    group = particle_data['group']

    # ========== LEPTONS (C=1) ==========
    if group == 'lepton':
        pool = knots.copy()

        # Rule 2: Odd determinant
        pool = pool[pool['determinant'] % 2 == 1]

        # Rule 3: Sort by crossing number (minimize complexity)
        pool = pool.sort_values(['crossing_number', 'volume']).reset_index(drop=True)

        return pool

    # ========== QUARKS (C>=2) ==========
    else:
        # Rule 1: Component assignment
        # Empirical pattern: up-type → C=2, down-type → C=3
        target_c = 2 if ptype == 'up-type' else 3
        pool = links[links['components'] == target_c].copy()

        # Rule 2: Determinant filter
        if ptype == 'down-type':
            # Binary Determinant Rule: Det = 2^k, k = gen + 3
            target_det = 2 ** (gen + 3)  # Gen 1→16, Gen 2→32, Gen 3→64
            pool = pool[pool['determinant'] == target_det]
        else:
            # Up-type: Even determinant (non-binary)
            pool = pool[pool['determinant'] % 2 == 0]

        # Rule 3: Sort by complexity
        pool = pool.sort_values(['crossing_number', 'volume']).reset_index(drop=True)

        return pool


# ============================================================================
# MASS-GUIDED SELECTION
# ============================================================================

def select_best_fit(pool: pd.DataFrame, target_mass: float, gen: int,
                   ptype: str, group: str) -> pd.DataFrame:
    """
    From the filtered pool, select the topology that best fits the observed mass.

    Strategy:
    - For leptons: Use N² scaling law
    - For quarks: Use volume scaling law with Twist correction
    """

    if len(pool) == 0:
        raise ValueError("No candidates in pool")

    # ========== LEPTON SELECTION ==========
    if group == 'lepton':
        # Lepton mass formula: ln(m) = (14/9)κ · N² - (1/6)·I_twist + C_l
        # Calibrate C_l using electron (N=3, no twist)
        N_electron = 3
        m_electron = 0.511
        gamma_l = (14/9) * KAPPA
        C_l = np.log(m_electron) - gamma_l * (N_electron ** 2)

        # Predict mass for each candidate
        pool = pool.copy()
        N_values = pool['crossing_number'].values

        # Twist correction: Muon (6_1) is a twist knot
        # Simple heuristic: N=6 with odd Det=9 → twist knot
        is_twist = (N_values == 6) & (pool['determinant'] == 9)
        twist_correction = np.where(is_twist, -1/6, 0.0)

        pool['pred_log_m'] = gamma_l * (N_values ** 2) + twist_correction + C_l
        pool['pred_m'] = np.exp(pool['pred_log_m'])
        pool['error'] = np.abs(pool['pred_m'] - target_mass) / target_mass

        # Select minimum error
        best = pool.loc[pool['error'].idxmin()]
        return best

    # ========== QUARK SELECTION ==========
    else:
        # Quark mass formula: ln(m) = 10κ·V + κ·T - (7 + 7κ)
        # Twist: T = (2 - Gen) × (-1)^C
        pool = pool.copy()
        C_values = pool['components'].values
        V_values = pool['volume'].values

        twist = (2 - gen) * ((-1) ** C_values)
        B_q = -(7 + 7 * KAPPA)

        pool['pred_log_m'] = 10 * KAPPA * V_values + KAPPA * twist + B_q
        pool['pred_m'] = np.exp(pool['pred_log_m'])
        pool['error'] = np.abs(pool['pred_m'] - target_mass) / target_mass

        # Select minimum error
        best = pool.loc[pool['error'].idxmin()]
        return best


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def run_selection(output_path: str = None):
    """
    Main selection workflow:
    1. Load databases
    2. For each particle, apply rules and select best fit
    3. Save results to JSON
    """
    print("="*80)
    print("KSAU v5.0: Automated Topology Selection")
    print("="*80)
    print()

    # Load data
    links, knots, particles = load_databases()

    # Selection results
    results = {}

    print("Applying selection protocol...")
    print("-"*80)
    print(f"{'Particle':<10} | {'Selected':<12} | {'C':>2} | {'Det':>4} | {'V':>8} | {'N':>2} | {'Error':>8}")
    print("-"*80)

    for name, data in particles.items():
        # Step 1: Apply selection rules
        pool = apply_selection_rules(name, data, links, knots)

        # Step 2: Select best mass fit
        try:
            selected = select_best_fit(pool, data['mass'], data['gen'],
                                      data['type'], data['group'])

            # Extract data
            topology = selected['name']
            V = float(selected['volume'])
            N = int(selected['crossing_number'])
            C = int(selected['components'])
            Det = int(selected['determinant'])
            error = float(selected['error']) * 100

            # Save
            results[name] = {
                'topology': topology,
                'volume': V,
                'crossing_number': N,
                'components': C,
                'determinant': Det,
                'generation': data['gen'],
                'charge_type': data['type'],
                'observed_mass': data['mass'],
                'predicted_mass': float(selected['pred_m']),
                'error_percent': error
            }

            print(f"{name:<10} | {topology:<12} | {C:>2} | {Det:>4} | {V:>8.3f} | {N:>2} | {error:>7.2f}%")

        except Exception as e:
            print(f"{name:<10} | ERROR: {e}")
            results[name] = {'error': str(e)}

    print("-"*80)
    print()

    # Save to JSON
    if output_path is None:
        output_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"OK Saved topology assignments to: {output_path}")
    print()
    print("="*80)
    print("Selection complete. Use these assignments in prediction scripts.")
    print("="*80)


if __name__ == "__main__":
    run_selection()
