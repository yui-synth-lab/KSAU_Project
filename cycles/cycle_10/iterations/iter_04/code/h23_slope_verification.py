import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

# SSoT Loader Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))
from ksau_ssot import SSOT

def main():
    ssot = SSOT()
    consts = ssot.constants()
    params = ssot.parameters()
    topologies = ssot.topology_assignments()

    pi = consts["mathematical_constants"]["pi"]
    kappa = consts["mathematical_constants"]["kappa"]
    
    # Integers for slope (eta)
    etas = {
        "quarks": 10.0,
        "leptons": 20.0,
        "bosons": 3.0
    }
    
    # Sector Intercepts (Official v6.0)
    bq = -(7 + 7 * kappa)
    cl = np.log(0.511)
    cb = 5.5414
    
    sector_intercepts = {
        "quarks": bq,
        "leptons": cl,
        "bosons": cb
    }
    
    particles = []
    for sector, eta in etas.items():
        for name, data in params.get(sector, {}).items():
            if name in topologies:
                v = topologies[name]["volume"]
                obs = data["observed_mass_mev"]
                ln_m_obs = np.log(obs)
                
                # Base Formula: ln(m) = eta * kappa * V + C
                log_pred = eta * kappa * v + sector_intercepts[sector]
                
                # Quark twist correction (from ksau_simulator.py v6.7)
                if sector == "quarks":
                    gen = topologies[name].get("generation", 1)
                    comp = topologies[name].get("components", 1)
                    twist = (2 - gen) * ((-1) ** comp)
                    log_pred += kappa * twist
                
                # Lepton twist correction (from ksau_simulator.py v6.7)
                if sector == "leptons" and name == "Tau":
                    log_pred += -1/6
                
                pred = np.exp(log_pred)
                err_pct = (pred - obs) / obs * 100
                
                particles.append({
                    "name": name,
                    "sector": sector,
                    "v": v,
                    "obs": obs,
                    "pred": pred,
                    "err_pct": err_pct,
                    "ln_err": log_pred - ln_m_obs
                })
                
    df = pd.DataFrame(particles)
    mae_pct = df["err_pct"].abs().mean()
    print(f"Grand Unified MAE (%): {mae_pct:.2f}%")
    print(df[["name", "obs", "pred", "err_pct"]])
    
    status = "SUCCESS" if mae_pct < 0.1 else "FAILURE"
    print(f"Status: {status}")

    results = {
        "iteration": 4,
        "hypothesis_id": "H23",
        "task_name": "Verification of Slope-Discretized Model",
        "computed_values": {
            "mae_pct": float(mae_pct),
            "status": status
        },
        "particle_details": df.to_dict(orient="records")
    }
    
    with open(current_file.parents[1] / "results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
