#!/usr/bin/env python3
"""
KSAU v26.0 Section 1 — Scale-Dependent (Two-Regime) Scaling Model (REVISED V2)
=========================================================================
Model: R₀(k, z) = R_base(3) * alpha * k^(-γ(k)) * (1+z)^(-beta)
where R_base(3) = 3 / (2 * kappa)
and γ(k) transitions smoothly between two regimes at k_pivot.

Parameters: alpha, gamma_low, gamma_high
Fixed: beta = beta_ssot, k_pivot, dk from SSoT

This revision addresses:
1. Central SSoT (v6.0/data) integration.
2. Removal of magic numbers (a**0.55, rz_min/max) moved to SSoT.
3. Strict Identifiability check.
"""

import sys
import os
import json
import math
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
TOPOLOGY_ASSIGN = SSOT_DIR / "topology_assignments.json"
WL5_CONFIG      = SSOT_DIR / "wl5_survey_config.json"

class TwoRegimeEngine:
    def __init__(self):
        # Load SSoT constants
        with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
            self.phys = json.load(f)
        with open(COSMO_CONFIG, "r", encoding="utf-8") as f:
            self.cosmo = json.load(f)
        
        # Initialize KSAU physics engine (Central SSoT fixed)
        self.ksau = LOOCVFinalAudit(config_path=str(COSMO_CONFIG))
        
        # Load survey data
        with open(WL5_CONFIG, "r", encoding="utf-8") as f:
            self.surveys = json.load(f)["surveys"]
        
        # SSoT Constants
        self.kappa = self.phys["kappa"]
        self.r_base_3 = 3.0 / (2.0 * self.kappa)
        self.beta_fixed = self.cosmo["beta_ssot"]
        self.chi2_baseline = self.cosmo["chi2_baseline"]
        
        self.gamma_bounds = (self.cosmo["gamma_min"], self.cosmo["gamma_max"])
        self.alpha_bounds = tuple(self.cosmo["alpha_bounds"])
        
        # Scaling Laws from SSoT
        self.growth_index = self.cosmo["scaling_laws"]["growth_index"]
        self.rz_min = self.cosmo["scaling_laws"]["rz_min"]
        self.rz_max = self.cosmo["scaling_laws"]["rz_max"]
        
        self.interp = self._build_s8_interpolator()

    def _build_s8_interpolator(self):
        z_vals = sorted(list(set(s["z_eff"] for s in self.surveys.values())))
        rz_grid = np.logspace(np.log10(self.rz_min), np.log10(self.rz_max), 120)
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

    def compute_rz(self, k, z, params):
        alpha, gamma = params
        r0 = self.r_base_3 * alpha * k**(-gamma)
        return r0 * (1.0 + z)**(-self.beta_fixed)

    def cost_function(self, params, training_surveys):
        alpha, gamma = params
        if alpha <= 0: return 1e10 + abs(alpha)*1e6
        
        chi2 = 0.0
        penalty = 0.0
        for name, sv in training_surveys.items():
            k, z = sv["k_eff"], sv["z_eff"]
            rz = self.compute_rz(k, z, params)
            
            # Quadratic penalty for boundary violations to help optimizer
            if rz < self.rz_min:
                penalty += 1e6 * (self.rz_min - rz)**2
                rz = self.rz_min
            elif rz > self.rz_max:
                penalty += 1e6 * (rz - self.rz_max)**2
                rz = self.rz_max
            
            s8_pred = self.s8_query(rz, z)
            if np.isnan(s8_pred): return 1e12
            
            a = 1.0 / (1.0 + z)
            s8_obs_z = sv["S8_obs"] * (a**self.growth_index)
            s8_err_z = sv["S8_err"] * (a**self.growth_index)
            chi2 += ((s8_pred - s8_obs_z) / s8_err_z)**2
        return chi2 + penalty

    def fit(self, training_surveys, x0=None):
        if x0 is None:
            x0 = [1.0, 0.5] # alpha, gamma
        
        res = minimize(
            self.cost_function,
            x0,
            args=(training_surveys,),
            method="L-BFGS-B",
            bounds=[self.alpha_bounds, self.gamma_bounds],
            options={"ftol": 1e-7}
        )
        return res

    def check_boundary(self, params):
        alpha, gamma = params
        tol = 0.01
        sticking = []
        if abs(alpha - self.alpha_bounds[0]) < tol: sticking.append("alpha_min")
        if abs(alpha - self.alpha_bounds[1]) < tol: sticking.append("alpha_max")
        if abs(gamma - self.gamma_bounds[0]) < tol: sticking.append("gamma_min")
        if abs(gamma - self.gamma_bounds[1]) < tol: sticking.append("gamma_max")
        return sticking

    def profile_likelihood(self, param_idx, p_range, surveys):
        res_best = self.fit(surveys)
        base_params = res_best.x
        chi2_min = res_best.fun
        
        chi2_vals = []
        for v in p_range:
            p = list(base_params)
            p[param_idx] = v
            def opt_rest(x):
                p_copy = list(p)
                p_copy[1-param_idx] = x[0]
                return self.cost_function(p_copy, surveys)
            
            x0_rest = [base_params[1-param_idx]]
            bounds_rest = [[self.alpha_bounds, self.gamma_bounds][1-param_idx]]
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
        alpha_boots = []
        gamma_boots = []
        mae_boots = []
        
        print(f"Running Bootstrap (n={n_iter})...")
        for _ in range(n_iter):
            resamp_names = np.random.choice(names, size=len(names), replace=True)
            resamp_surveys = {n: self.surveys[n] for n in resamp_names}
            res = self.fit(resamp_surveys)
            if res.success:
                alpha_boots.append(float(res.x[0]))
                gamma_boots.append(float(res.x[1]))
                
                # Internal LOO for this resample to get an MAE estimate
                fold_tensions = []
                unique_names = list(set(resamp_names))
                for ho in unique_names:
                    train = {n: self.surveys[n] for n in resamp_names if n != ho}
                    if not train: continue
                    r_ho = self.fit(train)
                    p_ho = r_ho.x
                    sv = self.surveys[ho]
                    rz = self.compute_rz(sv["k_eff"], sv["z_eff"], p_ho)
                    s8p = self.s8_query(rz, sv["z_eff"])
                    a = 1.0 / (1.0 + sv["z_eff"])
                    s8o = sv["S8_obs"] * (a**self.growth_index)
                    s8e = sv["S8_err"] * (a**self.growth_index)
                    fold_tensions.append((s8p - s8o) / s8e)
                if fold_tensions:
                    mae_boots.append(np.mean(np.abs(fold_tensions)))

        corr = np.corrcoef(alpha_boots, gamma_boots)[0, 1] if len(alpha_boots) > 1 else 0.0

        return {
            "alpha_mean": float(np.mean(alpha_boots)),
            "alpha_std": float(np.std(alpha_boots)),
            "gamma_mean": float(np.mean(gamma_boots)),
            "gamma_std": float(np.std(gamma_boots)),
            "mae_mean": float(np.mean(mae_boots)) if mae_boots else None,
            "mae_std": float(np.std(mae_boots)) if mae_boots else None,
            "alpha_gamma_corr": float(corr),
            "samples": {
                "alpha": alpha_boots,
                "gamma": gamma_boots
            }
        }

    def run_loo_cv(self):
        names = list(self.surveys.keys())
        results = {}
        
        print("\nStarting REVISED LOO-CV for Section 1 (Single-Regime)...")
        for held_out in names:
            train = {n: self.surveys[n] for n in names if n != held_out}
            res = self.fit(train)
            params_opt = res.x
            
            sv = self.surveys[held_out]
            k_ho, z_ho = sv["k_eff"], sv["z_eff"]
            rz_ho = self.compute_rz(k_ho, z_ho, params_opt)
            s8_pred = self.s8_query(rz_ho, z_ho)
            
            a_ho = 1.0 / (1.0 + z_ho)
            s8_obs_z = sv["S8_obs"] * (a_ho**self.growth_index)
            s8_err_z = sv["S8_err"] * (a_ho**self.growth_index)
            tension = (s8_pred - s8_obs_z) / s8_err_z
            
            sticking = self.check_boundary(params_opt)
            
            results[held_out] = {
                "params_opt": params_opt.tolist(),
                "alpha": round(params_opt[0], 4),
                "gamma": round(params_opt[1], 4),
                "k_ho": k_ho,
                "tension": round(tension, 4),
                "s8_pred": round(s8_pred, 4),
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
        res = self.fit(self.surveys)
        params_opt = res.x
        
        try:
            hess_inv = res.hess_inv.todense() if hasattr(res.hess_inv, "todense") else res.hess_inv
            uncertainties = np.sqrt(np.diag(hess_inv)).tolist()
        except:
            uncertainties = [None] * len(params_opt)
        
        per_survey = {}
        for name, sv in self.surveys.items():
            k, z = sv["k_eff"], sv["z_eff"]
            rz = self.compute_rz(k, z, params_opt)
            s8_pred = self.s8_query(rz, z)
            a = 1.0 / (1.0 + z)
            s8_obs_z = sv["S8_obs"] * (a**self.growth_index)
            s8_err_z = sv["S8_err"] * (a**self.growth_index)
            tension = (s8_pred - s8_obs_z) / s8_err_z
            
            per_survey[name] = {
                "rz": round(rz, 3),
                "tension": round(tension, 3)
            }
            
        return {
            "params": params_opt.tolist(),
            "uncertainties": uncertainties,
            "alpha": round(params_opt[0], 4),
            "gamma": round(params_opt[1], 4),
            "per_survey": per_survey,
            "chi2": round(res.fun, 4)
        }

def main():
    engine = TwoRegimeEngine()
    global_fit = engine.run_global_fit()
    loo_results = engine.run_loo_cv()
    bootstrap = engine.run_bootstrap(n_iter=50)
    
    chi2_baseline = engine.chi2_baseline 
    n = 5
    k_params = 2
    chi2_val = global_fit["chi2"]
    
    aic_val = 2 * k_params + chi2_val
    bic_val = k_params * np.log(n) + chi2_val
    
    delta_aic = aic_val - chi2_baseline
    delta_bic = bic_val - chi2_baseline
    
    print(f"\nGlobal Fit Result (2 params):")
    print(f"  Alpha: {global_fit['alpha']:.4f} +/- {bootstrap['alpha_std']:.4f}")
    print(f"  Gamma: {global_fit['gamma']:.4f} +/- {bootstrap['gamma_std']:.4f}")
    print(f"  Chi2:  {global_fit['chi2']:.4f}")
    print(f"  AIC: {aic_val:.4f} (delta={delta_aic:+.2f})")
    print(f"  BIC: {bic_val:.4f} (delta={delta_bic:+.2f})")
    print(f"  MAE (LOO-CV): {loo_results['mae_all']:.4f} sigma")
    print(f"  Bootstrap MAE: {bootstrap['mae_mean']:.4f} +/- {bootstrap['mae_std']:.4f}")
    
    print("\nScanning Profile Likelihood for gamma...")
    g_range = np.linspace(engine.gamma_bounds[0], engine.gamma_bounds[1], 15)
    profile_data = engine.profile_likelihood(1, g_range, engine.surveys)
    print(f"  Range: {g_range[0]:.2f} to {g_range[-1]:.2f}")
    print(f"  Identifiable: {profile_data['identifiable']}")
    if profile_data['ci_range']:
        print(f"  1-sigma CI: {profile_data['ci_range'][0]:.4f} to {profile_data['ci_range'][1]:.4f}")
    
    output = {
        "model": "Scale-Dependent (Single-Regime) Scaling Model (Section 1 Revised V3)",
        "global_fit": global_fit,
        "loo_cv": loo_results,
        "bootstrap": bootstrap,
        "profile_likelihood": profile_data,
        "metrics": {
            "n_data": n,
            "n_params": k_params,
            "chi2": chi2_val,
            "aic": aic_val,
            "bic": bic_val,
            "delta_aic_vs_base": delta_aic,
            "delta_bic_vs_base": delta_bic,
            "chi2_baseline": chi2_baseline
        },
        "ssot_keys_used": [
            "v6.0/data/physical_constants.json:kappa",
            "v6.0/data/cosmological_constants.json:gamma_min",
            "v6.0/data/cosmological_constants.json:gamma_max",
            "v6.0/data/cosmological_constants.json:scaling_laws"
        ]
    }
    
    out_path = BASE / "v26.0" / "data" / "section_1_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")

if __name__ == "__main__":
    main()
