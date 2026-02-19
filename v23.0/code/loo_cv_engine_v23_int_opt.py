
import numpy as np
import json
from scipy.optimize import minimize
from scipy.integrate import quad
import sys
sys.path.append('v23.0/code')
from power_spectrum_bao import PowerSpectrumBAOV23

class LOOCVIntegrationOptimized:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.Om0 = self.config['omega_m0']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        self.ps_gen = PowerSpectrumBAOV23(config_path)
        self.ns = self.config['n_s']
        
        # New "Best Fit" beta for integration (derived from search)
        self.beta_geo = 2.3916 
        
        self.A_norm = self.calculate_normalization()

    def window_tophat(self, k, r=8.0):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def calculate_normalization(self):
        def integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            return (k**2 / (2 * np.pi**2)) * (k**self.ns * T**2) * self.window_tophat(k, 8.0)**2
        integral, _ = quad(integrand, 1e-4, 10.0, limit=100)
        return 0.811**2 / integral

    def predict_s8_z(self, z, r0):
        a = 1.0 / (1.0 + z)
        r_z = r0 * (1 + z)**(-self.beta_geo)
        def integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            xi = 0.5 + 0.5 * (1.0 - self.window_tophat(k, r_z))
            om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
            gamma_k = 0.55 * np.log(om_eff) / np.log(self.Om0)
            d_z = a**gamma_k
            suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
            pk = self.A_norm * k**self.ns * T**2 * (d_z * suppression)**2
            return (k**2 / (2 * np.pi**2)) * pk * self.window_tophat(k, 8.0)**2
        sig8_sq, _ = quad(integrand, 1e-4, 10.0, limit=100)
        return np.sqrt(sig8_sq) * np.sqrt(self.Om0 / 0.3)

    def cost(self, r0, training_surveys):
        chi2 = 0
        for name, obs in training_surveys.items():
            z = obs['z_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(z, r0[0])
            s8_err_z = obs['S8_err'] * ((1/(1+z))**0.55)
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run_loocv(self):
        print("="*80)
        print(f"{'KSAU v23.0: Integrated LOO-CV (Beta={self.beta_geo:.4f})':^80}")
        print("="*80)
        survey_names = list(self.surveys.keys())
        for excluded in survey_names:
            training = {name: self.surveys[name] for name in survey_names if name != excluded}
            res = minimize(self.cost, x0=[36.0], args=(training,), bounds=[(1.0, 100.0)])
            r0_opt = res.x[0]
            
            obs = self.surveys[excluded]
            z = obs['z_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(z, r0_opt)
            s8_err_z = obs['S8_err'] * ((1/(1+z))**0.55)
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            
            print(f"Excl {excluded:<12} | R_opt: {r0_opt:6.2f} | Diff: {sigma_diff:6.2f} sig")

if __name__ == "__main__":
    LOOCVIntegrationOptimized().run_loocv()
