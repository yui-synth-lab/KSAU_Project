"""
KSAU v4.1 Leave-One-Out Cross-Validation (LOO-CV)

Model structure:
  Quarks:  ln(m) = (10/7)G * V - (7+G)           [0 free params]
  Leptons: ln(m) = (2/9)G * N^2 - (1/6)*twist + C_l  [1 free param: C_l]

Since the quark formula has 0 free parameters, LOO = in-sample for quarks.
For leptons, leaving one out requires re-calibrating C_l from the remaining two.
delta = -1/6 is treated as a theoretical/topological constant (not fitted).
"""
import numpy as np

G = 0.915965594177219
GAMMA_Q = (10.0 / 7.0) * G
GAMMA_L = (2.0 / 9.0) * G
B_PRIME = -(7.0 + G)
DELTA = -1.0 / 6.0

QUARKS = [
    {'p': 'u',   'm': 2.16,     'V': 6.598952},
    {'p': 'd',   'm': 4.67,     'V': 7.327725},
    {'p': 's',   'm': 93.4,     'V': 9.531880},
    {'p': 'c',   'm': 1270.0,   'V': 11.517101},
    {'p': 'b',   'm': 4180.0,   'V': 12.276278},
    {'p': 't',   'm': 172760.0, 'V': 15.270898},
]

LEPTONS = [
    {'p': 'e',   'm': 0.510998, 'N': 3, 'twist': 0},
    {'p': 'mu',  'm': 105.658,  'N': 6, 'twist': 1},
    {'p': 'tau', 'm': 1776.86,  'N': 7, 'twist': 0},
]

print("=" * 70)
print("  KSAU v4.1 LOO-CV ANALYSIS")
print("=" * 70)

# =====================================================================
# QUARKS: 0 free params -> LOO = in-sample
# =====================================================================
print("\n  QUARK CHANNEL (0 free params -> LOO = in-sample)")
print(f"  {'P':<4} {'m_obs':>10} {'m_pred':>10} {'Error':>8} {'LOO_err':>8}")
print(f"  {'-'*44}")

q_errors = []
for q in QUARKS:
    ln_pred = GAMMA_Q * q['V'] + B_PRIME
    m_pred = np.exp(ln_pred)
    err = (m_pred - q['m']) / q['m'] * 100
    q_errors.append(abs(err))
    print(f"  {q['p']:<4} {q['m']:>10.2f} {m_pred:>10.2f} {err:>+7.2f}% {err:>+7.2f}%")

q_mae = np.mean(q_errors)
print(f"\n  Quark LOO-CV MAE: {q_mae:.2f}% (= in-sample MAE)")

# =====================================================================
# LEPTONS: 1 free param (C_l) -> LOO re-calibrates C_l
# =====================================================================
print("\n  LEPTON CHANNEL (1 free param: C_l)")
print(f"  delta = -1/6 treated as theoretical constant")

# For each lepton left out:
# 1. Fit C_l from the remaining 2 leptons (OLS)
# 2. Predict the left-out lepton

# C_l for each lepton = ln(m) - (2/9)G * N^2 - delta * twist
def cl_from_lepton(lep):
    return np.log(lep['m']) - GAMMA_L * lep['N']**2 - DELTA * lep['twist']

print(f"\n  {'Left out':<8} {'C_l(fit)':>10} {'m_pred':>10} {'m_obs':>10} {'Error':>8}")
print(f"  {'-'*50}")

l_errors_loo = []
l_errors_insample = []

for i, left_out in enumerate(LEPTONS):
    # Remaining leptons
    remaining = [LEPTONS[j] for j in range(3) if j != i]

    # Fit C_l from remaining (OLS = average of individual C_l values)
    cl_values = [cl_from_lepton(lep) for lep in remaining]
    cl_fit = np.mean(cl_values)

    # Predict left-out
    ln_pred = GAMMA_L * left_out['N']**2 + DELTA * left_out['twist'] + cl_fit
    m_pred = np.exp(ln_pred)
    err = (m_pred - left_out['m']) / left_out['m'] * 100

    l_errors_loo.append(abs(err))

    # Also compute in-sample for comparison
    cl_insample = cl_from_lepton(LEPTONS[0])  # calibrated from electron
    ln_insample = GAMMA_L * left_out['N']**2 + DELTA * left_out['twist'] + cl_insample
    m_insample = np.exp(ln_insample)
    err_insample = (m_insample - left_out['m']) / left_out['m'] * 100
    l_errors_insample.append(abs(err_insample))

    print(f"  {left_out['p']:<8} {cl_fit:>10.6f} {m_pred:>10.4f} {left_out['m']:>10.4f} {err:>+7.2f}%")
    print(f"  {'':8} (C_l from: {', '.join(r['p'] for r in remaining)} = {', '.join(f'{c:.4f}' for c in cl_values)})")

