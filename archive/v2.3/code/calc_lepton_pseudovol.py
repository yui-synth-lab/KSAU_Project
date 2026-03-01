import numpy as np
from scipy import stats

# 1. Verification Data (Hyperbolic Knots)
# Source: Literature values obtained via search
knot_data = {
    '4_1': {'E': 78.0,  'Vol': 2.02988},
    '5_2': {'E': 83.5,  'Vol': 2.82812},
    '6_1': {'E': 87.2,  'Vol': 3.16396},
    '6_2': {'E': 88.1,  'Vol': 4.40083},
    '6_3': {'E': 88.7,  'Vol': 5.69302}
}

E = [v['E'] for v in knot_data.values()]
Vol = [v['Vol'] for v in knot_data.values()]

# 2. Regression Analysis (E-Vol Correlation)
slope, intercept, r_value, p_value, std_err = stats.linregress(E, Vol)

print("=== Lepton Pseudo-Volume Derivation ===")
print(f"Regression: Vol = {slope:.4f} * E + {intercept:.4f}")
print(f"R^2 Score : {r_value**2:.4f}")

# 3. Calculate Pseudo-Vol for Leptons
# E values from Paper_A_Lepton_Masses.md
lepton_E = {
    'e': 74.41,  # 3_1 knot
    'mu': 88.70, # 6_3 knot
    'tau': 96.30 # 7_1 knot
}

lepton_vol = {}
for name, e_val in lepton_E.items():
    if name == 'mu':
        vol = 5.693 # Use actual hyperbolic volume for 6_3
    else:
        vol = slope * e_val + intercept # Predict for non-hyperbolic
    lepton_vol[name] = vol
    print(f"  {name:3s}: E = {e_val:.2f} -> Calculated Vol = {vol:.3f}")

print("")
print("Official v2.4 Lepton Volume Set:")
print(lepton_vol)