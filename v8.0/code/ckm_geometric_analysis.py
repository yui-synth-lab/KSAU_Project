
import numpy as np
import json
from pathlib import Path

def main():
    # Quark data with v8.0 derived N values
    quarks = {
        "Up":      {"V": 5.3334895669, "N": 3,  "type": "up"},
        "Charm":   {"V": 11.2155040155, "N": 12, "type": "up"},
        "Top":     {"V": 15.6211281203, "N": 60, "type": "up"},
        "Down":    {"V": 6.5517432879, "N": 3,  "type": "down"},
        "Strange": {"V": 9.3123413166, "N": 6,  "type": "down"},
        "Bottom":  {"V": 15.1566701508, "N": 60, "type": "down"}
    }

    # Observed CKM Matrix (PDG typical values)
    # Rows: u, c, t | Cols: d, s, b
    ckm_obs = np.array([
        [0.9743, 0.2253, 0.0036], # u
        [0.2252, 0.9734, 0.0410], # c
        [0.0086, 0.0405, 0.9991]  # t
    ])

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]

    print("="*80)
    print("KSAU v8.0: Geometric CKM Mixing Analysis")
    print("="*80)
    print()

    kappa = np.pi / 24 # The universal modular heartbeat

    print(f"{'Transition':<15} | {'V_ij (Obs)':<8} | {'Delta(NV)':<10} | {'ln(V_ij)':<10} | {'ln(V_ij)/kappa':<10}")
    print("-" * 75)

    for i, u_name in enumerate(up_types):
        u = quarks[u_name]
        for j, d_name in enumerate(down_types):
            d = quarks[d_name]
            
            v_obs = ckm_obs[i, j]
            
            # Theoretical parameters
            nv_u = u["N"] * u["V"]
            nv_d = d["N"] * d["V"]
            delta_nv = abs(nv_u - nv_d)
            
            ln_v_obs = np.log(v_obs) if v_obs > 0 else -np.inf
            
            ratio_kappa = ln_v_obs / kappa if kappa != 0 else 0
            
            print(f"{u_name+'->'+d_name:<15} | {v_obs:<8.4f} | {delta_nv:<10.2f} | {ln_v_obs:<10.4f} | {ratio_kappa:<10.2f}")

    print()
    print("="*80)
    print("Hypothesis Testing: Theta_ij ~ exp(-kappa * f(V, N))")
    print("="*80)
    print()

    # Searching for a pattern in off-diagonal elements
    # V_us (Cabibbo angle)
    # Transition: Up -> Strange
    # Obs: 0.2253
    # ln(0.2253) = -1.490
    # ratio to kappa: -1.490 / 0.1309 = -11.38
    
    print("Pattern Search for Cabibbo Angle (V_us):")
    v_us_obs = ckm_obs[0, 1]
    u = quarks["Up"]
    s = quarks["Strange"]
    print(f"  Up (N=3, V=5.33) -> Strange (N=6, V=9.31)")
    print(f"  Delta V = {abs(u['V'] - s['V']):.4f}")
    print(f"  Ratio V_s / V_u = {s['V'] / u['V']:.4f}")
    print(f"  N_s / N_u = {s['N'] / u['N']:.4f}")
    
    print()
    print("Observation:")
    print("The off-diagonal elements V_ij seem to be governed by the mismatch")
    print("between the 'Total Trapped Action' (N * V) of the two states.")

if __name__ == "__main__":
    main()
