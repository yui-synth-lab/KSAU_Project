import numpy as np

def q_fact(n, omega):
    res = 1.0 + 0j
    for j in range(1, n + 1):
        res *= (1 - omega**j)
    return res

def q_symbol(a_pow, n, omega):
    res = 1.0 + 0j
    for j in range(n):
        res *= (1 - omega**(a_pow + j))
    return res

def compute_twist_kashaev(p, N):
    omega = np.exp(2j * np.pi / N)
    total = 0j
    for k in range(N):
        pk = 1.0
        for j in range(1, k + 1):
            pk *= (1 - omega**j) * (1 - omega**(-j))
        
        if p == -1:
            ak = 1.0
        elif p == -2:
            ak = 0j
            for n in range(k + 1):
                term = omega**(n*(n+1)) * q_symbol(k+1, n, omega) * q_symbol(k-n+1, n, omega) / q_fact(n, omega)
                ak += term
        else:
            ak = 1.0
        total += ak * pk
    return total

def main():
    print("Verification of Kashaev Invariants:")
    for knot, p in [("4_1", -1), ("6_1", -2)]:
        print(f"\nKnot: {knot} (p={p})")
        for n in [3, 10, 50]:
            val = compute_twist_kashaev(p, n)
            mag = np.abs(val)
            res = (2 * np.pi / n) * np.log(mag)
            print(f"N={n:3} | |K|={mag:12.4f} | (2pi/N)ln|K|={res:.6f}")

if __name__ == "__main__":
    main()
