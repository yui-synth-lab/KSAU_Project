---
name: ksau-ssot-auditor
description: Data integrity and Single Source of Truth (SSoT) auditor for the KSAU project. Monitors consistency between JSON metadata and Python implementation, preventing hard-coding of physical values and ensuring theoretical alignment.
---

# KSAU SSoT Auditor

## Overview

This skill enforces the project's most critical coding rule: **No Hard-coding**. It ensures that all scripts draw their parameters from the centralized Single Source of Truth (SSoT) files: `v6.0/data/physical_constants.json` and `v6.0/data/topology_assignments.json`.

## Audit Rules

### 1. Zero Tolerance for Hard-coded Numerics
- Physical constants (masses, mixing angles, coupling constants) must NOT appear as literals (e.g., `0.511`) in `.py` files.
- **Exception**: Universal mathematical constants like $\pi$ (if not defined in SSoT) or basic indices.

### 2. SSoT Synchronization
- Quark topologies in code must match `topology_assignments.json`.
- CKM coefficients in code must match `physical_constants.json` (`ckm.optimized_coefficients`).

### 3. File Inheritance Integrity
- Ensure `v6.1` and future version scripts correctly inherit data from `v6.0/data/` via `utils_v61.py` or `ksau_config.py`.
- Prevent "orphan" JSON files (like `topology_assignments_v61_old.json`) from being used by mistake.

## Workflow

When asked to "audit the codebase" or "check consistency":

1. **Grepping for Literals**: Search for common physical values (e.g., `172760`, `0.007297`) in the `v6.0/code/` directory.
2. **JSON Cross-Check**: Compare `physical_constants.json` against the reported results in `FINAL_SUMMARY.md`.
3. **Link/Knot Validation**: Verify that the topology names cited in `topology_assignments.json` exist in the underlying CSV databases (`linkinfo_data_complete.csv`).

## Corrective Actions
- If a discrepancy is found, **flag it as CRITICAL**.
- Recommend moving the hard-coded value to the appropriate JSON file and updating the script to load it dynamically.

---
*KSAU Integrity Kernel - Protecting the Single Source of Truth*
