import math
import os

# KSAU v13.9 Audit Script: Modular Minimality & Scan Extension
kappa = math.pi / 24
target_X = 51.52802  # ln(MPL/me)

def get_multiplicity(N):
    # Index mu for Gamma_0(N) where N is prime: mu = N + 1
    return N + 1

def get_genus(N):
    # Genus for X_0(prime N)
    if N == 2: return 0
    if N == 3: return 0
    if N == 5: return 0
    if N == 7: return 0
    if N == 11: return 1
    return math.ceil((N - 13) / 12) + 1 # Rough prime genus

def calculate_energy(N):
    # E[N] = mu + (2g-2) -> hypothesis for minimality
    mu = get_multiplicity(N)
    g = get_genus(N)
    # We look for the bottleneck where mu is minimal for a given genus
    return mu, g

if __name__ == "__main__":
    results = []
    print(f"Scanning modular levels N < 500...")
    for N in range(2, 501):
        if not all(N % i for i in range(2, int(N**0.5) + 1)): continue # Primes only
        
        mu, g = calculate_energy(N)
        R = 0.24  # Flux factor Sample
        X = R * (math.pi * N - (2*g - 2))
        error = abs(X - target_X) / target_X
        
        if error < 0.002: # 0.2% threshold
            results.append((N, mu, g, X, error))
    
    print("\nStatistical Results:")
    for N, mu, g, X, e in results:
        print(f"N={N:3} | mu={mu:3} | g={g} | X={X:.4f} | Error={e* 100:.4f}%")

    if not results:
        print("No additional resonances found in N < 500.")

    # Verify N=41 Minimality in g=3 sector
    g3_primes = [N for N in range(2, 500) if get_genus(N) == 3]
    if g3_primes:
        min_N = min(g3_primes, key=get_multiplicity)
        print(f"\nGenus-3 Ground State: N=41 (mu={get_multiplicity(41)}) vs Min(N).. {min_N} mu={get_multiplicity(min_N)}")
