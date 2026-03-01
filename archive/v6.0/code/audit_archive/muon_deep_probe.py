import numpy as np
import ksau_config
import pandas as pd

def deep_probe():
    print("="*80)
    print("KSAU v6.0: Muon Anomaly Deep Probe (Search for the Missing Physics)")
    print("="*80)

    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    kappa = ksau_config.KAPPA
    G = phys['G_catalan']
    
    # 1. Scaling Baseline
    slope = (2/9) * G
    cl = -2.52 # Current tuned intercept
    
    muon = topo['Muon']
    m_obs = muon['observed_mass']
    n = muon['crossing_number']
    det = muon['determinant']
    
    print(f"Muon Properties: N={n}, Det={det}, m_obs={m_obs} MeV")
    
    # --- ANALYSIS 1: The Twist Hypothesis ---
    print("\n[Analysis 1: Generation Twist Recovery]")
    # Apply Quark-like twist: Twist = (2 - gen) * (-1)^comp
    # For Leptons (comp=1): Gen1=-1, Gen2=0, Gen3=+1
    twists = { 'Electron': -1, 'Muon': 0, 'Tau': 1 }
    
    print(f"{'Particle':<10} | {'ln(m) target':<12} | {'slope*N^2':<12} | {'Diff':<10} | {'Twist?':<10}")
    for p in ['Electron', 'Muon', 'Tau']:
        data = topo[p]
        target = np.log(data['observed_mass'])
        val = slope * (data['crossing_number']**2) + cl
        diff = target - val
        print(f"{p:<10} | {target:>12.4f} | {val:>12.4f} | {diff:>10.4f} | {twists[p]:>+7d}k")

    # --- ANALYSIS 2: The 'Strange' Shadow ---
    print("\n[Analysis 2: Strange Quark Interference]")
    # Strange is the 2nd generation partner in the Bulk
    strange = topo['Strange']
    v_strange = strange['volume']
    # m_s / m_mu ratio
    ratio = strange['observed_mass'] / m_obs
    print(f"Strange Volume: {v_strange:.4f}")
    print(f"Mass Ratio (Strange/Muon): {ratio:.4f}")
    # Does ln(ratio) correlate with geometric difference?
    geom_diff = v_strange - (n**2 * (2/9)) # Comparing Bulk Volume to Boundary Complexity
    print(f"Geometric Sector Gap (V_s - N_mu^2 * 2/9): {geom_diff:.4f}")

    # --- ANALYSIS 3: Determinant Entropy ---
    print("\n[Analysis 3: Log-Determinant Penalty]")
    # Maybe ln(m) = slope * N^2 + cl - alpha * ln(Det)
    print(f"{'Particle':<10} | {'ln(Det)':<10} | {'Error Ratio':<10}")
    for p in ['Electron', 'Muon', 'Tau']:
        data = topo[p]
        pred = np.exp(slope * (data['crossing_number']**2) + cl)
        ratio = data['observed_mass'] / pred
        print(f"{p:<10} | {np.log(data['determinant']):>10.4f} | {ratio:>10.4f}")

if __name__ == "__main__":
    deep_probe()