import numpy as np
import ksau_config

def analyze_couplings():
    kappa = ksau_config.KAPPA
    
    # Load Standard Model Values
    try:
        phys = ksau_config.load_physical_constants()
        couplings = phys['couplings']
    except FileNotFoundError:
        print("Error: Could not load physical constants.")
        return

    alpha_s_mz = couplings['alpha_s_mz']
    alpha_em_0 = couplings['alpha_em_0']
    sin2theta_w = couplings['sin2theta_w']
    G = couplings['catalan_G']
    
    print("="*60)
    print("KSAU v6.0: Topological Gauge Coupling Analysis")
    print("="*60)
    print(f"Master Constant kappa = pi/24 = {kappa:.6f}")
    print("-"*60)
    
    # 1. Strong Coupling alpha_s
    # Hypothesis: alpha_s ~ kappa
    err_as = (kappa - alpha_s_mz) / alpha_s_mz
    print(f"Strong Coupling alpha_s(M_z):")
    print(f"  Observed: {alpha_s_mz:.4f}")
    print(f"  Theory (kappa): {kappa:.4f}")
    print(f"  Error: {err_as:.2%}")
    
    # 2. Fine Structure Constant alpha_em
    # Hypothesis: alpha_em ~ kappa / 18
    theory_em = kappa / 18
    err_em = (theory_em - alpha_em_0) / alpha_em_0
    print("")
    print(f"Fine Structure Constant alpha_em(0):")
    print(f"  Observed: {alpha_em_0:.6f}")
    print(f"  Theory (kappa/18): {theory_em:.6f}")
    print(f"  Error: {err_em:.2%}")
    
    # 3. Weak Mixing Angle sin^2(theta_w)
    # Hypothesis: sin^2(theta_w) ~ kappa * sqrt(pi)
    theory_w = kappa * np.sqrt(np.pi)
    err_w = (theory_w - sin2theta_w) / sin2theta_w
    print("")
    print(f"Weak Mixing Angle sin^2(theta_w):")
    print(f"  Observed: {sin2theta_w:.4f}")
    print(f"  Theory (kappa * sqrt(pi)): {theory_w:.4f}")
    print(f"  Error: {err_w:.2%}")

    # 4. The Catalan Connection
    theory_G = 7 * kappa
    err_G = (theory_G - G) / G
    print("")
    print(f"Catalan Constant G:")
    print(f"  Observed: {G:.6f}")
    print(f"  Theory (7 * kappa): {theory_G:.6f}")
    print(f"  Error: {err_G:.2%}")

    print("="*60)

if __name__ == "__main__":
    analyze_couplings()
