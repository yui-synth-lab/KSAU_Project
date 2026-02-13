"""
Monte Carlo Null Hypothesis Test for KSAU v6.0

This script quantifies the probability that the observed mass-volume correlation
could arise by chance from random topology assignments.

Methodology:
1. Load the full KnotInfo/LinkInfo database
2. Randomly assign topologies to particles (respecting component constraints)
3. Fit the mass-volume relationship
4. Repeat 10,000 times and measure R² distribution
5. Compare KSAU's R² to null distribution → compute p-value

Expected outcome: If p < 0.001, the correlation is statistically significant.
"""

import numpy as np
import pandas as pd
import ksau_config
from pathlib import Path
import json
from tqdm import tqdm

# ============================================================================
# SETUP
# ============================================================================

def load_databases():
    """Load KnotInfo and LinkInfo databases."""
    df_l = pd.read_csv(ksau_config.load_linkinfo_path(), sep='|', skiprows=[1])
    df_k = pd.read_csv(ksau_config.load_knotinfo_path(), sep='|', skiprows=[1], low_memory=False)

    # Clean link data
    for c in ['volume', 'crossing_number', 'components', 'determinant']:
        df_l[c] = pd.to_numeric(df_l[c], errors='coerce').fillna(0)

    # Clean knot data
    for c in ['volume', 'crossing_number', 'determinant']:
        df_k[c] = pd.to_numeric(df_k[c], errors='coerce').fillna(0)
    df_k['components'] = 1

    # Filter to hyperbolic only (V > 0)
    df_k = df_k[df_k['volume'] > 0].copy()
    df_l = df_l[df_l['volume'] > 0].copy()

    return df_k, df_l

def calculate_r2(observed_masses, predicted_masses):
    """Calculate R² on log scale."""
    log_obs = np.log(observed_masses)
    log_pred = np.log(predicted_masses)
    ss_res = np.sum((log_obs - log_pred)**2)
    ss_tot = np.sum((log_obs - np.mean(log_obs))**2)
    return 1 - (ss_res / ss_tot)

def calculate_mae(observed_masses, predicted_masses):
    """Calculate Mean Absolute Error in percent."""
    return np.mean(np.abs((predicted_masses - observed_masses) / observed_masses * 100))

# ============================================================================
# NULL HYPOTHESIS SIMULATION
# ============================================================================

def random_topology_assignment(df_k, df_l, phys, kappa):
    """
    Randomly assign topologies to particles respecting component constraints.

    Returns:
        dict: {particle_name: {'volume': V, 'observed_mass': m, 'predicted_mass': m_pred}}
    """
    results = {}

    # Leptons: Random knots
    for l_name in ['Electron', 'Muon', 'Tau']:
        knot = df_k.sample(n=1).iloc[0]
        obs_mass = phys['leptons'][l_name]['observed_mass']
        results[l_name] = {
            'volume': knot['volume'],
            'observed_mass': obs_mass,
            'type': 'lepton'
        }

    # Quarks: Random links with component constraint
    for q_name, q_meta in phys['quarks'].items():
        comp = 2 if q_name in ['Up', 'Charm', 'Top'] else 3
        candidates = df_l[df_l['components'] == comp]
        if len(candidates) == 0:
            continue
        link = candidates.sample(n=1).iloc[0]
        obs_mass = q_meta['observed_mass']
        results[q_name] = {
            'volume': link['volume'],
            'observed_mass': obs_mass,
            'type': 'quark',
            'generation': q_meta['generation'],
            'components': comp
        }

    return results

def fit_and_evaluate(assignment, kappa):
    """
    Fit the KSAU mass formula to a random assignment and return metrics.

    Strategy: Use the same functional form as KSAU (10κV for quarks, 20κV for leptons)
              but fit intercepts to the random data.
    """
    # Separate quarks and leptons
    quarks = {k: v for k, v in assignment.items() if v['type'] == 'quark'}
    leptons = {k: v for k, v in assignment.items() if v['type'] == 'lepton'}

    if len(quarks) < 2 or len(leptons) < 2:
        return None  # Not enough data

    # Fit quark intercept (slope fixed at 10κ as in KSAU)
    q_volumes = np.array([q['volume'] for q in quarks.values()])
    q_masses = np.array([q['observed_mass'] for q in quarks.values()])

    # ln(m) = 10κV + Bq → Bq = mean(ln(m) - 10κV)
    slope_q = 10 * kappa
    bq = np.mean(np.log(q_masses) - slope_q * q_volumes)

    # Fit lepton intercept (slope fixed at 20κ)
    l_volumes = np.array([l['volume'] for l in leptons.values()])
    l_masses = np.array([l['observed_mass'] for l in leptons.values()])

    slope_l = 20 * kappa
    cl = np.mean(np.log(l_masses) - slope_l * l_volumes)

    # Predict masses
    q_pred = np.exp(slope_q * q_volumes + bq)
    l_pred = np.exp(slope_l * l_volumes + cl)

    # Calculate metrics
    all_obs = np.concatenate([q_masses, l_masses])
    all_pred = np.concatenate([q_pred, l_pred])

    r2 = calculate_r2(all_obs, all_pred)
    mae = calculate_mae(all_obs, all_pred)

    return {'r2': r2, 'mae': mae}

# ============================================================================
# MAIN SIMULATION
# ============================================================================

