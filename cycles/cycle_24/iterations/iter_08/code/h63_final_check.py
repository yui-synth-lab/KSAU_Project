import sys
from pathlib import Path
import numpy as np
import pandas as pd
import json
from sklearn.metrics import r2_score

# SSoT Loading
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    # 1. Physical Constants
    G_ksau = consts['gravity']['G_ksau']
    M_P = 1.0 / np.sqrt(G_ksau)
    kappa = consts['mathematical_constants']['kappa']
    pi = consts['mathematical_constants']['pi']
    alpha = np.sqrt(2) * kappa
    gamma = -consts['topology_constants']['v_borromean']
    
    # 2. Unified Formula Parameters (Theoretical)
    S_vac_hbar = 14.0 * pi
    M_ksau = M_P * np.exp(-S_vac_hbar)
    
    # 3. Data Preparation
    data = []
    for name, entry in assignments.items():
        m_obs = None
        is_boson = False
        is_quark = False
        if name in consts['particle_data']['quarks']:
            m_obs = consts['particle_data']['quarks'][name]['observed_mass']
            is_quark = True
        elif name in consts['particle_data']['leptons']:
            m_obs = consts['particle_data']['leptons'][name]['observed_mass']
        elif name in consts['particle_data']['bosons']:
            m_obs = consts['particle_data']['bosons'][name]['observed_mass']
            is_boson = True
        
        if m_obs is None: continue
        data.append({
            "name": name, "m_obs": m_obs, "ln_m_obs": np.log(m_obs),
            "V": entry['volume'], "n": entry['crossing_number'],
            "c": entry['components'], "det": entry['determinant'],
            "s": entry['signature'], "is_boson": is_boson, "is_quark": is_quark
        })
    df = pd.DataFrame(data)
    
    # 4. Refined Unified Formula
    # ln(m/MeV) = Phi + offset
    # Phi = eta * kappa * V + alpha * T + gamma
    # eta = 18/c for fermions, eta = 18/(2c) for bosons
    # T = ln(det) + s - n - (pi/alpha)*ln(c)
    
    df['eta'] = np.where(df['is_boson'], 18.0 / (2 * df['c']), 18.0 / df['c'])
    
    pi_alpha = pi / alpha
    df['T'] = np.log(df['det']) + df['s'] - df['n'] - pi_alpha * np.log(df['c'])
    
    # Theoretical Shift (based on SSoT H42)
    # Bosons: + pi*sqrt(3)
    # Quarks: - pi*sqrt(3)? 
    # Let's test shifts
    shift_boson = pi * np.sqrt(3)
    shift_quark = -pi * np.sqrt(3)
    
    df['shift'] = 0.0
    df.loc[df['is_boson'], 'shift'] = shift_boson
    df.loc[df['is_quark'], 'shift'] = shift_quark
    
    df['base'] = df['eta'] * kappa * df['V'] + alpha * df['T'] + gamma + df['shift']
    
    # Unified Offset (The 1 free parameter)
    # If the theory is perfect, this should be ln(M_ksau/MeV)
    # ln(M_ksau) approx 6.87
    offset_val = np.log(M_ksau)
    
    # But Roadmap allows 1 free parameter, so let's optimize it to minimize MAE
    # or just use the theoretical one and see error.
    
    def evaluate(off):
        ln_pred = df['base'] + off
        return np.mean(np.abs(df['ln_m_obs'] - ln_pred))

    best_off = np.mean(df['ln_m_obs'] - df['base'])
    
    df['ln_m_pred'] = df['base'] + best_off
    df['m_pred'] = np.exp(df['ln_m_pred'])
    df['err_pct'] = (df['m_pred'] - df['m_obs']) / df['m_obs'] * 100
    
    r2 = r2_score(df['ln_m_obs'], df['ln_m_pred'])
    avg_err_abs = np.mean(np.abs(df['err_pct']))
    
    print(f"H63 Unified Model (Offset={best_off:.4f}, Theo_Scale={offset_val:.4f})")
    print(f"R2: {r2:.6f}, Avg Error: {avg_err_abs:.2f}%")
    print("-" * 80)
    for _, row in df.iterrows():
        print(f"{row['name']:10} | Obs: {row['m_obs']:10.2f} | Pred: {row['m_pred']:10.2f} | Err: {row['err_pct']:7.2f}%")

if __name__ == "__main__":
    main()
