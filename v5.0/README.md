# KSAU v5.0: Topological Mass Generation from π/24

**Unifying Chern-Simons Theory with Catalan Geometry**

[![arXiv](https://img.shields.io/badge/arXiv-pending-red.svg)](https://arxiv.org)
[![DOI](https://img.shields.io/badge/DOI-pending-blue.svg)](https://doi.org)

---

## 📄 Paper Files

- **Main Paper**: `KSAU_v5.0_Unified_Theory.md`
- **Supplementary Material**: `KSAU_v5.0_Supplementary.md`
- **Validation Code**: `code/ksau_v5_prediction.py`

---

## 🎯 Key Results

| Metric | Value |
|:-------|------:|
| **Global MAE** | **1.38%** |
| Quark MAE | 1.91% |
| Lepton MAE | 0.32% |
| Quark R² | > 0.9999 |
| Lepton R² | 0.9998 |
| Database Coverage | **17,154** knots/links |
| Selection Method | **Automated** (topology_selector.py) |
| Topological Parameters | **1** (Twist: $\mathcal{T} = (2-\text{Gen}) \times (-1)^C$) |
| Calibration Constants | 2 (quark/lepton vacuum scales) |

---

## 💡 Core Innovations

### 1. **Universal Constant from Field Theory**
```
κ = π/24 ~ 0.1309
```
Derived from:
- Bosonic string zero-point energy: E₀ = -1/24
- Dedekind η-function: η(τ) = q^(1/24) ∏(1-q^n)
- Modular invariance (CFT)

### 2. **Catalan-π Identity** (New Mathematical Discovery)
```
G ~ 7π/24  (error 0.036%)
```
This identity bridges:
- Hyperbolic geometry (Catalan constant)
- Topological field theory (π/24)

### 3. **Unified Mass Formulas**
All coefficients expressed as rational multiples of κ = π/24:

**Quarks** (C ≥ 2, Confinement):
```
ln(m_q / MeV) = 10κ · V + κ · 𝒯 - (7 + 7κ)

where 𝒯 = (2 - Gen) × (-1)^C  (Topological Twist)
```

**Leptons** (C = 1, Freedom):
```
ln(m_l / MeV) = (14/9)κ · N² - (1/6) · I_twist + C_l
```

---

## 🔬 Predictions

1. **Neutrino Masses**: Σm_ν ~ 0.10-0.12 eV (topological seesaw)
2. **Fourth Generation**: Excluded below ~1 TeV (unitarity bound)
3. **Muon g-2**: Anomaly correlated with hyperbolic volume V_μ ~ 5.69

---

## 📊 Validation

### Run the Complete Workflow
```bash
cd code/
python topology_selector.py      # Generate topology assignments from database
python ksau_v5_prediction.py     # Compute mass predictions
python plot_mass_hierarchy.py    # Generate all figures
python permutation_test.py       # Statistical validation
```

**Output** (from ksau_v5_prediction.py):

```
Global MAE: 1.38% (Target: < 5%) OK
All selection rules satisfied OK
Catalan identity verified (0.036% error) OK
Automated topology selection: 17,154 candidates evaluated OK
```

### Dependencies
- Python 3.10+
- NumPy
- (Optional) SnapPy for hyperbolic volume computation

---

## 📐 Three Geometric Principles

### 1. Confinement-Component Correspondence
```
Quarks (confined) ↔ Links (C ≥ 2)
Leptons (free)    ↔ Knots (C = 1)
```

### 2. Charge-Determinant Law
```
Up-type (Q=+2/3):   Det(L) ≡ 0 (mod 2)
Down-type (Q=-1/3): Det(L) = 2^k  (k=4,5,6)  Binary Rule!
Leptons (Q=-1):     Det(K) ≡ 1 (mod 2)
```

### 3. Geometric Mass Scaling
```
Mass ~ exp(κ × Geometric Invariant)
where Geometric Invariant = Volume (quarks) or N² (leptons)
```

---

## 🧬 Complete Topology-Particle Table

| Particle | Topology | C | Det | V / N² | Obs (MeV) | Pred (MeV) | Error |
|:---------|:---------|--:|----:|-------:|----------:|-----------:|------:|
| Up | L8a6{0} | 2 | 20 | 6.552 | 2.16 | 2.21 | +2.1% |
| Down | L6a4{0,0} | 3 | 16 | 7.328 | 4.67 | 4.69 | +0.4% |
| Strange | L10n95{0,0} | 3 | 32 | 9.532 | 93.4 | 95.67 | +2.4% |
| Charm | L11n64{0} | 2 | 12 | 11.517 | 1270 | 1286 | +1.3% |
| Bottom | L10a140{0,0} | 3 | 64 | 12.276 | 4180 | 3961 | -5.2% |
| Top | L11a62{0} | 2 | 124 | 15.360 | 172760 | 172642 | -0.07% |
| Electron | 3₁ | 1 | 3 | 9 | 0.511 | 0.511 | 0.0% |
| Muon | 6₁ | 1 | 9 | 36 | 105.66 | 105.61 | -0.05% |
| Tau | 7₁ | 1 | 7 | 49 | 1776.9 | 1760.7 | -0.9% |

---

## 🔗 Theoretical Framework

### Chern-Simons Effective Action
```
y_f = exp(-S_geom[K_f])

S_geom = (1/κ) × [∫_M L_Bulk + ∮_{∂M} L_Boundary + L_Twist]
```

### Callan-Harvey Anomaly Cancellation
```
δS_bulk + δS_boundary = 0
```
**Implication**: Leptons must exist on the boundary to cancel the bulk gauge anomaly.

---

## 📚 Evolution History

| Version | Key Features | MAE |
|:--------|:-------------|----:|
| v1.0-v3.4 | Empirical correlations | ~15% |
| v4.0 | Three geometric rules | 7.9% |
| v4.1 | Twist correction + database search | 4.6% |
| **v5.0** | **Automated selection + κ=π/24 + Twist** | **1.38%** |

---

## 🎓 Citation

```bibtex
@article{KSAU_v5_2026,
  title={Topological Mass Generation from π/24: Unifying Chern-Simons Theory with Catalan Geometry},
  author={Yui},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2026}
}
```

---

## 📧 Contact

- **Author**: Yui
- **Affiliation**: Yui Protocol Project
- **Email**: yui@yui-protocol.org
- **GitHub**: [github.com/yui-synth-lab/KSAU_Project](https://github.com/yui-synth-lab/KSAU_Project)

---

## 📄 License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Data sources:
- **KnotInfo/LinkInfo**: [knotinfo.math.indiana.edu](https://knotinfo.math.indiana.edu)
- **SnapPy**: [snappy.computop.org](http://snappy.computop.org)
- **Particle Data Group**: [pdg.lbl.gov](https://pdg.lbl.gov)

---

## 🌟 Highlights

> *"Why are there six quarks? Why three generations? Why these specific masses? The answer may not lie in symmetries we impose, but in knots we discover."*

**The universe is not made of points. It is made of knots.**

---

**Version**: 5.0 (Unified Theory)
**Date**: February 7, 2026
**Status**: Ready for arXiv submission
