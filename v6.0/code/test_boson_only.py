"""
Quick test: verify boson selection produces v6.3 candidates
"""
import json
import sys
from pathlib import Path

# Import the main script's boson selection
sys.path.insert(0, str(Path(__file__).parent))
import topology_official_selector as selector

# Load data
print("Loading data...")
phys = selector.load_physical_constants()
df_l, df_k = selector.load_data()

# Prepare hyperbolic links
hyper_links = df_l[df_l['volume'] > 0].copy()
print(f"Hyperbolic links: {len(hyper_links)}")

# Test boson selection
print("\n" + "="*80)
print("Testing v6.3 Boson Selection")
print("="*80)

expected = {
    'W': 'L11n387',
    'Z': 'L11a431',
    'Higgs': 'L11a55'
}

results = {}
for boson in ['W', 'Z', 'Higgs']:
    print(f"\nSelecting {boson}...")
    best = selector.select_boson_v63(boson, hyper_links, phys)
    topo_name = best['name'].split('{')[0]  # Remove braid indices
    results[boson] = topo_name

    status = "[OK]" if topo_name == expected[boson] else "[FAIL]"
    print(f"  {status} Got: {topo_name}, Expected: {expected[boson]}, Error: {best['mass_error_pct']:.2f}%")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
all_pass = all(results[b] == expected[b] for b in results)
if all_pass:
    print("[SUCCESS] All bosons match v6.3 candidates!")
else:
    print("[FAILED] Some bosons don't match:")
    for b in results:
        if results[b] != expected[b]:
            print(f"  {b}: got {results[b]}, expected {expected[b]}")
