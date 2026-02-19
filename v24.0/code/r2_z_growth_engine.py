#!/usr/bin/env python3
"""
KSAU v24.0 R-2: z-Dependent Growth Model (CMB Lensing Consistency)
==================================================================
Refactored for stability and performance.
"""

import sys
import numpy as np
import json
import math
from scipy.integrate import odeint, quad
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
V23_CODE = BASE / "v23.0" / "code"
V24_DATA = BASE / "v24.0" / "data"
V24_CODE = BASE / "v24.0" / "code"
sys.path.append(str(V23_CODE))
sys.path.append(str(V24_CODE))

from loo_cv_engine_v23_final_audit import LOOCVFinalAudit
import ksau_utils_v24 as utils

class GrowthEngineR2:
    def __init__(self, audit):
        self.audit = audit
        self.Om0 = audit.Om0
        self.Ode0 = 1.0 - self.Om0
        self.Otens0 = audit.Otens0
        self.w = -1.0
        self.ns = audit.ns
        self.kappa = audit.kappa
        self.alpha = audit.alpha
        
        # Load SSoT values
        self.leech_shells = utils.load_leech_shells()
        self.z_threshold = utils.get_z_transition_threshold()
        self.z0_shell = utils.get_shell_assignment("z0")
        self.z_high_shell = utils.get_shell_assignment("z_high")
        
        # Precompute Growth Table
        self.om_grid = np.linspace(0.1, 0.6, 51)
        self.a_grid = np.linspace(0.1, 1.0, 46) # z from 0 to 9
        self.growth_table = np.zeros((len(self.om_grid), len(self.a_grid)))
        
        print("Precomputing Growth Table...")
        for i, om in enumerate(self.om_grid):
            self.growth_table[i, :] = self.solve_growth_raw(self.a_grid, om)
            
        self.D1_std = self.get_growth(1.0, self.Om0)
        print(f"D1_std (at a=1, Om={self.Om0}): {self.D1_std:.6f}")

    def hubble_ratio_sq(self, a):
        return self.Om0 * a**-3 + self.Ode0

    def solve_growth_raw(self, a_arr, om_eff_0):
        def ode_func(y, a):
            D, dD_da = y
            E2 = self.hubble_ratio_sq(a)
            om_eff_a = (om_eff_0 * a**-3) / E2
            ode_a = self.Ode0 / E2
            # Correct LCDM Growth ODE: P = 1.5/a * (1 + ode_a) for w = -1
            d2D_da2 = - (1.5 / a) * (1.0 + ode_a) * dD_da + (1.5 / a**2) * om_eff_a * D
            return [dD_da, d2D_da2]

        a_init = 1e-4
        n = 0.5 * (-0.5 + math.sqrt(0.25 + 6.0 * om_eff_0 / self.Om0))
        y0 = [a_init**n, n * a_init**(n-1)]
        full_a = np.unique(np.concatenate([[a_init], a_arr]))
        sol = odeint(ode_func, y0, full_a, rtol=1e-8, atol=1e-8)
        return np.array([sol[np.where(full_a == a)[0][0], 0] for a in a_arr])

    def get_growth(self, a, om_eff_0):
        # 2D Linear Interpolation
        from scipy.interpolate import RegularGridInterpolator
        interp = RegularGridInterpolator((self.om_grid, self.a_grid), self.growth_table, bounds_error=False, fill_value=None)
        return float(interp([om_eff_0, a])[0])

    def calculate_s8_z(self, z, r0, beta, use_nl=True, use_rigorous_growth=True):
        a = 1.0 / (1.0 + z)
        
        # Leech Shell Quantization Logic (R3 compliance)
        # R_base = 3 / (2 * kappa) = 11.459 Mpc/h
        r_base = 3.0 / (2.0 * self.kappa)
        
        # Phenomenological Adjustment: 
        # To align with high-redshift CMB lensing data (z ≈ 1.7, 2.0), 
        # a transition to Shell 1 (inner, more compact) is assumed for z > z_threshold.
        # This is currently a fitting choice, not a first-principles derivation.
        if z > self.z_threshold:
            # High redshift: Manifold locked in Shell 1 (mag ≈ 1.414 from SSoT)
            r_z = r_base * self.leech_shells[self.z_high_shell]
        else:
            # Low redshift: Transition to Shell 2 (v23.0 legacy power law approx)
            r_z = r0 * (1 + z)**(-beta)
        
        def window_tophat(k, r=8.0):
            x = k * r
            if x < 1e-4: return 1.0
            return 3 * (np.sin(x) - x * np.cos(x)) / (x**3)

        def integrand(k):
            T = self.audit.ps_gen.transfer_function_eh_bao(k)
            xi_linear = 0.5 + 0.5 * (1.0 - window_tophat(k, r_z))
            if use_nl:
                boost_nl = 1.0 + self.alpha * (k / self.kappa)**2
                xi_eff = xi_linear * boost_nl
            else:
                xi_eff = xi_linear
            om_eff_0 = (self.Om0 - self.Otens0) + xi_eff * self.Otens0
            
            if use_rigorous_growth:
                D_a = self.get_growth(a, om_eff_0)
                # d_z_eff scales Today's fluctuation to Redshift z
                d_z_eff = D_a / self.D1_std
            else:
                gamma_k = 0.55 * np.log(np.maximum(om_eff_0, 1e-5)) / np.log(self.Om0)
                d_z_eff = a**gamma_k
                
            suppression = np.sqrt(om_eff_0 / self.Om0) * self.audit.F_branching
            pk = self.audit.A_norm * k**self.ns * T**2 * (d_z_eff * suppression)**2
            return (k**2 / (2 * np.pi**2)) * pk * window_tophat(k, 8.0)**2

        sig8_sq, _ = quad(integrand, 1e-4, 10.0, limit=100)
        
        # S8 definition consistently applied (Global Om0)
        return np.sqrt(sig8_sq) * np.sqrt(self.Om0 / 0.3)

