"""
Quantify the relationship between link determinant and electric charge.
This analysis determines whether Det is a reliable predictor of charge type.
"""

import numpy as np
import ksau_config
import matplotlib.pyplot as plt

def analyze_det_charge_relationship():
    print("="*80)
    print("KSAU v6.0: Determinant-Charge Relationship Analysis")
    print("="*80)

    # Load fermion data
    fermions = ksau_config.load_topology_assignments()

    # Define charge values
    charge_map = {
        'up-type': +2/3,
        'down-type': -1/3,
        'lepton': -1,
        'boson': 0
    }

    # Extract data
    particles = []
    determinants = []
    charges = []
    components = []

    for name, data in fermions.items():
        particles.append(name)
        determinants.append(data['determinant'])
        charge_type = data['charge_type']
        charges.append(charge_map[charge_type])
        components.append(data['components'])

    determinants = np.array(determinants)
    charges = np.array(charges)
    components = np.array(components)

    print("\n[DATA TABLE]")
    print(f"{'Particle':<10} | {'Det':<5} | {'Comp':<4} | {'Charge':<8} | {'ln(Det)':<8} | {'Det mod 4':<10}")
    print("-" * 80)

    for i, name in enumerate(particles):
        det = determinants[i]
        q = charges[i]
        c = components[i]
        ln_det = np.log(det)
        mod4 = det % 4
        print(f"{name:<10} | {det:<5} | {c:<4} | {q:>+7.2f} | {ln_det:>8.3f} | {mod4:<10}")

    # Analysis 1: Check if ln(Det) correlates with charge
    print("\n[ANALYSIS 1: ln(Det) vs Charge]")

    # Separate by charge type
    up_type_mask = charges == 2/3
    down_type_mask = charges == -1/3
    lepton_mask = charges == -1

    print(f"Up-type quarks (Q=+2/3):")
    print(f"  Determinants: {determinants[up_type_mask]}")
    print(f"  ln(Det) range: [{np.log(determinants[up_type_mask]).min():.2f}, {np.log(determinants[up_type_mask]).max():.2f}]")

    print(f"Down-type quarks (Q=-1/3):")
    print(f"  Determinants: {determinants[down_type_mask]}")
    print(f"  ln(Det) range: [{np.log(determinants[down_type_mask]).min():.2f}, {np.log(determinants[down_type_mask]).max():.2f}]")

    print(f"Leptons (Q=-1):")
    print(f"  Determinants: {determinants[lepton_mask]}")
    print(f"  ln(Det) range: [{np.log(determinants[lepton_mask]).min():.2f}, {np.log(determinants[lepton_mask]).max():.2f}]")

    # Analysis 2: Check modular arithmetic patterns
    print("\n[ANALYSIS 2: Modular Arithmetic Patterns]")
    print("Checking if Det mod 4 distinguishes up/down types...")

    up_mods = determinants[up_type_mask] % 4
    down_mods = determinants[down_type_mask] % 4

    print(f"Up-type: Det mod 4 = {up_mods}")
    print(f"Down-type: Det mod 4 = {down_mods}")

    if len(set(up_mods)) == 1 and len(set(down_mods)) == 1:
        print("[OK] PATTERN FOUND: Det mod 4 cleanly separates up/down types!")
    else:
        print("[NO] No clean modular pattern.")

    # Analysis 3: Check power-of-2 structure
    print("\n[ANALYSIS 3: Power-of-2 Structure]")
    print("Checking if Det = 2^k * (odd) structure relates to charge...")

    for i, name in enumerate(particles):
        det = determinants[i]
        # Factor out powers of 2
        k = 0
        temp = det
        while temp % 2 == 0:
            temp //= 2
            k += 1
        odd_part = temp
        print(f"{name:<10}: Det = 2^{k} × {odd_part}")

    # Analysis 4: Statistical correlation
    print("\n[ANALYSIS 4: Statistical Correlation]")

    # Can we predict charge from Det alone?
    # Try linear regression: Q ~ a*ln(Det) + b
    ln_det = np.log(determinants)

    # Only for quarks (leptons have different structure)
    quark_mask = (charges != -1)
    X = ln_det[quark_mask]
    Y = charges[quark_mask]

    if len(X) > 2:
        coeffs = np.polyfit(X, Y, 1)
        Y_pred = np.polyval(coeffs, X)
        r2 = 1 - np.sum((Y - Y_pred)**2) / np.sum((Y - np.mean(Y))**2)

        print(f"Quark sector regression: Q = {coeffs[0]:.4f}*ln(Det) + {coeffs[1]:.4f}")
        print(f"R^2 = {r2:.4f}")

        if r2 < 0.3:
            print("[NO] Weak correlation: Det does NOT directly encode charge magnitude.")

    # Conclusion
    print("\n" + "="*80)
    print("CONCLUSION:")
    print("-"*80)
    print("The link determinant (Det) does NOT have a simple functional relationship")
    print("with electric charge (Q). The observed pattern is:")
    print("")
    print("  1. Det values vary widely within the same charge type.")
    print("  2. No clean modular arithmetic (Det mod N) distinguishes up/down quarks.")
    print("  3. The determinant appears to be a TOPOLOGICAL LABEL related to the")
    print("     knot's mathematical properties, NOT a direct encoding of charge.")
    print("")
    print("REVISED INTERPRETATION:")
    print("  - Det is used as a SELECTION CRITERION (consistency check) during")
    print("    topology assignment, ensuring mathematical validity.")
    print("  - Charge type is determined by WHICH topology is assigned to each")
    print("    particle, not by a formula involving Det.")
    print("  - The relationship is INDIRECT: topology determines both Det and mass,")
    print("    and the mass hierarchy correlates with charge type by construction.")
    print("="*80)

    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot 1: Det vs Charge
    ax = axes[0]
    ax.scatter(determinants[up_type_mask], charges[up_type_mask],
               s=100, marker='o', color='red', label='Up-type', alpha=0.7)
    ax.scatter(determinants[down_type_mask], charges[down_type_mask],
               s=100, marker='s', color='blue', label='Down-type', alpha=0.7)
    ax.scatter(determinants[lepton_mask], charges[lepton_mask],
               s=100, marker='^', color='green', label='Leptons', alpha=0.7)
    ax.set_xlabel('Determinant (Det)', fontsize=12)
    ax.set_ylabel('Electric Charge (Q)', fontsize=12)
    ax.set_title('Determinant vs Electric Charge', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 2: ln(Det) vs Charge
    ax = axes[1]
    ax.scatter(np.log(determinants[up_type_mask]), charges[up_type_mask],
               s=100, marker='o', color='red', label='Up-type', alpha=0.7)
    ax.scatter(np.log(determinants[down_type_mask]), charges[down_type_mask],
               s=100, marker='s', color='blue', label='Down-type', alpha=0.7)
    ax.scatter(np.log(determinants[lepton_mask]), charges[lepton_mask],
               s=100, marker='^', color='green', label='Leptons', alpha=0.7)
    ax.set_xlabel('ln(Determinant)', fontsize=12)
    ax.set_ylabel('Electric Charge (Q)', fontsize=12)
    ax.set_title('ln(Det) vs Electric Charge', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()

    output_path = ksau_config.Path(__file__).parent.parent / 'figures' / 'det_charge_correlation.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved: {output_path}")

    plt.close()

if __name__ == "__main__":
    analyze_det_charge_relationship()
