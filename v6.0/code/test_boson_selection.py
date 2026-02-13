"""
Quick test of v6.3 boson selection algorithm
"""
import pandas as pd
import numpy as np
import ksau_config
import re

print("="*80)
print("Testing v6.3 Boson Selection Algorithm")
print("="*80)

# Load data
print("\nLoading data...")
phys = ksau_config.load_physical_constants()
df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1], low_memory=False)

# Prepare links
for c in ['volume', 'crossing_number', 'components', 'determinant']:
    df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)

hyper_links = df_l[df_l['volume'] > 0].copy()
print(f"Hyperbolic links: {len(hyper_links)}")

# Boson selection function
def select_boson(boson_name, links_df, phys):
    print(f"\n{'='*80}")
    print(f"Selecting {boson_name} Boson")
    print('='*80)

    # Parameters
    A_b = phys['bosons']['scaling']['A']
    C_b = phys['bosons']['scaling']['C']
    m_obs = phys['bosons'][boson_name]['observed_mass']
    V_borr = phys['v_borromean']

    # Target volume
    V_target = (np.log(m_obs) - C_b) / A_b
    print(f"Target volume from M_{boson_name} = {m_obs} MeV: V = {V_target:.4f}")

    # Search range
    if boson_name == 'Higgs':
        V_range = (V_target - 1.0, V_target + 1.0)
        target_comp = 2
    else:
        V_range = (V_target - 0.5, V_target + 0.5)
        target_comp = 3

    # Filter
    candidates = links_df[
        (links_df['volume'] >= V_range[0]) &
        (links_df['volume'] <= V_range[1])
    ].copy()

    if 'components' in links_df.columns:
        candidates = candidates[candidates['components'] == target_comp]

    print(f"Candidates: {len(candidates)}")

    # Score
    scores = []
    for _, row in candidates.iterrows():
        V = row['volume']

        # Brunnian
        lm_str = str(row.get('linking_matrix', ''))
        nums = re.findall(r'-?\d+', lm_str)
        is_brunnian = all(n == '0' for n in nums) if nums else False

        # Borromean
        borr_mult = None
        for n in [1.0, 1.5, 2.0, 2.5, 3.0]:
            if abs(V - n * V_borr) / (n * V_borr) < 0.05:
                borr_mult = n
                break

        # Mass error
        m_pred = np.exp(A_b * V + C_b)
        mass_error = abs(m_pred - m_obs) / m_obs

        # Score (higher is better)
        # For Higgs (2-comp scalar), prioritize mass accuracy over Borromean
        # For W/Z (3-comp gauge), Borromean relationship is physically meaningful
        score = 0.0
        if is_brunnian:
            score += 100

        if boson_name == 'Higgs':
            # Higgs: mass accuracy is paramount (scalar clasp)
            score -= 100 * mass_error  # Double weight for mass accuracy
            if borr_mult:
                score += 5  # Minor bonus for Borromean coincidence
        else:
            # W/Z: Borromean structure is physically meaningful
            score -= 50 * mass_error
            if borr_mult:
                score += 20

        scores.append({
            'name': row['name'],
            'V': V,
            'score': score,
            'brunnian': is_brunnian,
            'borr': borr_mult,
            'err_%': mass_error * 100
        })

    # Best (sort by score, then by name for deterministic tiebreaking)
    scores_df = pd.DataFrame(scores).sort_values(['score', 'name'], ascending=[False, True])
    print("\nTop 5:")
    print(scores_df.head(5).to_string(index=False))

    best = scores_df.iloc[0]
    print(f"\n[OK] Selected: {best['name']} (Error: {best['err_%']:.2f}%)")

    return best['name']

# Test all bosons
results = {}
for boson in ['W', 'Z', 'Higgs']:
    results[boson] = select_boson(boson, hyper_links, phys)

print("\n" + "="*80)
print("FINAL RESULTS")
print("="*80)
for boson, topo in results.items():
    print(f"{boson:<10} -> {topo}")
