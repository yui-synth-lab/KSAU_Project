import numpy as np
from scipy.integrate import quad
import sys
import os
sys.path.append('v23.0/code')
from power_spectrum_bao import PowerSpectrumBAOV23

ps = PowerSpectrumBAOV23()

def window_tophat(k, r=8.0):
    x = k * r
    if x < 1e-4: return 1.0
    return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

def integrand(k):
    T = ps.transfer_function_eh_bao(k)
    return (k**2 / (2 * np.pi**2)) * (k**ps.ns * T**2) * window_tophat(k, 8.0)**2

integral, _ = quad(integrand, 1e-4, 10.0)
print(f"Integral: {integral}")
print(f"A_norm: {0.811**2 / integral}")

# Test S8 at z=0.26 for R=21, xi=1
Om0 = 0.315
Otens0 = 0.091
F_branching = 3.9375 / 4.0
a = 1.0 / 1.26
xi = 1.0
om_eff = (Om0 - Otens0) + xi * Otens0 # 0.315
gamma = 0.55
d_z = a**gamma
suppression = np.sqrt(om_eff / Om0) * F_branching
pk_factor = (d_z * suppression)**2
print(f"D_z: {d_z}")
print(f"Suppression: {suppression}")
print(f"PK Factor: {pk_factor}")

final_integral = integral * pk_factor
print(f"Final Sig8 Sq: {final_integral}")
print(f"Final Sig8: {np.sqrt(final_integral)}")
print(f"Final S8: {np.sqrt(final_integral) * np.sqrt(0.315 / 0.3)}")
