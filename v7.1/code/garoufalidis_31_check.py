
import numpy as np

def garoufalidis_31_n3(N=3):
    # q = exp(2*pi*i/N)
    # In Garoufalidis formula, t is often q^{1/4} or q^{1/2}. 
    # Let's use q directly if possible or define t carefully.
    # Usually, t^4 = q.
    
    q = np.exp(2j * np.pi / N)
    t2 = np.exp(1j * np.pi / N) # t^2 = q^{1/2}
    t = np.exp(0.5j * np.pi / N) # t = q^{1/4}
    
    # J_n(t) = t^{-6(n^2-1)} * sum_{j=-(n-1)/2}^{(n-1)/2} t^{24j^2+12j} * (t^{8j+2} - t^{-(8j+2)})/(t^2 - t^{-2})
    
    n = N
    prefactor = t**(-6 * (n**2 - 1))
    
    total_sum = 0
    # j ranges from -(n-1)/2 to (n-1)/2
    # For n=3, j = -1, 0, 1
    for j in [-1, 0, 1]:
        num = t**(8*j + 2) - t**(-(8*j + 2))
        den = t**2 - t**(-2)
        
        # Handle division by zero if it occurs
        if np.abs(den) < 1e-12:
            term_inner = (8*j + 2) / 2 # L'Hopital
        else:
            term_inner = num / den
            
        term = t**(24*j**2 + 12*j) * term_inner
        total_sum += term
        print(f"j={j}: term={term}")
        
    final_val = prefactor * total_sum
    return final_val

if __name__ == "__main__":
    val = garoufalidis_31_n3(3)
    print("-" * 30)
    print(f"Garoufalidis J_3(3_1) value: {val}")
    print(f"Abs value: {np.abs(val)}")
    print(f"Abs^2: {np.abs(val)**2}")
