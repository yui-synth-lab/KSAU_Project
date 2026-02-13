import numpy as np
import pandas as pd
from ksau_config_v7 import load_data, load_physical_constants

def predict_mass(vol, slope, intercept, kappa=0, twist=0):
    return np.exp(slope * vol + intercept + kappa * twist)

def run_simulation():
    print("="*80)
    print("KSAU v7.0: Mass Prediction Simulation (Quantum Model)")
    print("="*80)
    
    data = load_data()
    phys = load_physical_constants()
    
    # -------------------------------------------------------------------------
    # Models
    # -------------------------------------------------------------------------
    models = {
        "v6.0 Baseline": {
            "kappa": np.pi / 24,
            "nq": 10.0,
            "nl": 20.0
        },
        "v7.0 Quantum": {
            "kappa": np.pi / 26,
            "nq": 8.0,
            "nl": 21.4
        }
    }
    
    results = {}
    
    for m_name, m_params in models.items():
        print(f"\nEvaluating Model: {m_name}")
        kappa = m_params['kappa']
        nq = m_params['nq']
        nl = m_params['nl']
        
        errors = []
        
        # We need to find the best intercepts for each model to be fair
        # (v6.0 intercepts were fixed, but v7.0 ones should be optimized)
        
        # Optimization of Intercepts (Shift only)
        # Quarks
        q_residuals = []
        for name in phys['quarks']:
            p = data[name]
            twist = (2 - p['generation']) * ((-1)**p['components'])
            val = np.log(p['observed_mass']) - (nq * kappa * p['volume'] + kappa * twist)
            q_residuals.append(val)
        cq = np.mean(q_residuals)
        
        # Leptons
        l_residuals = []
        for name in phys['leptons']:
            p = data[name]
            val = np.log(p['observed_mass']) - (nl * kappa * p['volume'])
            l_residuals.append(val)
        cl = np.mean(l_residuals)
        
        print(f"  Optimized Intercepts: Cq={cq:.4f}, Cl={cl:.4f}")
        
        # Prediction Loop
        print(f"\n  {'Particle':<12} | {'Observed':<10} | {'Predicted':<10} | {'Error %':<8}")
        print(f"  {'-'*45}")
        
        for sector, slope, intercept in [('quarks', nq*kappa, cq), ('leptons', nl*kappa, cl)]:
            for name in phys[sector]:
                p = data[name]
                obs = p['observed_mass']
                twist = 0
                if sector == 'quarks':
                    twist = (2 - p['generation']) * ((-1)**p['components'])
                
                log_pred = slope * p['volume'] + intercept + kappa * twist
                pred = np.exp(log_pred)
                err = abs(pred - obs) / obs * 100
                errors.append(err)
                print(f"  {name:<12} | {obs:<10.3f} | {pred:<10.3f} | {err:<8.2f}%")
        
        mae = np.mean(errors)
        results[m_name] = mae
        print(f"  {'-'*45}")
        print(f"  MEAN ABSOLUTE ERROR (MAE): {mae:.4f}%")
        
    print("\n" + "="*80)
    print("FINAL COMPARISON")
    print("="*80)
    for name, mae in results.items():
        print(f"  {name:<15}: {mae:.4f}%")
    
    improvement = (results['v6.0 Baseline'] - results['v7.0 Quantum']) / results['v6.0 Baseline'] * 100
    print(f"\n  Improvement: {improvement:.2f}%")
    
    if improvement > 0:
        print("\n✅ THE QUANTUM MODEL (k=26, Nq=8) IS SUPERIOR.")
    else:
        print("\n⚠️  THE BASELINE MODEL IS STILL COMPETITIVE. RE-EVALUATE N_l.")

if __name__ == "__main__":
    run_simulation()
