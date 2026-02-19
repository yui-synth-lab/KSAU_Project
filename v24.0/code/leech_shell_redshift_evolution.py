#!/usr/bin/env python3
"""
KSAU v24.0: Leech Shell with Redshift Evolution
================================================

Physical Insight (from v23.0):
  - R_cell(z) = R_0 * (1+z)^-β, with β = 13/6
  - Effective "shell depth" changes with redshift
  - DES (z_mean=0.55) and KiDS (z_mean=0.3) sample different evolved states

New Hypothesis (v24.0):
  - The "evolved effective radius" at each survey's redshift 
    corresponds to a discrete Leech shell magnitude
  - This explains R_cell variation without adding free parameters

Method:
  1. Apply z-evolution to a reference Leech shell magnitude
  2. Check if evolved radius matches another shell's magnitude
  3. If so, this is a "quantum transition" not a continuous variation
"""

import json
import numpy as np
from pathlib import Path

def load_leech_shells() -> dict:
    """Load Leech shell magnitudes."""
    config_path = "E:\\Obsidian\\KSAU_Project\\v24.0\\data\\leech_shell_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    shells = config['leech_shell_distances']
    magnitudes = {}
    for shell_name, shell_data in shells.items():
        if shell_name.startswith('shell_'):
            idx = int(shell_name.split('_')[1])
            magnitudes[idx] = shell_data['magnitude']
    
    return magnitudes

def load_v23_physical_constants() -> dict:
    """Load constants from v23.0."""
    return {
        'beta': 13.0 / 6.0,  # R_cell evolution exponent
        'alpha': 0.1309,  # From SSoT: κ
        'z_des': 0.55,
        'z_kids': 0.3,
        'r_cell_des': 39.8,
        'r_cell_kids': 16.5
    }

def redshift_evolve_radius(r_ref: float, z_ref: float, z_new: float, beta: float) -> float:
    """
    Evolve radius with redshift using power law:
    R(z) = R(z_ref) * ((1+z_ref) / (1+z_new))^beta
    """
    evolution_factor = ((1 + z_ref) / (1 + z_new)) ** beta
    return r_ref * evolution_factor

def hypothesis_leech_shell_evolution():
    """
    Test if Leech shell magnitudes with z-evolution can explain observations.
    
    Hypothesis:
      - Choose a reference shell at z=0 with magnitude M_ref
      - At DES redshift: M_ref * ((1+0)/(1+z_DES))^β ≈ observed shell magnitude M_DES
      - At KiDS redshift: M_ref * ((1+0)/(1+z_kids))^β ≈ observed shell magnitude M_kids
    """
    magnitudes = load_leech_shells()
    constants = load_v23_physical_constants()
    
    # Available shell magnitudes (excluding 0)
    shell_mags = {k: v for k, v in magnitudes.items() if v > 0}
    shell_mags_sorted = sorted(shell_mags.items(), key=lambda x: x[1])
    
    print("\n[Leech Shell + Redshift Evolution Test]")
    print("="*70)
    print(f"β (z-evolution) = {constants['beta']:.4f}")
    print(f"z_DES = {constants['z_des']}, z_KiDS = {constants['z_kids']}")
    print(f"\nAvailable shell magnitudes:")
    for shell_idx, mag in shell_mags_sorted:
        print(f"  Shell {shell_idx}: {mag:.4f}")
    
    # Try all shells as potential "reference" (z=0) states
    print(f"\n[Testing Shell Assignments]")
    print("-"*70)
    
    best_fit = {'error': float('inf')}
    
    for ref_shell_idx, ref_mag in shell_mags.items():
        # Evolve from z=0 to DES redshift
        des_evolved = redshift_evolve_radius(ref_mag, 0, constants['z_des'], constants['beta'])
        kids_evolved = redshift_evolve_radius(ref_mag, 0, constants['z_kids'], constants['beta'])
        
        # Find closest Leech shells to evolved values
        des_closest = min(shell_mags.items(), 
                         key=lambda x: abs(x[1] - des_evolved * constants['r_cell_des']))
        kids_closest = min(shell_mags.items(),
                          key=lambda x: abs(x[1] - kids_evolved * constants['r_cell_kids']))
        
        # Alternative: scale to match observations directly
        r0_des = constants['r_cell_des'] / des_evolved if des_evolved > 0 else float('inf')
        r0_kids = constants['r_cell_kids'] / kids_evolved if kids_evolved > 0 else float('inf')
        
        error = abs(r0_des - r0_kids) / max(r0_des, r0_kids)
        
        if error < best_fit['error']:
            best_fit = {
                'error': error,
                'ref_shell': ref_shell_idx,
                'ref_mag': ref_mag,
                'r0_from_des': r0_des,
                'r0_from_kids': r0_kids,
                'des_evolved': des_evolved,
                'kids_evolved': kids_evolved
            }
    
    # Report best fit
    print(f"\nBest Reference Shell: {best_fit['ref_shell']}")
    print(f"  Reference magnitude: {best_fit['ref_mag']:.4f}")
    print(f"  R_0 from DES: {best_fit['r0_from_des']:.4f} Mpc/h")
    print(f"  R_0 from KiDS: {best_fit['r0_from_kids']:.4f} Mpc/h")
    print(f"  R_0 discrepancy: {best_fit['error']*100:.2f}%")
    
    print(f"\n  Evolved magnitudes:")
    print(f"    At DES (z={constants['z_des']}): {best_fit['des_evolved']:.4f}")
    print(f"    At KiDS (z={constants['z_kids']}): {best_fit['kids_evolved']:.4f}")
    
    print(f"\n  Predicted R_cell:")
    r0_avg = (best_fit['r0_from_des'] + best_fit['r0_from_kids']) / 2
    print(f"    DES: {r0_avg * best_fit['des_evolved']:.2f} Mpc/h (observed: {constants['r_cell_des']:.2f})")
    print(f"    KiDS: {r0_avg * best_fit['kids_evolved']:.2f} Mpc/h (observed: {constants['r_cell_kids']:.2f})")
    
    # Check if error is acceptable
    if best_fit['error'] < 0.15:
        print(f"\n  ✓ CONSISTENT: Shell {best_fit['ref_shell']} + z-evolution explains observations")
    else:
        print(f"\n  ✗ INSUFFICIENT: Error still too high, may need 2-shell combination")
    
    return best_fit

if __name__ == "__main__":
    result = hypothesis_leech_shell_evolution()
