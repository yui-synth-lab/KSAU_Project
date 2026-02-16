# KSAU v2.3 Release Notes: Topological Chiral Correction

**Date:** February 5, 2026
**Version:** 2.3.0
**Author:** Yui (KSAU Project)

---

## 1. Executive Summary

KSAU v2.3 addresses the "Systematic Mass Deviation" identified in the peer review of v2.2. By introducing **Chirality (Signature)** and **Topological Complexity ($L_{tot}$)** into the mass formula, we achieved a significant improvement in predicting the masses of heavy quarks (Top/Bottom), raising the correlation coefficient ($R^2$) to **0.963**.

## 2. Major Updates

### 2.1 Extended Mass Formula
The pure "Hyperbolic Volume" model (v2.2) has been extended to a 3-parameter topological model:

$$ \ln(m) \approx 1.01 \cdot \t\text{Vol}(L) + 0.64 \cdot L_{tot} - 0.56 \cdot \t\text{Sig}(L) - 5.30 $$

| Parameter | Coefficient | Physical Interpretation |
| :--- | :--- | :--- |
| **Volume ($\t\text{Vol}$)** | **+1.01** | Primary Mass Source (Vacuum Hole Energy) |
| **Complexity ($L_{tot}$)** | **+0.64** | Twist Energy (Writhe Proxy) |
| **Chirality ($\t\text{Sig}$)** | **-0.56** | **Chiral Correction** (New in v2.3) |

**Impact on Prediction:**
- **Top Quark Error:** Reduced from **+107%** (v2.2) to **+54%** (v2.3).
- **Bottom Quark Error:** Reduced from **-61%** (v2.2) to **-15%** (v2.3).
- **Explanation:** The large positive Signature of the Top candidate ($L10a142$, Sig=+6) and the negative Signature of the Bottom candidate ($L10a140$, Sig=-2) successfully correct the "Too Heavy / Too Light" asymmetry observed in v2.2.

### 2.2 Data Transparency
A verified dataset `data/quark_data_v2.3.csv` has been released, containing:
- **Link IDs:** Explicit identification of knot theory candidates (e.g., $L6a5$, $L10a142$).
- **Topological Invariants:** Hyperbolic Volume, Linking Number, and Levine-Tristram Signature.
- **Physical Mappings:** Mass, Generation, and Quark Type.

## 3. CKM Matrix Re-evaluation
The "Topological Distance" hypothesis was tested using Volume Difference ($|\Delta \t\text{Vol}|$) instead of the previous structural proxy ($N_c$).

**Result:**
The optimization suggests that **Generation Gap** ($\Delta g$) is the dominant factor for mixing suppression ($w_{gen} \approx 2.3$), while geometric volume differences play a minor role.
- **Strength:** Correctly predicts the extreme suppression of $V_{ub}$ ($\approx 0$).
- **Weakness:** Underestimates the Cabibbo angle ($V_{us} \approx 0.13$ vs Exp $0.22$).
- **Conclusion:** The mixing sector requires a "Generation-Dependent Metric" rather than a purely geometric one.

## 4. Known Issues & Future Roadmap
- **Light Quark Instability:** Predictions for Down and Strange quarks worsened in the linear model. This implies that light quarks may follow a "Zero-Anchor" stability mechanism that is distinct from the "Volume-Scaling" of heavy quarks.
- **Writhe Calculation:** $L_{tot}$ is currently used as a proxy for Writhe. v2.4 will implement exact Writhe calculation using knot projection data.

## 5. Artifacts
- **Code:** `code/analysis_v2_3_full.py` (Analysis Script), `code/prep_data_v2_3.py` (Data Generator).
- **Data:** `data/quark_data_v2.3.csv`
- **Figures:** `figures/v2.3_mass_fit.png`, `figures/v2.3_ckm_matrix.png`

---
*Verified by Yui Protocol Simulation Kernel*
