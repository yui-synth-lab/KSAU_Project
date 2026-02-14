#!/usr/bin/env python3
"""
Parse Garoufalidis's colored Jones polynomial data for 6_1 knot

Extracts J_N(6_1; q) from CJTwist.-2.txt and evaluates at q = e^{2πi/N}
to get the Kashaev invariant.

Author: Claude Opus 4.6
Date: 2026-02-14
"""

import re
import numpy as np
import cmath
from pathlib import Path

def parse_mathematica_poly(poly_str):
    """
    Parse Mathematica polynomial string like:
    '2 + q^(-4) - q^(-3) + q^(-2) - 2/q - q + q^2'

    Returns: list of (power, coefficient) tuples
    """
    # Remove spaces
    poly_str = poly_str.strip()

    # Split by + and - while keeping the sign
    terms = re.split(r'([+-])', poly_str)

    # Clean up: merge signs with terms
    clean_terms = []
    i = 0
    while i < len(terms):
        term = terms[i].strip()
        if term == '':
            i += 1
            continue
        if term in ['+', '-']:
            if i + 1 < len(terms):
                sign = 1 if term == '+' else -1
                next_term = terms[i + 1].strip()
                clean_terms.append((sign, next_term))
                i += 2
            else:
                i += 1
        else:
            # First term without explicit sign
            clean_terms.append((1, term))
            i += 1

    # Parse each term
    result = []
    for sign, term in clean_terms:
        # Patterns:
        # - constant: '2'
        # - q^n: 'q^2', 'q^12'
        # - q^(-n): 'q^(-4)'
        # - 1/q^n: '2/q^7', '/q'
        # - just q: 'q'

        if 'q' not in term:
            # Pure constant
            coef = sign * float(term)
            result.append((0, coef))
        elif term == 'q':
            # Just q
            result.append((1, sign * 1.0))
        elif '/' in term:
            # Form: c/q^n or c/q
            parts = term.split('/')
            if len(parts) == 2:
                left, right = parts
                if left == '':
                    coef = 1.0
                else:
                    coef = float(left)

                if right == 'q':
                    power = -1
                elif 'q^' in right:
                    power = -int(right.split('^')[1])
                else:
                    power = -1

                result.append((power, sign * coef))
        elif '^' in term:
            # Form: c*q^n or q^n
            match = re.match(r'([0-9.]*)\*?q\^(.+)', term)
            if match:
                coef_str, power_str = match.groups()
                coef = float(coef_str) if coef_str else 1.0
                # Handle q^(-4) or q^4
                if power_str.startswith('('):
                    power = int(power_str.strip('()'))
                else:
                    power = int(power_str)
                result.append((power, sign * coef))
        else:
            # Should not reach here
            print(f"Warning: unparsed term '{term}'")

    return result

def eval_poly(poly_terms, q):
    """Evaluate polynomial at q"""
    result = complex(0.0)
    for power, coef in poly_terms:
        result += coef * (q ** power)
    return result

