#!/usr/bin/env python3
"""
Reidemeister Torsion Computation for KSAU Knots

Computes Reidemeister torsion from Alexander polynomial and compares
with hyperbolic volume to verify the Ray-Singer formula:

    ln|T(M)| ~ (1/2π) * Vol(M)

For KSAU, we investigate whether:
    ln(m) ~ N * κ * Vol(M)
can be connected to torsion.

Author: Claude Opus 4.6
Date: 2026-02-14
Reference: v7.1/docs/ray_singer_torsion_notes.md
"""

import numpy as np
from pathlib import Path
import json

try:
    import snappy
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    print("ERROR: SnapPy not available. Please install: pip install snappy")
    import sys
    sys.exit(1)

def load_constants():
    """Load physical constants from SSoT"""
    constants_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(constants_path, 'r') as f:
        return json.load(f)

def compute_reidemeister_torsion(knot_name):
    """
    Compute Reidemeister torsion from Alexander polynomial

    For a knot complement M, the Reidemeister torsion is related to
    the Alexander polynomial Δ_K(t) by:

        τ(M) = |Δ_K(-1)|

    (up to normalization factors)
    """
    M = snappy.Manifold(knot_name)

    # Get Alexander polynomial
    alex_poly = M.alexander_polynomial()

    # Evaluate at t = -1
    # Note: SnapPy's alexander_polynomial returns a Laurent polynomial
    # We need to evaluate it carefully
    try:
        tau = abs(alex_poly(-1))
    except:
        # If direct evaluation fails, try converting to sympy
        import sympy as sp
        t = sp.Symbol('t')
        alex_sympy = sp.sympify(str(alex_poly))
        tau = abs(complex(alex_sympy.subs(t, -1)))

    return tau

