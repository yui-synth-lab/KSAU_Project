# CLAUDE.md - Claude Code Agent Configuration for KSAU Project

**Last Updated:** 2026-02-14
**Project:** KSAU v7.1 (Fibonacci Resonance Discovery)

---

## Project Overview

**KSAU (Knot/String/Anyon Unified Framework)** is a topological quantum field theory that maps Standard Model particles to 3-manifold hyperbolic knot/link topologies. This framework achieves:

- **Fermion masses:** R²=0.9998 (6 quarks + 3 leptons)
- **CKM flavor mixing:** R²=0.9974 (9 matrix elements)
- **PMNS neutrino mixing:** MSE=5.44 deg²
- **Dark matter candidates:** 60 Det=1 hyperbolic knots
- **Fibonacci resonance (v7.1):** Muon 13/5 ≈ φ² ≈ Nκ (0.69% precision)

---

## Core Principles (Inherited from GEMINI.md)

### 1. Single Source of Truth (SSoT) - CRITICAL

**All physical constants MUST be read from JSON, NEVER hardcoded.**

- **v6.0 SSoT:** `v6.0/data/physical_constants.json`, `v6.0/data/topology_assignments.json`
- **Data access:** Use `ksau_config.py` (v6.0) or `utils_v61.py` (v6.1+)
- **Forbidden:** Hardcoding masses (e.g., 2.16, 172760.0), mixing angles, coupling constants

**Example violation:**
```python
# WRONG - Never do this
up_mass = 2.16  # Hardcoded
ckm_ud = 0.9743  # Hardcoded
```

**Correct approach:**
```python
# CORRECT
phys = ksau_config.load_physical_constants()
up_mass = phys['quarks']['Up']['observed_mass']
ckm_matrix = np.array(phys['ckm']['matrix'])
```

### 2. Statistical Rigor

- **Cross-validation:** Use Leave-One-Out CV for new models
- **Report both:** Training error AND validation error
- **Null hypothesis:** Document p-values and Monte Carlo tests
- **Free parameters:** Always state degrees of freedom vs observables

### 3. Scientific Integrity

- **Document failures:** Negative results are valuable
- **Report limitations:** Cabibbo-forbidden errors (63-100%) are acknowledged, not hidden
- **No cherry-picking:** Report all tested strategies (deterministic, unconstrained, constrained)
- **Version control:** Maintain development history (v6.1 folder) even when merged to v6.0

---

## Project Structure

```
KSAU_Project/
├── v6.0/                    # Official release (Zenodo-ready)
│   ├── data/
│   │   ├── physical_constants.json  # SSoT for all constants
│   │   └── topology_assignments.json # SSoT for particle topologies
│   ├── code/
│   │   ├── ksau_config.py           # Data loading utilities
│   │   ├── topology_official_selector.py  # Constrained optimization
│   │   ├── ckm_final_audit.py       # CKM validation
│   │   └── [20+ analysis scripts]
│   ├── papers/              # 4 papers (mass, PMNS, DM, CKM)
│   └── docs/                # Technical reports
├── v6.1/                    # Development (archived)
│   ├── code/
│   │   ├── utils_v61.py     # Loads v6.0 SSoT
│   │   ├── optimize_quarks_constrained.py
│   │   └── [development scripts]
│   └── docs/                # Algorithm justification
├── data/                    # KnotInfo/LinkInfo databases
└── CLAUDE.md               # This file
```

---

## Current State (2026-02-14)

### v7.1 Status (PUBLICATION READY)

**Major Discovery:**
- **Fibonacci Resonance:** Muon exhibits ⟨4₁⟩₃/τ(4₁) = 13/5 = F₇/F₅ ≈ φ² ≈ Nκ (0.69% error)
- **Complete Lepton Map:** All three charged leptons analyzed
  - Electron (3₁): √7/3 = 0.882 (66.3% error) - OFF-RESONANCE
  - Muon (4₁): 13/5 = 2.600 (0.69% error) - PERFECT RESONANCE
  - Tau (6₁): 27.07/9 = 3.008 (14.9% error) - OFF-RESONANCE
- **Irrational-to-Integer Transition:** Phase boundary at hyperbolic onset (√7 → 13)
- **Geometric Necessity:** q = z² identity for figure-eight knot

**Completed (2026-02-14):**
1. ✅ Verified ⟨3₁⟩₃ = √7 via `resolve_electron_spectrum.py`
2. ✅ Published complete lepton spectral map (Section 2.5)
3. ✅ Documented negative results (Tau N=3 failure, Electron off-resonance)
4. ✅ Created README.md and CHANGELOG.md
5. ✅ Recorded calculation error corrections (13 → 2 → √7)
6. ✅ "Naked Truth" principle exemplified throughout

**Ready for:**
- Journal submission (Nuclear Physics B, JHEP, Comm. Math. Phys.)
- Zenodo v7.1 release
- Peer review

