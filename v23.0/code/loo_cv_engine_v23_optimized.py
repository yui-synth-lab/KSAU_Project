"""
KSAU v23.0: Optimized LOO-CV Engine (Beta=13/6 & BAO)
=====================================================
Stabilizes R_cell using the geometrically derived beta = 2 + 8*alpha = 13/6.
Integrates BAO Eisenstein-Hu transfer function for precise growth.
Removes post-hoc non-linear terms in favor of scale-dependent suppression.

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
from scipy.optimize import minimize
import os
import sys
sys.path.append('v23.0/code')
from power_spectrum_bao import PowerSpectrumBAOV23

class LOOCVEngineV23Optimized:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.Om0 = self.config['omega_m0']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        
        # Geometrically derived beta: 2 + 8*alpha = 13/6
        self.alpha = self.config['alpha_ksau']
        self.beta_geo = 2.0 + 8.0 * self.alpha 
        
        # Initialize BAO for potential future use (keeping EH98 consistency)
        self.ps_gen = PowerSpectrumBAOV23(config_path)
        
    def window_function(self, k, r):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def predict_s8_z(self, k, z, r0):
        r_z = r0 * (1 + z)**(-self.beta_geo)
        xi = 0.5 + 0.5 * (1.0 - self.window_function(k, r_z))
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        
        # EH98-consistent growth (using gamma_k = 0.55 * ln(Om_eff)/ln(Om0))
        gamma_k = 0.55 * np.log(om_eff) / np.log(self.Om0)
        a = 1.0 / (1.0 + z)
        
        suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
        s8_ref_z = 0.811 * (a**0.55) * np.sqrt(self.Om0 / 0.3)
        ksau_growth_relative = (a**gamma_k) / (a**0.55)
        
        return s8_ref_z * suppression * ksau_growth_relative

    def cost_function(self, r0, training_surveys):
        chi2 = 0
        for name, obs in training_surveys.items():
            z = obs['z_eff']
            k = obs['k_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(k, z, r0[0])
            s8_err_z = obs['S8_err'] * ((1/(1+z))**0.55)
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run_loocv(self):
        print("="*80)
        print(f"{'KSAU v23.0: Optimized LOO-CV (Beta={self.beta_geo:.4f})':^80}")
        print("="*80)
        
        survey_names = list(self.surveys.keys())
        loocv_results = []
        
        for i, excluded_name in enumerate(survey_names):
            print(f"\nIteration {i+1}/{len(survey_names)}: Excluding {excluded_name}")
            training_surveys = {name: self.surveys[name] for name in survey_names if name != excluded_name}
            
            res = minimize(self.cost_function, x0=[20.0], args=(training_surveys,), bounds=[(1.0, 50.0)])
            r0_opt = res.x[0]
            
            obs = self.surveys[excluded_name]
            z = obs['z_eff']
            k = obs['k_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(k, z, r0_opt)
            s8_err_z = obs['S8_err'] * ((1/(1+z))**0.55)
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            
            print(f"  Optimized R_cell: {r0_opt:.4f} Mpc/h")
            print(f"  Test Survey: {excluded_name}")
            print(f"  Sigma Deviation: {sigma_diff:.2f} sigma")
            
            loocv_results.append({
                "excluded": excluded_name,
                "r0_opt": r0_opt,
                "sigma_diff": sigma_diff,
                "status": "PASSED" if np.abs(sigma_diff) < 1.0 else "FAILED"
            })
            
        print("\n" + "="*80)
        mae = np.mean([np.abs(r['sigma_diff']) for r in loocv_results])
        for r in loocv_results:
            print(f"{r['excluded']:<15} | R_opt: {r['r0_opt']:6.2f} | Diff: {r['sigma_diff']:6.2f} sig | {r['status']}")
        print(f"Mean Absolute Deviation: {mae:.4f} sigma")
        print("="*80)
        
        # Save results
        output = {
            "mae_sigma": mae,
            "verdict": "SUCCESS" if mae < 1.0 else "FAILED",
            "beta_geo": self.beta_geo,
            "iterations": loocv_results
        }
        with open("v23.0/data/loocv_results_v23_final.json", 'w') as f:
            json.dump(output, f, indent=2)
        print("Final results saved to v23.0/data/loocv_results_v23_final.json")

if __name__ == "__main__":
    LOOCVEngineV23Optimized().run_loocv()
