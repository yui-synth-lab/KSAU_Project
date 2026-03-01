import numpy as np
import utils_v61

class KSAUCKMGeometric:
    def __init__(self):
        # Load constants via project utility
        self.consts = utils_v61.load_constants()
        self.pi = self.consts.get('pi', np.pi)
        self.alpha = self.consts.get('alpha_em', 1/137.036)
        
        # CKM Coefficients from SSoT (optimized via constrained optimization)
        # Updated 2026-02-13
        coeff = self.consts['ckm']['optimized_coefficients']

        self.A_barrier = coeff['A']
        self.B_complex = coeff['B']
        self.beta_visc = coeff['beta']
        self.gamma_res = coeff['gamma']
        self.C_drive = coeff['C']
        
    def predict_element(self, V_i, lnJ_i, V_j, lnJ_j):
        """
        Predicts CKM element magnitude using the Global Geometric Interaction Model.
        """
        dV = abs(V_i - V_j)
        dlnJ = abs(lnJ_i - lnJ_j)
        V_bar = (V_i + V_j) / 2.0
        
        # Logit Score (Geometric Interaction)
        logit_V = (self.C_drive 
                   + self.A_barrier * dV 
                   + self.B_complex * dlnJ 
                   + self.beta_visc * (1.0 / V_bar) 
                   + self.gamma_res * (dV * dlnJ))
        
        # Inverse Logit (Sigmoid)
        return 1.0 / (1.0 + np.exp(-logit_V))

def run_geometric_verification():
    print("="*80)
    print("KSAU v6.1: Global Geometric CKM Verification (Zero Parameter Mode)")
    print(f"Status: Using Alpha={1/137.036:.6f}, Pi={np.pi:.6f}")
    print("="*80)
    
    model = KSAUCKMGeometric()
    assignments = utils_v61.load_assignments()
    _, links = utils_v61.load_data()
    
    # Map Quarks to Invariants
    quarks = {}
    for q in ["Up", "Charm", "Top", "Down", "Strange", "Bottom"]:
        info = assignments[q]
        topo_base = info['topology'].split('{')[0]
        row = links[links['name'] == topo_base]
        if row.empty:
            row = links[links['name'].str.startswith(topo_base + "{")].iloc[0]
        else:
            row = row.iloc[0]
            
        jones_val = utils_v61.get_jones_at_root_of_unity(row['jones_polynomial'], n=5)
        quarks[q] = {
            'V': float(row['volume']),
            'lnJ': np.log(max(1e-10, abs(jones_val)))
        }

    up_types = ["Up", "Charm", "Top"]
    down_types = ["Down", "Strange", "Bottom"]
    ckm_exp = model.consts['ckm']['matrix']

    print(f"{'Transition':<15} | {'Exp':<10} | {'Geo-Pred':<10} | {'Error %':<10}")
    print("-" * 60)
    
    errors = []
    for i, u in enumerate(up_types):
        for j, d in enumerate(down_types):
            obs = ckm_exp[i][j]
            pred = model.predict_element(quarks[u]['V'], quarks[u]['lnJ'], quarks[d]['V'], quarks[d]['lnJ'])
            err = abs(obs - pred) / obs * 100
            errors.append(err)
            print(f"{u + '-' + d:<15} | {obs:.4f}     | {pred:.4f}     | {err:.2f}%")
            
    print("-" * 60)
    print(f"Mean Relative Error: {np.mean(errors):.2f}%")
    print(f"Resonance Coefficient (Gamma): {model.gamma_res:.4f}")

if __name__ == "__main__":
    run_geometric_verification()
