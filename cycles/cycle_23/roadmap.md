# AIRDP Roadmap — KSAU Project Cycle 23

**作成日:** 2026-02-27
**Orchestrator:** Claude Sonnet 4.6
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_23\seed.md

## SSoT参照

- **定数ファイル:** E:\Obsidian\KSAU_Project\ssot\constants.json
- **仮説定義ディレクトリ:** E:\Obsidian\KSAU_Project\ssot\hypotheses\
- **否定的結果索引:** E:\Obsidian\KSAU_Project\NEGATIVE_RESULTS_INDEX.md
- **⚠️ 注意:** Researcher は上記の絶対パスのみを参照すること。cycles/cycle_23/ 配下に ssot/ を作成してはならない。

---

## 事前スクリーニング記録

### スクリーニング結果サマリー

| 候補 | 定量的? | NEG重複? | スコープ? | 実データ? | 第一原理? | 判定 |
|------|---------|---------|---------|---------|---------|------|
| H58（元 H56 MODIFY） | ✅ 3予測値の数値達成率 | なし（H56はMODIFY、未REJECT） | IN | ✅ 実験値 SSoT 登録済み | ✅ 自由パラメータ=0 | **PASS** |
| H59（元 H57 MODIFY） | ✅ LOO-R², LOO-MAE | H29「再開条件なし」に隣接するが、H34 再開条件「α幾何学的導出」を明示的に満たす形で進める | IN | ✅ フェルミオン9点 SSoT | CONDITIONAL ✅（α導出が鍵） | **条件付きPASS** |
| H60（新規） | ✅ Fisher 正確確率検定 | なし（H55 の ACCEPT 結果の一般化テスト、目的が異なる） | IN | ✅ KnotInfo データベース | ✅ 24-cell対称性から導出 | **PASS** |
| 「π/24 の理論的導出」（seed H59候補） | ❌ 数学的証明タスク、実データ不要 | — | スコープ外（empirical ではない） | ❌ | — | **QUEUE** |

### NEG 重複チェック詳細

- **H59 に関する注意:** NEG-20260225-02 [H29]「再開条件: なし」は、ST 単独の相関テストの限界を指摘。H59 は α を幾何学的定数から理論的に固定（自由パラメータ=1:βのみ）し、NEG-20260225-06 [H34] の再開条件「Torsion 寄与 α の幾何学的導出により自由パラメータを排除した厳密モデルが提示された場合」を正面から満たす形での再挑戦であり、H29 の単純な繰り返しではない。H59 は **H34 の再開条件に基づく正当な再挑戦** として採択する。
- **H60 に関する注意:** H30（DM 候補選定）は `det_mod_24_zero AND tsi_gte_24` を組み合わせ基準として使用済み。H60 はその基準を DM 候補だけでなく **KnotInfo 全 7163 結び目** に適用し、det ≡ 0 (mod 24) と TSI ≥ 24 の間の統計的相関が 24-cell 対称性から予測される独立した幾何学的関係かを検証するものであり、循環論法には当たらない。

### 仮説 ID 採番根拠

既存の最大 H 番号 = **H57**。本サイクルの仮説は H58, H59, H60 として採番する。
H56 および H57 は MODIFY ステータス（未 REJECT）のまま履歴に残り、H58・H59 がそれぞれの改訂版として新規 JSON に定義される。既存の H56.json, H57.json は上書きしない。

---

## 仮説一覧

| ID | 仮説名 | 優先順位 | 最大イテレーション | 元ID |
|----|--------|----------|------------------|------|
| H58 | ジョイントMC検定による定量的予測の統計的確立 | 高 | 4 | H56 MODIFY 再試 |
| H59 | LOO-CV検証とα理論導出によるST補正質量モデルの確立 | 高 | 4 | H57 MODIFY 再試 |
| H60 | Det ≡ 0 (mod 24) 条件と位相安定性の相関検証 | 中 | 3 | 新規 |

