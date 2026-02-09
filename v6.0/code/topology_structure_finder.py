import pandas as pd
import numpy as np
import json
import os
import bisect
import ksau_config
from concurrent.futures import ProcessPoolExecutor

# ============================================================================
# SEARCH WORKER
# ============================================================================
def find_best_triplet_for_comp(comp, vols, names, crossings, dets, target_log_masses, kappa, bq, pi_shift, sector_q):
    y1, y2, y3 = target_log_masses
    dV12_tgt = (y2 - y1) / (10*kappa)
    dV23_tgt = (y3 - y2) / (10*kappa)
    
    vol_tol = 0.2
    best_score = -1e9
    best_triplet = None
    best_intercept = 0

    vols = np.ascontiguousarray(vols)
    sy = y1 + y2 + y3
    syy = y1*y1 + y2*y2 + y3*y3
    n = 3

    # Optimization: Gen 1 should have relatively low volume
    gen1_indices = np.where(vols < 12.0)[0]

    for i1 in gen1_indices:
        v1 = vols[i1]
        
        # Gen 2 candidates
        idx_start2 = bisect.bisect_left(vols, v1 + dV12_tgt - vol_tol)
        idx_end2 = bisect.bisect_right(vols, v1 + dV12_tgt + vol_tol)
        
        for i2 in range(idx_start2, idx_end2):
            v2 = vols[i2]
            
            # Gen 3 candidates
            idx_start3 = bisect.bisect_left(vols, v2 + dV23_tgt - vol_tol)
            idx_end3 = bisect.bisect_right(vols, v2 + dV23_tgt + vol_tol)
            
            for i3 in range(idx_start3, idx_end3):
                v3 = vols[i3]
                
                # Regress
                sx = v1 + v2 + v3
                sxx = v1*v1 + v2*v2 + v3*v3
                sxy = v1*y1 + v2*y2 + v3*y3
                
                denom = (n * sxx - sx * sx)
                if denom == 0: continue
                
                m = (n * sxy - sx * sy) / denom
                b = (sy - m * sx) / n
                
                # R2 Calculation
                num_r = (n * sxy - sx * sy)
                den_r_sq = (n * sxx - sx * sx) * (n * syy - sy * sy)
                if den_r_sq <= 0: r2 = 0
                else: r2 = (num_r * num_r) / den_r_sq
                
                if r2 < 0.999: continue 
                
                # Physics Constraints (Unified Slope)
                slope_err = abs(m - 10*kappa) / (10*kappa)
                if slope_err > 0.05: continue 
                
                # Unified Formula Residuals
                # kT term for Quarks
                t1 = (kappa * (2 - 1) * ((-1)**comp)) if sector_q == 0 else 0
                t2 = (kappa * (2 - 2) * ((-1)**comp)) if sector_q == 0 else 0
                t3 = (kappa * (2 - 3) * ((-1)**comp)) if sector_q == 0 else 0
                
                # Residuals = Sum(|y_obs - (10kV + kT + Bq - Qpi)|)
                err1 = abs(y1 - (10 * kappa * v1 + t1 + bq - sector_q * pi_shift))
                err2 = abs(y2 - (10 * kappa * v2 + t2 + bq - sector_q * pi_shift))
                err3 = abs(y3 - (10 * kappa * v3 + t3 + bq - sector_q * pi_shift))
                resid = (err1 + err2 + err3) / 3
                
                # Scoring: Prioritize R2 and Residuals
                score = (r2 * 1000) - (slope_err * 200) - (resid * 50)
                
                if score > best_score:
                    best_score = score
                    best_intercept = b
                    best_triplet = [
                        {'name': names[i1], 'vol': v1, 'cross': crossings[i1], 'det': dets[i1]},
                        {'name': names[i2], 'vol': v2, 'cross': crossings[i2], 'det': dets[i2]},
                        {'name': names[i3], 'vol': v3, 'cross': crossings[i3], 'det': dets[i3]}
                    ]
                    
    return {'comp': comp, 'score': best_score, 'triplet': best_triplet, 'intercept': best_intercept}

def determine_structure_final():
    print("="*80)
    print("KSAU v6.0: Final Principled Structure Determination")
    print("Rules: Up=C2, Down=C3, Lepton=C2 (Link Unification)")
    print("="*80)

    phys = ksau_config.load_physical_constants()
    kappa = ksau_config.KAPPA
    bq = ksau_config.BQ_DEFAULT
    pi_shift = ksau_config.PI_SHIFT

    def load_csv(filepath):
        df = pd.read_csv(filepath, sep='|', low_memory=False)
        def find_col(possible_names):
            for p in possible_names:
                matches = [c for c in df.columns if p in c.lower() and 'anon' not in c.lower() and 'imag' not in c.lower()]
                if matches: return matches[0]
            return None
        c_map = {
            'name': find_col(['name']),
            'crossing': find_col(['crossing number', 'crossing']),
            'volume': find_col(['hyperbolic volume', 'volume']),
            'determinant': find_col(['determinant']),
            'components': find_col(['components', 'number of components'])
        }
        df = df.rename(columns={v: k for k, v in c_map.items() if v})
        for c in ['crossing', 'volume', 'determinant', 'components']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'components' not in df.columns: df['components'] = 1
        return df

    df_l = load_csv(ksau_config.load_linkinfo_path())
    # We only need LinkInfo for C>=2
    df_all = df_l[(df_l['volume'] > 0) & (df_l['crossing'] <= 12)].sort_values('volume').copy()

    # Sector definitions with ENFORCED components (The Physical Choice)
    sectors = [
        ("Up-Quarks", {k: v for k, v in phys['quarks'].items() if v['comp'] == 2}, 0, 2),
        ("Down-Quarks", {k: v for k, v in phys['quarks'].items() if v['comp'] == 3}, 0, 3),
        ("Leptons", phys['leptons'], 1, 2)
    ]

    results_json = {}
    
    for sector_name, particles, sector_q, enforced_c in sectors:
        print(f"
Analyzing {sector_name} (Fixed C={enforced_c})...")
        target_log_masses = np.array([np.log(p['mass_mev']) for p in particles.values()])
        
        subset = df_all[df_all['components'] == enforced_c]
        
        # We can just call the worker directly since C is fixed
        res = find_best_triplet_for_comp(
            enforced_c, subset['volume'].values, subset['name'].values, 
            subset['crossing'].values, subset['determinant'].values, 
            target_log_masses, kappa, bq, pi_shift, sector_q
        )
        
        print(f"  Best Triplet: {[x['name'] for x in res['triplet']]}")
        print(f"  R2 Score: {res['score']:.2f}, Intercept: {res['intercept']:.4f}")
        
        for i, (p_name, p_data) in enumerate(particles.items()):
            t = res['triplet'][i]
            results_json[p_name] = {
                "topology": str(t['name']),
                "volume": float(t['vol']),
                "crossing": int(t['cross']),
                "components": int(enforced_c),
                "determinant": int(t['det']),
                "generation": int(p_data['gen']),
                "charge_type": "lepton" if sector_name == "Leptons" else ("up-type" if p_name in ["Up","Charm","Top"] else "down-type"),
                "observed_mass": float(p_data['mass_mev']),
                "sector": "lepton" if sector_name=="Leptons" else "quark"
            }

    with open('v6.0/data/topology_assignments.json', 'w') as f:
        json.dump(results_json, f, indent=2)
    print("
SUCCESS: Final Structure Determined and Saved.")

if __name__ == "__main__":
    determine_structure_final()
