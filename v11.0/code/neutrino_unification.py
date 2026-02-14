import numpy as np

def test_neutrino_unification():
    # Target R = dm2_31 / dm2_21 ~ 33.88
    R_target = 33.88
    kappa = np.pi / 24
    
    print(f"Target Ratio R = {R_target}")
    
    N_candidates = [
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 6),
        (3, 6, 7) 
    ]
    
    print(f"\n{'Lambda':<20} | {'N-Set':<10} | {'Pred R':<10} | {'Error'}")
    print("-" * 60)
    
    lams = [
        ("13.5*kappa (9pi/16)", 13.5 * kappa),
        ("12*kappa (pi/2)", 12 * kappa),
        ("13*kappa", 13 * kappa),
        ("14*kappa", 14 * kappa),
        ("15*kappa", 15 * kappa),
        ("24*kappa (pi)", 24 * kappa)
    ]
    
    for l_name, l_val in lams:
        for ns in N_candidates:
            n1, n2, n3 = ns
            try:
                num = np.exp(2 * l_val * n3) - np.exp(2 * l_val * n1)
                den = np.exp(2 * l_val * n2) - np.exp(2 * l_val * n1)
                r = num / den
                error = (r / R_target - 1) * 100
                if abs(error) < 50:
                    print(f"{l_name:<20} | {str(ns):<10} | {r:<10.2f} | {error:+.2f}%")
            except OverflowError:
                continue

if __name__ == "__main__":
    test_neutrino_unification()