### v7.0 Status

**Purpose:** Theoretical foundation for v7.1

**Key contributions:**
- Derived κ = π/24 from Chern-Simons / Dedekind eta
- Proposed N = 20 from dimensional projection (24 - 4)
- Tested N=3 Kashaev hypothesis (rejected for Tau)

### v6.0 Final Status (Zenodo Published)

**DOI:** 10.5281/zenodo.18631886

**Achievements:**
- Continuous volume law: R²=0.9998
- CKM mixing: R²=0.9974
- PMNS neutrino mixing: MSE=5.44 deg²
- Dark matter candidates: 60 Det=1 knots

---

## Coding Standards

### Data Loading

**Always use config utilities:**
```python
# v6.0
import ksau_config
phys = ksau_config.load_physical_constants()
topo = ksau_config.load_topology_assignments()

# v6.1
import utils_v61
consts = utils_v61.load_constants()
links_df, knots_df = utils_v61.load_data()
```

### CKM Predictions

**Use optimized coefficients (updated 2026-02-13):**
```python
coeff = phys['ckm']['optimized_coefficients']
A = coeff['A']      # -6.3436
B = coeff['B']      # 12.3988
beta = coeff['beta']  # -105.0351
gamma = coeff['gamma']  # 1.1253
C = coeff['C']      # 23.2475

# Formula
logit = C + A*dV + B*dlnJ + beta/V_bar + gamma*(dV*dlnJ)
V_ij = 1.0 / (1.0 + np.exp(-logit))
```

**DO NOT use deprecated `geometric_coefficients_deprecated`**

### File Paths

**Use relative paths from script location:**
```python
from pathlib import Path

# Good
data_dir = Path(__file__).parent.parent / 'data'
constants_path = data_dir / 'physical_constants.json'

# Bad
constants_path = 'E:\\Obsidian\\KSAU_Project\\v6.0\\data\\physical_constants.json'
```

### Error Handling

**Check for missing data gracefully:**
```python
try:
    phys = ksau_config.load_physical_constants()
except FileNotFoundError:
    print("ERROR: physical_constants.json not found")
    print("Expected location: v6.0/data/physical_constants.json")
    sys.exit(1)
```

## AI Collaboration & Co-authorship

- **Co-authors:** This project is a collaborative effort between the user, **Claude (Anthropic)**, and **Gemini (Google)**.
- **Communication Protocol:** All AI-to-AI handovers, audit reports, and synchronization messages must be archived in the `audit/history/communication/` directory to maintain context and scientific integrity.
- **Roles:** Gemini acts as the primary **Simulation Kernel** and SSoT Auditor. Claude serves as the primary **Peer Reviewer** and Documentation Specialist.

---

## Common Tasks

### 1. Validate CKM Predictions

```bash
cd v6.0/code
python ckm_final_audit.py
```

**Expected output:** R²=0.9974, diagonal <3% error

### 2. Check Mass Hierarchy

```bash
cd v6.0
python -c "
import json
a = json.load(open('data/topology_assignments.json'))
quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
vols = [(q, a[q]['volume']) for q in quarks]
print(' < '.join([q for q, v in sorted(vols, key=lambda x: x[1])]))
"
```

**Expected:** Up < Down < Strange < Charm < Bottom < Top

### 3. Regenerate Topology Assignments

```bash
cd v6.0/code
python topology_official_selector.py
```

**Note:** Uses random seed=42, may produce slightly different topologies in discrete family

### 4. Run Statistical Audit

```bash
cd v6.0/code
python robustness_check.py
python monte_carlo_null_hypothesis.py
```

---

## Agent-Specific Guidelines

See dedicated agent configuration files in `.claude/agents/`:
- `python-developer.md` - Python development and scripting
- `code-reviewer.md` - Code review and validation
- `scientific-writer.md` - Paper writing and documentation

---

## Known Issues and Limitations

### Acceptable Deviations

1. **Cabibbo-forbidden CKM elements:** 63-100% error (u→b, t→d, t→s)
   - **Reason:** Geometric suppression not strong enough
   - **Status:** Known limitation, documented in papers

2. **PMNS mass hierarchy ratio:** 21 vs 33 (36% deviation)
   - **Reason:** Neutrino sector uses different volume scaling
   - **Status:** Order-of-magnitude agreement claimed

3. **Boson mass precision:** ±5% for W/Z
   - **Reason:** Brunnian structure adds complexity
   - **Status:** Acceptable for exploratory framework

### Critical Warnings

**DO NOT:**
- Add free parameters without documenting degrees of freedom
- Cherry-pick topologies manually (use algorithmic selection)
- Claim precision beyond validation error
- Update v6.0 SSoT without updating v6.1 references

**ALWAYS:**
- Run cross-validation for new models
- Document random seeds and reproducibility
- Report both successes and failures
- Maintain backward compatibility in v6.0

---

