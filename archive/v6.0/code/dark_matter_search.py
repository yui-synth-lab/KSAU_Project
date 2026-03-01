import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ksau_config
from pathlib import Path

def search_dark_matter_csv():
    # ---------------------------------------------------------
    # 1. Constants
    # ---------------------------------------------------------
    KAPPA = ksau_config.KAPPA
    BQ = ksau_config.BQ_DEFAULT
    
    csv_path = ksau_config.load_knotinfo_path()
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        return

    print("="*80)
    print("KSAU v6.0 Data-Driven: Dark Matter Candidate Search")
    print("="*80)
    print(f"Source: {csv_path}")
    print("Criterion: Determinant = 1 (Topologically Neutral)")
    print("-" * 80)

    # ---------------------------------------------------------
    # 2. Load and Filter Data
    # ---------------------------------------------------------
    # The file has a complex header (multi-line). 
    # Row 0: internal names, Row 1: display names.
    df = pd.read_csv(csv_path, sep='|', skiprows=[1])
    
    # Filter for Determinant = 1
    df['determinant'] = pd.to_numeric(df['determinant'], errors='coerce')
    
    # Volume column handling: "Not Hyperbolic" -> NaN, then numeric
    df['volume_num'] = pd.to_numeric(df['volume'], errors='coerce')
    
    dm_pool = df[(df['determinant'] == 1) & (df['volume_num'] > 0)].copy()
    
    # Sort by crossing number and then volume for stability
    df['crossing_number'] = pd.to_numeric(df['crossing_number'], errors='coerce')
    dm_pool = dm_pool.sort_values(['crossing_number', 'volume_num'])

    print(f"Found {len(dm_pool)} unique candidates with Det=1 and non-zero Volume.")
    print("-" * 80)
    print(f"{'Knot':<15} | {'N':<4} | {'Vol':<8} | {'Pred Mass (GeV)':<15} | {'Note'}")
    print("-" * 80)
    
    # Display top interesting ones
    display_pool = dm_pool.head(15)
    
    dm_masses = []
    dm_vols = []
    
    for _, row in display_pool.iterrows():
        name = row['name']
        vol = row['volume_num']
        n = row['crossing_number']
        
        # Calculate Mass: ln(m_MeV) = 10*kappa*Vol + BQ
        ln_m_mev = 10 * KAPPA * vol + BQ
        m_mev = np.exp(ln_m_mev)
        m_gev = m_mev / 1000.0
        
        dm_masses.append(m_gev)
        dm_vols.append(vol)
        
        if m_gev < 1: note = "Light DM"
        elif m_gev < 1000: note = "WIMP Range"
        else: note = "Heavy DM"
            
        print(f"{name:<15} | {n:<4.0f} | {vol:<8.3f} | {m_gev:<15.4f} | {note}")

    # ---------------------------------------------------------
    # 3. Visualization
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot DM Pool (all found)
    full_dm_vols = dm_pool['volume_num']
    full_dm_masses = np.exp(10 * KAPPA * full_dm_vols + BQ) / 1000.0
    ax.scatter(full_dm_vols, full_dm_masses, s=50, c='black', alpha=0.3, label='Det=1 Candidates')
    
    # Highlight specific ones
    for i in [0, len(display_pool)//2, len(display_pool)-1]:
        if i < len(dm_masses):
            ax.annotate(display_pool.iloc[i]['name'], (dm_vols[i], dm_masses[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=9)

    # SM Quarks for Scale (Load from config)
    phys = ksau_config.load_physical_constants()
    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    sm_masses = [phys['quarks'][q]['observed_mass'] / 1000.0 for q in quarks]
    # For visualization, approximate volumes are used
    sm_vols = [6.55, 7.33, 9.53, 11.52, 12.28, 15.36]
    ax.scatter(sm_vols, sm_masses, s=100, c='red', marker='s', label='SM Quarks')

    ax.set_yscale('log')
    ax.set_xlabel('Hyperbolic Volume')
    ax.set_ylabel('Mass (GeV)')
    ax.set_title('Topological Dark Matter Spectrum (KnotInfo Search)')
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.legend()
    
    output_dir = Path('v6.0/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'dark_matter_candidates_data.png'
    
    plt.savefig(output_path, dpi=300)
    print("-" * 80)
    print(f"Plot saved to {output_path}")
    print("="*80)

if __name__ == "__main__":
    search_dark_matter_csv()