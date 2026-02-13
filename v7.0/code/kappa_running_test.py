import numpy as np
import matplotlib.pyplot as plt
from ksau_config_v7 import load_data, load_physical_constants

def analyze_kappa_running():
    print("="*80)
    print("KSAU v7.0: Testing the Running Coupling Hypothesis")
    print("Objective: Solve for individual kappa_i for each fermion.")
    print("="*80)

    data = load_data()
    phys = load_physical_constants()
    
    # Fixed Theoretical Base
    N_q = 8.0
    N_l = 20.0
    
    # Use v6.0 Intercepts as the baseline "Anchor"
    # Note: These might need adjustment, but let's see the relative trend.
    C_q = -8.0540 # From previous simulation
    C_l = -0.6714 # Electron ln(m)
    
    particles = []
    
    print(f"{'Particle':<12} | {'ln(m)':<8} | {'Volume':<8} | {'Eff. Kappa':<12} | {'k_eff (pi/k)'}")
    print("-" * 75)
    
    for name, p in data.items():
        if 'observed_mass' not in p or 'volume' not in p:
            continue
        
        ln_m = np.log(p['observed_mass'])
        V = p['volume']
        
        # Skip Electron (Vol=0, Kappa undefined)
        if V == 0:
            continue
            
        if name in phys['quarks']:
            N = N_q
            C = C_q
            twist_factor = (2 - p['generation']) * ((-1)**p['components'])
            # ln_m = N * k * V + C + k * twist
            # ln_m - C = k * (N * V + twist)
            # k = (ln_m - C) / (N * V + twist)
            k_eff = (ln_m - C) / (N * V + twist_factor)
        else:
            N = N_l
            C = C_l
            k_eff = (ln_m - C) / (N * V)
            
        k_inv = np.pi / k_eff
        
        particles.append({
            'name': name,
            'ln_m': ln_m,
            'k_eff': k_eff,
            'k_inv': k_inv
        })
        
        print(f"{name:<12} | {ln_m:<8.4f} | {V:<8.4f} | {k_eff:<12.6f} | {k_inv:.2f}")

    # Plotting
    names = [p['name'] for p in particles]
    x = [p['ln_m'] for p in particles]
    y = [p['k_eff'] for p in particles]
    
    # Sort by mass
    sorted_indices = np.argsort(x)
    x_sorted = np.array(x)[sorted_indices]
    y_sorted = np.array(y)[sorted_indices]
    names_sorted = np.array(names)[sorted_indices]

    print("\n[Running Trend Summary]")
    for i in range(len(x_sorted)):
        print(f"  {names_sorted[i]:<12}: ln(m)={x_sorted[i]:>6.2f} -> Kappa={y_sorted[i]:.6f} (pi/{np.pi/y_sorted[i]:.2f})")

    # Final Check: Does it run toward pi/26 at high energy?
    kappa_24 = np.pi / 24
    kappa_26 = np.pi / 26
    
    print("\nReference Values:")
    print(f"  pi/24: {kappa_24:.6f}")
    print(f"  pi/26: {kappa_26:.6f}")

if __name__ == "__main__":
    analyze_kappa_running()
