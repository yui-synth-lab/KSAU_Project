
import numpy as np
import itertools

# Targets from KSAU v3.4 Regression
TARGET_GAMMA = 1.3079
TARGET_B_PRIME_ABS = 7.9159 

# Fundamental Constants
CONSTANTS = {
    'pi': np.pi,
    'e': np.e,
    'phi': (1 + np.sqrt(5)) / 2, # Golden Ratio
    'G': 0.915965594,            # Catalan's Constant
    'gamma_e': 0.57721566,       # Euler-Mascheroni
    'sqrt2': np.sqrt(2),
    'sqrt3': np.sqrt(3),
    'v_tet': 1.0149416,          # Volume of ideal regular tetrahedron
    'v_oct': 3.66386,            # Volume of ideal regular octahedron (= 4 * G ? No, 4*v_tet? No, 3.66 is approx) 
                                 # Actually Vol(Ideal Octahedron) = 3.663862376... = 4 * G matches? 
                                 # Wait, Vol(Ideal Tet) = 1.0149...
                                 # Vol(Ideal Oct) = 4 * G = 3.66386... Let's check G relationship.
                                 # G = 0.9159... 4*G = 3.6638. Yes.
    'zeta2': np.pi**2 / 6,
    'zeta3': 1.2020569           # Apery's constant
}

def search_combination(target, tolerance=0.002):
    results = []
    keys = list(CONSTANTS.keys())
    
    # 1. Simple fractions of constants: C1 * n/m
    for k in keys:
        val = CONSTANTS[k]
        for n in range(1, 13):
            for m in range(1, 13):
                candidate = val * n / m
                if abs(candidate - target) < tolerance:
                    results.append((f"{n}/{m} * {k}", candidate, abs(candidate - target)))

    # 2. Combinations: C1 op C2
    for k1 in keys:
        for k2 in keys:
            v1, v2 = CONSTANTS[k1], CONSTANTS[k2]
            
            # Add
            cand = v1 + v2
            if abs(cand - target) < tolerance: results.append((f"{k1} + {k2}", cand, abs(cand - target)))
            
            # Sub
            cand = abs(v1 - v2)
            if abs(cand - target) < tolerance: results.append((f"|{k1} - {k2}|", cand, abs(cand - target)))
            
            # Mul
            cand = v1 * v2
            if abs(cand - target) < tolerance: results.append((f"{k1} * {k2}", cand, abs(cand - target)))
            
            # Div
            cand = v1 / v2
            if abs(cand - target) < tolerance: results.append((f"{k1} / {k2}", cand, abs(cand - target)))

    # 3. Special Geometric forms for Gamma
    # e.g. 5*pi/12
    cand = 5 * np.pi / 12
    if abs(cand - target) < tolerance: results.append(("5*pi/12 (150 deg)", cand, abs(cand - target)))
    
    # 4. Special forms for B_Prime
    # e.g. 7 + G
    cand = 7 + CONSTANTS['G']
    if abs(cand - target) < tolerance: results.append(("7 + G", cand, abs(cand - target)))

    return sorted(results, key=lambda x: x[2])

print("--- Searching for Gamma (Slope) ~ 1.3079 ---")
gamma_matches = search_combination(TARGET_GAMMA, tolerance=0.005)
for expr, val, err in gamma_matches[:5]:
    print(f"{expr:<20} = {val:.5f} (Err: {err:.5f})")

print("\n--- Searching for |b'| (Intercept) ~ 7.9159 ---")
b_matches = search_combination(TARGET_B_PRIME_ABS, tolerance=0.005)
for expr, val, err in b_matches[:5]:
    print(f"{expr:<20} = {val:.5f} (Err: {err:.5f})")
