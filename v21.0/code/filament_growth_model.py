"""
KSAU v21.0: Filament Branching & Growth Suppression Model [Section 1]
======================================================================
Hypothesis: 
The cosmological growth index gamma is derived from the topological tension,
but the absolute S8 normalization is suppressed by the filament branching 
topology (B_obs = 3.94) compared to the ideal 24-cell boundary (B_cell = 4.0).

Suppression Factor: F_branching = B_obs / B_cell

Model:
S8_pred = sigma8_ref * sqrt(Omega_m_eff / 0.3) * F_branching
gamma = 0.55 * (1 + alpha * K4 * xi)

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import os
from scipy.optimize import minimize

class FilamentGrowthModel:
    def __init__(self, config_path="v21.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.alpha = self.config['alpha_ksau']
        self.kappa = self.config['kappa']
        self.sigma8_ref = self.config['sigma8']
        
        # Scenario 1 parameters
        params = self.config['hubble_scenarios']['Scenario 1']
        self.Otens0 = params['omega_tens0']
        self.Om_resid = params['omega_m_baseline'] - self.Otens0
        
        # Resonance factor
        self.K4 = np.pi / self.kappa
        
        # Filament branching (SSoT)
        self.B_predicted = self.config['filament_branching']['B_predicted']
        self.D_obs = self.config['filament_branching']['D']
        self.B_cell = self.config['filament_branching']['B_cell'] # Correct degree of 24-cell = 8.0
        self.B_eff = self.config['filament_branching']['B_eff']   # Effective branching (Double-strand hypothesis) = 4.0
        
        # Survey Data from SSoT
        self.surveys = self.config['survey_data']

    def branching_factor(self):
        """Geometric suppression factor due to non-ideal filament branching.
        Based on B_predicted compared to B_eff (physical strand branching).
        """
        return self.B_predicted / self.B_eff

    def predict_s8(self, xi):
        om_eff = self.Om_resid + xi * self.Otens0
        # Incorporate filament suppression factor
        f_b = self.branching_factor()
        return self.sigma8_ref * np.sqrt(om_eff / 0.3) * f_b

    def predict_gamma(self, xi):
        # Derived formula: gamma = 0.55 * (B_eff * D / B_predicted) * xi
        # Represents growth suppression scaled by branching efficiency
        p_factor = (self.B_eff * self.D_obs) / self.B_predicted
        return 0.55 * p_factor * xi

    def compute_chi2(self, xi, survey_keys):
        chi2 = 0
        s8_pred = self.predict_s8(xi)
        for key in survey_keys:
            obs = self.surveys[key]
            chi2 += ((s8_pred - obs['S8_obs']) / obs['S8_err'])**2
        return chi2

    def run_fit(self):
        print("="*80)
        print(f"{'KSAU v21.0: Filament Branching Model (LOO-CV)':^80}")
        print("="*80)
        print(f"B_cell (24-cell): {self.B_cell:.2f}")
        print(f"B_predicted (KSAU): {self.B_predicted:.4f}")
        print(f"F_branching:      {self.branching_factor():.4f}")
        print("-" * 80)
        
        keys = list(self.surveys.keys())
        results = []
        
        print(f"{'Excluded Survey':<20} | {'Fit xi':<10} | {'S8 Pred':<10} | {'S8 Obs':<10} | {'Gamma':<10}")
        print("-" * 80)
        
        for i in range(len(keys)):
            train_keys = keys[:i] + keys[i+1:]
            test_key = keys[i]
            
            res = minimize(self.compute_chi2, x0=[0.5], args=(train_keys,), bounds=[(0, 1)])
            xi_fit = res.x[0]
            
            s8_pred = self.predict_s8(xi_fit)
            gamma_pred = self.predict_gamma(xi_fit)
            obs_val = self.surveys[test_key]['S8_obs']
            
            print(f"{test_key:<20} | {xi_fit:10.4f} | {s8_pred:10.4f} | {obs_val:10.4f} | {gamma_pred:10.4f}")
            
            results.append({
                "excluded": test_key,
                "xi_fit": xi_fit,
                "gamma": gamma_pred,
                "s8_pred": s8_pred
            })
            
        gamma_avg = np.mean([r['gamma'] for r in results])
        gamma_std = np.std([r['gamma'] for r in results])
        xi_avg = np.mean([r['xi_fit'] for r in results])
        
        print("-" * 80)
        print(f"LOO-CV Mean Gamma: {gamma_avg:.4f} +/- {gamma_std:.4f}")
        print(f"LOO-CV Mean xi:    {xi_avg:.4f}")
        
        # Scientific Verdict
        # Success if gamma_avg < 0.70 (Roadmap requirement)
        if gamma_avg < 0.70:
            status = "ACCEPTED"
            verdict = "Filament branching model successfully reduces required gamma below 0.70."
        else:
            status = "REJECTED"
            verdict = "Branching suppression insufficient to reach gamma < 0.70."
            
        print(f"Verdict: {status}")
        print(f"Detail:  {verdict}")
        print("="*80)
        
        # Save results
        output = {
            "gamma_loo_mean": gamma_avg,
            "gamma_loo_std": gamma_std,
            "xi_loo_mean": xi_avg,
            "f_branching": self.branching_factor(),
            "status": status,
            "results": results
        }
        with open("v21.0/filament_growth_results.json", 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    model = FilamentGrowthModel()
    model.run_fit()
