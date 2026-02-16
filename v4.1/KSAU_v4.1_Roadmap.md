# KSAU v4.1 Roadmap

**Date:** February 6, 2026
**Base Version:** v4.0 (Global MAE 7.9%, Quarks 8.7%, Leptons 6.3%)
**Goal:** 精度改善・理論的統一性の強化

---

## 1. v4.0 課題サマリー

### 1.1 精度面の課題

| 粒子 | トポロジー | v4.0 誤差 | 問題の性質 |
|---|---|---|---|
| **Muon (μ)** | $6_1$ | **+17.8%** | N² スケーリングが N=6 で不適合 |
| **Bottom (b)** | $L10a141$ | **-17.3%** | 系統的過小予測（V=12.276） |
| **Down (d)** | $L6a4$ | **+14.0%** | Borromean rings, V=8G |
| **Top (t)** | $L11a62$ | **+13.1%** | 系統的過大予測（V=15.360） |

- Bottom と Top の偏差が逆方向 → 線形\ln(m) ∝ V が V > 12 で破綻する兆候
- Muon は lepton チャンネル最大の異常値

### 1.2 構造的課題

| # | 課題 | 詳細 |
|---|---|---|
| S1 | Quark-Lepton 非統一性 | Quark は双曲体積 V、Lepton は交差数² N² を使用。統一不変量が不在 |
| S2 | Lepton knot 系列の不規則性 | $3_1$(torus）→ $6_1$（twist）→ $7_1$（torus）の混在に理論的根拠が弱い |
| S3 | Up-type 行列式の不明瞭さ | Det = 18, 12, 124 に $2^k$ のような明確な規則がない |
| S4 | $C_l$ の自由パラメータ | Lepton チャンネルに $C_l \approx -2.503$ が残存。幾何学的導出なし |
| S5 | 7D/9D 分岐の物理的根拠 | 係数 10/7 と 2/9 の第一原理からの導出がない |
| S6 | Catalan 定数 G の出現理由 | LQG/M-theory との接続が定性的議論のみ |
| S7 | ニュートリノ質量の未予測 | 荷電レプトンのみ。ニュートリノは推測止まり |
| S8 | サンプルサイズ n=9 | LOO-CV MAE = 14.9%（in-sample の 1.7 倍） |

---

## 2. v4.1 実施計画

### Phase 1: 重クォーク補正（最優先）

**目標:** Bottom (-17.3%) と Top (+13.1%) の系統的偏差を解消

#### 1A. 非線形補正項の導入
- v4.0 のクォーク質量公式:
  $$\ln(m_q) = \frac{10}{7}G \cdot V - (7+G)$$
- v4.1 候補公式（高次補正付き）:
  $$\ln(m_q) = \frac{10}{7}G \cdot V - (7+G) + \alpha \cdot f(V)$$
- 補正関数 $f(V)$ の候補:
  - **(a)** Bridge number 補正: $f = \beta \cdot \t\text{bridge}(L)$
  - **(b)** Writhe 補正: $f = \beta \cdot \t\text{writhe}(L) / N_{cross}$
  - **(c)** 二次体積補正: $f = \beta \cdot (V - V_0)^2$（$V_0$ は中央値）
  - **(d)** 複素体積/CS項補正: $f = \beta \cdot \t\text{Im}(Vol_{complex})$ (Chern-Simons不変量)

#### 1B. 検証手順
1. SnapPy で全候補リンクの bridge number, writhe, Chern-Simons不変量を取得
2. 各補正モデルで 6-quark 再フィット
3. LOO-CV で過学習チェック（MAE が in-sample の 1.5 倍以内を目標）
4. 補正パラメータ数が増えないモデルを優先

**成功基準:** Quark MAE < 6%, Bottom/Top 個別誤差 < 10%

---

### Phase 2: Muon 異常の解決

**目標:** Muon 誤差を +17.8% → < 8% に低減

#### 2A. Lepton 質量公式の改良
- v4.0: $\ln(m_l) = \frac{2}{9}G \cdot N^2 + C_l$
- 改良候補:
  - **(a)** Twist number 補正: $\ln(m_l) = \frac{2}{9}G \cdot N^2 + \delta \cdot \t\text{twist}(K) + C_l$
  - **(b)** 双曲体積ハイブリッド: Muon ($6_1$) と Tau ($7_1$) は双曲的 → V を活用、Electron ($3_1$) のみ N² を使用
  - **(c)** 統一不変量の探索（Phase 3 と連動）

#### 2B. $6_1$ の特殊性の調査
- $6_1$（Stevedore knot）の全不変量を列挙
- $3_1, 7_1$ との比較で「なぜ $6_1$ だけ外れるか」を特定
- Signature, genus, Alexander polynomial の寄与を検討

**成功基準:** Lepton MAE < 5%, Muon 個別誤差 < 8%

---

### Phase 3: Quark-Lepton 統一不変量の探索

**目標:** Quark と Lepton で異なる不変量を使用する問題（S1）の解消

#### 3A. 候補不変量
| 不変量 | 利点 | 課題 |
|---|---|---|
| Jones 多項式の特定評価値 | 全 knot/link で定義 | 質量との相関が未検証 |
| A-多項式 | 双曲体積を含む | 計算コストが高い |
| Colored Jones polynomial | TQFT と直結 | 高次計算が困難 |
| Khovanov homology | 圏論的に精密 | Link への拡張が非自明 |
| Simplicial volume (Gromov norm) | 非双曲でも定義可 | Torus knot では 0 |

#### 3B. 探索手順
1. $3_1$ (torus, V=0) を含む全 9 粒子で各不変量を計算
2. $\ln(m)$ との相関を検証
3. Quark/Lepton を単一公式で表現できる不変量を探索

**成功基準:** 単一不変量 + 単一公式で Global MAE < 10%

---

### Phase 4: Up-type 行列式の規則性発見

**目標:** Det = 18, 12, 124 の数論的構造を解明（課題 S3）

#### 4A. 分析方針
- 素因数分解: $18 = 2 \cdot 3^2$, $12 = 2^2 \cdot 3$, $124 = 2^2 \cdot 31$
- 世代との関係を調査（Down-type の $2^{k+3}$ に対応する規則があるか）
- 他の候補リンクで Up-type に $2^k$ 類似の規則が成立するか再探索
- Weak isospin doublet 構造（$u/d$, $c/s$, $t/b$）の行列式比を調査

**成功基準:** Up-type 行列式を表現する閉じた数学的規則の発見

---

### Phase 5: 理論的深化

**目標:** 物理的メカニズムの定量化（課題 S5, S6）

#### 5A. 7D/9D 分岐の導出
- M-theory における G2 多様体（7D）コンパクト化と Quark チャンネルの対応
- CY3 × S1 構造（9D = 10 - 1）と Lepton チャンネルの対応
- 超弦理論の Calabi-Yau コンパクト化体積と Catalan 定数の関係

#### 5B. $C_l$ の幾何学的導出
- $C_l = -2.503$ の Catalan 定数・次元パラメータによる表現を探索
- 候補: $C_l = -(2 + G/\pi)$, $C_l = -\ln(4\pi G)$ 等

#### 5C. ニュートリノへの拡張
- Unknot ($0_1$, N=0) → $m_\nu = e^{C_l}$?
- $N=1$ (unknot), $N=2$ ($2_1$ = Hopf link は link なので不適) の帰結
- Majorana vs Dirac の区別がトポロジーに現れるか

---

## 3. 優先度と依存関係

```
Phase 1 (重クォーク補正) ─────────────────┐
                                           ├→ Phase 3 (統一不変量)
Phase 2 (Muon 補正) ──────────────────────┘

Phase 4 (Up-type 行列式) ── 独立に並行可能

Phase 5 (理論的深化) ── Phase 1-3 の結果に依存
```

- Phase 1 と Phase 2 は独立に並行実施可能
- Phase 3 は Phase 1, 2 の結果を踏まえて設計
- Phase 4 は他と独立に実施可能
- Phase 5 は Phase 1-3 の公式が確定した後に着手

---

## 4. 成功指標（v4.1 全体）

| 指標 | v4.0 | v4.1 目標 |
|---|---|---|
| Global MAE | 7.9% | **< 5%** |
| Quark MAE | 8.7% | **< 5%** |
| Lepton MAE | 6.3% | **< 4%** |
| 最大個別誤差 | 17.8% (Muon) | **< 10%** |
| 自由パラメータ数 | 1 ($C_l$) | **≤ 1**（増やさない） |
| LOO-CV MAE | 14.9% | **< 10%** |
| 統一公式 | 2本（Quark/Lepton別） | **可能なら1本** |

---

## 5. 必要リソース

- **SnapPy**: bridge number, writhe, 双曲体積の追加計算
- **KnotInfo / LinkInfo**: 全候補の不変量一括取得
- **SageMath**: Jones 多項式、A-多項式の計算
- **Python**: 統計検証スクリプト（permutation test, bootstrap, LOO-CV）

---

**End of Roadmap**