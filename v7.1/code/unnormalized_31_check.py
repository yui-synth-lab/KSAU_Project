
import numpy as np

def q_pochhammer(a, q, k):
    res = 1.0 + 0j
    for i in range(k):
        res *= (1 - a * (q**i))
    return res

def unnormalized_jones_31(N=3):
    q = np.exp(2j * np.pi / N)
    
    total_sum = 0
    for k in range(N):
        num = q_pochhammer(q**(N-k), q, k) * q_pochhammer(q**(N+1), q, k)
        den = q_pochhammer(q, q, k)
        
        term = ((-1)**k) * (q**(-k*(k+3)/2)) * (num / den)
        total_sum += term
        print(f"k={k}: term={term}")
        
    return total_sum

if __name__ == "__main__":
    val = unnormalized_jones_31(3)
    print("-" * 30)
    print(f"Unnormalized J_3(3_1) value: {val}")
    print(f"Abs value: {np.abs(val)}")
    print(f"Abs^2: {np.abs(val)**2}")
