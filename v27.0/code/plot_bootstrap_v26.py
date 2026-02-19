#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
RESULT_PATH = BASE / "v26.0" / "data" / "section_1_results.json"
OUT_DIR = BASE / "v27.0" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def plot_bootstrap():
    with open(RESULT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    samples = data["bootstrap"]["samples"]
    alpha = np.array(samples["alpha"])
    gamma = np.array(samples["gamma"])
    
    # Filter outliers or extreme values for plotting if necessary
    # (Checking data showed some alpha=100.0 values at boundary)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Scatter plot
    ax.scatter(alpha, gamma, alpha=0.5, edgecolors='none', label='Bootstrap Samples')
    
    # Global fit point
    gf_alpha = data["global_fit"]["alpha"]
    gf_gamma = data["global_fit"]["gamma"]
    ax.scatter(gf_alpha, gf_gamma, color='red', marker='X', s=100, label='Global Fit')
    
    ax.set_xlabel(r'$\alpha$ (Scaling Factor)')
    ax.set_ylabel(r'$\gamma$ (Scale Index)')
    ax.set_title('v26.0 Section 1: Bootstrap Joint Distribution')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    # Text for correlation
    corr = data["bootstrap"]["alpha_gamma_corr"]
    ax.text(0.05, 0.95, f'Corr: {corr:.3f}', transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    out_file = OUT_DIR / "v26_bootstrap_scatter.png"
    plt.savefig(out_file, dpi=150)
    print(f"Saved: {out_file}")
    
    # Histogram subplots
    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.hist(alpha, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.axvline(gf_alpha, color='red', linestyle='--', label='Global Fit')
    ax1.set_xlabel(r'$\alpha$')
    ax1.set_ylabel('Frequency')
    ax1.set_title(r'Distribution of $\alpha$')
    ax1.legend()
    
    ax2.hist(gamma, bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
    ax2.axvline(gf_gamma, color='red', linestyle='--', label='Global Fit')
    ax2.set_xlabel(r'$\gamma$')
    ax2.set_ylabel('Frequency')
    ax2.set_title(r'Distribution of $\gamma$')
    ax2.legend()
    
    plt.tight_layout()
    out_file2 = OUT_DIR / "v26_bootstrap_hist.png"
    plt.savefig(out_file2, dpi=150)
    print(f"Saved: {out_file2}")

if __name__ == "__main__":
    plot_bootstrap()
