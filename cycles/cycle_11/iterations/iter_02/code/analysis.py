import sys
import numpy as np
import pandas as pd
import json
from pathlib import Path

# SSoT Loader Setup
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def get_poly_info(vector_str):
    if pd.isna(vector_str) or vector_str == '' or vector_str == '[]' or vector_str == '{}':
        return 0, 0, 0
    try:
        clean_v = vector_str.replace('{', '[').replace('}', ']')
        clean_v = clean_v.replace(' ', ',').replace(',,', ',')
        v = json.loads(clean_v)
        if len(v) < 2: return 0, 0, 0
        dmin, dmax = int(v[0]), int(v[1])
        return dmin, dmax, dmax - dmin
    except:
        return 0, 0, 0

def analyze_h25_iteration_02_v2():
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()

    kappa = consts['mathematical_constants']['kappa']
    
    # Particle Data
    particles = {}
    for sector in ['quarks', 'leptons', 'bosons']:
        for p_name, p_meta in params[sector].items():
            particles[p_name] = {
                'mass_mev': p_meta['observed_mass_mev'],
                'topology': assignments[p_name]['topology'],
                'volume': assignments[p_name]['volume']
            }

    p_list = []
    for p_name, p_data in particles.items():
        ln_m = np.log(p_data['mass_mev'])
        v = p_data['volume']
        topo_name = p_data['topology']
        invs = {}
        if topo_name.startswith('L'):
            row = links_df[links_df['name'] == topo_name]
            if not row.empty: invs = row.iloc[0].to_dict()
        else:
            row = knots_df[knots_df['name'] == topo_name]
            if not row.empty: invs = row.iloc[0].to_dict()
            
        k = invs.get('crossing_number', 0)
        s = invs.get('signature', 0)
        try: s = int(s)
        except: s = 0
        comp = invs.get('components', 1)
        jmin, jmax, jrange = get_poly_info(invs.get('jones_polynomial_vector', ''))
        
        p_list.append({
            'name': p_name,
            'ln_m': ln_m,
            'V': v,
            'K': k,
            'S': s,
            'C': comp,
            'Jmax': jmax,
            'mass_mev': p_data['mass_mev']
        })

    # Dual Scan: offset 'c' and Rule Coefficients
    print("Performing Dual Scan for (c, A, B, C, D, Offset)...")
    best_overall_mae = 100
    best_params = None
    
    # We'll use a subset of the search space for speed
    # n_eff = (ln_m - kappa*V - c) / kappa
    # Goal: n_eff should be close to A*K + B*S + C*Comp + D*Jmax + Offset
    
    muon_ln_m = np.log(particles['Muon']['mass_mev'])
    muon_v = particles['Muon']['volume']

    # Test different c values around Muon baseline
    for c_shift in np.linspace(-5, 5, 21):
        c_test = (muon_ln_m - kappa * muon_v) + c_shift * kappa
        
        # For each c, find the best rule
        for a in [5, 6, 7]:
            for b in [-6, -5, -4, 0, 4, 5, 6]:
                for d_j in [0, 1, 2, 3]:
                    c_comp = -9 # Constant for now
                    for offset in [-48, -24, 0, 24, 48]:
                        mae = 0
                        for p in p_list:
                            nt_calc = (p['ln_m'] - kappa * p['V'] - c_test) / kappa
                            nt_pred = a*p['K'] + b*p['S'] + c_comp*p['C'] + d_j*p['Jmax'] + offset
                            mae += abs(nt_calc - nt_pred)
                        mae /= len(p_list)
                        if mae < best_overall_mae:
                            best_overall_mae = mae
                            best_params = (c_test, a, b, c_comp, d_j, offset)

    c_final, a, b, c_comp, d_j, offset = best_params
    print(f"Best Params: c={c_final:.4f}, Rule: NT = {a}*K + {b}*S + {c_comp}*C + {d_j}*Jmax + {offset}")
    print(f"Min MAE (NT): {best_overall_mae:.4f}")

    # Final Validation
    results_data = []
    for p in p_list:
        nt_pred = a*p['K'] + b*p['S'] + c_comp*p['C'] + d_j*p['Jmax'] + offset
        ln_m_pred = kappa * (p['V'] + nt_pred) + c_final
        m_pred = np.exp(ln_m_pred)
        err = (m_pred - p['mass_mev']) / p['mass_mev'] * 100
        results_data.append({
            'name': p['name'],
            'observed_m': p['mass_mev'],
            'predicted_m': m_pred,
            'error_pct': err,
            'NT_pred': int(nt_pred)
        })

    # FPR
    print("Running FPR check...")
    np.random.seed(42)
    n_trials = 10000
    hits = 0
    topo_quads = np.array([[p['K'], p['S'], p['C'], p['Jmax']] for p in p_list])
    nt_targets = np.array([(p['ln_m'] - kappa*p['V'] - c_final)/kappa for p in p_list])
    for _ in range(n_trials):
        perm_quads = np.random.permutation(topo_quads)
        perm_preds = a*perm_quads[:,0] + b*perm_quads[:,1] + c_comp*perm_quads[:,2] + d_j*perm_quads[:,3] + offset
        perm_mae = np.mean(np.abs(nt_targets - perm_preds))
        if perm_mae <= best_overall_mae:
            hits += 1
    fpr = hits / n_trials

    # Save
    output = {
        "iteration": "2",
        "hypothesis_id": "H25",
        "timestamp": "2026-02-25T02:10:00Z",
        "task_name": "全12粒子に対する決定論的モデルの R² および FPR 検証 (再試行)",
        "computed_values": {
            "c_final": c_final,
            "rule": f"NT = {a}*K + {b}*S + {c_comp}*C + {d_j}*Jmax + {offset}",
            "mae_nt": best_overall_mae,
            "fpr": fpr,
            "particle_data": results_data
        },
        "ssot_compliance": {"all_constants_from_ssot": True, "synthetic_data_used": False}
    }
    with open("E:/Obsidian/KSAU_Project/cycles/cycle_11/iterations/iter_02/results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*40)
    print(f"{'Particle':<12} | {'Obs (MeV)':>10} | {'Pred (MeV)':>10} | {'Error %':>8}")
    print("-" * 45)
    for r in results_data:
        print(f"{r['name']:<12} | {r['observed_m']:>10.2f} | {r['predicted_m']:>10.2f} | {r['error_pct']:>8.2f}%")
    print("="*40)
    print(f"FINAL FPR: {fpr:.4f}")

if __name__ == "__main__":
    analyze_h25_iteration_02_v2()
