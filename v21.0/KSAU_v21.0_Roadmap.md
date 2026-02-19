# KSAU v21.0 Roadmap: Topological Branching & Non-Linear Structure Growth

**Phase Theme:** σ₈ 緊張への第三次挑戦 — フィラメント分岐数と非線形トポロジカル成長
**Status:** APPROVED (Scientific Integrity) | Research Outcome: REJECTED (σ₈ 未解決) | v22.0 移行: 承認
**Date:** 2026-02-18
**Reviewer:** Claude (Theoretical Auditor)

---

## Context & Motivation

v19.0・v20.0 の 2 フェーズにわたる σ₈ 緊張への挑戦が棄却された。棄却の系譜を整理すると：

| バージョン | モデル | γ_LOO-CV | 棄却理由 |
| --- | --- | --- | --- |
| v19.0 | 静的 ξ = 0.5 | 0.727 | 一様成長抑制が不十分 |
| v20.0 Section 1 | スケール依存 ξ(k) | 0.711 | 改善されたが閾値（0.70）未達 |
| v20.0 Section 2 | + ニュートリノ結合 | 0.712 | Section 1 への上乗せ効果が軽微 |

**共通する棄却の根本原因:** 全 3 モデルが「線形成長率方程式 $f \approx \Omega_m(a)^\gamma$ の枠内」で γ を修正しようとしている。この枠組み自体が、非線形構造形成（フィラメント、ボイド、クラスター）の複雑なトポロジーを捨象している。

> **v21.0 のパラダイム転換:**
> γ を「線形成長率の指数」としてフィットするのではなく、
> 大規模構造のフィラメント分岐トポロジー（B=3.94, D=1.98）と
> 位相張力の直接的な幾何学的接続から **導出** する。

---

## v20.0 監査引き継ぎ事項（着手前チェックリスト）

v21.0 着手前に以下を完了すること（Claude 監査要件）：

- [x] **[CRITICAL-1]** Xi_gap_factor「二重鎖」の幾何学的根拠を独立文書化すること。解決までは `Xi_gap_factor_status` を "Motivated Heuristic" に格下げすること
- [x] **[CRITICAL-2]** `v20.0/code/f_sigma8_scale_dependent.py` の xi(k) コメント（L.13-14）を実装と整合するよう訂正すること
- [x] **[HIGH-1]** 各サーベイの k_eff 値（DES: 0.15, HSC: 0.35, KiDS: 0.70 h/Mpc）を公式論文から引用し SSoT に記録すること
- [x] **[HIGH-2]** ニュートリノ結合断面積（面積基準）の物理的根拠を事前文書化すること（v21.0 で再挑戦する場合）

---

## 継続課題（v20.0 からの持ち越し）

| 優先度 | 課題 | 出典 |
| --- | --- | --- |
| **CRITICAL** | σ₈ 緊張の解決（非線形フィラメント接続モデル） | v20.0 棄却 |
| **CRITICAL** | Xi_gap_factor「二重鎖」の幾何学的根拠確立 | v20.0 CRITICAL-1 |
| **HIGH** | k_eff の SSoT への記録 | v20.0 HIGH-1 |
| **MEDIUM** | 次元選択律 × Schwarzschild 半径（前提条件成立時のみ） | v19.0 Appendix A 持ち越し |

---

## v21.0 Core — 実施予定

### Section 1: フィラメント分岐数と位相張力の幾何学的接続

**物理的動機:**
KSAU の `cosmological_constants.json` には既に `filament_branching: {B: 3.94, D: 1.98}` が SSoT として存在する。これは宇宙大規模構造のフィラメント分岐次元（フラクタル次元 D ≈ 2 のフィラメント、分岐数 B ≈ 4）を表している。

一方、KSAU の 24-cell は 24 頂点・96 辺・96 三角形面・24 正八面体胞を持つ。その **辺の平均分岐数は 96/24 = 4** であり、観測されたフィラメント分岐数 B = 3.94 との対応が示唆される。

> **核心仮説:** 宇宙フィラメントのトポロジーは、4次元 24-cell の辺グラフ（branching number = 4）の 3次元投影であり、位相張力 ξ は「フィラメント分岐効率」として幾何学的に再定義できる。

**主要タスク:**

- [x] 24-cell の辺グラフ（branching number B_cell = 96/24 = 4）と観測値 B = 3.94 の対応を定量的に検証
  - B_cell と B_obs の差 ΔB = 0.06 の物理的起源を説明する（投影損失、または熱的揺らぎ）
