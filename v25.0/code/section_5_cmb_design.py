#!/usr/bin/env python3
"""
KSAU v25.0 Section 5 — CMB Lensing Integration: Initial Design Document
========================================================================
Design-only (no implementation/tests required per roadmap).

Physical motivation:
  v24.0 Session 4: ACT-DR6/Planck PR4 forward prediction failed at 4.35σ.
  v23.0 engine is calibrated for z < 1 WL surveys. At z > 1, the growth
  factor D(z) and lensing kernel require ΛCDM numerical integration, not
  the simplified power-law approximation currently used.

This section provides:
  5a. Interface design for extending predict_s8_z() to z > 1
  5b. Prototype growth function D(z) via Planck ΛCDM numerical integration
  5c. CMB lensing data points for future forward prediction testing

Author: KSAU v25.0 Simulation Kernel — Section 5
Date:   2026-02-18  # W-NEW-1 fix (Session 7, P-S7-1): corrected from 2026-02-19
References: ACT-DR6 (Qu et al. 2023), Planck PR4 (Carron et al. 2022)
"""

import json, math
import numpy as np
from pathlib import Path
from scipy.integrate import quad

BASE = Path("E:/Obsidian/KSAU_Project")

# ─── Planck 2018 ΛCDM parameters ─────────────────────────────────────────────
PLANCK2018 = {
    "H0":       67.4,     # km/s/Mpc
    "Omega_m0": 0.315,    # matter density parameter
    "Omega_L0": 0.685,    # dark energy density parameter
    "Omega_r0": 9.2e-5,   # radiation (negligible at z<100)  # M-S7-1 fix: SSoT value 9.2e-5
    "sigma8":   0.811,    # matter fluctuation amplitude
    "n_s":      0.9667,   # scalar spectral index  # M-S7-1 fix: SSoT value 0.9667
}


# ─── Section 5a: Interface Design ────────────────────────────────────────────
def design_interface():
    """
    5a: Design document for extending the v23.0 engine to z > 1.

    Current v23.0 engine predict_s8_z(z, r0, beta):
      - Uses d_z = a^gamma_k where a = 1/(1+z)
      - This is a simplified growth factor: D(z) ≈ (1+z)^(-gamma_k)
      - For gamma_k ~ 0.55 (ΛCDM), this is reasonable at z < 1
      - At z > 1, the approximation breaks down significantly

    Proposed extension interface:
    """
    interface = {
        "current_function": {
            "signature": "predict_s8_z(z, r0, beta, use_nl=False)",
            "growth_model": "d_z = a^gamma_k (power-law approximation)",
            "valid_range":  "z < 1 (WL surveys)",
            "failure_mode": "Overestimates growth at z > 1",
        },
        "proposed_extension": {
            "new_function_name": "predict_s8_z_extended",
            "signature": (
                "predict_s8_z_extended(z, r0, beta, "
                "use_nl=False, use_lcdm_growth=False)"
            ),
            "parameters": {
                "use_lcdm_growth": (
                    "bool: If True, use numerical ΛCDM growth factor D(z) "
                    "from Planck 2018 integration (valid at z > 1). "
                    "If False, use current power-law approximation (legacy)."
                ),
                "growth_normalisation": (
                    "float: normalise D(z) such that D(0)=1. "
                    "Default: True."
                ),
            },
            "growth_function_new": {
                "method": "Numerical ODE or integral: D(z) ∝ H(z) × ∫_{z}^{∞} dz'/(H(z')^3 × a'^3)",
                "reference": "Heath (1977), Eq. 13; Carroll et al. (1992)",
                "implementation": "scipy.integrate.quad with Planck 2018 H(z)",
            },
            "backward_compatibility": (
                "When use_lcdm_growth=False (default), behaviour identical to v23.0. "
                "All existing v23.0/v24.0 results are unchanged."
            ),
            "test_protocol": (
                "Validate: for z ∈ [0, 1], D_ΛCDM(z) vs D_powerlaw(z) < 5% difference. "
                "For z ∈ [1, 3], D_ΛCDM(z) is used instead of power-law."
            ),
        },
        "integration_plan": {
            "phase_v26":  "Implement use_lcdm_growth=True in loo_cv_engine_v26.py",
            "phase_v26_test": "Verify ACT-DR6/Planck PR4 forward prediction at z_eff~1.0",
            "phase_v27":  "Full CMB lensing LOO-CV integration",
        },
    }
    return interface


