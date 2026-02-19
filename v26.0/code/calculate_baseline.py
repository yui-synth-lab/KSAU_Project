import sys
import json
import numpy as np
from pathlib import Path

# Path setup
BASE = Path("E:/Obsidian/KSAU_Project")
sys.path.insert(0, str(BASE / "v23.0" / "code"))
from loo_cv_engine_v23_final_audit import LOOCVFinalAudit

# SSoT Paths
DATA_DIR        = BASE / "v6.0" / "data"
PHYS_CONSTANTS  = DATA_DIR / "physical_constants.json"
COSMO_CONSTANTS = DATA_DIR / "cosmological_constants.json"
WL5_CONFIG      = DATA_DIR / "wl5_survey_config.json"

def calculate_baseline_chi2():
    with open(PHYS_CONSTANTS, "r", encoding="utf-8") as f:
        phys = json.load(f)
    with open(COSMO_CONSTANTS, "r", encoding="utf-8") as f:
        cosmo = json.load(f)
    with open(WL5_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
        surveys = config["surveys"]
        leech = config["expected_leech_assignment"]
    
    ksau = LOOCVFinalAudit(config_path=str(COSMO_CONSTANTS))
    
    kappa = phys["kappa"]
    r_base = 3.0 / (2.0 * kappa)
    beta = cosmo["beta_ssot"]
    growth_index = cosmo["scaling_laws"]["growth_index"]
    
    print(f"Baseline Params: R_base={r_base:.4f}, Beta={beta:.4f}, Growth Index={growth_index:.4f}")
    
    chi2 = 0.0
    for name, sv in surveys.items():
        shell_mag = leech[name]["shell_mag"]
        z = sv["z_eff"]
        r0 = r_base * shell_mag
        rz = r0 * (1.0 + z)**(-beta)
        
        s8_pred = ksau.predict_s8_z(z, rz, 0.0, use_nl=True)
        
        a = 1.0 / (1.0 + z)
        s8_obs_z = sv["S8_obs"] * (a**growth_index)
        s8_err_z = sv["S8_err"] * (a**growth_index)
        
        term = ((s8_pred - s8_obs_z) / s8_err_z)**2
        chi2 += term
        print(f"  {name:<12}: rz={rz:6.3f}, pred={s8_pred:.4f}, obs={s8_obs_z:.4f}, chi2_term={term:.4f}")
    
    print(f"\nTotal Baseline Chi2: {chi2:.4f}")
    return chi2

if __name__ == "__main__":
    calculate_baseline_chi2()
