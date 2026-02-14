
import numpy as np

def q_fact(n, omega):
    res = 1.0 + 0j
    for j in range(1, n + 1):
        res *= (1 - omega**j)
    return res

def compute_5_2_yokota(N):
    omega = np.exp(2j * np.pi / N)
    # The Kashaev invariant for 5_2 is sum_{k=0}^{N-1} (omega)_k * sum_{j=0}^k [k choose j]_omega * omega^{j(j+1)} ?
    # Let's try the formula: sum_{k=0}^{N-1} |(omega)_k|^2 * (something)
    
    total = 0j
    for k in range(N):
        # Product term P_k = prod_{j=1}^k (1-omega^j)
        pk = q_fact(k, omega)
        
        # Inner sum for 5_2 (from a known state sum for 2-bridge knots)
        inner = 0j
        for j in range(k + 1):
            # q-binomial [k choose j]_omega
            binom = q_fact(k, omega) / (q_fact(j, omega) * q_fact(k - j, omega))
            inner += binom * omega**(j*(j+1))
            
        total += pk * inner
    return total

def main():
    val = compute_5_2_yokota(3)
    print(f"5_2 Kashaev (N=3): {np.abs(val)}")

if __name__ == "__main__":
    main()
