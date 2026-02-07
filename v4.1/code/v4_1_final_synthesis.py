
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# =============================================================================
# CONSTANTS & DATA
# =============================================================================
G = 0.915965594

# Theoretical Base Coefficients
GAMMA_Q_THEORY = (10/7) * G
B_PRIME_THEORY = -(7 + G)
GAMMA_L_THEORY = (2/9) * G

# Particle Data Dictionary
# Includes SnapPy invariants (Vol, CS) and Genus
PARTICLES = [
    # Quarks (Links)
    {'p': 'u', 'type': 'q', 'm': 2.16,      'V': 6.598952,  'CS': -0.1703015, 'g': 0}, # g not used for quarks
    {'p': 'd', 'type': 'q', 'm': 4.67,      'V': 7.327725,  'CS': 0.0,        'g': 0},
    {'p': 's', 'type': 'q', 'm': 93.4,      'V': 9.531880,  'CS': 0.1028109,  'g': 0},
    {'p': 'c', 'type': 'q', 'm': 1270.0,    'V': 11.517101, 'CS': 0.0082835,  'g': 0},
    {'p': 'b', 'type': 'q', 'm': 4180.0,    'V': 12.276278, 'CS': -0.2153578, 'g': 0},
    {'p': 't', 'type': 'q', 'm': 172760.0,  'V': 15.359984, 'CS': -0.1110999, 'g': 0},
    
    # Leptons (Knots) - Added Genus (g)
    # e(3_1): g=1, mu(6_1): g=2, tau(7_1): g=3
    {'p': 'e',   'type': 'l', 'm': 0.510998, 'N2': 9,  'g': 1, 'CS': 0.0},
    {'p': 'mu',  'type': 'l', 'm': 105.658,  'N2': 36, 'g': 2, 'CS': 0.0},
    {'p': 'tau', 'type': 'l', 'm': 1776.86,  'N2': 49, 'g': 3, 'CS': 0.0}
]

df = pd.DataFrame(PARTICLES)
df['ln_m_obs'] = np.log(df['m'])

# =============================================================================
# MODEL DEFINITION
# =============================================================================

def objective(params):
    alpha_cs, beta_g, cl = params
    
    # Predictions
    ln_preds = []
    for _, row in df.iterrows():
        if row['type'] == 'q':
            # Quark: Base + CS correction
            # ln(m) = (10/7)G*V - (7+G) + alpha * CS
            ln_m = GAMMA_Q_THEORY * row['V'] + B_PRIME_THEORY + alpha_cs * row['CS']
        else:
            # Lepton: Base + Genus correction
            # ln(m) = (2/9)G*N^2 + Cl + beta * (g - 1)
            # (g-1) ensures Electron (g=1) is only affected by Cl
            ln_m = GAMMA_L_THEORY * row['N2'] + cl + beta_g * (row['g'] - 1)
            
        ln_preds.append(ln_m)
    
    preds = np.exp(ln_preds)
    mae = np.mean(np.abs((preds - df['m']) / df['m']))
    return mae

def main():
    print("=" * 60)
    print("  KSAU v4.1 Final Synthesis: CS & Genus Correction")
    print("=" * 60)

    # Initial Guesses
    # alpha_cs ~ -0.3 (from Phase 1)
    # beta_g   ~ 0.5  (from Phase 2 Genus model)
    # cl       ~ -2.5 (from v4.0)
    x0 = [-0.3, 0.5, -2.5]
    
    res = minimize(objective, x0, method='Nelder-Mead')
    best_alpha, best_beta, best_cl = res.x
    final_mae = objective(res.x)
    
    print("\nOptimized Parameters:")
    print(f"  alpha_cs (Quark CS factor):   {best_alpha:.6f}")
    print(f"  beta_g   (Lepton Genus factor): {best_beta:.6f}")
    print(f"  C_l      (Lepton Constant):     {best_cl:.6f}")
    
    print(f"\nGlobal MAE: {final_mae:.4%}")
    
    # Detailed Results
    print("\nIndividual Results:")
    print(f"  {'Particle':<8} {'Type':<6} {'Obs (MeV)':>12} {'Pred (MeV)':>12} {'Error %':>10}")
    print("-" * 52)
    
    q_errs = []
    l_errs = []
    
    for _, row in df.iterrows():
        if row['type'] == 'q':
            ln_pred = GAMMA_Q_THEORY * row['V'] + B_PRIME_THEORY + best_alpha * row['CS']
            m_pred = np.exp(ln_pred)
            err = (m_pred - row['m']) / row['m']
            q_errs.append(abs(err))
        else:
            ln_pred = GAMMA_L_THEORY * row['N2'] + best_cl + best_beta * (row['g'] - 1)
            m_pred = np.exp(ln_pred)
            err = (m_pred - row['m']) / row['m']
            l_errs.append(abs(err))
            
        print(f"  {row['p']:<8} {row['type']:<6} {row['m']:>12.4f} {m_pred:>12.4f} {err*100:>10.2f}%")

    print("-" * 52)
    print(f"  Quark MAE:  {np.mean(q_errs):.4%}")
    print(f"  Lepton MAE: {np.mean(l_errs):.4%}")
    
    # Save Plot
    plt.figure(figsize=(10, 6))
    particles = df['p']
    errors = np.concatenate([q_errs, l_errs]) # Order matches iteration? No, be careful
    # Re-calculate ordered errors for plot
    plot_errs = []
    for _, row in df.iterrows():
        if row['type'] == 'q':
            ln_p = GAMMA_Q_THEORY * row['V'] + B_PRIME_THEORY + best_alpha * row['CS']
        else:
            ln_p = GAMMA_L_THEORY * row['N2'] + best_cl + best_beta * (row['g'] - 1)
        err = (np.exp(ln_p) - row['m']) / row['m']
        plot_errs.append(err * 100)
        
    colors = ['red' if t=='q' else 'blue' for t in df['type']]
    plt.bar(particles, plot_errs, color=colors)
    plt.axhline(0, color='k', linewidth=0.5)
    plt.ylabel('Error (%)')
    plt.title(f'KSAU v4.1 Final: Unified CS & Genus Correction (Global MAE {final_mae*100:.2f}%)')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig("v4.1/figures/v4_1_final_fit.png")
    print("\nFigure saved to v4.1/figures/v4_1_final_fit.png")

if __name__ == "__main__":
    main()