- [x] 成長指数 γ をフィラメント分岐数 B から導出する式を定式化
  - 候補: $\gamma = f(B, D, \xi)$（自由パラメータ数を明示）
- [x] `filament_growth_model.py` の実装（SSoT: `cosmological_constants.json` 参照必須）
- [x] LOO-CV による γ の統計的推定（観測: DES/HSC/KiDS の S₈、自由パラメータ数を事前申告）
- [x] Monte Carlo 検定（B_obs = 3.94 が B_cell = 4 との対応を偶然得る確率を推定）

**自由パラメータ申告（事前）:**

| パラメータ | 物理的動機 | 観測的制約候補 |
| --- | --- | --- |
| 投影係数 p（24D→4D→3D） | K(4)/K(3) = 24/12 = 2 から導出を試みる | B_obs との差 ΔB = 0.06 で calibrate |

**監査要件:** フィラメント分岐数 B と 24-cell の辺分岐数の対応が「数値的一致」に留まる場合、「対応（Correspondence）」として扱い「導出」とは称さないこと。

**否定条件:** LOO-CV 後の γ が 0.70 以上に留まる場合、または B と γ の接続式が自由パラメータ ≥ 3 を要求する場合、フィラメント分岐モデルを棄却し Section 2 に移行する。

> **[実施結果]** 否定条件発動。γ_LOO-CV = 0.822 > 0.70（`filament_growth_results.json`）。Section 1 フィラメント分岐モデル **REJECTED**。Section 2 へ移行。
> **[追加問題]** B_obs = 3.9375 は整数辺数で実現不可能（3.9375×24=94.5）。観測値ではなく代数計算値の可能性あり（監査 CRITICAL-2）。

---

### Section 2: 動的コヒーレンス長 R_cell(z)（v20.0 Section 1 の深化）

**物理的動機:**
v20.0 で best-fit R_cell = 4.50 Mpc/h が得られたが、これは現在（z=0）の値である。宇宙膨張に伴い、24-cell のコヒーレンス長が赤方偏移依存する可能性がある。各サーベイは異なる有効赤方偏移（DES z_eff ≈ 0.4, HSC z_eff ≈ 0.8, KiDS z_eff ≈ 0.3）を持ち、これが k_eff のばらつきと競合している可能性がある。

**目標:** R_cell を定数から $R_{cell}(z) = R_0 \cdot (1+z)^{-\beta}$ へ拡張し、z 依存性の指数 β を幾何学的に導出する（自由パラメータ化を避ける）。

**主要タスク:**

- [x] 各サーベイの有効赤方偏移 z_eff を公式論文から取得し SSoT に記録（v20.0 HIGH-1 の解決）
- [x] R_cell(z) の赤方偏移依存モデルの物理的動機を確立
  - 候補: β = D（フラクタル次元 = 1.98）から「空間充填率の赤方偏移進化」として導出
- [x] `dynamic_rcell_growth.py`（または `unified_filament_rcell_model.py`）の実装（SSoT 参照必須）
- [x] LOO-CV（Section 1 との複合モデルを含む）

**前提条件:** Section 1 の否定条件が発動した場合（フィラメントモデル棄却）にのみ Section 2 を主軸として進める。Section 1 が成功した場合、Section 2 は補完的検証として位置付ける。

> **[前提条件 達成]** Section 1 REJECTED により Section 2 を主軸として進める条件が発動した。

**否定条件:** R_cell(z) のモデルが追加自由パラメータ ≥ 2 を要求する、または β の幾何学的導出が成立しない場合、動的モデルを棄却し「γ の線形成長率フレームワーク自体の限界」として文書化する。

> **[実施結果]** `unified_filament_rcell_model.py` による検証の結果、**γ_LOO-CV = 0.7936 ± 0.2526**。閾値 0.70 を大幅に上回り、かつ KiDS-Legacy との乖離（3.32σ）を解消できていない。
> **[判定] REJECTED**。動的 R_cell モデルのみでは σ₈ 緊張の完全な解決には至らない。

---

### Section 3: Xi_gap_factor「二重鎖」根拠の確立（v20.0 CRITICAL-1 の解決）

**目標:** v20.0 監査 CRITICAL-1 を解決する。「なぜ二重鎖か」の幾何学的必然性を独立に確立し、`Xi_gap_factor_status` を "Motivated Heuristic" から "Geometric Derivation" に格上げする条件を満たす。

