
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# v4.0 Constants
G = 0.915965594
GAMMA_Q_THEORY = (10/7) * G
B_PRIME_THEORY = -(7 + G)

# PDG Masses (MeV)
OBS_MASSES = {
    'u': 2.16,
    'd': 4.67,
    's': 93.4,
    'c': 1270,
    'b': 4180,
    't': 172760
}

def main():
    # Load invariants
    df = pd.read_csv("v4.1/data/topological_invariants.csv")
    quarks = df[df['Type'] == 'Quark'].copy()
    quarks['m_obs'] = quarks['Particle'].map(OBS_MASSES)
    quarks['ln_m_obs'] = np.log(quarks['m_obs'])
    
    # v4.0 Prediction (Baseline)
    quarks['ln_m_v40'] = GAMMA_Q_THEORY * quarks['Volume'] + B_PRIME_THEORY
    quarks['err_v40'] = (np.exp(quarks['ln_m_v40']) - quarks['m_obs']) / quarks['m_obs']
    
    # Phase 1: CS Correction Model
    # ln(m) = ln(m_v40) + alpha * CS
    def objective(alpha):
        ln_m_pred = quarks['ln_m_v40'] + alpha * quarks['CS']
        mae = np.mean(np.abs((np.exp(ln_m_pred) - quarks['m_obs']) / quarks['m_obs']))
        return mae

    res = minimize(objective, x0=0.0)
    alpha_best = res.x[0]
    
    quarks['ln_m_v41'] = quarks['ln_m_v40'] + alpha_best * quarks['CS']
    quarks['err_v41'] = (np.exp(quarks['ln_m_v41']) - quarks['m_obs']) / quarks['m_obs']
    
    print(f"--- Phase 1: Heavy Quark Correction Result ---")
    print(f"Optimized Alpha (CS factor): {alpha_best:.4f}")
    print(f"Global Quark MAE: v4.0 = {objective(0.0):.2%}, v4.1 = {objective(alpha_best):.2%}")
    print("\nIndividual Particle Errors:")
    print(quarks[['Particle', 'Volume', 'CS', 'err_v40', 'err_v41']])
    
    # Plot comparison
    plt.figure(figsize=(10, 6))
    particles = quarks['Particle'].values
    x = np.arange(len(particles))
    plt.bar(x - 0.2, quarks['err_v40']*100, width=0.4, label='v4.0 (Baseline)', color='gray', alpha=0.6)
    plt.bar(x + 0.2, quarks['err_v41']*100, width=0.4, label='v4.1 (CS Corrected)', color='red')
    plt.xticks(x, [p.upper() for p in particles])
    plt.ylabel('Error (%)')
    plt.title('Quark Mass Error Comparison: v4.0 vs v4.1 (CS Correction)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig("v4.1/figures/phase1_error_comparison.png")
    print("\nFigure saved to v4.1/figures/phase1_error_comparison.png")

if __name__ == "__main__":
    main()
