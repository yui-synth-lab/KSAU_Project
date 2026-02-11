"""
Analyze current determinant assignments and discover better rules.
"""

import pandas as pd
import numpy as np
import json
import ksau_config
from pathlib import Path

def analyze_current_assignments():
    """
    Examine what determinant values are actually being selected for each particle.
    """
    print("="*80)
    print("DETERMINANT RULE ANALYSIS")
    print("="*80)
    
    # Load current assignments
    assignments_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(assignments_path, 'r') as f:
        assignments = json.load(f)
    
    phys = ksau_config.load_physical_constants()
    
    # Organize by particle type
    print("\nQUARKS:")
    print("-" * 80)
    print(f"{'Particle':<12} {'Det':<6} {'Charge':<12} {'Gen':<4} {'Topology':<15} {'Volume':<10}")
    print("-" * 80)
    
    quark_ints = []
    for q_name in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
        if q_name in assignments:
            det = assignments[q_name]['determinant']
            mass = phys['quarks'][q_name]['observed_mass']
            gen = assignments[q_name]['generation']
            charge_type = phys['quarks'][q_name]['charge_type']
            topo = assignments[q_name]['topology']
            vol = assignments[q_name]['volume']
            
            quark_ints.append({
                'name': q_name,
                'det': det,
                'mass': mass,
                'charge_type': charge_type,
                'gen': gen
            })
            
            is_power_of_2 = det > 0 and (det & (det - 1)) == 0
            is_mult_4 = det % 4 == 0
            
            print(f"{q_name:<12} {det:<6} {charge_type:<12} {gen:<4} {topo:<15} {vol:.4f}")
            print(f"  → Power of 2? {is_power_of_2}, Mult of 4? {is_mult_4}")
    
    print("\nLEPTONS:")
    print("-" * 80)
    print(f"{'Particle':<12} {'Det':<6} {'N':<6} {'Topology':<15}")
    print("-" * 80)
    
    lepton_ints = []
    for l_name in ['Electron', 'Muon', 'Tau']:
        if l_name in assignments:
            det = assignments[l_name]['determinant']
            mass = phys['leptons'][l_name]['observed_mass']
            gen = assignments[l_name]['generation']
            n = assignments[l_name]['crossing_number']
            topo = assignments[l_name]['topology']
            
            lepton_ints.append({
                'name': l_name,
                'det': det,
                'mass': mass,
                'gen': gen,
                'n': n
            })
            
            print(f"{l_name:<12} {det:<6} {n:<6} {topo:<15}")
            print(f"  → Odd? {det % 2 != 0}")
    
    print("\n" + "="*80)
    print("CURRENT RULE VIOLATIONS")
    print("="*80)
    
    def is_power_of_two(n):
        return n > 0 and (n & (n - 1)) == 0
    
    print("\nExpected Rules (from topology_official_selector.py):")
    print("  Down-type:  Det = 2^k (power of 2)")
    print("  Up-type:    Det = 4n but NOT 2^k")
    print("  Leptons:    Det = odd")
    
    print("\nViolations:")
    violations = []
    for q in quark_ints:
        charge = phys['quarks'][q['name']]['charge_type']
        if charge == 'down-type':
            if not is_power_of_two(q['det']):
                violations.append(f"  ✗ {q['name']:12} (down-type): Det={q['det']} (NOT power of 2)")
        elif charge == 'up-type':
            if is_power_of_two(q['det']) or q['det'] % 4 != 0:
                violations.append(f"  ✗ {q['name']:12} (up-type): Det={q['det']} (should be 4n, not 2^k)")
    
    for l in lepton_ints:
        if l['det'] % 2 == 0:
            violations.append(f"  ✗ {l['name']:12} (lepton): Det={l['det']} (EVEN, should be odd)")
    
    if violations:
        print("\n".join(violations))
    else:
        print("  (None - all match expected rules)")
    
    # Now analyze the physics
    print("\n" + "="*80)
    print("PHYSICS ANALYSIS")
    print("="*80)
    
    print("\nDeterminant vs. Mass (Quarks):")
    sorted_quarks = sorted(quark_ints, key=lambda x: x['mass'])
    for q in sorted_quarks:
        print(f"  {q['name']:12}: m={q['mass']:>8.3f}, Det={q['det']:>3}, Gen={q['gen']}")
    
    print("\nDeterminant vs. Crossing Number (Leptons):")
    sorted_leptons = sorted(lepton_ints, key=lambda x: x['mass'])
    for l in sorted_leptons:
        print(f"  {l['name']:12}: m={l['mass']:>8.3f}, N={l['n']}, Det={l['det']}")
    
    # Statistical analysis
    print("\n" + "="*80)
    print("DETERMINANT STATISTICS")
    print("="*80)
    
    all_dets = [q['det'] for q in quark_ints] + [l['det'] for l in lepton_ints]
    print(f"\nAll determinants: {sorted(set(all_dets))}")
    print(f"Min: {min(all_dets)}, Max: {max(all_dets)}, Mean: {np.mean(all_dets):.1f}")
    
    # Check for patterns
    print("\nPower of 2 analysis:")
    for det in sorted(set(all_dets)):
        is_pow2 = is_power_of_two(det)
        is_mult4 = (det % 4 == 0)
        is_odd = (det % 2 != 0)
        print(f"  Det={det:>3}: Power2={is_pow2}, Mult4={is_mult4}, Odd={is_odd}")

if __name__ == "__main__":
    analyze_current_assignments()