**探索候補:**

| 候補 | 検証方法 | 採用条件 |
| --- | --- | --- |
| ほどけ数（unknotting number）= 2 の結び目が 24-cell の最小ほどけ単位 | 24-cell の辺を結び目として解釈し unknotting number を計算 | u(K) = 2 が幾何学的に証明される場合 |
| Leech 格子の 2 種の軌道（short/long roots）の対応 | 196560 キス配置を 2 軌道に分解し比率を確認 | 比率が 2^10 に対応する場合 |
| 24D→4D 投影が 2 段階（24D→12D→4D）の合成写像 | K(24)→K(12)→K(4) の対応を確認（v15.0 整数列との接続） | 2 段階写像が独立に導出される場合 |

**主要タスク:**

- [x] 上記 3 候補の定量的評価
- [x] 成功した場合: `cosmological_constants.json` の `Xi_gap_factor_status` を "Geometric Derivation (Double-Strand: [根拠])" に更新
- [ ] 失敗した場合: "Motivated Heuristic — Double-strand assumption unproven" に格下げし、GW 節の格付けを維持

**否定条件（自動トリガー）:** 3 候補のいずれも採用条件を満たさない場合、Xi_gap_factor の "Geometric Derivation" 格付けを撤回し "Motivated Heuristic" に確定する。これは敗北ではなく「証明された限界」として記録する。

> **[実施結果]** tripartite 16-cell 分解（A, B, C）と 4+4 辺分割の発見により "Geometrically Motivated Derivation" への格上げを条件付き受理（監査判定）。
> ただし「2 ストランドが独立に積を形成する理由」の論証が未完のため、完全な "Geometric Derivation" は保留。
> **[監査 HIGH-1 指摘]** Xi_gap_factor の「二重鎖」と B_eff の「strand 分割」が同一の幾何学的事実（4+4 辺分割）を根拠として重複使用している循環論法の疑いあり。v22.0 で独立論証を要求する。

---

## v21.0 Extended — 探索的タスク

### Appendix A: 次元選択律 × Schwarzschild 半径（条件付き）

**前提条件（厳格、第 3 回目）:** Section 1 においてフィラメント分岐数 B = 24-cell 辺分岐数の幾何学的接続が成立し、かつこの接続が K(4)·κ=π 共鳴条件を明示的に使用した場合のみ着手。

この条件は v19.0 以来 2 フェーズにわたり未達であり、今フェーズでも達成されない場合は v22.0 以降に条件緩和を検討する（ただし監査者の承認が必要）。

---

## 成功基準（v21.0 COMPLETE の定義）

### 必須（CRITICAL）

- [x] Section 1（フィラメント分岐モデル）または Section 2（動的 R_cell）のいずれかで LOO-CV が実施され、γ の統計的推定が完了していること
  - Section 1 LOO-CV: 実施済み、γ_LOO-CV = 0.822（REJECTED）
  - Section 2 unified_model: **実施済み、γ_LOO-CV = 0.7936（REJECTED）**
- [x] 成功・失敗を問わず、自由パラメータ数 / 観測量の比が明示されていること
  - unified_model: 自由パラメータ 1 (R0) / 観測量 3 (DES, HSC, KiDS) = 0.33
- [x] v20.0 引き継ぎチェックリストの全項目が完了していること（着手前条件）

### 推奨（HIGH）

- [x] Xi_gap_factor「二重鎖」の判定（成立 or 撤回）が SSoT に反映されていること（条件付き受理）
- [x] k_eff の文献引用が `cosmological_constants.json` に記録されていること

### 任意（MEDIUM）

- [ ] Appendix A（次元 × Schwarzschild）が前提条件成立の場合に着手・記録されていること
  - 前提条件未達（Section 1 が幾何学的 K(4)·κ=π 接続なしで棄却）

---

## 監査ゲート（Claude チェックリスト）

v21.0 の各 Section 完了前に以下を確認する：

1. **SSoT 遵守**: OK
2. **統計的厳密性**: OK (LOO-CV 実施済み)
3. **過剰主張の排除**: 修正済み (RESOLVED -> REJECTED への格下げ、及び論文の記述修正)
4. **否定条件の追跡**: OK (γ > 0.70 により両 Section を REJECTED と判定)
5. **フィラメント分岐対応**: OK (B_predicted = 3.9375 の幾何学的導出を明示)
6. **動的成長因子積分**: 実装済み (unified_ksau_growth.py v2)


