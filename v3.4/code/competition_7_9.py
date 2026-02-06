
import numpy as np

# Data
G = 0.915965594
SLOPE_Q = 1.3079  # Quark scaling factor
SLOPE_L = 0.2029  # Lepton scaling factor

def find_best_rational(target, base, max_den=20):
    results = []
    ratio = target / base
    for d in range(1, max_den + 1):
        for n in range(1, max_den * 2): # molecular can be larger
            candidate = n / d
            err = abs(candidate - ratio)
            results.append((n, d, candidate, err))
    return sorted(results, key=lambda x: x[3])

print("--- [1] Rational Competition for Quark Slope (Slope/G) ---")
q_best = find_best_rational(SLOPE_Q, G, max_den=20)
print(f"{'n/d':<10} | {'Value':<10} | {'Error':<10}")
for n, d, val, err in q_best[:5]:
    print(f"{n}/{d:<8} | {val:.5f} | {err:.5f}")

print("\n--- [2] Rational Competition for Lepton Slope (Slope/G) ---")
l_best = find_best_rational(SLOPE_L, G, max_den=20)
print(f"{'n/d':<10} | {'Value':<10} | {'Error':<10}")
for n, d, val, err in l_best[:5]:
    print(f"{n}/{d:<8} | {val:.5f} | {err:.5f}")

# Check other bases
print("\n--- [3] Rival Base Competition (Which constant wins?) ---")
BASES = {'G': G, 'pi': np.pi, 'e': np.e, 'phi': 1.618034}

for name, base in BASES.items():
    q_err = find_best_rational(SLOPE_Q, base, max_den=10)[0][3]
    l_err = find_best_rational(SLOPE_L, base, max_den=10)[0][3]
    print(f"Base {name:<4}: Best Quark Err (d<=10): {q_err:.5f}, Best Lepton Err (d<=10): {l_err:.5f}")

