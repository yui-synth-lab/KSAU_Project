import numpy as np

def analyze_residue():
    kappa = np.pi / 24
    me = 0.511e6 # eV
    mu0_target = 2.14e-7 # eV
    
    mu0_base = me * np.exp(-216 * kappa)
    print(f"Base mu_0 (B=216): {mu0_base:.4e} eV")
    print(f"Target mu_0: {mu0_target:.4e} eV")
    
    residue_val = -np.log(mu0_target / mu0_base)
    print(f"\nRequired Residue (log scale): {residue_val:.4f}")
    
    residue_kappa = residue_val / kappa
    print(f"Residue in units of kappa: {residue_kappa:.4f}")
    
    print("\nTesting geometric candidates for Residue factor:")
    candidates = [
        ("sqrt(3)", np.sqrt(3)),
        ("phi", (1 + np.sqrt(5)) / 2),
        ("zeta(3)", 1.202),
        ("Euler-Mascheroni gamma", 0.577)
    ]
    
    for name, val in candidates:
        pred = mu0_base * np.exp(-val * kappa)
        error = (pred / mu0_target - 1) * 100
        print(f"{name:<25} | Pred: {pred:.4e} | Error: {error:+.2f}%")

    final_theory_kappa = 216 + np.sqrt(3)
    final_pred = me * np.exp(-final_theory_kappa * kappa)
    print(f"\nFINAL HYPOTHESIS: mu_0 = m_e * exp(-(216 + sqrt(3)) * kappa)")
    print(f"Result: {final_pred:.4e} eV (Error: {(final_pred/mu0_target-1)*100:+.2f}%)")

if __name__ == "__main__":
    analyze_residue()
