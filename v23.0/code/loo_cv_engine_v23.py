"""
KSAU v23.0: LOO-CV Engine (Data-Exclusion Validation)
=====================================================
Implements Section 1 of the v23.0 Roadmap.
Performs true Leave-One-Out Cross-Validation by excluding each survey
one at a time, re-optimizing the R_cell parameter, and testing prediction
accuracy on the held-out survey.

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
from scipy.optimize import minimize
import os

class LOOCVEngineV23:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.Om0 = self.config['omega_m0']
        self.sigma8_ref = self.config['sigma8']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.gamma_app_derived = self.config['scaling_factors']['gamma_app_derived']
        self.surveys = self.config['survey_data']
        
        # Branching factor (v21.0 inheritance)
        self.B_eff = self.config['filament_branching']['B_eff']
        self.B_pred = self.config['filament_branching']['B_predicted']
        self.F_branching = self.B_pred / self.B_eff
        
        self.beta_fixed = self.config['filament_branching']['D'] # 1.979
        self.Om_ref = self.config['scaling_factors']['omega_m_ref_sigma8']
        self.k_nl_scale = self.config.get('k_nl_scale', 0.1309)
        
    def growth_factor(self, a, om0, gamma):
        return a**gamma

    def get_observed_s8_z(self, s8_obs_reported, z, om0):
        """Convert LCDM-reported S8(0) back to S8(z)."""
        a = 1.0 / (1.0 + z)
        d_lcdm_z = self.growth_factor(a, om0, 0.55)
        d_lcdm_0 = self.growth_factor(1.0, om0, 0.55)
        return s8_obs_reported * (d_lcdm_z / d_lcdm_0)

    def window_function(self, k, r):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def xi_k_z(self, k, z, r0):
        r_z = r0 * (1 + z)**(-self.beta_fixed)
        # Non-linear "knot-entanglement" correction (v23.0 Alpha)
        # Prevents over-suppression at intermediate scales.
        # k_nl_scale (kappa=0.1309) derived from the resonance identity K(4)*kappa=pi
        f_nl = 1.0 / (1.0 + (k * self.k_nl_scale)**2) 
        xi_linear = 0.5 + 0.5 * (1.0 - self.window_function(k, r_z))
        return xi_linear**f_nl

    def predict_s8_z(self, k, z, r0):
        xi = self.xi_k_z(k, z, r0)
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        gamma_k = 0.55 * np.log(om_eff) / np.log(self.Om0)
        
        suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
        s8_ref_z0 = self.sigma8_ref * np.sqrt(self.Om0 / self.Om_ref)
        a = 1.0 / (1.0 + z)
        return s8_ref_z0 * suppression * self.growth_factor(a, self.Om0, gamma_k)

    def cost_function(self, r0, training_surveys):
        chi2 = 0
        for name, obs in training_surveys.items():
            z_eff = obs['z_eff']
            k_eff = obs['k_eff']
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff, self.Om0)
            s8_pred_z = self.predict_s8_z(k_eff, z_eff, r0)
            
            # Error scaling
            a_eff = 1.0 / (1.0 + z_eff)
            growth_ratio_lcdm = self.growth_factor(a_eff, self.Om0, 0.55) / self.growth_factor(1.0, self.Om0, 0.55)
            s8_err_z = s8_err_rep * growth_ratio_lcdm
            
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run_loocv(self):
        print("="*80)
        print(f"{'KSAU v23.0: True LOO-CV Validation Engine':^80}")
        print("="*80)
        
        survey_names = list(self.surveys.keys())
        loocv_results = []
        
        for i, excluded_name in enumerate(survey_names):
            print(f"\nIteration {i+1}/{len(survey_names)}: Excluding {excluded_name}")
            
            # Prepare training set
            training_surveys = {name: self.surveys[name] for name in survey_names if name != excluded_name}
            
            # Optimize R_cell (r0) on training set
            # Expanded bounds to 25.0 to detect saturation vs physical convergence
            res = minimize(self.cost_function, x0=[4.5], args=(training_surveys,), bounds=[(1.0, 25.0)])
            r0_opt = res.x[0]
            
            # Test on excluded survey
            obs = self.surveys[excluded_name]
            z_eff = obs['z_eff']
            k_eff = obs['k_eff']
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff, self.Om0)
            s8_pred_z = self.predict_s8_z(k_eff, z_eff, r0_opt)
            
            a_eff = 1.0 / (1.0 + z_eff)
            growth_ratio_lcdm = self.growth_factor(a_eff, self.Om0, 0.55) / self.growth_factor(1.0, self.Om0, 0.55)
            s8_err_z = s8_err_rep * growth_ratio_lcdm
            
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            
            print(f"  Optimized R_cell: {r0_opt:.4f} Mpc/h")
            print(f"  Test Survey: {excluded_name}")
            print(f"  Observed S8(z): {s8_obs_z:.4f}")
            print(f"  Predicted S8(z): {s8_pred_z:.4f}")
            print(f"  Sigma Deviation: {sigma_diff:.2f} sigma")
            
            loocv_results.append({
                "excluded_survey": excluded_name,
                "r0_opt": r0_opt,
                "s8_obs_z": s8_obs_z,
                "s8_pred_z": s8_pred_z,
                "sigma_diff": sigma_diff,
                "status": "PASSED" if np.abs(sigma_diff) < 1.0 else "FAILED"
            })
            
        print("\n" + "="*80)
        print(f"{'Final LOO-CV Summary':^80}")
        print("-" * 80)
        mae_sigma = np.mean([np.abs(r['sigma_diff']) for r in loocv_results])
        
        for r in loocv_results:
            print(f"{r['excluded_survey']:<15} | R_opt: {r['r0_opt']:5.2f} | Diff: {r['sigma_diff']:6.2f} sig | {r['status']}")
            
        print("-" * 80)
        print(f"Mean Absolute Deviation: {mae_sigma:.4f} sigma")
        
        verdict = "SUCCESS" if mae_sigma < 1.0 else "FAILED"
        print(f"Overall LOO-CV Verdict: {verdict}")
        print("="*80)
        
        # Save results
        output = {
            "mae_sigma": mae_sigma,
            "verdict": verdict,
            "iterations": loocv_results
        }
        
        os.makedirs("v23.0/data", exist_ok=True)
        with open("v23.0/data/loocv_results.json", 'w') as f:
            json.dump(output, f, indent=2)
            
        print("Results saved to v23.0/data/loocv_results.json")

if __name__ == "__main__":
    engine = LOOCVEngineV23()
    engine.run_loocv()
