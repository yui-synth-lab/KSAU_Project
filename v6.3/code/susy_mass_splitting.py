import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def calculate_susy_splitting():
    print("="*60)
    print("KSAU v6.3 Phase 1: SUSY Mirror Mass Splitting")
    print("="*60)
    
    # 1. Load Data & Constants
    knots, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    assignments = utils_v61.load_assignments()
    
    # 2. Define Particles (Standard Model)
    # Generate from topology_assignments.json
    sm_particles = {}
    for name, data in assignments.items():
        # Determine type (Knot or Link) based on components or topology name
        # L... is Link, others usually Knot. Or check components > 1.
        # But Electron is 3_1 (Knot).
        
        # Base topology name
        base_topo = data['topology'].split('{')[0]
        
        # Heuristic for type
        if data['components'] == 1:
            p_type = "Knot"
        else:
            p_type = "Link"
            
        sm_particles[name] = {
            "topo": base_topo,
            "type": p_type,
            "obs_mass": data['observed_mass']
        }
    
    # 3. Parameters
    # ln(m) = A*V + B*CS + C
    kappa = consts['kappa']
    A = 10 * kappa
    C = -(7 + 7 * kappa)   
    
    # Hypothesis: B (SUSY Coupling) is related to the "Geometric Phase"
    # Let's use B = 2*pi, as CS is periodic in 2pi^2? 
    # Or B = 1.0 for simplicity to see the scale.
    # In many papers, CS splitting is O(1).
    B = 1.0 
    
    print(f"Using B (SUSY Coupling) = {B:.2f}")
    print("-" * 60)
    print(f"{'Particle':<12} | {'Symmetry':<15} | {'Mass (MeV)':<10} | {'Sparticle (MeV)'}")
    print("-" * 60)
    
    results = []
    
    for name, data in sm_particles.items():
        # Get properties
        if data['type'] == "Knot":
            row = knots[knots['name'] == data['topo']]
        else:
            row = links[links['name'] == data['topo']]
            if row.empty:
                row = links[links['name'].str.startswith(data['topo'] + "{")]
        
        if row.empty: continue
        row = row.iloc[0]
        
        vol = float(row['volume'])
        # Handle missing CS in links
        cs_raw = row['chern_simons_invariant'] if 'chern_simons_invariant' in row else 0.05
        try:
            cs = float(cs_raw) if pd.notna(cs_raw) else 0.05
        except:
            cs = 0.05 # Fallback for 'Not Hyperbolic' or other strings
            
        sym = row.get('symmetry_type', "Chiral (Assumed)")
        
        # Standard Mass (Positive CS bias?)
        ln_m = A * vol + B * cs + C
        m_sm = np.exp(ln_m)
        
        # Sparticle Mass (Mirror Image -> Negative CS)
        ln_m_susy = A * vol + B * (-cs) + C
        m_susy = np.exp(ln_m_susy)
        
        # Adjustment: If amphicheiral, CS=0, No Splitting (Symmetry Restored)
        is_amphi = "amphi" in str(sym).lower()
        if is_amphi:
            m_susy = m_sm
            status = "Amphi (Restored)"
        else:
            status = "Chiral (Split)"
            
        print(f"{name:<12} | {status:<15} | {m_sm:10.2f} | {m_susy:10.2f}")
        
        results.append({
            'name': name,
            'sm': m_sm,
            'susy': m_susy,
            'gap': m_susy - m_sm
        })

    # 4. Analysis
    print("\n[Analysis]")
    print("  For Chiral particles (Up, Down, Electron), the mirror image has a different mass.")
    print("  With B = 1.0, the Sparticle is roughly exp(2*B*CS) times heavier/lighter.")
    print("  Example: Top quark Sparticle (Stop) would be significantly shifted.")
    print("  If B is large, SUSY particles become very heavy (TeV scale).")
    
    # Calculate required B to get Stop at 1 TeV
    m_top = sm_particles['Top']['obs_mass']
    # m_top MeV -> 1000 GeV => ratio
    ratio = 1000000.0 / m_top
    # exp(2 * B * CS) = ratio
    # 2 * B * CS = ln(ratio)
    # B = ln(ratio) / (2 * 0.05)
    b_req = np.log(ratio) / (2 * 0.05)
    
    print(f"\n[Required B for 1 TeV Stop]")
    print(f"  To reach M_Stop = 1000 GeV from M_Top = {m_top/1000:.1f} GeV:")
    print(f"  B_critical ~ {b_req:.2f}")

if __name__ == "__main__":
    calculate_susy_splitting()
