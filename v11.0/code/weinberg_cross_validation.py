import numpy as np
import json
import os

def load_ssot():
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "unified_particle_dataset_v11.json")
    with open(json_path, "r") as f:
        return json.load(f)

def weinberg_validation():
    data = load_ssot()
    kappa = data['metadata']['universal_constants']['kappa']
    
    # Target: Predict mW from mZ and kappa ONLY
    def get_mass(name):
        p = [p for p in data['particles'] if p['name'] == name][0]
        # me = 0.511 from dataset? No, let's use standard value for now or extract
        ln_me = np.log(0.511)
        return np.exp(6 * kappa * p['V'] + ln_me - p['n_shift'] * kappa)

    mz_obs = get_mass("Z")
    mw_obs = get_mass("W")
    
    print(f"Observed Z mass (rec): {mz_obs:.2f} MeV")
    print(f"Observed W mass (rec): {mw_obs:.2f} MeV")
    
    mw_pred = mz_obs * np.exp(-kappa)
    error = (mw_pred / mw_obs - 1) * 100
    
    print(f"\nPREDICTION: mW = mZ * exp(-kappa)")
    print(f"Predicted W mass: {mw_pred:.2f} MeV")
    print(f"Error: {error:+.2f}%")
    
    cos2theta_pred = (mw_pred / mz_obs)**2
    cos2theta_obs = (mw_obs / mz_obs)**2
    
    print(f"\nPredicted cos^2 theta_w: {cos2theta_pred:.4f}")
    print(f"Observed cos^2 theta_w:  {cos2theta_obs:.4f}")
    print(f"Error in angle: {(cos2theta_pred/cos2theta_obs-1)*100:+.2f}%")

if __name__ == "__main__":
    weinberg_validation()
