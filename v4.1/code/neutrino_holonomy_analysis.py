
import numpy as np

# =============================================================================
# KSAU CONSTANTS (v4.1 Verified)
# =============================================================================
G = 0.915965594177219
GAMMA_Q = (10/7) * G
B_PRIME_MAG = 7 + G
CL = -2.503321  # Electron-fixed constant

# =============================================================================
# EXPERIMENTAL DATA (NuFIT 5.3, 2024 - Normal Ordering)
# =============================================================================
DM2_21 = 7.42e-5
DM2_31 = 2.514e-3

def get_masses(m1):
    m2 = np.sqrt(m1**2 + DM2_21)
    m3 = np.sqrt(m1**2 + DM2_31)
    return np.array([m1, m2, m3])

def run_comparison():
    print("=" * 80)
    print("  KSAU Neutrino Analysis: Model Comparison (Gemini vs Claude)")
    print("=" * 80)
    print(f"Constants: G={G:.6f}, Gamma_Q={GAMMA_Q:.6f}, |B'|={B_PRIME_MAG:.6f}")

    # -------------------------------------------------------------------------
    # MODEL A: Gemini Initial (Resonance at ln(m3/m2) = G)
    # -------------------------------------------------------------------------
    # Finding m1 such that ln(m3/m2) = G
    # m3^2 / m2^2 = exp(2G)
    # (m1^2 + DM2_31) / (m1^2 + DM2_21) = exp(2G)
    exp2G = np.exp(2*G)
    m1_sq_a = (DM2_31 - exp2G * DM2_21) / (exp2G - 1)
    m1_a = np.sqrt(m1_sq_a)
    m_a = get_masses(m1_a)
    r32_a = np.log(m_a[2]/m_a[1])

    print("\n[Model A] Gemini: Resonance ln(m3/m2) = G")
    print(f"  m1: {m_a[0]:.6f} eV")
    print(f"  m2: {m_a[1]:.6f} eV")
    print(f"  m3: {m_a[2]:.6f} eV")
    print(f"  Sum: {np.sum(m_a):.6f} eV")
    print(f"  ln(m3/m2) = {r32_a:.6f} (Target G={G:.6f}, Err={abs(r32_a-G)/G:.4%})")

    # -------------------------------------------------------------------------
    # MODEL B: Claude (Double-Decoupling S = 2|B'|)
    # -------------------------------------------------------------------------
    ln_m1_b_mev = CL - 2 * B_PRIME_MAG
    m1_b = np.exp(ln_m1_b_mev) * 1e6 # Convert MeV to eV
    m_b = get_masses(m1_b)
    r32_b = np.log(m_b[2]/m_b[1])

    print("\n[Model B] Claude: Double-Decoupling S = 2|B'|")
    print(f"  Suppression S: {2*B_PRIME_MAG:.6f}")
    print(f"  m1: {m_b[0]:.6f} eV")
    print(f"  m2: {m_b[1]:.6f} eV")
    print(f"  m3: {m_b[2]:.6f} eV")
    print(f"  Sum: {np.sum(m_b):.6f} eV")
    print(f"  ln(m3/m2) = {r32_b:.6f}")
    print(f"  Target Gamma_Q = {GAMMA_Q:.6f}")
    print(f"  Error to Gamma_Q: {abs(r32_b-GAMMA_Q)/GAMMA_Q:.4%}")

    # -------------------------------------------------------------------------
    # VERDICT
    # -------------------------------------------------------------------------
    print("\n--- Summary ---")
    print(f"  Model A Error (to G):       {abs(r32_a-G)/G:.4%}")
    print(f"  Model B Error (to Gamma_Q): {abs(r32_b-GAMMA_Q)/GAMMA_Q:.4%}")
    
    if abs(r32_b-GAMMA_Q) < abs(r32_a-G):
        print("\nConclusion: Claude's Model B (Gamma_Q resonance) is numerically superior.")
    else:
        print("\nConclusion: Gemini's Model A (G resonance) is numerically superior.")

if __name__ == "__main__":
    run_comparison()
