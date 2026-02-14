
import numpy as np

def colored_jones_trefoil(N, q):
    # Standard formula for unnormalized J_N of right-handed trefoil
    # J_N(q) = q^{N-1} * sum_{k=0}^{N-1} q^{k(N+1)} * prod_{j=1}^k (1 - q^{N-j})
    
    prefactor = q**(N - 1)
    total_sum = 0
    for k in range(N):
        product = 1
        for j in range(1, k + 1):
            product *= (1 - q**(N - j))
        
        term = (q**(k * (N + 1))) * product
        total_sum += term
        
    return prefactor * total_sum

def kashaev_evaluation():
    N = 3
    q = np.exp(2j * np.pi / N)
    
    # Test unnormalized
    val = colored_jones_trefoil(N, q)
    print(f"Unnormalized J_3(3_1) at q=exp(2pi i/3):")
    print(f"  Value: {val}")
    print(f"  Abs:   {np.abs(val)}")
    print(f"  Abs^2: {np.abs(val)**2}")
    
    # Test normalized (Divided by Unknot = [N]_q)
    # J_N(Unknot) = (q^{N/2} - q^{-N/2}) / (q^{1/2} - q^{-1/2})
    # For N=3, q=exp(2pi i/3): [3]_q = (exp(pi i) - exp(-pi i)) / (...) = 0
    # This is why normalization fails at roots of unity for Kashaev!
    # Kashaev invariant MUST use the unnormalized version.

if __name__ == "__main__":
    kashaev_evaluation()
