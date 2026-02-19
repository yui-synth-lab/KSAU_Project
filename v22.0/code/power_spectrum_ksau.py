"""
KSAU v22.0: Power Spectrum P(k) Prediction
==========================================
Implements Section 2 of the v22.0 Roadmap.
Predicts the shape of the matter power spectrum P(k) by applying scale-dependent
KSAU suppression xi(k) and branching losses to a base LCDM P(k).

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import matplotlib.pyplot as plt
import os

class PowerSpectrumKSAU:
    def __init__(self, config_path="v22.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.Om0 = self.config['omega_m0']
        self.H0 = self.config['H0_planck']
        self.sigma8 = self.config['sigma8']
        self.ns = self.config['n_s']
        
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.R_cell = self.config['R_cell']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        
    def transfer_function_eh(self, k):
        """Eisenstein & Hu (1998) transfer function approximation (no baryons)."""
        h = self.H0 / 100.0
        # Shape parameter Gamma (not growth index!)
        gamma_param = self.Om0 * h
        q = k / (gamma_param)
        L0 = np.log(2 * np.exp(1) + 1.8 * q)
        C0 = 14.2 + 731.0 / (1 + 62.5 * q)
        return L0 / (L0 + C0 * q**2)

    def power_spectrum_lcdm(self, k):
        """Linear power spectrum P(k) ~ k^ns * T(k)^2."""
        tk = self.transfer_function_eh(k)
        pk_raw = k**self.ns * tk**2
        return pk_raw

    def window_function(self, k, r):
        """Top-hat window function in Fourier space (3D). Handles array inputs."""
        x = np.atleast_1d(k * r)
        res = np.ones_like(x)
        mask = x > 1e-4
        xm = x[mask]
        res[mask] = 3 * (np.sin(xm) - xm * np.cos(xm)) / (xm**3)
        return res if np.ndim(k) > 0 else res[0]

    def xi_k(self, k):
        """Scale-dependent clustering efficiency."""
        return 0.5 + 0.5 * (1.0 - self.window_function(k, self.R_cell))

    def predict_p_ksau(self, k):
        """
        P_KSAU(k) = P_LCDM(k) * (Omega_eff/Om0) * F_branching^2
        Note: Omega_eff depends on xi(k). 
        This refined formula relaxes small-scale over-suppression by removing the 
        redundant xi(k)^2 factor, aligning with the auditor's requirement.
        """
        pk_lcdm_raw = self.power_spectrum_lcdm(k)
        xi = self.xi_k(k)
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        
        suppression_sq = (om_eff / self.Om0) * self.F_branching**2
        return pk_lcdm_raw * suppression_sq

    def run_analysis(self):
        print("="*80)
        print(f"{'KSAU v22.0: Power Spectrum P(k) Shape Prediction':^80}")
        print("="*80)
        
        k_vals = np.logspace(-3, 1, 200)
        pk_lcdm = self.power_spectrum_lcdm(k_vals)
        pk_ksau = self.predict_p_ksau(k_vals)
        
        # Normalize to target sigma8 (LCDM base)
        # sigma8^2 = 1/(2pi^2) * int P(k) k^2 W(k, 8)^2 dk
        def get_sigma8_norm(k, pk):
            w8 = self.window_function(k, 8.0)
            integrand = pk * k**2 * w8**2
            # Use np.trapezoid (NumPy 2.0+) or fallback to np.trapz
            if hasattr(np, 'trapezoid'):
                return np.sqrt(np.trapezoid(integrand, k) / (2 * np.pi**2))
            else:
                return np.sqrt(np.trapz(integrand, k) / (2 * np.pi**2))
            
        s8_lcdm_raw = get_sigma8_norm(k_vals, pk_lcdm)
        norm = (self.sigma8 / s8_lcdm_raw)**2
        
        pk_lcdm *= norm
        pk_ksau *= norm
        
        # Final S8 values
        s8_lcdm_final = get_sigma8_norm(k_vals, pk_lcdm)
        s8_ksau_final = get_sigma8_norm(k_vals, pk_ksau)
        
        # S8 = sigma8 * sqrt(Om0 / 0.3)
        S8_norm = np.sqrt(self.Om0 / 0.3)
        
        print(f"Base Sigma8 (Planck): {s8_lcdm_final:.4f}")
        print(f"KSAU Predicted Sigma8: {s8_ksau_final:.4f}")
        print(f"KSAU Predicted S8:     {s8_ksau_final * S8_norm:.4f}")
        print(f"Suppression Factor:    {s8_ksau_final/s8_lcdm_final:.4f}")
        
        # Compare with Survey S8(0) values
        print("-" * 80)
        print("Comparison with Surveys (z=0 extrapolated):")
        for name, data in self.config['survey_data'].items():
            print(f"  {name:<12}: S8_obs = {data['S8_obs']:.3f} +/- {data['S8_err']:.3f}")
        
        # Plotting
        try:
            plt.figure(figsize=(10, 6))
            plt.loglog(k_vals, pk_lcdm, label="LCDM (Planck Baseline)", color='black', linestyle='--')
            plt.loglog(k_vals, pk_ksau, label="KSAU Predicted (v22.0)", color='blue', linewidth=2)
            plt.xlabel("k [h/Mpc]")
            plt.ylabel("P(k) [(Mpc/h)^3]")
            plt.title("KSAU Topological Suppression of Power Spectrum")
            plt.grid(True, which="both", ls="-", alpha=0.5)
            plt.legend()
            
            # Save plot
            os.makedirs("v22.0/figures", exist_ok=True)
            plt.savefig("v22.0/figures/power_spectrum_ksau.png")
            print("Plot saved to v22.0/figures/power_spectrum_ksau.png")
        except Exception as e:
            print(f"Plotting failed: {e}")

        # Save Results (HIGH-2)
        output = {
            "k": k_vals.tolist(),
            "pk_lcdm": pk_lcdm.tolist(),
            "pk_ksau": pk_ksau.tolist(),
            "sigma8_lcdm": s8_lcdm_final,
            "sigma8_ksau": s8_ksau_final,
            "status": "P(k) Prediction Complete"
        }
        
        with open("v22.0/unified_filament_results.json", 'w') as f:
            json.dump(output, f, indent=2)
            
        print("Results saved to v22.0/unified_filament_results.json")

if __name__ == "__main__":
    model = PowerSpectrumKSAU()
    model.run_analysis()
