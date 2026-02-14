import numpy as np

def analyze_neutrino_ratio():
    # Experimental values (NuFIT 5.2)
    dm2_21 = 7.42e-5
    dm2_31 = 2.514e-3
    R_obs = dm2_31 / dm2_21
    print(f"Observed Ratio R = {R_obs:.4f}")

    kappa = np.pi / 24
    
    print(f"\n{'Lambda Candidate':<20} | {'N1, N2, N3':<12} | {'Pred Ratio':<10} | {'Error'}")
    print("-" * 65)
    
    candidates = [
        ("9*pi/16", 9*np.pi/16, (3, 6, 7)),
        ("12*kappa (pi/2)", np.pi/2, (3, 4, 6)),
        ("13*kappa", 13*kappa, (3, 4, 6)),
        ("13*kappa", 13*kappa, (3, 4, 10)), # If tau-nu follows quark N=10?
        ("pi", np.pi, (1, 2, 3)),
        ("1.701 (Approx)", 1.701, (3, 4, 6))
    ]
    
    for name, lam, (n1, n2, n3) in candidates:
        try:
            num = np.exp(2 * lam * n3) - np.exp(2 * lam * n1)
            den = np.exp(2 * lam * n2) - np.exp(2 * lam * n1)
            R_pred = num / den
            error = (R_pred / R_obs - 1) * 100
            print(f"{name:<20} | {str((n1,n2,n3)):<12} | {R_pred:<10.2f} | {error:+.2f}%")
        except OverflowError:
            print(f"{name:<20} | {str((n1,n2,n3)):<12} | Overflow   | N/A")

    # Manual search for best lambda for N=(3,4,6)
    # R(lam) = (exp(2*lam*6) - exp(2*lam*3)) / (exp(2*lam*4) - exp(2*lam*3))
    print("\nManual scanning for N=(3,4,6):")
    for l_val in np.arange(1.6, 1.8, 0.01):
        num = np.exp(2 * l_val * 6) - np.exp(2 * l_val * 3)
        den = np.exp(2 * l_val * 4) - np.exp(2 * l_val * 3)
        R_val = num / den
        if abs(R_val - R_obs) < 5.0:
            print(f"lambda = {l_val:.3f} -> R = {R_val:.2f} (Error: {(R_val/R_obs-1)*100:+.2f}%)")

if __name__ == "__main__":
    analyze_neutrino_ratio()
