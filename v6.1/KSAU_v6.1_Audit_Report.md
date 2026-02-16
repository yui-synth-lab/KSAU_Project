# KSAU v6.1 Independent Audit Report

**Date:** 2026-02-13
**Auditor:** Claude Opus 4.6
**Scope:** Code execution, SSoT integrity, formula consistency, document-code alignment

---

## Executive Summary

v6.1は「Quantum Topological Interference」フレームワークとしてCKM、PMNS、Dark Matterの3セクターを統一的に扱う意欲的な拡張です。しかし、独立検証の結果、**7つのCritical問題**と**5つのWarning**を発見しました。最も深刻なのは、3つの異なるCKMモデルが文書間で混在しており、コードが実際にどのモデルを実装しているか不明瞭な点です。

### Severity Summary
| Level | Count | Description |
|-------|-------|-------------|
| CRITICAL | 7 | 理論・コード間の矛盾、未使用SSoT、欠落ファイル |
| WARNING | 5 | 精度不足、退化メトリック、文書不整合 |
| INFO | 3 | コード品質、パフォーマンス |

---

## CRITICAL Issues

### C1: CKMモデルが3つ存在し互いに矛盾

v6.1内に3つの異なるCKMモデルが存在します：

| Source | Formula LHS | B |\beta |\gamma | R² claimed |
|--------|-------------|---|------|-------|------------|
| **Paper IV** |\ln\|V_ij\| | -2.36 | -12.22 | なし | 0.7017 |
| **SSoT/Code** | logit(\|V_ij\|) | -5π = -15.71 | -1/(2α) = -68.52 | √3 = 1.73 | なし |
| **Upgrade Log §4** | \|V_ij\| ∝ ... | (J比の3乗) | 0.12 | なし | 0.6717 |

**問題点:**
- Paper IVは `ln|V|` を使い、コードは `logit(|V|) =\ln(|V|/(1-|V|))` を使う → 左辺が異なる
- Paper IVは4項モデル、コードは5項モデル（γ交差項あり）
- Upgrade Log §4の「Cubic Suppression Law」は更に別の指数型モデル
- **どれが「正式」なv6.1モデルかが不明**

**推奨:** 1つのモデルに統一し、Paper IV、Upgrade Log、physical_constants.jsonを全て同期させる。

### C2: v6.1独自SSoTが未使用

`v6.1/data/topology_assignments_optimized.json` が存在するが、**全コードは `utils_v61.load_assignments()` 経由でv6.0のSSoTを読み込んでいる**。

```python
# utils_v61.py line 38
path = Path(__file__).parent.parent.parent / 'v6.0' / 'data' / 'topology_assignments.json'
```

v6.1 optimized JSONの全てのquark topologyが異なるにもかかわらず（例: Up: L7a5→L11n13, Charm: L9a10→L11n64, Top: L10a43→L11a32）、コードが実行するのはv6.0のトポロジーです。

**影響:** v6.1の全CKM結果はv6.0のトポロジーに基づいており、v6.1 Upgrade Logが主張するトポロジー更新は検証されていない。

### C3: CKM Master Formula 精度が壊滅的（Mean Error 290%）

実行結果:
```
Charm-Bottom : Obs 0.0410 → Pred 0.9989 → Error 2336%
Top-Bottom   : Obs 0.9991 → Pred 0.6541 → Error 35%
Global Mean Error: 290.58%
```

特にCharm-Bottom遷移で予測値が0.9989（観測値0.0410の24倍）となっている。Verification Reportはこの問題を「335% error」と報告しているが、実際は**2336%**であり、数値も過小報告されている。

### C4: Paper IV R²=0.70の主張が再現不可能

Paper IVが主張するR²=0.7017は、Paper内の係数（B=-2.36, β=-12.22）を使ったモデルによるもの。しかし：
- コードにこの係数を使った実装が**存在しない**
- `optimize_ckm_coupling.py`（READMEが参照）が**ファイルごと欠落**
- 現在のコードが出力するMean Error 290%は R²≈0.70 と整合しない

### C5: optimize_ckm_coupling.py が欠落

README.mdが参照する `optimize_ckm_coupling.py` がv6.1/code/に存在しない。このスクリプトはUpgrade Log §4の「Cubic Suppression Law (R²=0.6717)」を導出したとされる中心的コードです。

### C6: Muonとν₁のトポロジー衝突

- v6.0 SSoT: Muon = `4_1` (vol=2.03)
- v6.1 PMNS: ν₁候補 = `4_1` (vol=2.03)

同一のトポロジーが荷電レプトン（Muon）とニュートリノ（ν₁）の両方に割り当てられている。KSAUフレームワーク上でのSU(2)パートナー関係として正当化可能かもしれないが、明示的な議論がない。

### C7: Dark Matter質量公式のパラメータ不一致

Upgrade Logの公式:
```\ln(m) = (10/7 · G_catalan) · V - (7 + G_catalan)
slope = 1.3085, intercept = -7.9160
```

コードの実装:
```python
slope = 10 *\kappa  # = 1.3090
intercept = -(7 + 7*kappa)  # = -7.9163
```

κ = 0.1309 vs G_catalan/7 = 0.1308。値は近いが理論的意味が異なる（κはKSAU coupling定数、GはCatalan定数）。どちらが正しいかの記述がない。

---

## WARNING Issues

### W1: PMNS「Unknotting Efficiency」メトリックの退化

候補triplet (4_1, 7_2, 8_9) は全て `unknotting_number = 1` であるため：
```
Efficiency = Volume / UnknottingNumber = Volume
```

