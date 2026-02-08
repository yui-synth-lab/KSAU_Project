import numpy as np
import ksau_config

def analyze_ckm_data_driven():
    # 1. Load Data via Config
    topo_assignments = ksau_config.load_topology_assignments()
    phys_constants = ksau_config.load_physical_constants()
    
    # Map short keys to JSON keys
    key_map = {
        'u': 'Up', 'c': 'Charm', 't': 'Top',
        'd': 'Down', 's': 'Strange', 'b': 'Bottom'
    }
    
    # Build quark data dictionary
    quarks = {}
    for short_k, json_k in key_map.items():
        data = topo_assignments[json_k]
        quarks[short_k] = {
            'Vol': data['volume'],
            'C': data['components'],
            'Gen': data['generation']
        }

    # 2. Load CKM Matrix
    ckm_exp = np.array(phys_constants['ckm']['matrix'])
    
    up_type = ['u', 'c', 't']
    down_type = ['d', 's', 'b']
    kappa = ksau_config.KAPPA
    
    print("="*95)
    print(f"{'CKM Matrix Analysis (Data-Driven from Config)':^95}")
    print("="*95)
    print(f"{'Trans':<8} | {'Exp':<8} | {'ln(Exp)':<8} | {'dVol':<8} | {'-dVol/2':<10} | {'Penalty':<8} | {'Pen/kappa':<8}")
    print("-" * 95)
    
    for i, u_key in enumerate(up_type):
        for j, d_key in enumerate(down_type):
            u = quarks[u_key]
            d = quarks[d_key]
            
            exp_val = ckm_exp[i, j]
            ln_exp = np.log(exp_val)
            d_vol = abs(u['Vol'] - d['Vol'])
            base_term = -d_vol / 2
            penalty = ln_exp - base_term
            pen_kappa = penalty / kappa
            
            print(f"{u_key}->{d_key:<5} | {exp_val:<8.4f} | {ln_exp:<8.4f} | {d_vol:<8.4f} | {base_term:<10.4f} | {penalty:<8.4f} | {pen_kappa:<8.2f}")

    print("="*95)

if __name__ == "__main__":
    analyze_ckm_data_driven()
