
import numpy as np

def compute_kashaev(knot_name, N):
    omega = np.exp(2j * np.pi / N)
    
    # Precompute |1 - omega^j|^2
    vals = []
    for j in range(N):
        val = np.abs(1 - omega**j)**2
        vals.append(val)
    
    # Precompute products P_k = prod_{j=1}^k |1 - omega^j|^2
    P = [1.0]
    curr_p = 1.0
    for k in range(1, N):
        curr_p *= vals[k]
        P.append(curr_p)
        
    if knot_name == "4_1":
        # Formula: sum_{k=0}^{N-1} P_k
        return np.sum(P)
    
    elif knot_name == "6_1":
        # Formula (Hypothesis): sum_{k=0}^{N-1} a_2(k) * P_k
        # where a_2(k) = sum_{n=0}^k P_n
        a2 = np.cumsum(P)
        return np.sum(a2 * P)

    elif knot_name == "8_1":
        # Formula (Hypothesis): sum_{k=0}^{N-1} a_3(k) * P_k
        # where a_3(k) = sum_{n=0}^k a_2(n) * P_n
        a2 = np.cumsum(P)
        a3 = np.cumsum(a2 * P)
        return np.sum(a3 * P)

    return None

def main():
    # Vol(4_1) = 2.0298832128
    # Vol(6_1) = 3.1639632288
    # Vol(8_1) = 4.0597664256
    
    volumes = {
        "4_1": 2.0298832128,
        "6_1": 3.1639632288,
        "8_1": 4.0597664256
    }
    
    print(f"{'Knot':<5} | {'N':<3} | {'Kashaev':<15} | {'(2pi/N)ln|K|':<15} | {'Vol':<10} | {'Error':<7}")
    print("-" * 75)
    
    for knot in ["4_1", "6_1", "8_1"]:
        vol = volumes[knot]
        for n in [3, 10, 50, 100]:
            val = compute_kashaev(knot, n)
            if val is None: continue
            
            res = (2 * np.pi / n) * np.log(np.abs(val))
            error = (res - vol) / vol * 100
            print(f"{knot:<5} | {n:<3} | {np.abs(val):<15.4f} | {res:<15.6f} | {vol:<10.6f} | {error:>6.2f}%")
        print("-" * 75)

    # Special check for tau mass prediction
    # ln(m_tau / m_e) = 8.154
    k_6_1_3 = compute_kashaev("6_1", 3)
    pred_tau = (2 * np.pi / 3) * np.log(np.abs(k_6_1_3))
    actual_tau = 8.1542
    
    print("\nTau Mass Check (6_1, N=3):")
    print(f"Kashaev invariant <6_1>_3 = {np.abs(k_6_1_3)}")
    print(f"(2pi/3) * ln|<6_1>_3| = {pred_tau:.4f}")
    print(f"ln(m_tau / m_e) = {actual_tau:.4f}")
    print(f"Difference: {pred_tau - actual_tau:.4f} ({(pred_tau - actual_tau)/actual_tau*100:.2f}%)")

if __name__ == "__main__":
    main()
