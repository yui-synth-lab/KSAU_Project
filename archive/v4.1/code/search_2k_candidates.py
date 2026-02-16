"""
Scientific Link Search: Exhaustive exploration within 2^k Binary Rule.
Search for Det=64 (bottom), Det=128 (4th gen), and Det=124 (top) candidates.
"""
import pandas as pd
import numpy as np

G = 0.915965594
GAMMA_Q = (10.0/7.0) * G
B_PRIME = -(7.0 + G)

# Ideal volumes (from ln(m_obs) = GAMMA_Q * V + B_PRIME)
def ideal_volume(m_obs):
    return (np.log(m_obs) - B_PRIME) / GAMMA_Q

V_IDEAL = {
    'u': ideal_volume(2.16),
    'd': ideal_volume(4.67),
    's': ideal_volume(93.4),
    'c': ideal_volume(1270),
    'b': ideal_volume(4180),
    't': ideal_volume(172760),
}

print("=" * 80)
print("  KSAU v4.1: Scientific Link Search (2^k Rule Preserved)")
print("=" * 80)

print("\n  Ideal volumes for each quark:")
for q, v in V_IDEAL.items():
    print(f"    {q}: V_ideal = {v:.4f}")

# Load LinkInfo
df = pd.read_csv("data/linkinfo_data_complete.csv", sep='|', low_memory=False, skiprows=[1])

# Clean columns
df.columns = df.columns.str.strip()
print(f"\n  Loaded {len(df)} link entries")

# Parse key columns
df['det_val'] = pd.to_numeric(df['determinant'], errors='coerce')
df['vol_val'] = pd.to_numeric(df['volume'], errors='coerce')
df['comp_val'] = pd.to_numeric(df['components'], errors='coerce')
df['cross_val'] = pd.to_numeric(df['crossing_number'], errors='coerce')

# Drop rows with missing critical data
valid = df.dropna(subset=['det_val', 'vol_val', 'comp_val'])
print(f"  Valid entries (with det, vol, comp): {len(valid)}")

def search_candidates(det_target, comp_target, v_ideal, label, top_n=20):
    """Search for links with given determinant and component count, sorted by volume proximity."""
    mask = (valid['det_val'] == det_target) & (valid['comp_val'] == comp_target)
    candidates = valid[mask].copy()

    if len(candidates) == 0:
        print(f"\n  [{label}] No candidates found with Det={det_target}, C={comp_target}")

        # Try without component filter
        mask2 = (valid['det_val'] == det_target)
        all_det = valid[mask2]
        if len(all_det) > 0:
            print(f"  (Found {len(all_det)} links with Det={det_target} but different component counts:)")
            comp_counts = all_det['comp_val'].value_counts()
            for c, n in comp_counts.items():
                print(f"    Components={int(c)}: {n} links")
        return None

    candidates['v_diff'] = abs(candidates['vol_val'] - v_ideal)
    candidates['error_pct'] = (np.exp(GAMMA_Q * candidates['vol_val'] + B_PRIME) -
                                np.exp(GAMMA_Q * v_ideal + B_PRIME)) / \
                               np.exp(GAMMA_Q * v_ideal + B_PRIME) * 100
    candidates = candidates.sort_values('v_diff')

    print(f"\n  [{label}] Found {len(candidates)} candidates (Det={det_target}, C={comp_target})")
    print(f"  Target: V_ideal = {v_ideal:.4f}")
    print(f"\n  {'Rank':<5} {'Name':<16} {'V':>10} {'|V-V_id|':>10} {'Pred Err':>10} {'Cross':>6}")
    print(f"  {'-'*60}")

    for i, (_, row) in enumerate(candidates.head(top_n).iterrows()):
        name = str(row['name']).strip() if pd.notna(row['name']) else '?'
        v = row['vol_val']
        vd = row['v_diff']
        m_pred = np.exp(GAMMA_Q * v + B_PRIME)
        m_obs = np.exp(GAMMA_Q * v_ideal + B_PRIME)
        err = (m_pred - m_obs) / m_obs * 100
        cross = int(row['cross_val']) if pd.notna(row['cross_val']) else '?'
        print(f"  {i+1:<5} {name:<16} {v:>10.4f} {vd:>10.4f} {err:>+9.1f}% {cross:>6}")

    return candidates

# =====================================================================
# SEARCH 1: Bottom quark — Det=64, 3-component, V≈12.42
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 1: Bottom Quark (Det=64, 3-component)")
print("  Current: L10a141 (V=12.276, err=-17.3%)")
print("  Ideal: V=12.42")
print("=" * 80)

