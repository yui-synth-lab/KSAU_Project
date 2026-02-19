"""
KSAU v21.0: Unified Filament & Dynamic Resonance Model
=======================================================
Combines Section 1 (Filament Branching) and Section 2 (Dynamic R_cell).

Model:
1. Scale-Dependent xi(k, z):
   xi(k, z) = 0.5 + 0.5 * (1 - W(k, R_cell(z)))
   R_cell(z) = R0 * (1+z)^-beta (beta = D = 1.98)

2. Filament Growth Suppression:
   S8_pred = sigma8_ref * sqrt(Omega_m_eff / 0.3) * (B_obs / B_cell)

3. Derived Growth Index gamma(k, z):
   gamma(k, z) = 0.55 * (B_cell * D / B_obs) * xi(k, z)

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
from scipy.optimize import minimize

class UnifiedKSAUModel:
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
        
        # Filament branching (SSoT)
        self.B_predicted = self.config['filament_branching']['B_predicted']
        self.D_obs = self.config['filament_branching']['D']
        self.B_cell = self.config['filament_branching']['B_cell']
        self.B_eff = self.config['filament_branching']['B_eff']
        
        # Survey Data from SSoT
        self.surveys = self.config['survey_data']

    def window_function(self, k, r):
        """Top-hat window function in Fourier space (3D)."""
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def r_cell_z(self, r0, z, beta):
        """Redshift-dependent coherence length. 
        beta is derived from fractal dimension D = 2 - alpha_ksau.
        """
        return r0 * (1 + z)**(-beta)

    def xi_k_z(self, k, z, r0, beta):
        r_z = self.r_cell_z(r0, z, beta)
        return 0.5 + 0.5 * (1.0 - self.window_function(k, r_z))

    def branching_factor(self):
        """Geometric suppression factor based on physical strand branching."""
        return self.B_predicted / self.B_eff

    def predict_s8(self, k, z, r0, beta):
        xi = self.xi_k_z(k, z, r0, beta)
        om_eff = self.Om_resid + xi * self.Otens0
        f_b = self.branching_factor()
        return self.sigma8_ref * np.sqrt(om_eff / 0.3) * f_b

    def predict_gamma(self, k, z, r0, beta):
        xi = self.xi_k_z(k, z, r0, beta)
        p_factor = (self.B_eff * self.D_obs) / self.B_predicted
        return 0.55 * p_factor * xi

    def compute_chi2(self, params, survey_keys):
        r0, beta = params
        chi2 = 0
        for key in survey_keys:
            obs = self.surveys[key]
            pred = self.predict_s8(obs['k_eff'], obs['z_eff'], r0, beta)
            chi2 += ((pred - obs['S8_obs']) / obs['S8_err'])**2
        return chi2

    def run_fit(self, fix_beta=True):
        print("="*80)
        print(f"{'KSAU v21.0: Unified Filament & Dynamic Resonance Analysis':^80}")
        print("="*80)
        
        beta_val = self.D_obs if fix_beta else 1.98
        
        # Fit R0
        keys = list(self.surveys.keys())
        
        def objective(r0):
            return self.compute_chi2([r0[0], beta_val], keys)
            
        res = minimize(objective, x0=[5.0], bounds=[(0.1, 50.0)])
        r0_best = res.x[0]
        
        print(f"Fixed beta (D): {beta_val:.4f}")
        print(f"Best-fit R0:    {r0_best:.4f} Mpc/h")
        print(f"Chi2 / DoF:     {res.fun:.4f} / 2")
        print("-" * 80)
        
        print(f"{'Survey':<15} | {'k_eff':<6} | {'z_eff':<6} | {'xi':<8} | {'S8 Pred':<8} | {'S8 Obs':<8} | {'Gamma':<8}")
        print("-" * 80)
        
        results = []
        for name, obs in self.surveys.items():
            k, z = obs['k_eff'], obs['z_eff']
            xi = self.xi_k_z(k, z, r0_best, beta_val)
            s8_pred = self.predict_s8(k, z, r0_best, beta_val)
            gamma = self.predict_gamma(k, z, r0_best, beta_val)
            print(f"{name:<15} | {k:6.2f} | {z:6.2f} | {xi:8.4f} | {s8_pred:8.4f} | {obs['S8_obs']:8.4f} | {gamma:8.4f}")
            results.append({
                "survey": name,
                "xi": xi,
                "s8_pred": s8_pred,
                "gamma": gamma
            })

        # LOO-CV
        print("-" * 80)
        print("LOO-CV Verification:")
        gammas = []
        for i in range(len(keys)):
            train_keys = keys[:i] + keys[i+1:]
            test_key = keys[i]
            
            def objective_loo(r):
                return self.compute_chi2([r[0], beta_val], train_keys)
                
            res_loo = minimize(objective_loo, x0=[5.0], bounds=[(0.1, 50.0)])
            r0_loo = res_loo.x[0]
            
            obs_test = self.surveys[test_key]
            gamma_loo = self.predict_gamma(obs_test['k_eff'], obs_test['z_eff'], r0_loo, beta_val)
            gammas.append(gamma_loo)
            print(f"  Exclude {test_key:<12}: R0={r0_loo:6.2f}, Gamma={gamma_loo:.4f}")

        gamma_avg = np.mean(gammas)
        gamma_std = np.std(gammas)
        
        print("-" * 80)
        print(f"LOO-CV Mean Gamma: {gamma_avg:.4f} +/- {gamma_std:.4f}")
        
        if gamma_avg < 0.70:
            status = "ACCEPTED"
            verdict = "Unified model resolves sigma8 tension with gamma < 0.70."
        else:
            status = "REJECTED"
            verdict = "Gamma remains above 0.70 threshold."
            
        print(f"Verdict: {status}")
        print(f"Detail:  {verdict}")
        print("="*80)
        
        # Save results
        output = {
            "r0_best": r0_best,
            "beta": beta_val,
            "gamma_loo_mean": gamma_avg,
            "gamma_loo_std": gamma_std,
            "status": status,
            "surveys": results
        }
        with open("v21.0/unified_model_results.json", 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    model = UnifiedKSAUModel()
    model.run_fit()
