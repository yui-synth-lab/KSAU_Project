"""
KSAU v23.0: Power Spectrum with BAO (Eisenstein-Hu)
===================================================
Implements Section 1 of the v23.0 Roadmap.
Introduces the Baryon Acoustic Oscillation (BAO) terms into the 
Eisenstein-Hu transfer function, considering baryon density Omega_b.

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import os

class PowerSpectrumBAOV23:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.h = self.config['H0_planck'] / 100.0
        self.Om0 = self.config['omega_m0']
        self.Ob0 = self.config['omega_b0']
        self.Tcmb = 2.725
        self.ns = self.config['n_s']
        self.sigma8 = self.config['sigma8']

    def transfer_function_eh_bao(self, k):
        """
        Eisenstein & Hu (1998) transfer function with BAO (Full formulation).
        Equations from EH98, Section 3.
        """
        om = self.Om0 * self.h**2
        ob = self.Ob0 * self.h**2
        f_b = ob / om
        f_c = (self.Om0 - self.Ob0) / self.Om0
        
        # Sound horizon
        zeq = 2.50e4 * om * (self.Tcmb / 2.7)**(-4)
        keq = 0.0746 * om * (self.Tcmb / 2.7)**(-2)
        
        zdag = 1.0 + 0.0513 * om**(-0.731) * (1.0 + 0.336 * om**0.372)
        req = 31.5 * ob * (self.Tcmb / 2.7)**(-4) / (zeq / 1e3)
        
        # Drag epoch redshift (approx)
        b1 = 0.313 * om**(-0.419) * (1.0 + 0.607 * om**0.674)
        b2 = 0.238 * om**0.223
        zd = 1291.0 * (om**0.251 / (1.0 + 0.659 * om**0.828)) * (1.0 + b1 * ob**b2)
        
        rd = 31.5 * ob * (self.Tcmb / 2.7)**(-4) / (zd / 1e3)
        s = (2.0 / (3.0 * keq)) * np.sqrt(6.0 / req) * np.log((np.sqrt(1.0 + rd) + np.sqrt(rd + req)) / (1.0 + np.sqrt(req)))
        
        # Effective shape parameter
        ksilk = 1.6 * ob**0.52 * om**0.73 * (1.0 + (10.4 * om)**(-0.95))
        
        # Cold Dark Matter component
        q = k / (13.41 * keq)
        a1 = (46.9 * om)**0.670 * (1.0 + (32.1 * om)**(-0.532))
        a2 = (12.0 * om)**0.424 * (1.0 + (45.0 * om)**(-0.582))
        alpha_c = a1**(-f_b) * a2**(-(f_b**3))
        
        b1_c = 0.944 / (1.0 + (458.0 * om)**(-0.708))
        b2_c = (0.395 * om)**(-0.0266)
        beta_c = 1.0 / (1.0 + b1_c * (f_c**b2_c - 1.0))
        
        def f_tilde(k, alpha, beta):
            q_eff = k / (13.41 * keq)
            C = 14.2 / alpha + 386.0 / (1.0 + 69.9 * q_eff**1.08)
            L = np.log(np.e + 1.8 * beta * q_eff)
            return L / (L + C * q_eff**2)
        
        Tc = f_c * f_tilde(k, 1.0, beta_c) + f_b * f_tilde(k, alpha_c, beta_c)
        
        # Baryon component
        beta_node = 8.41 * om**0.431
        alpha_b = 2.07 * keq * s * (1.0 + zdag)**(-1.36)
        
        Tb = (f_tilde(k, 1.0, 1.0) / (1.0 + (k * s / 5.2)**2) + 
              (alpha_b / (1.0 + (beta_node / (k * s))**3)) * np.exp(-(k / ksilk)**1.4))
        Tb *= np.sinc(k * s / np.pi)
        
        return Tc + Tb

    def power_spectrum(self, k):
        """Primordial P(k) = A * k^ns * T(k)^2"""
        T = self.transfer_function_eh_bao(k)
        return k**self.ns * T**2

    def generate_spectrum(self):
        print("="*80)
        print(f"{'KSAU v23.0: Power Spectrum with BAO Features':^80}")
        print("="*80)
        
        k_vals = np.logspace(-3, 1, 100)
        p_vals = [self.power_spectrum(k) for k in k_vals]
        
        print(f"Generated P(k) for {len(k_vals)} points from k=0.001 to 10.0")
        
        # Save results
        output = {
            "parameters": {
                "omega_m": self.Om0,
                "omega_b": self.Ob0,
                "h": self.h,
                "n_s": self.ns
            },
            "spectrum": [
                {"k": k, "Pk": p} for k, p in zip(k_vals, p_vals)
            ]
        }
        
        os.makedirs("v23.0/data", exist_ok=True)
        with open("v23.0/data/power_spectrum_bao_results.json", 'w') as f:
            json.dump(output, f, indent=2)
            
        print("Results saved to v23.0/data/power_spectrum_bao_results.json")
        print("="*80)

if __name__ == "__main__":
    ps = PowerSpectrumBAOV23()
    ps.generate_spectrum()
