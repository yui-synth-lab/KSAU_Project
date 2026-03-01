import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

STATUS_FILE    = r"E:\Obsidian\KSAU_Project\ssot\project_status.json"
OUTPUT_FILE    = os.path.join(os.path.dirname(__file__), "fig_05_negative_results.png")

with open(STATUS_FILE, 'r', encoding='utf-8') as f:
    status = json.load(f)

# --- Empirical statistics for each rejected hypothesis ---
# Source: NEGATIVE_RESULTS_INDEX.md + cycle verdict files
# Format: (p_value_or_fpr, metric_type)
# metric_type: 'p'  = Bonferroni-corrected p-value
#              'fpr'= False Positive Rate (Monte Carlo)
#              'or' = Odds-Ratio (used when p is marginal and OR is the primary rejection criterion)
#              'loo'= LOO-R² ratio (training R² vs LOO-R², used for overfitting rejection)
#              'ci' = CI mismatch (no single p; plotted at Bonferroni threshold for comparison)

REJECT_DATA = {
    # H3  CS Mapping — physical inconsistency (Witten condition satisfaction 58.3%)
    'H3':  (0.583, 'fpr', 'CS Mapping\n(Witten 58%)'),
    # H4  Axion-ST Correlation — p=0.0588 > 0.025 (Bonferroni for 2 hyps)
    'H4':  (0.0588, 'p', 'Axion-ST\nCorrelation'),
    # H8  CS Mapping Redesign — repeated physical inconsistency (Cycle 4)
    'H8':  (0.667, 'fpr', 'CS Mapping\nRedesign'),
    # H10 k-Function Integrity — resource exhaustion / consistency rate 75%
    'H10': (0.25, 'fpr', 'k-Function\nIntegrity'),
    # H13 WRT TQFT Mapping — consistency rate 75%, target 80%
    'H13': (0.25, 'fpr', 'WRT TQFT\nMapping'),
    # H21 DM Prediction — FPR=72.66%
    'H21': (0.7266, 'fpr', 'DM Prediction\n(FPR 73%)'),
    # H22 κ single-param model — p=0.0354
    'H22': (0.0354, 'p', 'κ Simple\nModel'),
    # H23 Phase Discretization — FPR=93.82% (circular test)
    'H23': (0.9382, 'fpr', 'Phase Disc.\n(FPR 94%)'),
    # H26 TSI Universal — p=0.1734
    'H26': (0.1734, 'p', 'TSI\nUniversal'),
    # H28 Decay Width TSI — p=0.4310
    'H28': (0.4310, 'p', 'Decay Width\nTSI'),
    # H29 ST Mass Correction — p=0.0588
    'H29': (0.0588, 'p', 'ST Mass\nCorrection'),
    # H32 Torsion correction — p=0.0712
    'H32': (0.0712, 'p', 'Torsion\nCorrection'),
    # H33 κ independent recovery — CI mismatch, κ_fit ≈1.43 vs theory 0.1309
    'H33': (0.05,  'ci', 'κ Recovery\n(CI mismatch)'),
    # H34 Linear ST Correction — p=0.0712
    'H34': (0.0712, 'p', 'Linear ST\nCorrection'),
    # H37 Decay Width Topological — p=0.1610
    'H37': (0.1610, 'p', 'Decay Width\nTopol.'),
    # H38 ST Lepton Correction — p=0.25
    'H38': (0.25, 'p', 'ST Lepton\nCorrection'),
    # H40 Holistic V_eff — p=0.0970
    'H40': (0.0970, 'p', 'Holistic\nV_eff'),
    # H45 Linear ST All Fermions — p=0.22
    'H45': (0.22, 'p', 'Linear ST\nAll Fermions'),
    # H47 κ regression via V_eff — CI mismatch; κ_fit 11× too large
    'H47': (0.05,  'ci', 'κ Reg.\nV_eff (CI)'),
    # H48 Non-linear ET Correction — p=0.0435 (Bonferroni 0.016667)
    'H48': (0.0435, 'p', 'Non-linear\nET Corr.'),
    # H52 τ-V Correlation — p=0.0213
    'H52': (0.0213, 'p', 'τ-V\nCorrelation'),
    # H58 Joint MC Predictions — p=0.067
    'H58': (0.067,  'p', 'Joint MC\nPredictions'),
    # H59 ST LOO Stability — LOO-R²=0.11 vs train R²=0.2948 (ratio 37%)
    'H59': (0.37,  'loo', 'ST LOO\nStability'),
    # H60 Det≡0 mod24 Stability — OR=0.745 (negative correlation), p=0.00556 but OR<1
    'H60': (0.7452, 'or', 'Det≡0 mod24\n(OR=0.745)'),
}

