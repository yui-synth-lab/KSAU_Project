import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# v4.0 Constants
G = 0.915965594
GAMMA_L_THEORY = (2/9) * G

# Observed Masses (MeV)
LEPTONS_OBS = {
    'e': 0.510998,
    'mu': 105.658,
    'tau': 1776.86
}

# N^2 values from v4.0
LEPTONS_N2 = {
    'e': 9,
    'mu': 36,
    'tau': 49
}

def main():
    # Load previously collected invariants
    inv_df = pd.read_csv("v4.1/data/topological_invariants.csv")
    df = inv_df[inv_df['Type'] == 'Lepton'].copy()
    
    # Fill in Electron (3_1) which was error
    if 'e' not in df['Particle'].values:
        e_data = pd.DataFrame([{
            'Name': '3_1', 'Volume': 0.0, 'CS': 0.0625, 'Writhe': 0.0, 
            'Bridge': 0, 'Particle': 'e', 'Type': 'Lepton'
        }])
        df = pd.concat([df, e_data], ignore_index=True)

    df['m_obs'] = df['Particle'].map(LEPTONS_OBS)
    df['N2'] = df['Particle'].map(LEPTONS_N2)
    df['ln_m_obs'] = np.log(df['m_obs'])
    
    # Baseline v4.0 (Fixing Cl with Electron)
    df['ln_m_v40_no_cl'] = GAMMA_L_THEORY * df['N2']
    e_row = df[df['Particle']=='e']
    cl_v40 = e_row['ln_m_obs'].values[0] - e_row['ln_m_v40_no_cl'].values[0]
    df['ln_m_v40'] = df['ln_m_v40_no_cl'] + cl_v40
    df['err_v40'] = (np.exp(df['ln_m_v40']) - df['m_obs']) / df['m_obs']
    
    print("--- Lepton v4.0 Baseline ---")
    print(f"Fixed Cl: {cl_v40:.4f}")
    print(df[['Particle', 'm_obs', 'err_v40']])

    # Hypothesis 1: CS Correction
    # ln(m) = (2/9)G * N2 + beta * CS + Cl
    def objective_cs(params):
        beta, cl = params
        ln_m_pred = GAMMA_L_THEORY * df['N2'] + beta * df['CS'] + cl
        mae = np.mean(np.abs((np.exp(ln_m_pred) - df['m_obs']) / df['m_obs']))
        return mae

    res_cs = minimize(objective_cs, x0=[0.0, cl_v40])
    beta_best, cl_best = res_cs.x
    
    df['ln_m_v41_cs'] = GAMMA_L_THEORY * df['N2'] + beta_best * df['CS'] + cl_best
    df['err_v41_cs'] = (np.exp(df['ln_m_v41_cs']) - df['m_obs']) / df['m_obs']
    
    print("\n--- Hypothesis 1: CS Correction ---")
    print(f"Best Beta: {beta_best:.4f}, Best Cl: {cl_best:.4f}")
    print(f"Lepton MAE: v4.0 = {np.mean(np.abs(df['err_v40'])):.2%}, v4.1 = {objective_cs([beta_best, cl_best]):.2%}")
    print(df[['Particle', 'm_obs', 'err_v41_cs']])

    # Hypothesis 2: Volume Hybrid (Correction for hyperbolic MU)
    v_mu = df.loc[df['Particle']=='mu', 'Volume'].values[0]
    # delta = (ln_obs - ln_pred_v40) / V
    delta = (df.loc[df['Particle']=='mu', 'ln_m_obs'].values[0] - df.loc[df['Particle']=='mu', 'ln_m_v40'].values[0]) / v_mu
    
    print("\n--- Hypothesis 2: Volume Correction (Muon only) ---")
    print(f"Delta (Vol factor for Muon): {delta:.4f}")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    df_sorted = df.sort_values('m_obs')
    x = np.arange(len(df_sorted))
    plt.bar(x - 0.2, df_sorted['err_v40']*100, width=0.4, label='v4.0 Baseline', color='gray', alpha=0.6)
    plt.bar(x + 0.2, df_sorted['err_v41_cs']*100, width=0.4, label='v4.1 CS Correction', color='blue')
    plt.xticks(x, [p.upper() for p in df_sorted['Particle']])
    plt.ylabel('Error (%)')
    plt.title('Lepton Mass Error: CS Correction Analysis')
    plt.legend()
    plt.grid(axis='y', linestyle='--')
    plt.savefig("v4.1/figures/phase2_lepton_error.png")
    print("\nFigure saved to v4.1/figures/phase2_lepton_error.png")

if __name__ == "__main__":
    main()