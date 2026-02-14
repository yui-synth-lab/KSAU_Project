import numpy as np

def search_modular_factors():
    kappa = np.pi / 24
    
    target_res = 0.5 * kappa
    print(f"Target Residue: {target_res:.6f}")
    
    candidates = [
        ("1/2 * kappa", 0.5 * kappa),
        ("1/4 * kappa", 0.25 * kappa),
        ("1/8 * kappa", 0.125 * kappa),
        ("ln(2) / 24", np.log(2) / 24),
        ("ln(phi) / 12", np.log((1+np.sqrt(5))/2) / 12),
        ("pi / 48", np.pi / 48)
    ]
    
    print("\nModular Candidates:")
    for name, val in candidates:
        print(f"{name:<25} | Value: {val:.6f} | Unit of kappa: {val/kappa:.4f}")

    print(f"\nHiggs Residue observed: {0.1321 * kappa:.6f} (Unit of kappa: 0.1321)")
    print(f"kappa / 8 = {0.125 * kappa:.6f}")
    print(f"ln(2) / 2pi = {np.log(2)/(2*np.pi):.6f}")

if __name__ == "__main__":
    search_modular_factors()
