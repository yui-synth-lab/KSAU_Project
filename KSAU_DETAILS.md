# KSAU_DETAILS.md — 詳細参照ファイル

> このファイルはCLAUDE.mdから切り出した詳細情報です。
> **否定的結果の完全な索引は [NEGATIVE_RESULTS_INDEX.md](NEGATIVE_RESULTS_INDEX.md) を参照。**

---

## プロジェクト管理と技術仕様 (Technical Protocols)

### 1. データ管理とSSoT (Single Source of Truth)
- **原則**: 物理定数や実験値のハードコードを厳禁。
- **データソース**: 
  - `v6.0/data/physical_constants.json` (物理定数)
  - `v6.0/data/topology_assignments.json` (トポロジー割り当て)
  - `v6.0/data/cosmological_constants.json` (宇宙論定数)
- **ユーティリティ**: `v28.0/code/ksau_standard_cosmology.py` 等を経由してデータにアクセスすること。

### 2. 統計的妥当性
- **Bonferroni 補正**: 多重検定の際は必ず独立試行数 $n$ で補正した有意水準 $\alpha/n$ を使用すること。
- **p値基準**: 
  - $S_8$ (Cosmology): **SIGNIFICANT (p=0.00556)**
  - Mass Spectrum (Section 2): **NOT SIGNIFICANT (p>0.0050)**

### 3. Gemini 自己抑制プロトコル (Self-Inhibition Details)
- **再探索禁止**: 既に数学的に閉鎖された経路（WZW、代数的写像、幾何学的 $\alpha_{em}$）の再探索を禁止。
- **用語の厳格化**: 「予言 (Prediction)」は統計的に有意なもの（$S_8$）に限定し、他は「対応 (Correspondence)」または「適合 (Fit)」と呼ぶこと。

---

## バージョン別詳細ステータス

### v36.0 (FINAL ARCHIVE ✅)
**最終ステータス:** ARCHIVED
**成果:**
- $S_8$ 検証設計 (Euclid/LSST) 完成。
- 否定的結果論文 (Negative Results Paper) 作成。
- プロジェクト全アーカイブ完了。

### v30.0 - v35.0 (NEGATIVE RESULTS & CLOSURE)
**成果:**
- WZW 全経路閉鎖 (数学的証明)。
- $q_{mult}=7$ の Free Parameter 確定。
- Section 2/3 の統計的有意性否定 (Bonferroni 補正)。

### v28.0 (STATISTICAL VICTORY)
**成果:**
- 7サーベイ順列検定で $p=0.00556$ を達成。
- $S_8$ テンションの位相的共鳴モデルによる解決。

### v23.0 (σ₈ TENSION FINALITY ✅)
**成果:**
- LOO-CV 厳密化と非線形結び目ダイナミクスの導入。

---

## 主要公式一覧 (Complete Framework)

```
# 宇宙論セクター (Statistically Significant)
S_8(z, k) = S_8(z_CMB) · (1+z)^-γ(k)
γ(k) = Gaussian Resonance based on R_cell ≈ 20 Mpc
p-value = 0.00556 (7 surveys)

# 質量セクター (Phenomenological Fit)
ln(m) = κ·V + c   (R²=0.9998 using q_mult=7)
q_mult = 7 (Free Parameter, Algebraic Origin Unknown)

# CKM混合 (Phenomenological Fit)
logit(V_ij) = C + A·ΔV + B·Δln|J| + ... (R²=0.998 using 5 params)
```

---

## 出版準備状況 (v36.0 Final Status)

| 論文 | ターゲット | 状態 |
|------|-----------|------|
| **Paper 1: Negative Results on Algebraic Mass Origin** | arXiv (hep-th) | **Draft v2 Ready** |
| **Paper 2: S8 Resonance Model & Euclid Verification** | ApJ / MNRAS | **Design Complete** |
| Paper 3: Geometric Origin of SM Parameters | (Withdrawn) | **Merged into Paper 1** |

---

## 既知の限界 (Scientific Integrity)

| 事象 | ステータス | 理由 |
|------|------------|------|
| **$q_{mult}=7$ の起源** | **不明 (Free Param)** | WZW/代数/幾何からの導出は全否定された |
| **Section 2 質量公式** | **統計的有意性なし** | Bonferroni 補正後 $p > 0.05$ |
| **$H_0$ Tension** | **悪化 (17σ)** | KSAU $H_0=76.05$ は Planck $67.4$ と不整合 |
| **$\alpha_{em}$ 幾何学的導出** | **棄却** | 偶然の一致率 87% |

---

*KSAU_DETAILS.md — Last Updated: 2026-02-21 (v36.0 Final)*
