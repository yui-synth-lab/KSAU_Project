import sys
import numpy as np
import pandas as pd
import json
from pathlib import Path

# SSoT Loader Setup
sys.path.insert(0, r"E:\Obsidian\KSAU_Project\ssot")
from ksau_ssot import SSOT

def analyze_n_quantization():
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    assignments = ssot.topology_assignments()
    knots_df, links_df = ssot.knot_data()

    kappa = consts['mathematical_constants']['kappa']
    unit_quant = np.pi / 12

    # Particle Data
    particles = {}
    for sector in ['quarks', 'leptons', 'bosons']:
        for p_name, p_meta in params[sector].items():
            particles[p_name] = {
                'mass_mev': p_meta['observed_mass_mev'],
                'topology': assignments[p_name]['topology'],
                'volume': assignments[p_name]['volume']
            }

    # Use a fixed c such that Muon (4_1, V=2.029883) has n=0, eps=0
    # Muon: ln(m) = kappa*V + c + (2n+eps)*kappa
    # 4.660 = 0.1309*2.0298 + c + 0 => c = 4.660 - 0.2657 = 4.3943
    c_base = np.log(particles['Muon']['mass_mev']) - kappa * particles['Muon']['volume']
    
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

    analysis_results = []
    for p_name, p_data in particles.items():
        ln_m = np.log(p_data['mass_mev'])
        v = p_data['volume']
        
        # ln_m = kappa*V + c + NT*kappa  where NT = 2n + eps
        nt_calc = (ln_m - kappa * v - c_base) / kappa
        
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
        
        # Rule check: epsilon = k % 2
        eps = k % 2
        # nt_calc = 2n + eps => n = (nt_calc - eps) / 2
        n_calc = (nt_calc - eps) / 2
        n_int = int(round(n_calc))
        nt_pred = 2 * n_int + eps
        
        analysis_results.append({
            'Particle': p_name,
            'K': k,
            'S': s,
            'C': comp,
            'NT_calc': nt_calc,
            'NT_pred': nt_pred,
            'n_int': n_int,
            'eps': eps,
            'Error_kappa': nt_calc - nt_pred
        })

    print(f"{'Particle':<10} | {'K':>2} | {'S':>2} | {'C':>2} | {'NT_calc':>7} | {'NT_pred':>7} | {'n':>3} | {'eps':>1} | {'Err':>5}")
    print("-" * 75)
    for r in analysis_results:
        print(f"{r['Particle']:<10} | {r['K']:>2} | {r['S']:>2} | {r['C']:>2} | {r['NT_calc']:>7.2f} | {r['NT_pred']:>4} | {r['n_int']:>3} | {r['eps']:>1} | {r['Error_kappa']:>5.2f}")

    # Extract more invariants for the search
    for r in analysis_results:
        p_name = r['Particle']
        topo = particles[p_name]['topology']
        if topo.startswith('L'):
            row = links_df[links_df['name'] == topo]
            inv = row.iloc[0].to_dict() if not row.empty else {}
        else:
            row = knots_df[knots_df['name'] == topo]
            inv = row.iloc[0].to_dict() if not row.empty else {}
        
        jmin, jmax, jrange = get_poly_info(inv.get('jones_polynomial_vector', ''))
        braid = inv.get('braid_index', 0)
        try: braid = int(braid)
        except: braid = 0
        r['jmax'] = jmax
        r['braid'] = braid

    # Search for rule for NT
    print("\nSearching for Integer Rule for NT = f(K, S, C, Jmax, Braid):")
    best_rule = None
    min_mae = 100
    # Focus on K, S, Jmax
    for a in range(-5, 6):
        for b in range(-5, 6):
            for c in range(-5, 6):
                for d in range(-30, 31):
                    mae = 0
                    for r in analysis_results:
                        pred = a*r['K'] + b*r['S'] + c*r['jmax'] + d
                        mae += abs(pred - r['NT_pred'])
                    mae /= len(analysis_results)
                    if mae < min_mae:
                        min_mae = mae
                        best_rule = (a, b, c, d)
    
    print(f"Best NT Rule: NT = {best_rule[0]}*K + {best_rule[1]}*s + {best_rule[2]}*Jmax + {best_rule[3]}")
    print(f"Min MAE: {min_mae:.4f}")

    # Verify
    a, b, c, d = best_rule
    for r in analysis_results:
        pred = a*r['K'] + b*r['S'] + r['jmax']*c + d
        print(f"{r['Particle']:<10} | NT_pred: {r['NT_pred']:>3} | NT_calc: {r['NT_calc']:>7.2f} | Pred: {pred:>3}")

if __name__ == "__main__":
    analyze_n_quantization()
