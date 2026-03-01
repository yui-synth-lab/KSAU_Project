import numpy as np
import pandas as pd
import utils_v61

def run_pmns_analysis():
    print("="*60)
    print("KSAU v6.1: PMNS Boundary Resonance Analysis")
    print("="*60)
    
    # 1. Load Knots and Constants
    knots, _ = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # Filter for low crossing number to find candidates
    candidates = knots[knots['crossing_number'] <= 9].copy()
    
    # 2. Define PMNS Target Angles (degrees) from Central Constants
    pmns_data = consts['neutrinos']['pmns_angles_deg']
    targets = {
        '12': pmns_data['theta12'],
        '23': pmns_data['theta23'],
        '13': pmns_data['theta13']
    }
    
    # 3. Compute Metrics
    # "Unknotting Efficiency" hypothesis: related to Volume and Unknotting Number
    # Also calculate Jones Resonance
    
    metrics = []
    
    for _, row in candidates.iterrows():
        try:
            vol = float(row['volume'])
            u_num = float(row['unknotting_number'])
            
            if u_num == 0: 
                eff = 0 # Unknot
            else:
                eff = vol / u_num
                
            # Jones at 2pi/5
            jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
            j_mag = abs(jones_val)
            
            metrics.append({
                'name': row['name'],
                'vol': vol,
                'u_num': u_num,
                'eff': eff,
                'j_mag': j_mag
            })
        except:
            continue
            
    df = pd.DataFrame(metrics)
    
    # 4. Search for Triplet (Nu1, Nu2, Nu3) that fits PMNS
    # Hypothesis: Mixing Angle theta_ij = k * |Eff_i - Eff_j| + c ?
    # OR: theta_ij = k * |J_i - J_j| ?
    # BUT PMNS has large angles. So maybe inverse distance? Or just specific values.
    
    # Let's try to match "Resonance".
    # Resonance usually implies Constructive Interference.
    # Maybe Theta ~ 90 - Difference? Or Theta ~ Sum?
    
    # Let's try a simple model: Theta_ij (deg) = A * |J_i - J_j|
    # If J_i and J_j are close, angle is small? No, we want large angles for 12 and 23.
    # So we want J_i and J_j to be FAR for 12 and 23?
    # But 13 is small.
    # If 1-2 is Far, 2-3 is Far, then 1-3 could be Near or Far.
    # Let's try to find a triplet.
    
    print("Searching for Neutrino Candidates (Top 5 matches)...")
    
    # Simplistic Search: Find 3 knots where pairwise differences match the ratio of angles.
    # Ratio 23:12:13 ~ 49:33:8.6 ~ 5.7 : 3.8 : 1
    
    # We will score triplets.
    best_score = float('inf')
    best_triplet = None
    
    # Limit search space for performance (e.g. first 20 knots)
    search_pool = df.head(30).to_dict('records')
    
    for i in range(len(search_pool)):
        for j in range(i+1, len(search_pool)):
            for k in range(j+1, len(search_pool)):
                n1 = search_pool[i]
                n2 = search_pool[j]
                n3 = search_pool[k]
                
                # Metric: Unknotting Efficiency
                val1 = n1['eff']
                val2 = n2['eff']
                val3 = n3['eff']
                
                # Distances
                d12 = abs(val1 - val2)
                d23 = abs(val2 - val3)
                d13 = abs(val1 - val3)
                
                # Check if they fit the ratio 49 : 33 : 8.6
                # We need a scaling factor 'scale'.
                # Fit: Minimize error of (Scale * d - Theta)
                
                # We want: Scale * d12 ~ 33.4
                #          Scale * d23 ~ 49.0
                #          Scale * d13 ~ 8.6
                
                # Or any permutation of assignment (Nu1, Nu2, Nu3)
                
                perms = [
                    (d12, d23, d13), # 1-2, 2-3, 1-3
                    (d12, d13, d23), # 1-2, 3-2, 1-3 ... wait. 
                    # The pairs are fixed: (1,2), (2,3), (1,3).
                    # But we can assign the knots to 1, 2, 3 in different orders.
                    # 1,2,3: d12, d23, d13
                    # 1,3,2: d13, d32, d12 -> target 33, 49, 8
                ]
                
                # Actually, standard ordering is m1 < m2 < m3 (usually).
                # But mixing angles are between mass eigenstates.
                # Let's just fit the set {d12, d23, d13} to {33.4, 49.0, 8.6}
                
                # Current distances
                dists = sorted([d12, d23, d13])
                targs = sorted([33.4, 49.0, 8.6])
                
                # Linear fit y = ax (pass through zero)
                # a = sum(x*y) / sum(x^2)
                x = np.array(dists)
                y = np.array(targs)
                slope = np.sum(x*y) / np.sum(x**2)
                
                preds = slope * x
                mse = np.mean((y - preds)**2)
                
                if mse < best_score:
                    best_score = mse
                    best_triplet = (n1, n2, n3, slope, preds)

    if best_triplet:
        n1, n2, n3, slope, preds = best_triplet
        print("\nBest Candidate Triplet Found:")
        print(f"  Nu1: {n1['name']} (Eff: {n1['eff']:.4f})")
        print(f"  Nu2: {n2['name']} (Eff: {n2['eff']:.4f})")
        print(f"  Nu3: {n3['name']} (Eff: {n3['eff']:.4f})")
        print(f"  Scaling Factor (deg/eff): {slope:.2f}")
        print(f"  Fit Error (MSE): {best_score:.4f}")
        print("\n  Angle Matches:")
        dists = sorted([abs(n1['eff']-n2['eff']), abs(n2['eff']-n3['eff']), abs(n1['eff']-n3['eff'])])
        targs = sorted([33.4, 49.0, 8.6])
        preds = sorted(preds) # correspond to dists
        
        for d, p, t in zip(dists, preds, targs):
            print(f"    d={d:.4f} -> Pred={p:.2f} deg (Target: {t} deg)")

if __name__ == "__main__":
    run_pmns_analysis()