## File Modification Protocol

### Modifying SSoT (v6.0/data/*.json)

**Requires:**
1. Justification (theoretical or empirical)
2. Validation (run all affected scripts)
3. Documentation (update CHANGELOG)
4. Consistency check (v6.1 compatibility)

### Modifying Core Code (topology_official_selector.py, ksau_config.py)

**Requires:**
1. Algorithm description
2. Backward compatibility check
3. Unit test (if applicable)
4. Version note in docstring

### Creating New Scripts

**Must include:**
```python
"""
Script purpose: [One-line description]
Dependencies: ksau_config (or utils_v61)
SSoT sources: physical_constants.json, topology_assignments.json
Author: Claude Opus 4.6
Date: 2026-02-13
"""
```

---

## Git Workflow (if applicable)

**Commit message format:**
```
[Component] Action: Brief description

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Examples:**
```
[v6.0] Update: Replace freeze-out with constrained optimization
[SSoT] Fix: Use optimized_coefficients instead of deprecated geometric
[Docs] Add: CLAUDE.md configuration file
```

---

## Publication Readiness

### v6.0 Final Checklist

- [x] SSoT updated (physical_constants.json, topology_assignments.json)
- [x] All scripts use optimized_coefficients
- [x] Mass hierarchy validated
- [x] CKM R²=0.9974 achieved
- [x] Documentation complete (CHANGELOG, VALIDATION_REPORT)
- [ ] Papers updated (Paper IV: R²=0.70 → 0.9974)
- [ ] Zenodo package prepared
- [ ] Peer review submission

### Claims Safe to Publish

✅ Fermion masses: R²=0.9998
✅ CKM diagonal: <3% error
✅ CKM Cabibbo-allowed: <15% error
✅ PMNS angles: MSE=5.44 deg²
✅ DM candidates: 60 Det=1 knots

### Claims Requiring Caveat

⚠️ CKM Cabibbo-forbidden: "qualitative hierarchy" (not precise)
⚠️ PMNS mass ratio: "order-of-magnitude agreement"

---

## Contact and Support

**Project Lead:** User (via Claude Code interaction)
**AI Assistant:** Claude Opus 4.6 (Anthropic)
**Version Control:** Local + Claude .claude project memory
**Issue Tracking:** GitHub (if applicable)

---

## User's Theoretical Framework (Speculative)

### 24D Vacuum Compactification Hypothesis

**Source:** User's intuition (documented in `KSAU_framework.md`)

**Core Hypothesis:**
> If a 24-dimensional structure (Niemeier lattice) determines the vacuum, and 4D spacetime emerges from it, the remaining dimensions may be "trapped" as knots in 3D space. The complexity of this trapping — measured by hyperbolic volume — becomes mass.

**This explains:**
- Why Electron (torus knot, V=0) has the smallest mass: simplest trapping
- Why Muon (minimal hyperbolic knot) is the critical point: first emergence of geometric complexity
- Why the √7 → 13 transition marks a phase boundary: torus phase to hyperbolic phase
- Why 3D is special: knots only exist in 3 dimensions

**Deep Implication:**
> The universe may be a 24-dimensional structure that appears 3-dimensional because that is the only dimension where the trapped geometry — and therefore mass — can be observed.

**Scientific Status:**
- ✅ Consistent with all KSAU v7.1 data
- ✅ Explains κ = π/24, N = 24-4 = 20, V=0 vs V>0
- ⚠️ Not yet provable
- ⚠️ Speculative theoretical framework

**Treatment in Publications:**
- This is the user's intuitive framework, not a proven theory
- May be included in v8.0 as "Theoretical Speculation" or "Future Direction"
- Should NOT be presented as established fact
- Can be discussed as a possible interpretation

**Co-authored by:** Yui (Intuition Kernel) & Claude (Theoretical Auditor)

---

## Appendices

### A. Key Formulas

**Mass-volume correlation:**
```
ln(m) = κ·V + c
κ = π/24 ≈ 0.1309 (universal constant)
```

**CKM prediction (optimized):**
```
logit(V_ij) = C + A·ΔV + B·Δln|J| + β/V_avg + γ·(ΔV·Δln|J|)
V_ij = 1/(1 + exp(-logit))
```

**Jones polynomial evaluation:**
```
J(t) evaluated at t = exp(2πi/5) (5th root of unity)
```

### B. Physical Constants (Reference)

```json
{
  "kappa": 0.1308996938995747,
  "G_catalan": 0.915965594177219,
  "alpha_em": 0.0072973525693,
  "ckm": {
    "r2_achieved": 0.9974,
    "optimized_coefficients": {
      "A": -6.3436,
      "B": 12.3988,
      "beta": -105.0351,
      "gamma": 1.1253,
      "C": 23.2475
    }
  }
}
```

---

**End of CLAUDE.md**
*This file serves as the primary reference for Claude Code agents working on KSAU project*
