import numpy as np
import json
from scipy.optimize import minimize
from scipy.integrate import quad
import sys
import os
sys.path.append('v23.0/code')
from power_spectrum_bao import PowerSpectrumBAOV23

class LOOCVFinalAudit:
    """
    KSAU v23.0: Final Audit of Non-Linear Knot Dynamics
    Corrects dimensional errors and quantifies contributions of Beta vs Non-Linearity.
    """
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.Om0 = self.config['omega_m0']
        self.Otens0 = self.config['hubble_scenarios']['Scenario 1']['omega_tens0']
        self.surveys = self.config['survey_data']
        self.F_branching = self.config['filament_branching']['B_predicted'] / self.config['filament_branching']['B_eff']
        self.ps_gen = PowerSpectrumBAOV23(config_path)
        self.ns = self.config['n_s']
        
        # SSoT Constants
        self.kappa = self.config['kappa'] # 0.1309 (Action per Pachner Move)
        self.alpha = self.config['alpha_ksau'] # 1/48
        
        # Baselines
        self.beta_phase1 = 2.3916
        self.beta_geo = 13.0 / 6.0 # 2.1667
        
        # Normalization: Fixed to Planck 2018 Sigma8 extrapolated to z=0 via LambdaCDM
        # This represents the "expected" power if there were no KSAU suppression.
        self.A_norm = self.calculate_normalization()

    def window_tophat(self, k, r=8.0):
        x = k * r
        if x < 1e-4: return 1.0
        return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

    def calculate_normalization(self):
        # Normalizes the raw Power Spectrum (P ~ k^ns * T^2) to Sigma8 = 0.811
        def integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            return (k**2 / (2 * np.pi**2)) * (k**self.ns * T**2) * self.window_tophat(k, 8.0)**2
        integral, _ = quad(integrand, 1e-4, 10.0, limit=100)
        return 0.811**2 / integral

    def predict_s8_z(self, z, r0, beta, use_nl=False):
        a = 1.0 / (1.0 + z)
        r_z = r0 * (1 + z)**(-beta)
        
        def integrand(k):
            T = self.ps_gen.transfer_function_eh_bao(k)
            xi_linear = 0.5 + 0.5 * (1.0 - self.window_tophat(k, r_z))
            
            if use_nl:
                # Corrected Non-linear boost: (k/kappa)^2
                # Physically justified as the scale-dependent recovery of growth
                # due to knot entanglement (Chern-Simons linking density).
                # Dimension: [k] = h/Mpc, [kappa] = h/Mpc (identified with physical scale).
                boost_nl = 1.0 + self.alpha * (k / self.kappa)**2
                xi_eff = xi_linear * boost_nl
            else:
                xi_eff = xi_linear
            
            om_eff = (self.Om0 - self.Otens0) + xi_eff * self.Otens0
            # gamma_k scales with om_eff to reflect tension-induced growth variation
            gamma_k = 0.55 * np.log(np.maximum(om_eff, 1e-5)) / np.log(self.Om0)
            d_z = a**gamma_k
            suppression = np.sqrt(om_eff / self.Om0) * self.F_branching
            pk = self.A_norm * k**self.ns * T**2 * (d_z * suppression)**2
            return (k**2 / (2 * np.pi**2)) * pk * self.window_tophat(k, 8.0)**2
            
        sig8_sq, _ = quad(integrand, 1e-4, 10.0, limit=100)
        # S8 = sigma8 * sqrt(Omega_m / 0.3)
        return np.sqrt(sig8_sq) * np.sqrt(self.Om0 / 0.3)

    def cost(self, r0, training_surveys, beta, use_nl):
        chi2 = 0
        for name, obs in training_surveys.items():
            z = obs['z_eff']
            a = 1.0 / (1.0 + z)
            # Target S8 at redshift z
            s8_obs_z = obs['S8_obs'] * (a**0.55)
            s8_err_z = obs['S8_err'] * (a**0.55)
            s8_pred_z = self.predict_s8_z(z, r0[0], beta, use_nl)
            chi2 += ((s8_pred_z - s8_obs_z) / s8_err_z)**2
        return chi2

    def run_audit(self, beta, use_nl, label):
        print(f"\nAudit Mode: {label}")
        survey_names = list(self.surveys.keys())
        diffs = []
        for excluded in survey_names:
            training = {name: self.surveys[name] for name in survey_names if name != excluded}
            res = minimize(self.cost, x0=[20.0], args=(training, beta, use_nl), bounds=[(1.0, 100.0)])
            r0_opt = res.x[0]
            
            obs = self.surveys[excluded]
            z = obs['z_eff']
            a = 1.0 / (1.0 + z)
            s8_obs_z = obs['S8_obs'] * (a**0.55)
            s8_err_z = obs['S8_err'] * (a**0.55)
            s8_pred_z = self.predict_s8_z(z, r0_opt, beta, use_nl)
            sigma_diff = (s8_pred_z - s8_obs_z) / s8_err_z
            diffs.append(sigma_diff)
            print(f"Excl {excluded:<12} | R_opt: {r0_opt:6.2f} | Pred: {s8_pred_z:6.4f} | Obs: {s8_obs_z:6.4f} | Diff: {sigma_diff:6.2f} sig")
        
        mae = np.mean(np.abs(diffs))
        print(f"Mean Absolute Deviation: {mae:.4f} sigma")
        return mae

    def run_full_comparison(self):
        print("="*80)
        print(f"{'KSAU v23.0: Final Audit & Correction (Chern-Simons Dynamics)':^80}")
        print("="*80)
        
        # 1. Phase 1 Baseline (Beta=2.39, No NL)
        mae1 = self.run_audit(self.beta_phase1, False, "Phase 1 Baseline (Beta=2.39, No NL)")
        
        # 2. Beta Correction Only (Beta=13/6, No NL)
        mae2 = self.run_audit(self.beta_geo, False, "Beta Correction Only (Beta=13/6, No NL)")
        
        # 3. Full Model (Beta=13/6 + Corrected NL)
        mae3 = self.run_audit(self.beta_geo, True, "Full Model (Beta=13/6 + Corrected NL)")
        
        print("\n" + "="*80)
        print(f"{'Contribution Analysis':^80}")
        print("-" * 80)
        print(f"Beta Shift (2.39 -> 13/6): {mae1 - mae2:+.4f} sigma improvement")
        print(f"Non-Linear Boost Impact:    {mae2 - mae3:+.4f} sigma improvement")
        print(f"Total Improvement:          {mae1 - mae3:+.4f} sigma")
        print("="*80)

if __name__ == "__main__":
    LOOCVFinalAudit().run_full_comparison()
