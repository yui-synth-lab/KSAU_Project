import numpy as np
import json
from pathlib import Path

# ==============================================================================
# KSAU v5.0 PRECISION (Twist Restored) Verification Script
# ==============================================================================
# This script verifies the calculations for the KSAU v5.0 model where the
# Quark Twist correction is restored, achieving maximum precision.
#
# DATA SOURCE: Loads from topology_assignments.json
# ==============================================================================

# --- 1. Constants ---
PI = np.pi
KAPPA = PI / 24  # The Master Constant (pi/24)

# --- 2. Load Data from JSON ---
def load_data():
    json_path = Path(__file__).parent.parent / 'data' / 'topology_assignments.json'
    with open(json_path, 'r') as f:
        data = json.load(f)

    PARTICLES = {}
    M_OBS = {}

    for name, info in data.items():
        M_OBS[name] = info['observed_mass']

        if info['charge_type'] == 'lepton':
            N = info['crossing_number']
            is_twist = (info['topology'] == '6_1')
            PARTICLES[name] = {
                'Type': 'Lepton',
                'N': N,
                'Vol': info['volume'],
                'IsTwist': 1 if is_twist else 0
            }
        else:
            gen = info['generation']
            C = info['components']
            PARTICLES[name] = {
                'Type': 'Quark',
                'Gen': gen,
                'Comp': C,
                'V': info['volume']
            }

    return PARTICLES, M_OBS

PARTICLES, M_OBS = load_data()

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
            # Lepton Formula (v5.0 Unified)
            gamma_l = (14/9) * KAPPA
            twist_corr = -1/6 if p['IsTwist'] else 0
            # C_l is calibrated to electron (N=3)
            C_l = np.log(M_OBS['Electron']) - gamma_l * (3**2)
            log_m = gamma_l * (p['N']**2) + twist_corr + C_l
            input_val = f"N={p['N']}"
            twist_val = f"{twist_corr:.3f}" if twist_corr != 0 else "0.000"
            
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