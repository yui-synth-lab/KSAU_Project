def calculate_genus_x0(N):
    """
    Calculates the genus of the modular curve X_0(N).
    Based on the standard formula using psi(N), nu2(N), nu3(N), and the number of cusps.
    """
    import math
    from sympy import factorint

    def psi(n):
        res = n
        factors = factorint(n)
        for p in factors:
            res *= (1 + 1/p)
        return int(res)

    def nu2(n):
        """Number of elliptic points of order 2."""
        if n % 4 == 0: return 0
        res = 1
        factors = factorint(n)
        for p in factors:
            if p == 2: continue
            # Legendre symbol (-1/p)
            if p % 4 == 3: return 0
            if p % 4 == 1: res *= 2
        return res

    def nu3(n):
        """Number of elliptic points of order 3."""
        if n % 9 == 0: return 0
        res = 1
        factors = factorint(n)
        for p in factors:
            if p == 3: continue
            # Legendre symbol (-3/p)
            if p % 3 == 2: return 0
            if p % 3 == 1: res *= 2
        return res

    def count_cusps(n):
        """Correct cusp formula for X0(N): sum_{d|N} phi(gcd(d, N/d))."""
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

    g = 1 + psi(N)/12 - nu2(N)/4 - nu3(N)/3 - count_cusps(N)/2
    return int(g)

def search_modular_generations():
    print(f"{'Level N':<10} | {'Genus g':<10} | {'Status'}")
    print("-" * 40)
    # Verification against known values (e.g., N=11 -> g=1, N=41 -> g=3)
    for N in range(1, 101):
        g = calculate_genus_x0(N)
        status = "MATCH (3 Generations)" if g == 3 else ""
        if g == 3:
            print(f"{N:<10} | {g:<10} | {status}")

if __name__ == "__main__":
    search_modular_generations()
