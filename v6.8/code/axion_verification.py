import numpy as np
import os
import sys

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def calculate_axion_mass(volume, twist=0):
    """
    Calculates the mass of a topological defect using the Unified Bulk Law.
    Formula: ln(m) = 10*kappa * V + kappa * twist + bq
    """
    consts = utils_v61.load_constants()
    kappa = consts['kappa']
    
    # Universal Bulk Parameters
    slope_q = 10 * kappa
    bq = -(7 + 7 * kappa)
    
    log_m = slope_q * volume + kappa * twist + bq
    return np.exp(log_m)

def verify_review_predictions():
    print("="*60)
    print("KSAU v6.8: Axion & Lagrangian Verification Code (SSoT Aligned)")
    print("="*60)

    # 1. The 6_3 "Geometric Axion"
    # Volume of 6_3 knot is a known invariant.
    v_6_3 = 5.693021
    m_6_3 = calculate_axion_mass(v_6_3, twist=0)
    
    print(f"[6_3 Knot Analysis]")
    print(f"Hyperbolic Volume : {v_6_3:.6f}")
    print(f"Twist (CS)        : 0.0 (Amphicheiral)")
    print(f"Predicted Mass    : {m_6_3:.4f} MeV")
    
    # 2. Decay Mode Logic (Load electron mass from SSoT)
    consts = utils_v61.load_constants()
    m_electron = consts['leptons']['Electron']['observed_mass']
    
    print(f"\n[Decay Channel Logic]")
    print(f"m(6_3) < 2 * m(e) ({m_6_3:.3f} < {2*m_electron:.3f})")
    if m_6_3 < 2 * m_electron:
        print("Status: e+ e- decay is KINEMATICALLY FORBIDDEN.")
        print("Primary Channel: 2-photon (gamma + gamma)")
    
    # 3. Lagrangian Mapping Constants
    print(f"\n[Lagrangian Mapping]")
    print(f"Vacuum Rigidity (kappa)   : {consts['kappa']:.6f}")
    print(f"Topological Tension (10k) : {10*consts['kappa']:.6f}")
    
    print("="*60)

if __name__ == "__main__":
    verify_review_predictions()
