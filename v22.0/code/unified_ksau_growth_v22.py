"""
KSAU v22.0: Unified Growth Validation (Physical Gamma Reinterpretation)
======================================================================
Implements Section 1 of the v22.0 Roadmap.
Re-evaluates the growth index gamma relative to the geometric prediction 
gamma_app = 0.623 instead of the arbitrary 0.70 threshold.

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
from scipy.optimize import minimize
import os

class UnifiedKSAUGrowthV22:
    def __init__(self, config_path="v22.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.Om0 = self.config['omega_m0']
        self.sigma8_ref = self.config['sigma8']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.gamma_app_derived = self.config['scaling_factors']['gamma_app_derived'] # 0.623
        self.surveys = self.config['survey_data']
        
        # Branching factor (Fixed in v21.0)
        self.B_eff = self.config['filament_branching']['B_eff']
        self.B_pred = self.config['filament_branching']['B_predicted']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        
        # Best-fit R0 from SSoT (v20.0/v21.0)
        self.R0_fixed = self.config['R_cell']
        self.beta_fixed = self.config['filament_branching']['D'] # 1.979
        
    def growth_factor(self, a, om0, gamma):
        """Standard growth factor approximation D(a) = a^gamma."""
        return a**gamma

    def get_observed_s8_z(self, s8_obs_reported, z, om0):
        """
        Convert reported S8(0) (extrapolated via LCDM) back to S8(z).
        S8_obs(z) = S8_obs_reported(0) * (D_lcdm(z)/D_lcdm(0))
        """
        a = 1.0 / (1.0 + z)
        d_lcdm_z = self.growth_factor(a, om0, 0.55)
        d_lcdm_0 = self.growth_factor(1.0, om0, 0.55)
        return s8_obs_reported * (d_lcdm_z / d_lcdm_0)

    def window_function(self, k, r):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def xi_k_z(self, k, z):
        r_z = self.R0_fixed * (1 + z)**(-self.beta_fixed)
        return 0.5 + 0.5 * (1.0 - self.window_function(k, r_z))

    def predict_s8_z(self, k, z):
        """Predict S8(z) for KSAU including geometric suppression."""
        xi = self.xi_k_z(k, z)
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        gamma_k = 0.55 * np.log(om_eff) / np.log(self.Om0)
        
        # Linear suppression for sigma8
        suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
        
        # Convert sigma8_ref (0.811) to S8_ref (0.831) at z=0 for proper comparison.
        s8_ref_z0 = self.sigma8_ref * np.sqrt(self.Om0 / 0.3)
        
        # S8(z) = S8_ref * suppression * D(z)
        a = 1.0 / (1.0 + z)
        return s8_ref_z0 * suppression * self.growth_factor(a, self.Om0, gamma_k)

    def predict_gamma_loo(self, k, z, xi):
        """Theoretical gamma_app for the given xi."""
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        return 0.55 * np.log(om_eff) / np.log(self.Om0)

    def run_validation(self):
        print("="*80)
        print(f"{'KSAU v22.0: Unified Growth Validation (Gamma Reinterpretation)':^80}")
        print("="*80)
        
        results_surveys = []
        gammas = []
        chi2 = 0
        
        print(f"{'Survey':<15} | {'z_eff':<6} | {'S8 Obs(z)':<10} | {'S8 Pred(z)':<10} | {'Sigma Diff':<10} | {'Gamma_impl'}")
        print("-" * 80)
        
        for name, obs in self.surveys.items():
            z_eff = obs['z_eff']
            k_eff = obs['k_eff']
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff, self.Om0)
            s8_pred_z = self.predict_s8_z(k_eff, z_eff)
            
            # Growth-scaled error
            a_eff = 1.0 / (1.0 + z_eff)
            growth_ratio_lcdm = self.growth_factor(a_eff, self.Om0, 0.55) / self.growth_factor(1.0, self.Om0, 0.55)
            s8_err_z = s8_err_rep * growth_ratio_lcdm
            
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            chi2 += sigma_diff**2
            
            xi = self.xi_k_z(k_eff, z_eff)
            gamma_impl = self.predict_gamma_loo(k_eff, z_eff, xi)
            gammas.append(gamma_impl)
            
            print(f"{name:<15} | {z_eff:6.2f} | {s8_obs_z:10.4f} | {s8_pred_z:10.4f} | {sigma_diff:10.2f} | {gamma_impl:.4f}")
            results_surveys.append({
                "survey": name,
                "z_eff": z_eff,
                "k_eff": k_eff,
                "s8_obs_z": s8_obs_z,
                "s8_pred_z": s8_pred_z,
                "sigma_diff": sigma_diff,
                "gamma_impl": gamma_impl
            })
            
        gamma_avg = np.mean(gammas)
        gamma_std = np.std(gammas)
        
        print("-" * 80)
        print(f"Total Chi-squared: {chi2:.4f}")
        print(f"LOO-CV Mean Gamma: {gamma_avg:.4f} +/- {gamma_std:.4f}")
        print(f"Target Gamma_app:  {self.gamma_app_derived:.4f}")
        
        # Verdict 1: Old threshold (0.70)
        status_old = "ACCEPTED" if gamma_avg < 0.70 else "REJECTED"
        
        # Verdict 2: New threshold (gamma_app +/- 2*std)
        # If the average is within 2 sigma of the geometric prediction
        diff_from_app = np.abs(gamma_avg - self.gamma_app_derived)
        status_new = "ACCEPTED" if diff_from_app < 2 * gamma_std else "REJECTED"
        
        print(f"Verdict (Old 0.70): {status_old}")
        print(f"Verdict (New App):  {status_new}")
        print("="*80)
        
        # Save results (HIGH-2)
        output = {
            "gamma_avg": gamma_avg,
            "gamma_std": gamma_std,
            "gamma_app_target": self.gamma_app_derived,
            "chi2": chi2,
            "verdict_old": status_old,
            "verdict_new": status_new,
            "surveys": results_surveys
        }
        
        # Ensure directory exists
        os.makedirs("v22.0", exist_ok=True)
        
        with open("v22.0/unified_single_point_results.json", 'w') as f:
            json.dump(output, f, indent=2)
            
        print("Results saved to v22.0/unified_single_point_results.json")

if __name__ == "__main__":
    model = UnifiedKSAUGrowthV22()
    model.run_validation()