l_mae_loo = np.mean(l_errors_loo)
l_mae_insample = np.mean(l_errors_insample)
print(f"\n  Lepton LOO-CV MAE: {l_mae_loo:.2f}%")
print(f"  Lepton in-sample MAE: {l_mae_insample:.2f}%")
print(f"  Ratio (LOO/in-sample): {l_mae_loo/l_mae_insample:.2f}")

# =====================================================================
# GLOBAL LOO-CV
# =====================================================================
all_loo = q_errors + l_errors_loo
all_insample = q_errors + l_errors_insample
global_loo = np.mean(all_loo)
global_insample = np.mean(all_insample)

print(f"\n{'='*70}")
print(f"  GLOBAL LOO-CV SUMMARY")
print(f"{'='*70}")
print(f"  {'Metric':<30} {'In-sample':>10} {'LOO-CV':>10} {'Ratio':>8}")
print(f"  {'-'*60}")
print(f"  {'Quark MAE':<30} {q_mae:>9.2f}% {q_mae:>9.2f}% {1.00:>7.2f}")
print(f"  {'Lepton MAE':<30} {l_mae_insample:>9.2f}% {l_mae_loo:>9.2f}% {l_mae_loo/l_mae_insample:>7.2f}")
print(f"  {'Global MAE':<30} {global_insample:>9.2f}% {global_loo:>9.2f}% {global_loo/global_insample:>7.2f}")

print(f"\n  Roadmap target: LOO-CV MAE < 10%")
print(f"  v4.0 LOO-CV MAE: 14.9%")
print(f"  v4.1 LOO-CV MAE: {global_loo:.2f}%")
print(f"  Status: {'PASS' if global_loo < 10 else 'FAIL'}")

# =====================================================================
# ROBUSTNESS: LOO-CV / in-sample ratio
# =====================================================================
print(f"\n  Overfitting check:")
print(f"    LOO/in-sample ratio = {global_loo/global_insample:.3f}")
print(f"    (Roadmap target: < 1.5)")
print(f"    Status: {'PASS' if global_loo/global_insample < 1.5 else 'FAIL'}")

# =====================================================================
# COMPARISON WITH v4.0
# =====================================================================
print(f"\n{'='*70}")
print(f"  v4.0 vs v4.1 LOO-CV COMPARISON")
print(f"{'='*70}")

# v4.0 LOO-CV: quark channel had 0 params (same), lepton channel had C_l from electron
# v4.0 lepton formula: ln(m) = (2/9)G*N^2 + C_l (no twist correction)
# The LOO-CV for v4.0 was dominated by the muon error (+17.8%)

CL_v40 = np.log(0.510998) - GAMMA_L * 9  # same as v4.1

# v4.0 in-sample lepton errors
v40_lepton_errors = []
for lep in LEPTONS:
    ln_p = GAMMA_L * lep['N']**2 + CL_v40
    m_p = np.exp(ln_p)
    err = abs((m_p - lep['m']) / lep['m'] * 100)
    v40_lepton_errors.append(err)

# v4.0 LOO-CV lepton errors (re-calibrate C_l without twist correction)
v40_loo_errors = []
for i, left_out in enumerate(LEPTONS):
    remaining = [LEPTONS[j] for j in range(3) if j != i]
    cl_vals = [np.log(r['m']) - GAMMA_L * r['N']**2 for r in remaining]
    cl_fit = np.mean(cl_vals)
    ln_pred = GAMMA_L * left_out['N']**2 + cl_fit
    m_pred = np.exp(ln_pred)
    err = abs((m_pred - left_out['m']) / left_out['m'] * 100)
    v40_loo_errors.append(err)

v40_global_insample = np.mean(q_errors + v40_lepton_errors)
v40_global_loo = np.mean(q_errors + v40_loo_errors)

print(f"\n  {'Metric':<30} {'v4.0':>10} {'v4.1':>10} {'Improvement':>12}")
print(f"  {'-'*65}")
print(f"  {'In-sample MAE':<30} {v40_global_insample:>9.2f}% {global_insample:>9.2f}% {(1-global_insample/v40_global_insample)*100:>10.0f}%")
print(f"  {'LOO-CV MAE':<30} {v40_global_loo:>9.2f}% {global_loo:>9.2f}% {(1-global_loo/v40_global_loo)*100:>10.0f}%")
print(f"  {'LOO/in-sample ratio':<30} {v40_global_loo/v40_global_insample:>9.3f} {global_loo/global_insample:>9.3f}")

print(f"\n{'='*70}")
