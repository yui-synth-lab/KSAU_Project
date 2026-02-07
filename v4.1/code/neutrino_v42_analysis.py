"""
KSAU Neutrino Extension: Systematic Analysis
Target: Derive neutrino masses from KSAU framework principles.

Key problem:
  v4.1 lepton formula gives m(N=0, unknot) = 82 keV, but neutrinos must be < 0.1 eV.
  Need suppression factor ~10^6. What is it, and why?

Experimental constraints (PDG 2024 / NuFIT 5.3):
  Normal Ordering: m1 < m2 < m3
  Dm2_21 = 7.42e-5 eV^2  (solar)
  Dm2_31 = 2.514e-3 eV^2  (atmospheric)
  Sum < 0.12 eV (Planck 2018 + BAO)
  Sum < 0.072 eV (DESI 2024, 95% CL, if confirmed)
"""
import numpy as np

# =============================================================================
# KSAU CONSTANTS
# =============================================================================
G = 0.915965594177219
GAMMA_Q = (10.0 / 7.0) * G      # 1.30852...
GAMMA_L = (2.0 / 9.0) * G       # 0.20355...
B_PRIME = -(7.0 + G)             # -7.91597...
DELTA_TWIST = -1.0 / 6.0         # -0.16667...
CL = np.log(0.510998) - GAMMA_L * 9  # -2.50332...
PI = np.pi

# Experimental neutrino data
DM2_21 = 7.42e-5   # eV^2
DM2_31 = 2.514e-3  # eV^2

print("=" * 80)
print("  KSAU NEUTRINO EXTENSION: SYSTEMATIC ANALYSIS")
print("=" * 80)

# =============================================================================
# PART 1: THE SCALING PROBLEM
# =============================================================================
print("\n" + "=" * 80)
print("  PART 1: The Scaling Problem")
print("=" * 80)

# What does the v4.1 formula predict for N=0 (unknot)?
m_unknot_MeV = np.exp(CL)
m_unknot_eV = m_unknot_MeV * 1e6
print(f"\n  v4.1 lepton formula at N=0 (unknot):")
print(f"    ln(m) = C_l = {CL:.6f}")
print(f"    m = {m_unknot_MeV:.6e} MeV = {m_unknot_eV:.2f} eV")
print(f"    Cosmological limit: Sum < 0.12 eV")
print(f"    Required suppression: {m_unknot_eV / 0.05:.0f}x (to reach ~0.05 eV)")

# Required suppression factor S for various target masses
print(f"\n  Required suppression S = C_l - ln(m_nu/MeV):")
print(f"    {'Target m_nu (eV)':<20} {'ln(m/MeV)':<12} {'S':>8}")
print(f"    {'-'*42}")
for m_target_eV in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]:
    m_target_MeV = m_target_eV * 1e-6
    ln_m = np.log(m_target_MeV)
    S = CL - ln_m
    print(f"    {m_target_eV:<20.3f} {ln_m:<12.4f} {S:>8.4f}")

# =============================================================================
# PART 2: SYSTEMATIC SUPPRESSION FACTOR SEARCH
# =============================================================================
print("\n" + "=" * 80)
print("  PART 2: Systematic Suppression Factor Search")
print("  Looking for S expressible in KSAU constants {G, pi, 7, 9, 10, 1/6}")
print("=" * 80)

# Generate all "clean" candidates from KSAU constants
candidates = {}

# Single-term
candidates['7+G = |B\'|'] = 7 + G
candidates['2(7+G) = 2|B\'|'] = 2 * (7 + G)
candidates['7^2/(7+G)'] = 49 / (7 + G)
candidates['9G'] = 9 * G
candidates['10G'] = 10 * G
candidates['7G'] = 7 * G
candidates['(10/7)G * 7'] = GAMMA_Q * 7
candidates['(10/7)G * 9'] = GAMMA_Q * 9
candidates['(10/7)G * 10'] = GAMMA_Q * 10
candidates['(2/9)G * 70'] = GAMMA_L * 70
candidates['(2/9)G * 63'] = GAMMA_L * 63  # 7*9
candidates['(2/9)G * 81'] = GAMMA_L * 81  # 9^2
candidates['(2/9)G * 49'] = GAMMA_L * 49  # 7^2