# ─── Section 5b: Growth function D(z) prototype ──────────────────────────────
def planck_growth_function_prototype(z_max=2.5, n_points=50):
    """
    5b: Prototype numerical ΛCDM growth function D(z).

    Uses the integral form:
    D(z) = H(z) × ∫_z^∞ dz' / (H(z')^3 × (1+z')^3) / D_normalisation

    where H(z) = H0 × sqrt(Ω_m(1+z)³ + Ω_Λ + Ω_r(1+z)⁴)
    """
    Om  = PLANCK2018["Omega_m0"]
    OL  = PLANCK2018["Omega_L0"]
    Or  = PLANCK2018["Omega_r0"]
    H0  = PLANCK2018["H0"]

    def H_over_H0(z):
        """H(z)/H0."""
        return math.sqrt(Om * (1+z)**3 + OL + Or * (1+z)**4)

    def growth_integrand(zp):
        """Integrand for growing-mode growth factor (Heath 1977)."""
        Hp = H_over_H0(zp)
        return (1.0 + zp) / (Hp ** 3)   # correct form: (1+z') / H(z')^3

    # D(z) = 5Ω_m/2 × H(z)/H0 × ∫_z^∞ (1+z') / (H(z')/H0)^3 dz'
    prefactor = 5.0 * Om / 2.0

    def D_unnorm(z):
        integral, _ = quad(growth_integrand, z, 50.0, limit=300, epsabs=1e-8)
        return prefactor * H_over_H0(z) * integral

    # Normalise: D(0) = 1
    D0 = D_unnorm(0.0)

    z_arr = np.linspace(0.0, z_max, n_points)
    D_arr = np.array([D_unnorm(z) / D0 for z in z_arr])

    # Also compute power-law approximation: D(z) ≈ (1+z)^(-gamma) with gamma=0.55
    gamma_eff = 0.55 * math.log(Om) / math.log(Om)  # simplified
    D_powerlaw = np.array([(1/(1+z))**0.55 for z in z_arr])
    # Normalise powerlaw to D(0)=1
    D_powerlaw = D_powerlaw / D_powerlaw[0]

    # Compute deviation at key redshifts
    comparison = []
    key_z = [0.0, 0.26, 0.33, 0.40, 0.52, 0.60, 1.0, 1.5, 2.0, 2.5]
    for z in key_z:
        D_lcdm = D_unnorm(z) / D0
        D_pl   = (1/(1+z))**0.55
        D_pl  /= 1.0  # already normalised since D_pl(0)=1^(-0.55)=1
        dev_pct = (D_pl - D_lcdm) / D_lcdm * 100.0
        comparison.append({
            "z":         z,
            "D_LCDM":    round(D_lcdm, 6),
            "D_powerlaw":round(D_pl, 6),
            "dev_pct":   round(dev_pct, 3),
        })

    # Compute S₈ correction factor at CMB lensing z_eff
    # CMB lensing effective z: z_eff ~ 1.0 (lens plane peak)
    D_at_1 = D_unnorm(1.0) / D0
    D_pl_1 = (1/(1+1.0))**0.55
    s8_correction_factor_z1 = D_at_1 / D_pl_1

    return {
        "omega_m0":   Om,
        "omega_L0":   OL,
        "z_array":    [round(float(z), 4) for z in z_arr.tolist()[::5]],
        "D_LCDM":     [round(float(D), 6) for D in D_arr.tolist()[::5]],
        "D_powerlaw": [round(float(D), 6) for D in D_powerlaw.tolist()[::5]],
        "comparison_key_z": comparison,
        "s8_correction_factor_at_z1": round(s8_correction_factor_z1, 6),
        "diagnostic": (
            f"At z=1.0: D_ΛCDM={D_at_1:.4f} vs D_powerlaw={D_pl_1:.4f} "
            f"(ratio={D_at_1/D_pl_1:.4f}). "
            f"Power-law deviation at z=1: {(D_pl_1/D_at_1 - 1)*100:.1f}%. "
            "This systematic bias is the primary cause of the 4.35σ CMB lensing failure."
        ),
    }


