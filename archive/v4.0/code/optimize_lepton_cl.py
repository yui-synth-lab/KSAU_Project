
import numpy as np

# Constants
G = 0.915965594
GAMMA_L = (2/9) * G

# Lepton Data (N^2, Mass)
data = [
    (9, 0.5109989),   # Electron (N=3)
    (36, 105.65837),  # Muon (N=6)
    (49, 1776.86)     # Tau (N=7)
]

def calculate_mae(c_l):
    errors = []
    for n2, obs in data:
        ln_pred = GAMMA_L * n2 + c_l
        pred = np.exp(ln_pred)
        err = abs(pred - obs) / obs * 100
        errors.append(err)
    return np.mean(errors), errors

# Optimize C_l
# Search range around electron-fit value (-2.50)
c_range = np.linspace(-3.0, -2.0, 10000)
best_c = None
best_mae = float('inf')
best_errors = []

for c in c_range:
    mae, errs = calculate_mae(c)
    if mae < best_mae:
        best_mae = mae
        best_c = c
        best_errors = errs

print(f"Optimal C_l: {best_c:.6f}")
print(f"Lepton MAE: {best_mae:.4f}%")
print("Individual Errors:")
labels = ['Electron', 'Muon', 'Tau']
for i, err in enumerate(best_errors):
    n2, obs = data[i]
    pred = np.exp(GAMMA_L * n2 + best_c)
    print(f"{labels[i]:<10}: Obs={obs:.2f}, Pred={pred:.2f}, Err={err:.2f}%")

# Quark Errors (Geometric Model)
# From previous run: u: -5.0%, d: +14.0%, s: +2.0%, c: +0.8%, b: -17.3%, t: +13.1%
# Let's recalculate precisely
QUARKS = {
    'u': {'m': 2.16, 'V': 6.598952},
    'd': {'m': 4.67, 'V': 7.327725},
    's': {'m': 93.4, 'V': 9.5319},
    'c': {'m': 1270, 'V': 11.517101},
    'b': {'m': 4180, 'V': 12.276278},
    't': {'m': 172760, 'V': 15.359984}
}
GAMMA_Q = (10/7) * G
B_PRIME = -(7 + G)

quark_errors = []
print("\nQuark Errors:")
for q, d in QUARKS.items():
    pred = np.exp(GAMMA_Q * d['V'] + B_PRIME)
    err = (pred - d['m']) / d['m'] * 100
    quark_errors.append(abs(err))
    print(f"{q.upper():<2}: Obs={d['m']:.2f}, Pred={pred:.2f}, Err={err:+.2f}%")

q_mae = np.mean(quark_errors)
print(f"Quark MAE: {q_mae:.4f}%")

# Global MAE
global_mae = (np.sum(quark_errors) + np.sum(best_errors)) / 9
print(f"\nGlobal MAE (Optimized): {global_mae:.4f}%")
