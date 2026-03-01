import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def analyze_gauge_mass():
    print("="*60)
    print("KSAU v6.2 Phase 2: Gauge Boson Geometric Mass")
    print("="*60)
    
    # 1. Load Data
    knots, links = utils_v61.load_data()
    
    # 2. Target: W Boson Mass (Loaded from SSoT)
    consts = utils_v61.load_constants()
    mw_target = consts['bosons']['W']['observed_mass']
    
    # 10*kappa Law Constants
    kappa = consts.get('kappa', np.pi/24)
    bq = -(7 + 7 * kappa) # Intercept from ksau_config
    
    # Links (Quark-like) and Knots (Lepton-like)
    knots['v_cusp'] = pd.to_numeric(knots['maximum_cusp_volume'], errors='coerce')
    
    print("Analyzing Cusp Volume Distribution...")
    v_cusp_stats = knots['v_cusp'].describe()
    print(v_cusp_stats)
    
    # Critical Volume Calculation using 10*kappa Law: ln(m) = 10*kappa * V + Intercept
    # Note: Gauge bosons are modeled as Bulk-like (10*kappa) due to their link components
    critical_vol = (np.log(mw_target) - bq) / (10 * kappa)
    print(f"\nCalculated Critical Volume for M_W: {critical_vol:.4f}")
    
    # Search for knots/links near this volume with special symmetry
    knots['chern_simons_invariant'] = pd.to_numeric(knots['chern_simons_invariant'], errors='coerce')
    near_w = knots[
        (knots['volume'] >= critical_vol - 0.2) & 
        (knots['volume'] <= critical_vol + 0.2)
    ].sort_values('volume')
    
    print(f"\n[Candidates near M_W Volume ({critical_vol:.2f})]")
    print(f"{'Name':<12} | {'Volume':<8} | {'CS':<8} | {'Symmetry'}")
    print("-" * 50)
    for _, row in near_w.head(10).iterrows():
        cs_val = row['chern_simons_invariant']
        cs_str = f"{cs_val:.4f}" if pd.notna(cs_val) else "N/A"
        print(f"{row['name']:<12} | {row['volume']:.4f}   | {cs_str:<8} | {row['symmetry_type']}")

    # 3. W-Top Connection
    assignments = utils_v61.load_assignments()
    v_top = assignments['Top']['volume']
    v_bottom = assignments['Bottom']['volume']
    
    print("\n[W-Top Connection Analysis]")
    print(f"  Top Quark Volume: {v_top:.4f}")
    print(f"  W Boson Target Volume: {critical_vol:.4f}")
    print(f"  Bottom Quark Volume: {v_bottom:.4f}")
    print(f"  Difference (Top - W): {v_top - critical_vol:.4f}")
    print(f"  Difference (Top - Bottom): {v_top - v_bottom:.4f}")
    print("")
    print("  Testing Fission Model: V_top = V_W + V_bottom")
    print(f"  Sum check: {critical_vol:.2f} + {v_bottom:.2f} = {critical_vol + v_bottom:.2f} (Expected: {v_top:.2f})")
    print(f"  Residual: {abs(v_top - (critical_vol + v_bottom)):.2f}")
    print("")
    print("  LIMITATION (Updated 2026-02-13):")
    print("  The simple volume addition model V_top = V_W + V_bottom does NOT hold")
    print("  with the new v6.0 final topology assignments (constrained optimization).")
    print("  Residual = 13.32 >> 0, indicating the fission mechanism requires refinement.")
    print("  Alternative models (e.g., mass-energy conservation, cusp corrections)")
    print("  may be needed to explain Top -> W + Bottom decay geometrically.")

if __name__ == "__main__":
    analyze_gauge_mass()
