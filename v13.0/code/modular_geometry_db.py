import pandas as pd
import math
from sympy import factorint

def calculate_invariants(N):
    """
    Pure mathematical calculation of invariants for modular curve X_0(N).
    Based on standard formulas from Shimura, Miyake, or Diamond & Shurman.
    """
    # 1. Index mu = [SL2(Z) : Gamma_0(N)]
    mu = N
    factors = factorint(N)
    for p in factors:
        mu = mu * (p + 1) // p
    
    # 2. Number of elliptic points of order 2 (nu_2)
    if N % 4 == 0:
        nu_2 = 0
    else:
        nu_2 = 1
        for p in factors:
            if p == 2: continue
            if p % 4 == 3: nu_2 = 0; break
            if p % 4 == 1: nu_2 *= 2
            
    # 3. Number of elliptic points of order 3 (nu_3)
    if N % 9 == 0:
        nu_3 = 0
    else:
        nu_3 = 1
        for p in factors:
            if p == 3: continue
            if p % 3 == 2: nu_3 = 0; break
            if p % 3 == 1: nu_3 *= 2
            
    # 4. Number of cusps (nu_inf)
    nu_inf = 0
    for d in range(1, N + 1):
        if N % d == 0:
            nu_inf += math.isqrt(math.gcd(d, N // d)) # This is not quite right, fixing...
    
    # Correct cusp formula: sum_{d|N} phi(gcd(d, N/d))
    def phi(n):
        res = n
        for p in factorint(n):
            res -= res // p
        return res
    
    nu_inf = 0
    for d in range(1, N + 1):
        if N % d == 0:
            nu_inf += phi(math.gcd(d, N // d))
            
    # 5. Genus (g)
    # g = 1 + mu/12 - nu_2/4 - nu_3/3 - nu_inf/2
    # Standard formula for Riemann surfaces with orbifold points.
    g = 1 + mu/12 - nu_2/4 - nu_3/3 - nu_inf/2
    
    return {
        "N": N,
        "Index": int(mu),
        "Genus": int(g),
        "Cusps": int(nu_inf),
        "Elliptic_2": int(nu_2),
        "Elliptic_3": int(nu_3)
    }

def build_database():
    print("Building Modular Geometry Database (N=2 to 100)...")
    data = []
    for N in range(2, 101):
        data.append(calculate_invariants(N))
    
    df = pd.DataFrame(data)
    output_path = "v13.0/data/modular_invariants.csv"
    df.to_csv(output_path, index=False)
    print(f"Database saved to {output_path}")
    
    # Display interesting genus-3 candidates (The Generational Sector)
    print("\n--- Potential Genus-3 (Generational) Candidates ---")
    print(df[df['Genus'] == 3])

if __name__ == "__main__":
    build_database()