# pi-based
candidates['4pi'] = 4 * PI
candidates['5pi'] = 5 * PI
candidates['4pi + G'] = 4 * PI + G
candidates['4pi + ln(4pi)'] = 4 * PI + np.log(4 * PI)
candidates['2pi^2'] = 2 * PI**2
candidates['pi^2 + G'] = PI**2 + G

# Mixed
candidates['9G + 7'] = 9 * G + 7
candidates['10G + 7'] = 10 * G + 7
candidates['7G + 7'] = 7 * G + 7
candidates['7(1+G)'] = 7 * (1 + G)
candidates['9(1+G)'] = 9 * (1 + G)
candidates['10(1+G)'] = 10 * (1 + G)
candidates['G * |B\'|'] = G * abs(B_PRIME)
candidates['pi * |B\'|'] = PI * abs(B_PRIME)

# Seesaw-inspired: 2*|C_l| + something
candidates['7 * |C_l|'] = 7 * abs(CL)
candidates['9 * |C_l|'] = 9 * abs(CL)

# Deep KSAU: using the slope relationship
candidates['GAMMA_Q / GAMMA_L * 7'] = (GAMMA_Q / GAMMA_L) * 7  # (45/7) * 7 = 45... no
candidates['(GAMMA_Q + GAMMA_L) * 10'] = (GAMMA_Q + GAMMA_L) * 10

# Compute masses and filter
print(f"\n  {'Expression':<28} {'S':>8} {'m_nu (eV)':>12} {'Sum_nu (eV)':>12} {'Status'}")
print(f"  {'-'*70}")

viable = []
for name, S in sorted(candidates.items(), key=lambda x: x[1]):
    ln_m = CL - S
    m_MeV = np.exp(ln_m)
    m1_eV = m_MeV * 1e6

    if m1_eV <= 0 or m1_eV > 1.0:
        continue

    m2_eV = np.sqrt(m1_eV**2 + DM2_21)
    m3_eV = np.sqrt(m1_eV**2 + DM2_31)
    sum_eV = m1_eV + m2_eV + m3_eV

    status = "OK" if sum_eV < 0.12 else "EXCLUDED"
    if sum_eV < 0.072:
        status = "OK (DESI)"

    print(f"  {name:<28} {S:>8.4f} {m1_eV:>12.6f} {sum_eV:>12.6f} {status}")

    if sum_eV < 0.12:
        viable.append((name, S, m1_eV, m2_eV, m3_eV, sum_eV))

print(f"\n  Viable candidates (Sum < 0.12 eV): {len(viable)}")

# =============================================================================
# PART 3: HIERARCHY ANALYSIS FOR VIABLE CANDIDATES
# =============================================================================
print("\n" + "=" * 80)
print("  PART 3: Hierarchy Analysis for Viable Candidates")
print("=" * 80)

for name, S, m1, m2, m3, sm in viable:
    print(f"\n  --- {name} (S = {S:.6f}) ---")
    print(f"  m1 = {m1:.6f} eV, m2 = {m2:.6f} eV, m3 = {m3:.6f} eV")
    print(f"  Sum = {sm:.6f} eV")
    print(f"  m3/m2 = {m3/m2:.4f}, m2/m1 = {m2/m1:.4f}, m3/m1 = {m3/m1:.4f}")
    print(f"  ln(m3/m1) = {np.log(m3/m1):.6f}")
    print(f"  ln(m2/m1) = {np.log(m2/m1):.6f}")
    print(f"  ln(m3/m2) = {np.log(m3/m2):.6f}")

    # Check if log-ratios match KSAU constants
    log_ratios = {
        'ln(m3/m1)': np.log(m3 / m1),
        'ln(m2/m1)': np.log(m2 / m1),
        'ln(m3/m2)': np.log(m3 / m2),
    }

    ksau_vals = {
        'G': G, 'G/2': G/2, 'G/3': G/3, 'G/7': G/7, 'G/9': G/9,
        '1/6': 1/6, '1/7': 1/7, '1/9': 1/9,
        '(2/9)G': GAMMA_L, '(10/7)G': GAMMA_Q,
        'ln(2)': np.log(2), 'ln(3)': np.log(3), 'ln(7)': np.log(7),
        'pi/7': PI/7, 'pi/9': PI/9, 'pi/10': PI/10,
        '1': 1.0, '2': 2.0,
    }

    for rname, rval in log_ratios.items():
        matches = []
        for kname, kval in ksau_vals.items():
            if abs(rval) > 0.001 and abs(rval - kval) / abs(rval) < 0.05:
                matches.append(f"{kname}={kval:.4f}")
        if matches:
            print(f"    {rname} = {rval:.6f} ~ {', '.join(matches)}")

