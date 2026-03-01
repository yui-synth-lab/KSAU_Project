import numpy as np
import matplotlib.pyplot as plt
import ksau_config
from pathlib import Path

def robustness_test():
    # Load Data via Config
    try:
        data = ksau_config.load_topology_assignments()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    
    # Extract mass and invariants
    particles = []
    for name, info in data.items():
        # Only process fermions for robustness mass fit
        if info['charge_type'] == 'boson':
            continue
            
        particles.append({
            'name': name,
            'obs': info['observed_mass'],
            'vol': info['volume'],
            'gen': info['generation'],
            'comp': info['components'],
            'type': info['charge_type'],
            'n': info['crossing_number'],
            'is_twist': (info['topology'] == '6_1')
        })
    
    kappa_nominal = ksau_config.KAPPA
    
    # Perturbation range
    deltas = np.linspace(0.9, 1.1, 100)
    maes = []
    
    for d in deltas:
        k = kappa_nominal * d
        errors = []

        # Lepton formula: OFFICIAL 20κV law (unified with quarks)
        slope_l = 20 * k
        # Electron: ground state intercept
        m_e = ksau_config.load_physical_constants()['leptons']['Electron']['observed_mass']
        cl = np.log(m_e)  # Intercept is electron mass (V=0 ground state)

        for p in particles:
            if p['type'] == 'lepton':
                # ln(m) = 20κV + ln(m_e)
                log_pred = slope_l * p['vol'] + cl
            else:
                bq = -(7 + 7 * k)
                twist = (2 - p['gen']) * ((-1)**p['comp'])
                log_pred = 10 * k * p['vol'] + k * twist + bq

            pred = np.exp(log_pred)
            errors.append(abs(pred - p['obs']) / p['obs'] * 100)
        
        maes.append(np.mean(errors))
    
    # Plotting
    output_dir = Path(__file__).parent.parent / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    plt.plot(deltas, maes, 'b-', linewidth=2)
    plt.axvline(1.0, color='r', linestyle='--', label='Theoretical pi/24')
    plt.xlabel('Kappa / (pi/24)')
    plt.ylabel('Global MAE (%)')
    plt.title('Robustness Test: Sensitivity of MAE to Master Constant')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(output_dir / 'kappa_sensitivity.png')
    
    min_idx = np.argmin(maes)
    print(f"Minimum MAE of {maes[min_idx]:.4f}% reached at {deltas[min_idx]:.4f} * kappa")
    print(f"Nominal MAE: {maes[50]:.4f}%") # Index 50 is roughly 1.0

if __name__ == "__main__":
    robustness_test()