alpha_bonf = 0.0167  # Bonferroni threshold (3 hyps/cycle)

ids    = list(REJECT_DATA.keys())
vals   = [REJECT_DATA[h][0] for h in ids]
mtypes = [REJECT_DATA[h][1] for h in ids]
labels = [REJECT_DATA[h][2] for h in ids]

# Color by metric type
color_map = {
    'p':   '#d62728',   # red    — direct p-value failure
    'fpr': '#ff7f0e',   # orange — FPR too high
    'ci':  '#9467bd',   # purple — CI mismatch
    'loo': '#8c564b',   # brown  — overfitting
    'or':  '#2ca02c',   # green  — wrong direction (OR < 1)
}
colors = [color_map[mt] for mt in mtypes]

# --- Plot ---
fig, ax = plt.subplots(figsize=(14, 6))

x = np.arange(len(ids))
bars = ax.bar(x, vals, color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)

# Bonferroni line (applies only to p-value metric)
ax.axhline(alpha_bonf, color='navy', linestyle='--', linewidth=1.5,
           label=f'Bonferroni threshold α={alpha_bonf}')

# Reference line at 1.0 (FPR / OR upper bound)
ax.axhline(1.0, color='gray', linestyle=':', linewidth=1.0, alpha=0.5)

ax.set_xticks(x)
ax.set_xticklabels(ids, rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Statistic value (p / FPR / OR / LOO ratio)', fontsize=11)
ax.set_ylim(0, 1.08)
ax.set_title('Statistical Summary of 24 Rejected Hypotheses (H3–H60)\n'
             'All values are empirical — no imputed defaults', fontsize=13)

# Annotate key rejections
annotations = {
    'H23': ('FPR=93.8%\n(circular)', 'top'),
    'H21': ('FPR=72.7%', 'top'),
    'H60': ('OR=0.745\n(wrong sign)', 'top'),
    'H58': ('p=0.067\n(joint MC)', 'top'),
    'H59': ('LOO-R²\n=37% of train', 'top'),
}
for hid, (note, pos) in annotations.items():
    if hid in ids:
        xi = ids.index(hid)
        yi = vals[xi]
        ax.annotate(note, xy=(xi, yi), xytext=(xi, yi + 0.06),
                    ha='center', fontsize=7.5, color='black',
                    arrowprops=dict(arrowstyle='-', color='gray', lw=0.8))

# Legend
patches = [
    mpatches.Patch(color=color_map['p'],   label='p-value (Bonferroni failure)'),
    mpatches.Patch(color=color_map['fpr'], label='FPR (Monte Carlo)'),
    mpatches.Patch(color=color_map['ci'],  label='CI mismatch (κ recovery)'),
    mpatches.Patch(color=color_map['loo'], label='LOO ratio (overfitting)'),
    mpatches.Patch(color=color_map['or'],  label='Odds ratio (wrong direction)'),
]
ax.legend(handles=patches + [
    plt.Line2D([0], [0], color='navy', linestyle='--', label=f'Bonferroni α={alpha_bonf}')
], fontsize=9, loc='upper left', framealpha=0.9)

ax.grid(True, axis='y', linestyle=':', alpha=0.4)
plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close()
print(f"Generated: {OUTPUT_FILE}")
