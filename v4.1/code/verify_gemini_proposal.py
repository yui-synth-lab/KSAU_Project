"""
Verify Gemini's v4.1 Final Proposal claims.
Check: volumes, determinants, errors, and pattern consistency.
"""
import numpy as np

G = 0.915965594
GAMMA_Q = (10.0/7.0) * G
B_PRIME = -(7.0 + G)
GAMMA_L = (2.0/9.0) * G

print("=" * 70)
print("  Verification of Gemini's v4.1 Final Proposal")
print("=" * 70)

# =====================================================================
# 1. Quark channel: verify claimed errors
# =====================================================================
print("\n--- 1. Quark Error Verification ---")

quarks_v41 = {
    'd': {'link': 'L6a4',    'V': 7.327725,  'Det': 16,  'm': 4.67},
    's': {'link': 'L10n95',  'V': 9.531900,  'Det': 32,  'm': 93.4},
    'b': {'link': 'L11n422', 'V': 12.447,    'Det': 48,  'm': 4180.0},
    'u': {'link': 'L7a5',    'V': 6.598952,  'Det': 18,  'm': 2.16},
    'c': {'link': 'L11n64',  'V': 11.517101, 'Det': 12,  'm': 1270.0},
    't': {'link': 'L11a144', 'V': 15.271,    'Det': 114, 'm': 172760.0},
}

print(f"  {'Q':<4} {'Link':<12} {'V':>8} {'Det':>5} {'Obs':>10} {'Pred':>10} {'Err':>8}")
print(f"  {'-'*60}")

errors = []
for q in ['u', 'd', 's', 'c', 'b', 't']:
    d = quarks_v41[q]
    ln_pred = GAMMA_Q * d['V'] + B_PRIME
    pred = np.exp(ln_pred)
    err = (pred - d['m']) / d['m'] * 100
    errors.append(abs(err))
    print(f"  {q:<4} {d['link']:<12} {d['V']:>8.3f} {d['Det']:>5} {d['m']:>10.1f} {pred:>10.1f} {err:>+7.1f}%")

q_mae = np.mean(errors)
print(f"\n  Quark MAE = {q_mae:.2f}%")
print(f"  Gemini claims: 4.31%  -> {'MATCH' if abs(q_mae - 4.31) < 0.5 else 'MISMATCH'}")

# =====================================================================
# 2. Lepton channel with twist correction
# =====================================================================
print("\n--- 2. Lepton Twist Correction Verification ---")

leptons = [
    {'name': 'e',   'N': 3, 'twist': 0, 'm': 0.510998},
    {'name': 'mu',  'N': 6, 'twist': 1, 'm': 105.658},
    {'name': 'tau', 'N': 7, 'twist': 0, 'm': 1776.86},
]

# C_l fixed by electron (with twist correction -1/6)
C_l = np.log(0.510998) - GAMMA_L * 9 - (-1.0/6.0) * 0  # electron is not twist
print(f"  C_l (electron-fixed) = {C_l:.6f}")

l_errors = []
for lep in leptons:
    ln_pred = GAMMA_L * lep['N']**2 + (-1.0/6.0) * lep['twist'] + C_l
    pred = np.exp(ln_pred)
    err = (pred - lep['m']) / lep['m'] * 100
    l_errors.append(abs(err))
    print(f"  {lep['name']:<4}: Obs={lep['m']:.4f}, Pred={pred:.4f}, Err={err:+.2f}%")

l_mae = np.mean(l_errors)
print(f"\n  Lepton MAE = {l_mae:.2f}%")
print(f"  Gemini claims: 0.48%  -> {'MATCH' if abs(l_mae - 0.48) < 0.1 else 'MISMATCH'}")

# Global
global_mae = (sum(errors) + sum(l_errors)) / 9
print(f"\n  Global MAE = {global_mae:.2f}%")
print(f"  Gemini claims: 3.03%  -> {'MATCH' if abs(global_mae - 3.03) < 0.3 else 'MISMATCH'}")

