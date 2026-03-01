import numpy as np
import ksau_config
import pandas as pd

def validate_paper_i():
    print("="*90)
    print(f"{'KSAU Paper I: Final Statistical Validation (Holographic Dual Model)':^90}")
    print("="*90)

    try:
        topo = ksau_config.load_topology_assignments()
        phys = ksau_config.load_physical_constants()
        coeffs = ksau_config.get_kappa_coeffs()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    kappa = ksau_config.KAPPA
    
    # cl is updated for Entropy Correction in this validation context
    slope_q = coeffs['quark_vol_coeff']
    bq = coeffs['quark_intercept']
    cl_unified = phys['boundary_ansatz']['cl_intercept']
    
    # --- SECTION 1: QUARK MASSES (Bulk Volume Law) ---
    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    q_obs, q_pred = [], []
    
    print(f"\n[SECTION 1: QUARK MASSES (Bulk Volume Law: {slope_q/kappa:.0f}kV)]")
    print(f"{'Particle':<10} | {'Topology':<12} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error (%)':<8}")
    print("-" * 90)
    
    for q in quarks:
        data = topo[q]
        obs = data['observed_mass']
        twist = (2 - data['generation']) * ((-1) ** data['components'])
        
        # ln(m) = Slope_q * V + k*T + Bq
        log_pred = slope_q * data['volume'] + kappa * twist + bq
        pred = np.exp(log_pred)
        
        err = (pred - obs) / obs * 100
        q_obs.append(obs)
        q_pred.append(pred)
        print(f"{q:<10} | {data['topology']:<12} | {obs:>10.2f} | {pred:>10.2f} | {err:>8.2f}%")

    q_r2 = 1 - np.sum((np.log(q_obs) - np.log(q_pred))**2) / np.sum((np.log(q_obs) - np.mean(np.log(q_obs)))**2)
    q_mae = np.mean(np.abs((np.array(q_pred) - np.array(q_obs)) / np.array(q_obs) * 100))

    # --- SECTION 2: CHARGED LEPTON MASSES (Unified Bulk Law: 20kV) ---
    leptons = ['Electron', 'Muon', 'Tau']
    l_obs, l_pred = [], []
    
    # 20*kappa Law derived from Topological Freeze-out
    slope_l_unified = 20 * kappa
    cl_lepton = coeffs['lepton_intercept']
    
    print(f"\n[SECTION 2: CHARGED LEPTON MASSES (Unified Bulk Law: {slope_l_unified/kappa:.0f}kV)]")
    print(f"{'Particle':<10} | {'Topology':<12} | {'Volume':<6} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error (%)':<8}")
    print("-" * 90)
    
    for l in leptons:
        data = topo[l]
        obs = data['observed_mass']
        vol = data['volume']
        
        # ln(m) = 20*kappa * V + Intercept
        log_pred = slope_l_unified * vol + cl_lepton
        pred = np.exp(log_pred)
        
        err = (pred - obs) / obs * 100
        l_obs.append(obs)
        l_pred.append(pred)
        print(f"{l:<10} | {data['topology']:<12} | {vol:>6.2f} | {obs:>10.2f} | {pred:>10.2f} | {err:>8.2f}%")

    l_r2 = 1 - np.sum((np.log(l_obs) - np.log(l_pred))**2) / np.sum((np.log(l_obs) - np.mean(np.log(l_obs)))**2)
    l_mae = np.mean(np.abs((np.array(l_pred) - np.array(l_obs)) / np.array(l_obs) * 100))

    # --- SECTION 3: SUMMARY ---
    print(f"\n[SUMMARY STATISTICS]")
    print("-" * 90)
    print(f"Quark Mass R^2 (Log)        : {q_r2:.6f}")
    print(f"Lepton Mass R^2 (Log)       : {l_r2:.6f}")
    print(f"Quark MAE                   : {q_mae:.2f}%")
    print(f"Lepton MAE                  : {l_mae:.2f}%")
    print("="*90)

if __name__ == "__main__":
    validate_paper_i()