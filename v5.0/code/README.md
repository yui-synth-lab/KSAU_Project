# KSAU v5.0 Code Repository

This directory contains the computational core of the KSAU v5.0 theory. The pipeline is designed to be **fully data-driven and algorithmic**, ensuring reproducibility and eliminating arbitrary "cherry-picking" of topological assignments.

## 🚀 Reproduction Pipeline

To reproduce all figures and results in the paper, execute the scripts in the following order:

### 1. Topological Identification (The "Selector")
The theory predicts particle topologies based on their mass and charge. This script applies the mass formula ($\ln(m) \sim 10\kappa V + \kappa \mathcal{T}$) and selection rules (determinant, components) to the entire knot database to find the physical solutions.

```bash
python topology_selector.py
```
*   **Input**: `../data/mass_data.csv` (Physics), `../../data/linkinfo_data_complete.csv` (Geometry)
*   **Output**: `../data/topology_assignments.json` (The theoretical predictions)

### 2. Statistical Robustness & Verification
Validates the selection against all other possible combinations in the database and computes precision metrics.

```bash
python brute_force_ab_test.py
python complexity_test.py
python verify_ksau_v5.py
```
*   **Input**: `../data/topology_assignments.json`, `../data/mass_data.csv`
*   **Output**: `../data/brute_force_ab_results.json`, Console Reports (MAE, R², Ranks)

### 3. Figure Generation
Generates high-resolution plots for the manuscript and supplementary materials.

```bash
python plot_mass_hierarchy.py
python plot_exhaustive_search.py
```
*   **Input**: `../data/topology_assignments.json`, `../data/brute_force_ab_results.json`
*   **Output**: `../figures/figure1-6.png`, `../figures/figureS1-S2.png`

---

## 📂 File Structure

| File | Description |
| :--- | :--- |
| `topology_selector.py` | **Core Algorithm.** Maps physical particles to knot topologies using mass formulas. |
| `verify_ksau_v5.py` | Calculates precision metrics (MAE) for the selected topologies. |
| `brute_force_ab_test.py` | Exhaustive search in Top-K subspace to prove statistical significance. |
| `complexity_test.py` | Proves KSAU is the global optimum under the **Minimal Complexity Principle**. |
| `plot_mass_hierarchy.py` | Generates all 6 main figures for the KSAU v5.0 manuscript. |
| `plot_exhaustive_search.py` | Generates distribution and complexity tradeoff plots using real data. |
| `prove_no_overfitting.py` | Analyzes search space constraints and topological quantization noise. |
| `catalan_pi24_verify.py` | Verifies the mathematical identity $G \approx 7\pi/24$. |
| `permutation_test.py` | Performs 100,000 permutations to calculate the p-value ($p < 8 \\times 10^{-5}$). |

## 📊 Data Sources

*   **Geometry**: Derived from **KnotInfo / LinkInfo** (Chaos et al., 2024 Snapshot).
*   **Physics**: PDG 2024 Mass values (contained in `mass_data.csv`).

## 🛠 Requirements

*   Python 3.8+
*   `pandas`, `numpy`, `matplotlib`, `scipy`

```bash
pip install pandas numpy matplotlib scipy
```
