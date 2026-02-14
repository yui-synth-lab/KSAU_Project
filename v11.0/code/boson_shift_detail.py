import numpy as np
import json
import os

def analyze_boson_shifts():
    kappa = np.pi / 24
    
    # EXPERIMENTAL masses (PDG 2024 / Standard values)
    # These are INDEPENDENT of KSAU fits.
    m_w_exp = 80377.0  
    m_z_exp = 91187.0
    m_h_exp = 125100.0
    m_e_exp = 0.511
    
    # 1. Weinberg Angle Identity Check (Independent of shifts)
    cos2theta_exp = (m_w_exp / m_z_exp)**2 # ~ 0.7770
    cos2theta_ksau = np.exp(-2 * kappa)    # ~ 0.7697
    
    error_theta = (cos2theta_ksau / cos2theta_exp - 1) * 100
    
    print("--- Electroweak Mixing Verification (Independent) ---")
    print(f"Experimental cos^2 theta_w: {cos2theta_exp:.4f}")
    print(f"KSAU Prediction exp(-2*kappa): {cos2theta_ksau:.4f}")
    print(f"Prediction Error: {error_theta:+.2f}%")
    
    # 2. W/Z Mass Splitting Check
    ln_ratio_exp = np.log(m_w_exp / m_z_exp)
    ln_ratio_ksau = -kappa
    
    error_ratio = (ln_ratio_ksau / ln_ratio_exp - 1) * 100
    
    print("\n--- W/Z Mass Splitting ---")
    print(f"Experimental ln(mw/mz): {ln_ratio_exp:.4f}")
    print(f"KSAU Prediction -kappa: {ln_ratio_ksau:.4f}")
    print(f"Prediction Error: {error_ratio:+.2f}%")

    # 3. Residual Shift Analysis (Non-circular)
    # Recovering what 'n' must be from experimental values
    # ln(m_exp) = N*kappa*V + ln(me) - n*kappa
    # => n = (N*kappa*V + ln(me) - ln(m_exp)) / kappa
    
    vols = {
        "W": 14.6554,
        "Z": 15.0276,
        "Higgs": 15.8207
    }
    
    print("\n--- Required Shifts from Experimental Masses ---")
    print(f"{'Particle':<8} | {'ln(m)_exp':<10} | {'Req. Shift n':<10}")
    print("-" * 40)
    
    for name, v in vols.items():
        m_exp = locals()[f"m_{name[0].lower()}_exp"]
        lnm_exp = np.log(m_exp)
        ln_me = np.log(m_e_exp)
        n_req = (6 * kappa * v + ln_me - lnm_exp) / kappa
        print(f"{name:<8} | {lnm_exp:<10.4f} | {n_req:.4f}")

if __name__ == "__main__":
    analyze_boson_shifts()
