
import numpy as np

def q_fact(n, omega):
    res = 1.0 + 0j
    for j in range(1, n + 1):
        res *= (1 - omega**j)
    return res

def q_symbol(a_pow, n, omega):
    res = 1.0 + 0j
    for j in range(n):
        res *= (1 - omega**(a_pow + j))
    return res

def compute_5_2_kashaev(N):
    omega = np.exp(2j * np.pi / N)
    # J_N(5_2; q) = sum_{k=0}^{N-1} (q^{N+1})_k (q^{N-1})_k * (sum_{j=0}^k q^{j(j+1)} (q)_{k}/(q)_{j}?)
    # Masbaum 2003, "Skein-theoretical derivation of some formulas of Habiro"
    # For a twist knot T_m with m half-twists. 5_2 is T_3 (3 half-twists).
    # J_{N+1}(T_m) = sum_{k=0}^N c_m(k) {N+k+1 \choose 2k+1}_q (2k+1)!_q / (q^{1/2}-q^{-1/2})^{2k}
    
    # Actually, for 5_2 (3 half-twists), a known expansion is:
    # J_{N+1}(5_2) = sum_{k=0}^N (prod_{j=1}^k (1-q^{N+j+1})(1-q^{N-j+1})) * (sum_{j=0}^k q^{j(j+1)} {k \choose j}_q)
    
    q = omega
    total = 0j
    for k in range(N):
        # Product term P_k = prod_{j=1}^k (1-q^{N+j})(1-q^{N-j})
        # At q^N = 1, this is prod_{j=1}^k (1-q^j)(1-q^{-j}) = |1-q^j|^2
        pk = 1.0
        for j in range(1, k + 1):
            pk *= (1 - q**j) * (1 - q**(-j))
            
        # Sum term S_k = sum_{j=0}^k q^{j(j+1)} * [k choose j]_q
        sk = 0j
        for j in range(k + 1):
            # q-binomial [k choose j]_q = (q)_k / ((q)_j (q)_{k-j})
            binom_q = q_fact(k, q) / (q_fact(j, q) * q_fact(k-j, q))
            sk += q**(j*(j+1)) * binom_q
            
        total += pk * sk
    return total

def main():
    for n in [3]:
        val = compute_5_2_kashaev(n)
        mag = np.abs(val)
        res = (2 * np.pi / n) * np.log(mag)
        print(f"5_2 (N={n}): |K| = {mag:.4f}, (2pi/3)ln|K| = {res:.4f}")

    # Also check 6_1 again with a slightly different formula
    # 6_1 is T_4 (4 half-twists)
    def compute_6_1_kashaev(N):
        q = np.exp(2j * np.pi / N)
        total = 0j
        for k in range(N):
            pk = 1.0
            for j in range(1, k + 1):
                pk *= (1 - q**j) * (1 - q**(-j))
            
            # S_k for T_4 (negative full twists)
            # S_k = sum q^{-j(j+1)} [k choose j]_q
            sk = 0j
            for j in range(k + 1):
                binom_q = q_fact(k, q) / (q_fact(j, q) * q_fact(k-j, q))
                sk += q**(-j*(j+1)) * binom_q
            total += pk * sk
        return total

    val6 = compute_6_1_kashaev(3)
    mag6 = np.abs(val6)
    res6 = (2 * np.pi / 3) * np.log(mag6)
    print(f"6_1 (N=3): |K| = {mag6:.4f}, (2pi/3)ln|K| = {res6:.4f}")

if __name__ == "__main__":
    main()
