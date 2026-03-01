import pandas as pd
import numpy as np
import json
import os
import bisect
import ksau_config

def search_best_knots_optimized():
    print("="*80)
    print("KSAU v6.0: Lepton Knot Optimization (High Speed)")
    print("="*80)

    phys = ksau_config.load_physical_constants()
    kappa = ksau_config.KAPPA
    
    # Load Knots (C=1)
    df = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', low_memory=False)
    c_map = {
        'name': [c for c in df.columns if 'name' in c.lower()][0],
        'volume': [c for c in df.columns if 'volume' in c.lower() and 'imag' not in c.lower()][0],
        'crossing': [c for c in df.columns if 'crossing' in c.lower()][0],
        'determinant': [c for c in df.columns if 'determinant' in c.lower()][0]
    }
    df = df.rename(columns={v: k for k, v in c_map.items()})
    for c in ['volume', 'crossing']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df[(df['volume'] > 0) & (df['crossing'] <= 12)].sort_values('volume')
    
    vols = df['volume'].values
    names = df['name'].values
    crossings = df['crossing'].values
    dets = df['determinant'].values

    leptons = phys['leptons']
    target_log_masses = np.array([np.log(p['mass_mev']) for p in leptons.values()])
    
    # Target Delta V (assuming 10k slope)
    dV12_tgt = (target_log_masses[1] - target_log_masses[0]) / (10*kappa)
    dV23_tgt = (target_log_masses[2] - target_log_masses[1]) / (10*kappa)
    
    vol_tol = 0.2
    best_score = -1e9
    best_triplet = None

    print(f"Searching {len(vols)} knots with linear spacing filter...")

    for i1 in range(len(vols)):
        v1 = vols[i1]
        if v1 > 10: break
        
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
                
                triplet_vols = np.array([v1, v2, v3])
                # Check Linearity
                r2 = np.corrcoef(triplet_vols, target_log_masses)[0,1]**2
                if r2 < 0.9999: continue
                
                # Check Slope Consistency
                slope, intercept = np.polyfit(triplet_vols, target_log_masses, 1)
                slope_err = abs(slope - 10*kappa) / (10*kappa)
                
                score = (r2 * 1000) - (slope_err * 100)
                
                if score > best_score:
                    best_score = score
                    best_triplet = [
                        {'name': names[i1], 'vol': v1, 'cross': crossings[i1], 'det': dets[i1]},
                        {'name': names[i2], 'vol': v2, 'cross': crossings[i2], 'det': dets[i2]},
                        {'name': names[i3], 'vol': v3, 'cross': crossings[i3], 'det': dets[i3]}
                    ]

    print("\n--- BEST LINEAR KNOT TRIPLET FOUND ---")
    if best_triplet:
        final_vols = [x['vol'] for x in best_triplet]
        slope, intercept = np.polyfit(final_vols, target_log_masses, 1)
        r2 = np.corrcoef(final_vols, target_log_masses)[0,1]**2
        print(f"  R2: {r2:.8f}")
        print(f"  Slope: {slope:.4f} (Theory 10k: {10*kappa:.4f})")
        print(f"  Intercept: {intercept:.4f}")
        print("  Assignments:")
        l_names = list(leptons.keys())
        for i, t in enumerate(best_triplet):
            print(f"    {l_names[i]:<10}: {t['name']:<8} (V={t['vol']:.4f}, N={t['cross']}, Det={t['det']})")
    else:
        print("No suitable linear triplet found within tolerance.")

if __name__ == "__main__":
    search_best_knots_optimized()