---
name: ksau-physics-engine
description: Execution kernel for KSAU topological simulations. Manages mass formula calculations, flavor-mixing matrix derivations, and verification against experimental data. Use when running core physics scripts to ensure theoretical consistency.
---

# KSAU Physics Engine

## Overview

This skill provides a standardized workflow for executing and validating the KSAU (Knot-based Standard Model) simulations. It ensures that all calculations derive from the Single Source of Truth (SSoT) and follow the proper physical constraints (e.g., mass hierarchy).

## Core Capabilities

### 1. Mass Spectrum Calculation
- **Fermion Masses**: Executes `paper_I_validation.py` to verify $R^2$ for quarks and leptons.
- **Neutrino Sector**: Solves transcendental mass equations using `verify_neutrino_math.py`.
- **Glueballs**: Predicts mass spectra for closed manifolds using `glueball_spectrum_analysis.py`.

### 2. Flavor Mixing Analysis
- **CKM Matrix**: Executes the Master Formula (logit model) via `ckm_final_audit.py`.
- **PMNS Matrix**: Derives mixing angles from unknotting efficiency and boundary resonance.

### 3. Anomaly & Sensitivity Testing
- **g-2 Analysis**: Runs `g_minus_2_analysis.py` to check for geometric contributions to magnetic moments.
- **Robustness**: Varies master constant $\kappa$ via `robustness_check.py` to confirm local optima.

## Operational Workflow

When asked to "run simulations" or "verify physics," follow this sequence:

1. **Environment Check**: Verify presence of `numpy`, `scipy`, `pandas`, and `sklearn`.
2. **SSoT Validation**: Read `v6.0/data/physical_constants.json` to ensure constants are current.
3. **Execution Sequence**:
   - First, run `topology_official_selector.py` if assignments need updating.
   - Second, run `verify_neutrino_math.py` to establish the baseline scale.
   - Third, run validation/audit scripts (`paper_I_validation.py`, `ckm_final_audit.py`).
4. **Consistency Check**: Ensure output $R^2$ matches or exceeds the values recorded in `FINAL_SUMMARY.md`.

## Physics Constraints to Enforce
- **Mass Hierarchy**: $V(Up) < V(Down) < V(Strange) < V(Charm) < V(Bottom) < V(Top)$.
- **Quantization**: All determinants must match the $2^k \times (odd)$ structure defined in `det_charge_analysis.py`.

---
*KSAU Physics Simulation Kernel - First-Principles Derived*
