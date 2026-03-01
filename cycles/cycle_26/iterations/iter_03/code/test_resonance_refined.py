
import numpy as np
import sys
from pathlib import Path
from scipy.special import gamma

# Setup SSOT
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def n_sphere_volume(n, r=1.0):
    """Volume of an n-dimensional sphere."""
    return (np.pi**(n/2) / gamma(n/2 + 1)) * (r**n)

def n_sphere_area(n, r=1.0):
    """Surface area of an n-dimensional sphere (S^{n-1})."""
    return (2 * np.pi**(n/2) / gamma(n/2)) * (r**(n-1))

def main():
    ssot = SSOT()
    consts = ssot.constants()
    
    c_target = consts['scaling_laws']['boson_scaling']['C_theoretical']
    kappa = consts['mathematical_constants']['kappa']
    
    # 1. pi * sqrt(3)
    c_base = np.pi * np.sqrt(3)
    diff = c_target - c_base
    
    # 2. Volume and Area ratios
    v10 = n_sphere_volume(10)
    v9 = n_sphere_volume(9)
    v10_v9 = v10 / v9
    v9_v10 = v9 / v10
    
    s9 = n_sphere_area(10) # Area of S^9 (Boundary of B^10)
    s8 = n_sphere_area(9)  # Area of S^8
    s9_s8 = s9 / s8

    # 3. KSAU Specific ratios
    # In H65/H66, alpha_em and boundary_projection (9) are used.
    # diff is approx 0.1
    
    print(f"Target C:          {c_target:.10f}")
    print(f"pi * sqrt(3):      {c_base:.10f}")
    print(f"Difference:        {diff:.10f}")
    
    print(f"\nV(10)/V(9):        {v10_v9:.10f}")
    print(f"V(9)/V(10):        {v9_v10:.10f}")
    print(f"S(9)/S(8):        {s9_s8:.10f}")
    
    # Test: C = pi * sqrt(3) + 1/pi?
    print(f"1/pi:              {1/np.pi:.10f}")
    
    # Test: C = pi * sqrt(3) + alpha_em * constant?
    alpha = consts['physical_constants']['alpha_em']
    print(f"diff / alpha:      {diff / alpha:.10f}")
    
    # Test: C = pi * sqrt(3) + kappa / boundary_projection?
    print(f"kappa / 9:         {kappa / 9:.10f}")
    print(f"kappa / 1.3:       {kappa / 1.30899:.10f}") # approx 0.1? No.
    
    # Maybe C = pi * sqrt(3) + V(10)/V(9) * kappa?
    print(f"v10_v9 * kappa:    {v10_v9 * kappa:.10f}")
    
    # Maybe C = pi * sqrt(3) + ln(9/10)? No.
    
    # Test: C = pi * sqrt(3) + (10/9) * alpha_em? No.
    
    # What if it's related to Catalan G?
    g_cat = consts['mathematical_constants']['G_catalan']
    print(f"diff / G_cat:      {diff / g_cat:.10f}")
    
    # Check if 0.1 is related to dimensions
    # diff is 0.0999999999999
    print(f"Is diff close to 0.1? {diff:.12f}")
    
    # If diff is exactly 0.1, then C = pi*sqrt(3) + 1/10?
    
    # Looking at v6.0 papers or physical constants...
    # The value 5.5413980927
    # 5.4413980927 + 0.1 = 5.5413980927
    
    # Why +0.1? 1/bulk_total?
    bulk_total = consts['dimensions']['bulk_total']
    print(f"1 / bulk_total:    {1/bulk_total:.10f}")
    
    # Theoretical Formula Candidate:
    # C = pi * sqrt(3) + 1/bulk_total
    c_theory = c_base + 1/bulk_total
    print(f"\nCandidate: C = pi * sqrt(3) + 1/10")
    print(f"Value:             {c_theory:.10f}")
    print(f"Error:             {abs(c_theory - c_target):.10e}")
    
if __name__ == "__main__":
    main()
