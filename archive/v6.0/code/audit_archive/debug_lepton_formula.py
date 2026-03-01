"""
Debug the lepton mass prediction formula.

The formula is:
  ln(m) = slope * N^2 + intercept

But we need to understand what intercept value is being used.
"""

import numpy as np
import json
from pathlib import Path
import ksau_config

phys = ksau_config.load_physical_constants()
coeffs = ksau_config.get_kappa_coeffs()

G = phys['G_catalan']
slope_l = (2/9) * G
cl = coeffs['lepton_intercept']

print("LEPTON FORMULA DEBUGGING")
print("="*60)
print(f"G_catalan: {G}")
print(f"Lepton slope: (2/9) * G = {slope_l:.10f}")
print(f"Lepton intercept (CL): {cl:.10f}")
print(f"CL = κ - (7/3)(1 + κ) where κ = {ksau_config.KAPPA:.10f}")

print("\nFORWARD FORMULA: ln(m) = slope * N^2 + CL")
print("-"*60)

leptons_data = [
    ('Electron', 0.511, 3),
    ('Muon', 105.66, 6),
    ('Tau', 1776.86, 7)
]

for l_name, obs_mass, n in leptons_data:
    ln_m = np.log(obs_mass)
    predicted_n2 = (ln_m - cl) / slope_l
    predicted_n = np.sqrt(predicted_n2)
    
    # Verify: go back
    ln_m_back = slope_l * (n ** 2) + cl
    m_back = np.exp(ln_m_back)
    
    print(f"\n{l_name}:")
    print(f"  Observed m:        {obs_mass:.3f} MeV, ln(m) = {ln_m:.6f}")
    print(f"  Observed N:        {n}")
    print(f"  Predicted N^2:     (ln(m) - CL) / slope = {predicted_n2:.4f}")
    print(f"  Predicted N:       {predicted_n:.4f}")
    print(f"  Recalculated ln(m): slope * N^2 + CL = {ln_m_back:.6f}")
    print(f"  Recalculated m:    {m_back:.3f} MeV")
    print(f"  Error:             {abs(m_back - obs_mass) / obs_mass * 100:.2f}%")
