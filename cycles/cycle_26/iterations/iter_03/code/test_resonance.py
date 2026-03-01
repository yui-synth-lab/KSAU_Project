
import numpy as np
import sys
from pathlib import Path

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def n_sphere_volume(n, r=1.0):
    """Volume of an n-dimensional sphere."""
    from scipy.special import gamma
    return (np.pi**(n/2) / gamma(n/2 + 1)) * (r**n)

def main():
    ssot = SSOT()
    consts = ssot.constants()
    
    # Target values from SSOT
    c_target = consts['scaling_laws']['boson_scaling']['C_theoretical']
    
    # 1. pi * sqrt(3) approach
    c_resonance = np.pi * np.sqrt(3)
    
    # 2. 10D/9D Volume Ratio approach
    # In KSAU, if we consider the unit bulk (10D) vs unit boundary (9D)
    v10 = n_sphere_volume(10)
    v9 = n_sphere_volume(9)
    ratio_10_9 = v10 / v9
    
    # 3. Geometric mean or other combinations?
    # Let's check the value of c_resonance
    print(f"Target C (SSOT):      {c_target:.10f}")
    print(f"pi * sqrt(3):         {c_resonance:.10f}")
    print(f"Error (Resonance):    {abs(c_resonance - c_target):.10e}")
    print(f"Error % (Resonance):  {abs(c_resonance - c_target)/c_target*100:.6f}%")
    
    print(f"\nV(10D):               {v10:.10f}")
    print(f"V(9D):                {v9:.10f}")
    print(f"V10 / V9:             {ratio_10_9:.10f}")
    
    # Maybe 2 * pi?
    print(f"2 * pi:               {2*np.pi:.10f}")
    
    # What about sqrt(10/9) factors?
    # Let's check the ratio to pi
    print(f"C_target / pi:        {c_target / np.pi:.10f}")
    print(f"sqrt(3):              {np.sqrt(3):.10f}")

    # Theoretical derivation from seed: "10D/9D volume ratio"
    # Actually, the seed mentions C = pi * sqrt(3)
    
    results = {
        "c_target": c_target,
        "pi_sqrt_3": c_resonance,
        "error": abs(c_resonance - c_target),
        "v10_v9_ratio": ratio_10_9
    }

if __name__ == "__main__":
    main()