---

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説 ID とタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H58    | 3予測値（アクシオン, 重力, Top崩壊幅）の個別 z-score 計算と Bonferroni N=3 統合フレームワーク実装 | [x] |
| 2    | H58    | ジョイント MC 置換検定の実施（n=10000, seed=42、3変数の同時ランダム置換） | [ ] |
| 3    | H58    | 個別 Bonferroni 評価 (N=3, p < 0.016667) と統合レポート作成 | [x] |
| 4    | H58    | [バッファ: MODIFY 発生時のみ使用。通常は未使用] | [x] |
| 5    | H59    | α = 0.18512 の導出式探索（SSoT 定数 G_catalan=0.915966, κ=0.130900, π=3.141593 の組み合わせ）と derivation_formula の確定 | [x] |
| 6    | H59    | 固定α・固定γ（= -v_borromean = -7.327724753 または理論値）での β 単回帰と LOO-CV 実施（LOO-MAE, LOO-R², 各Leave-Out残差を明示） | [x] |
| 7    | H59    | γ と SSoT v_borromean の 1.5% 乖離の理論的説明（固定値か独立パラメータかを明示）と最終結果レポート | [x] |
| 8    | H59    | [バッファ: MODIFY 発生時のみ使用。通常は未使用] | [x] |
| 9    | H60    | KnotInfo 全データ（交差数 3–12, N=7163）における det(K) mod 24 と TSI(K) の計算・分布確認 | [x] |
| 10   | H60    | Fisher 正確確率検定（det ≡ 0 mod 24 × TSI ≥ 24 の 2×2 分割表）と Bonferroni 補正後 p 値の評価 | [x] |
| 11   | H60    | 結果統合レポート（相関係数、オッズ比、95%CI、Bonferroni 補正 p 値の明示） | [x] |

> **ルール:** 優先順位が高い仮説（H58, H59）を先に配置。H58 は全体の 4/11 = 36.4%、H59 は 4/11 = 36.4% を占め、単一仮説への 60% 上限を遵守。H60 は残りの 3/11 = 27.3% を使用。

---

## 仮説 H58: ジョイントMC検定による定量的予測の統計的確立

> **[MODIFY 再試 — 元 H56]** Judge verdict による必須修正項目を完全実施する。

### 帰無仮説 (H0)

アクシオン質量 m_a=12.16 μeV、重力偏差 ΔG/G=8.43×10⁻⁶、Top 崩壊幅 Γ=1321 MeV の3予測を同時評価するジョイント MC 置換検定において、Bonferroni 補正後 p ≥ 0.016667 となり、統計的有意性が認められない。

### 対立仮説 (H1)

KSAU 24-cell フレームワーク（K(4)×κ=π, κ=π/24）から純粋に導出された固定予測値（自由パラメータ数 = 0）に対し、アクシオン・重力・Top の3予測の同時達成率はランダム置換より有意に高く、ジョイント MC 検定の Bonferroni 補正後 p < 0.016667 を達成する。個別 z-score の Bonferroni N=3 統合評価においても各予測が p < 0.016667 を達成する。

> **導出元:** SSoT constants.json の固定値を使用。axion_prediction.m_a_uev=12.16、gravity.gravity_deviation=8.43e-6、particle_data.quarks.Top.sm_decay_width_mev=1321.0。理論予測値は完全に固定（フィッティングなし）。

### データ要件

実験データ（SSoT から読み込むこと、ハードコード禁止）:
- **アクシオン:** SSoT `axion_prediction.m_a_uev`=12.16、実験窓 `axion_exclusion.admx_2023.mass_range_uev`=[11.0, 14.0]
- **重力:** SSoT `gravity.G_corrected`=6.708056580391778e-39 vs `gravity.G_newton_exp`=6.708e-39、`gravity.gravity_deviation`=8.43e-6
- **Top 崩壊幅:** SSoT `particle_data.quarks.Top.sm_decay_width_mev`=1321.0（予測）、`observed_decay_width_mev`=1420.0、`observed_decay_width_err_mev`=180.0

### 物理的制約（PHYSICAL CONSTRAINTS）

> **⚠️ 重要:** 以下の制約は成功の「目標値」ではなく、モデルが満たすべき「物理的条件」である。

- **自由パラメータ数:** 0（全予測値は SSoT から固定。フィッティング一切禁止）
- **適用範囲:** アクシオン・重力・Top の全3予測を同時評価すること。個別評価のみによる ACCEPT は不可
- **導出要件:** 予測値は SSoT に記録された KSAU 理論値をそのまま使用。後付け調整禁止
- **MC 検定の実装:** 3変数を「同時」にランダム置換（独立置換の積ではなく、同一置換インデックスを共有する joint test）

### 統計的有意性基準

- Bonferroni 補正後閾値（本サイクル N=3）: **p < 0.016667**（= 0.05 / 3、SSoT `statistical_thresholds.bonferroni_base_alpha` / 本サイクル仮説数）
- FPR（モンテカルロ置換検定, n=10000, seed=42）: **< 50%**（SSoT `statistical_thresholds.fpr_rejection_threshold`）
- ジョイント MC のサンプル数: SSoT `statistical_thresholds.monte_carlo_n_trials`=10000

### 撤退基準（削除不可）

