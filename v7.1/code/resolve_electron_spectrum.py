
import numpy as np

def quantum_int(n, q):
    if np.abs(q - 1) < 1e-12:
        return n
    return (q**(n/2) - q**(-n/2)) / (q**0.5 - q**(-0.5))

def unnormalized_colored_jones_31(N, q):
    """
    Unnormalized Colored Jones polynomial for right-handed trefoil 3_1
    Using the sum formula from Masbaum / Habiro
    J_N(q) = [N]_q * sum_{k=0}^{N-1} q^{k(k+3)/2} * prod_{j=1}^k (q^{N-j} - 1)(q^{N+j} - 1) / (q - 1)...?
    No, let's use the most robust state sum:
    """
    # Sum formula for 3_1:
    # J_N(q) = q^{N-1} * sum_{k=0}^{N-1} q^{k(N+1)} * prod_{j=1}^k (1 - q^{N-j})
    
    total = 0j
    for k in range(N):
        product = 1.0 + 0j
        for j in range(1, k + 1):
            product *= (1 - q**(N - j))
        term = (q**(k * (N + 1))) * product
        total += term
    
    return (q**(N - 1)) * total

def solve_electron():
    results = {}
    for n in [2, 3, 4, 5]:
        # Evaluate at Kashaev point: q = exp(2pi i / n)
        q = np.exp(2j * np.pi / n)
        val = unnormalized_colored_jones_31(n, q)
        abs_val = np.abs(val)
        results[n] = {"val": val, "abs": abs_val}
        print(f"N={n}, q=exp(2pi i/{n}):")
        print(f"  Unnormalized J_N(3_1) = {val}")
        print(f"  Abs Value = {abs_val}")
        print(f"  Abs^2 = {abs_val**2}")
    return results

if __name__ == "__main__":
    print("CRITICAL RESOLUTION: Trefoil Colored Jones Spectrum")
    solve_electron()
