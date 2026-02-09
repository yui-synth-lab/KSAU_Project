import numpy as np
from sklearn.linear_model import LinearRegression

def evolve_theory():
    print("="*80)
    print("KSAU v6.0 -> v6.1 Evolution: Geometric Search")
    print("="*80)

    # 1. Load Data & Constants
    # ---------------------------------------------------------
    kappa = np.pi / 24
    
    # Topology Data (Quarks)
    # T = (2-g)*(-1)^c
    quarks = {
        'Up':      {'V': 6.5517,  'g': 1, 'c': 2, 'obs': 2.16},
        'Down':    {'V': 7.3277,  'g': 1, 'c': 3, 'obs': 4.67},
        'Strange': {'V': 9.5319,  'g': 2, 'c': 3, 'obs': 93.4},
        'Charm':   {'V': 11.5171, 'g': 2, 'c': 2, 'obs': 1270.0},
        'Bottom':  {'V': 12.2763, 'g': 3, 'c': 3, 'obs': 4180.0},
        'Top':     {'V': 15.3600, 'g': 3, 'c': 2, 'obs': 172760.0},
    }
    
    # Calc Twist for Quarks
    for q, d in quarks.items():
        twist = (2 - d['g']) * ((-1)**d['c'])
        d['twist'] = twist

    # CKM Experimental (Magnitude)
    ckm_exp = {
        ('Up', 'Down'): 0.9743, ('Up', 'Strange'): 0.2253, ('Up', 'Bottom'): 0.0036,
        ('Charm', 'Down'): 0.2252, ('Charm', 'Strange'): 0.9734, ('Charm', 'Bottom'): 0.0410,
        ('Top', 'Down'): 0.0086, ('Top', 'Strange'): 0.0400, ('Top', 'Bottom'): 0.9991
    }

    # ---------------------------------------------------------
    # 2. Improve CKM: Add Twist Penalty
    # ---------------------------------------------------------
    print("\n[STEP 1: CKM Twist Penalty Search]")
    
    best_r2 = -100
    best_k_twist = 0
    
    test_range = np.linspace(0, 2.0, 200)
    
    x_data = [] # Stores (dV, dTwist)
    y_data = [] # Stores ln(obs)
    
    for (u, d), val in ckm_exp.items():
        dV = abs(quarks[u]['V'] - quarks[d]['V'])
        dT = abs(quarks[u]['twist'] - quarks[d]['twist'])
        x_data.append([dV, dT])
        y_data.append(np.log(val))
        
    x_data = np.array(x_data)
    y_data = np.array(y_data)
    
    for kt in test_range:
        # Pred = -0.5 * dV - kt * dT
        pred_log = -0.5 * x_data[:, 0] - kt * x_data[:, 1]
        
        ss_res = np.sum((y_data - pred_log)**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r2 = 1 - (ss_res / ss_tot)
        
        if r2 > best_r2:
            best_r2 = r2
            best_k_twist = kt
            
    print(f"  Best Twist Coefficient: {best_k_twist:.4f}")
    print(f"  Resulting R^2         : {best_r2:.4f} (Prev: 0.48)")
    print(f"  Comparison to kappa   : {best_k_twist / kappa:.2f} * kappa")
    print(f"  Comparison to 0.5     : {best_k_twist / 0.5:.2f} * 0.5")

    # ---------------------------------------------------------
    # 3. Solve for Intercepts (B_q, C_l)
    # ---------------------------------------------------------
    print("\n[STEP 2: Intercept Geometric Origin]")
    
    # --- Quarks (B_q) ---
    b_vals = []
    for q, d in quarks.items():
        val = np.log(d['obs']) - 10*kappa*d['V'] - kappa*d['twist']
        b_vals.append(val)
    
    avg_bq = np.mean(b_vals)
    print(f"  Fitted B_q (Quark Intercept) : {avg_bq:.4f}")
    
    targets = {
        "-7 - 7k": -7 - 7*kappa,
        "-1/kappa": -1/kappa,
        "-4 * pi": -4 * np.pi,
        "-20 * G (Catalan)": -20 * 0.915965,
        "ln(m_electron) - 10": np.log(0.511) - 10
    }
    
    best_bq_name = ""
    best_bq_diff = 100
    for name, val in targets.items():
        diff = abs(avg_bq - val)
        print(f"    Target '{name}': {val:.4f} (diff: {diff:.4f})")
        if diff < best_bq_diff:
            best_bq_diff = diff
            best_bq_name = name

        # --- Leptons (C_l) ---
        # Use Electron (N=3) as anchor
        m_e = ksau_config.load_physical_constants()['leptons']['Electron']['mass_mev']
        c_l = np.log(m_e) - (14/9)*kappa * (3**2)
        print(f"\n  Fitted C_l (Lepton Intercept): {c_l:.4f}")
    
        l_targets = {
            "-7 (Simple Integer)": -7.0,
            "-5 * sqrt(2)": -5 * np.sqrt(2),
            "ln(alpha_EM)": np.log(1/137.036),
            "ln(m_pl / m_e) ... no": -100,
            "ln(m_electron) - 10": np.log(m_e) - 10,
            "-3 * pi": -3 * np.pi
        }    
    best_cl_name = ""
    best_cl_diff = 100
    for name, val in l_targets.items():
        diff = abs(c_l - val)
        print(f"    Target '{name}': {val:.4f} (diff: {diff:.4f})")
        if diff < best_cl_diff:
            best_cl_diff = diff
            best_cl_name = name

if __name__ == "__main__":
    evolve_theory()