# =============================================================================
# PART 4: THE ANALYTIC CONTINUATION HYPOTHESIS
# =============================================================================
print("\n" + "=" * 80)
print("  PART 4: Analytic Continuation Hypothesis")
print("  What if neutrinos use N^2 -> -N^2 (imaginary crossing number)?")
print("=" * 80)

# If ln(m_nu) = -(2/9)G * N_eff^2 + C_l, what N_eff^2 gives viable masses?
print(f"\n  Formula: ln(m_nu) = -(2/9)G * N_eff^2 + C_l")
print(f"  {'m_nu (eV)':<12} {'N_eff^2':>10} {'sqrt(N_eff^2)':>14} {'Close to?'}")
print(f"  {'-'*55}")

for m_target_eV in [0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.08]:
    ln_m = np.log(m_target_eV * 1e-6)
    N_eff_sq = (CL - ln_m) / GAMMA_L
    sqrt_N = np.sqrt(N_eff_sq)

    # Check closeness to integers and KSAU numbers
    close = []
    for n in range(1, 15):
        if abs(N_eff_sq - n) < 0.5:
            close.append(f"{n}")
    for expr, val in [('7*9', 63), ('7*10', 70), ('9*9', 81), ('7^2', 49),
                      ('10*7', 70), ('9*10', 90), ('10^2', 100)]:
        if abs(N_eff_sq - val) < 2:
            close.append(f"{expr}={val}")

    close_str = ", ".join(close) if close else "-"
    print(f"  {m_target_eV:<12.3f} {N_eff_sq:>10.2f} {sqrt_N:>14.2f} {close_str}")

# Specific test: N_eff^2 = 7*10 = 70
N_sq_70 = 70
ln_m_70 = -GAMMA_L * N_sq_70 + CL
m_70_eV = np.exp(ln_m_70) * 1e6
print(f"\n  Special case: N_eff^2 = 7*10 = 70")
print(f"    ln(m) = -(2/9)G * 70 + C_l = {ln_m_70:.6f}")
print(f"    m = {m_70_eV:.6f} eV")

m2_70 = np.sqrt(m_70_eV**2 + DM2_21)
m3_70 = np.sqrt(m_70_eV**2 + DM2_31)
sum_70 = m_70_eV + m2_70 + m3_70
print(f"    m1={m_70_eV:.6f}, m2={m2_70:.6f}, m3={m3_70:.6f}")
print(f"    Sum = {sum_70:.6f} eV ({'OK' if sum_70 < 0.12 else 'EXCLUDED'})")

# N_eff^2 = 9*9 = 81
N_sq_81 = 81
ln_m_81 = -GAMMA_L * N_sq_81 + CL
m_81_eV = np.exp(ln_m_81) * 1e6
print(f"\n  Special case: N_eff^2 = 9^2 = 81")
print(f"    ln(m) = -(2/9)G * 81 + C_l = {ln_m_81:.6f}")
print(f"    m = {m_81_eV:.6f} eV")

m2_81 = np.sqrt(m_81_eV**2 + DM2_21)
m3_81 = np.sqrt(m_81_eV**2 + DM2_31)
sum_81 = m_81_eV + m2_81 + m3_81
print(f"    m1={m_81_eV:.6f}, m2={m2_81:.6f}, m3={m3_81:.6f}")
print(f"    Sum = {sum_81:.6f} eV ({'OK' if sum_81 < 0.12 else 'EXCLUDED'})")

