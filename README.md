# KSAU: The Geometry of Everything
### Topological Resonance & The Limits of Geometric Unification

[![Status](https://img.shields.io/badge/Status-ARCHIVED_(Passive_Monitoring)-red)](v38.0/KSAU_v38.0_Roadmap.md)
[![Version](https://img.shields.io/badge/Version-v37.0--archived-lightgrey)](v37.0/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/1148825711.svg)](https://doi.org/10.5281/zenodo.18631885)

> **"The vacuum resonates, but the coupling is free."**

**KSAU (Knot-Synchronization-Adhesion Unified)** is a theoretical physics framework exploring the geometric origins of the Standard Model and Cosmology. While the project successfully derives a scale-dependent topological resonance that resolves the $S_8$ cosmological tension ($p=0.00556$), extensive investigation has confirmed that the mass hierarchy multiplier ($q_{mult}=7$) cannot be derived from first principles within this geometry. 

**Current State:** The project is in **Hibernation (Passive Monitoring)**. Active development has ceased. The repository serves as a permanent archive of the methodology, negative results, and the specific $S_8$ prediction awaiting verification by Euclid/LSST data.

---

## 🔬 Project Status: ARCHIVED (Passive Monitoring)

The theoretical development phase is complete. The repository is **Read-Only** for all intents and purposes, except for the periodic update of the $S_8$ monitoring log.

1.  **Theory Construction:** **COMPLETE** (v1.0 - v37.0)
2.  **Negative Results:** **PUBLISHED** (see `NEGATIVE_RESULTS_INDEX.md`)
3.  **External Verification:** **PENDING** (Euclid DR1 / LSST Y1)

---

## 🌌 Key Findings & Documentation

### 📄 Final Publications
- **Negative Results Index:** [NEGATIVE_RESULTS_INDEX.md](NEGATIVE_RESULTS_INDEX.md) - A comprehensive list of all rejected hypotheses.
- **LaTeX Draft:** [v37.0/paper_latex_draft.tex](v37.0/paper_latex_draft.tex) - The formal derivation and statistical analysis.
- **Monitoring Log:** [v37.0/s8_monitoring_log.md](v37.0/s8_monitoring_log.md) - Record of external $S_8$ measurements.

### ✅ Validated: Cosmological Resonance ($S_8$ Tension)
The KSAU framework predicts a specific suppression of the growth of structure ($S_8$) at intermediate redshifts due to the resonant scale of the Leech lattice ($R_{cell} \approx 20$ Mpc).
- **Prediction:** $S_8(z \approx 1.0) \in [0.72, 0.76]$ (Euclid forecast).
- **Status:** Statistically significant on current data; awaiting Euclid/LSST confirmation.

### ❌ Negative Result: Algebraic Mass Origin
Despite high-precision fits ($R^2 > 0.99$), the multiplicative factor $q_{mult}=7$ scaling the fermion mass spectrum has been proven to be algebraically independent of the base geometry.
- **Conclusion:** The mass hierarchy is an effective parameterization, not a first-principles derivation.

---

## 🛠️ Usage & Reproduction

This repository is archived, but the code remains executable for verification purposes.

### 1. Environment Setup
Dependencies are pinned in `v37.0/requirements.txt`.
```bash
pip install -r v37.0/requirements.txt
```

### 2. SSoT Audit (Data Integrity)
To verify the internal consistency of the physical constants and topology assignments against the Single Source of Truth:
```bash
python v6.0/code/ckm_final_audit.py
```

### 3. Cosmological Predictions ($S_8$)
To generate the $S_8$ tension resolution plots and statistics:
```bash
python v28.0/code/ksau_standard_cosmology.py
```

---

## 📬 Contact & Maintenance

This repository is maintained in a **Passive Monitoring** state.
- **Bug Reports:** Please open an issue on GitHub.
- **Future Research:** Researchers interested in the $S_8$ tension predictions should refer to the monitoring protocol in `v38.0/monitoring_protocol.md`.

---

## 📜 Citation

If you use KSAU in your research, please cite our definitive negative results paper:

> **KSAU Collaboration.** (2026). *Negative Results on the Algebraic Origin of Mass Multipliers in Leech Lattice Geometry.* arXiv:2602.XXXX [hep-th].

---

## 📄 License
This project is open-source under the **MIT License**.
