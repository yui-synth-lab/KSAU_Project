# KSAU v16.1 Replication Package

This directory contains the core derivation scripts and artifacts for the KSAU v16.1 "Geometric Bridge" framework.

## Contents

- `unified_density_derivation.py`: Derives macroscopic mass density from 24D/4D/3D invariants.
- `impedance_derivation.py`: Demonstrates the convergence of Gauge (Unitary) and Gravity (Transport) scaling laws.
- `gauge_coupling_derivation.py`: Derives α and α_s from Leech lattice and 3D boundary constraints.
- `generate_publication_figures.py`: Generates Figures 2, 3, and 4 for the manuscript.
- `supplementary/Monte_Carlo_Null_Test.py`: Statistical significance verification (p-value calculation).

## Execution

To replicate the results, ensure you have `numpy` and `matplotlib` installed, then run:

```powershell
python unified_density_derivation.py
python impedance_derivation.py
python gauge_coupling_derivation.py
python generate_publication_figures.py
python supplementary/Monte_Carlo_Null_Test.py
```

## Data Sources

The physical constants used in these derivations are sourced from the Single Source of Truth (SSoT) file located at `v6.0/data/physical_constants.json`.

---
*KSAU v16.1 Replication Package | 2026-02-17*
