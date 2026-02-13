import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from ksau_config_v7 import load_data, load_physical_constants

def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma)**2) / (sigma * np.sqrt(2 * np.pi))

def run_bayesian_inference():
    print("--- KSAU v7.0 Route C: Bayesian Measurement of Kappa ---")
    
    # 1. Load Data
    data = load_data()
    phys = load_physical_constants()
    
    # 2. Extract Data Points (Log Mass vs Volume)
    # Model: ln(m) = Slope * V + Intercept + Twist_Term
    # Quark Twist: kappa * (2 - gen) * (-1)^components
    
    quarks = []
    leptons = []
    
    print("\n[Data Loaded]")
    for name, p in data.items():
        if 'observed_mass' not in p or 'volume' not in p:
            continue
            
        sigma_log = 0.01 
        
        point = {
            'name': name,
            'ln_m': np.log(p['observed_mass']),
            'V': p['volume'],
            'sigma': sigma_log,
            'twist_factor': 0 # Default for Leptons
        }
        
        if name in phys['quarks']:
            # Calculate Quark Twist
            gen = p.get('generation', 0)
            comp = p.get('components', 0)
            # Formula: (2 - gen) * (-1)^comp
            # Note: comp is integer.
            twist = (2 - gen) * ((-1)**comp)
            point['twist_factor'] = twist
            
            quarks.append(point)
            print(f"  Quark: {name:8s} | V={p['volume']:.4f} | Twist={twist:>2} | ln(m)={point['ln_m']:.4f}")
            
        elif name in phys['leptons']:
            leptons.append(point)
            print(f"  Lepton:{name:8s} | V={p['volume']:.4f} | Twist= 0 | ln(m)={point['ln_m']:.4f}")
            
    # 3. Optimization for Fixed Quantum Kappa
    k_v7 = np.pi / 26
    print(f"\n[Fixed Quantum Model: Kappa = pi/26 ({k_v7:.6f})]")
    
    # Optimize N_q
    nq_range = np.linspace(7.0, 11.0, 1000)
    best_nq = 0
    min_chi2_q = float('inf')
    for nq in nq_range:
        slope_q = nq * k_v7
        residuals_q = [q['ln_m'] - (slope_q * q['V'] + k_v7 * q['twist_factor']) for q in quarks]
        C_q_opt = np.mean(residuals_q)
        chi2_q = sum([(r - C_q_opt)**2 for r in residuals_q])
        if chi2_q < min_chi2_q:
            min_chi2_q = chi2_q
            best_nq = nq
            
    # Optimize N_l
    nl_range = np.linspace(18.0, 24.0, 1000)
    best_nl = 0
    min_chi2_l = float('inf')
    for nl in nl_range:
        slope_l = nl * k_v7
        residuals_l = [l['ln_m'] - slope_l * l['V'] for l in leptons]
        C_l_opt = np.mean(residuals_l)
        chi2_l = sum([(r - C_l_opt)**2 for r in residuals_l])
        if chi2_l < min_chi2_l:
            min_chi2_l = chi2_l
            best_nl = nl

    print(f"  Optimal N_q: {best_nq:.4f}")
    print(f"  Optimal N_l: {best_nl:.4f}")
    
    # Check if N_l is close to a significant number
    # (e.g., 21.6? 22?)
    
    return k_v7, best_nq, best_nl



        
    print(f"\nSaved 'measurement' of kappa to memory: {kappa_peak}")
    
    return kappa_peak

if __name__ == "__main__":
    run_bayesian_inference()
