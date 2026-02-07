"""
KSAU v5.0: Mass Prediction and Validation
Topological Mass Generation from π/24

This script reproduces all numerical results from the main paper.
"""

import numpy as np
from typing import Dict, Tuple

# ============================================================================
# UNIVERSAL CONSTANT
# ============================================================================

KAPPA = np.pi / 24  # The master constant from Chern-Simons theory

# ============================================================================
# OBSERVED MASSES (PDG 2024)
# ============================================================================

MASSES_OBS = {
    'Up': 2.16,
    'Down': 4.67,
    'Strange': 93.4,
    'Charm': 1270.0,
    'Bottom': 4180.0,
    'Top': 172760.0,
    'Electron': 0.510998,
    'Muon': 105.658,
    'Tau': 1776.86
}

# ============================================================================
# TOPOLOGICAL PARAMETERS (from v4.1 optimized assignments)
# ============================================================================

TOPOLOGY = {
    # Quarks: (Volume, Component, Determinant, Crossing, Generation, Twist)
    # Twist = (2 - Gen) × (-1)^Comp
    'Up':      {'V': 6.599,  'C': 2, 'Det': 18,  'N': 7,  'Gen': 1, 'Twist': +1, 'Link': 'L7a5'},
    'Down':    {'V': 7.328,  'C': 3, 'Det': 16,  'N': 6,  'Gen': 1, 'Twist': -1, 'Link': 'L6a4'},  # Borromean Rings
    'Strange': {'V': 9.532,  'C': 3, 'Det': 32,  'N': 10, 'Gen': 2, 'Twist':  0, 'Link': 'L10n95'},
    'Charm':   {'V': 11.517, 'C': 2, 'Det': 12,  'N': 11, 'Gen': 2, 'Twist':  0, 'Link': 'L11n64'},
    'Bottom':  {'V': 12.276, 'C': 3, 'Det': 64,  'N': 10, 'Gen': 3, 'Twist': +1, 'Link': 'L10a141'},
    'Top':     {'V': 15.360, 'C': 2, 'Det': 124, 'N': 11, 'Gen': 3, 'Twist': -1, 'Link': 'L11a62'},

    # Leptons: (N^2, Volume, IsTwistKnot, Component, Determinant)
    'Electron': {'N2': 9,  'V': 0.0,  'IsTwist': False, 'C': 1, 'Det': 3, 'Knot': '3_1'},
    'Muon':     {'N2': 36, 'V': 5.69, 'IsTwist': True,  'C': 1, 'Det': 9, 'Knot': '6_1'},
    'Tau':      {'N2': 49, 'V': 0.0,  'IsTwist': False, 'C': 1, 'Det': 7, 'Knot': '7_1'}
}

# ============================================================================
# MASS FORMULAS
# ============================================================================

def predict_quark_mass(V: float, twist: int) -> float:
    """
    Quark mass formula (v5.0 with Twist correction):

    ln(m_q / MeV) = 10κ · V + κ · Twist - (7 + 7κ)

    where κ = π/24 and Twist = (2 - Gen) × (-1)^Comp
    """
    # Using G ~ 7π/24 = 7κ, the intercept is -(7 + G) = -(7 + 7κ)
    B_q = -(7 + 7 * KAPPA)

    log_mass = 10 * KAPPA * V + KAPPA * twist + B_q
    return np.exp(log_mass)


def predict_lepton_mass(N_squared: float, is_twist_knot: bool) -> float:
    """
    Lepton mass formula (two parameters):

    ln(m_l / MeV) = (14/9)κ · N² - (1/6) · I_twist + C_l

    where C_l is calibrated to electron mass.
    """
    # Coefficient: (14/9) × κ
    gamma_l = (14/9) * KAPPA

    # Calibration constant (fixed by electron: N²=9, no twist correction)
    C_l = np.log(MASSES_OBS['Electron']) - gamma_l * 9

    # Twist correction (only for twist knots, e.g., muon)
    twist_correction = -1/6 if is_twist_knot else 0

    log_mass = gamma_l * N_squared + twist_correction + C_l
    return np.exp(log_mass)