def main():
    # Load the data
    data_path = Path(__file__).parent.parent / 'data' / 'CJTwist.-2.txt'

    with open(data_path, 'r') as f:
        content = f.read()

    # The file is a Mathematica list: {poly1, poly2, poly3, ...}
    # Strip outer braces
    content = content.strip()
    if content.startswith('{'):
        content = content[1:]
    if content.endswith('}'):
        content = content[:-1]

    # Split by commas at the top level (careful with nested braces)
    # For simplicity, we'll look for the pattern between successive indices

    # Actually, let's extract the first few polynomials manually by position
    # The structure is: {poly1, poly2, poly3, poly4, ...}
    # where each poly can span multiple lines

    # Find the 3rd polynomial (for N=3)
    # Start after first two commas at brace level 0

    depth = 0
    comma_positions = []
    for i, c in enumerate(content):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == ',' and depth == 0:
            comma_positions.append(i)

    # Extract polynomials
    polys = []
    start = 0
    for pos in comma_positions[:10]:  # Get first 10 polynomials
        poly_str = content[start:pos].strip()
        polys.append(poly_str)
        start = pos + 1

    # Also get the last one (or next few)
    if start < len(content):
        poly_str = content[start:start+2000].strip()
        # Find where it ends (next comma or end)
        end = poly_str.find(',')
        if end > 0:
            polys.append(poly_str[:end])
        else:
            polys.append(poly_str)

    print("="*70)
    print("Garoufalidis Colored Jones Polynomial Data for 6_1 Knot")
    print("="*70)
    print()

    # The list is 1-indexed: {J_1, J_2, J_3, ...}
    # J_1 should be 1 (trivial representation)
    # J_2 is the standard Jones polynomial
    # J_3 is what we need

    for N in range(1, min(len(polys)+1, 6)):
        poly_str = polys[N-1]
        print(f"N={N}:")
        print(f"  Polynomial (truncated): {poly_str[:100]}...")
        print()

        if N == 1:
            # Should be just 1
            print(f"  J_1 = {poly_str}")
        elif N >= 2:
            # Parse and evaluate at root of unity
            poly_terms = parse_mathematica_poly(poly_str)
            q = cmath.exp(2 * cmath.pi * 1j / N)

            J_N = eval_poly(poly_terms, q)
            kashaev = abs(J_N)

            print(f"  q = e^(2πi/{N})")
            print(f"  J_{N}(q) = {J_N}")
            print(f"  |J_{N}(q)| = {kashaev:.6f}")

            # Volume Conjecture check
            vol_61 = 3.1639632288
            if kashaev > 0:
                vol_from_J = (2 * np.pi / N) * np.log(kashaev)
                error = abs(vol_from_J - vol_61) / vol_61 * 100
                print(f"  (2π/{N})·ln|J_{N}| = {vol_from_J:.6f} (Vol = {vol_61:.6f}, error = {error:.2f}%)")
        print()

    # Focus on N=3 for Tau mass prediction
    print("="*70)
    print("N=3 ANALYSIS: Tau Mass Prediction")
    print("="*70)
    print()

    # Load physical constants
    import json
    constants_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(constants_path, 'r') as f:
        phys = json.load(f)

    m_e = phys['leptons']['Electron']['observed_mass']
    m_mu = phys['leptons']['Muon']['observed_mass']
    m_tau = phys['leptons']['Tau']['observed_mass']

    ln_ratio_mu_e = np.log(m_mu / m_e)
    ln_ratio_tau_e = np.log(m_tau / m_e)

    print(f"Target: ln(m_τ/m_e) = {ln_ratio_tau_e:.6f}")
    print()

    # Parse N=3 polynomial (3rd in list, index 2)
    if len(polys) >= 3:
        poly_str_3 = polys[2]
        print(f"J_3(6_1; q) polynomial:")
        # Show full polynomial
        lines = poly_str_3.split('\n')
        for line in lines[:5]:
            print(f"  {line}")
        if len(lines) > 5:
            print(f"  ... ({len(lines)} lines total)")
        print()

        poly_terms_3 = parse_mathematica_poly(poly_str_3)
        q3 = cmath.exp(2 * cmath.pi * 1j / 3)

        J_3 = eval_poly(poly_terms_3, q3)
        kashaev_3 = abs(J_3)

        print(f"Kashaev invariant ⟨6_1⟩_3 = |J_3(e^(2πi/3))| = {kashaev_3:.6f}")
        print()

        # Compute (2π/3)·ln|⟨6_1⟩_3|
        if kashaev_3 > 0:
            factor = (2 * np.pi / 3) * np.log(kashaev_3)
            error = abs(factor - ln_ratio_tau_e) / ln_ratio_tau_e * 100

            print(f"Prediction:")
            print(f"  (2π/3)·ln(⟨6_1⟩_3) = {factor:.6f}")
            print(f"  ln(m_τ/m_e)         = {ln_ratio_tau_e:.6f}")
            print(f"  Error: {error:.2f}%")
            print()

            # Also compute what mass ratio this would imply
            implied_ratio = np.exp(factor)
            actual_ratio = m_tau / m_e
            mass_error = abs(implied_ratio - actual_ratio) / actual_ratio * 100

            print(f"Implied mass ratio:")
            print(f"  (⟨6_1⟩_3)^(2π/3) = {implied_ratio:.1f}")
            print(f"  m_τ/m_e          = {actual_ratio:.1f}")
            print(f"  Error: {mass_error:.2f}%")
            print()

            if error < 5:
                print("✓ SUCCESS! The N=3 pattern extends to Tau!")
                print("  The hierarchy is REAL.")
            elif error < 15:
                print("~ SUGGESTIVE. The N=3 pattern shows promise for Tau.")
                print("  Further investigation warranted.")
            else:
                print("✗ The N=3 Muon result appears to be an arithmetic coincidence.")
                print("  The pattern does not extend to Tau.")

    print()
    print("="*70)

if __name__ == '__main__':
    main()
