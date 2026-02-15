import numpy as np
import pandas as pd
from sympy import isprime, factorint

def get_invariants(N):
    def psi(n):
        res = n
        for p in factorint(n):
            res *= (1 + 1/p)
        return int(res)
    def nu2(n):
        if n % 4 == 0: return 0
        val = 1
        for p in factorint(n):
            if p == 2: continue
            if p % 4 == 3: return 0
            if p % 4 == 1: val *= 2
        return val
    def nu3(n):
        if n % 9 == 0: return 0
        val = 1
        for p in factorint(n):
            if p == 3: continue
            if p % 3 == 2: return 0
            if p % 3 == 1: val *= 2
        return val
    def count_cusps(n):
        import math
        def phi(m):
            res = m
            for p in factorint(m):
                res -= res // p
            return res
        cusps = 0
        for d in range(1, n + 1):
            if n % d == 0:
                cusps += phi(math.gcd(d, n // d))
        return cusps

    mu = N
    for p in factorint(N):
        mu = mu * (p + 1) // p
    
    n2 = nu2(N)
    n3 = nu3(N)
    n_inf = count_cusps(N)
    g = 1 + mu/12 - n2/4 - n3/3 - n_inf/2
    return int(g), int(n_inf)

def run_composite_null_test():
    print("=== KSAU v13.9 Composite Null Hypothesis Test ===")
    target_X = 49.91577
    threshold = 0.001 
    
    all_levels = range(2, 200)
    matches = []
    print(f"Scanning all levels N from 2 to 199 (Total: {len(all_levels)})...")
    
    for N in all_levels:
        g, nu_inf = get_invariants(N)
        if g + nu_inf == 0: continue
        R = nu_inf / (g + nu_inf)
        X_static = R * (np.pi * N - (2*g - 2))
        error = abs(float(X_static) / target_X - 1)
        
        if error < threshold:
            matches.append(N)
            print(f"  [MATCH] N={N}, g={g}, Action={float(X_static):.4f}, Err={error*100:.4f}%")

    p_value = len(matches) / len(all_levels)
    print(f"\nTotal scanned: {len(all_levels)}")
    print(f"Matches found: {len(matches)}")
    print(f"Global p-value: {p_value:.4f}")

if __name__ == "__main__":
    run_composite_null_test()
