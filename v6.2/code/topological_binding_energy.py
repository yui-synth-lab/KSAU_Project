"""
KSAU v6.2: Topological Binding Energy (Volume Defect Model)
Objective: Explain Top -> W + Bottom decay with v6.0 constrained assignments.

Theory:
  The Top quark is not a simple sum of W + Bottom volumes.
  Instead, we model it as a bound state with "Volume Defect" (delta_V):
  V_top = V_W + V_bottom - delta_V_binding

  This delta_V represents the topological entropy reduction when 
  individual knots/links merge into a single higher-crossing state.
"""
import numpy as np
import pandas as pd
import sys
import os
from pathlib import Path

# Load project utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def calculate_topological_defect():
    print("="*70)
    print("KSAU v6.2: Topological Binding Energy Analysis")
    print("="*70)

    # 1. Load SSoT Data
    consts = utils_v61.load_constants()
    topo = utils_v61.load_assignments()
    
    v_top = topo['Top']['volume']
    v_bottom = topo['Bottom']['volume']
    v_w_obs = topo['W']['volume'] # Topological volume of W in SSoT
    
    mw_exp = consts['bosons']['W']['observed_mass']
    kappa = consts['kappa']
    bq = -(7 + 7 * kappa) # Bulk Intercept
    
    # Target volume for W from Mass Law: ln(m) = 10*kappa*V + bq
    v_w_target = (np.log(mw_exp) - bq) / (10 * kappa)

    print(f"Data Inputs:")
    print(f"  V(Top)    : {v_top:.4f}")
    print(f"  V(Bottom) : {v_bottom:.4f}")
    print(f"  V(W) [Target from Mass] : {v_w_target:.4f}")
    print(f"  V(W) [SSoT Assignment]  : {v_w_obs:.4f}")
    print("-" * 40)

    # 2. Calculate Defect (delta_V)
    # Model: V_top = V_W + V_bottom - delta_V
    # Using v_w_target (Mass-equivalent volume)
    defect = (v_w_target + v_bottom) - v_top
    
    print(f"Volume Defect Analysis (V_W_target + V_bottom - V_top):")
    print(f"  Total Fragment Volume : {v_w_target + v_bottom:.4f}")
    print(f"  Top Quark Volume      : {v_top:.4f}")
    print(f"  Calculated Defect (dV): {defect:.4f}")
    print("-" * 40)

    # 3. Physical Interpretation
    # Relate dV to Jones Polynomial Entropy (ln|J|)
    # Let's get the ln|J| for Top and Bottom
    _, links = utils_v61.load_data()
    
    def get_lnj(name):
        topo_name = topo[name]['topology'].split('{')[0]
        row = links[links['name'] == topo_name]
        if row.empty:
            row = links[links['name'].str.startswith(topo_name + "{")].iloc[0]
        else:
            row = row.iloc[0]
        jones = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        return np.log(max(1e-10, abs(jones)))

    lnj_top = get_lnj('Top')
    lnj_bottom = get_lnj('Bottom')
    dlnj = abs(lnj_top - lnj_bottom)

    print(f"Topological Interaction Context:")
    print(f"  ln|J| (Top)    : {lnj_top:.4f}")
    print(f"  ln|J| (Bottom) : {lnj_bottom:.4f}")
    print(f"  Delta ln|J|    : {dlnj:.4f}")
    print("-" * 40)

    # Hypothesis: Defect is proportional to complexity separation
    # dV = beta * Delta ln|J|
    beta_effective = defect / dlnj if dlnj > 0 else 0
    print(f"Empirical Binding Constant (beta_binding): {beta_effective:.4f}")
    
    print("\n[CONCLUSION]")
    print(f"The Top -> W + Bottom decay is geometrically consistent if we assume")
    print(f"a Topological Binding Energy (Volume Defect) of Delta_V = {defect:.2f}.")
    print(f"This defect scales with the Jones complexity difference (beta ~ {beta_effective:.2f}).")
    print("This moves KSAU from 'rigid sum' to 'interacting manifold' dynamics.")

if __name__ == "__main__":
    calculate_topological_defect()
