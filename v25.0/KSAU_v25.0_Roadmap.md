# KSAU v25.0 Roadmap: Scale-Dependent Growth & R₀ Universality

**Phase Theme:** スケール依存スケーリング則と R₀ 普遍性の確立
**Status:** DRAFT — 未着手
**Date:** 2026-02-18 *(W-NEW-1 fix: corrected from 2026-02-19)*
**Reviewer:** Claude (Theoretical Auditor)

---

## Context & Motivation

v24.0 は 7 Session にわたる反復検証を経て、以下の成果と限界を明らかにした：

**v24.0 の確定成果:**
- 5 独立 WL サーベイ LOO-CV: MAE = 1.030σ（v23.0 の 1.356σ から改善）
- 順列検定: SSoT 拘束付き p=0.025 < 0.05（k_eff 順序 ↔ R₀ 順序の有意性）
- κ^n × α^m → Λ: 公式棄却（Planck 単位 69.6 dex 不一致、次元的偶然）
- Bootstrap MC バグ修正・B+P 結合検定: 76% 試行で p<0.05

**v24.0 が残した構造的限界:**
1. **DES/KiDS 逆符号テンション**: DES +1.82σ / KiDS −1.58σ は単一 β で解消不可
2. **R_base SSoT 乖離 13.6%**: SSoT = 11.459 vs best-fit = 9.896 Mpc/h
3. **β 非普遍性**: KiDS 除外で β≈1.0、含むと β≈3.1（Δβ = −2.12）
4. **k_eff 不変量 CV = 24.9%**: 目標 10% に対し 2.5× 超過（KiDS 外れ値）
5. **R-2 (CMB lensing)**: z>1 の成長モデル未実装
6. **SSoT クインタプル {7,6,5,3,1} の導出**: 8 シェルから 5 つを選ぶ first-principles なし

v25.0 は、**DES/KiDS テンションの構造的解消**に集中する。v24.0 の監査報告書が指摘した「(k_eff, z) 交差項モデル」を中核に据え、R₀ 普遍性の再評価と多重検定補正を実施する。

---

## SSoT 確認 (v25.0 で使用する定数)

v23.0 `cosmological_constants.json` から継続。新たなハードコード定数は導入しない。

| 定数 | 値 | 導出 |
|------|-----|------|
| κ | π/24 = 0.130900 | KSAU アクション定数 |
| α | 1/48 = 0.020833 | Pachner 移動結合 |
| β_SSoT | 13/6 = 2.1667 | 幾何学的 z-進化 |
| R_base_SSoT | 3/(2κ) = 11.459 Mpc/h | v24.0 提案（要再評価） |

5 WL サーベイデータ: v24.0 `wl5_survey_config.json` を継続使用。

---

## v25.0 Core — 実施セクション

### Section 1: (k_eff, z) 交差項スケーリングモデル
**Priority: BLOCKING — v25.0 最重要課題**

**物理的動機:**
v24.0 で β が普遍的でない（KiDS Δβ = −2.12）ことが確定した。根本原因は、R₀ のスケーリング則が k_eff と z を独立に扱っている点にある。高 k_eff（小スケール）ではバリオンフィードバックが強く、z-進化の効き方が大スケールとは異なるはずである。

**実装内容:**

#### 1a. 交差項モデルの定式化と fitting
$$R_0(k_{\rm eff}, z) = A \times k_{\rm eff}^{-\gamma} \times (1+z)^{\,\beta_0 + \delta\beta \cdot \ln(k_{\rm eff})}$$

- $\beta_0$: ベースライン z-進化指数
- $\delta\beta$: k_eff 依存の z-進化補正（交差項）
- $A, \gamma$: v24.0 Session 7 の初期推定を出発点（A=7.09, γ=0.478）

5 サーベイの LOO-CV R₀ と (k_eff, z_eff) を用いてフィッティング。

**成功基準:**
- [ ] 5 サーベイ LOO-CV MAE < 0.8σ（v24.0: 1.030σ）
- [ ] DES |tension| < 1.5σ AND KiDS |tension| < 1.5σ（同時充足）
- [ ] k_eff 不変量 CV < 15%（v24.0: 24.9%）

#### 1b. LOO-CV with 交差項
各 LOO fold で (A, γ, β₀, δβ) を 4 訓練サーベイで最適化。held-out サーベイの S₈ 予測精度を評価。

**成功基準:**
- [ ] LOO-CV MAE < 0.8σ
- [x] 過適合検出: 4 パラメータ / 5 データ点 → 自由度比 0.8 の開示が必須

#### 1c. 代替モデル: survey-specific β
交差項が不十分な場合、k_eff 閾値（例: k_eff > 0.5）で β を切り替える Two-regime モデルを検討：
$$\beta(k_{\rm eff}) = \begin{cases} \beta_{\rm low} & (k_{\rm eff} \leq 0.35) \\ \beta_{\rm high} & (k_{\rm eff} > 0.35) \end{cases}$$