# =====================================================================
# 3. Determinant Pattern Analysis
# =====================================================================
print("\n--- 3. Determinant Pattern Critical Analysis ---")

print("\n  v4.0 Down-type: 2^k (geometric/binary)")
print(f"    d: {16} = 2^4")
print(f"    s: {32} = 2^5")
print(f"    b: {64} = 2^6")
print(f"    Pattern: 2^(k+3), k = generation")
print(f"    Theoretical meaning: Pure binary / SU(2) / qubit encoding")

print("\n  Gemini v4.1 Down-type: 16k (arithmetic)")
print(f"    d: {16} = 16 x 1")
print(f"    s: {32} = 16 x 2")
print(f"    b: {48} = 16 x 3")
print(f"    Pattern: 16k, k = generation")
print(f"    48 = 2^4 x 3  --> BREAKS 'pure binary' (factor of 3)")

print("\n  v4.0 Up-type: no clear pattern")
print(f"    u: 18 = 2 x 3^2")
print(f"    c: 12 = 2^2 x 3")
print(f"    t: 124 = 2^2 x 31")

print("\n  Gemini v4.1 Up-type: '6 x prime'")
print(f"    u: 18 = 6 x 3  (p=3)")
print(f"    c: 12 = 6 x 2  (p=2)")
print(f"    t: 114 = 6 x 19  (p=19)")
print(f"    Primes: 3, 2, 19  --> NO natural progression")
print(f"    Note: p=2,3 are tiny; p=19 is a huge jump")
print(f"    How many 11-crossing links have Det = 6*prime?")
dets_6p = [6*p for p in [2,3,5,7,11,13,17,19,23,29,31] if 6*p < 200]
print(f"    Possible: {dets_6p}")
print(f"    --> Many options exist; '6 x prime' is not selective")

# =====================================================================
# 4. What v4.0 loses by abandoning 2^k
# =====================================================================
print("\n--- 4. Cost of Abandoning 2^k Binary Rule ---")
print("""
  v4.0's Third Principle stated:
    "Down-type quarks possess a 'Pure Binary' topological structure,
     potentially linked to SU(2) weak isospin or qubit-like encoding."

  v4.0 explicitly REJECTED candidates based on this rule:
    - L11n419 (Strange rival, Det=24): rejected because 24 != 2^k
    - L10a146 (Bottom rival, Det=60): rejected because 60 != 2^k

  Gemini's v4.1 now proposes Det=48 for Bottom.
    48 = 2^4 x 3  (NOT pure binary)
    This is equivalent to un-rejecting the type of candidate v4.0 excluded.

  The 16k pattern (16, 32, 48) can be rewritten as 2^4 x (1, 2, 3).
    The (1, 2, 3) factor is simply the generation number.
    This is a WEAKER pattern than 2^(k+3).
""")

# =====================================================================
# 5. Unverified link claims
# =====================================================================
print("--- 5. Unverified Claims ---")
print("""
  The following link assignments are NEW and UNVERIFIED:

  1. L11n422: claimed V=12.447, Det=48
     - Need SnapPy verification
     - Need component count = 3 (down-type must be 3-component)

  2. L11a144: claimed V=15.271, Det=114
     - Need SnapPy verification
     - Need component count = 2 (up-type must be 2-component)
     - Det=114 = 6 x 19 claimed to fit "6 x prime" pattern

  Without independent verification, these results cannot be trusted.
""")

# =====================================================================
# 6. Max Error check
# =====================================================================
print("--- 6. v4.1 Target Check ---")
all_errors = errors + l_errors
max_err = max(all_errors)
print(f"  Global MAE: {global_mae:.2f}%  (Target < 5%: {'PASS' if global_mae < 5 else 'FAIL'})")
print(f"  Max Error:  {max_err:.2f}%  (Target < 10%: {'PASS' if max_err < 10 else 'FAIL'})")
print(f"  Down quark: {errors[1]:.2f}%  <-- still the bottleneck")

print("\n" + "=" * 70)
print("  END OF VERIFICATION")
print("=" * 70)
