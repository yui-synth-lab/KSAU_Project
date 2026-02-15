import pandas as pd
from sympy import factorint

def calculate_index(N):
    """Calculates the Index mu = [SL2(Z) : Gamma_0(N)]"""
    mu = N
    for p in factorint(N):
        mu = mu * (p + 1) // p
    return int(mu)

def calculate_genus(N, mu, nu_2, nu_3, nu_inf):
    return int(1 + mu/12 - nu_2/4 - nu_3/3 - nu_inf/2)

# Re-use invariant calculation logic
def get_full_invariants(N):
    import math
    def phi(n):
        res = n
        for p in factorint(n):
            res -= res // p
        return res
    
    mu = calculate_index(N)
    
    # Elliptic points
    if N % 4 == 0: nu_2 = 0
    else:
        nu_2 = 1
        for p in factorint(N):
            if p == 2: continue
            if p % 4 == 3: nu_2 = 0; break
            if p % 4 == 1: nu_2 *= 2
            
    if N % 9 == 0: nu_3 = 0
    else:
        nu_3 = 1
        for p in factorint(N):
            if p == 3: continue
            if p % 3 == 2: nu_3 = 0; break
            if p % 3 == 1: nu_3 *= 2
            
    # Cusps
    nu_inf = 0
    for d in range(1, N + 1):
        if N % d == 0:
            nu_inf += phi(math.gcd(d, N // d))
            
    g = calculate_genus(N, mu, nu_2, nu_3, nu_inf)
    
    return {"N": N, "Index": mu, "Genus": g, "Cusps": nu_inf}

def analyze_stability():
    print("=== KSAU v13.5 Stability Analysis: Vacuum Energy Minimization ===")
    print("Hypothesis: For a given Genus (g), the physical vacuum selects the Level (N)")
    print("            that minimizes the Index (Volume/Energy).")
    
    # Collect data
    data = []
    for N in range(2, 101):
        data.append(get_full_invariants(N))
    
    df = pd.DataFrame(data)
    
    # Analyze Genus 1, 2, 3
    for g in [1, 2, 3]:
        print(f"\n--- Genus g={g} Sector ---")
        subset = df[df['Genus'] == g].sort_values(by='Index')
        print(f"{'N':<5} | {'Index (Energy)':<15} | {'Cusps':<5} | {'Status'}")
        print("-" * 45)
        
        min_index = subset['Index'].min()
        
        for _, row in subset.iterrows():
            N_val = row['N']
            idx = row['Index']
            status = "GROUND STATE" if idx == min_index else f"Excited (+{idx - min_index})"
            print(f"{N_val:<5} | {idx:<15} | {row['Cusps']:<5} | {status}")

if __name__ == "__main__":
    analyze_stability()