**注意:** パラメータ数の増加は過適合リスクを伴う。BIC/AIC で model comparison を実施すること。

---

### Section 2: R_base 普遍性の再評価
**Priority: BLOCKING**

**物理的動機:**
v24.0 で R_base_SSoT = 3/(2κ) = 11.459 と best-fit R_base = 9.896 に 13.6% の乖離が判明。「3=空間次元」の導出根拠が不十分。

**実装内容:**

#### 2a. D を自由パラメータとした LOO-CV 推定
$$R_{\rm base}(D) = \frac{D}{2\kappa}$$

D を [1, 24] の範囲でスキャンし、5 サーベイ LOO-CV MAE を最小化する D_opt を求める。

**成功基準:**
- [x] D_opt の特定と SSoT D=3 との比較
- [x] D_opt が整数（または既知の幾何学的定数）と一致するか検証
- [x] best-fit R_base との乖離が 5% 以内に収まるか

#### 2b. R_base を自由パラメータとした LOO-CV
Section 1 の交差項モデルに R_base を追加し、(R_base, A, γ, β₀, δβ) の 5 パラメータ LOO-CV。
**警告:** 5 パラメータ / 5 データ点 = 完全決定系。LOO-CV の意味が薄れる。AIC/BIC 比較必須。

#### 2c. SSoT R_base の「公式受容」判定
D_opt ≠ 3 の場合、R_base = 3/(2κ) は棄却し、best-fit R_base を新 SSoT として登録するか、あるいは R_base を「近似的 heuristic」として格下げする判断を下す。

**成功基準:**
- [x] R_base の最終ステータスを明確に宣言（SSoT 維持 / 修正 / 格下げ）

---

### Section 3: KiDS z_eff 系統的再推定
**Priority: RECOMMENDED**

**物理的動機:**
KiDS-Legacy の z_eff=0.26 はソース銀河赤方偏移分布 n(z) の「有効値」だが、n(z) のピークは z~0.5 付近。z_eff の定義が他サーベイと異なる可能性がある。

**実装内容:**
- KiDS-1000 n(z) データ（公開済み）から、median z, mean z, S₈-weight z を再計算
- 再推定 z_eff で Section 1 の交差項モデルを再実行し、KiDS 外れ値が改善するか定量評価

**成功基準:**
- [x] z_eff 再推定値の文書化（少なくとも 3 種の定義を比較）
- [x] 再推定 z_eff ≥ 0.40 であれば、Section 1 のモデルを再実行

---

### Section 4: 多重検定補正と統計的頑健性
**Priority: BLOCKING**

**物理的動機:**
v24.0 で 2 種の順列検定（unconstrained p=0.0167, SSoT-constrained p=0.025）を別個に報告。多重検定の補正なし。

**実装内容:**

#### 4a. Bonferroni 補正
- 2 検定 → α_adj = 0.05/2 = 0.025
- SSoT-constrained p=0.025 は Bonferroni 補正後ちょうど境界（p ≤ α_adj）
- この結果を明確に文書化

#### 4b. v25.0 新検定との統合
Section 1 の交差項モデルで新たな LOO-CV を実施した場合、追加の順列検定を行い、全検定（v24.0 + v25.0）に対して FDR (Benjamini-Hochberg) 補正を適用

**成功基準:**
- [x] 全検定の p 値一覧表（補正前 / 補正後）を報告
- [x] 補正後も p < 0.05 を維持する検定の同定

---

### Section 5: CMB Lensing 統合の初期設計（R-2 準備）
**Priority: LONG-TERM（設計のみ）**

**物理的動機:**
v24.0 Session 4 で ACT-DR6 / Planck PR4 の forward prediction が 4.35σ で失敗。v23.0 エンジンは z < 1 WL 向けキャリブレーション。z > 1 では成長率の記述が不正確。

**実装内容（設計ドキュメントのみ）:**
- v23.0 エンジンの `predict_s8_z()` を z > 1 に拡張するためのインターフェース設計
- $D(z)$ 成長関数の Planck ΛCDM 数値積分（z=0 → z=2.5）のプロトタイプ
- ACT-DR6, Planck PR4 のデータ点を v25.0 data/ に追加（forward prediction テスト用）

**成功基準:**
- [x] 設計ドキュメント（仕様書レベル）の作成
- [x] z=0→2.5 成長関数のプロトタイプコード（テスト不要、設計のみ）

---

## 成功基準（v25.0 COMPLETE の定義）

