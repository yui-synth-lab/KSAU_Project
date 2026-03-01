
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Constants
G = 0.915965594
GAMMA_Q_THEORY = (10/7) * G
B_PRIME_THEORY = -(7 + G)
GAMMA_L_THEORY = (2/9) * G

# PDG Masses (MeV) - Unified
OBS_MASSES = {
    'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270, 'b': 4180, 't': 172760,
    'e': 0.510998, 'mu': 105.658, 'tau': 1776.86
}
N2_VALUES = {'e': 9, 'mu': 36, 'tau': 49}

def main():
    # Load Data
    inv_df = pd.read_csv("v4.1/data/topological_invariants.csv")
    
    # Add Electron if missing (it was added in Phase 2 but let's ensure)
    if 'e' not in inv_df['Particle'].values:
        e_data = pd.DataFrame([{
            'Name': '3_1', 'Volume': 0.0, 'CS': 0.0625, 'Writhe': 0.0, 
            'Bridge': 0, 'Particle': 'e', 'Type': 'Lepton'
        }])
        inv_df = pd.concat([inv_df, e_data], ignore_index=True)
        
    df = inv_df.copy()
    df['m_obs'] = df['Particle'].map(OBS_MASSES)
    df['ln_m_obs'] = np.log(df['m_obs'])
    df['N2'] = df['Particle'].map(N2_VALUES).fillna(0) # 0 for quarks

    # Define Base Prediction
    def get_base_log_mass(row):
        if row['Type'] == 'Quark':
            return GAMMA_Q_THEORY * row['Volume'] + B_PRIME_THEORY
        else: # Lepton
            # Cl is optimized later, so just the N^2 part here
            return GAMMA_L_THEORY * row['N2']

    df['ln_m_base_no_c'] = df.apply(get_base_log_mass, axis=1)

    # Optimization
    # Params: alpha (Vol correction), beta (CS correction), cl (Lepton constant)
    def objective(params):
        alpha, beta, cl = params
        
        # Calculate Predictions
        preds = []
        for _, row in df.iterrows():
            base = row['ln_m_base_no_c']
            correction = alpha * row['Volume'] + beta * row['CS']
            
            if row['Type'] == 'Lepton':
                total_ln_m = base + correction + cl
            else:
                total_ln_m = base + correction
            
            preds.append(total_ln_m)
            
        preds = np.array(preds)
        mae = np.mean(np.abs((np.exp(preds) - df['m_obs']) / df['m_obs']))
        return mae

    # Initial guess: alpha=0, beta=0, cl=-2.5
    res = minimize(objective, x0=[0.0, 0.0, -2.503])
    best_alpha, best_beta, best_cl = res.x
    
    # Calculate Final Results
    df['ln_m_pred'] = df.apply(lambda r: 
        (r['ln_m_base_no_c'] + best_alpha * r['Volume'] + best_beta * r['CS'] + best_cl) 
        if r['Type'] == 'Lepton' else 
        (r['ln_m_base_no_c'] + best_alpha * r['Volume'] + best_beta * r['CS']), axis=1)
    
    df['m_pred'] = np.exp(df['ln_m_pred'])
    df['error'] = (df['m_pred'] - df['m_obs']) / df['m_obs']

    # --- Quark-Only Optimization for comparison ---
    # To see if unifying hurts the quark fit
    q_df = df[df['Type'] == 'Quark']
    q_mae = np.mean(np.abs(q_df['error']))
    l_df = df[df['Type'] == 'Lepton']
    l_mae = np.mean(np.abs(l_df['error']))

    print("--- Phase 3: Unified Complex Volume Correction ---")
    print(f"Optimized Parameters:")
    print(f"  Alpha (Volume Correction): {best_alpha:.5f}")
    print(f"  Beta  (CS Correction):     {best_beta:.5f}")
    print(f"  Cl    (Lepton Constant):   {best_cl:.5f}")
    print("-" * 30)
    print(f"Global MAE: {objective(res.x):.2%}")
    print(f"Quark MAE:  {q_mae:.2%}")
    print(f"Lepton MAE: {l_mae:.2%}")
    
    print("\nIndividual Errors:")
    print(df[['Particle', 'Type', 'Volume', 'CS', 'm_obs', 'm_pred', 'error']])
    
    # Plot
    plt.figure(figsize=(10, 6))
    colors = df['Type'].map({'Quark': 'red', 'Lepton': 'blue'})
    plt.bar(df['Particle'], df['error']*100, color=colors)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.ylabel('Error (%)')
    plt.title(f'v4.1 Unified Correction (Alpha={best_alpha:.4f}, Beta={best_beta:.4f})')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig("v4.1/figures/phase3_unified_fit.png")
    print("\nFigure saved to v4.1/figures/phase3_unified_fit.png")

if __name__ == "__main__":
    main()
