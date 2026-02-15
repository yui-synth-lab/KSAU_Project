"""
Script purpose: Test geometric candidates for the universal intercept X = ln(M_Pl/m_e)
Dependencies: physical_constants.json (SSoT)
SSoT sources: physical_constants.json
Author: Gemini (Simulation Kernel), modified by Claude (Theoretical Auditor)
Date: 2026-02-15
"""
import json
from pathlib import Path
import numpy as np

def load_ssot():
    data_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(data_path, "r") as f:
        return json.load(f)

def test_electron_geometric_origin():
    phys = load_ssot()
    m_e_mev = phys['leptons']['Electron']['observed_mass']  # MeV
    m_planck_mev = phys['gravity']['m_planck_gev'] * 1e3  # GeV -> MeV

    X_obs = np.log(m_planck_mev / m_e_mev)
    print(f"Observed X = {X_obs:.6f}")
    print(f"  (m_e = {m_e_mev} MeV, M_Pl = {m_planck_mev:.6e} MeV from SSoT)")

    # Hypothesis 1: X = 16*pi + 4/pi
    X_pred = 16 * np.pi + 4 / np.pi
    print(f"\nHypothesis 1: X = 16*pi + 4/pi = {X_pred:.6f}")
    error = (X_pred / X_obs - 1) * 100
    print(f"Error in exponent: {error:+.4f}%")
    me_pred = m_planck_mev * np.exp(-X_pred)
    print(f"Predicted m_e: {me_pred:.6e} MeV")
    print(f"Mass Error: {(me_pred/m_e_mev - 1)*100:+.4f}%")

    # Hypothesis 2: X = 16.4*pi = 82*pi/5
    X_pred2 = 16.4 * np.pi
    print(f"\nHypothesis 2: X = 82/5 * pi = {X_pred2:.6f}")
    me_pred2 = m_planck_mev * np.exp(-X_pred2)
    print(f"Mass Error: {(me_pred2/m_e_mev - 1)*100:+.4f}%")

    # Hypothesis 3: X = pi*(16 + 24/60) — E8xE8 rank + Leech/A5
    X_pred3 = np.pi * (16 + 24/60)
    print(f"\nHypothesis 3: X = pi*(16 + 24/60) = {X_pred3:.6f}")
    me_pred3 = m_planck_mev * np.exp(-X_pred3)
    print(f"Mass Error: {(me_pred3/m_e_mev - 1)*100:+.4f}%")
    print(f"Note: Hypotheses 2 and 3 are algebraically identical (16.4 = 16 + 24/60).")

if __name__ == "__main__":
    test_electron_geometric_origin()
