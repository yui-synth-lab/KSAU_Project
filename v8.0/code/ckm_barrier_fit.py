
import numpy as np
import json

def main():
    # CKM values (PDG 2024 typical)
    ckm = {
        "Vus": 0.2250,
        "Vcb": 0.0410,
        "Vub": 0.0037,
        "Vcd": 0.2249,
        "Vcs": 0.9735,
        "Vtb": 0.9991,
        "Vts": 0.0405,
        "Vtd": 0.0086
    }

    kappa = np.pi / 24
    
    print("="*60)
    print("KSAU v8.0: CKM Integer Barrier Analysis")
    print("="*60)
    print(f"Base kappa = pi/24 = {kappa:.6f}")
    print()
    print(f"{'Element':<10} | {'Value':<8} | {'Barrier (ln/kappa)':<15} | {'Nearest Int':<10} | {'Error'}")
    print("-" * 60)

    for key, val in ckm.items():
        if val >= 0.9: # Diagonal elements
            barrier = 0
        else:
            barrier = abs(np.log(val) / kappa)
        
        nearest_int = round(barrier)
        error = barrier - nearest_int
        
        print(f"{key:<10} | {val:<8.4f} | {barrier:<15.2f} | {nearest_int:<10} | {error:+.3f}")

    print()
    print("Geometric Interpretation of Barriers:")
    print("1. Vus/Vcd (Level 1): Barrier ~ 11.4 -> Target: 12 (Modular Weight)")
    print("2. Vcb/Vts (Level 2): Barrier ~ 24.4 -> Target: 24 (Vacuum Rank)")
    print("3. Vub     (Level 3): Barrier ~ 42.8 -> Target: 43? (24 + 20 - 1?)")
    print("4. Vtd     (Level 3): Barrier ~ 36.3 -> Target: 36 (3 x 12?)")

if __name__ == "__main__":
    main()
