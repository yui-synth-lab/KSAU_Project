#!/usr/bin/env python3
"""
Systematic Search for Tau Mass Knot (N=3 Kashaev Invariant)

Goal: Find a knot K such that (2π/3)*ln|⟨K⟩_3| ≈ ln(m_τ/m_e) = 8.154
Expected: ⟨K⟩_3 ≈ 49

Method: Download and evaluate all twist knots K_m (m = -14 to 15) from
Garoufalidis database and find the best match.

Author: Claude Opus 4.6
Date: 2026-02-14
"""

import numpy as np
import cmath
from pathlib import Path
import json
import urllib.request
import gzip
import shutil
import re
import sys

# Base URL for Garoufalidis database
BASE_URL = "https://people.mpim-bonn.mpg.de/stavros/publications/twist.knot.data/"

def download_twist_knot_data(m, data_dir):
    """Download colored Jones polynomial data for twist knot K_m"""
    filename = f"CJTwist.{m}.txt.gz"
    url = BASE_URL + filename
    local_gz = data_dir / filename
    local_txt = data_dir / f"CJTwist.{m}.txt"

    # Check if already downloaded and extracted
    if local_txt.exists():
        print(f"  Already have {local_txt.name}")
        return local_txt

    # Download
    print(f"  Downloading {filename}...", end=" ")
    try:
        urllib.request.urlretrieve(url, local_gz)
        print("OK")
    except Exception as e:
        print(f"FAILED ({e})")
        return None

    # Extract
    print(f"  Extracting...", end=" ")
    try:
        with gzip.open(local_gz, 'rb') as f_in:
            with open(local_txt, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print("OK")
        # Clean up gz file
        local_gz.unlink()
        return local_txt
    except Exception as e:
        print(f"FAILED ({e})")
        return None

def parse_mathematica_list(content):
    """
    Extract the first few polynomials from Mathematica list format.
    Returns list of polynomial strings.
    """
    # Strip outer braces
    content = content.strip()
    if content.startswith('{'):
        content = content[1:]
    if content.endswith('}'):
        content = content[:-1]

    # Find comma positions at depth 0
    depth = 0
    comma_positions = []
    for i, c in enumerate(content):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == ',' and depth == 0:
            comma_positions.append(i)

    # Extract first 5 polynomials (indices 0-4, corresponding to N=1,2,3,4,5)
    polys = []
    start = 0
    for pos in comma_positions[:5]:  # Get first 5 commas
        poly_str = content[start:pos].strip()
        polys.append(poly_str)
        start = pos + 1

    # Get one more if available
    if start < len(content) and len(polys) < 5:
        remaining = content[start:].strip()
        # Find the end (next comma or end of string)
        end = remaining.find(',')
        if end > 0:
            polys.append(remaining[:end].strip())
        else:
            polys.append(remaining)

    return polys

def eval_poly_at_root_of_unity(poly_str, N):
    """
    Evaluate polynomial at q = e^{2πi/N}.
    Returns |J_N(q)|.

    Note: This is a simplified evaluator. For complex polynomials,
    we use symbolic evaluation with numpy.
    """
    q = cmath.exp(2 * cmath.pi * 1j / N)

    # Replace Mathematica notation with Python
    # q^(-n) -> q**(-n)
    # n/q^m -> n * q**(-m)
    # n*q^m -> n * q**m

    poly_str = poly_str.strip()

    # Simple approach: replace q with actual value and use eval
    # This is unsafe in general, but OK for trusted Garoufalidis data

    # Prepare for evaluation
    expr = poly_str

    # Replace q^(...) with q**(...)
    expr = re.sub(r'q\^(\(-?\d+\))', r'q**\1', expr)
    expr = re.sub(r'q\^(-?\d+)', r'q**\1', expr)

    # Replace /q^n with * q**(-n)
    expr = re.sub(r'/q\^(\d+)', r'* q**(-\1)', expr)

    # Replace /q with * q**(-1)
    expr = expr.replace('/q', '* q**(-1)')

    # Replace standalone q with q**1
    expr = re.sub(r'([^q*])q([^*\^])', r'\1q**1\2', expr)

    # Add q**1 at start if needed
    if expr.startswith('q ') or expr.startswith('q+') or expr.startswith('q-'):
        expr = 'q**1' + expr[1:]

    try:
        result = eval(expr, {"q": q, "e": np.e, "pi": np.pi})
        return abs(result)
    except Exception as e:
        print(f"    Error evaluating polynomial: {e}")
        print(f"    Expression: {expr[:100]}")
        return None

def main():
    print("="*70)
    print("Systematic Search for Tau Mass Knot (N=3)")
    print("="*70)
    print()

    # Setup
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)

    # Load physical constants
    constants_path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(constants_path, 'r') as f:
        phys = json.load(f)

    m_e = phys['leptons']['Electron']['observed_mass']
    m_tau = phys['leptons']['Tau']['observed_mass']
    ln_ratio_tau_e = np.log(m_tau / m_e)

    target_kashaev = np.exp(ln_ratio_tau_e * 3 / (2 * np.pi))

    print(f"Target:")
    print(f"  ln(m_tau/m_e) = {ln_ratio_tau_e:.6f}")
    print(f"  Expected <K>_3 ~ {target_kashaev:.2f}")
    print()

    # Download and process all twist knots
    print("Downloading Garoufalidis database (twist knots K_m, m = -14 to 15)...")
    print()

    results = []

    for m in range(-14, 16):  # -14 to 15 inclusive
        print(f"Twist knot K_{m}:")

        # Download
        txt_file = download_twist_knot_data(m, data_dir)
        if txt_file is None:
            continue

        # Parse
        try:
            with open(txt_file, 'r') as f:
                content = f.read()

            polys = parse_mathematica_list(content)

            if len(polys) < 3:
                print(f"  Warning: Only {len(polys)} polynomials found")
                continue

            # Evaluate N=3 (third polynomial, index 2)
            poly_3 = polys[2]
            kashaev_3 = eval_poly_at_root_of_unity(poly_3, 3)

            if kashaev_3 is None:
                print(f"  Failed to evaluate")
                continue

            # Compute error
            factor = (2 * np.pi / 3) * np.log(kashaev_3)
            error_log = abs(factor - ln_ratio_tau_e) / ln_ratio_tau_e * 100
            error_kashaev = abs(kashaev_3 - target_kashaev) / target_kashaev * 100

            results.append({
                'm': m,
                'kashaev_3': kashaev_3,
                'factor': factor,
                'error_log': error_log,
                'error_kashaev': error_kashaev
            })

            print(f"  <K_{m}>_3 = {kashaev_3:.2f}")
            print(f"  (2π/3)*ln(<K_{m}>_3) = {factor:.4f} (target: {ln_ratio_tau_e:.4f})")
            print(f"  Error: {error_log:.2f}% (log), {error_kashaev:.2f}% (Kashaev)")

        except Exception as e:
            print(f"  Error processing: {e}")

        print()

    # Summary
    print("="*70)
    print("SUMMARY: Best Matches for Tau")
    print("="*70)
    print()

    if not results:
        print("No results found!")
        return

    # Sort by Kashaev error
    results_sorted = sorted(results, key=lambda x: x['error_kashaev'])

    print(f"{'Knot':<10} | {'<K>_3':<10} | {'Target':<10} | {'Error (K)':<12} | {'Error (log)':<12}")
    print("-" * 70)

    for i, r in enumerate(results_sorted[:10]):  # Top 10
        m = r['m']
        kashaev = r['kashaev_3']
        err_k = r['error_kashaev']
        err_log = r['error_log']

        marker = " ** BEST **" if i == 0 else ""
        print(f"K_{m:<8} | {kashaev:<10.2f} | {target_kashaev:<10.2f} | {err_k:>10.2f}% | {err_log:>10.2f}% {marker}")

    print()

    # Best match
    best = results_sorted[0]
    print("="*70)
    print("BEST MATCH")
    print("="*70)
    print()
    print(f"Twist Knot: K_{best['m']}")
    print(f"  <K_{best['m']}>_3 = {best['kashaev_3']:.4f}")
    print(f"  Target:     {target_kashaev:.4f}")
    print(f"  Error:      {best['error_kashaev']:.2f}%")
    print()
    print(f"  (2π/3)*ln(<K_{best['m']}>_3) = {best['factor']:.6f}")
    print(f"  ln(m_tau/m_e)                 = {ln_ratio_tau_e:.6f}")
    print(f"  Error:                         {best['error_log']:.2f}%")
    print()

    # Interpretation
    if best['error_log'] < 5:
        print("SUCCESS! This knot reproduces Tau mass to <5%!")
        print(f"Recommendation: Re-assign Tau from 6_1 to K_{best['m']}")
    elif best['error_log'] < 15:
        print("Suggestive. This is better than 6_1 (15.27% error).")
        print(f"Consider K_{best['m']} as alternative assignment.")
    else:
        print(f"No good match found. Best error is {best['error_log']:.2f}%.")
        print("The N=3 hypothesis is definitively rejected for Tau.")

    print()

    # Save results
    output_file = data_dir.parent / 'papers' / 'tau_knot_search_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'target': {
                'ln_tau_e': ln_ratio_tau_e,
                'expected_kashaev_3': target_kashaev
            },
            'results': results_sorted,
            'best_match': best
        }, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

if __name__ == '__main__':
    main()
