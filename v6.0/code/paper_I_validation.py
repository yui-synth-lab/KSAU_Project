import numpy as np
import ksau_config
import pandas as pd

def validate_paper_i():
    print("="*90)
    print(f"{'KSAU Paper I: Final Statistical Validation (Quarks & Charged Leptons)':^90}")
    print("="*90)

    # 1. Load Data
    try:
        topo = ksau_config.load_topology_assignments()
        phys = ksau_config.load_physical_constants()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    kappa = ksau_config.KAPPA
    # bq = ksau_config.BQ_DEFAULT  <-- OLD
    bq = -(7 + 7 * kappa)        # <-- NEW Geometric Definition
    
    # 2. Quark Analysis
    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    q_obs = []
    q_pred = []
    
    print(f"\n[SECTION 1: QUARK MASSES]")
    print(f"{'Particle':<10} | {'Topology':<12} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error (%)':<8}")
    print("-" * 90)
    
    for q in quarks:
        data = topo[q]
        obs = data['observed_mass']
        # ln(m) = 10*kappa*V + kappa*Twist + Bq
        twist = (2 - data['generation']) * ((-1) ** data['components'])
        log_pred = 10 * kappa * data['volume'] + kappa * twist + bq
        pred = np.exp(log_pred)
        
        err = (pred - obs) / obs * 100
        q_obs.append(obs)
        q_pred.append(pred)
        print(f"{q:<10} | {data['topology']:<12} | {obs:>10.2f} | {pred:>10.2f} | {err:>8.2f}%")

    q_r2 = 1 - np.sum((np.log(q_obs) - np.log(q_pred))**2) / np.sum((np.log(q_obs) - np.mean(np.log(q_obs)))**2)
    q_mae = np.mean(np.abs((np.array(q_pred) - np.array(q_obs)) / np.array(q_obs) * 100))

    # 3. Lepton Analysis
    leptons = ['Electron', 'Muon', 'Tau']
    l_obs = []
    l_pred = []
    
    # Calibration for Leptons (Parameter-Free)
    gamma_l = (14/9) * kappa
    
    # NEW GEOMETRIC CONSTANT for Cl
    # Cl = kappa - (7/3)*(1 + kappa)
    # This removes the dependency on Electron mass anchor.
    cl = kappa - (7/3) * (1 + kappa)
    
    print(f"\n[SECTION 2: CHARGED LEPTON MASSES]")
    print(f"Formula: ln(m) = (14/9)k N^2 + Twist + (k - 7/3(1+k))")
    print(f"{'Particle':<10} | {'N^2':<5} | {'Twist':<6} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error (%)':<8}")
    print("-" * 90)
    
    for l in leptons:
        data = topo[l]
        obs = data['observed_mass']
        n2 = data['crossing_number']**2
        twist_corr = -1/6 if data['topology'] == '6_1' else 0
        
        log_pred = gamma_l * n2 + twist_corr + cl
        pred = np.exp(log_pred)
        
        err = (pred - obs) / obs * 100
        l_obs.append(obs)
        l_pred.append(pred)
        print(f"{l:<10} | {n2:<5} | {twist_corr:<6.3f} | {obs:>10.2f} | {pred:>10.2f} | {err:>8.2f}%")

    l_r2 = 1 - np.sum((np.log(l_obs) - np.log(l_pred))**2) / np.sum((np.log(l_obs) - np.mean(np.log(l_obs)))**2)
    l_mae = np.mean(np.abs((np.array(l_pred) - np.array(l_obs)) / np.array(l_obs) * 100))

    # 4. CKM Analysis (Foundation verification)
    ckm_exp = np.array(phys['ckm']['matrix'])
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    print(f"\n[SECTION 3: CKM MIXING CORRELATION]")
    print(f"Theory: ln|Vij| ~ -0.5 * dVol")
    print("-" * 90)
    
    d_vols = []
    ln_vij = []
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            dv = abs(topo[u]['volume'] - topo[d]['volume'])
            val = ckm_exp[i, j]
            d_vols.append(dv)
            ln_vij.append(np.log(val))
    
    # Simple check for the -0.5 factor
    coeffs = np.polyfit(d_vols, ln_vij, 1)
    print(f"Empirical Fit: ln|Vij| = {coeffs[0]:.4f} * dVol + {coeffs[1]:.4f}")
    print(f"Target Factor: -0.5000")
    print(f"Delta Factor : {abs(coeffs[0] - (-0.5)):.4f}")

    # 5. Summary Stats for Paper I
    print(f"\n[SUMMARY STATISTICS FOR PAPER I]")
    print("-" * 90)
    print(f"Quark Mass R^2 (Log Scale)  : {q_r2:.6f}")
    print(f"Quark Mass MAE              : {q_mae:.2f}%")
    print(f"Lepton Mass R^2 (Log Scale) : {l_r2:.6f}")
    print(f"Lepton Mass MAE             : {l_mae:.2f}%")
    print(f"Universal Constant kappa    : pi/24 ({kappa:.6f})")
    print("="*90)

if __name__ == "__main__":
    validate_paper_i()
