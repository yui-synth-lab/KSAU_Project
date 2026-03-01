
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# v4.1 Constants
G = 0.915965594
CL = -2.5033  # Lepton Constant (from e, mu, tau fit)
BETA_G = 0.4924 # Genus factor (from Claude's best fit)

# Experimental Neutrino Bounds (eV)
# Reference: PDG 2024 / Cosmology (Sum < 0.12 eV)
NEUTRINO_BOUNDS = {
    'nu_e': 0.8,      # KATRIN upper limit
    'nu_sum': 0.12,   # Cosmological sum limit
    'delta_m2_21': 7.53e-5, # eV^2
    'delta_m2_32': 2.45e-3  # eV^2
}

def analyze_neutrino_gap():
    print("=" * 60)
    print("  KSAU v4.1 Neutrino Preliminary Analysis")
    print("=" * 60)

    # 1. Prediction using Charged Lepton Formula (N=0, g=0)
    # ln(m in MeV) = (2/9)G * N^2 + CL + BETA_G * (g - 1)
    ln_m_nu_mev = 0 + CL + BETA_G * (0 - 1)
    m_nu_mev = np.exp(ln_m_nu_mev)
    m_nu_ev = m_nu_mev * 1e6
    
    print(f"Standard Lepton Formula Prediction (N=0, g=0):")
    print(f"  Mass: {m_nu_ev:.2f} eV")
    print(f"  Experimental Target: < 0.1 eV")
    
    gap_factor = m_nu_ev / 0.1
    print(f"  Gap Factor: ~{gap_factor:.1e}")
    print(f"  Log Gap: {np.log(gap_factor):.4f}")

    # 2. Search for Geometric Dampening Factors
    # Could the gap be a power of G, pi, or 1/7?
    print("\nPotential Geometric Dampening Factors for Log-Gap:")
    candidates = {
        '10 * G': 10 * G,
        '4 * pi': 4 * np.pi,
        '7 / G': 7 / G,
        '2 * pi * G': 2 * np.pi * G,
        'G * (7+G)': G * (7+G)
    }
    
    log_gap = np.log(gap_factor)
    for name, val in candidates.items():
        diff = abs(val - log_gap)
        print(f"  {name:<15}: {val:.4f} (diff to log-gap: {diff:.4f})")

    # 3. Neutrino Generation Hypothesis
    # If nu_e, nu_mu, nu_tau have different masses, they need different g or N.
    # What if they are related to "Virtual Knots" or "Smallest Hyperbolic"?
    # Minimal Hyperbolic Volume is ~0.94 (Weeks manifold). 
    # But Neutrinos should be lighter than Electrons.
    
    print("\nNeutrino Hierarchy Constraints (Normal Ordering):")
    # m1^2, m2^2 = m1^2 + 7.5e-5, m3^2 = m1^2 + 2.5e-3
    m1 = 0.01 # eV (assumption)
    m2 = np.sqrt(m1**2 + NEUTRINO_BOUNDS['delta_m2_21'])
    m3 = np.sqrt(m2**2 + NEUTRINO_BOUNDS['delta_m2_32'])
    
    print(f"  Assumed m1: {m1:.4f} eV")
    print(f"  Calculated m2: {m2:.4f} eV")
    print(f"  Calculated m3: {m3:.4f} eV")
    print(f"  ln(m3/m1): {np.log(m3/m1):.4f}")
    
    # Note: ln(m3/m1) ~ 1.6-1.7. 
    # Compare with Lepton Genus spacing: BETA_G * Delta_g = 0.49 * 1 = 0.49.
    # Spacing is different. Neutrinos might follow a different Genus-scaling (e.g. ln(m) proportional to 1/g?)

if __name__ == "__main__":
    analyze_neutrino_gap()
