# AIRDP Roadmap — KSAU Project Cycle 10

**作成日:** 2026-02-24
**Orchestrator:** Gemini-2.0-Flash-Thinking-Exp
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_10\seed.md

## SSoT 参照
- **SSoT ディレクトリ (絶対パス):** `E:\Obsidian\KSAU_Project\ssot`
- **定数ファイル:** `E:\Obsidian\KSAU_Project\ssot\constants.json`
- **仮説定義:** `E:\Obsidian\KSAU_Project\ssot\hypotheses\H*.json`

## 仮説一覧

| ID  | 仮説名 | 優先順位 | 最大イテレーション |
|-----|--------|----------|------------------|
| H22 | Derivation of kappa = pi/24 from Topological Resonance | 高 | 5 |
| H23 | Phase-Discretized Mass Model (K=24) | 高 | 5 |
| H24 | Topological Stability Index for Particle Lifetimes | 中 | 5 |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H22    | 位相幾何学的レゾナンスによる kappa = pi/24 の理論的導出と整合性検証 | [x] |
| 2    | H22    | 4次元 Pachner move と resonance identity K(4)*kappa = pi の幾何学的証明 | [x] |
| 3    | H23    | 位相離散化（K=24）を導入した ln(m) = kappa*V + c モデルの実装 | [x] |
| 4    | H23    | 全12粒子に対する位相離散化モデルの適合度検証と MAE 0.1% 以下への最適化 | [x] |
| 5    | H24    | KnotInfo データを用いた Topological Stability Index (Crossing, Unknotting, Signature) の構築 | [x] |
| 6    | H24    | 実験的な粒子寿命 Gamma と Stability Index の相関分析（R^2 > 0.70 目標） | [x] |
| 7    | H22    | 導出された理論的 kappa を用いた既存質量モデルの再計算と精度検証 | [x] |
| 8    | H23    | 位相離散化モデルにおけるモンテカルロ置換検定による FPR 検証 | [x] |
| 9    | H24    | Stability Index モデルの統計的有意義性（Bonferroni補正後 p値）の最終評価 | [x] |

> **ルール**: 優先順位が高い仮説を先に配置すること。ただし「高優先仮説がすべての配分を消費してしまう」ことを防ぐため、最高でも全体の 60% を単一仮説に割り当てないこと。

---

## 仮説 H22: Derivation of kappa = pi/24 from Topological Resonance

### 帰無仮説 (H0)
質量公式の傾き kappa は経験的なフィッティングパラメータであり、幾何学的不変量 pi とは無関係である（kappa != pi/24）。

### 対立仮説 (H1)
kappa は 4次元 Pachner move における「Action per Move」として定義され、レゾナンス条件 K(4) * kappa = pi (K(4)=24) から一意に導出される。
> **注意:** H22 は KSAU 理論の重力 derivation の最終段階であり、幾何学的安定性から kappa = pi/24 を第一原理として導出する。

### データ要件
SSoT (`constants.json`) の数学的定数および、先行サイクルで検証された質量データ（V, ln_m）。

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** 全12粒子（フェルミオン9 + ボソン3）の質量勾配に対して一貫して適用されること。
- **最大自由パラメータ数:** 0（理論的導出値 pi/24 を固定値として使用）。
- **導出要件:** 任意の多項式フィッティングは厳禁。pi/24 という特定の有理数係数としての必然性を証明すること。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666 (= 0.05 / 3)
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- kappa の理論導出値と経験値の乖離 > 1.0% → 即座に REJECT
- 物理的制約（上記）を満たさないモデルを提出した場合 → 即座に MODIFY
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
理論導出値 kappa = pi/24 を用いた質量予測の残差分析、および幾何学的レゾナンスの数理的証明。

### 最大イテレーション数
5

---

## 仮説 H23: Phase-Discretized Mass Model (K=24)

### 帰無仮説 (H0)
粒子の質量分布は位相幾何学的体積 V に対して連続的であり、離散的な位相レゾナンス構造（K=24）は存在しない。

### 対立仮説 (H1)
質量公式 ln(m) = kappa * V + c において、切片 c は位相レゾナンス K=24 に基づく離散化（Phase-Discretization）を受け、これにより予測精度が MAE 0.1% 以下に向上する。
> **注意:** 離散化の構造は K=24 という幾何学的制約（H22と連動）から導出されるべきであり、残差に合わせた恣意的な離散化は禁止。

### データ要件
SSoT 経由で取得した全12粒子の実験質量および、対応するトポロジーの双曲体積 V。

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** 全12粒子。
- **最大自由パラメータ数:** 最大1つ（離散化の全体的なオフセット等）。
- **導出要件:** 離散化のステップ幅は第一原理（1/24 等）に基づき、各粒子への割り当てはトポロジー的不変量によって決定されること。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 物理的制約（上記）を満たさないモデルを提出した場合 → 即座に MODIFY
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
Phase-Discretized モデルの $R^2$ 評価、および従来の連続モデルとの尤度比検定。

### 最大イテレーション数
5

---

## 仮説 H24: Topological Stability Index for Particle Lifetimes

### 帰無仮説 (H0)
粒子の寿命（Gamma）は位相幾何学的構造（Crossing Number, Unknotting Number 等）とは無関係である。

### 対立仮説 (H1)
Topological Stability Index (TSI) を Crossing Number (n), Unknotting Number (u), Signature (s) の組み合わせとして定義し、これが粒子の崩壊率 ln(Gamma) と強い正の相関 ($R^2 > 0.70$) を持つ。
> **注意:** TSI は「結び目の解けにくさ」や「幾何学的複雑度」を物理的な崩壊耐性として解釈する第一原理的アプローチである。 [Orchestrator補完]

### データ要件
KnotInfo (Real Data) から取得した Crossing Number, Unknotting Number, Signature、および実験的な粒子寿命データ。

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** 寿命が測定されている主要なフェルミオンおよびボソン。
- **最大自由パラメータ数:** 1つ（TSI のスケーリング係数）。
- **導出要件:** 指数は各トポロジー不変量の整数値の組み合わせからなり、連続的な自由パラメータによる調整は禁止。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 物理的制約（上記）を満たさないモデルを提出した場合 → 即座に MODIFY
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
TSI と ln(Gamma) の線形回帰分析、およびトポロジー割り当てをシャッフルしたモンテカルロ置換検定。

### 最大イテレーション数
5

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H22  | 3 | 理論的基盤であり、成功すれば他の仮説の前提となるため。 |
| H23  | 3 | 質量精度の飛躍的向上（0.08%）を検証する重要タスク。 |
| H24  | 3 | 新規領域（寿命）の探索であり、一定のリソースを確保。 |

## キュー（次サイクル候補）
- カビボ禁止遷移の幾何学的抑制モデルの再評価
- ニュートリノ振動パラメータの位相幾何学的導出

## 人間への確認事項
- $\kappa = \pi/24$ の導出において、4次元 Pachner move 以外の幾何学的解釈（例：シンプレクティック幾何）の許容範囲。
- 寿命データのソースとして Particle Data Group (PDG) 2024年版の使用可否。