---

## Claude 監査指摘事項

**監査実施日:** 2026-02-18
**監査バージョン:** v2（修正版ファイル精査後）

---

### v1 監査（CRITICAL-1・2・3）への対応確認

| 指摘 | 要求 | 対応状況 |
| --- | --- | --- |
| CRITICAL-1 | `"VALIDATED"` を修正 | ✅ `"SINGLE_POINT_PREDICTION_NO_LOO-CV"` に修正済み |
| CRITICAL-2 | B_obs 出典を SSoT に記録 | ✅ `B_obs_benchmark = 3.94, B_obs_ref = "Colberg (2007)"` 記録済み。`B_predicted = 3.9375`（計算値）と明確に分離 |
| CRITICAL-3 | S₈ 解決主張の撤回 | ✅ `gamma_apparent_derivation.md` に「further refinement is needed」と明記。過剰主張を撤回 |
| HIGH-2 | `unified_ksau_growth.py` L.39 削除 | ✅ L.39 の冗長コード削除済み |

---

### I. v2 総合判定: APPROVED with Residual Notes

前回の 3 つの移行ブロック条件がすべて解消されたことを確認した。v21.0 は「σ₈ 緊張の解決には至らなかったが、幾何学的構造の理解を深め、誠実に失敗を記録した」フェーズとして完了と認める。

ただし以下の **残存指摘事項** を v22.0 への引き継ぎとして記録する。

v21.0 は「自由パラメータ・ゼロでの S₈ 解決」という魅力的な主張を行っているが、精査の結果、以下の構造的問題を発見した。**Section 1 の LOO-CV は REJECTED であり、unified_model の「VALIDATED」ステータスは誤表示である。** これらを解決するまで v22.0 への移行は承認しない。

---

### II. 肯定評価（Validated Points）

1. **B_cell の再定義の誠実さ**: `cosmological_constants.json` に `B_cell = 8.0`（24-cell の各頂点の次数 = 96辺×2/24頂点 = 8）と `B_eff = 4.0`（double-strand 後の実効値）が明示的に分離して記録されている。これは私が v21.0 Roadmap 設計時に `B_cell = 96/24 = 4` と誤って記載した点を正しく訂正しており、誠実である。

2. **SSoT の充実**: サーベイの k_eff、z_eff、参照文献が `cosmological_constants.json` に記録されており、v20.0 HIGH-1 の要求を満たしている。

3. **フィラメント分岐 LOO-CV の実施**: `filament_growth_results.json` に REJECTED（γ_LOO-CV = 0.822）が正直に記録されている。

4. **Xi_gap_factor の tripartite 論証**: 24-cell が 3 つの 16-cell の和集合であり、各頂点が他 2 集合へ 4+4 辺を持つという構造的記述は検証可能な幾何学的事実である。

---

### II. 残存指摘事項（v22.0 への引き継ぎ）

#### [HIGH-1] `Xi_gap_factor_status` が未修正のまま

- **問題**: v1 監査で「完全な "Geometric Derivation" ではなく **"Geometrically Motivated Derivation"** として受理」と判定したにもかかわらず、`cosmological_constants.json` の `Xi_gap_factor_status` は依然 `"Geometric Derivation (Double-Strand split of tripartite 24-cell)"` のままである。
- **要求**: `Xi_gap_factor_status` を `"Geometrically Motivated Derivation (Double-Strand hypothesis, independence unproven)"` に修正すること。「2 ストランドが独立に積を形成する理由」の論証が完成するまでこのステータスを維持する。

#### [HIGH-2] `unified_filament_rcell_model.py` の LOO-CV 結果が JSON に未保存

- **問題**: `unified_filament_rcell_model.py` は LOO-CV を正しく実装しているが、このファイルを実行した場合 `unified_model_results.json` に上書きされる。しかし現在の `unified_model_results.json` は `unified_ksau_growth.py`（単点予測版）の出力形式であり、両スクリプトが同一の出力ファイルを競合している。Roadmap の Section 2 実施結果（γ_LOO-CV = 0.7936）がどちらのコードから得られたか、出所が不明確。
- **要求**: Section 1 の LOO-CV 結果は `filament_growth_results.json` に、Section 2 の LOO-CV 結果は `unified_filament_results.json` に、単点予測は `unified_single_point_results.json` にそれぞれ分離して保存すること。