# =============================================================================
# PART 5: TOPOLOGICAL SEESAW HYPOTHESIS
# =============================================================================
print("\n" + "=" * 80)
print("  PART 5: Topological Seesaw Hypothesis")
print("  ln(m_nu) = 2*ln(m_l) - ln(M), where M is a topological scale")
print("=" * 80)

# Charged lepton masses (MeV)
m_e = 0.510998
m_mu = 105.658
m_tau = 1776.86

# If all three neutrinos see the SAME scale M:
# Then m_nu_e = m_e^2 / M, m_nu_mu = m_mu^2 / M, m_nu_tau = m_tau^2 / M
# Ratios: m_nu_tau / m_nu_e = (m_tau/m_e)^2 = (3478)^2 = 1.21e7
# This is way too large — experiment has m3/m1 < ~50 (for normal ordering)
# So a simple universal seesaw FAILS

print(f"\n  Universal seesaw M: m_nu = m_l^2 / M")
print(f"    Predicted ratio m_nu_tau/m_nu_e = (m_tau/m_e)^2 = {(m_tau/m_e)**2:.0f}")
print(f"    Experimental range: m3/m1 = 5 to 50")
print(f"    --> FAILS: ratio too large by ~10^5")

# Seesaw with generation-dependent M?
# ln(m_nu) = 2*ln(m_l) - M_i
# Need: M_e, M_mu, M_tau such that m_nu_e < m_nu_mu < m_nu_tau < 0.05 eV
# For m_nu_e = 0.01 eV: M_e = 2*ln(m_e) - ln(0.01/1e6) = -1.342 - (-18.42) = 17.08
# For m_nu_tau = 0.05 eV: M_tau = 2*ln(m_tau) - ln(0.05/1e6) = 14.966 - (-16.81) = 31.78
# M values span 17 to 32 — not universal
print(f"\n  Generation-dependent seesaw would need:")
for name, m_l, m_nu_target in [('e', m_e, 0.01), ('mu', m_mu, 0.03), ('tau', m_tau, 0.05)]:
    M_needed = 2 * np.log(m_l) - np.log(m_nu_target * 1e-6)
    print(f"    nu_{name}: M = {M_needed:.4f} (for m_nu = {m_nu_target} eV)")
print(f"    --> No universal M exists")

# =============================================================================
# PART 6: FLAVOR-INDEPENDENT SUPPRESSION + HIERARCHY FROM TOPOLOGY
# =============================================================================
print("\n" + "=" * 80)
print("  PART 6: Flavor-Independent Suppression + Hierarchy from Topology")
print("  m_nu_i = exp(C_l - S + gamma_i), where S is universal, gamma_i is topological")
print("=" * 80)

# If all neutrinos share a base suppression S but differ by a small topological term gamma_i:
# ln(m_i) = C_l - S + gamma_i
# Then: m1 = exp(C_l - S), m2 = exp(C_l - S + gamma_2), m3 = exp(C_l - S + gamma_3)
# With gamma_1 = 0 (lightest)

# From Delta_m^2 constraints:
# m2^2 - m1^2 = DM2_21, m3^2 - m1^2 = DM2_31
# m2 = m1 * exp(gamma_2), m3 = m1 * exp(gamma_3)
# m1^2 * (exp(2*gamma_2) - 1) = DM2_21
# m1^2 * (exp(2*gamma_3) - 1) = DM2_31

# If gamma_2, gamma_3 << 1:
# m1^2 * 2*gamma_2 ≈ DM2_21
# m1^2 * 2*gamma_3 ≈ DM2_31
# gamma_3/gamma_2 ≈ DM2_31/DM2_21 = 33.9

# This means gamma_3 >> gamma_2, so the log-spacing is NOT uniform
# The "solar" splitting is much smaller than the "atmospheric"

print(f"\n  Ratio DM2_31/DM2_21 = {DM2_31/DM2_21:.1f}")
print(f"  This means gamma_3/gamma_2 ~ {DM2_31/DM2_21:.1f} (highly non-uniform)")

