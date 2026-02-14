"""
KSAU v10.0: Boson Effective Slope Analysis
===========================================

Purpose: Determine whether N_boson = 3 or N_boson = 6 through rigorous calculation
of effective slopes and comparison with theoretical predictions.

Method:
1. Calculate effective slope for each boson: slope_i = ln(m_i/m_e) / V_i
2. Compare with N*kappa predictions for N=3 and N=6
3. Test goodness of fit for both hypotheses

Dependencies: unified_particle_dataset.json (v10.0 SSoT)
Author: Claude Opus 4.6
Date: 2026-02-15
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load unified dataset
data_path = Path(__file__).parent.parent / 'data' / 'unified_particle_dataset.json'
with open(data_path, 'r') as f:
    data = json.load(f)

# Extract constants
kappa = data['metadata']['universal_constants']['kappa']
particles = data['particles']

# Separate by sector
leptons = [p for p in particles if p['sector'] == 'Lepton']
quarks = [p for p in particles if p['sector'] == 'Quark']
bosons = [p for p in particles if p['sector'] == 'Boson']

print("=" * 70)
print("KSAU v10.0: Boson Effective Slope Analysis")
print("=" * 70)
print()

# ============================================================================
# PART 1: Calculate Effective Slopes for All Particles
# ============================================================================

print("PART 1: Effective Slope Calculation")
print("-" * 70)
print(f"Universal kappa = π/24 = {kappa:.10f}")
print()

def calculate_effective_slope(particle):
    """Calculate ln(m/m_e) / V for a particle (excluding V=0)"""
    if particle['volume'] == 0:
        return None
    return particle['ln_m_over_me'] / particle['volume']

# Leptons (excluding electron)
print("LEPTONS (N = 20):")
lepton_slopes = []
for p in leptons:
    slope = calculate_effective_slope(p)
    if slope is not None:
        lepton_slopes.append(slope)
        print(f"  {p['name']:10s}: V={p['volume']:7.4f}, "
              f"ln(m/me)={p['ln_m_over_me']:7.4f}, "
              f"slope={slope:.6f}")

lepton_avg = np.mean(lepton_slopes)
lepton_std = np.std(lepton_slopes)
print(f"  Average slope: {lepton_avg:.6f} ± {lepton_std:.6f}")
print(f"  Theoretical 20κ: {20 * kappa:.6f}")
print(f"  Error: {abs(lepton_avg - 20*kappa) / (20*kappa) * 100:.3f}%")
print()

# Bosons
print("BOSONS (N = ?):")
boson_slopes = []
for p in bosons:
    slope = calculate_effective_slope(p)
    if slope is not None:
        boson_slopes.append(slope)
        print(f"  {p['name']:10s}: V={p['volume']:7.4f}, "
              f"ln(m/me)={p['ln_m_over_me']:7.4f}, "
              f"slope={slope:.6f}")

boson_avg = np.mean(boson_slopes)
boson_std = np.std(boson_slopes)
print(f"  Average slope: {boson_avg:.6f} ± {boson_std:.6f}")
print()

# ============================================================================
# PART 2: Test Hypothesis A (N = 3, v8.0 Model)
# ============================================================================

print("PART 2: Hypothesis A - N_boson = 3 (v8.0 Brunnian Model)")
print("-" * 70)

N_A = 3
slope_A = N_A * kappa
print(f"Theoretical slope (3κ): {slope_A:.6f}")
print(f"Observed average:        {boson_avg:.6f}")
print(f"Absolute error:          {abs(boson_avg - slope_A):.6f}")
print(f"Relative error:          {abs(boson_avg - slope_A) / slope_A * 100:.3f}%")
print()

# Calculate predictions for each boson
print("Individual Predictions (N=3):")
predictions_A = []
for p in bosons:
    predicted_ln_m = N_A * kappa * p['volume']
    observed_ln_m = p['ln_m_over_me']
    error = abs(predicted_ln_m - observed_ln_m) / observed_ln_m * 100
    predictions_A.append({
        'name': p['name'],
        'predicted': predicted_ln_m,
        'observed': observed_ln_m,
        'error_pct': error
    })
    print(f"  {p['name']:10s}: predicted={predicted_ln_m:7.4f}, "
          f"observed={observed_ln_m:7.4f}, error={error:6.2f}%")

avg_error_A = np.mean([p['error_pct'] for p in predictions_A])
print(f"  Average prediction error: {avg_error_A:.3f}%")
print()

# ============================================================================
# PART 3: Test Hypothesis B (N = 6, Gemini Model)
# ============================================================================

print("PART 3: Hypothesis B - N_boson = 6 (24/4 Dimensional Model)")
print("-" * 70)

N_B = 6
slope_B = N_B * kappa
print(f"Theoretical slope (6κ): {slope_B:.6f}")
print(f"Observed average:        {boson_avg:.6f}")
print(f"Absolute error:          {abs(boson_avg - slope_B):.6f}")
print(f"Relative error:          {abs(boson_avg - slope_B) / slope_B * 100:.3f}%")
print()

# Calculate predictions for each boson
print("Individual Predictions (N=6):")
predictions_B = []
for p in bosons:
    predicted_ln_m = N_B * kappa * p['volume']
    observed_ln_m = p['ln_m_over_me']
    error = abs(predicted_ln_m - observed_ln_m) / observed_ln_m * 100
    predictions_B.append({
        'name': p['name'],
        'predicted': predicted_ln_m,
        'observed': observed_ln_m,
        'error_pct': error
    })
    print(f"  {p['name']:10s}: predicted={predicted_ln_m:7.4f}, "
          f"observed={observed_ln_m:7.4f}, error={error:6.2f}%")

avg_error_B = np.mean([p['error_pct'] for p in predictions_B])
print(f"  Average prediction error: {avg_error_B:.3f}%")
print()

# ============================================================================
# PART 4: Statistical Comparison
# ============================================================================

print("PART 4: Statistical Comparison")
print("-" * 70)

# Calculate R² for both models
def calculate_r2(predictions):
    """Calculate R² for predicted vs observed"""
    observed = np.array([p['observed'] for p in predictions])
    predicted = np.array([p['predicted'] for p in predictions])
    ss_res = np.sum((observed - predicted)**2)
    ss_tot = np.sum((observed - np.mean(observed))**2)
    return 1 - (ss_res / ss_tot)

r2_A = calculate_r2(predictions_A)
r2_B = calculate_r2(predictions_B)

print(f"Hypothesis A (N=3):")
print(f"  R^2 = {r2_A:.6f}")
print(f"  Average error = {avg_error_A:.3f}%")
print(f"  Slope match = {abs(boson_avg - slope_A) / slope_A * 100:.3f}%")
print()

print(f"Hypothesis B (N=6):")
print(f"  R^2 = {r2_B:.6f}")
print(f"  Average error = {avg_error_B:.3f}%")
print(f"  Slope match = {abs(boson_avg - slope_B) / slope_B * 100:.3f}%")
print()

# Determine winner
print("=" * 70)
print("CONCLUSION:")
print("=" * 70)

if r2_A > r2_B:
    print(f">> Hypothesis A (N=3) is SUPERIOR")
    print(f"  - Better R^2 ({r2_A:.6f} vs {r2_B:.6f})")
    print(f"  - Lower average error ({avg_error_A:.3f}% vs {avg_error_B:.3f}%)")
    winning_N = 3
elif r2_B > r2_A:
    print(f">> Hypothesis B (N=6) is SUPERIOR")
    print(f"  - Better R^2 ({r2_B:.6f} vs {r2_A:.6f})")
    print(f"  - Lower average error ({avg_error_B:.3f}% vs {avg_error_A:.3f}%)")
    winning_N = 6
else:
    print("! INCONCLUSIVE - Both models perform equally")
    winning_N = None

print()

# ============================================================================
# PART 5: Cross-Sector Comparison
# ============================================================================

print("PART 5: Cross-Sector Slope Ratios")
print("-" * 70)

print(f"Lepton slope / Boson slope = {lepton_avg / boson_avg:.4f}")
print(f"Expected if N_lepton=20, N_boson=3: {20/3:.4f}")
print(f"Expected if N_lepton=20, N_boson=6: {20/6:.4f}")
print()

if winning_N == 3:
    expected_ratio = 20/3
elif winning_N == 6:
    expected_ratio = 20/6
else:
    expected_ratio = None

if expected_ratio:
    ratio_error = abs(lepton_avg/boson_avg - expected_ratio) / expected_ratio * 100
    print(f"Ratio match for N={winning_N}: {ratio_error:.3f}% error")

print()
print("=" * 70)
print("Analysis complete. Proceeding to visualization...")
print("=" * 70)

# ============================================================================
# PART 6: Visualization
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('KSAU v10.0: Boson Sector N-Value Determination',
             fontsize=14, fontweight='bold')

# Plot 1: Effective Slopes by Particle
ax1 = axes[0, 0]
particles_for_plot = [p for p in particles if p['volume'] > 0]
x_pos = np.arange(len(particles_for_plot))
slopes_plot = [calculate_effective_slope(p) for p in particles_for_plot]
colors = ['blue' if p['sector']=='Lepton' else 'red' if p['sector']=='Quark'
          else 'green' for p in particles_for_plot]
labels = [p['name'] for p in particles_for_plot]

ax1.bar(x_pos, slopes_plot, color=colors, alpha=0.7)
ax1.axhline(y=20*kappa, color='blue', linestyle='--', linewidth=2,
            label=f'Lepton N=20: {20*kappa:.3f}')
ax1.axhline(y=3*kappa, color='green', linestyle='--', linewidth=2,
            label=f'Boson N=3: {3*kappa:.3f}')
ax1.axhline(y=6*kappa, color='orange', linestyle='--', linewidth=2,
            label=f'Boson N=6: {6*kappa:.3f}')
ax1.set_xticks(x_pos)
ax1.set_xticklabels(labels, rotation=45, ha='right')
ax1.set_ylabel('Effective Slope (ln(m/m_e) / V)')
ax1.set_title('Effective Slopes by Particle')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Predicted vs Observed (Hypothesis A)
ax2 = axes[0, 1]
obs_A = [p['observed'] for p in predictions_A]
pred_A = [p['predicted'] for p in predictions_A]
names_A = [p['name'] for p in predictions_A]
ax2.scatter(obs_A, pred_A, s=200, alpha=0.6, color='green')
for i, name in enumerate(names_A):
    ax2.annotate(name, (obs_A[i], pred_A[i]), fontsize=9, ha='right')
min_val = min(min(obs_A), min(pred_A))
max_val = max(max(obs_A), max(pred_A))
ax2.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect fit')
ax2.set_xlabel('Observed ln(m/m_e)')
ax2.set_ylabel('Predicted ln(m/m_e)')
ax2.set_title(f'Hypothesis A: N=3 (R²={r2_A:.4f}, Error={avg_error_A:.2f}%)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Predicted vs Observed (Hypothesis B)
ax3 = axes[1, 0]
obs_B = [p['observed'] for p in predictions_B]
pred_B = [p['predicted'] for p in predictions_B]
names_B = [p['name'] for p in predictions_B]
ax3.scatter(obs_B, pred_B, s=200, alpha=0.6, color='orange')
for i, name in enumerate(names_B):
    ax3.annotate(name, (obs_B[i], pred_B[i]), fontsize=9, ha='right')
ax3.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect fit')
ax3.set_xlabel('Observed ln(m/m_e)')
ax3.set_ylabel('Predicted ln(m/m_e)')
ax3.set_title(f'Hypothesis B: N=6 (R²={r2_B:.4f}, Error={avg_error_B:.2f}%)')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Error Comparison
ax4 = axes[1, 1]
boson_names = [p['name'] for p in predictions_A]
errors_A = [p['error_pct'] for p in predictions_A]
errors_B = [p['error_pct'] for p in predictions_B]
x_pos_err = np.arange(len(boson_names))
width = 0.35
ax4.bar(x_pos_err - width/2, errors_A, width, label='N=3', color='green', alpha=0.7)
ax4.bar(x_pos_err + width/2, errors_B, width, label='N=6', color='orange', alpha=0.7)
ax4.set_xticks(x_pos_err)
ax4.set_xticklabels(boson_names)
ax4.set_ylabel('Prediction Error (%)')
ax4.set_title('Individual Boson Prediction Errors')
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output_path = Path(__file__).parent.parent / 'figures' / 'boson_N_determination.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {output_path}")

print("\n" + "=" * 70)
print("FINAL RECOMMENDATION:")
print("=" * 70)
if winning_N == 3:
    print("Based on statistical analysis, N_boson = 3 is recommended.")
    print("Geometric interpretation: 3D spatial connection (Brunnian property)")
elif winning_N == 6:
    print("Based on statistical analysis, N_boson = 6 is recommended.")
    print("Geometric interpretation: 24/4 dimensional projection")
else:
    print("Further investigation required - both models need refinement.")
print("=" * 70)
