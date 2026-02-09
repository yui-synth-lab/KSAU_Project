import numpy as np
import pandas as pd
import utils_v61

def verify_pmns_mass():
    print("="*60)
    print("KSAU v6.1: PMNS Mass Hierarchy Verification")
    print("="*60)
    
    # 1. Load Data
    knots, _ = utils_v61.load_data()
    
    # 2. Target Triplet
    triplet_names = ['4_1', '7_2', '8_9']
    
    print("Retrieving Triplet Data...")
    triplet_data = []
    for name in triplet_names:
        row = knots[knots['name'] == name].iloc[0]
        triplet_data.append({
            'name': name,
            'vol': float(row['volume'])
        })
        print(f"  {name}: Vol = {float(row['volume']):.4f}")
        
    # 3. Define Mass Scaling Law (Paper II)
    # The prompt says: lambda = 9*pi / 16 (~ 1.767)
    # Assumption: Mass m ~ exp( - lambda * V ) or similar?
    # Or Delta m^2 ~ ...
    # KSAU usually implies m ~ exp(kV). 
    # Let's test the hypothesis: m_i = m_0 * exp( - lambda * V_i ) (Inverted for Boundary?)
    # Or m_i = m_0 * exp( lambda * V_i )?
    # Neutrinos are very light, so maybe suppression?
    # If quarks are exp(+kV), maybe neutrinos are exp(-kV) (Boundary vs Bulk duality).
    
    lam = (9 * np.pi) / 16
    print(f"\nScaling Constant lambda = 9pi/16 = {lam:.4f}")
    
    # Let's calculate relative masses assuming m ~ exp(-lam * V)
    # We don't know m_0, but we can check the ratio of Delta m^2.
    
    # m1, m2, m3
    # Delta m21^2 = m2^2 - m1^2
    # Delta m32^2 = m3^2 - m2^2 (approx Delta m31^2)
    # Ratio R = Delta m32^2 / Delta m21^2 ~ (2.5e-3) / (7.5e-5) ~ 33
    
    v1 = triplet_data[0]['vol'] # 4_1
    v2 = triplet_data[1]['vol'] # 7_2
    v3 = triplet_data[2]['vol'] # 8_9
    
    # Try Model A: m = exp(-lam * V)
    print("\n[Testing Model A: m ~ exp(-lambda * V)]")
    m1_a = np.exp(-lam * v1)
    m2_a = np.exp(-lam * v2)
    m3_a = np.exp(-lam * v3)
    
    print(f"  Unscaled Masses (rel): m1={m1_a:.2e}, m2={m2_a:.2e}, m3={m3_a:.2e}")
    # This produces m1 > m2 > m3 if V1 < V2 < V3. (4_1=2.02, 7_2=3.33, 8_9=7.58)
    # So m1 is heaviest? That contradicts Normal Hierarchy (m1 < m2 < m3).
    # It fits Inverted Hierarchy? (m3 << m1 ~ m2).
    # Let's check Dm.
    dm21_a = abs(m2_a**2 - m1_a**2)
    dm32_a = abs(m3_a**2 - m2_a**2)
    ratio_a = dm32_a / dm21_a if dm21_a > 0 else 0
    print(f"  Ratio (Dm32 / Dm21): {ratio_a:.4f} (Target ~ 33)")
    
    # Try Model B: m = exp(lambda * V) -> Normal Hierarchy?
    print("\n[Testing Model B: m ~ exp(lambda * V)]")
    # Actually, quarks have m ~ exp(k * V).
    # If we use lambda = 9pi/16 ~ 1.7
    # m1 = exp(1.7 * 2.02) ~ 30
    # m2 = exp(1.7 * 3.33) ~ 280
    # m3 = exp(1.7 * 7.58) ~ 600000
    # The gaps are huge.
    # m3^2 / m2^2 ~ (6e5 / 2.8e2)^2 ~ 4e6. Too big.
    
    # Maybe the formula is linear in V for log m? Yes.
    # Maybe lambda is smaller?
    # Or maybe lambda applies to Delta m?
    
    # Let's try to find if there exists a scale M0 such that
    # Dm21 = 7.5e-5 eV2
    # Dm32 = 2.5e-3 eV2
    
    # Let's assume m ~ V^lambda (Power Law)?
    print("\n[Testing Model C: m ~ V^lambda]")
    m1_c = v1 ** lam
    m2_c = v2 ** lam
    m3_c = v3 ** lam
    print(f"  Unscaled Masses: m1={m1_c:.2f}, m2={m2_c:.2f}, m3={m3_c:.2f}")
    dm21_c = abs(m2_c**2 - m1_c**2)
    dm32_c = abs(m3_c**2 - m2_c**2)
    ratio_c = dm32_c / dm21_c if dm21_c > 0 else 0
    print(f"  Ratio: {ratio_c:.4f} (Target ~ 33)")
    
    # Try Model D: "Paper II" Special Scaling?
    # Maybe m ~ exp(- V / lambda)?
    # lambda = 1.77. 1/lambda = 0.56.
    print("\n[Testing Model D: m ~ exp(-V / lambda)]")
    m1_d = np.exp(-v1 / lam)
    m2_d = np.exp(-v2 / lam)
    m3_d = np.exp(-v3 / lam)
    
    dm21_d = abs(m2_d**2 - m1_d**2)
    dm32_d = abs(m3_d**2 - m2_d**2)
    ratio_d = dm32_d / dm21_d if dm21_d > 0 else 0
    print(f"  Ratio: {ratio_d:.4f} (Target ~ 33)")
    
    # Report best fit
    print("\nConclusion:")
    if abs(ratio_a - 33) < abs(ratio_c - 33):
        print(f"  Model A (Exponential Suppression) is closest. Ratio={ratio_a:.2f}")
    else:
        print(f"  Model C (Power Law) is closest. Ratio={ratio_c:.2f}")

if __name__ == "__main__":
    verify_pmns_mass()