# Scan over S and check if gamma_2, gamma_3 have clean expressions
print(f"\n  Scan: For each S, compute required gamma_2, gamma_3")
print(f"  {'S expression':<25} {'m1 (eV)':>10} {'gamma_2':>10} {'gamma_3':>10} {'gamma_3/gamma_2':>16}")
print(f"  {'-'*75}")

for name, S, m1, m2, m3, sm in viable:
    if m1 > 0.001:  # Skip extremely light ones
        gamma_2 = np.log(m2 / m1)
        gamma_3 = np.log(m3 / m1)
        ratio = gamma_3 / gamma_2 if gamma_2 > 0 else float('inf')
        print(f"  {name:<25} {m1:>10.6f} {gamma_2:>10.6f} {gamma_3:>10.6f} {ratio:>16.2f}")

# =============================================================================
# PART 7: THE FRAMING HYPOTHESIS
# =============================================================================
print("\n" + "=" * 80)
print("  PART 7: Framing Hypothesis")
print("  Unknot with framing n: ln(m_nu_n) = C_l - S + f(n)")
print("  Can different framings of the unknot produce the mass hierarchy?")
print("=" * 80)

# In Chern-Simons theory, the unknot with framing f contributes:
# <unknot>_f = <unknot>_0 * exp(2*pi*i*f / k)
# The mass analog might be a real phase: m_f = m_0 * exp(alpha * f^p)

# For the mass hierarchy to work:
# m_nu_1 = m_0 (framing 0)
# m_nu_2 = m_0 * exp(alpha * n_2^p)
# m_nu_3 = m_0 * exp(alpha * n_3^p)

# If p=2 (quadratic like leptons) and n = {0, 1, 2}:
# ln(m3/m1) = alpha * 4
# ln(m2/m1) = alpha * 1
# Ratio = 4

# But we need ratio ≈ DM2_31/DM2_21 ≈ 34 (very non-uniform)
# So p=2 with n={0,1,2} doesn't work

# If n = {0, 1, n_3} with p=2:
# ln(m3/m1) / ln(m2/m1) = n_3^2
# Need n_3^2 ≈ 34 → n_3 ≈ 5.8

# But the actual ratios depend on m1. Let me compute for a specific case.

# Use S = 2(7+G) as example
S_ex = 2 * (7 + G)
m1_ex = np.exp(CL - S_ex) * 1e6  # eV
m2_ex = np.sqrt(m1_ex**2 + DM2_21)
m3_ex = np.sqrt(m1_ex**2 + DM2_31)

g2_ex = np.log(m2_ex / m1_ex)
g3_ex = np.log(m3_ex / m1_ex)

print(f"\n  Example: S = 2(7+G) = {S_ex:.4f}")
print(f"  m1 = {m1_ex:.6f}, m2 = {m2_ex:.6f}, m3 = {m3_ex:.6f}")
print(f"  gamma_2 = {g2_ex:.6f}, gamma_3 = {g3_ex:.6f}")
print(f"  gamma_3/gamma_2 = {g3_ex/g2_ex:.2f}")

# For quadratic framing f(n) = alpha * n^2:
# gamma_2 = alpha * n_2^2, gamma_3 = alpha * n_3^2
# If n_2=1: alpha = gamma_2
# n_3 = sqrt(gamma_3 / alpha) = sqrt(gamma_3/gamma_2)
n3_needed = np.sqrt(g3_ex / g2_ex)
print(f"\n  Quadratic framing: n2=1, n3 = sqrt(g3/g2) = {n3_needed:.4f}")
print(f"  Not an integer -> quadratic framing with {0,1,n} doesn't work simply")

# What if framing is {0, a, b} with linear scaling f(n) = alpha * n?
# gamma_2 = alpha * a, gamma_3 = alpha * b
# b/a = gamma_3/gamma_2
# Need b/a ≈ 5.6 -> a=1, b≈6? or a=2, b≈11?
ba_ratio = g3_ex / g2_ex
print(f"\n  Linear framing: b/a = {ba_ratio:.2f}")
print(f"  Closest integer pairs: a=1,b={round(ba_ratio)}; a=2,b={round(2*ba_ratio)}")

