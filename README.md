# KSAU: Topological Mass Formula from Hyperbolic 3-Manifold Invariants

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-draft__v4-blue.svg)
![Status](https://img.shields.io/badge/status-Under_Review-orange.svg)

> **"Matter is Knot, Force is Link, Gravity is Geometry."**

**KSAU (Knot/String/Anyon Unified Framework)** is a data-driven theoretical physics framework that maps Standard Model particles to hyperbolic 3-manifold topologies and derives their masses and mixing parameters from knot invariants. All results are produced by 69 hypothesis tests conducted across 26 AIRDP cycles, including 24 documented rejections.

---

## Key Results

| Result | Metric | Hypothesis |
| ------ | ------ | ---------- |
| Fermion mass formula | R²=0.9998 (LOO-CV) | H1, H11, H35, H41 |
| 12-particle topology assignment | p=0.0, FPR=0.0 | H49, H55, H64 |
| Gravitational constant G | error=0.0000263% | H20, H46, H53 |
| CKM matrix | R²=0.9980 | H67 |
| κ = π/24 geometric derivation | error=0% | H6, H16, H36, H39, H44 |

---

## Repository Structure

```text
KSAU_Project/
├── papers/ksau_main/     ← Main paper (draft_v04.md)
├── cycles/               ← AIRDP research cycles (cycle_01–cycle_27)
├── ssot/                 ← Single Source of Truth (constants, hypotheses)
├── src/                  ← Simulation code
├── data/                 ← KnotInfo/LinkInfo raw data
├── archive/              ← Historical versions (v1.4–v6.9) and audit logs
├── airdp_prompts/        ← AIRDP role prompts
└── NEGATIVE_RESULTS_INDEX.md  ← Documented rejections
```

---

## Installation & Usage

### Prerequisites

- Python 3.8+
- NumPy, Pandas, Matplotlib, SciPy

### Run the Simulator

```bash
python src/ksau_simulator.py
```

Constants and particle data are loaded from `ssot/constants.json` and `ssot/parameters.json`. No hardcoded values.

---

## Statistical Protocol

All hypotheses were tested under the following criteria:

- **Bonferroni correction**: α = 0.05 / 3 ≈ 0.0167 per cycle
- **LOO-CV**: Leave-One-Out Cross-Validation for all regression models
- **Monte Carlo**: n=10,000, seed=42
- **SSoT adherence**: All constants sourced from `ssot/constants.json`

---

## Citation

> **Yui / KSAU Collaboration.** (2026). *Topological Mass Formula from Hyperbolic 3-Manifold Invariants: A Data-Driven Framework with 69 Hypothesis Tests.* (Zenodo Archive, pending DOI).

---

## License

This project is open-source under the **MIT License**.
