
import numpy as np

G = 0.915965594
PI = np.pi

# Experimental Δm^2 (PDG 2024)
DM2_21 = 7.41e-5
DM2_31 = 2.437e-3

def analyze_detailed_ratios():
    print("=" * 80)
    print("  Detailed Neutrino Resonance: The Holonomy Model")
    print("=" * 80)
    
    # We found resonance at m3/m2 = e^G. 
    # Let's see what m1/m2 looks like at that point.
    m2 = np.sqrt((DM2_31 - DM2_21) / (np.exp(2*G) - 1))
    m3 = m2 * np.exp(G)
    m1 = np.sqrt(m2**2 - DM2_21)
    
    print(f"Resonance Point (ln(m3/m2) = G):")
    print(f"  m1 = {m1:.6f} eV")
    print(f"  m2 = {m2:.6f} eV")
    print(f"  m3 = {m3:.6f} eV")
    print(f"  Sum(m) = {m1+m2+m3:.6f} eV (Exp limit: < 0.12 eV)")
    
    print("\nCheck Ratio ln(m2/m1):")
    r21 = np.log(m2/m1)
    print(f"  ln(m2/m1) = {r21:.6f}")
    print(f"  Ratio to G: {r21/G:.6f}")
    print(f"  Ratio to G/(2*pi): {r21/(G/(2*PI)):.6f}")
    
    # Is ln(m2/m1) related to 1/10 (Dimension)?
    print(f"  Ratio to 1/10: {r21/0.1:.4f}")
    
    print("\n--- Theoretical Interpretation ---")
    print("If masses follow ln(m_i) = A + k_i * G:")
    print(f"  k3 - k2 = 1.0 (Exactly G)")
    print(f"  k2 - k1 = {r21/G:.4f} (Approx 1/10 G?)")
    
    # Test: if k2-k1 = 1/10, then ln(m2/m1) = 0.09159
    m1_pred = m2 / np.exp(G/10)
    dm2_21_pred = m2**2 - m1_pred**2
    print(f"\nPrediction check if ln(m2/m1) = G/10:")
    print(f"  Observed DM2_21: {DM2_21:.2e}")
    print(f"  Predicted DM2_21: {dm2_21_pred:.2e}")
    print(f"  Error: {abs(dm2_21_pred - DM2_21)/DM2_21*100:.2f}%")

if __name__ == "__main__":
    analyze_detailed_ratios()
