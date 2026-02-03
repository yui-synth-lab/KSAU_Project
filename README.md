# KSAU Project: Topological Link Theory of Quark Masses and CKM Matrix

**Version:** 2.2 (Unified Framework)
**Author:** Yui¹†
**Affiliation:** ¹ Yui Protocol Project
**License:** CC BY 4.0

---

## Overview
KSAU (Knot-Synchronization-Adhesion Unified) Theory is a theoretical physics project that describes the mass hierarchy and mixing phenomena (CKM/PMNS matrices) of elementary particles as geometric properties of topological defects (knots and links) in spacetime manifolds.

This repository archives the results (papers, analysis codes, datasets) of **KSAU v2.2**, as well as past versions (v1.4, v1.6).

## Directory Structure

```text
KSAU_Project/
├── KSAU_v3_Roadmap.md      # Theoretical roadmap for the next version (v3.0)
├── v2.2/                   # [Latest] v2.2 deliverables (Quark & Link Theory)
│   ├── KSAU_v2_Comprehensive_Paper.md  # Integrated paper (Mass formula, CKM derivation)
│   ├── KSAU_v2_Theoretical_Supplement.md # Theoretical supplement (Mathematical definitions, numerical verification)
│   ├── code/               # Python scripts for analysis
│   │   ├── analysis_v2_stats.py        # Statistical verification of mass formula
│   │   ├── analysis_v2_quark.py        # Derivation of CKM matrix
│   │   ├── berry_plot_refined.py       # Numerical simulation of Berry phase
│   │   └── berry_plot.py
│   ├── data/               # Datasets for analysis
│   │   ├── quark_link_candidates.csv   # Parameters for quark link candidates
│   │   └── quark_link_signatures_update.csv # Signature data
│   └── figures/            # Generated figures
│       ├── v2_stat_analysis.png        # Statistical analysis plot of mass fit
│       ├── top_quark_berry_spectrum.png # Visualization of spectral flow
│       ├── v2_ckm_comparison.png       # Heatmap of CKM matrix
│       └── ...
└── archive/                # Past versions
    ├── v1.6.1/             # v1.6.1 (Lepton & Knot Theory)
    │   └── KSAU_v1.6.1.md
    └── v1.4.1/             # v1.4.1 (Early Draft)
        └── KSAU_v1.4.1.md
```

## Key Results of v2.2

1.  **Mass-Volume Law**: Statistically demonstrated that quark masses follow an exponential function of the hyperbolic volume of links ($R^2 \approx 0.95$).
2.  **CKM Matrix Derivation**: Derived mixing angles from first principles based on topological distances between links.
3.  **CP Violation Origin**: Discovered strong chirality (Signature=6) in the top quark candidate ($L10a142$) and identified the geometric origin of the CP phase.

## Usage

The scripts in `v2.2/code/` run on Python 3.x and the following libraries:
`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `sklearn`, `statsmodels`

```bash
cd v2.2
python code/analysis_v2_stats.py
python code/berry_plot_refined.py
```

---
**Contact:** https://github.com/yui-synth-lab
**DOI:** [Zenodo DOI will be assigned]