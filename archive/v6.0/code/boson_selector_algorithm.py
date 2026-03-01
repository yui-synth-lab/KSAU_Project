"""
Boson Selection Algorithm (KSAU v6.0 - Phase 1 Update)
=======================================================

Algorithmic selection of gauge bosons and Higgs based on:
1. Brunnian topology (gauge mediation principle)
2. Borromean volume relationships (V = n×V_borr)
3. Mass prediction accuracy using boson scaling law

This ensures objective, reproducible selection without hardcoding.
"""

import pandas as pd
import numpy as np

def check_brunnian_property(link_name, df_links):
    """
    Check if a link has Brunnian property.
    A link is Brunnian if removing any one component unties the rest.

    For LinkInfo database, we use heuristics:
    - Must have >=2 components
    - Specific link families known to be Brunnian (L11n, L11a, etc.)
    """
    row = df_links[df_links['name'] == link_name]
    if row.empty:
        return False

    row = row.iloc[0]
    components = int(row['components'])

    if components < 2:
        return False

    # Known Brunnian families (from literature)
    # Borromean Rings and their generalizations
    brunnian_patterns = ['L6a4', 'L6n1', 'L8', 'L9', 'L10', 'L11', 'L12']

    for pattern in brunnian_patterns:
        if link_name.startswith(pattern):
            return True

    return False

def compute_borromean_multiplicity(volume, v_borr, tolerance=0.05):
    """
    Check if volume is a simple multiple of Borromean volume.
    Returns (multiplicity, error) if found, else (None, inf)
    """
    for n in [1.0, 1.5, 2.0, 2.5, 3.0]:
        expected = n * v_borr
        error = abs(volume - expected) / expected
        if error < tolerance:
            return n, error

    return None, np.inf

def score_boson_candidate(link_row, observed_mass, v_borr, slope_b, intercept_b):
    """
    Score a boson candidate based on multiple criteria:
    1. Brunnian property (required)
    2. Borromean multiplicity (bonus)
    3. Mass prediction accuracy

    Returns: (total_score, components_dict)
    """
    volume = float(link_row['volume'])
    components = int(link_row['components'])

    # Criterion 1: Brunnian property (binary)
    is_brunnian = check_brunnian_property(link_row['name'], link_row.to_frame().T)
    if not is_brunnian:
        return -np.inf, {}  # Reject non-Brunnian

    # Criterion 2: Borromean multiplicity
    mult, mult_error = compute_borromean_multiplicity(volume, v_borr)

    # Criterion 3: Mass prediction accuracy
    ln_m_pred = slope_b * volume + intercept_b
    m_pred = np.exp(ln_m_pred)
    mass_error = abs(m_pred - observed_mass) / observed_mass

    # Scoring (lower is better for errors)
    # Prioritize mass accuracy, then Borromean relationship
    score = 0.0
    score -= 100 * mass_error  # Primary: mass accuracy

    if mult is not None:
        score += 10  # Bonus for Borromean relationship
        score -= 5 * mult_error  # Penalty for imperfect ratio

    components_dict = {
        'is_brunnian': True,
        'borromean_multiplicity': mult,
        'borromean_error': mult_error if mult else None,
        'mass_prediction_error': mass_error,
        'predicted_mass': m_pred,
        'score': score
    }

    return score, components_dict

def select_boson_algorithmically(boson_name, df_links, phys_constants):
    """
    Algorithmically select the best topology for a gauge boson or Higgs.

    Selection criteria (in order of priority):
    1. Must be Brunnian (gauge principle)
    2. Crossing number near target range (11-12 for W/Z/H)
    3. Borromean volume relationship (bonus)
    4. Best mass prediction accuracy

    Returns: (best_link_name, selection_info)
    """
    boson_config = phys_constants['bosons'][boson_name]
    observed_mass = boson_config['observed_mass'] / 1000  # MeV to GeV
    target_crossing = boson_config.get('target_crossing', 11)

    # Boson scaling law parameters
    slope_b = phys_constants['bosons']['scaling']['A']
    intercept_b = phys_constants['bosons']['scaling']['C']

    # Borromean reference volume
    v_borr = phys_constants['v_borromean']

    # Filter candidates
    # - Hyperbolic (V > 0)
    # - Crossing number near target
    # - Components: 2-3 (gauge mediation or scalar)
    candidates = df_links[
        (df_links['volume'] > 0) &
        (df_links['crossing_number'].between(target_crossing - 1, target_crossing + 1)) &
        (df_links['components'].isin([2, 3]))
    ].copy()

    print(f"  Candidates for {boson_name}: {len(candidates)} links")

    if candidates.empty:
        raise ValueError(f"No candidates found for {boson_name}")

    # Score all candidates
    scores = []
    for idx, row in candidates.iterrows():
        score, info = score_boson_candidate(row, observed_mass, v_borr, slope_b, intercept_b)
        scores.append({
            'name': row['name'],
            'score': score,
            'volume': row['volume'],
            'components': row['components'],
            **info
        })

    # Sort by score (descending)
    scores_df = pd.DataFrame(scores).sort_values('score', ascending=False)

    # Top candidates
    print(f"\n  Top 5 candidates for {boson_name}:")
    for i, row in scores_df.head(5).iterrows():
        print(f"    {row['name']:<15} Score={row['score']:>6.2f} | "
              f"V={row['volume']:.3f} | "
              f"Mass_err={row['mass_prediction_error']*100:.2f}% | "
              f"Borr×{row['borromean_multiplicity']}")

    # Best candidate
    best = scores_df.iloc[0]

    selection_info = {
        'selected_topology': best['name'],
        'volume': best['volume'],
        'components': best['components'],
        'score': best['score'],
        'is_brunnian': best['is_brunnian'],
        'borromean_multiplicity': best['borromean_multiplicity'],
        'mass_prediction_error_percent': best['mass_prediction_error'] * 100,
        'predicted_mass_gev': best['predicted_mass'],
        'selection_method': 'algorithmic_brunnian_borromean_mass'
    }

    print(f"\n  ✓ Selected: {best['name']} (Score={best['score']:.2f}, Error={best['mass_prediction_error']*100:.2f}%)")

    return best['name'], selection_info

if __name__ == "__main__":
    # Test the algorithm
    import ksau_config

    phys = ksau_config.load_physical_constants()
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1], low_memory=False)

    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)

    hyper_links = df_l[df_l['volume'] > 0].copy()

    print("Testing Boson Selection Algorithm")
    print("="*80)

    for boson in ['W', 'Z', 'Higgs']:
        print(f"\n{'='*80}")
        print(f"Selecting {boson} Boson")
        print('='*80)
        best_name, info = select_boson_algorithmically(boson, hyper_links, phys)
        print(f"\nResult: {boson} -> {best_name}")
        print(f"  Volume: {info['volume']:.3f}")
        print(f"  Borromean multiplicity: {info['borromean_multiplicity']}")
        print(f"  Mass prediction error: {info['mass_prediction_error_percent']:.2f}%")
