# KSAU v3.4 Analysis Supplement: Uniqueness & Robustness

**Date:** 2026-02-06
**Version:** 3.4 Supplement
**Code Reference:** `v3.3/code/ksau_v3_4_robustness.py`

## 1. Top-5 Candidates Analysis (Uniqueness)
The following tables list the top 5 topological candidates for each quark slot when varying one quark at a time (holding others fixed to v3.4 assignment). Lower MAE indicates a better fit.

### Up Quark (Comp=2)
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L7a5$** | 6.5990 | 8.38 | **Selected** |
| 2 | $L11n136$ | 6.5938 | 8.49 | |
| 3 | $L10n54$ | 6.7552 | 8.52 | |

### Down Quark (Comp=3)
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L6a4$** | 7.3277 | 8.38 | **Selected** |
| 2 | $L8n5$ | 7.3277 | 8.38 | Degenerate vol |

### Strange Quark (Comp=3)
*Note: This corrects the v3.3 selection ($L11n345$).*
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L10n95$** | 9.5319 | 8.38 | **Selected** |
| 2 | $L11n419$ | 9.5034 | 8.52 | |
| 3 | $L11n345$ | 9.4919 | 8.77 | (v3.3 Choice) |

### Charm Quark (Comp=2)
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L11n64$** | 11.5171 | 8.38 | **Selected** |
| 2 | $L11n52$ | 11.4972 | 8.86 | |

### Bottom Quark (Comp=3) - **Attention Needed**
The robustness check reveals a potential alternative that fits *better* than the v3.3/v3.4 default ($L10a141$, Vol=12.28).
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L10a146$** | 12.48 | 4.74 | **Better Fit?** |
| - | $L10a141$ | 12.28 | 8.38 | **Selected** |

*Note: The script indicates $L10a146$ reduces global MAE to 4.74%. This requires further physical justification before switching, as $L10a141$ may have other properties (symmetry).*

### Top Quark (Comp=2) - **Attention Needed**
Similarly, a better fit exists for Top.
| Rank | Link Name | Volume | MAE (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **$L10a107$** | 15.14 | 6.93 | **Better Fit?** |
| - | $L11a62$ | 15.36 | 8.38 | **Selected** |

---

## 2. Statistical Robustness (v3.4 Assignment)

### Bootstrap Analysis (N=10,000)
*   **Slope ($\gamma$):** $1.308 \pm 0.029$ (95% CI)
*   **Intercept ($b'$):** $-7.915 \pm 0.307$ (95% CI)
*   **MAE:** $8.38\% \pm [7.85\%, 14.31\%]$ (95% CI)

### Leave-One-Out (LOO) Cross-Validation
*   **LOO MAE:** 14.90%
*   **Prediction Errors:**
    *   Top Quark: +34.28% (Hardest to predict)
    *   Charm: +0.02% (Extremely precise)
    *   Strange: +1.68% (Highly robust)

## 3. Conclusion
The v3.4 assignment (switching Strange to $L10n95$) is statistically robust and stable. However, the top-k analysis suggests that **Bottom ($L10a146$)** and **Top ($L10a107$)** assignments could be further optimized to halve the global error. For v3.4, we stick to the conservative update (Strange only) to maintain continuity, but label $b/t$ updates as "v4.0 candidates".