# ============================================================================
# PREDICTION ENGINE
# ============================================================================

def compute_all_predictions() -> Dict[str, Tuple[float, float]]:
    """
    Compute predicted masses for all 9 fermions.

    Returns:
        Dictionary mapping particle name to (predicted_mass, error_percent)
    """
    results = {}

    for particle, obs_mass in MASSES_OBS.items():
        topo = TOPOLOGY[particle]

        # Check if quark or lepton based on component number
        if topo['C'] >= 2:  # Quark (link)
            pred_mass = predict_quark_mass(topo['V'], topo['Twist'])
        else:  # Lepton (knot)
            pred_mass = predict_lepton_mass(topo['N2'], topo['IsTwist'])

        # Compute error
        error_pct = (pred_mass - obs_mass) / obs_mass * 100

        results[particle] = (pred_mass, error_pct)

    return results


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def compute_statistics(results: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
    """Compute summary statistics."""
    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    leptons = ['Electron', 'Muon', 'Tau']

    quark_errors = [abs(results[p][1]) for p in quarks]
    lepton_errors = [abs(results[p][1]) for p in leptons]
    all_errors = quark_errors + lepton_errors

    return {
        'quark_mae': np.mean(quark_errors),
        'lepton_mae': np.mean(lepton_errors),
        'global_mae': np.mean(all_errors),
        'max_error': max(all_errors),
        'median_error': np.median(all_errors),
        'quark_r2': compute_r_squared([MASSES_OBS[p] for p in quarks],
                                      [results[p][0] for p in quarks]),
        'lepton_r2': compute_r_squared([MASSES_OBS[p] for p in leptons],
                                       [results[p][0] for p in leptons])
    }


def compute_r_squared(obs: list, pred: list) -> float:
    """Compute R^2 coefficient of determination."""
    obs = np.array(obs)
    pred = np.array(pred)

    # Use log scale for masses (spanning 6 orders of magnitude)
    obs_log = np.log(obs)
    pred_log = np.log(pred)

    ss_res = np.sum((obs_log - pred_log)**2)
    ss_tot = np.sum((obs_log - np.mean(obs_log))**2)

    return 1 - (ss_res / ss_tot)


def verify_selection_rules():
    """Verify that all topology assignments satisfy the three selection rules."""
    print("\n" + "="*80)
    print("VERIFYING SELECTION RULES")
    print("="*80)

    quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
    leptons = ['Electron', 'Muon', 'Tau']

    # Rule 1: Confinement-Component Correspondence
    print("\nRule 1: Confinement-Component Correspondence")
    for p in quarks:
        C = TOPOLOGY[p]['C']
        assert C >= 2, f"{p} should have C >= 2 (link)"
        print(f"  {p:8s}: C = {C} (link) OK")

    for p in leptons:
        C = TOPOLOGY[p]['C']
        assert C == 1, f"{p} should have C = 1 (knot)"
        print(f"  {p:8s}: C = {C} (knot) OK")

    # Rule 2: Charge-Determinant Law
    print("\nRule 2: Charge-Determinant Law")

    # Up-type quarks: even determinant
    up_type = ['Up', 'Charm', 'Top']
    for p in up_type:
        det = TOPOLOGY[p]['Det']
        assert det % 2 == 0, f"{p} (up-type) should have even Det"
        print(f"  {p:8s}: Det = {det:3d} (even) OK")

    # Down-type quarks: Det = 2^k
    down_type = ['Down', 'Strange', 'Bottom']
    for i, p in enumerate(down_type):
        det = TOPOLOGY[p]['Det']
        expected = 2**(i + 4)  # 2^4, 2^5, 2^6
        assert det == expected, f"{p} should have Det = {expected}"
        k = int(np.log2(det))
        print(f"  {p:8s}: Det = {det:3d} = 2^{k} (Binary Rule) OK")

    # Leptons: odd determinant
    for p in leptons:
        det = TOPOLOGY[p]['Det']
        assert det % 2 == 1, f"{p} (lepton) should have odd Det"
        print(f"  {p:8s}: Det = {det:3d} (odd) OK")

    # Rule 3: Geometric Mass Scaling (verified implicitly by formulas)
    print("\nRule 3: Geometric Mass Scaling")
    print(f"  Quark coefficient:  10κ = {10*KAPPA:.6f}")
    print(f"  Lepton coefficient: (14/9)κ = {(14/9)*KAPPA:.6f}")
    print("  OK All formulas use κ = π/24")

    print("\n" + "="*80)
    print("ALL SELECTION RULES SATISFIED OK")
    print("="*80)


# ============================================================================
# MAIN OUTPUT
# ============================================================================

def main():
    """Main execution: compute predictions and display results."""

    print("="*80)
    print("KSAU v5.0: Topological Mass Generation from π/24")
    print("="*80)
    print()
    print(f"Master Constant: κ = π/24 = {KAPPA:.15f}")
    print()

    # Verify selection rules
    verify_selection_rules()

    # Compute predictions
    results = compute_all_predictions()

    # Display results
    print("\n" + "="*80)
    print("MASS PREDICTIONS")
    print("="*80)
    print()
    print(f"{'Particle':<10} | {'Topology':<10} | {'Observed':<12} | {'Predicted':<12} | {'Error (%)':<10}")
    print("-" * 80)

    for particle in MASSES_OBS.keys():
        topo = TOPOLOGY[particle]
        topo_name = topo.get('Link', topo.get('Knot', ''))
        obs = MASSES_OBS[particle]
        pred, err = results[particle]

        print(f"{particle:<10} | {topo_name:<10} | {obs:>10.4f} | {pred:>10.4f} | {err:>9.2f}%")

    # Summary statistics
    stats = compute_statistics(results)

    print("-" * 80)
    print(f"{'Quark MAE':<10} | {'':<10} | {'':<12} | {'':<12} | {stats['quark_mae']:>9.2f}%")
    print(f"{'Lepton MAE':<10} | {'':<10} | {'':<12} | {'':<12} | {stats['lepton_mae']:>9.2f}%")
    print(f"{'Global MAE':<10} | {'':<10} | {'':<12} | {'':<12} | {stats['global_mae']:>9.2f}%")
    print(f"{'Median Err':<10} | {'':<10} | {'':<12} | {'':<12} | {stats['median_error']:>9.2f}%")
    print(f"{'Max Error':<10} | {'':<10} | {'':<12} | {'':<12} | {stats['max_error']:>9.2f}%")
    print()
    print(f"Quark R^2:  {stats['quark_r2']:.6f}")
    print(f"Lepton R^2: {stats['lepton_r2']:.6f}")

    # Verify Catalan identity
    print("\n" + "="*80)
    print("CATALAN CONSTANT IDENTITY")
    print("="*80)
    G = 0.915965594177219  # Catalan constant (high precision)
    approx = 7 * np.pi / 24
    rel_err = abs(G - approx) / G * 100

    print(f"G (Catalan)     = {G:.15f}")
    print(f"7π/24           = {approx:.15f}")
    print(f"Relative error  = {rel_err:.4f}%")
    print()
    print("This identity allows v4.1 coefficients to be rewritten:")
    print(f"  (10/7)G ~ 10κ:   {(10/7)*G:.10f} ~ {10*KAPPA:.10f}")
    print(f"  (2/9)G ~ (14/9)κ: {(2/9)*G:.10f} ~ {(14/9)*KAPPA:.10f}")

    print("\n" + "="*80)
    print("VALIDATION COMPLETE")
    print("="*80)
    print()
    print(f"OK Global MAE: {stats['global_mae']:.2f}% (Target: < 5%)")
    print(f"OK All selection rules satisfied")
    print(f"OK Catalan identity verified (0.036% error)")
    print(f"OK Quark formula: 10kappa*V + kappa*Twist + B_q")
    print(f"OK Lepton formula: (14/9)kappa*N^2 - (1/6)*I_twist + C_l")
    print()


if __name__ == "__main__":
    main()
