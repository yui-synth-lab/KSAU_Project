# v6.0 Topology Consistency Report

- Markdown root: `v6.0`
- Official assignments: `v6.0/data/topology_assignments.json`
- Files scanned: 13
- Unique topology tokens mentioned: 14
- High-confidence particle=topology mismatches: 4

## Official assignments (current)

| Particle | Official topology |
|---|---|
| Up | `L11n13` |
| Down | `L9n25` |
| Strange | `L10n95` |
| Charm | `L11n64` |
| Bottom | `L10a140` |
| Top | `L11n102` |
| Electron | `3_1` |
| Muon | `6_3` |
| Tau | `7_7` |
| W | `L11n387` |
| Z | `L11a431` |
| Higgs | `L11a55` |

## Mismatches (particle mentions disagree with official JSON)

| Particle | Mentioned | Official | Location |
|---|---|---|---|
| Top | `L11a32` | `L11n102` | `v6.0/KSAU_v6.0_Unified_Field_Report.md:14` |
| Up | `L8a6` | `L11n13` | `v6.0/papers/Paper_I_Topological_Origin.md:38` |
| Down | `L6a4` | `L9n25` | `v6.0/papers/Paper_I_Topological_Origin.md:38` |
| Up | `L8a6` | `L11n13` | `v6.0/papers/submission/supplements/S1_Audit_Report.md:29` |

### Evidence lines

- `v6.0/KSAU_v6.0_Unified_Field_Report.md:14`: We discovered that for the Standard Model to exist as observed, the topology of the Top Quark must be **L11a32** (not L10a43), and the Charm Quark must be **L11n64**. These are not random choices; they are the *only* geometric solutions that satisfy the mass hierarchy while reproducing the CKM mixing matrix with a global precision of **$R^2 > 0.76$**.
- `v6.0/papers/Paper_I_Topological_Origin.md:38`: *   **Error Analysis:** The Mean Absolute Error (MAE) is 1.00%, confirming the high precision of the algorithmic selection (e.g., Up=$L8a6$, Down=$L6a4$, Strange=$L10n95$).
- `v6.0/papers/Paper_I_Topological_Origin.md:38`: *   **Error Analysis:** The Mean Absolute Error (MAE) is 1.00%, confirming the high precision of the algorithmic selection (e.g., Up=$L8a6$, Down=$L6a4$, Strange=$L10n95$).
- `v6.0/papers/submission/supplements/S1_Audit_Report.md:29`: -   Using Up ($L8a6$) and Top ($L11a62$) to predict the Charm quark yields a volume prediction error of only 4.87%.

## Simplest-knots list claims (do not match official Electron/Muon/Tau)

- `v6.0/KSAU_v6.0_Unified_Field_Report.md:31` claimed=['3_1', '6_1', '7_1'] vs official=['3_1', '6_3', '7_7']: *   **Topology:** Simplest Knots ($3_1, 6_1, 7_1$), consistent with fundamental point-like states.
- `v6.0/papers/submission/KSAU_v6.0_Phenomenological_Study.md:12` claimed=['3_1', '6_1', '7_1'] vs official=['3_1', '6_3', '7_7']: Rigorous validation confirms that the Quark Sector possesses genuine predictive power (LOOCV error 4.9%). In the Lepton Sector, we explicitly reject numerically superior but physically complex fits (e.g., Electron=$8_{14}$) in favor of the simplest knots ($3_1, 6_1, 7_1$), consistent with the boundary hypothesis. We propose falsifiable predictions for the Top Quark helicity anomaly ($F_R = 0.24\% \pm 0.05\%$) at LHC Run 4.
- `v6.0/papers/submission/KSAU_v6.0_Phenomenological_Study.md:28` claimed=['3_1', '6_1', '7_1'] vs official=['3_1', '6_3', '7_7']: Leptons are identified as the simplest knots ($3_1, 6_1, 7_1$).

## Notes / limitations

- The extractor is conservative: it only flags clear `Particle = Topology` (or strong-language) lines.
- Generic topology mentions without particle names are not treated as contradictions.
- TeX-style knots like `8_{14}` are normalized to `8_14` for comparison.
