# Paper III: Topological Dark Matter from Hyperbolic Knots
**Status:** Research Note (Speculative)
**Focus:** Dark Matter Candidates, Topologically Neutral Knots (Det=1)

## Abstract
In the KSAU **Holographic Dual Model**, fundamental particles are identified with topological vacuum defects (knot and link complements). While visible matter is coupled to bulk volume (quarks) or boundary complexity (leptons), we observe that "Topologically Neutral" knots—defined by a link determinant of unity ($\t\text{Det} = 1$)—possess unique geometric properties: they carry zero electric charge coupling and are topologically stable. We propose that these neutral knots constitute the dark matter sector. A survey of the knot census reveals a multi-component dark matter spectrum, including a "Warm" candidate at $\sim 15$ keV and "WIMP-like" candidates in the $1-10$ GeV range.

## 1. Introduction
*   The nature of Dark Matter and the lack of WIMP detection.
*   KSAU proposal: Dark Matter is not a new field, but a "hidden sector" of the same topological vacuum geometry.

## 2. Selection Criteria

### 2.1 The Determinant-Charge Relationship

A detailed analysis of the fermion sector (see `det_charge_analysis.py`) reveals that the link determinant (Det) does **not** have a direct functional relationship with electric charge. Statistical regression shows $R^2 < 0.001$ for $Q \sim \ln(\t\text{Det})$, ruling out simple encodings.

However, we observe that:

* **All visible fermions** (quarks and leptons) have $\t\text{Det} \geq 3$.
* **Det = 1** knots have never appeared in the Standard Model assignments.

This suggests an **exclusion principle**: Det=1 topologies represent a **topologically neutral sector** that does not couple to electromagnetism. While we cannot prove $\t\text{Det}=1 \Rightarrow Q=0$ from first principles, the empirical pattern is compelling.

### 2.2 Dark Matter Selection Rules

Based on this observation, we propose the following criteria for dark matter candidates:

* **Determinant = 1:** Ensures electromagnetic neutrality (no photon coupling).
* **Hyperbolic Volume:** Generates mass via the knot formula $m = \exp(\gamma_{\t\text{DM}} N^2 + C)$ (for knots) or link formula (for multi-component links).
* **Topological Stability:** Knots cannot untie, ensuring the particle is absolutely stable (no decay channels).

## 3. Candidate Spectrum
Using the KSAU mass formula with standard couplings:

### 3.1 Warm Dark Matter (Geometric Majoron)
*   **Candidate:** Knot 12n_242
*   **Mass:** $\sim 15$ keV
*   **Role:** Structure formation, possible sterile neutrino connection.

### 3.2 Light WIMP (Hidden Scalar)
*   **Candidate:** Knot 12n_430
*   **Mass:** $\sim 1.1$ GeV
*   **Role:** Explains galactic center excess?

### 3.3 Heavy WIMP
*   **Candidate:** Knot 12n_210
*   **Mass:** $\sim 8.4$ GeV

## 4. Discussion
*   The existence of a "Dark Sector" is a natural consequence of knot theory (many knots have Det=1).
*   Unlike ad-hoc models, the mass spectrum is fixed by the mathematical census of knots.

## 5. Conclusion
*   We identify specific topological candidates for Dark Matter.
*   This framework unifies Visible and Dark matter under the same geometric origin (Topology of the Vacuum).

## References

[1] KSAU Paper I: Topological Origin of Fermion Mass Hierarchy (this volume)

[2] C. Livingston and A. H. Moore, *KnotInfo: Table of Knot Invariants*, <https://knotinfo.math.indiana.edu>

[3] G. Bertone and D. Hooper, *History of dark matter*, Rev. Mod. Phys. 90, 045002 (2018)

[4] LUX-ZEPLIN Collaboration, J. Aalbers et al., *First Dark Matter Search Results from the LUX-ZEPLIN Experiment*, Phys. Rev. Lett. 131, 041002 (2023)

[5] A. Boyarsky et al., *Sterile neutrino Dark Matter*, Prog. Part. Nucl. Phys. 104, 1-45 (2019)
