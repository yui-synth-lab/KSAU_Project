# KSAU v17.0 Code: Topological Unraveling Simulation

**Version:** 0.2.1 (Refined Toy Model)
**Date:** 2026-02-17
**Status:** Planning / Audited

## [AUDIT ADVISORY 2026-02-17]
**Theoretical Auditor (Claude):** "Current a⁻² scaling and alpha parameters are standard cosmic string theory/empirical placeholders. The simulation demonstrates qualitative behavior but lacks direct derivation from KSAU's geometric constants (κ, N, etc.)."

## Overview
This directory contains the simulation code for the **"Topological Unraveling"** hypothesis.
**IMPORTANT:** The current implementation is a **non-KSAU toy model** used to verify the qualitative scaling behavior of topological tension vs. volume expansion.

## Future Goals (Phase 1)
- **KSAU Parameter Connection:** Derive the "unraveling rate" ($\alpha$) from the KSAU constant $\kappa = \pi/24$ and the lattice coordination number $N=41$.
- **Quantitative Validation:** Compare results against NFW profiles and galaxy rotation curve data.

## The Model
We model the universe using a modified Friedman equation system coupled with a topological decay term.

### Variables
- $a(t)$: Scale Factor.
- $T(t)$: **Topological Tension** (Background constraint proxy for DM). Modeled as 1D defects with density scaling $\rho_T \propto a^{-2}$.
- $M(t)$: **Relaxed Matter** (Baryons). Modeled as 3D fluid with density scaling $\rho_M \propto a^{-3}$.

### Equations
1. **Expansion:**
   $$ \frac{da}{dt} = a H_0 \sqrt{\Omega_{\Lambda} + T + M} $$
2. **Tension Decay (Unraveling):**
   $$ \frac{dT}{dt} = -2HT - \Gamma(H)T $$
   Where $2HT$ is geometric dilution (area expansion for 1D defects) and $\Gamma(H)$ is the conversion rate to matter.
3. **Matter Creation:**
   $$ \frac{dM}{dt} = -3HM + \Gamma(H)T $$

## Results (Qualitative)
The simulation demonstrates how Topological Tension ($a^{-2}$) naturally persists longer than Baryonic Matter ($a^{-3}$), providing a geometric justification for Dark Matter's dominance.

## Usage
```bash
python unraveling_dynamics.py
```
Output data is saved to `../data/unraveling_simulation_results.csv`.
