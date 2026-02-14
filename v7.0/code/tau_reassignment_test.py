
import numpy as np
from sklearn.linear_model import LinearRegression
import json
from pathlib import Path

def calculate_stats(volumes, log_masses):
    volumes = np.array(volumes).reshape(-1, 1)
    log_masses = np.array(log_masses)
    
    model = LinearRegression()
    model.fit(volumes, log_masses)
    
    r2 = model.score(volumes, log_masses)
    preds = model.predict(volumes)
    mae = np.mean(np.abs(np.exp(preds) - np.exp(log_masses)) / np.exp(log_masses)) * 100
    
    return r2, mae, model.coef_[0], model.intercept_

# Data from SSoT
# Electron: 0.511 MeV, Muon: 105.658 MeV, Tau: 1776.86 MeV
m_e = 0.51099895
m_mu = 105.6583755
m_tau = 1776.86

log_masses = [np.log(m_e), np.log(m_mu), np.log(m_tau)]

# Scenario 1: v6.0 Baseline (Tau = 6_1)
v_e = 0.0
v_mu = 2.0298832128
v_tau_v6 = 3.1639632288
volumes_v6 = [v_e, v_mu, v_tau_v6]

r2_v6, mae_v6, kappa_v6, c_v6 = calculate_stats(volumes_v6, log_masses)

# Scenario 2: v7.1 Quantization Hypothesis (Tau = 7_3)
v_tau_v7 = 4.5921256970
volumes_v7 = [v_e, v_mu, v_tau_v7]

r2_v7, mae_v7, kappa_v7, c_v7 = calculate_stats(volumes_v7, log_masses)

print(f"--- Lepton Sector Comparison ---")
print(f"Scenario 1: v6.0 (Tau = 6_1, V=3.16)")
print(f"  R^2: {r2_v6:.6f}")
print(f"  MAE: {mae_v6:.2f}%")
print(f"  Kappa (Effective): {kappa_v6:.4f}")
print(f"  Intercept: {c_v6:.4f}")
print()
print(f"Scenario 2: v7.1 (Tau = 7_3, V=4.59)")
print(f"  R^2: {r2_v7:.6f}")
print(f"  MAE: {mae_v7:.2f}%")
print(f"  Kappa (Effective): {kappa_v7:.4f}")
print(f"  Intercept: {c_v7:.4f}")

# Analysis of Kappa stability
# KSAU standard kappa = pi/24 = 0.1309
# Note: The effective kappa here includes the sector-specific multiplier N (Lepton N=20)
# So effective_kappa = N * kappa_ksau = 20 * 0.1309 = 2.618
print()
print(f"Comparison with KSAU Master Formula (N*kappa = 2.618):")
print(f"  v6.0 Eff Kappa Error: {abs(kappa_v6 - 2.618)/2.618*100:.2f}%")
print(f"  v7.1 Eff Kappa Error: {abs(kappa_v7 - 2.618)/2.618*100:.2f}%")