- ジョイント MC 検定の Bonferroni 補正後 p > 0.016667 → **即座に REJECT**
- FPR > 50% → **即座に REJECT**
- 自由パラメータが導入された場合（予測値の後付け調整） → **即座に MODIFY**
- 4 イテレーション到達で進展なし → **REJECT**
- Reviewer の連続 STOP 判定 2 回 → **強制終了**

### テスト手法

1. 各予測値の z-score を計算: z_i = (predicted_i - observed_i) / σ_observed_i
2. ジョイント検定統計量: χ² = Σ z_i²（χ²(3) 分布）またはフィッシャーの結合 p 値法
3. MC 置換: 3予測に対し同一のランダムインデックスを適用した joint permutation test (n=10000, seed=42)
4. 個別 Bonferroni 評価: 各 z_i の p 値が 0.016667 未満かを確認
5. 全結果を results.json に記録（個別 z-score、個別 p、joint p、FPR を含む）

### 最大イテレーション数

4（バッファ 1 回を含む）

---

## 仮説 H59: LOO-CV検証とα理論導出によるST補正質量モデルの確立

> **[MODIFY 再試 — 元 H57]** 3 つの必須修正項目（LOO-CV 未報告、α 導出式未記載、γ SSoT 不整合）を完全解決する。

### 帰無仮説 (H0)

線形 ST 補正モデル ln(m) = κV + α·ln(ST) + γ + β において、係数 α を KSAU 幾何学的定数（G_catalan, κ, π）から理論的に導出することができない。または、理論導出された α で固定した場合、LOO-CV による汎化性能が著しく劣化する（LOO-R² < training R² × 0.95、または LOO-MAE > 2 × training MAE）。

### 対立仮説 (H1)

α は KSAU フレームワークにおける幾何学的「Action per Torsion unit」として第一原理から導出（例: G_catalan × κ や π/k_resonance × 何らかの定数比など、SSoT 定数の組み合わせ）され、α を固定した単回帰（β のみが自由パラメータ, k=1, N=9, k/N=0.11 < 1/3）が以下を同時に達成する:
- LOO-R² ≥ training R² × 0.95
- LOO-MAE ≤ 2 × training MAE
- γ は SSoT `topology_constants.v_borromean`=7.327724753 から理論的に固定（または乖離 1.5% の幾何学的説明が提示）される
- Bonferroni 補正後 p（β ≠ 0 検定）< 0.016667

> **導出要件の明示:** H1 の核は「α が SSoT 定数の組み合わせとして一意に導出される」こと。α = 0.18512 をそのまま使うことは禁止。Researcher は SSoT constants.json の数値のみを使った閉じた式を提示すること。

### データ要件

SSoT `particle_data.quarks` および `particle_data.leptons` の全 9 フェルミオン（Up, Down, Strange, Charm, Bottom, Top, Electron, Muon, Tau）の `observed_mass`。ST（Smallest Torsion）値は topology_assignments.json または SSoT 経由で取得。κ = SSoT `mathematical_constants.kappa` = 0.1308996938995747。

### 物理的制約（PHYSICAL CONSTRAINTS）

> **⚠️ 重要:** 以下の制約は成功の「目標値」ではなく、モデルが満たすべき「物理的条件」である。

- **適用範囲:** 全フェルミオン 9 点（Up, Down, Strange, Charm, Bottom, Top, Electron, Muon, Tau）に普遍的に適用。一部のみへの適用は MODIFY
- **最大自由パラメータ数:** 1（β のみ）。α と γ は定数として固定。k/N = 1/9 ≈ 0.11 < 1/3 を満たすこと
- **α の導出要件:** α は SSoT constants.json 内の定数（G_catalan, kappa, pi, k_resonance 等）の四則演算・累乗・対数の組み合わせで閉じた式として導出されること。任意フィッティングによる α = 0.18512 の直接使用は禁止
- **γ の扱い:** γ = -SSoT `topology_constants.v_borromean`（= -7.327724753）に固定するか、別の理論値から導出。独立パラメータとして扱う場合は即座に MODIFY（自由パラメータが β+γ=2 となり制約違反）
- **LOO-CV 必須:** results.json に LOO-MAE, LOO-R², 各 Leave-Out 残差（9個）を明示すること。未記載は即座に MODIFY

### 統計的有意性基準

- Bonferroni 補正後閾値（本サイクル N=3）: **p < 0.016667**（β ≠ 0 の F 検定または t 検定）
- FPR（モンテカルロ置換検定, n=10000, seed=42）: **< 50%**
- LOO 過学習チェック: LOO-R² ≥ training R² × 0.95 かつ LOO-MAE ≤ 2 × training MAE

### 撤退基準（削除不可）