def main():
    print("="*80)
    print(f"{'KSAU v24.0 R-2: Rigorous Structure Growth Audit':^80}")
    print("="*80)
    
    # Load SSoT Configs
    audit = LOOCVFinalAudit(config_path=str(BASE / "v23.0" / "data" / "cosmological_constants.json"))
    engine = GrowthEngineR2(audit)
    
    with open(V24_DATA / "cosmological_benchmarks.json", "r") as f:
        bench_data = json.load(f)
    
    r0 = audit.config['R_cell']
    beta = audit.beta_geo
    
    # Define Evaluation Redshifts
    redshifts = sorted(list(set([0.0, 1.0, 1.7, 2.0, 3.0])))
    
    # Calculate Rigorous Growth for Planck LCDM Baseline (for Benchmark Extrapolation)
    # D(z)/D(0) from standard growth ODE
    growth_lcdm = {}
    for z in redshifts:
        a = 1.0 / (1.0 + z)
        D_a = engine.get_growth(a, engine.Om0)
        growth_lcdm[z] = D_a / engine.D1_std
    
    print(f"\n{'z':>5} | {'S8_pred':>12} | {'S8_bench':>12} | {'Err (1s)':>10} | {'Tension':>10}")
    print("-" * 100)
    
    results = []
    for z in redshifts:
        # 1. Model Prediction
        s8_pred = engine.calculate_s8_z(z, r0, beta, use_nl=True, use_rigorous_growth=True)
        
        # 2. Benchmark Retrieval and Rigorous Extrapolation
        s8_bench_z0 = np.nan
        s8_err_z0 = np.nan
        s8_bench_z = np.nan
        s8_err_z = np.nan
        
        # Find relevant benchmark
        for name, info in bench_data['benchmarks'].items():
            if abs(info['z_eff'] - z) < 0.01:
                s8_bench_z0 = info['S8_z0']
                s8_err_z0 = info['S8_err']
                # Extrapolate observed S8(z=0) to S8(z) using SAME rigorous ODE
                # This ensures consistency in the growth model.
                s8_bench_z = s8_bench_z0 * growth_lcdm[z]
                s8_err_z = s8_err_z0 * growth_lcdm[z]
                break
        
        tension = (s8_pred - s8_bench_z) / s8_err_z if not np.isnan(s8_bench_z) else np.nan
        
        print(f"{z:5.1f} | {s8_pred:12.6f} | {s8_bench_z:12.6f} | {s8_err_z:10.4f} | {tension:10.2f}s")
        results.append({'z': z, 's8_pred': s8_pred, 's8_bench_z': s8_bench_z, 'tension_sigma': tension})
    
    V24_DATA.mkdir(parents=True, exist_ok=True)
    with open(V24_DATA / "r2_z_growth_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {V24_DATA / 'r2_z_growth_results.json'}")

if __name__ == "__main__":
    main()
