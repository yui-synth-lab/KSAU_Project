
import numpy as np
import json
from scipy.optimize import minimize

class ParamSearchV23:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.Om0 = self.config['omega_m0']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']

    def window_function(self, k, r):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def predict_s8_z(self, k, z, r0, beta):
        r_z = r0 * (1 + z)**(-beta)
        xi = 0.5 + 0.5 * (1.0 - self.window_function(k, r_z))
        om_eff = (self.Om0 - self.Otens0) + xi * self.Otens0
        gamma_k = 0.55 * np.log(om_eff) / np.log(self.Om0)
        a = 1.0 / (1.0 + z)
        suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
        # Normalized to baseline sigma8(0) = 0.811
        # and converted to S8(z) assuming LCDM baseline
        s8_ref_z = 0.811 * (a**0.55) * np.sqrt(self.Om0 / 0.3)
        # KSAU growth relative to LCDM growth
        ksau_growth_relative = (a**gamma_k) / (a**0.55)
        return s8_ref_z * suppression * ksau_growth_relative

    def get_observed_s8_z(self, s8_obs_reported, z):
        a = 1.0 / (1.0 + z)
        return s8_obs_reported * (a**0.55)

    def cost(self, params):
        r0, beta = params
        chi2 = 0
        for name, obs in self.surveys.items():
            z = obs['z_eff']
            k = obs['k_eff']
            s8_obs_z = self.get_observed_s8_z(obs['S8_obs'], z)
            s8_pred_z = self.predict_s8_z(k, z, r0, beta)
            s8_err_z = obs['S8_err'] * ( (1/(1+z))**0.55 )
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run(self):
        res = minimize(self.cost, x0=[18.0, 1.979], bounds=[(1.0, 100.0), (0.1, 10.0)])
        print(f"Best fit: R_cell = {res.x[0]:.4f}, beta = {res.x[1]:.4f}")
        print(f"Chi2 = {res.fun:.4f}")
        
        r0, beta = res.x
        for name, obs in self.surveys.items():
            z = obs['z_eff']
            k = obs['k_eff']
            s8_obs_z = self.get_observed_s8_z(obs['S8_obs'], z)
            s8_pred_z = self.predict_s8_z(k, z, r0, beta)
            print(f"{name}: Obs={s8_obs_z:.4f}, Pred={s8_pred_z:.4f}, Diff={(s8_pred_z-s8_obs_z)/(obs['S8_err']*((1/(1+z))**0.55)):.2f} sigma")

if __name__ == "__main__":
    ParamSearchV23().run()