b_candidates = search_candidates(64, 3, V_IDEAL['b'], "Bottom (Det=64, C=3)")

# Also check 2-component with Det=64
print("\n  --- Also checking Det=64, 2-component ---")
search_candidates(64, 2, V_IDEAL['b'], "Bottom (Det=64, C=2)", top_n=10)

# =====================================================================
# SEARCH 2: Det=128 (2^7) — 4th generation prediction OR better bottom
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 2: Det=128 (2^7) Links")
print("  Purpose: 4th generation candidate OR alternative bottom")
print("=" * 80)

search_candidates(128, 3, V_IDEAL['b'], "Det=128, C=3 (near bottom V)", top_n=15)
search_candidates(128, 2, V_IDEAL['b'], "Det=128, C=2 (near bottom V)", top_n=10)

# =====================================================================
# SEARCH 3: Top quark — Det=124, 2-component, V≈15.1
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 3: Top Quark alternatives (Det=124, 2-component)")
print("  Current: L11a62 (V=15.360, err=+13.1%)")
print("  Ideal: V=15.14")
print("=" * 80)

t_candidates = search_candidates(124, 2, V_IDEAL['t'], "Top (Det=124, C=2)")

# =====================================================================
# SEARCH 4: Down quark — Det=16, 3-component, V≈7.22
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 4: Down Quark alternatives (Det=16, 3-component)")
print("  Current: L6a4 (V=7.328, err=+14.0%)")
print("  Ideal: V=7.22")
print("=" * 80)

d_candidates = search_candidates(16, 3, V_IDEAL['d'], "Down (Det=16, C=3)")

# =====================================================================
# SEARCH 5: Gemini's candidates — verify existence
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 5: Verify Gemini's proposed links")
print("=" * 80)

for link_name in ['L11n422', 'L11a144']:
    mask = valid['name'].str.strip() == link_name
    matches = valid[mask]
    if len(matches) > 0:
        row = matches.iloc[0]
        print(f"\n  {link_name}: FOUND")
        print(f"    Det = {row['det_val']}")
        print(f"    Vol = {row['vol_val']}")
        print(f"    Components = {row['comp_val']}")
        print(f"    Crossing = {row['cross_val']}")
    else:
        # Try with orientation suffix
        mask2 = valid['name'].str.strip().str.startswith(link_name)
        matches2 = valid[mask2]
        if len(matches2) > 0:
            print(f"\n  {link_name}: Found {len(matches2)} orientation variant(s):")
            for _, row in matches2.iterrows():
                print(f"    {str(row['name']).strip()}: Det={row['det_val']}, Vol={row['vol_val']:.4f}, C={row['comp_val']}")
        else:
            print(f"\n  {link_name}: NOT FOUND in database")

# =====================================================================
# SEARCH 6: Up-type even-determinant alternatives for Top
# =====================================================================
print("\n" + "=" * 80)
print("  SEARCH 6: Top quark — broader even-Det search (C=2)")
print("  Looking for 2-comp links with V in [15.0, 15.3]")
print("=" * 80)

mask = (valid['comp_val'] == 2) & (valid['vol_val'] >= 15.0) & (valid['vol_val'] <= 15.3) & (valid['det_val'] % 2 == 0)
top_broad = valid[mask].copy()
top_broad['err'] = (np.exp(GAMMA_Q * top_broad['vol_val'] + B_PRIME) - 172760) / 172760 * 100

if len(top_broad) > 0:
    top_broad = top_broad.sort_values('err', key=abs)
    print(f"\n  Found {len(top_broad)} candidates")
    print(f"  {'Name':<20} {'V':>10} {'Det':>6} {'Error':>8} {'Cross':>6}")
    print(f"  {'-'*55}")
    for _, row in top_broad.head(20).iterrows():
        name = str(row['name']).strip()
        print(f"  {name:<20} {row['vol_val']:>10.4f} {int(row['det_val']):>6} {row['err']:>+7.1f}% {int(row['cross_val']):>6}")
else:
    print("  No candidates in this volume range")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 80)
print("  SUMMARY: Can we maintain 2^k AND improve accuracy?")
print("=" * 80)

print(f"""
  Bottom (Det=64, C=3):
    Current best: L10a141, V=12.276, err=-17.3%
    Ideal V = {V_IDEAL['b']:.4f}
    Gap: {V_IDEAL['b'] - 12.276:.4f} (need V to increase by this amount)
""")

print("=" * 80)
print("  END OF SEARCH")
print("=" * 80)
