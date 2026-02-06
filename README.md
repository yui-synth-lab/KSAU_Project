# KSAU Project: Geometric Origin of Fermion Flavor and Mass Hierarchy

**Latest Version:** 3.3 (Component-Charge Symmetry)  
**Author:** Yui  
**Affiliation:** Yui Protocol Project  
**License:** CC BY 4.0  
**Significance:** >5σ (Statistical Discovery Level)

---

## Overview
KSAU (Knot-Structure-At-Universal) Theory is a unified topological framework that derives the fundamental properties of fermions—mass, electric charge, and weak isospin—from the geometry of 3-manifold complements. 

## Key Discovery in v3.3: Component-Charge Symmetry
A major breakthrough in the latest version is the establishing of the **Component-Charge Symmetry**, which links the number of components ($C$) in a link to its gauge charge:
*   **1 Component (Knot)**: Leptons (Charge -1, $I_3 = -1/2$ or $0$)
*   **2 Components (Link)**: Up-type Quarks (Charge +2/3, $I_3 = +1/2$)
*   **3 Components (Link)**: Down-type Quarks (Charge -1/3, $I_3 = -1/2$)

## Directory Structure

```text
KSAU_Project/
├── KSAU_v3_Roadmap.md      # Roadmap for TQFT integration
├── data/                   # [Required] Global link database (linkinfo_data_complete.csv)
├── v3.3/                   # The Discovery Version deliverables
│   ├── KSAU_v3.3_Main_Paper.md
│   ├── code/               # Python scripts (Fixed for portability)
│   │   ├── brute_force_v3_3_compliant.py
│   │   ├── generate_figures_from_data.py
│   │   └── ksau_full_9_particle_verification.py
│   ├── data/               # results output location
│   └── figures/            # High-res publication plots
└── archive/                # Past versions
```

## Prerequisites
To run the verification scripts, you need Python 3.x and the following libraries:
```bash
pip install pandas numpy matplotlib scipy tqdm
```

## Reproducibility Instructions

### 1. Unified Verification (Fast)
To see the predicted masses for all 9 particles and calculate the MAE:
```bash
python v3.3/code/ksau_full_9_particle_verification.py
```

### 2. Statistical Significance Test (Monte Carlo)
To verify that the model is not due to random chance within the component-charge restricted space:
```bash
# This generates 10,000 random trials (approx. 1 min)
python v3.3/code/brute_force_v3_3_compliant.py
```

### 3. Visualization
To generate the statistical significance plot from the actual data generated in step 2:
```bash
python v3.3/code/generate_figures_from_data.py
```

## Performance Summary
*   **Global MAE:** 8.33%
*   **Statistical Significance:** $p < 0.00001$ ($>5\sigma$)
*   **Highest Precision:** Charm (+0.79%), Strange (-2.87%), Up (-4.24%)

---
**Contact:** https://github.com/yui-synth-lab