- Bonferroni 補正後 p > 0.016667 → **即座に REJECT**
- FPR > 50% → **即座に REJECT**
- α の幾何学的導出式が提示されない → **即座に MODIFY**
- LOO-CV 結果が results.json に未記載 → **即座に MODIFY**
- γ を独立パラメータとして扱い、自由パラメータ数が 2 以上になった場合 → **即座に MODIFY**
- 物理的制約（上記）を満たさないモデルを提出した場合 → **即座に MODIFY**
- 4 イテレーション到達で進展なし → **REJECT**
- Reviewer の連続 STOP 判定 2 回 → **強制終了**

### テスト手法

1. **α 導出（Iter 5）:** SSoT の G_catalan=0.915966, κ=0.130900, π=3.141593, k_resonance=24 等の組み合わせを系統的に探索し、0.18512 に最も近い閉じた式を確定。理論的正当化（KSAU フレームワーク内での幾何学的意味）を記述
2. **回帰実施（Iter 6）:** α 固定、γ 固定（v_borromean または理論値）、β を OLS 推定。p 値（β ≠ 0 の t 検定）を報告
3. **LOO-CV 実施（Iter 6）:** 9 点の全 Leave-One-Out を実施。各 Leave-Out の residual、LOO-MAE（= mean(|predicted_i - actual_i|) for left-out points）、LOO-R² を results.json に記録
4. **γ 整合性検証（Iter 7）:** sector_offset_gamma = -7.219 と v_borromean = 7.327724753 の 1.5% 乖離を解析。γ = -v_borromean に固定した場合と fitted γ の結果を比較し、物理的意味を記述

### 最大イテレーション数

4（バッファ 1 回を含む）

---

## 仮説 H60: Det ≡ 0 (mod 24) 条件と位相安定性の相関検証

> **[新規仮説 — seed Section 4: H55 成果の一般化]**

### 帰無仮説 (H0)

KnotInfo データベース（交差数 3–12 の全結び目、N ≈ 7163）において、det(K) ≡ 0 (mod 24) を満たす結び目の集合と、TSI(K) ≥ 24 を満たす結び目の集合の間に統計的に有意な正相関は存在しない（Fisher 正確確率検定 p ≥ 0.016667）。

### 対立仮説 (H1)

24-cell 対称性の幾何学的制約（k_resonance=24, K(4)×κ=π）から、安定性を担うトポロジーは行列式が 24 の倍数である必要があり、KnotInfo 全データにおいて {det(K) ≡ 0 mod 24} と {TSI(K) ≥ 24} の間に有意な正の相関が観測される（Fisher 正確確率検定 Bonferroni 補正後 p < 0.016667）。この相関は 24-cell 対称性の普遍性を示す独立した検証となる。

> **導出元:** SSoT `v16_derivation.resonance_identity` = "K(4) * kappa = pi"（24-cell 共鳴条件）。k_resonance=24 は数学的定数として SSoT に登録済み。DM 候補選定（H30）とは独立した一般的検証として設計（全 7163 結び目を対象とし、DM 候補 60 個への限定は行わない）。

### データ要件

- **KnotInfo データベース:** E:\Obsidian\KSAU_Project\data\ 以下の交差数 3–12 の全結び目データ（det, TSI 計算に必要な n, u, s の各不変量）
- **TSI 公式:** SSoT `lifetime_model.stability_index_formula` = "n * u / |s|"（|s|=0 の場合の正則化に注意）
- **k_resonance:** SSoT `mathematical_constants.k_resonance` = 24（ハードコード禁止）
- **tsi_threshold:** SSoT `dark_matter_candidates.tsi_threshold` = 24（ハードコード禁止）

### 物理的制約（PHYSICAL CONSTRAINTS）

> **⚠️ 重要:** 以下の制約は成功の「目標値」ではなく、モデルが満たすべき「物理的条件」である。

- **適用範囲:** KnotInfo 全データ（交差数 3–12、特定の結び目のみを対象とするチェリーピッキングは即座に MODIFY）
- **最大自由パラメータ数:** 0（det mod 24 と TSI はトポロジー不変量であり自由パラメータなし）
- **導出要件:** k_resonance=24 と tsi_threshold=24 は SSoT から読み込むこと。任意の閾値設定は禁止
- **DM候補との独立性:** 60 DM 候補のみを対象とした検定は「循環論法」（選択基準に det_mod_24_zero を使用済み）であるため禁止。全データを使用すること

### 統計的有意性基準

