
import numpy as np

# Constants
G = 0.915965594
PI = np.pi
CL = -2.5033  # Lepton constant (ln(MeV))

# Neutrino Squared Mass Differences (eV^2) - PDG 2024 / NuFIT 5.2
# Normal Ordering assumed
DM2_21 = 7.42e-5
DM2_31 = 2.51e-3 

def search_hierarchy_model():
    print("="*60)
    print("  KSAU v4.1 Neutrino Hierarchy Geometric Search")
    print("="*60)
    
    # Base Suppression: 4*pi
    # ln(m_scale) = CL - 4*pi
    # m_scale_mev = exp(-2.5033 - 12.566) = exp(-15.07)
    m_scale_mev = np.exp(CL - 4 * PI)
    m_scale_ev = m_scale_mev * 1e6
    
    print(f"Base Scale (4*pi suppression): {m_scale_ev:.4f} eV")
    
    # Target Ratios from Experiment
    # Assume m1 is the base scale (or close to it)
    # Then m2 = sqrt(m1^2 + DM2_21)
    #      m3 = sqrt(m1^2 + DM2_31)
    
    m1_ref = m_scale_ev
    m2_ref = np.sqrt(m1_ref**2 + DM2_21)
    m3_ref = np.sqrt(m1_ref**2 + DM2_31)
    
    target_ln_m2_m1 = np.log(m2_ref / m1_ref)
    target_ln_m3_m1 = np.log(m3_ref / m1_ref)
    
    print(f"\nTarget Log Ratios (assuming m1 = {m1_ref:.4f} eV):")
    print(f"  ln(m2/m1): {target_ln_m2_m1:.4f}")
    print(f"  ln(m3/m1): {target_ln_m3_m1:.4f}")
    
    # Search for gamma that explains these steps
    # Hypothesis: ln(m_i) = ln(m1) + gamma * (N_i)
    # Generation steps could be N=0,1,2 or N=0,2,3 etc.
    
    gamma_candidates = {
        'pi/2': PI / 2,
        'G': G,
        'G * pi': G * PI,
        '1 / G': 1 / G,
        'ln(G)': np.log(G), # negative
        'sqrt(3)': np.sqrt(3),
        '5/3': 5/3,
        'ln(pi)': np.log(PI),
        'G + 1': G + 1
    }
    
    print("\nMatching Gamma Candidates to Target Ratios:")
    print(f"  {'Candidate':<12} {'Value':<8} {'Ratio(m3/m1) ?':<15}")
    print("-" * 50)
    
    best_match = None
    min_diff = 999.0
    
    for name, val in gamma_candidates.items():
        # Check if val fits target_ln_m3_m1 (assuming 2 steps: 0 -> 2)
        # Or 1 step (0 -> 1)
        
        # Scenario A: Step is 1 (0, 1, 2) -> m3 is 2*gamma away? No, m3 is much heavier
        # Actually mass differences are not linear in log.
        # Let's check direct match to ln(m3/m1)
        diff = abs(val - target_ln_m3_m1)
        print(f"  {name:<12} {val:.4f}   diff: {diff:.4f}")
        
        if diff < min_diff:
            min_diff = diff
            best_match = (name, val)
            
    print(f"\nBest Gamma Match for m3/m1 Gap: {best_match[0]} ({best_match[1]:.4f})")
    
    # Test Full Spectrum with Best Gamma
    # Hypothesis: Generations follow specific "Topological Charge" Q_topo
    # nu1: Q=0
    # nu2: Q=?
    # nu3: Q=1 (if gamma matches gap)
    
    gamma = best_match[1]
    
    # If gap m3/m1 is ~gamma, and m2/m1 is small ~0.02
    # This implies nu1 and nu2 are topologically very close, while nu3 is distinct.
    # This matches the "Solar" (small) vs "Atmospheric" (large) split.
    # Maybe nu1, nu2 are a "doublet" (Q=0, Q=epsilon) and nu3 is singlet (Q=1)?
    
    # Let's try to fit exact indices
    idx2 = target_ln_m2_m1 / gamma
    idx3 = target_ln_m3_m1 / gamma
    
    print(f"\nImplied Topological Indices (scale factor {best_match[0]}):")
    print(f"  nu1: 0")
    print(f"  nu2: {idx2:.4f} (Very small shift)")
    print(f"  nu3: {idx3:.4f} (~1.0?)")

if __name__ == "__main__":
    search_hierarchy_model()
