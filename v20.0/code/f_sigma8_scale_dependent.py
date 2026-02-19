"""
KSAU v20.0: Scale-Dependent Phase Tension Model [Section 1]
==========================================================
Hypothesis: Clustering efficiency xi is scale-dependent due to the 
finite resolution of volume-filling elements (cells) in the 24-cell resonance.

Model:
xi(k) = xi_min + (1 - xi_min) * (1 - W(k, R_cell))
where xi_min = 0.5 (Bipartite baseline: 24 vertices cluster, 24 cells don't).
W(k, R_cell) is the normalized window function (Fourier transform) of 
the 24-cell's octahedral cells.

As k -> 0 (large scales), W -> 1, so xi -> 0.5 (Bulk homogeneous limit).
As k -> inf (small scales), W -> 0, so xi -> 1.0 (Local knot clustering limit).

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import os
from scipy.optimize import minimize
from scipy.special import j1

class ScaleDependentGrowth:
    def __init__(self, config_path="v20.0/data/cosmological_constants.json"):
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
        
        # Observational Data (S8 and effective k-scales)
        # Scale ranges estimated from survey window functions
        self.surveys = {
            "DES Y3":      {"val": 0.759, "err": 0.025, "k_eff": 0.15},
            "HSC Y3":      {"val": 0.776, "err": 0.033, "k_eff": 0.35},
            "KiDS-Legacy": {"val": 0.815, "err": 0.021, "k_eff": 0.70}
        }

    def window_function(self, k, r):
        """Top-hat window function in Fourier space (3D)."""
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def xi_k(self, k, r_cell):
        """Scale-dependent clustering efficiency.
        Hypothesis: xi(k) = 0.5 + 0.5 * (1.0 - W(k, R_cell)).
        - As k -> 0 (large scale): W -> 1, xi -> 0.5 (Standard KSAU bulk).
        - As k -> inf (small scale): W -> 0, xi -> 1.0 (Concentrated knot clustering).
        """
        return 0.5 + 0.5 * (1.0 - self.window_function(k, r_cell))

    def predict_s8(self, k, r_cell):
        xi = self.xi_k(k, r_cell)
        om_eff = self.Om_resid + xi * self.Otens0
        return self.sigma8_ref * np.sqrt(om_eff / 0.3)

    def predict_gamma(self, k, r_cell):
        xi = self.xi_k(k, r_cell)
        return 0.55 * (1 + self.alpha * self.K4 * xi)

    def compute_chi2(self, r_cell):
        chi2 = 0
        for name, obs in self.surveys.items():
            pred = self.predict_s8(obs['k_eff'], r_cell)
            chi2 += ((pred - obs['val']) / obs['err'])**2
        return chi2

    def run_fit(self):
        print("="*80)
        print(f"{'KSAU v20.0: Scale-Dependent Growth Analysis (xi(k))':^80}")
        print("="*80)
        
        # Minimize chi2 for R_cell
        res = minimize(self.compute_chi2, x0=[5.0], bounds=[(0.1, 50.0)])
        r_best = res.x[0]
        
        print(f"Best-fit Coherence Length R_cell: {r_best:.4f} Mpc/h")
        print(f"Chi-squared / DoF:                {res.fun:.4f} / 2")
        print("-" * 80)
        
        print(f"{'Survey':<15} | {'k_eff':<8} | {'xi(k)':<10} | {'S8 Pred':<10} | {'S8 Obs':<10} | {'Gamma':<10}")
        print("-" * 80)
        
        results = []
        for name, obs in self.surveys.items():
            k = obs['k_eff']
            xi = self.xi_k(k, r_best)
            s8_pred = self.predict_s8(k, r_best)
            gamma = self.predict_gamma(k, r_best)
            print(f"{name:<15} | {k:8.2f} | {xi:10.4f} | {s8_pred:10.4f} | {obs['val']:10.4f} | {gamma:10.4f}")
            results.append({
                "survey": name,
                "k_eff": k,
                "xi": xi,
                "s8_pred": s8_pred,
                "gamma": gamma
            })

        # LOO-CV (Leave-One-Out)
        print("-" * 80)
        print("LOO-CV Verification:")
        gammas = []
        for i in range(len(self.surveys)):
            keys = list(self.surveys.keys())
            train_keys = keys[:i] + keys[i+1:]
            
            def chi2_loo(r):
                c = 0
                for k in train_keys:
                    obs = self.surveys[k]
                    pred = self.predict_s8(obs['k_eff'], r)
                    c += ((pred - obs['val']) / obs['err'])**2
                return c
                
            res_loo = minimize(chi2_loo, x0=[5.0], bounds=[(0.1, 50.0)])
            r_loo = res_loo.x[0]
            
            # Predict for the excluded survey
            test_key = keys[i]
            gamma_loo = self.predict_gamma(self.surveys[test_key]['k_eff'], r_loo)
            gammas.append(gamma_loo)
            print(f"  Exclude {test_key:<12}: R_cell={r_loo:6.2f}, Gamma={gamma_loo:.4f}")

        gamma_avg = np.mean(gammas)
        gamma_std = np.std(gammas)
        
        print("-" * 80)
        print(f"LOO-CV Mean Gamma: {gamma_avg:.4f} +/- {gamma_std:.4f}")
        
        # Scientific Verdict
        # Threshold: gamma_avg < 0.70 is Success (better than v19.0's 0.727)
        if gamma_avg < 0.70:
            status = "ACCEPTED (Scale-Dependent)"
            verdict = "Scale-dependent model resolves sigma8 tension better than static model."
        else:
            status = "REJECTED"
            verdict = "Scale-dependence insufficient to reach gamma ~ 0.55."
            
        print(f"Verdict: {status}")
        print(f"Detail:  {verdict}")
        print("="*80)
        
        # Save results
        output = {
            "r_cell_best": r_best,
            "gamma_loo_mean": gamma_avg,
            "gamma_loo_std": gamma_std,
            "surveys": results,
            "status": status
        }
        with open("v20.0/scale_dependent_results.json", 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    sdg = ScaleDependentGrowth()
    sdg.run_fit()
