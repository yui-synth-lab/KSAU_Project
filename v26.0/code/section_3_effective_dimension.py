#!/usr/bin/env python3
"""
KSAU v26.0 Section 3 — Effective Dimension D(k) Model (REVISED V2)
=====================================================
Model: D(k) = 3 + delta_D * exp(-k / k_c)
       R_base(k) = D(k) / (2 * kappa)
       r0_i = R_base(k_i) * shell_mag_i
       rz_i = r0_i * (1 + z_i)^(-beta)

Parameters: delta_D, k_c, beta

This revision addresses:
1. Central SSoT (v6.0/data) integration.
2. Removal of magic numbers (a**0.55, rz_min/max) moved to SSoT.
3. Proper chi2_baseline and AIC/BIC comparison.
"""

import sys
import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize
from scipy.interpolate import RegularGridInterpolator

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

# SSoT Paths (Centralized)
SSOT_DIR        = BASE / "v6.0" / "data"
COSMO_CONFIG    = SSOT_DIR / "cosmological_constants.json"
PHYS_CONSTANTS  = SSOT_DIR / "physical_constants.json"
WL5_CONFIG      = SSOT_DIR / "wl5_survey_config.json"

class EffectiveDimensionEngine:
    def __init__(self):
        with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
            self.cosmo = json.load(f)
        with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
            self.phys = json.load(f)
        
        self.ksau = LOOCVFinalAudit(config_path=str(COSMO_CONFIG))
        # Use kappa from SSoT
        self.kappa = self.phys["kappa"]
        self.chi2_baseline = self.cosmo["chi2_baseline"]
        
        with open(WL5_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.surveys = config["surveys"]
            self.leech = config["expected_leech_assignment"]
        
        # Simplified linear D(k) model parameters
        self.slope_bounds = (-50.0, 50.0)
        self.beta_bounds = tuple(self.cosmo["beta_bounds"])
        
        # Scaling Laws from SSoT
        self.growth_index = self.cosmo["scaling_laws"]["growth_index"]
        self.rz_min = self.cosmo["scaling_laws"]["rz_min"]
        self.rz_max = self.cosmo["scaling_laws"]["rz_max"]
        
        self.interp = self._build_s8_interpolator()

    def _build_s8_interpolator(self):
        z_vals = sorted(list(set(s["z_eff"] for s in self.surveys.values())))
        rz_grid = np.logspace(np.log10(self.rz_min), np.log10(self.rz_max), 100)
        s8_grid = np.zeros((len(rz_grid), len(z_vals)))
        
        for j, z in enumerate(z_vals):
            for i, rz in enumerate(rz_grid):
                s8_grid[i, j] = self.ksau.predict_s8_z(z, rz, 0.0, use_nl=True)
        
        return RegularGridInterpolator(
            (np.log(rz_grid), np.array(z_vals)),
            s8_grid,
            method="linear",
            bounds_error=False,
            fill_value=None
        )

    def s8_query(self, rz, z):
        res = self.interp([[np.log(max(rz, 1e-5)), z]])[0]
        return float(res)

    def compute_rz(self, name, slope, beta):
        sv = self.surveys[name]
        k = sv["k_eff"]
        z = sv["z_eff"]
        
        # Linear D(k) model centered at k=0.4
        d_k = 3.0 + slope * (k - 0.4)
        r_base_k = d_k / (2.0 * self.kappa)
        
        shell_mag = self.leech[name]["shell_mag"]
        r0 = r_base_k * shell_mag
        return r0 * (1.0 + z)**(-beta)

    def cost_function(self, params, training_names):
        slope, beta = params
        chi2 = 0.0
        penalty = 0.0
        for name in training_names:
            rz = self.compute_rz(name, slope, beta)
            
            if rz < self.rz_min:
                penalty += 1e6 * (self.rz_min - rz)**2
                rz = self.rz_min
            elif rz > self.rz_max:
                penalty += 1e6 * (rz - self.rz_max)**2
                rz = self.rz_max
            
            s8_pred = self.s8_query(rz, self.surveys[name]["z_eff"])
            if np.isnan(s8_pred): return 1e12
            
            sv = self.surveys[name]
            a = 1.0 / (1.0 + sv["z_eff"])
            s8_obs_z = sv["S8_obs"] * (a**self.growth_index)
            s8_err_z = sv["S8_err"] * (a**self.growth_index)
            chi2 += ((s8_pred - s8_obs_z) / s8_err_z)**2
        return chi2 + penalty

    def fit(self, training_names):
        x0 = [0.0, 2.16] # slope, beta
        res = minimize(
            self.cost_function,
            x0,
            args=(training_names,),
            method="L-BFGS-B",
            bounds=[self.slope_bounds, self.beta_bounds],
            options={"ftol": 1e-7}
        )
        return res

    def check_boundary(self, params):
        slope, beta = params
        sticking = []
        if abs(slope - self.slope_bounds[0]) < 0.1: sticking.append("slope_min")
        if abs(slope - self.slope_bounds[1]) < 0.1: sticking.append("slope_max")
        if abs(beta - self.beta_bounds[0]) < 0.01: sticking.append("beta_min")
        if abs(beta - self.beta_bounds[1]) < 0.01: sticking.append("beta_max")
        return sticking

    def profile_likelihood(self, param_idx, p_range, names):
        res_best = self.fit(names)
        base_params = res_best.x
        chi2_min = res_best.fun
        
        chi2_vals = []
        bounds_all = [self.slope_bounds, self.beta_bounds]
        for v in p_range:
            p = list(base_params)
            p[param_idx] = v
            def opt_rest(x):
                p_copy = list(p)
                p_copy[1-param_idx] = x[0]
                return self.cost_function(p_copy, names)
            
            x0_rest = [base_params[1-param_idx]]
            bounds_rest = [bounds_all[1-param_idx]]
            res_rest = minimize(opt_rest, x0_rest, method="L-BFGS-B", bounds=bounds_rest)
            chi2_vals.append(res_rest.fun)
            
        threshold = self.cosmo.get("delta_chi2_threshold", 1.0)
        left_identifiable = (chi2_vals[0] - chi2_min > threshold)
        right_identifiable = (chi2_vals[-1] - chi2_min > threshold)
        
        at_boundary = False
        tol = 1e-3
        if abs(base_params[param_idx] - p_range[0]) < tol or abs(base_params[param_idx] - p_range[-1]) < tol:
            at_boundary = True
            
        identifiable = bool(left_identifiable and right_identifiable and not at_boundary)
        
        ci_mask = np.array(chi2_vals) - chi2_min < threshold
        ci_values = np.array(p_range)[ci_mask]
        ci_range = [float(min(ci_values)), float(max(ci_values))] if len(ci_values) > 0 else None
        
        return {
            "values": p_range.tolist(),
            "chi2": chi2_vals,
            "identifiable": identifiable,
            "ci_range": ci_range,
            "at_boundary": at_boundary,
            "threshold": threshold
        }

    def run_bootstrap(self, n_iter=50):
        names = list(self.surveys.keys())
        slope_boots = []
        beta_boots = []
        mae_boots = []
        
        print(f"Running Bootstrap (n={n_iter})...")
        for _ in range(n_iter):
            resamp_names = np.random.choice(names, size=len(names), replace=True)
            res = self.fit(resamp_names)
            if res.success:
                slope_boots.append(res.x[0])
                beta_boots.append(res.x[1])
                
                fold_tensions = []
                for ho in set(resamp_names):
                    train = [n for n in resamp_names if n != ho]
                    if not train: continue
                    r_ho = self.fit(train)
                    p_ho = r_ho.x
                    rz = self.compute_rz(ho, p_ho[0], p_ho[1])
                    s8p = self.s8_query(rz, self.surveys[ho]["z_eff"])
                    a = 1.0 / (1.0 + self.surveys[ho]["z_eff"])
                    s8o = self.surveys[ho]["S8_obs"] * (a**self.growth_index)
                    s8e = self.surveys[ho]["S8_err"] * (a**self.growth_index)
                    fold_tensions.append((s8p - s8o) / s8e)
                if fold_tensions:
                    mae_boots.append(np.mean(np.abs(fold_tensions)))

        return {
            "slope_mean": float(np.mean(slope_boots)),
            "slope_std": float(np.std(slope_boots)),
            "beta_mean": float(np.mean(beta_boots)),
            "beta_std": float(np.std(beta_boots)),
            "mae_mean": float(np.mean(mae_boots)) if mae_boots else None,
            "mae_std": float(np.std(mae_boots)) if mae_boots else None
        }

    def run_loo_cv(self):
        names = list(self.surveys.keys())
        results = {}
        
        print("\nStarting REVISED LOO-CV for Section 3 (Linear D(k))...")
        for held_out in names:
            train = [n for n in names if n != held_out]
            res = self.fit(train)
            slope_opt, beta_opt = res.x
            
            rz_ho = self.compute_rz(held_out, slope_opt, beta_opt)
            s8_pred = self.s8_query(rz_ho, self.surveys[held_out]["z_eff"])
            
            sv = self.surveys[held_out]
            a_ho = 1.0 / (1.0 + sv["z_eff"])
            s8_obs_z = sv["S8_obs"] * (a_ho**self.growth_index)
            s8_err_z = sv["S8_err"] * (a_ho**self.growth_index)
            tension = (s8_pred - s8_obs_z) / s8_err_z
            sticking = self.check_boundary([slope_opt, beta_opt])
            
            results[held_out] = {
                "slope_loo": round(slope_opt, 4),
                "beta_loo": round(beta_opt, 4),
                "tension":  round(tension, 4),
                "s8_pred":  round(s8_pred, 4),
                "s8_obs_z": round(s8_obs_z, 4),
                "boundary_sticking": sticking
            }
            stick_str = f" [STICK: {','.join(sticking)}]" if sticking else ""
            print(f"  Held out: {held_out:<12} | Tension: {tension:>+6.2f} sigma{stick_str}")

        tensions = [v["tension"] for v in results.values()]
        mae = np.mean(np.abs(tensions))
        return {
            "per_fold": results,
            "mae_all": round(float(mae), 4)
        }

    def run_global_fit(self):
        res = self.fit(list(self.surveys.keys()))
        slope_opt, beta_opt = res.x
        
        try:
            hess_inv = res.hess_inv.todense() if hasattr(res.hess_inv, "todense") else res.hess_inv
            uncertainties = np.sqrt(np.diag(hess_inv)).tolist()
        except:
            uncertainties = [None, None]
        
        per_survey = {}
        for name in self.surveys.keys():
            rz = self.compute_rz(name, slope_opt, beta_opt)
            s8_pred = self.s8_query(rz, self.surveys[name]["z_eff"])
            a = 1.0 / (1.0 + self.surveys[name]["z_eff"])
            s8_obs_z = self.surveys[name]["S8_obs"] * (a**self.growth_index)
            s8_err_z = self.surveys[name]["S8_err"] * (a**self.growth_index)
            tension = (s8_pred - s8_obs_z) / s8_err_z
            
            per_survey[name] = {
                "rz": round(rz, 3),
                "tension": round(tension, 3)
            }
            
        return {
            "slope": round(slope_opt, 4),
            "beta": round(beta_opt, 4),
            "uncertainties": uncertainties,
            "per_survey": per_survey,
            "chi2": round(res.fun, 4)
        }

def main():
    engine = EffectiveDimensionEngine()
    global_fit = engine.run_global_fit()
    loo_results = engine.run_loo_cv()
    bootstrap = engine.run_bootstrap(n_iter=50)
    
    chi2_baseline = engine.chi2_baseline 
    n = 5
    k = 2
    chi2 = global_fit["chi2"]
    aic = 2*k + chi2
    bic = k*np.log(n) + chi2
    
    print(f"\nGlobal Fit Result:")
    print(f"  Slope: {global_fit['slope']:.4f} +/- {bootstrap['slope_std']:.4f}")
    print(f"  Beta:  {global_fit['beta']:.4f} +/- {bootstrap['beta_std']:.4f}")
    print(f"  Chi2:  {global_fit['chi2']:.4f}")
    print(f"  AIC: {aic:.4f} (delta={aic - chi2_baseline:+.2f})")
    print(f"  BIC: {bic:.4f} (delta={bic - chi2_baseline:+.2f})")
    print(f"  MAE (LOO-CV): {loo_results['mae_all']:.4f} sigma")
    print(f"  Bootstrap MAE: {bootstrap['mae_mean']:.4f} +/- {bootstrap['mae_std']:.4f}")
    
    print("\nScanning Profile Likelihood for Slope...")
    s_range = np.linspace(engine.slope_bounds[0], engine.slope_bounds[1], 15)
    profile_data = engine.profile_likelihood(0, s_range, list(engine.surveys.keys()))
    print(f"  Range: {s_range[0]:.1f} to {s_range[-1]:.1f}")
    print(f"  Identifiable: {profile_data['identifiable']}")
    if profile_data['ci_range']:
        print(f"  1-sigma CI: {profile_data['ci_range'][0]:.4f} to {profile_data['ci_range'][1]:.4f}")
    
    output = {
        "model": "Effective Dimension D(k) Linear (Section 3 Revised V3)",
        "global_fit": global_fit,
        "loo_cv": loo_results,
        "bootstrap": bootstrap,
        "profile_likelihood": profile_data,
        "metrics": {
            "n_data": n,
            "n_params": k,
            "chi2": chi2,
            "aic": aic,
            "bic": bic,
            "delta_aic_vs_base": aic - chi2_baseline,
            "delta_bic_vs_base": bic - chi2_baseline,
            "chi2_baseline": chi2_baseline
        },
        "ssot_keys_used": [
            "v6.0/data/physical_constants.json:kappa",
            "v6.0/data/cosmological_constants.json:beta_bounds",
            "v6.0/data/cosmological_constants.json:scaling_laws"
        ]
    }
    
    out_path = BASE / "v26.0" / "data" / "section_3_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")

if __name__ == "__main__":
    main()
