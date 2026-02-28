import sys
import json
import numpy as np
from pathlib import Path

# SSOT Loader integration
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def check_ssot_baseline():
    ssot = SSOT()
    consts = ssot.constants()
    assignments = ssot.topology_assignments()
    
    kappa = consts['mathematical_constants']['kappa']
    viscosity = consts['phase_viscosity_model']['sectors']
    
    results = []
    
    # 12 Particles
    order = [
        ('Electron', 'leptons'), ('Muon', 'leptons'), ('Tau', 'leptons'),
        ('Up', 'quarks_c2'), ('Charm', 'quarks_c2'), ('Top', 'quarks_c2'),
        ('Down', 'quarks_c3'), ('Strange', 'quarks_c3'), ('Bottom', 'quarks_c3'),
        ('W', 'bosons'), ('Z', 'bosons'), ('Higgs', 'bosons')
    ]
    
    for p_name, sector_key in order:
        topo = assignments[p_name]
        v = topo['volume']
        
        # Sector parameters from SSOT
        eta = viscosity[sector_key]['eta']
        intercept = viscosity[sector_key]['intercept']
        
        # ln(m) = eta * kappa * V + intercept
        ln_m_pred = eta * kappa * v + intercept
        m_pred = np.exp(ln_m_pred)
        
        # Get observed mass
        if 'quarks' in sector_key:
            obs = consts['particle_data']['quarks'][p_name]['observed_mass']
        elif 'leptons' in sector_key:
            obs = consts['particle_data']['leptons'][p_name]['observed_mass']
        else:
            obs = consts['particle_data']['bosons'][p_name]['observed_mass']
            
        error = (m_pred - obs) / obs * 100
        
        results.append({
            "particle": p_name,
            "predicted": m_pred,
            "observed": obs,
            "error_pct": error
        })

    # Output table
    print(f"{'Particle':<12} | {'Observed (MeV)':>15} | {'Predicted (MeV)':>15} | {'Error %':>10}")
    print("-" * 60)
    for res in results:
        print(f"{res['particle']:<12} | {res['observed']:>15.2f} | {res['predicted']:>15.2f} | {res['error_pct']:>10.2f}%")
    
    mae = np.mean([abs(res['error_pct']) for res in results])
    print("-" * 60)
    print(f"Mean Absolute Error (MAE): {mae:.4f}%")

if __name__ == "__main__":
    check_ssot_baseline()
