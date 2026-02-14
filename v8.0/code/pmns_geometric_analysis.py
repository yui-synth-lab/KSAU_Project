
import numpy as np
import json

def main():
    # PMNS matrix typical magnitudes (from global fits)
    # Rows: e, mu, tau | Cols: nu1, nu2, nu3
    # Approximated from sin^2(theta) values in physical_constants.json
    # theta12 ~ 33.4, theta23 ~ 49.0, theta13 ~ 8.6
    
    s12 = np.sin(np.radians(33.4))
    c12 = np.cos(np.radians(33.4))
    s23 = np.sin(np.radians(49.0))
    c23 = np.cos(np.radians(49.0))
    s13 = np.sin(np.radians(8.6))
    c13 = np.cos(np.radians(8.6))

    # Standard PMNS magnitudes (ignoring CP phase for now)
    Ue1 = c12 * c13
    Ue2 = s12 * c13
    Ue3 = s13
    Umu3 = s23 * c13
    Utau3 = c23 * c13

    pmns = {
        "Ue2": Ue2,   # Solar mixing
        "Umu3": Umu3, # Atmospheric mixing
        "Ue3": Ue3    # Reactor mixing
    }

    kappa = np.pi / 24
    
    print("="*60)
    print("KSAU v8.0: PMNS (Neutrino) Geometric Analysis")
    print("="*60)
    print(f"Base kappa = pi/24 = {kappa:.6f}")
    print()
    print(f"{'Element':<10} | {'Value':<8} | {'Barrier (ln/kappa)':<15} | {'Nearest Int':<10}")
    print("-" * 60)

    for key, val in pmns.items():
        barrier = abs(np.log(val) / kappa)
        nearest_int = round(barrier)
        
        print(f"{key:<10} | {val:<8.4f} | {barrier:<15.2f} | {nearest_int:<10}")

    print()
    print("Comparison with CKM:")
    print("CKM Barriers: 12, 24, 36 (Multiples of 12)")
    print("PMNS Barriers: Are they related to the Spacetime Dimension (4)?")

if __name__ == "__main__":
    main()