# =============================================================================
# PART 8: KEY INSIGHT — WHAT IF N_eff^2 = 7*10 = 70?
# =============================================================================
print("\n" + "=" * 80)
print("  PART 8: The N_eff^2 = 70 = 7*10 Hypothesis")
print("  Neutrino formula: ln(m_nu) = -(2/9)G * 70 + C_l")
print("  This uses BOTH KSAU fundamental numbers (7 and 10) from the quark slope (10/7)G")
print("=" * 80)

# The analytic continuation idea: leptons have positive N^2, neutrinos have negative N^2
# For charged leptons: ln(m) = (2/9)G * N^2 + corrections + C_l
# For neutrinos: ln(m) = (2/9)G * (-N_eff^2) + corrections + C_l
# = -(2/9)G * N_eff^2 + C_l

# N_eff^2 = 70 = 7 * 10
ln_m_nu = -GAMMA_L * 70 + CL
m_nu_MeV = np.exp(ln_m_nu)
m_nu_eV = m_nu_MeV * 1e6

print(f"\n  ln(m_nu) = -(2/9)G * 70 + C_l = {ln_m_nu:.6f}")
print(f"  m_nu = {m_nu_eV:.6f} eV")

# This gives the LIGHTEST neutrino mass
m1 = m_nu_eV
m2 = np.sqrt(m1**2 + DM2_21)
m3 = np.sqrt(m1**2 + DM2_31)
sum_m = m1 + m2 + m3

print(f"\n  Normal Ordering hierarchy:")
print(f"    m1 = {m1:.6f} eV (N_eff^2 = 70)")
print(f"    m2 = {m2:.6f} eV")
print(f"    m3 = {m3:.6f} eV")
print(f"    Sum = {sum_m:.6f} eV ({'< 0.12 OK' if sum_m < 0.12 else 'EXCLUDED'})")
print(f"    {'< 0.072 DESI OK' if sum_m < 0.072 else '> 0.072 (DESI tension)' if sum_m < 0.12 else ''}")

# Deeper interpretation:
# Why 70 = 7 * 10?
# In KSAU: quark slope = (10/7)*G. The "10" and "7" appear as fundamental numbers.
# The product 7*10 = 70 combines both.
# Physical interpretation: neutrinos are "dual" to quarks in the sense that
# their mass scale is set by the PRODUCT of the quark numerator and denominator.

# Check: what's the effective suppression S?
S_70 = GAMMA_L * 70  # = (2/9)G * 70 = 140G/9
print(f"\n  Effective suppression: S = (2/9)G * 70 = 140G/9 = {S_70:.6f}")
print(f"  = {140.0/9:.4f} * G = {S_70:.6f}")
print(f"  Note: 140/9 = {140/9:.4f}")

# =============================================================================
# PART 9: THREE GENERATIONS FROM ANALYTIC CONTINUATION
# =============================================================================
print("\n" + "=" * 80)
print("  PART 9: Three Generations from N_eff^2 Variants")
print("  If N_eff^2 = {70, 70-a, 70-b}, what are a, b?")
print("=" * 80)

# For three neutrino masses from analytic continuation:
# m_i = exp(-(2/9)G * N_i^2 + C_l) * 1e6 eV
# We need N_1^2 > N_2^2 > N_3^2 (larger N^2 = lighter)
# m1 corresponds to the LARGEST N^2, m3 to the smallest

# Given m1, m2, m3 are fixed by m1 and Dm^2:
# N_3^2 = -[ln(m3/MeV) - C_l] / GAMMA_L
# N_2^2 = -[ln(m2/MeV) - C_l] / GAMMA_L
# N_1^2 = -[ln(m1/MeV) - C_l] / GAMMA_L = 70

N1_sq = -(np.log(m1 * 1e-6) - CL) / GAMMA_L
N2_sq = -(np.log(m2 * 1e-6) - CL) / GAMMA_L
N3_sq = -(np.log(m3 * 1e-6) - CL) / GAMMA_L

print(f"\n  Required N_eff^2 values:")
print(f"    nu_1 (lightest): N_eff^2 = {N1_sq:.4f} (target: 70)")
print(f"    nu_2:            N_eff^2 = {N2_sq:.4f} (diff from 70: {70 - N2_sq:.4f})")
print(f"    nu_3 (heaviest): N_eff^2 = {N3_sq:.4f} (diff from 70: {70 - N3_sq:.4f})")

