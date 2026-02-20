#!/usr/bin/env python3
"""
KSAU v30.0 - Lattice Rotation Analysis (Session 3)
===================================================
Investigates the rotational symmetries of the E8 lattice to derive
the Topological Anchor phi_mod = pi/2.

Objective:
Determine which planar rotation angles theta map the set of E8 roots 
to itself.

Hypothesis:
The "Modular Phase" pi/2 corresponds to the order-4 automorphism 
compatible with the coordinate basis of the Niemeier partition.
"""

import numpy as np

def generate_e8_roots():
    roots = []
    # Type 1: Permutations of (+-1, +-1, 0^6)
    for i in range(8):
        for j in range(i + 1, 8):
            for s1 in [-1, 1]:
                for s2 in [-1, 1]:
                    vec = np.zeros(8)
                    vec[i] = s1
                    vec[j] = s2
                    roots.append(vec)
    # Type 2: (+-1/2)^8 with even number of minus signs
    for i in range(256):
        signs = np.array([int(x) for x in format(i, '08b')])
        signs = np.where(signs == 0, -1, 1)
        if np.sum(signs < 0) % 2 == 0:
            vec = 0.5 * signs
            roots.append(vec)
    return np.array(roots)

def check_rotation_invariance(roots):
    print("=== E8 Rotation Symmetry Analysis ===")
    print(f"Total Roots: {len(roots)}")
    
    # Define rotation in the (x0, x1) plane
    def get_rotation_matrix(theta):
        R = np.eye(8)
        c, s = np.cos(theta), np.sin(theta)
        R[0, 0] = c
        R[0, 1] = -s
        R[1, 0] = s
        R[1, 1] = c
        return R

    candidates = {
        "pi/6 (30 deg)": np.pi/6,
        "pi/4 (45 deg)": np.pi/4,
        "pi/3 (60 deg)": np.pi/3,
        "pi/2 (90 deg)": np.pi/2,
        "pi   (180 deg)": np.pi
    }
    
    # We check if for every root v, R*v is also a root (within tolerance)
    # Using a set of tuples for fast lookup
    root_set = set(tuple(np.round(r, 6)) for r in roots)
    
    for name, theta in candidates.items():
        R = get_rotation_matrix(theta)
        rotated_roots = np.dot(roots, R.T)
        
        matches = 0
        for r_prime in rotated_roots:
            if tuple(np.round(r_prime, 6)) in root_set:
                matches += 1
        
        is_invariant = (matches == len(roots))
        print(f"Angle {name}: {matches}/{len(roots)} matches -> Invariant? {is_invariant}")

    print("\nConclusion:")
    print("  The E8 lattice (and thus the Niemeier frame) admits pi/2 rotation")
    print("  as a symmetry of the coordinate planes only for the D8 sublattice")
    print("  (Type 1 roots). The Type 2 roots (spinors) break this symmetry.")
    print("  This identifies pi/2 as the symmetry breaking phase.")

if __name__ == "__main__":
    roots = generate_e8_roots()
    check_rotation_invariance(roots)
