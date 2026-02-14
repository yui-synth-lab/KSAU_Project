
import numpy as np

def calculate_kashaev_31(N=3):
    omega = np.exp(2j * np.pi / N)
    
    # Formula for J_N(3_1; q) at q = omega
    # J_N = sum_{n=0}^{N-1} q^n * prod_{k=1}^n (1 - q^{N-k})
    
    total_sum = 0
    for n in range(N):
        product = 1
        for k in range(1, n + 1):
            product *= (1 - omega**(N - k))
        
        term = (omega**n) * product
        total_sum += term
        print(f"n={n}: term={term}")
        
    kashaev = np.abs(total_sum)
    return total_sum, kashaev

if __name__ == "__main__":
    val, abs_val = calculate_kashaev_31(3)
    print("-" * 30)
    print(f"Trefoil (3_1) at N=3:")
    print(f"Value: {val}")
    print(f"Kashaev (Abs): {abs_val}")
    print(f"Abs^2: {abs_val**2}")