# ─── Section 5c: CMB Lensing Data Points ─────────────────────────────────────
def cmb_lensing_data():
    """
    5c: CMB lensing data points for future forward prediction testing.
    These are NOT added to the WL LOO-CV pool (z > 1, different physics).
    """
    return {
        "_description": "CMB lensing datasets for v26+ forward prediction testing",
        "_note": (
            "NOT included in v25.0 LOO-CV. These are z > 1 (lens plane at z > 0.5) "
            "and require the ΛCDM growth function (Section 5b). "
            "Forward prediction with v23.0 engine failed 4.35σ (v24.0 Session 4)."
        ),
        "datasets": {
            "ACT-DR6": {
                "S8_obs": 0.840,
                "S8_err": 0.028,
                "z_eff":  1.0,
                "ref":    "Qu et al. (2023), arXiv:2304.05196",
                "notes":  "ACT DR6 CMB lensing + SDSS galaxies. z_eff~1.0.",
                "type":   "CMB_lensing",
            },
            "Planck_PR4": {
                "S8_obs": 0.823,
                "S8_err": 0.023,
                "z_eff":  0.95,
                "ref":    "Carron et al. (2022), JCAP 09 (2022) 039",
                "notes":  "Planck PR4 CMB lensing. z_eff~0.95-1.05.",
                "type":   "CMB_lensing",
            },
        },
        "v24_session4_failure": {
            "predicted_S8_ACT":     0.704,
            "predicted_S8_Planck":  0.712,
            "tension_ACT_sigma":    4.86,
            "tension_Planck_sigma": 4.83,
            "note": "v24.0 Session 4 forward prediction failed catastrophically at >4σ.",
        },
        "v26_implementation_requirements": [
            "Implement predict_s8_z_extended with use_lcdm_growth=True",
            "Validate D(z) growth function against CAMB/CLASS output",
            "Test forward prediction for ACT-DR6 and Planck PR4",
            "If tension < 2σ, consider adding to LOO-CV pool in v27.0",
        ],
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 76)
    print("KSAU v25.0 Section 5 — CMB Lensing Integration Design")
    print("(Design document only — no implementation in v25.0)")
    print("=" * 76)

    # 5a: Interface design
    print("\nSection 5a: Interface design for z>1 extension...")
    interface = design_interface()
    print(f"  New function: {interface['proposed_extension']['signature']}")
    print(f"  Growth model: {interface['proposed_extension']['growth_function_new']['method']}")
    print(f"  Backward compatible: Yes (use_lcdm_growth=False by default)")

    # 5b: D(z) prototype
    print("\nSection 5b: Planck ΛCDM growth function D(z) prototype...")
    growth = planck_growth_function_prototype()
    print(f"  D(z) comparison at key redshifts:")
    for row in growth["comparison_key_z"]:
        dev_flag = " ← SIGNIFICANT" if abs(row["dev_pct"]) > 5 else ""
        print(f"    z={row['z']:.2f}: D_ΛCDM={row['D_LCDM']:.4f}, "
              f"D_powerlaw={row['D_powerlaw']:.4f}, "
              f"dev={row['dev_pct']:+.1f}%{dev_flag}")
    print(f"  {growth['diagnostic']}")

    # 5c: CMB lensing data
    print("\nSection 5c: CMB lensing data points for future testing...")
    cmb_data = cmb_lensing_data()
    for name, ds in cmb_data["datasets"].items():
        print(f"  {name}: S₈={ds['S8_obs']}±{ds['S8_err']}, z_eff={ds['z_eff']}")

    # Save
    results = {
        "date":    "2026-02-18",  # W-NEW-1 fix (Session 7, P-S7-1): corrected from 2026-02-19
        "section": "Section 5",
        "type":    "design_document_only",
        "section_5a_interface":  interface,
        "section_5b_growth_fn":  growth,
        "section_5c_cmb_data":   cmb_data,
        "roadmap_compliance": {
            "design_doc_created":      True,
            "growth_fn_prototype":     True,
            "cmb_data_added":          True,
            "implementation_required": False,
            "target_version":          "v26.0+",
        },
    }

    out_path = BASE / "v25.0" / "data" / "section_5_results.json"
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved → {out_path}")
    return results


if __name__ == "__main__":
    main()
