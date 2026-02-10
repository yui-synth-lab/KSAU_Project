import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add v6.1 code to path for utils_v61
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def verify_g_v6_unified():
    print("="*60)
    print("KSAU v6.7: Verification of G (Refactored using utils_v61)")
    print("="*60)
    
    # 1. Load Constants from Central JSON
    consts = utils_v61.load_constants()
    
    kappa = consts['kappa']
    V_borr = consts['v_borromean']
    
    # 2. Universal Mass Law Parameters
    A = 10 * kappa
    C_off = -(7 + 7 * kappa)
    
    # 3. Planck Scale Parameters
    v_factor = consts['gravity']['v_planck_factor']
    V_P = v_factor * V_borr
    
    # 4. Correction Factors
    k_c = consts['gravity']['k_c']
    delta = consts['gravity']['delta']
    
    # 5. Calculation
    ln_MP_raw = A * V_P + C_off
    ln_MP_corr = ln_MP_raw + k_c - delta
    MP_gev = np.exp(ln_MP_corr) / 1000.0
    
    # 6. Gravitational Constant G
    G_nat = 1.0 / (MP_gev**2)
    G_exp = consts['gravity']['G_newton_exp']
    
    print(f"[Constants Used]")
    print(f"  kappa: {kappa:.6f}")
    print(f"  V_borr: {V_borr:.6f}")
    print(f"  V_P Factor: {v_factor}")
    print(f"  k_c (Variance): {k_c:.6f}")
    print(f"  delta (Dissipation): {delta:.6f}")
    
    print("\n[Derivation Results]")
    print(f"  Planck Volume V_P: {V_P:.4f}")
    print(f"  Planck Mass (M_P'): {MP_gev/1e19:.4f} x 10^19 GeV")
    print(f"  Derived G: {G_nat:.4e} GeV^-2")
    print(f"  Experimental G: {G_exp:.4e} GeV^-2")
    
    error = abs(G_nat - G_exp) / G_exp * 100
    print(f"  Relative Error: {error:.4f}%")
    print(f"  Precision Score: {100 - error:.4f}%")
    
    # 7. Visualization
    v_range = np.linspace(0, 60, 500)
    ln_m_particle = A * v_range + C_off
    ln_m_bh = 0.5 * np.log(v_range + 1e-9) + (ln_MP_corr - 0.5 * np.log(V_P))
    
    os.makedirs('v6.7/figures', exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.plot(v_range, ln_m_particle, 'b-', label=r'Universal Mass Law ($10\kappa$)')
    plt.plot(v_range, ln_m_bh, 'g--', label='Holographic Bound')
    plt.axvline(V_P, color='red', linestyle=':', label=f'Planck Volume $V_P$')
    plt.scatter([V_P], [ln_MP_corr], color='black', zorder=5, label='Planck Point')
    
    plt.title(r'KSAU v6.7: Gravity Derivation (Refactored)')
    plt.xlabel('Topological Volume (V)')
    plt.ylabel('ln(Mass) [MeV]')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('v6.7/figures/g_derivation_v6_unified.png')
    print("\nVisualization saved to: v6.7/figures/g_derivation_v6_unified.png")

if __name__ == "__main__":
    verify_g_v6_unified()
