"""
KSAU v14.0.2 Dark Matter Mass Solver
Script purpose: Calculates topological soliton masses for N=2, 6, 12, 24.
Dependencies: numpy, pandas, json
SSoT sources: v6.0/data/physical_constants.json, v13.0/data/modular_invariants.csv
Author: Gemini (Simulation Kernel)
Date: 2026-02-16
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path

def load_constants():
    """Load physical constants from SSoT with fallback."""
    path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            path = Path('v6.0/data/physical_constants.json')
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("CRITICAL: SSoT constants not found.")
            return {'kappa': np.pi/24.0}

def dark_matter_mass_solver():
    """
    KSAU v14.0: Dark Matter Mass Specificity Solver (Integrity Revision).
    Calculates soliton masses with clarified geometric factors.
    """
    consts = load_constants()
    kappa = consts['kappa']
    m_e = 0.510998 # MeV
    
    # Load modular database
    csv_path = Path(__file__).parent.parent.parent / 'v13.0' / 'data' / 'modular_invariants.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        try:
            df = pd.read_csv('v13.0/data/modular_invariants.csv')
        except FileNotFoundError:
            print("Error: modular_invariants.csv not found.")
            return
    
    candidates = [
        {"N": 24, "label": "Leech Lattice Soliton (N=24)"},
        {"N": 12, "label": "Modular Weight Soliton (N=12)"},
        {"N": 6,  "label": "Hexagonal Packing Soliton (N=6)"},
        {"N": 2,  "label": "Fundamental Binary Clot (N=2)"}
    ]
    
    print("="*80)
    print(f"{'KSAU v14.0: Dark Matter Mass Specificity Solver':^80}")
    print("="*80)
    print(f"{'N':<4} | {'Index':<6} | {'Predicted Mass':<25} | {'Nature'}")
    print("-" * 80)
    
    for c in candidates:
        row = df[df['N'] == c['N']].iloc[0]
        mu = row['Index']
        g = row['Genus']
        chi = 2 - 2*g
        
        action = kappa * (mu - chi)
        s_41 = kappa * 46
        
        # Final DM Scaling Model (Normalized by Cusp/Bulk Ratio):
        # 1/(2*kappa): The Interface Tension factor.
        # 24/mu: The Bulk-to-Surface projection density factor.
        tension_factor = 1 / (2 * kappa)
        density_factor = 24 / mu 
        
        ln_ratio = (s_41 - action) * density_factor * tension_factor
        m_dm = m_e * np.exp(ln_ratio)
        
        if m_dm > 1e12:
            val_str = f"{m_dm/1e6/1e6:>18.2e} PeV"
        elif m_dm > 1e9:
            val_str = f"{m_dm/1e6/1000:>18.2f} TeV"
        elif m_dm > 1e6:
            val_str = f"{m_dm/1e6:>18.2f} GeV"
        else:
            val_str = f"{m_dm:>18.2f} MeV"
            
        print(f"{c['N']:<4} | {mu:<6} | {val_str:<25} | {c['label']}")

    print("="*80)
    print("Note: N=2 candidate points to trans-Planckian/Primordial region.")
    print("="*80)

if __name__ == "__main__":
    dark_matter_mass_solver()
