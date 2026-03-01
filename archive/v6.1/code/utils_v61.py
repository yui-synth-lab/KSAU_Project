import pandas as pd
import numpy as np
from pathlib import Path
import re
import json

def load_data():
    """
    Loads KnotInfo and LinkInfo data.
    Returns two DataFrames: knots, links.
    """
    # Paths are relative to project root.
    # __file__ is in project/v6.1/code/
    base_path = Path(__file__).parent.parent.parent / 'data'
    knot_path = base_path / 'knotinfo_data_complete.csv'
    link_path = base_path / 'linkinfo_data_complete.csv'

    knots = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False)
    links = pd.read_csv(link_path, sep='|', skiprows=[1], low_memory=False)
    
    return knots, links

def load_constants():
    """
    Loads physical constants from v6.0/data/physical_constants.json.
    """
    path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'physical_constants.json'
    with open(path, 'r') as f:
        return json.load(f)

def load_assignments():
    """
    Loads topology assignments (unified with physical constants).
    """
    phys = load_constants()
    
    # Base assignments (invariants)
    path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'topology_assignments.json'
    with open(path, 'r') as f:
        assignments = json.load(f)

    # Merge physical metadata into assignments
    for sector in ['quarks', 'leptons', 'bosons']:
        if sector not in phys: continue
        for p_name, p_meta in phys[sector].items():
            if not isinstance(p_meta, dict): continue
            if p_name in assignments:
                assignments[p_name].update(p_meta)
                # Ensure 'sector' key exists for legacy script support
                if 'sector' not in assignments[p_name]:
                    assignments[p_name]['sector'] = sector.rstrip('s')
    
    return assignments

def parse_polynomial(poly_str, variable='x', val=None):
    """
    Parses a polynomial string like "-x^(-5)-x^(-1)" and evaluates it at val.
    If val is None, returns the coefficients dict.
    
    Supported format examples: 
    -x^(-5)-x^(-1)
    1 - 2*t + t^2
    """
    if pd.isna(poly_str):
        return 0.0

    # DEBUG
    # print(f"Raw poly: {poly_str}")

    # Replace specific variable if different
    # The dataset seems to use 'x' or 't' or 'q'.
    # We will standardize to 'x' for parsing.
    poly_str = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x')
    
    # Split by + or - (keeping the sign)
    # This is a simple regex parser.
    # Terms look like: [+-]? [coeff*]? x [^power]?
    
    # Evaluate directly using python's eval if val is provided (easiest for complex numbers)
    # BUT, need to handle '^' as power '**'.
    if val is not None:
        expr = poly_str.replace('^', '**')
        # Safety: verify chars
        if not re.match(r'^[0-9x\+\-\*\(\)\./e\s]+$', expr):
            # Fallback or error
            pass
        
        # Define x in local scope
        x = val
        try:
            # Handle multivariable t1, t2, t3 by mapping them all to x
            clean_expr = re.sub(r'x[0-9]+', 'x', expr)
            # print(f"Eval expr: {clean_expr}")
            return eval(clean_expr)
        except Exception as e:
            # print(f"Error evaluating {poly_str}: {e}")
            return 0.0
    
    return None

def get_jones_at_root_of_unity(poly_str, n=5):
    """
    Evaluates Jones Polynomial at e^(i * 2 * pi / n).
    """
    phase = np.exp(1j * 2 * np.pi / n)
    return parse_polynomial(poly_str, variable='x', val=phase)
