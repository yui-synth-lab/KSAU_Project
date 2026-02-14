import numpy as np
import json

def load_data():
    with open("v10.0/data/unified_particle_dataset.json", "r") as f:
        data = json.load(f)
    return data

def verify_boson_shifts():
    data = load_data()
    kappa = data['metadata']['universal_constants']['kappa']
    C_univ = -0.7087 # Electron baseline
    N_boson = 6 # Claude's conclusion
    
    print(f"{'Boson':<8} | {'V':<8} | {'ln(m)_obs':<10} | {'ln(m)_pred':<10} | {'Shift(S)':<10} | {'S/kappa'}")
    print("-" * 70)
    
    bosons = [p for p in data['particles'] if p['sector'] == 'Boson']
    
    for b in bosons:
        v = b['volume']
        lnm_obs = b['ln_m_over_me'] # This is ln(m/me)
        # Note: dataset stores ln(m/me) directly relative to electron
        # Formula: ln(m/me) = N * kappa * V - S (since C_univ is cancelled if using ratio, or included in definition)
        
        # Let's use the absolute log mass formula to be consistent with v9.0
        # ln(m_obs) = ln(m_obs_mev)
        # ln(m_pred) = N * kappa * V + ln(m_e) - S
        
        ln_me = np.log(0.511)
        ln_m_obs = np.log(b['mass_mev'])
        
        # Predicted without shift
        ln_m_base = N_boson * kappa * v + ln_me
        
        # Required Shift
        S = ln_m_base - ln_m_obs
        s_over_kappa = S / kappa
        
        print(f"{b['name']:<8} | {v:<8.4f} | {ln_m_obs:<10.4f} | {ln_m_base:<10.4f} | {S:<10.4f} | {s_over_kappa:.4f}")

if __name__ == "__main__":
    verify_boson_shifts()
