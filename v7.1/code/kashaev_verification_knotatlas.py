#!/usr/bin/env python3
"""
Comprehensive Verification: Kashaev Invariants for 4_1, 6_1, 7_3

Re-verification of all N=3 calculations using KnotAtlas data
to determine if the mathematical identity J_N(K; e^{2πi/N}) = 1 holds

Source: https://katlas.org/wiki/
Author: Claude Opus 4.6
Date: 2026-02-14
"""

import numpy as np
import cmath
import json
from pathlib import Path

def evaluate_polynomial(coeffs_dict, q):
    """
    Evaluate polynomial given as dictionary {exponent: coefficient}
    """
    total = 0.0 + 0.0j
    for exp, coeff in coeffs_dict.items():
        total += coeff * (q ** exp)
    return total

def main():
    print("="*70)
    print("COMPREHENSIVE VERIFICATION: N=3 Kashaev Invariants")
    print("Source: KnotAtlas (katlas.org)")
    print("="*70)
    print()

    # Load physical constants
    constants_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(constants_path, 'r') as f:
        phys = json.load(f)

    m_e = phys['leptons']['Electron']['observed_mass']
    m_mu = phys['leptons']['Muon']['observed_mass']
    m_tau = phys['leptons']['Tau']['observed_mass']

    ln_ratio_mu_e = np.log(m_mu / m_e)
    ln_ratio_tau_e = np.log(m_tau / m_e)

    print("Physical Targets:")
    print(f"  Muon: ln(m_mu/m_e) = {ln_ratio_mu_e:.6f} => <K>_3 ~ {np.exp(ln_ratio_mu_e * 3 / (2 * np.pi)):.2f}")
    print(f"  Tau:  ln(m_tau/m_e) = {ln_ratio_tau_e:.6f} => <K>_3 ~ {np.exp(ln_ratio_tau_e * 3 / (2 * np.pi)):.2f}")
    print()

    # N=3 root of unity
    N = 3
    q = cmath.exp(2 * cmath.pi * 1j / N)

    print(f"Evaluation point:")
    print(f"  q = exp(2*pi*i/{N}) = {q.real:.6f} + {q.imag:.6f}i")
    print()

    # Colored Jones polynomials from KnotAtlas (n=2, representing 3-dimensional rep)

    # 4_1 (Figure-eight knot)
    J3_41_coeffs = {
        6: 1, 5: -1, 4: -1, 3: 2, 2: -1, 1: -1, 0: 3,
        -1: -1, -2: -1, -3: 2, -4: -1, -5: -1, -6: 1
    }

    # 6_1 (Stevedore knot)
    J3_61_coeffs = {
        6: 1, 5: -1, 3: 2, 2: -3, 0: 4,
        -1: -4, -3: 4, -4: -3, -6: 3, -7: -2, -8: -1, -9: 2, -10: -1, -11: -1, -12: 1
    }

    # 7_3 knot
    J3_73_coeffs = {
        48: -1, 47: 1, 44: -1, 43: 2, 41: -1, 40: -2, 39: 4, 38: 2, 37: -4, 36: -5,
        35: 6, 34: 6, 33: -7, 32: -7, 31: 6, 30: 10, 29: -9, 28: -8, 27: 6, 26: 9,
        25: -7, 24: -7, 23: 4, 22: 8, 21: -4, 20: -6, 19: 1, 18: 7, 17: -1, 16: -4,
        15: -2, 14: 5, 13: 1, 12: -2, 11: -2, 10: 2, 9: 1, 7: -1, 6: 1
    }

    knots = {
        '4_1': {
            'description': 'Figure-eight (Muon assignment)',
            'volume': 2.0298832128,
            'coeffs': J3_41_coeffs,
            'target_particle': 'Muon',
            'target_ln_ratio': ln_ratio_mu_e,
            'target_kashaev': np.exp(ln_ratio_mu_e * 3 / (2 * np.pi)),
            'previous_claim': 13.00
        },
        '6_1': {
            'description': 'Stevedore (v6.0 Tau assignment)',
            'volume': 3.1639632288,
            'coeffs': J3_61_coeffs,
            'target_particle': 'Tau',
            'target_ln_ratio': ln_ratio_tau_e,
            'target_kashaev': np.exp(ln_ratio_tau_e * 3 / (2 * np.pi)),
            'previous_claim': 27.07
        },
        '7_3': {
            'description': 'Knot 7_3 (Empirical scaling candidate)',
            'volume': 4.5921256970,
            'coeffs': J3_73_coeffs,
            'target_particle': 'Tau',
            'target_ln_ratio': ln_ratio_tau_e,
            'target_kashaev': np.exp(ln_ratio_tau_e * 3 / (2 * np.pi)),
            'previous_claim': 50.0
        }
    }

    results = []

    for name, data in knots.items():
        print(f"{'='*70}")
        print(f"Knot: {name} - {data['description']}")
        print(f"{'='*70}")
        print(f"Volume: {data['volume']:.10f}")
        print(f"Target particle: {data['target_particle']}")
        print(f"Previous claim: <{name}>_3 = {data['previous_claim']:.2f}")
        print()

        # Evaluate colored Jones polynomial at q = exp(2*pi*i/3)
        J_q = evaluate_polynomial(data['coeffs'], q)
        kashaev = abs(J_q)

        print(f"KnotAtlas Colored Jones Polynomial J_3(q):")
        print(f"  Number of terms: {len(data['coeffs'])}")
        print(f"  Exponent range: {min(data['coeffs'].keys())} to {max(data['coeffs'].keys())}")
        print()

        print(f"Evaluation at q = exp(2*pi*i/3):")
        print(f"  J_3(q) = {J_q.real:.6f} + {J_q.imag:.6f}i")
        print(f"  <{name}>_3 = |J_3(q)| = {kashaev:.6f}")
        print()

        # Compare with previous claim
        if data['previous_claim'] is not None:
            discrepancy = abs(kashaev - data['previous_claim']) / data['previous_claim'] * 100
            print(f"Comparison with Previous Claim:")
            print(f"  Previous:  <{name}>_3 = {data['previous_claim']:.2f}")
            print(f"  KnotAtlas: <{name}>_3 = {kashaev:.2f}")
            print(f"  Discrepancy: {discrepancy:.2f}%")

            if discrepancy > 1:
                print(f"  *** CRITICAL: Previous claim was WRONG ***")
            else:
                print(f"  OK: Previous claim verified")
            print()

        # Compute mass ratio prediction
        if kashaev > 0:
            factor = (2 * np.pi / 3) * np.log(kashaev)
        else:
            factor = np.nan

        error_log = abs(factor - data['target_ln_ratio']) / data['target_ln_ratio'] * 100 if not np.isnan(factor) else 999
        error_kas = abs(kashaev - data['target_kashaev']) / data['target_kashaev'] * 100

        print(f"N=3 Hypothesis Test for {data['target_particle']}:")
        print(f"  (2*pi/3)*ln(<{name}>_3) = {factor:.6f}")
        print(f"  Target ln(m/m_e)         = {data['target_ln_ratio']:.6f}")
        print(f"  Error (log):               {error_log:.2f}%")
        print()
        print(f"  <{name}>_3 prediction:    {kashaev:.2f}")
        print(f"  Target:                    {data['target_kashaev']:.2f}")
        print(f"  Error (Kashaev):           {error_kas:.2f}%")
        print()

        # Verdict
        if error_log < 1.0:
            verdict = "EXCELLENT MATCH"
        elif error_log < 5.0:
            verdict = "GOOD MATCH"
        elif error_log < 10.0:
            verdict = "Promising"
        elif error_log < 15.0:
            verdict = "Marginal"
        else:
            verdict = "REJECTED"

        print(f"VERDICT: {verdict}")
        print()

        results.append({
            'name': name,
            'kashaev_3_knotatlas': kashaev,
            'kashaev_3_previous': data['previous_claim'],
            'discrepancy_percent': discrepancy if data['previous_claim'] else None,
            'error_log_percent': error_log,
            'error_kashaev_percent': error_kas,
            'verdict': verdict
        })

    # Final Analysis
    print("="*70)
    print("FINAL ANALYSIS: Mathematical Identity Investigation")
    print("="*70)
    print()

    all_equal_to_one = all(abs(r['kashaev_3_knotatlas'] - 1.0) < 0.01 for r in results)

    if all_equal_to_one:
        print("CRITICAL FINDING:")
        print("  ALL knots give <K>_3 = 1.00 when evaluated at q = exp(2*pi*i/3)")
        print()
        print("This is a MATHEMATICAL IDENTITY:")
        print("  J_N(K; e^{2πi/N}) = 1 for all hyperbolic knots K")
        print()
        print("IMPLICATIONS:")
        print("  1. The N=3 hypothesis was FUNDAMENTALLY FLAWED from the beginning")
        print("  2. The 'Muon 0.76% agreement' was based on incorrect calculation")
        print("  3. The empirical scaling (<4_1>_3=13, <6_1>_3=27) was WRONG")
        print("  4. The Volume Conjecture ONLY works in the limit N→∞")
        print()
        print("CONCLUSION:")
        print("  Finite N evaluation of Kashaev invariants CANNOT predict particle masses")
        print("  The continuous Volume Law (v6.0) is the only valid approach")
        print()
    else:
        print("MIXED RESULTS:")
        print("  Not all knots give <K>_3 = 1")
        print()
        for r in results:
            status = "= 1" if abs(r['kashaev_3_knotatlas'] - 1.0) < 0.01 else f"= {r['kashaev_3_knotatlas']:.2f}"
            print(f"  {r['name']}: <K>_3 {status}")
        print()
        print("CONCLUSION:")
        print("  Mathematical identity does not hold universally")
        print("  Further investigation needed to understand the pattern")
        print()

    # Save results
    output_file = Path(__file__).parent.parent / 'papers' / 'kashaev_verification_knotatlas_final.json'
    with open(output_file, 'w') as f:
        json.dump({
            'verification_date': '2026-02-14',
            'data_source': 'KnotAtlas (katlas.org)',
            'knots': results,
            'mathematical_identity': all_equal_to_one,
            'conclusion': 'N=3 hypothesis definitively rejected' if all_equal_to_one else 'Mixed results'
        }, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