def main():
    print("="*70)
    print("Reidemeister Torsion and Ray-Singer Formula Verification")
    print("="*70)
    print()

    # Load physical constants
    phys = load_constants()

    # Knots to analyze
    knots_data = [
        {
            'name': '4_1',
            'description': 'Figure-eight (Muon)',
            'particle': 'Muon',
            'mass': phys['leptons']['Muon']['observed_mass'],
        },
        {
            'name': '6_1',
            'description': 'Stevedore (Tau, v6.0)',
            'particle': 'Tau',
            'mass': phys['leptons']['Tau']['observed_mass'],
        },
        {
            'name': '5_2',
            'description': 'Three-twist knot',
            'particle': None,
            'mass': None,
        },
    ]

    print("Computing torsion and volume for knots...")
    print()

    results = []

    for knot in knots_data:
        name = knot['name']
        print(f"Knot: {name} ({knot['description']})")
        print("-" * 70)

        try:
            # Load manifold
            M = snappy.Manifold(name)

            # Get hyperbolic volume
            vol = float(M.volume())

            # Get Alexander polynomial
            alex_poly = M.alexander_polynomial()
            print(f"  Alexander polynomial: {alex_poly}")

            # Compute Reidemeister torsion
            tau = compute_reidemeister_torsion(name)

            # Compute ln(tau) / Vol ratio
            if tau > 0:
                ln_tau = np.log(tau)
                ratio = ln_tau / vol
            else:
                ln_tau = np.nan
                ratio = np.nan

            # Ray-Singer prediction: ln|T| ~ Vol / (2π)
            # => ln|T| / Vol ~ 1 / (2π)
            expected_ratio = 1.0 / (2 * np.pi)

            # KSAU coefficient: N * κ
            if knot['particle'] == 'Muon':
                N = 20  # Lepton sector
                kappa = np.pi / 24
                ksau_coeff = N * kappa
                ln_m = np.log(knot['mass'])
                ksau_ratio = ln_m / vol
            elif knot['particle'] == 'Tau':
                N = 20
                kappa = np.pi / 24
                ksau_coeff = N * kappa
                ln_m = np.log(knot['mass'])
                ksau_ratio = ln_m / vol
            else:
                ksau_coeff = None
                ksau_ratio = None

            # Store results
            result = {
                'name': name,
                'description': knot['description'],
                'volume': vol,
                'alexander': str(alex_poly),
                'tau': tau,
                'ln_tau': ln_tau,
                'ratio_tau_vol': ratio,
                'expected_ratio': expected_ratio,
                'ksau_coeff': ksau_coeff,
                'ksau_ratio': ksau_ratio,
            }
            results.append(result)

            # Print results
            print(f"  Volume: {vol:.10f}")
            print(f"  Reidemeister torsion τ: {tau:.6f}")
            print(f"  ln(τ): {ln_tau:.6f}")
            print(f"  ln(τ) / Vol: {ratio:.6f}")
            print(f"  Expected 1/(2π): {expected_ratio:.6f}")
            print(f"  Discrepancy: {abs(ratio - expected_ratio):.6f}")

            if ksau_ratio is not None:
                print()
                print(f"  KSAU comparison ({knot['particle']}):")
                print(f"    Mass: {knot['mass']:.6f} MeV")
                print(f"    ln(m): {ln_m:.6f}")
                print(f"    ln(m) / Vol: {ksau_ratio:.6f}")
                print(f"    KSAU coeff (N*κ): {ksau_coeff:.6f}")
                print(f"    Ratio: ln(m)/Vol vs N*κ: {ksau_ratio / ksau_coeff:.6f}")

        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    # Summary
    print("="*70)
    print("SUMMARY: Torsion vs Volume")
    print("="*70)
    print()

    print(f"{'Knot':<10} | {'Vol':<12} | {'τ':<12} | {'ln(τ)/Vol':<12} | {'1/(2π)':<12} | {'Error':<12}")
    print("-" * 85)

    for r in results:
        name = r['name']
        vol = r['volume']
        tau = r['tau']
        ratio = r['ratio_tau_vol']
        expected = r['expected_ratio']
        error = abs(ratio - expected) if not np.isnan(ratio) else np.nan

        print(f"{name:<10} | {vol:<12.6f} | {tau:<12.6f} | {ratio:<12.6f} | {expected:<12.6f} | {error:<12.6f}")

    print()

    # Analysis
    print("="*70)
    print("ANALYSIS")
    print("="*70)
    print()

    print("Ray-Singer Torsion Formula:")
    print("  ln|T(M)| ~ (1/2π) * Vol(M)")
    print("  => ln|T| / Vol ~ 0.159")
    print()

    print("KSAU Master Formula:")
    print("  ln(m) = N * κ * Vol + C")
    print("  For leptons: N = 20, κ = π/24")
    print("  => ln(m) / Vol ~ N*κ ~ 2.618 (after subtracting C/Vol)")
    print()

    print("Discrepancy Factor:")
    print("  (N*κ) / (1/2π) = 2.618 / 0.159 = 16.4")
    print()

    print("Possible Explanations:")
    print("  1. Representation-dependent scaling: j^2 factor?")
    print("  2. N=20 is not a representation dimension")
    print("  3. κ=π/24 has different origin (zeta regularization, modular forms)")
    print("  4. KSAU measures different invariant than Ray-Singer torsion")
    print()

    # Check if torsion matches predictions
    print("="*70)
    print("VERDICT")
    print("="*70)
    print()

    # Check 4_1 specifically
    r_41 = [r for r in results if r['name'] == '4_1'][0]
    ratio_41 = r_41['ratio_tau_vol']
    expected = r_41['expected_ratio']

    if abs(ratio_41 - expected) / expected < 0.1:
        print("Ray-Singer formula is VERIFIED for 4_1 knot (<10% error).")
        print("The ln(tau) / Vol ratio matches 1/(2pi).")
    elif abs(ratio_41 - expected) / expected < 0.5:
        print("Ray-Singer formula is APPROXIMATELY verified for 4_1 knot.")
        print(f"Deviation: {abs(ratio_41 - expected) / expected * 100:.1f}%")
    else:
        print("Ray-Singer formula does NOT match for 4_1 knot.")
        print(f"Deviation: {abs(ratio_41 - expected) / expected * 100:.1f}%")
        print()
        print("Possible reasons:")
        print("  - Normalization convention differs")
        print("  - Reidemeister torsion != Ray-Singer torsion (need analytic formula)")
        print("  - Alexander polynomial evaluation at t=-1 is not the full story")

    print()

    # KSAU connection
    if r_41['ksau_ratio'] is not None:
        ksau_ratio = r_41['ksau_ratio']
        print("KSAU Connection:")
        print(f"  ln(m_muon) / Vol(4_1) = {ksau_ratio:.6f}")
        print(f"  N*κ (lepton) = {r_41['ksau_coeff']:.6f}")
        print()
        print(f"  Ratio: {ksau_ratio / r_41['ksau_coeff']:.6f}")
        print("  (Should be close to 1 if ln(m) ~ N*κ*Vol holds without intercept)")
        print()
        print("  Note: KSAU has intercept C, so ln(m)/Vol != N*κ exactly.")

    print()

    # Save results
    output_file = Path(__file__).parent.parent / 'papers' / 'torsion_analysis_results.json'
    with open(output_file, 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        results_serializable = []
        for r in results:
            r_clean = {}
            for k, v in r.items():
                if isinstance(v, (np.floating, np.integer)):
                    r_clean[k] = float(v)
                elif isinstance(v, float) and np.isnan(v):
                    r_clean[k] = None
                else:
                    r_clean[k] = v
            results_serializable.append(r_clean)

        json.dump({
            'analysis': 'Reidemeister Torsion vs Ray-Singer Formula',
            'date': '2026-02-14',
            'ray_singer_formula': 'ln|T| ~ Vol / (2*pi)',
            'ksau_formula': 'ln(m) = N * kappa * Vol + C',
            'discrepancy_factor': 16.4,
            'results': results_serializable
        }, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
