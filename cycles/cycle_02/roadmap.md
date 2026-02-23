# AIRDP Roadmap — KSAU Project Cycle 02

**作成日:** 2026-02-23
**Orchestrator:** gemini
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_01\seed.md

## 仮説一覧

| ID | 仮説名 | 優先順位 | 最大イテレーション |
|----|--------|----------|------------------|
| H4 | アキシオン質量とトポロジカル・トーション(ST)の相関 | 高 | 5 |
| H5 | TQFT Chern-Simons レベル k と双曲体積 V の幾何学的対応 | 中 | 5 |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H4     | 既存の fermion 質量公式への ST (Smallest Torsion) 項の導入と残差分析 | [x] |
| 2    | H4     | log(ST) > 2 の部分群におけるアキシオン質量 m_a の回帰分析 | [x] |
| 3    | H5     | 双曲体積 V と Chern-Simons レベル k の相関関数の導出（線形 vs 対数） | [x] |
| 4    | H4     | Jones 多項式以外の不変量（Alexander/A-polynomial）による ST 補完の検証 | [x] |
| 5    | H5     | 修正 Witten 不変量による k-V 対応の統計的検証 | [x] |

> **ルール**: 優先順位が高い仮説を先に配置すること。ただし「高優先仮説がすべての配分を消費してしまう」ことを防ぐため、最高でも全体の 60% を単一仮説に割り当てないこと。

---

## 仮説 H4: アキシオン質量とトポロジカル・トーション(ST)の相関 [Seed H2 MODIFY]

### 帰無仮説 (H0)
アキシオン質量 $m_a$ とトポロジカル・トーション $ST$ (Smallest Torsion) の間には統計的に有意な相関が存在しない。

### 対立仮説 (H1)
アキシオン質量 $m_a$ は双曲体積 $V$ およびトーションの行列式 $ST$ によって記述され、特に $\ln(m_a) = \kappa V - \beta \ln(ST) + C$ の形式で高い相関を示す。

### データ要件
- KnotInfo/LinkInfo における Hyperbolic Volume ($V$)
- KnotInfo における Torsion Invariants ($ST$)
- SSoT (`ssot/constants.json`) の `axion_suppression_model` パラメータ

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.025（= 0.05 / 2）
- 許容誤差: 5%以内
- 最小 $R^2$: 0.75

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- **[Orchestrator補完]** $\log(ST) \le 2$ の領域で相関が消失し、かつ全体での有意性が失われた場合 → REJECT

### テスト手法
既存の fermion 質量回帰モデルに $ST$ を第2独立変数として追加し、赤池情報量規準 (AICc) および LOO-CV MAE で改善を確認する。

### 最大イテレーション数
5

---

## 仮説 H5: TQFT Chern-Simons レベル k と双曲体積 V の幾何学的対応 [Seed H3 MODIFY]

### 帰無仮説 (H0)
Chern-Simons レベル $k$ と双曲体積 $V$ の間には、既存の Witten 不変量を超えた統計的な幾何学的対応は存在しない。

### 対立仮説 (H1)
双曲体積 $V$ の対数または線形項が Chern-Simons レベル $k$ を整数値として誘起し、特定の幾何学的位相（$\pi/24$ 等）を介して結合している。

### データ要件
- KnotInfo/LinkInfo の双曲体積 $V$
- Chern-Simons 不変量データ
- `ssot/constants.json` の `k_mapping_coefficients`

### 成功基準
- p値閾値: 0.05（Bonferroni補正前）
- Bonferroni補正後閾値: 0.025
- **[Orchestrator補完]** 整数値 $k$ への丸め誤差が 10% 未満であること。

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.025 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了
- **[Orchestrator補完]** `Det(K) mod k == 0` の物理的整合性が保てない場合 → REJECT

### テスト手法
モンテカルロ・シミュレーション（N=10,000）を用い、ランダムな体積割り当てと比較して $k-V$ 相関の有意性を検定する。

### 最大イテレーション数
5

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H4 | 3 | Cycle 01 で H1 が成功しており、その拡張である H4 (Axion) の優先度が高いため。 |
| H5 | 2 | 理論的基盤は強固だが、先行研究 (Cycle 04? 等) での否定的結果があるため慎重な配分とする。 |

## キュー（次サイクル候補）
- PMNS 混合行列の幾何学的導出（v7.0 への持ち越し）
- CKM Cabibbo禁止遷移の補正（高次トポロジカル不変量の導入）

## 人間への確認事項
- `seed.md` に記載のあった「Cycle 04 での H3 否定的結果」について、現在の Cycle 01 -> 02 の時間軸との整合性を確認してください。
- アキシオン質量の期待値 $m_a = 0.392$ MeV は一般的な暗黒物質候補としては重すぎるため、KSAU 特有のスケールであることを承認願います。

## SSoT参照
- **SSoT ディレクトリ:** E:\Obsidian\KSAU_Project\ssot
- **定数ファイル:** E:\Obsidian\KSAU_Project\ssot\constants.json
