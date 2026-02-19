"""
KSAU v23.0: Fixed LOO-CV Engine (BAO Integrated & Rigorous Sigma8)
=================================================================
Corrects the methodological debt identified in the v23.0 Audit.
1. Integrates Eisenstein-Hu BAO transfer function.
2. Calculates sigma8 via full k-space integration instead of single-point k_eff.
3. Removes heuristic f_nl and tests physical R_cell stability.
4. Uses unbiased observation comparison at z_eff.

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
from scipy.optimize import minimize
from scipy.integrate import quad
import os
from power_spectrum_bao import PowerSpectrumBAOV23

class LOOCVEngineV23Fixed:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.Om0 = self.config['omega_m0']
        self.sigma8_baseline = self.config['sigma8']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.ns = self.config['n_s']
        
        # Branching factor (v21.0 inheritance)
        self.B_pred = self.config['filament_branching']['B_predicted']
        self.B_eff = self.config['filament_branching']['B_eff']
        self.F_branching = self.B_pred / self.B_eff
        
        # Scaling parameters
        self.beta_fixed = 1.0 # Testing co-moving scaling instead of 1.979
        self.Om_ref = self.config['scaling_factors']['omega_m_ref_sigma8']
        
        # Initialize BAO Power Spectrum
        self.ps_gen = PowerSpectrumBAOV23(config_path)
        
        # Normalization constant A for P(k) to match baseline sigma8
        self.A_norm = self.calculate_normalization()

    def window_tophat(self, k, r=8.0):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def window_24cell(self, k, r):
        """KSAU geometric window function (xi)."""
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def calculate_normalization(self):
        """Find A such that sigma8(z=0, tension=0) = baseline sigma8."""
        def integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            pk = k**self.ns * T**2
            return (k**2 / (2 * np.pi**2)) * pk * self.window_tophat(k, 8.0)**2
        
        integral, _ = quad(integrand, 1e-4, 10.0, limit=100)
        return self.sigma8_baseline**2 / integral

    def get_growth_factor(self, a, om_eff):
        gamma = 0.55 * np.log(om_eff) / np.log(self.Om0)
        return a**gamma

    def predict_s8_z(self, z, r0):
        """
        Integrates the power spectrum to find sigma8(z), 
        applying KSAU tension at each k.
        """
        a = 1.0 / (1.0 + z)
        r_z = r0 * (1 + z)**(-self.beta_fixed)
        
        def sigma8_integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            
            # KSAU Tension effect
            xi = 0.5 + 0.5 * (1.0 - self.window_24cell(k, r_z))
            # f_nl removed to test physical baseline stability
            
            om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
            # Growth with scale-dependent om_eff
            d_z = self.get_growth_factor(a, om_eff)
            
            # Suppression factor (local density effect)
            suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
            
            pk = self.A_norm * k**self.ns * T**2 * (d_z * suppression)**2
            return (k**2 / (2 * np.pi**2)) * pk * self.window_tophat(k, 8.0)**2
        
        sig8_sq, _ = quad(sigma8_integrand, 1e-4, 10.0, limit=100)
        sig8_z = np.sqrt(sig8_sq)
        
        # S8(z) = sigma8(z) * sqrt(Om(z)/0.3)
        # We use Om0 as the baseline for the S8 definition.
        return sig8_z * np.sqrt(self.Om0 / 0.3)

    def get_observed_s8_z(self, s8_obs_reported, z):
        """Convert LCDM-reported S8(0) back to S8(z)."""
        a = 1.0 / (1.0 + z)
        # LCDM growth with gamma=0.55
        d_lcdm_z = a**0.55
        return s8_obs_reported * d_lcdm_z

    def cost_function(self, r0, training_surveys):
        chi2 = 0
        for name, obs in training_surveys.items():
            z_eff = obs['z_eff']
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff)
            s8_pred_z = self.predict_s8_z(z_eff, r0[0])
            
            # Error scaling (unbiased: error also scales with growth)
            a_eff = 1.0 / (1.0 + z_eff)
            s8_err_z = s8_err_rep * (a_eff**0.55)
            
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run_loocv(self):
        print("="*80)
        print(f"{'KSAU v23.0: Fixed LOO-CV Engine (BAO & Integration)':^80}")
        print("="*80)
        
        survey_names = list(self.surveys.keys())
        loocv_results = []
        
        for i, excluded_name in enumerate(survey_names):
            print(f"\nIteration {i+1}/{len(survey_names)}: Excluding {excluded_name}")
            training_surveys = {name: self.surveys[name] for name in survey_names if name != excluded_name}
            
            res = minimize(self.cost_function, x0=[18.0], args=(training_surveys,), bounds=[(1.0, 100.0)])
            r0_opt = res.x[0]
            
            # Test on excluded survey
            obs = self.surveys[excluded_name]
            z_eff = obs['z_eff']
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff)
            s8_pred_z = self.predict_s8_z(z_eff, r0_opt)
            
            a_eff = 1.0 / (1.0 + z_eff)
            s8_err_z = s8_err_rep * (a_eff**0.55)
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            
            print(f"  Optimized R_cell: {r0_opt:.4f} Mpc/h")
            print(f"  Test Survey: {excluded_name}")
            print(f"  Observed S8(z): {s8_obs_z:.4f}")
            print(f"  Predicted S8(z): {s8_pred_z:.4f}")
            print(f"  Sigma Deviation: {sigma_diff:.2f} sigma")
            
            loocv_results.append({
                "excluded_survey": excluded_name,
                "r0_opt": r0_opt,
                "sigma_diff": sigma_diff,
                "status": "PASSED" if np.abs(sigma_diff) < 1.0 else "FAILED"
            })
            
        print("\n" + "="*80)
        mae_sigma = np.mean([np.abs(r['sigma_diff']) for r in loocv_results])
        for r in loocv_results:
            print(f"{r['excluded_survey']:<15} | R_opt: {r['r0_opt']:6.2f} | Diff: {r['sigma_diff']:6.2f} sig | {r['status']}")
        print(f"Mean Absolute Deviation: {mae_sigma:.4f} sigma")
        print("="*80)

if __name__ == "__main__":
    # Ensure we are in the right directory to import power_spectrum_bao
    import sys
    sys.path.append('v23.0/code')
    engine = LOOCVEngineV23Fixed()
    engine.run_loocv()
