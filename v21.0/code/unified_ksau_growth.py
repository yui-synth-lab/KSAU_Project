import numpy as np
import json
import os

from scipy.integrate import quad

class UnifiedKSAUGrowth:
    def __init__(self, config_path="v21.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.sigma8_ref = self.config['sigma8'] # Baseline sigma8 (Planck-like)
        self.alpha = self.config['alpha_ksau']
        self.kappa = self.config['kappa']
        self.K4 = np.pi / self.kappa
        
        # Scenario 1 (Fixed in SSoT)
        params = self.config['hubble_scenarios']['Scenario 1']
        self.Otens0 = params['omega_tens0']
        self.Om0 = params['omega_m_baseline']
        
        # Derived Constants (No fitting)
        self.xi = 0.5 # Equipartition baseline
        self.B_predicted = self.config['filament_branching']['B_predicted']
        self.B_eff = self.config['filament_branching']['B_eff']
        self.F_branching = self.B_predicted / self.B_eff # Suppression factor
        
        # Survey Data
        self.surveys = self.config['survey_data']

    def omega_m_a(self, a, om0):
        """Matter density at scale factor a."""
        den = om0 * a**(-3) + (1 - om0)
        return om0 * a**(-3) / den

    def growth_integrand(self, x, om0, gamma):
        """Integrand for the growth factor D(a)."""
        return (self.omega_m_a(x, om0)**gamma - 1) / x

    def growth_factor(self, a, om0, gamma):
        """Linear growth factor D(a) normalized to D(a)->a as a->0."""
        integral, _ = quad(self.growth_integrand, 0, a, args=(om0, gamma))
        return a * np.exp(integral)

    def predict_s8_dynamic(self, z, om0, gamma):
        """Predict S8 at redshift z using integrated growth factor."""
        a = 1.0 / (1.0 + z)
        
        # KSAU growth (gamma_app)
        d_ksau_z = self.growth_factor(a, om0, gamma)
        d_ksau_0 = self.growth_factor(1.0, om0, gamma)
        
        # Effective Om suppression at z=0
        om_eff_0 = (om0 - self.Otens0) + self.xi * self.Otens0
        suppression = np.sqrt(om_eff_0 / om0) * self.F_branching
        
        # S8_pred(z) = S8_pred(0) * (D_ksau(z)/D_ksau(0))
        s8_pred_0 = self.sigma8_ref * suppression
        return s8_pred_0 * (d_ksau_z / d_ksau_0)

    def get_observed_s8_z(self, s8_obs_reported, z, om0):
        """
        Convert reported S8(0) (extrapolated via LCDM) back to S8(z).
        S8_obs(z) = S8_obs_reported(0) * (D_lcdm(z)/D_lcdm(0))
        """
        a = 1.0 / (1.0 + z)
        d_lcdm_z = self.growth_factor(a, om0, 0.55)
        d_lcdm_0 = self.growth_factor(1.0, om0, 0.55)
        return s8_obs_reported * (d_lcdm_z / d_lcdm_0)

    def derive_gamma_app(self, om_eff):
        """Derived apparent growth index."""
        return 0.55 * np.log(om_eff) / np.log(self.Om0)

    def run_validation(self):
        print("="*80)
        print(f"{'KSAU v21.0: Unified Growth Validation (Dynamic Consistency)':^80}")
        print("="*80)
        
        om_eff_0 = (self.Om0 - self.Otens0) + self.xi * self.Otens0
        gamma_app = self.derive_gamma_app(om_eff_0)
        
        print(f"Baseline Om:      {self.Om0:.4f}")
        print(f"Effective Om:     {om_eff_0:.4f}")
        print(f"Filament Supp.:   {self.F_branching:.4f}")
        print(f"Apparent Gamma:   {gamma_app:.4f}")
        print("-" * 80)
        
        print(f"{'Survey':<15} | {'z_eff':<6} | {'S8(z) Obs':<10} | {'S8(z) Pred':<10} | {'Error (sigma)':<10}")
        print("-" * 80)
        
        chi2 = 0
        results_surveys = []
        for name, obs in self.surveys.items():
            s8_obs_rep = obs['S8_obs']
            s8_err_rep = obs['S8_err']
            z_eff = obs['z_eff']
            
            # S8(z) values
            s8_obs_z = self.get_observed_s8_z(s8_obs_rep, z_eff, self.Om0)
            s8_pred_z = self.predict_s8_dynamic(z_eff, self.Om0, gamma_app)
            
            # We assume the error also scales roughly with the growth factor
            a_eff = 1.0 / (1.0 + z_eff)
            growth_ratio_lcdm = self.growth_factor(a_eff, self.Om0, 0.55) / self.growth_factor(1.0, self.Om0, 0.55)
            s8_err_z = s8_err_rep * growth_ratio_lcdm
            
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            chi2 += sigma_diff**2
            print(f"{name:<15} | {z_eff:6.2f} | {s8_obs_z:10.4f} | {s8_pred_z:10.4f} | {sigma_diff:10.2f}")
            results_surveys.append({
                "survey": name,
                "z_eff": z_eff,
                "s8_obs_z": s8_obs_z,
                "s8_pred_z": s8_pred_z,
                "gamma_app": gamma_app
            })
            
        print("-" * 80)
        print(f"Total Chi-squared: {chi2:.4f}")
        print(f"Reduced Chi-sq:    {chi2/len(self.surveys):.4f}")
        
        # Also report the implied S8(0) for comparison with standard LCDM Planck
        suppression = np.sqrt(om_eff_0 / self.Om0) * self.F_branching
        s8_pred_0 = self.sigma8_ref * suppression
        print(f"Implied S8(0) KSAU: {s8_pred_0:.4f}")
        
        # Save results
        output = {
            "gamma_app": gamma_app,
            "s8_pred_0": s8_pred_0,
            "chi2": chi2,
            "status": "SINGLE_POINT_PREDICTION_NO_LOO-CV",
            "surveys": results_surveys
        }
        with open("v21.0/unified_model_results.json", 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    model = UnifiedKSAUGrowth()
    model.run_validation()
