import numpy as np
import ksau_config

def search_cl():
    phys = ksau_config.load_physical_constants()
    kappa = ksau_config.KAPPA
    m_e = phys['leptons']['Electron']['mass_mev']
    cl_target = np.log(m_e) - 14 * kappa 
    print(f"Target Cl: {cl_target:.6f}")
    print("-" * 50)

    candidates = {
        "-(7/3)(1 + k)": -(7/3) * (1 + kappa),
        "-(7/3 + k)": -(7/3 + kappa),
        "-(2 + 2k)": -(2 + 2*kappa),
        "-(2 + 2k + k)": -(2 + 3*kappa),
        "-19 * k": -19 * kappa,
        "0.5 * ln(1/137.036)": 0.5 * np.log(1/137.036),
        "-(2 + 1/pi)": -(2 + 1/np.pi),
        "-(e - k)": -(np.e - kappa)
    }

    results = []
    for name, val in candidates.items():
        diff = abs(cl_target - val)
        results.append((name, val, diff))

    results.sort(key=lambda x: x[2])

    print(f"{'Candidate Formula':<20} | {'Value':<10} | {'Diff':<10}")
    print("-" * 50)
    for name, val, diff in results:
        print(f"{name:<20} | {val:<10.6f} | {diff:<10.6f}")

    print("\n[Hybrid Dimension Search]")
    hypo = -(7/3) * (1 + kappa) + kappa
    print(f"-(7/3)(1 + k) + k : {hypo:.6f} (Diff: {abs(cl_target - hypo):.6f})")
    
    hypo2 = -7/3 - (4/3)*kappa
    print(f"-7/3 - (4/3)k     : {hypo2:.6f} (Diff: {abs(cl_target - hypo2):.6f})")

if __name__ == "__main__":
    search_cl()