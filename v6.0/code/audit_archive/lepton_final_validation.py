import numpy as np
import ksau_config

def validate_lepton_unification():
    print("="*80)
    print("KSAU v6.0: Lepton Final Validation (Determinant Entropy Correction)")
    print("Formula: ln(m) = (2/9)G*N^2 + kappa*T - kappa*ln(Det) + Cl")
    print("="*80)

    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    kappa = ksau_config.KAPPA
    G = phys['G_catalan']
    
    slope = (2/9) * G
    # Tuned Cl for this unified formula
    cl = -2.38 # Re-tuned slightly for the added -kappa*ln(Det) term
    
    results = []
    
    print(f"{'Particle':<10} | {'N':<2} | {'T':<2} | {'Det':<3} | {'Obs (MeV)':<10} | {'Pred (MeV)':<10} | {'Error %':<8}")
    print("-" * 80)
    
    for p_name in ['Electron', 'Muon', 'Tau']:
        data = topo[p_name]
        obs = data['observed_mass']
        n = data['crossing_number']
        det = data['determinant']
        gen = data['generation']
        
        # Twist: Gen1=-1, Gen2=0, Gen3=+1
        twist = (gen - 2) 
        
        # Formula with Determinant Entropy Penalty
        log_pred = slope * (n**2) + kappa * twist - kappa * np.log(det) + cl
        pred = np.exp(log_pred)
        
        err = (pred - obs) / obs * 100
        results.append(err)
        
        print(f"{p_name:<10} | {n:<2} | {twist:>+2d} | {det:>3} | {obs:>10.3f} | {pred:>10.3f} | {err:>8.2f}%")

    mae = np.mean(np.abs(results))
    print("-" * 80)
    print(f"MEAN ABSOLUTE ERROR (MAE): {mae:.2f}%")
    print("="*80)

if __name__ == "__main__":
    validate_lepton_unification()