delta_N_21 = N1_sq - N2_sq
delta_N_31 = N1_sq - N3_sq

print(f"\n  Differences:")
print(f"    Delta(N^2)_21 = {delta_N_21:.6f}")
print(f"    Delta(N^2)_31 = {delta_N_31:.6f}")
print(f"    Ratio: {delta_N_31/delta_N_21:.2f}")

# Check if these differences match KSAU constants
print(f"\n  Matching Delta(N^2) to KSAU constants:")
for expr, val in [('1', 1.0), ('G', G), ('1/G', 1/G), ('7/9', 7/9), ('9/7', 9/7),
                  ('pi', PI), ('2', 2.0), ('7', 7.0), ('G^2', G**2), ('1/6', 1/6),
                  ('1/7', 1/7), ('G/7', G/7), ('G/9', G/9),
                  ('7*G', 7*G), ('10*G', 10*G)]:
    for dname, dval in [('D21', delta_N_21), ('D31', delta_N_31)]:
        if abs(dval) > 1e-6 and abs(dval - val) / max(abs(dval), 1e-10) < 0.1:
            print(f"    {dname} = {dval:.6f} ~ {expr} = {val:.6f} (err {abs(dval-val)/abs(dval)*100:.1f}%)")

# =============================================================================
# PART 10: ALTERNATIVE — N_eff^2 = 9^2 = 81
# =============================================================================
print("\n" + "=" * 80)
print("  PART 10: Alternative — N_eff^2 = 9^2 = 81")
print("  Motivation: 9 is a KSAU fundamental, and 81 = 9*9 mirrors N^2 structure")
print("=" * 80)

ln_m_81 = -GAMMA_L * 81 + CL
m1_81 = np.exp(ln_m_81) * 1e6  # eV

m2_81 = np.sqrt(m1_81**2 + DM2_21)
m3_81 = np.sqrt(m1_81**2 + DM2_31)
sum_81 = m1_81 + m2_81 + m3_81

print(f"\n  m1 = {m1_81:.6f} eV")
print(f"  m2 = {m2_81:.6f} eV, m3 = {m3_81:.6f} eV")
print(f"  Sum = {sum_81:.6f} eV ({'OK' if sum_81 < 0.12 else 'EXCLUDED'})")

if m1_81 > 0 and m1_81 < 1:
    N1_81 = -(np.log(m1_81 * 1e-6) - CL) / GAMMA_L
    N2_81 = -(np.log(m2_81 * 1e-6) - CL) / GAMMA_L
    N3_81 = -(np.log(m3_81 * 1e-6) - CL) / GAMMA_L
    print(f"\n  N_eff^2 values: {N1_81:.4f}, {N2_81:.4f}, {N3_81:.4f}")
    print(f"  Deltas: D21={N1_81-N2_81:.6f}, D31={N1_81-N3_81:.6f}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("  SUMMARY")
print("=" * 80)

print(f"""
  The KSAU v4.1 lepton formula predicts m(unknot) = 82 keV for neutrinos,
  which is ~10^6 too heavy. A suppression mechanism is needed.

  VIABLE APPROACHES (Sum < 0.12 eV):
  {len(viable)} candidates found from KSAU constant combinations.

  MOST PROMISING:
  1. Analytic Continuation: N^2 -> -N^2
     - N_eff^2 = 70 = 7*10: m1 = {np.exp(-GAMMA_L*70 + CL)*1e6:.4f} eV
     - Uses both KSAU fundamental numbers (7, 10) from quark slope (10/7)G
     - Suppression S = 140G/9

  KEY UNSOLVED PROBLEM:
  - Three-generation mechanism: How to derive m2, m3 from topology?
  - The mass splittings require Delta(N^2) ~ {delta_N_21:.4f} and {delta_N_31:.4f}
  - These are NOT close to simple KSAU constants
""")

print("=" * 80)
print("  END OF ANALYSIS")
print("=" * 80)
