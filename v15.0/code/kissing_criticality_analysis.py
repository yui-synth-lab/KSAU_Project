"""
KSAU v15.1.1: Kissing Number Criticality & Kappa Resonance
Script purpose: Analyzes the relationship between the unknotting threshold (pi^2),
                kissing numbers K(d), and the spectral weight kappa = pi/24.
                
Theoretical discovery:
    - d > pi^2 is the condition for emergent dynamics (Time).
    - K(4) * kappa = pi is the resonance condition for stable spacetime.
"""

import numpy as np

def analyze_kissing_criticality():
    kappa = np.pi / 24.0
    pi2 = np.pi**2
    
    # Known Kissing Numbers
    kissing = {
        1:  2,
        2:  6,
        3:  12,
        4:  24,
        8:  240,
        24: 196560,
    }

    print("="*80)
    print(f"{'KSAU v15.1.1: Criticality of Dimensionality & Kappa Resonance':^80}")
    print("="*80)
    print(f"D_critical / 2 = pi^2 = {pi2:.6f}")
    print("-"*80)
    print(f"{'Dim':>4} | {'K(d)':>12} | {'K(d)/pi^2':>10} | {'Status':>12} | {'K(d)*kappa/pi':>15}")
    print("-"*80)

    for dim, k in sorted(kissing.items()):
        ratio = k / pi2
        resonance = (k * kappa) / np.pi
        
        if k < pi2:
            state = "FROZEN"
        elif abs(k - pi2) < 3:
            state = "BOUNDARY"
        else:
            state = "FLUID"
            
        print(f"{dim:4d} | {k:12d} | {ratio:10.4f} | {state:12s} | {resonance:15.4f}")

    print("
" + "="*80)
    print("THEORETICAL DEDUCTIONS:")
    print(f"1. TIME IGNITION: 3D is the first dimension where K(d) > pi^2 ({kissing[3]} > {pi2:.2f}).")
    print(f"2. KAPPA RESONANCE: In 4D, K(4)*kappa = pi exactly. Spacetime is a perfect filter.")
    print(f"3. BULK SOURCE: In 24D, K(24)*kappa = 8190*pi. The bulk potential is rational.")
    print("="*80)

if __name__ == "__main__":
    analyze_kissing_criticality()
