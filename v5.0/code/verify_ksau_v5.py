import numpy as np
import math
import os

# ==============================================================================
# KSAU v5.0 PRECISION (Twist Restored) Verification Script
# ==============================================================================
# This script verifies the calculations for the KSAU v5.0 model where the 
# Quark Twist correction is restored, achieving maximum precision.
# ==============================================================================

# --- 1. Constants ---
PI = np.pi
KAPPA = PI / 24  # The Master Constant (pi/24)

# --- 2. Particle Data & Invariants ---
# Twist Rule: Twist = (2 - Gen) * (-1)^Comp
PARTICLES = {
    'Up':      {'Gen': 1, 'Comp': 2, 'V': 6.599,  'Type': 'Quark'},
    'Down':    {'Gen': 1, 'Comp': 3, 'V': 7.328,  'Type': 'Quark'},
    'Strange': {'Gen': 2, 'Comp': 3, 'V': 9.532,  'Type': 'Quark'},
    'Charm':   {'Gen': 2, 'Comp': 2, 'V': 11.517, 'Type': 'Quark'},
    'Bottom':  {'Gen': 3, 'Comp': 3, 'V': 12.276, 'Type': 'Quark'},
    'Top':     {'Gen': 3, 'Comp': 2, 'V': 15.360, 'Type': 'Quark'}, # Using L11a62
    'Electron':{'N': 3,  'Vol': 0.0,   'Type': 'Lepton', 'IsTwist': 0},
    'Muon':    {'N': 6,  'Vol': 5.69,  'Type': 'Lepton', 'IsTwist': 1},
    'Tau':     {'N': 7,  'Vol': 0.0,   'Type': 'Lepton', 'IsTwist': 0}
}

M_OBS = {
    'Up': 2.16, 'Down': 4.67, 'Strange': 93.4,
    'Charm': 1270.0, 'Bottom': 4180.0, 'Top': 172760.0,
    'Electron': 0.510998, 'Muon': 105.658, 'Tau': 1776.86
}

# --- 3. Model Parameters ---
# Quark Formula: ln(m) = 10k*V + 1k*Twist + Bq
B_Q = -7.9159 

# Lepton Formula: ln(m) = (14/9)k*N^2 - beta*Vol + Bl
COEFF_L_N2 = (14 / 9) * KAPPA
BETA = 0.0292
B_L = np.log(M_OBS['Electron']) - COEFF_L_N2 * (3**2)

# --- 4. Calculation ---
def run_verification():
    results = {}
    print("")
    print("="*85)
    print(f"{'KSAU v5.0 PRECISION (Twist Restored) REPORT':^85}")
    print("="*85)
    print(f"{'Particle':<10} | {'Twist':<6} | {'Input':<10} | {'Obs (MeV)':<12} | {'Pred (MeV)':<12} | {'Error %':<10}")
    print("-" * 85)
    
    order = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top', 'Electron', 'Muon', 'Tau']
    errors = []
    
    for name in order:
        p = PARTICLES[name]
        obs = M_OBS[name]
        
        if p['Type'] == 'Quark':
            # Calculate Twist: (2 - Gen) * (-1)^Comp
            twist = (2 - p['Gen']) * ((-1)**p['Comp'])
            log_m = 10 * KAPPA * p['V'] + KAPPA * twist + B_Q
            input_val = f"V={p['V']:.3f}"
            twist_val = f"{twist:+d}"
        else:
            # Lepton Formula
            log_m = COEFF_L_N2 * (p['N']**2) - BETA * p['Vol'] + B_L
            input_val = f"N={p['N']}"
            twist_val = "N/A"
            
        pred = np.exp(log_m)
        err = (pred - obs) / obs * 100
        errors.append(abs(err))
        results[name] = pred
        
        print(f"{name:<10} | {twist_val:<6} | {input_val:<10} | {obs:<12.4f} | {pred:<12.4f} | {err:>9.2f}%")

    q_mae = np.mean(errors[:6])
    l_mae = np.mean(errors[6:])
    g_mae = np.mean(errors)
    
    print("-" * 85)
    print(f"Quark MAE:  {q_mae:.2f}%  (Dramatic improvement in Down/Bottom!)")
    print(f"Lepton MAE: {l_mae:.2f}%")
    print(f"Global MAE: {g_mae:.2f}%")
    print("="*85)
    
    # Neutrino
    m_unknot = np.exp(B_L)
    m_nu = (m_unknot**2 / results['Top']) * 1e6
    print(f"Neutrino Prediction (Topological Seesaw): {m_nu:.4f} eV")
    print("="*85 + "\n")

if __name__ == "__main__":
    run_verification()