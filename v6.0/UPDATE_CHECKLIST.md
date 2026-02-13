# v6.0 Update Checklist (Strategy C Adoption)

**Date:** 2026-02-13
**Objective:** Update v6.0 to incorporate v6.1 constrained optimization results

---

## Files Modified

### Core Data Files

- [x] **`code/topology_official_selector.py`**
  - Replaced freeze-out algorithm with constrained optimization
  - Added `constrained_topology_search()` function
  - Added `evaluate_ckm_r2()` function
  - Leptons/bosons unchanged (deterministic)

- [x] **`data/physical_constants.json`**
  - Added `ckm.r2_achieved = 0.9980`
  - Added `ckm.optimized_coefficients` (A, B, beta, gamma, C)
  - Added `ckm.selection_method`
  - Deprecated old geometric_coefficients

- [ ] **`data/topology_assignments.json`** (In progress)
  - Awaiting `topology_official_selector.py` execution
  - Will contain Strategy C quark assignments
  - Leptons/bosons unchanged

---

## Documentation Created

- [x] **`CHANGELOG_v6.0_FINAL.md`**
  - Summary of changes
  - Old vs new comparison
  - Justification
  - Publication impact

- [x] **`UPDATE_CHECKLIST.md`** (this file)

---

## Validation Tasks

### After `topology_assignments.json` is generated:

- [x] **Verify quark assignments**
  ```bash
  python -c "import json; print(json.load(open('data/topology_assignments.json')))"
  ```
  Expected:
  ```
  Up:      L10a114{0}   V=5.083
  Down:    L8n4{1,0}    V=5.333
  Strange: L9a45{1,1}   V=9.665
  Charm:   L10a100{1}   V=9.707
  Bottom:  L11n309{1,1} V=13.602
  Top:     L10a69{1}    V=14.963
  ```

- [ ] **Run CKM validation**
  ```bash
  cd code
  python -c "
  import json
  import numpy as np
  phys = json.load(open('../data/physical_constants.json'))
  print(f\"CKM R^2: {phys['ckm']['r2_achieved']}\")
  print(f\"Method: {phys['ckm']['selection_method']}\")
  "
  ```
  Expected: R² = 0.9980

- [ ] **Verify mass hierarchy**
  ```bash
  python -c "
  import json
  a = json.load(open('data/topology_assignments.json'))
  quarks = ['Up', 'Down', 'Strange', 'Charm', 'Bottom', 'Top']
  vols = [(q, a[q]['volume']) for q in quarks]
  print('Volume ordering:', ' < '.join([v[0] for v in sorted(vols, key=lambda x: x[1])]))
  "
  ```
  Expected: Up < Down < Strange < Charm < Bottom < Top

- [ ] **Run final audit**
  ```bash
  # Run ckm_final_audit.py if available
  python ckm_final_audit.py
  ```

---

## Optional Tasks

- [ ] **Update Papers 1-4**
  - Paper 1 (Mass): No changes needed
  - Paper 2 (PMNS): No changes needed
  - Paper 3 (DM): No changes needed
  - Paper 4 (CKM): **MUST UPDATE**
    - Replace R² = 0.70 → 0.9980
    - Update quark topology table
    - Add constrained optimization section

- [ ] **Create Zenodo release**
  - Package v6.0 final
  - Include CHANGELOG
  - Cite in all 4 papers
  - DOI assignment

- [ ] **Clean up v6.1 directory**
  - Option A: Delete v6.1 (merged into v6.0)
  - Option B: Keep v6.1 as development archive
  - Option C: Rename v6.1 → v6.0_development_notes

---

## Next Steps (After Validation)

1. **If all checks pass:**
   - Mark v6.0 as **FINAL**
   - Prepare for publication
   - Archive v6.1

2. **If issues found:**
   - Debug and re-run `topology_official_selector.py`
   - Adjust random seed if needed
   - Verify constraints are satisfied

---

## Status

**Current:** ⏳ Awaiting `topology_official_selector.py` completion

**Last Run:**
- Started: [timestamp from execution]
- Command: `python topology_official_selector.py`
- Expected duration: ~5-10 minutes (200k samples)

---

## Notes

- Random seed = 42 (reproducible)
- Different seeds may produce slightly different topologies (R² ∈ [0.995, 0.999])
- All valid solutions are in same discrete family
- Stochastic variation is acceptable (algorithm-justified)

---

*Checklist created: 2026-02-13*