### 必須 (MUST)
1. Section 1: (k_eff, z) 交差項モデルの LOO-CV MAE < 1.0σ — **[FAIL: MAE=1.3251σ (all folds), 過適合確認]**
2. Section 1: DES/KiDS 同時 |tension| < 1.5σ — **[FAIL: KiDS=−3.024σ, DES=1.716σ。β 非普遍性が構造的根拠として確定]**
3. Section 2: R_base の最終ステータス宣言（SSoT 維持 / 修正 / 格下げ）— **[DONE: DOWNGRADED — D=3 導出根拠不十分。best-fit R_base ≈ 9.896 Mpc/h を参照値として記録]**
4. Section 4: 全検定 p 値の多重補正後一覧表 — **[DONE: Section 4 v3 — T1 p_Bonf=0.0334 SIGNIFICANT, T2 p_Bonf=0.050 境界]**

### 望ましい (SHOULD)
5. Section 1: k_eff 不変量 CV < 15%
6. Section 3: KiDS z_eff 再推定の文書化
7. Section 5: CMB lensing 統合の設計ドキュメント

### 理想 (NICE-TO-HAVE)
8. Section 1: LOO-CV MAE < 0.8σ
9. DES/KiDS 同時 |tension| < 1.0σ

---

## 監査プロトコル (Auditor Directive for v25.0)

1. **過適合の厳格な監視**: 4+ パラメータ / 5 データ点は過適合の温床。AIC/BIC でモデル選択を正当化すること。旧モデル（β 固定、2 パラメータ）との定量比較を必須とする。
2. **KiDS 除外版の併記**: KiDS を含む結果と除外した結果を常に併記し、KiDS がモデル全体を支配しているかを可視化する。
3. **SSoT への変更は慎重に**: R_base や β の SSoT 値を変更する場合、変更前後の全メトリクス比較表を必須とする。
4. **否定的結果の価値**: 交差項モデルが失敗した場合（MAE 改善なし）、それ自体が v23.0 エンジンの限界を確定する価値ある結果である。誠実に記録せよ。

---

## リスク評価

| リスク | 影響 | 緩和策 |
|--------|------|--------|
| 交差項モデルの過適合（4 param / 5 data） | 高 | AIC/BIC 比較、LOO-CV で検出、旧モデルとの比較 |
| KiDS z_eff 再推定が変化を生まない | 中 | Section 3 を FAIL として記録、KiDS を系統的外れ値として公式認定 |
| R_base D_opt が非物理的値 | 中 | D を整数に制約したバージョンも並行実行 |
| CMB lensing 設計が v23.0 と非互換 | 低 | v25.0 は設計ドキュメントのみ。実装は v26.0+ |

---

## ファイル計画

| ファイル | 内容 | セクション |
|---------|------|-----------|
| `code/section_1_cross_term.py` | 交差項モデル実装 + LOO-CV | Section 1 |
| `code/section_2_rbase_scan.py` | D スキャン + R_base 再評価 | Section 2 |
| `code/section_3_kids_zeff.py` | KiDS n(z) 再推定 | Section 3 |
| `code/section_4_multiple_testing.py` | 多重検定補正 | Section 4 |
| `code/section_5_cmb_design.py` | CMB lensing プロトタイプ | Section 5 |
| `data/wl5_survey_config.json` | v24.0 から継続（変更なし） | 共通 |
| `data/section_*_results.json` | 各セクション実行結果 | 各セクション |

---

*Created: 2026-02-18 | v25.0 Status: DRAFT | Auditor: Claude (Theoretical Auditor)*
*⚠️ W-NEW-1 fix (Session 4): Creation date corrected from 2026-02-19 → 2026-02-18*

---

## v25.0 Final Status: NEGATIVE RESULT — Engine Limit Confirmed

**Status: COMPLETED-WITH-NEGATIVE-RESULT**
**Recorded: 2026-02-18 (Session 6 ng.md Fix-3)**

### MUST 基準の最終判定

| # | 基準 | 結果 | 値 |
|---|------|------|-----|
| MUST-1 | Section 1 LOO-CV MAE < 1.0σ | **[FAIL]** | MAE=1.3251σ（全 fold）, MAE_valid=0.7689σ（有効 fold 3/5） |
| MUST-2 | DES/KiDS 同時 \|tension\| < 1.5σ | **[FAIL]** | KiDS −3.024σ, DES +1.716σ（β 非普遍性による構造的失敗） |
| MUST-3 | R_base 最終ステータス宣言 | **[DONE]** | DOWNGRADED（D=3 導出根拠不十分）|
| MUST-4 | 全検定 p 値の多重補正後一覧表 | **[DONE]** | T1 p_Bonf=0.0334 SIGNIFICANT, T2 p_Bonf=0.050 境界 |

### 科学的評価

MUST-1/2 の失敗は単純な数値的未達ではない。交差項モデル（4 パラメータ / 5 データ点）は構造的過適合に陥り、かつ 4/5 fold で γ≈0 境界解（=非識別）が確認された。これは v23.0 エンジンのスケーリング則が DES/KiDS テンションの同時解消に原理的に不十分であることを数学的に確定する。

**この否定的結果は価値ある科学的発見であり、v26.0 エンジン刷新の正当な根拠を与える。**