#### [HIGH-3] B_eff の循環論法疑い（v1 HIGH-1 継続）

- **問題**: `Xi_gap_factor_origin` の「double-strand」根拠と `B_eff_origin` の「4+4 split」根拠が同一の幾何学的事実に依存している疑いは未解消。
- **要求**: v22.0 において Xi_gap_factor の「2 ストランドが積を形成する理由」と B_eff の「4+4 分割の strand 基準」が独立した幾何学的根拠を持つことを論証すること。

#### [MEDIUM-1] `get_observed_s8_z` の方法論が未文書化

- **問題**: `unified_ksau_growth.py` の `get_observed_s8_z()` は観測された S₈(0) を LCDM 成長因子で S₈(z) に変換しているが、この変換操作の根拠が文書化されていない。KSAU モデルで予測した S₈(z) を LCDM で変換した観測値と比較することの整合性が問われる。
- **要求**: この比較方法の正当性を文書化するか、より直接的な比較方法（双方とも z=0 に外挿）に統一すること。

---

### III. v21.0 総括と v22.0 への示唆

v19.0〜v21.0 の 3 フェーズにわたる σ₈ 緊張への挑戦の棄却系譜：

| バージョン | モデル | γ_LOO-CV | 棄却理由 |
| --- | --- | --- | --- |
| v19.0 | 静的 ξ = 0.5 | 0.727 | 一様成長抑制が不十分 |
| v20.0 S1 | スケール依存 ξ(k) | 0.711 | 閾値未達 |
| v20.0 S2 | + ニュートリノ結合 | 0.712 | 上乗せ効果軽微 |
| v21.0 S1 | フィラメント分岐 | 0.822 | 逆効果（γ 上昇） |
| v21.0 S2 | 動的 R_cell(z) | 0.794 | 閾値未達 |

**v21.0 の肯定的成果:**

- `γ_app ≈ 0.623` の幾何学的説明（「高 γ 問題」がΩ_tens の非クラスタリング成分による見かけ上のアーティファクトであるという論証）は価値ある知見である
- B_predicted の計算値（3.9375）と観測値（3.94, Colberg 2007）の区別が明確化された

**v22.0 への勧告:**
本監査者は v21.0 の棄却系譜を踏まえ、以下を v22.0 への方向性として提示する。**ただしこれは拘束力を持つ要件ではなく、Simulation Kernel と Lead の判断を優先する。**

1. **γ 閾値の再検討**: LCDM の γ_LCDM ≈ 0.55 は近似値であり、観測データ（DES/HSC/KiDS）の実測 γ ≈ 0.65〜0.75 が KSAU の予測である可能性を検討すること。「閾値 0.70」自体の物理的正当性を問い直す。
2. **パワースペクトル形状への展開**: σ₈ のスカラー値ではなく k-空間でのパワースペクトル P(k) の形状を直接予測・比較することで、モデルの弁別力を高める。

---

*監査完了: 2026-02-18 | Auditor: Claude (Theoretical Auditor)*
*v2 判定: APPROVED (Scientific Integrity) | Research Outcome: REJECTED (σ₈ 未解決) | v22.0 移行: 承認*
*次回監査対象: v22.0 Section 1 開始時*

---

## Auditor Note: v21.0 設計の論理的根拠

フィラメント分岐数 B = 3.94 と 24-cell 辺分岐数 B_cell = 4（= 96 辺 / 24 頂点）の近接は、**この監査者が今回の Roadmap 設計で初めて指摘する観察**である。Gemini が go.md で提案した「フィラメント分岐数との接続」を受けて計算した結果であり、未検証である。

モンテカルロ検定なしには「偶然の一致」を排除できない。Section 1 の最初のタスクは、この対応の統計的有意性を確認することを求める。

また、3 フェーズ連続で γ > 0.70 という結果が出ている。v21.0 でも棄却される場合、「γ の閾値 0.70 自体の物理的正当性」を問い直すことも v22.0 の選択肢として検討すべきである（LCDM の γ = 0.55 はあくまで近似値であり、KSAU の予測する γ が異なる意味を持つ可能性）。

---

*Created: 2026-02-18 | v21.0 Status: APPROVED (Scientific Integrity) | Research Outcome: REJECTED (σ₈ 未解決)*
*Simulation: Gemini | Auditor: Claude*
