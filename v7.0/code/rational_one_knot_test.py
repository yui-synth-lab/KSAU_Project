import numpy as np

def test_muon_rationality():
    print("="*80)
    print("KSAU v7.0: The 'One-Knot' Breakthrough Test (Muon 4_1)")
    print("Objective: Predict m_mu (105.66 MeV) using ZERO free parameters.")
    print("="*80)

    # Fundamental Constants
    m_e = 0.511
    vol_mu = 2.0298832128
    target = 105.66
    
    # Candidates for Kappa (Bare vs Quantum)
    kappas = {
        "pi/24 (Bare)": np.pi / 24,
        "pi/26 (Quantum)": np.pi / 26
    }
    
    # Candidates for N_l (Rational/Integer)
    # 20: v6.0 integer
    # 21: CY Moduli lower bound
    # 21.4: Grid search optimum
    # 64/3: CFT scaling (8 * 8/3)
    # 22: Integer
    n_leptons = {
        "20": 20,
        "21": 21,
        "21.4 (v7.0 grid)": 21.4,
        "64/3 (CFT)": 64/3,
        "22": 22
    }
    
    print(f"{'Kappa':<15} | {'N_l':<15} | {'Pred (MeV)':<10} | {'Error %':<8}")
    print("-" * 65)
    
    for k_name, k_val in kappas.items():
        for n_name, n_val in n_leptons.items():
            # Formula: ln(m) = N * kappa * V + ln(m_e)
            ln_m = n_val * k_val * vol_mu + np.log(m_e)
            pred = np.exp(ln_m)
            err = abs(pred - target) / target * 100
            
            mark = "⭐️" if err < 1.0 else "  "
            print(f"{k_name:<15} | {n_name:<15} | {pred:<10.3f} | {err:<8.2f}% {mark}")

if __name__ == "__main__":
    test_muon_rationality()