- Bonferroni 補正後閾値（本サイクル N=3）: **p < 0.016667**（Fisher 正確確率検定）
- FPR（モンテカルロ置換検定, n=10000, seed=42）: **< 50%**
- オッズ比 > 1 であること（det mod 24 == 0 が TSI ≥ 24 に対して正の寄与を持つこと）

### 撤退基準（削除不可）

- Fisher 正確確率検定の Bonferroni 補正後 p > 0.016667 → **即座に REJECT**
- FPR > 50% → **即座に REJECT**
- オッズ比 ≤ 1（負または無相関）かつ p > 0.016667 → **REJECT**
- DM 候補 60 個のみを対象とした検定を実施した場合 → **即座に MODIFY（循環論法）**
- 3 イテレーション到達で進展なし → **REJECT**
- Reviewer の連続 STOP 判定 2 回 → **強制終了**
- **[Orchestrator 補完]** TSI = n*u/|s| が定義不能（|s|=0）の場合: 正則化として |s|=1 とするか、TSI=∞（≥ 24）として扱い、処理方針を results.json に明記すること

### テスト手法

1. **Iter 9:** KnotInfo 全データ（交差数 3–12）から det(K) と TSI(K) を計算。2×2 分割表を構築: {det≡0 mod 24} × {TSI≥24}
2. **Iter 10:** Fisher 正確確率検定を実施。p 値、オッズ比、95%CI を報告。モンテカルロ置換検定 (n=10000, seed=42) で FPR を推定
3. **Iter 11:** Bonferroni 補正後 p 値（= p × 3）の評価、全数値を results.json に記録

### 最大イテレーション数

3

---

## リソース配分

| 仮説 | イテレーション配分 | 優先順位 | 全体比率 | 理由 |
|------|------------------|---------|---------|------|
| H58 | 4（バッファ含む） | 高 | 36.4% | MODIFY 再試: 具体的修正内容が明確（joint MC 実装）。3 Iter で完結予定、1 バッファ確保 |
| H59 | 4（バッファ含む） | 高 | 36.4% | MODIFY 再試: α 導出・LOO-CV・γ 整合性の 3 課題。各 1 Iter で対応、1 バッファ確保 |
| H60 | 3 | 中 | 27.3% | 新規仮説: 2Iter で検定完了可能、1Iter をレポートに充当 |
| **合計** | **11** | — | **100%** | 最大単一仮説比率 36.4% < 60% 上限 ✓ |

---

## キュー（次サイクル候補）

- **H61（仮）: π/24 の理論的導出（24-cell 共鳴条件）**（seed Section 4 H59 相当）
  - 除外理由: 数学的証明タスクであり「実データで検証可能な仮説」の定義を満たさない。empirical な検証プロトコルを設計できない。
  - 次サイクル条件: 24-cell 既約表現分解から κ = π/24 を導出する数学的論証を準備し、その論証が KSAU の数値予測に追加の testable な帰結をもたらす場合に再提案すること。

---

## 人間への確認事項

1. **H59 の α 理論導出について:** α = 0.18512 を SSoT 定数（G_catalan=0.915966, κ=0.130900, π, k_resonance=24 等）から導出する閉じた式が Researcher に見つかるか不確実。見つからない場合、H59 は「α 導出不可能」として REJECT になる可能性がある。**承認前に α の候補式（例: G_catalan × κ + 何らかの補正 など）を Researcher に提示することを推奨。**

2. **H60 の「安定粒子」の定義について:** seed では「陽子、光子、ニュートリノ等」が例示されているが、陽子は複合粒子（トポロジー未割り当て）、光子はゲージボソン（既に12粒子に含まれる）、ニュートリノは既に SSoT の leptons に含まれる。本 roadmap では「全 KnotInfo 結び目」に対して det mod 24 と TSI の相関を検証する形（H55 の一般化）に設計変更した。**この設計変更の妥当性を確認すること。**

3. **H59 の γ について:** γ = -v_borromean（理論固定値）とする方針を採用しているが、Iter 10 の fitted γ = -7.219 との 1.5% 乖離が H59 の結果に与える影響は未知。γ を理論値に固定した場合、R² が 0.999718 から低下する可能性がある。**LOO-CV の結果次第では H59 が REJECT になるシナリオも含め、事前の期待値調整を推奨。**

4. **H58 の「ジョイント MC 検定」の実装方法について:** 3変数の同時置換（joint permutation）を採用する設計としたが、代替として Fisher の結合確率法（p_joint = -2Σln(p_i)、χ²(2k) 分布）も有効。どちらのアプローチを優先するかを Researcher に事前に指示することを推奨。

---

*AIRDP Roadmap v1.0 — Cycle 23 | Generated by Claude Sonnet 4.6 | 2026-02-27*
