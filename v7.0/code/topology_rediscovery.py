import numpy as np
import pandas as pd
import json
from pathlib import Path
from ksau_config_v7 import load_physical_constants, load_knotinfo_path

def run_topology_rediscovery():
    print("="*80)
    print("KSAU v7.0: Topology Re-discovery (The Superstring Model)")
    print("Constants: kappa = pi/26, Nq = 8.0, Nl = 21.4")
    print("="*80)
    
    phys = load_physical_constants()
    ki_path = load_knotinfo_path()
    
    # 1. Load Knot Database
    print(f"Loading Knot Database from {ki_path}...")
    df = pd.read_csv(ki_path, sep='|', low_memory=False)
    # Filter for reasonable knots (crossing <= 12)
    # Convert crossing_number to numeric first
    df['crossing_number'] = pd.to_numeric(df['crossing_number'], errors='coerce')
    df = df[df['crossing_number'] <= 12]
    # Ensure volume is numeric and positive
    df['hyperbolic_volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df = df[df['hyperbolic_volume'] > 0]
    
    # 2. Parameters (The v7.0 Quantum Model)
    kappa = np.pi / 26
    nq = 8.0
    nl = 21.4
    
    # Anchor Lepton Intercept (Electron is the base state)
    cl = np.log(phys['leptons']['Electron']['observed_mass'])
    
    # Optimize Quark Intercept Cq globally
    # We'll test a range around our anchor to find the absolute minimum MAE
    cq_candidates = np.linspace(-4.55, -4.45, 100)
    best_cq = -4.5063
    min_overall_mae = float('inf')
    
    results = {}
    
    print("\n[Phase 1: Precision Intercept Optimization]")
    for cq_test in cq_candidates:
        temp_errors = []
        for name, meta in phys['quarks'].items():
            obs_ln_m = np.log(meta['observed_mass'])
            twist = (2 - meta['generation']) * ((-1)**(2 if meta['charge_type'] == 'up-type' else 3))
            
            # Find best knot for this Cq
            df['pred_ln_m'] = nq * kappa * df['hyperbolic_volume'] + cq_test + kappa * twist
            df['diff'] = np.abs(df['pred_ln_m'] - obs_ln_m)
            best_err = df['diff'].min()
            temp_errors.append(best_err)
            
        mae_test = np.mean(temp_errors)
        if mae_test < min_overall_mae:
            min_overall_mae = mae_test
            best_cq = cq_test
            
    print(f"  Optimal Quark Intercept Found: {best_cq:.6f}")
    
    # 3. Final Rediscovery Loop with Optimized Parameters
    for sector, particles in [('quarks', phys['quarks']), ('leptons', phys['leptons'])]:
        slope = (nq if sector == 'quarks' else nl) * kappa
        intercept = best_cq if sector == 'quarks' else cl
        
        print(f"\nSearching for {sector.upper()}:")
        for name, meta in particles.items():
            obs_mass = meta['observed_mass']
            target_ln_m = np.log(obs_mass)
            
            # Special case for Electron (Anchor)
            if name == 'Electron':
                results[name] = {
                    'topology': '3_1', # Canonical Unknot/Torus base
                    'volume': 0.0,
                    'obs_mass': obs_mass,
                    'pred_mass': obs_mass,
                    'error': 0.0
                }
                print(f"  {name:<12}: 3_1 (Anchor) | Vol=0.0000  | Err=0.00%")
                continue
            
            # For quarks, we need to account for twist in the search
            # We don't know the components/gen of the "new" knot yet, 
            # so we assume Standard Model generation and typical components for the search.
            twist = 0
            if sector == 'quarks':
                gen = meta['generation']
                comp = 2 if meta['charge_type'] == 'up-type' else 3
                twist = (2 - gen) * ((-1)**comp)
            
            # Find closest knot
            df['pred_ln_m'] = slope * df['hyperbolic_volume'] + intercept + kappa * twist
            df['diff'] = np.abs(df['pred_ln_m'] - target_ln_m)
            
            best_match = df.nsmallest(1, 'diff').iloc[0]
            pred_mass = np.exp(best_match['pred_ln_m'])
            error = abs(pred_mass - obs_mass) / obs_mass * 100
            
            results[name] = {
                'topology': best_match['name'],
                'volume': best_match['hyperbolic_volume'],
                'obs_mass': obs_mass,
                'pred_mass': pred_mass,
                'error': error
            }
            
            print(f"  {name:<12}: {best_match['name']:<10} | Vol={best_match['hyperbolic_volume']:<7.4f} | Err={error:.2f}%")
            
    # 4. Final Audit
    all_errors = [r['error'] for r in results.values()]
    mae = np.mean(all_errors)
    print("\n" + "="*80)
    print(f"FINAL v7.0 AUDIT MAE: {mae:.4f}%")
    print("="*80)
    
    # Save to v7.0 data
    output_path = Path(__file__).parent.parent / 'data' / 'v7_topology_assignments.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"New assignments saved to {output_path}")

if __name__ == "__main__":
    run_topology_rediscovery()
