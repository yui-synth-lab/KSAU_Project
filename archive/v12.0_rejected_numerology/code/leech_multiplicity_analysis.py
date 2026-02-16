import sympy

def analyze_leech_multiplicities():
    # Multiplicities of the first few shells of the Leech Lattice
    # a_n is the number of vectors with norm 2n
    multiplicities = {
        "Norm 4 (a_2)": 196560,
        "Norm 6 (a_3)": 16773120,
        "Norm 8 (a_4)": 398034000,
        "Norm 10 (a_5)": 4608155520,
        "Norm 12 (a_6)": 33230691840
    }
    
    print(f"{'Shell':<15} | {'Multiplicity':<15} | {'Prime Factorization'}")
    print("-" * 60)
    
    for name, val in multiplicities.items():
        factors = sympy.factorint(val)
        factor_str = " * ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())])
        print(f"{name:<15} | {val:<15} | {factor_str}")
        
        # Check for 41 or related primes
        if 41 in factors:
            print(f"  --> FOUND PRIME 41 in {name}!")

    print("\n--- Conway Group Co_0 Order Analysis ---")
    # Order of Co_0 = 2^22 * 3^9 * 5^4 * 7^2 * 11 * 13 * 23
    co0_order = (2**22) * (3**9) * (5**4) * (7**2) * 11 * 13 * 23
    print(f"Order of Co_0: {co0_order}")
    print(f"Factors: 2^22 * 3^9 * 5^4 * 7^2 * 11 * 13 * 23")

if __name__ == "__main__":
    analyze_leech_multiplicities()