メトリックがVolumeと完全に同一となり、「Unknotting Efficiency」という概念が追加的な物理的意味を持っていない。

### W2: PMNS質量階層比の精度不足

Power Law モデル (m ∝ V^λ) の予測:
- Δm²₃₂/Δm²₂₁ = **20.98** (観測値 ≈ **33**)
- 偏差: **36%**

Verification Reportはこれを「physically plausible」と評価しているが、同等のv6.0 CKM対角要素精度（2-3%）と比較すると大幅に劣る。

### W3: DM断面積のモデル選択が恣意的

`dm_shadow_calculation.py` は3つの断面積モデルを提示するが、どれを「公式」とするかの物理的根拠がない：
- Model 1 (Volume only): σ = 1.1×10⁻⁴³ cm²
- Model 2 (Shadow only): σ = 6.1×10⁻⁴⁴ cm²
- Model 3 (Combined): σ = 2.8×10⁻⁴⁶ cm² (LZの2.8倍で除外)

### W4: pmns_boundary_resonance.py の RuntimeWarning

```
RuntimeWarning: invalid value encountered in scalar divide
  slope = np.sum(x*y) / np.sum(x**2)
```

一部のtripletで全距離が0（同一ノット）のケースが処理されていない。結果には影響しないが、コード品質の問題。

### W5: v6.1 optimized JSON のLepton Volume が 0.0

v6.1 optimized JSONで Muon(6_1), Tau(7_1) の volume が 0.0 とされている。しかしKnotInfoでは：
- 6_1: volume = 3.1640 (torus knot、non-hyperbolic → vol=0は正しい)
- 7_1: volume = 0.0 (torus knot → vol=0は正しい)

数値的には正しいが、**非双曲ノットをKSAUの双曲体積ベースフレームワーク内で使う** ことの理論的正当性が未記述。

---

## INFO

### I1: コード重複
`ckm_final_v61.py` と `ksau_ckm_geometric.py` は同一のCKM Master Formulaを実装。出力も完全に同一（Mean Error 290.58%）。1つに統合可能。

### I2: データ読み込みの DtypeWarning
全スクリプトで KnotInfo CSV の mixed types 警告が出る。`low_memory=False` またはdtype指定で解消可能。

### I3: 探索範囲の制限
`pmns_boundary_resonance.py` は検索プールを `df.head(30)` に制限している（line 83）。全候補の探索では異なるtripletが最適解となる可能性がある。

---

## Structural Summary

### v6.1に存在する3つのCKMモデル

```
┌─────────────────────────────────────────────────────────┐
│  Paper IV (R²=0.70)    Code (Master Formula)            │
│\ln|V| = A·dV + B·dlnJ  logit(|V|) = C + A·dV + B·dlnJ│
│    + β/V̄ + C              + β/V̄ + γ·(dV·dlnJ)         │
│  B=-2.36, β=-12.22      B=-5π, β=-1/(2α), γ=√3        │
│  [NO CODE EXISTS]       [CODE EXISTS, Error=290%]       │
├─────────────────────────────────────────────────────────┤
│  Upgrade Log §4 (R²=0.67)                               │
│  |V_ij| ∝ (J_light/J_heavy)³ ·\exp(-0.12·dV)           │
│  [CODE MISSING: optimize_ckm_coupling.py]                │
└─────────────────────────────────────────────────────────┘
```

### SSoT使用状況

```
v6.1/data/topology_assignments_optimized.json  → 未使用
v6.0/data/topology_assignments.json            → 全v6.1コードが参照
v6.0/data/physical_constants.json              → 全v6.1コードが参照（CKM係数含む）
```

---

## Recommendations

### 優先度1: CKMモデルの統一 (CRITICAL)
1. Paper IV、Upgrade Log §4、SSoT geometric_coefficients のうち1つを正式モデルとして選択
2. 残りを明示的に「代替モデル」「旧モデル」として分類
3. 正式モデルの係数をphysical_constants.jsonに格納

### 優先度2: SSoTの整理 (CRITICAL)
1. `utils_v61.py` の `load_assignments()` がv6.1独自のトポロジーを読むように修正するか、
2. v6.1 optimized JSONを削除してv6.0 SSoTを正式採用するか、方針を決定

### 優先度3: 欠落コードの復元 (CRITICAL)
1. `optimize_ckm_coupling.py` を復元または再実装
2. Paper IV の R²=0.70 モデルを実装するスクリプトを追加

### 優先度4: PMNSの改善 (WARNING)
1. Unknotting Number > 1 の候補を含む探索で、Efficiencyメトリックの有効性を再検証
2. 探索プールを `head(30)` から全候補に拡大
3. ν₁=4_1 / Muon=4_1 の衝突を理論的に議論

### 優先度5: DM公式のパラメータ統一 (CRITICAL)
1. Upgrade Log (G_catalan) vs Code (κ) の質量公式パラメータを統一
2. 断面積モデルの物理的根拠を明記

---

## Verification Status by Component

| Component | Runs? | Correct? | Doc Match? | SSoT Aligned? |
|-----------|-------|----------|------------|---------------|
| CKM Master Formula | Yes | No (290% error) | No (3 models) | Partial |
| CKM Geometric | Yes | No (duplicate) | No | Partial |
| PMNS Mass | Yes | Partial (ratio 21 vs 33) | Yes | Yes |
| PMNS Resonance | Yes (warning) | Yes (MSE=5.44) | Yes | Yes |
| DM Scan | Yes | Yes | Partial (formula mismatch) | Yes |
| DM Shadow | Yes | Yes | Yes | Yes |

---

*Generated by Claude Opus 4.6 - KSAU v6.1 Independent Audit*
