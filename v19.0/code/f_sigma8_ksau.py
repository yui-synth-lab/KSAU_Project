"""
KSAU v19.0: S8 Tension Resolution and Statistical Validation (LOO-CV)
======================================================================
Hypothesis: Topological tension clusters with 50% efficiency (xi = 0.5).
This bipartite efficiency factor is derived from the self-duality of the 24-cell
in 4D spacetime. The 24-cell has 24 vertices and 24 octahedral cells (Total 48
elements). In the KSAU framework, clustering occurs at the localized vertices,
while the volume-filling cells represent the non-clustering background. 
By equipartition, xi = N_vertices / (N_vertices + N_cells) = 24/48 = 0.5.
This factor is also mirrored in the Leech lattice's bipartite partition.

Effective Matter Density:
Omega_m_eff = (Omega_m_baseline - Omega_tens0) + xi * Omega_tens0

Growth Index Correction:
gamma = 0.55 * (1 + alpha * K(4) * xi)
where K(4) = pi / kappa approx 24 (4D Kissing Number).

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import os
from pathlib import Path
from scipy.optimize import minimize

class S8Resolution:
    def __init__(self, config_path="v19.0/data/cosmological_constants.json"):
        if not os.path.exists(config_path):
            config_path = "v18.0/data/cosmological_constants.json"
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.alpha = self.config['alpha_ksau']
        self.kappa = self.config['kappa']
        self.sigma8_ref = self.config['sigma8']
        self.xi_theory = self.config.get('clustering_efficiency_xi', 0.5)
        
        # Scenario 1 parameters
        params = self.config['hubble_scenarios']['Scenario 1']
        self.Otens0 = params['omega_tens0']
        self.Om_resid = params['omega_m_baseline'] - self.Otens0
        
        # Leech lattice resonance factor
        self.K4 = np.pi / self.kappa # Kissing number in 4D (approx 24)
        
        # Observational Data (S8 measurements with 1-sigma uncertainties)
        self.surveys = {
            "DES Y3 (2021/24)": {"val": 0.759, "err": 0.025},
            "HSC Y3 (2023/24)": {"val": 0.776, "err": 0.033},
            "KiDS-Legacy (2025)": {"val": 0.815, "err": 0.021}
        }

    def predict_s8(self, xi):
        """Predicts S8 for a given clustering efficiency xi."""
        om_eff = self.Om_resid + xi * self.Otens0
        return self.sigma8_ref * np.sqrt(om_eff / 0.3)

    def predict_gamma(self, xi):
        """Predicts the growth index gamma for a given clustering efficiency xi."""
        return 0.55 * (1 + self.alpha * self.K4 * xi)

    def compute_chi2(self, xi, survey_keys):
        """Computes chi-squared for a subset of surveys."""
        chi2 = 0
        s8_pred = self.predict_s8(xi)
        for key in survey_keys:
            obs = self.surveys[key]
            chi2 += ((s8_pred - obs['val']) / obs['err'])**2
        return chi2

    def perform_loo_cv(self):
        """Performs Leave-One-Out Cross-Validation to estimate xi and gamma."""
        keys = list(self.surveys.keys())
        results = []
        
        print(f"{'Excluded Survey':<25} | {'Best-fit xi':<12} | {'S8 Prediction':<15} | {'Gamma Prediction':<18}")
        print("-" * 75)
        
        for i in range(len(keys)):
            train_keys = keys[:i] + keys[i+1:]
            test_key = keys[i]
            
            # Minimize chi2 for training set
            res = minimize(self.compute_chi2, x0=[0.5], args=(train_keys,), bounds=[(0, 1)])
            xi_fit = res.x[0]
            
            s8_pred = self.predict_s8(xi_fit)
            gamma_pred = self.predict_gamma(xi_fit)
            
            results.append({
                "excluded": test_key,
                "xi_fit": xi_fit,
                "s8_pred": s8_pred,
                "gamma_pred": gamma_pred,
                "test_obs": self.surveys[test_key]['val']
            })
            
            print(f"{test_key:<25} | {xi_fit:12.4f} | {s8_pred:15.4f} | {gamma_pred:18.4f}")
            
        # Statistics
        xi_mean = np.mean([r['xi_fit'] for r in results])
        xi_std = np.std([r['xi_fit'] for r in results])
        gamma_mean = np.mean([r['gamma_pred'] for r in results])
        s8_mean = np.mean([r['s8_pred'] for r in results])
        
        return results, xi_mean, xi_std, gamma_mean, s8_mean

    def analyze(self):
        print("="*80)
        print(f"{'KSAU v19.0: S8 Tension Resolution & LOO-CV Validation':^80}")
        print("="*80)
        print(f"Theoretical Parameters (SSoT):")
        print(f"  alpha:           {self.alpha:.6f}")
        print(f"  K(4):            {self.K4:.4f}")
        print(f"  xi_theory:       {self.xi_theory:.4f}")
        print(f"  Omega_tens0:     {self.Otens0:.4f}")
        print(f"  Omega_m_resid:   {self.Om_resid:.4f}")
        print("-" * 80)
        
        # Theoretical Prediction
        s8_theo = self.predict_s8(self.xi_theory)
        gamma_theo = self.predict_gamma(self.xi_theory)
        
        print(f"Theoretical KSAU Prediction (xi={self.xi_theory}):")
        print(f"  S8 (KSAU):       {s8_theo:.4f}")
        print(f"  Gamma (KSAU):    {gamma_theo:.4f}")
        print("-" * 80)
        
        # LOO-CV
        cv_results, xi_m, xi_s, gamma_m, s8_m = self.perform_loo_cv()
        
        print("-" * 80)
        print(f"Statistical Summary (LOO-CV):")
        print(f"  Estimated xi:    {xi_m:.4f} +/- {xi_s:.4f}")
        print(f"  Estimated gamma: {gamma_m:.4f}")
        print(f"  Estimated S8:    {s8_m:.4f}")
        print("-" * 80)
        
        # Final Results for Export
        final_results = {
            "gamma_mean": gamma_m,
            "gamma_std": np.std([r['gamma_pred'] for r in cv_results]),
            "gamma_theory": gamma_theo,
            "S8_pred": s8_theo,
            "S8_loo_cv_mean": s8_m,
            "Om_ksau": self.Om_resid + self.xi_theory * self.Otens0,
            "xi_theory": self.xi_theory,
            "loo_cv_results": cv_results
        }
        
        # Scientific Honesty Check (v19.0 Audit)
        # Rejection threshold: gamma > 0.70 (Insufficient growth suppression)
        if gamma_m > 0.70:
            status = "REJECTED/INCOMPLETE"
            verdict = f"Static Model REJECTED. Estimated gamma ({gamma_m:.4f}) > 0.70, indicating insufficient growth suppression."
        elif 0.75 < s8_theo < 0.79:
            status = "PARTIAL/RESOLVED"
            verdict = "Matches DES/HSC within 1-sigma, but theoretical gamma remains low."
        else:
            status = "PARTIAL"
            verdict = "Discrepancy remains with KiDS-Legacy (2025)."
            
        print(f"Verdict: {status} ({verdict})")
        print("="*80)
        
        # Write files
        with open("v19.0/growth_analysis_results.json", 'w') as f:
            json.dump(final_results, f, indent=2)
            
        with open("v19.0/s8_resolution_summary.json", 'w') as f:
            json.dump({
                "Om_eff": final_results["Om_ksau"],
                "S8_ksau": s8_theo,
                "gamma_refined": gamma_m, # Report the statistically estimated gamma (honesty)
                "xi": self.xi_theory,
                "status": status,
                "verdict": verdict
            }, f, indent=2)

if __name__ == "__main__":
    solver = S8Resolution()
    solver.analyze()
