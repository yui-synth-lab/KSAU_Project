#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
RESULT_PATH = BASE / "v27.0" / "data" / "scale_dependent_fit_results.json"
BENCHMARK_PATH = BASE / "v27.0" / "data" / "cmb_lensing_benchmarks.json"
OUT_DIR = BASE / "v27.0" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_growth_curve():
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        fit = json.load(f)
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        bench = json.load(f)["benchmarks"]
    
    # Model parameters
    p = fit["params"]
    # alpha, g_low, g_high, k_pivot = p
    
    # Let's plot S8(z) for a few characteristic k values
    k_vals = [0.07, 0.15, 0.7] # Planck/ACT, DES, KiDS
    z_range = np.linspace(0, 2.5, 50)
    
    # To get smooth curves, we'd need to run the engine, but we can approximate
    # S8(z) ~ S8_pred_eff_z0 * (1/(1+z))**0.55
    # or use the per_survey results from the fit.
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    colors = ['blue', 'green', 'red']
    for i, k in enumerate(k_vals):
        # Find the survey matching this k to get the predicted S8(z=0) effective
        # (For plotting purposes, we'll use the fit's effective S8_z0)
        s8_z0_eff = 0.8 # default
        label = f"KSAU Model (k={k})"
        if k == 0.07: s8_z0_eff = fit["per_survey"]["Planck_PR4"]["s8_pred_eff_z0"]
        if k == 0.15: s8_z0_eff = fit["per_survey"]["DES Y3"]["s8_pred_eff_z0"]
        if k == 0.7:  s8_z0_eff = fit["per_survey"]["KiDS-Legacy"]["s8_pred_eff_z0"]
        
        s8_z = s8_z0_eff * (1.0 / (1.0 + z_range))**0.55
        ax.plot(z_range, s8_z, label=label, color=colors[i], lw=2)
    
    # Plot benchmarks
    # Planck PR4 Lensing
    pr4 = bench["Planck_PR4_Lensing"]
    ax.errorbar(pr4["z_eff"], pr4["S8_z0"] * (1.0/(1.0+pr4["z_eff"]))**0.55, 
                yerr=pr4["S8_err"] * (1.0/(1.0+pr4["z_eff"]))**0.55, 
                fmt='o', color='blue', label='Planck PR4 (z=2)', capsize=5)
    
    # ACT DR6
    act = bench["ACT_DR6_Lensing"]
    ax.errorbar(act["z_eff"], act["S8_z0"] * (1.0/(1.0+act["z_eff"]))**0.55, 
                yerr=act["S8_err"] * (1.0/(1.0+act["z_eff"]))**0.55, 
                fmt='s', color='cyan', label='ACT DR6 (z=1.7)', capsize=5)
    
    # DES Y3
    des = bench["DES_Y3"]
    ax.errorbar(des["z_eff"], des["S8_z0"] * (1.0/(1.0+des["z_eff"]))**0.55, 
                yerr=des["S8_err"] * (1.0/(1.0+des["z_eff"]))**0.55, 
                fmt='^', color='green', label='DES Y3 (z=0.33)', capsize=5)
    
    # KiDS Legacy
    kids = bench["KiDS_Legacy"]
    ax.errorbar(kids["z_eff"], kids["S8_z0"] * (1.0/(1.0+kids["z_eff"]))**0.55, 
                yerr=kids["S8_err"] * (1.0/(1.0+kids["z_eff"]))**0.55, 
                fmt='v', color='red', label='KiDS-Legacy (z=0.26)', capsize=5)
    
    # Planck 2018 Primary (Reference)
    p18 = bench["Planck_2018_Primary"]
    ax.axhline(p18["S8_z0"], color='black', linestyle=':', alpha=0.5, label='Planck 2018 Primary (z=0 ref)')

    ax.set_xlabel('Redshift $z$')
    ax.set_ylabel('$S_8(z)$')
    ax.set_title('KSAU Growth History: Scale-Dependent Resolution')
    ax.legend(loc='upper right', fontsize='small', ncol=2)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    out_file = OUT_DIR / "s8_growth_history_z2.png"
    plt.savefig(out_file, dpi=150)
    print(f"Saved: {out_file}")

if __name__ == "__main__":
    plot_growth_curve()
