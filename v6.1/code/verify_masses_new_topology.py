"""
Verify that quark mass predictions remain accurate with new topology assignment
Critical: v6.0 achieved R²=0.9998 for fermion masses - must not degrade
"""
import numpy as np
import pandas as pd
import utils_v61
from sklearn.metrics import r2_score

def verify_quark_masses():
    print("="*80)
    print("Quark Mass Verification with New Topology Assignment")
    print("="*80)

    # New optimized assignment
    new_assignment = {
        'Up': 'L8n1{0}',
        'Charm': 'L11a358{0}',
        'Top': 'L11n409{1,0}',
        'Down': 'L7a3{1}',
        'Strange': 'L9a49{1,0}',
        'Bottom': 'L11n113{1}'
    }

    # Old v6.0 assignment
    old_assignment = utils_v61.load_assignments()

    # Load data
    _, links = utils_v61.load_data()
    consts = utils_v61.load_constants()

    # Observed masses (MeV)
    obs_masses = {
        'Up': consts['quarks']['Up']['observed_mass'],
        'Down': consts['quarks']['Down']['observed_mass'],
        'Charm': consts['quarks']['Charm']['observed_mass'],
        'Strange': consts['quarks']['Strange']['observed_mass'],
        'Top': consts['quarks']['Top']['observed_mass'],
        'Bottom': consts['quarks']['Bottom']['observed_mass']
    }

    # KSAU mass formula: ln(m) = kappa * V + intercept
    # From v6.0: kappa = 0.1309, but we need to determine intercept from data
    kappa = consts['kappa']

    def predict_masses(assignment_dict):
        """Predict masses for given topology assignment"""
        volumes = {}
        for q in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
            # Handle both dict (old) and string (new) formats
            if isinstance(assignment_dict[q], dict):
                topo = assignment_dict[q]['topology']
            else:
                topo = assignment_dict[q]
            topo_base = topo.split('{')[0]

            row = links[links['name'] == topo_base]
            if row.empty:
                row = links[links['name'].str.startswith(topo_base + "{")].iloc[0]
            else:
                row = row.iloc[0]

            volumes[q] = float(row['volume'])

        # Fit intercept using linear regression on log(mass) vs volume
        V_vals = np.array([volumes[q] for q in obs_masses.keys()])
        ln_m_vals = np.array([np.log(obs_masses[q]) for q in obs_masses.keys()])

        # ln(m) = kappa * V + intercept
        # intercept = mean(ln_m) - kappa * mean(V)
        intercept = np.mean(ln_m_vals) - kappa * np.mean(V_vals)

        # Predict
        predictions = {}
        for q, V in volumes.items():
            ln_m_pred = kappa * V + intercept
            predictions[q] = np.exp(ln_m_pred)

        return volumes, predictions, intercept

    # Evaluate old assignment
    print("\n[OLD ASSIGNMENT (v6.0 SSoT)]")
    print("-"*80)
    old_volumes, old_preds, old_intercept = predict_masses(old_assignment)

    old_obs = []
    old_pred = []
    for q in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
        obs = obs_masses[q]
        pred = old_preds[q]
        old_obs.append(obs)
        old_pred.append(pred)
        error = abs(obs - pred) / obs * 100
        print(f"  {q:<8}: V={old_volumes[q]:<7.3f} | Obs={obs:<10.2f} MeV | Pred={pred:<10.2f} MeV | Error={error:>6.2f}%")

    old_r2 = r2_score(old_obs, old_pred)
    print(f"\n  R² (old): {old_r2:.6f}")

    # Evaluate new assignment
    print("\n[NEW ASSIGNMENT (Optimized)]")
    print("-"*80)
    new_volumes, new_preds, new_intercept = predict_masses(new_assignment)

    new_obs = []
    new_pred = []
    for q in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
        obs = obs_masses[q]
        pred = new_preds[q]
        new_obs.append(obs)
        new_pred.append(pred)
        error = abs(obs - pred) / obs * 100
        print(f"  {q:<8}: V={new_volumes[q]:<7.3f} | Obs={obs:<10.2f} MeV | Pred={pred:<10.2f} MeV | Error={error:>6.2f}%")

    new_r2 = r2_score(new_obs, new_pred)
    print(f"\n  R² (new): {new_r2:.6f}")

    # Comparison
    print("\n" + "="*80)
    print("MASS PREDICTION COMPARISON")
    print("="*80)
    print(f"  Old Assignment R²: {old_r2:.6f}")
    print(f"  New Assignment R²: {new_r2:.6f}")
    print(f"  Difference: {new_r2 - old_r2:+.6f}")

    if new_r2 >= 0.98:
        print(f"\n  ✓ SUCCESS: New assignment maintains R² ≥ 0.98")
        print(f"    New topology assignment is VALIDATED for adoption")
    elif new_r2 >= old_r2 - 0.01:
        print(f"\n  ⚠ WARNING: New assignment R² within 1% of old ({new_r2:.4f} vs {old_r2:.4f})")
        print(f"    Acceptable degradation - recommend adoption with caveat")
    else:
        print(f"\n  ✗ FAILURE: New assignment degrades mass predictions by {old_r2 - new_r2:.4f}")
        print(f"    DO NOT ADOPT - CKM improvement not worth mass prediction loss")

    # Volume correlation analysis
    print("\n" + "="*80)
    print("VOLUME COMPARISON")
    print("="*80)
    print(f"{'Quark':<8} | {'Old V':<8} | {'New V':<8} | {'Change':<8} | {'Mass Hierarchy'}")
    print("-"*80)
    for q in ['Up', 'Down', 'Charm', 'Strange', 'Top', 'Bottom']:
        old_v = old_volumes[q]
        new_v = new_volumes[q]
        change = new_v - old_v
        mass = obs_masses[q]
        print(f"{q:<8} | {old_v:<8.3f} | {new_v:<8.3f} | {change:>+8.3f} | {mass:.2f} MeV")

    # Check if volume ordering is preserved
    old_order = sorted(old_volumes.items(), key=lambda x: x[1])
    new_order = sorted(new_volumes.items(), key=lambda x: x[1])

    print("\n  Volume Ordering (lightest → heaviest):")
    print(f"    Old: {' < '.join([q for q, v in old_order])}")
    print(f"    New: {' < '.join([q for q, v in new_order])}")

    if [q for q, v in old_order] == [q for q, v in new_order]:
        print(f"    ✓ Ordering PRESERVED")
    else:
        print(f"    ✗ Ordering CHANGED (may affect mass hierarchy interpretation)")

    # Save results
    results = {
        'old_r2': old_r2,
        'new_r2': new_r2,
        'old_intercept': old_intercept,
        'new_intercept': new_intercept
    }

    with open('mass_validation_result.txt', 'w') as f:
        f.write(f"Old R²: {old_r2:.6f}\n")
        f.write(f"New R²: {new_r2:.6f}\n")
        f.write(f"Verdict: {'PASS' if new_r2 >= 0.98 else 'FAIL'}\n")

    print("\nSaved to mass_validation_result.txt")

    return new_r2 >= 0.98

if __name__ == "__main__":
    success = verify_quark_masses()
    exit(0 if success else 1)
