
import numpy as np
import json
from scipy.optimize import minimize
from scipy.integrate import quad
import os
import sys
sys.path.append('v23.0/code')
from power_spectrum_bao import PowerSpectrumBAOV23

class ParamSearchV23Integration:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.Om0 = self.config['omega_m0']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        self.ps_gen = PowerSpectrumBAOV23(config_path)
        self.ns = self.config['n_s']
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

    def predict_s8_z(self, z, r0, beta):
        a = 1.0 / (1.0 + z)
        r_z = r0 * (1 + z)**(-beta)
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

    def cost(self, params):
        r0, beta = params
        chi2 = 0
        for name, obs in self.surveys.items():
            z = obs['z_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(z, r0, beta)
            s8_err_z = obs['S8_err'] * ((1/(1+z))**0.55)
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run(self):
        res = minimize(self.cost, x0=[20.0, 2.166], bounds=[(1.0, 100.0), (0.1, 10.0)])
        print(f"Best fit (Integration): R_cell = {res.x[0]:.4f}, beta = {res.x[1]:.4f}")
        print(f"Chi2 = {res.fun:.4f}")
        
        r0, beta = res.x
        for name, obs in self.surveys.items():
            z = obs['z_eff']
            s8_obs_z = obs['S8_obs'] * ((1/(1+z))**0.55)
            s8_pred_z = self.predict_s8_z(z, r0, beta)
            print(f"{name}: Obs={s8_obs_z:.4f}, Pred={s8_pred_z:.4f}, Diff={(s8_pred_z-s8_obs_z)/(obs['S8_err']*((1/(1+z))**0.55)):.2f} sigma")

if __name__ == "__main__":
    ParamSearchV23Integration().run()