def run_monte_carlo(n_iterations=10000, seed=42):
    """
    Run Monte Carlo null hypothesis test.

    Returns:
        dict: {
            'null_r2_distribution': [...],
            'null_mae_distribution': [...],
            'ksau_r2': float,
            'ksau_mae': float,
            'p_value_r2': float,
            'p_value_mae': float
        }
    """
    print("="*80)
    print("KSAU v6.0: Monte Carlo Null Hypothesis Test")
    print("="*80)

    np.random.seed(seed)

    # Load databases
    print("Loading KnotInfo/LinkInfo databases...")
    df_k, df_l = load_databases()
    print(f"  Knots (V>0): {len(df_k)}")
    print(f"  Links (V>0): {len(df_l)}")

    # Load KSAU's actual performance
    phys = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    kappa = ksau_config.KAPPA

    # Calculate KSAU's R² and MAE
    q_obs, q_pred = [], []
    l_obs, l_pred = [], []
    coeffs = ksau_config.get_kappa_coeffs()

    for name, data in topo.items():
        if 'charge_type' not in data or data['charge_type'] == 'boson':
            continue
        obs = data['observed_mass']
        vol = data['volume']

        if data['charge_type'] == 'lepton':
            log_pred = 20 * kappa * vol + coeffs['lepton_intercept']
            l_obs.append(obs)
            l_pred.append(np.exp(log_pred))
        else:  # quark
            twist = (2 - data['generation']) * ((-1) ** data['components'])
            log_pred = 10 * kappa * vol + kappa * twist + coeffs['quark_intercept']
            q_obs.append(obs)
            q_pred.append(np.exp(log_pred))

    all_obs = np.array(q_obs + l_obs)
    all_pred = np.array(q_pred + l_pred)

    ksau_r2 = calculate_r2(all_obs, all_pred)
    ksau_mae = calculate_mae(all_obs, all_pred)

    print(f"\nKSAU v6.0 Performance (Actual):")
    print(f"  R² (log scale): {ksau_r2:.6f}")
    print(f"  MAE: {ksau_mae:.2f}%")

    # Run Monte Carlo
    print(f"\nRunning {n_iterations} random topology assignments...")
    null_r2 = []
    null_mae = []

    for i in tqdm(range(n_iterations), desc="Monte Carlo"):
        assignment = random_topology_assignment(df_k, df_l, phys, kappa)
        metrics = fit_and_evaluate(assignment, kappa)

        if metrics is not None:
            null_r2.append(metrics['r2'])
            null_mae.append(metrics['mae'])

    null_r2 = np.array(null_r2)
    null_mae = np.array(null_mae)

    # Calculate p-values
    p_r2 = np.sum(null_r2 >= ksau_r2) / len(null_r2)
    p_mae = np.sum(null_mae <= ksau_mae) / len(null_mae)

    # Summary statistics
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Null Hypothesis R² Distribution:")
    print(f"  Mean: {np.mean(null_r2):.6f}")
    print(f"  Std:  {np.std(null_r2):.6f}")
    print(f"  95th percentile: {np.percentile(null_r2, 95):.6f}")
    print(f"  99th percentile: {np.percentile(null_r2, 99):.6f}")
    print(f"\nKSAU R²: {ksau_r2:.6f}")
    print(f"p-value: {p_r2:.4f} ({p_r2*100:.2f}%)")
    print(f"\nInterpretation:")
    if p_r2 < 0.001:
        print("  ✓ HIGHLY SIGNIFICANT: KSAU correlation is not due to chance")
    elif p_r2 < 0.05:
        print("  ✓ SIGNIFICANT: KSAU correlation is unlikely due to chance")
    else:
        print("  ✗ NOT SIGNIFICANT: Random assignments can achieve similar R²")

    print("\n" + "-"*80)
    print(f"Null Hypothesis MAE Distribution:")
    print(f"  Mean: {np.mean(null_mae):.2f}%")
    print(f"  Std:  {np.std(null_mae):.2f}%")
    print(f"  5th percentile: {np.percentile(null_mae, 5):.2f}%")
    print(f"  1st percentile: {np.percentile(null_mae, 1):.2f}%")
    print(f"\nKSAU MAE: {ksau_mae:.2f}%")
    print(f"p-value: {p_mae:.4f} ({p_mae*100:.2f}%)")

    # Save results
    output_dir = Path(__file__).parent.parent / 'data'
    output_path = output_dir / 'monte_carlo_null_test.json'

    results = {
        'n_iterations': n_iterations,
        'seed': seed,
        'ksau_r2': float(ksau_r2),
        'ksau_mae': float(ksau_mae),
        'null_r2_mean': float(np.mean(null_r2)),
        'null_r2_std': float(np.std(null_r2)),
        'null_r2_95th': float(np.percentile(null_r2, 95)),
        'null_r2_99th': float(np.percentile(null_r2, 99)),
        'null_mae_mean': float(np.mean(null_mae)),
        'null_mae_std': float(np.std(null_mae)),
        'null_mae_5th': float(np.percentile(null_mae, 5)),
        'null_mae_1st': float(np.percentile(null_mae, 1)),
        'p_value_r2': float(p_r2),
        'p_value_mae': float(p_mae),
        'verdict': 'SIGNIFICANT' if p_r2 < 0.001 else ('MARGINAL' if p_r2 < 0.05 else 'NOT_SIGNIFICANT')
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    results = run_monte_carlo(n_iterations=10000)
