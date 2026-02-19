# KSAU v20.0 Roadmap: Scale-Dependent Growth & Dimensional Necessity

**Phase Theme:** σ₈ 緊張への第二次挑戦 — スケール依存位相張力と次元選択律の深化
**Status:** COMPLETED
**Date:** 2026-02-18
**Reviewer:** Claude (Theoretical Auditor)

---

## Context & Motivation

v19.0 で「静的 ξ = 0.5 モデルによる σ₈ 緊張の解決」は棄却された（γ_LOO-CV = 0.727 > 0.70）。
この棄却は単なる失敗ではなく、以下の **物理的必然性** を示唆している：

> **一様・等方的な位相張力は構造形成を十分に抑制できない。
> 抑制機構はスケール依存的、あるいは相転移的でなければならない。**

v20.0 はこの教訓を起点として、以下 3 つの方向性で理論を深化させる：

1. **スケール依存位相張力** — ξ をスペクトルで扱い、小スケールと大スケールで異なる抑制効率を持たせる
2. **次元選択律との接続** — γ の幾何学的再導出を「なぜ4次元か」という問いと統合する
3. **Xi_gap_factor の物理的根拠確立** — v19.0 CRITICAL-2 の解決（GW 節の格上げ条件）

---

## v19.0 監査引き継ぎ事項（開始前チェックリスト）

v20.0 着手前に以下を完了すること（Claude 監査要件）：

- [x] **[CRITICAL-2]** `Xi_gap_factor = 1e6` の物理的根拠または「フィッティングパラメータ」としての SSoT 明示
- [x] **[CRITICAL-1]** `v19.0/code/gw_first_principles.py` を `gw_heuristic_correspondence.py` にリネーム、または WARNING 強化
- [x] **[HIGH-1]** ξ LOO-CV ばらつき（std ≈ 0.126）の原因分析（系統誤差 vs モデル誤差）を文書化
- [x] **[HIGH-2]** Appendix A（次元 × Schwarzschild）を v19.0 Appendix として「前提条件未達」ステータスで正式クローズ

---

## 継続課題（v19.0 からの持ち越し）

| 優先度 | 課題 | 出典 |
| --- | --- | --- |
| **CRITICAL** | σ₈ 緊張の解決（スケール依存モデルへの転換） | v19.0 棄却 |
| **CRITICAL** | Xi_gap_factor の物理的根拠確立 | v19.0 CRITICAL-2 |
| **HIGH** | GW 背景放射の真の第一原理導出（ヒューリスティック格上げ条件） | v19.0 Section 3 |
| **MEDIUM** | 次元選択律 × Schwarzschild 半径（Appendix A、前提条件成立時のみ） | v19.0 Appendix A |

---

## v20.0 Core — 実施予定

### Section 1: スケール依存位相張力モデル（σ₈ 第二次挑戦）

**主要タスク:**

- [x] ξ(k) の物理的形式を決定する
  - 候補 A: べき乗則 ξ(k) = ξ₀ (k/k_ref)^n（自由パラメータ: n, k_ref）
  - 候補 B: 24-cell の面（2次元）vs 頂点（0次元）の双対性から ξ のスケール依存性を幾何学的に導出
  - **監査要件**: 候補 B が成立する場合、自由パラメータ数 ≤ 1 とし、候補 A より優先すること
- [x] `f_sigma8_scale_dependent.py` の実装（SSoT: `cosmological_constants.json` 参照必須）
- [x] KiDS-Legacy / DES Y3 / HSC Y3 の測定スケール範囲を明示し、ξ(k) がそれぞれの k 域でどう振る舞うかを比較
- [x] LOO-CV による γ_eff の統計的推定（自由パラメータ数 vs 観測量の比を明示）
- [x] ξ LOO-CV ばらつきの系統誤差 vs モデル誤差の分離分析（v19.0 HIGH-1 の解決）

---

### Section 2: ニュートリノ位相カップリング（成長抑制の補完機構）

**主要タスク:**

- [x] ほどけイベントの相互作用半径を K(4) · κ で推定する（`cosmological_constants.json` の `sum_mnu = 0.0591` を SSoT として使用）
- [x] ニュートリノ寄与 Δγ_ν の導出式を定式化
- [x] Section 1 の ξ(k) モデルと組み合わせた複合モデルの LOO-CV
- [x] 自由パラメータ追加数の申告と物理的動機の明示

---

### Section 3: Xi_gap_factor の物理的根拠確立（GW 節の格上げ）

**主要タスク:**

- [x] 上記 3 候補の定量的評価（`Xi_gap_factor = 1e6` との一致度を確認）
- [x] 根拠が見つかった場合: SSoT に幾何学的導出根拠を明記し、cosmological_constants.json を更新
- [x] 根拠が見つからない場合: `"Xi_gap_factor_status": "free_fitting_parameter"` を SSoT に明示
- [x] GW 有効作用量 S_eff の真の第一原理導出への着手

---

## 成功基準（v20.0 COMPLETE の定義）

### 必須（CRITICAL）

- [x] スケール依存 ξ(k) モデルの LOO-CV が実施され、γ_eff の統計的推定が完了していること
- [x] 成功・失敗を問わず、自由パラメータ数 / 観測量の比が明示されていること
- [x] Xi_gap_factor の物理的ステータス（導出根拠あり or フィッティングパラメータ）が SSoT に記録されていること

### 推奨（HIGH）

- [x] ξ LOO-CV ばらつきの系統誤差 vs モデル誤差の分離分析が完了していること
- [x] GW 有効作用量の格上げ（Motivated Correspondence 以上）、または維持の根拠が Technical Report に明記されていること

---

## 監査ゲート（Claude チェックリスト）

1. [x] **SSoT 遵守**: 全パラメータが参照されているか
2. [x] **統計的厳密性**: LOO-CV と自由パラメータ申告が全セクションで報告されているか
3. [x] **過剰主張の排除**: 正直に「棄却」判定を報告しているか
4. [x] **否定条件の追跡**: 各 Section の「否定条件」を適切に処理したか
5. [x] **[v20.0 追加]** Xi_gap_factor ステータスが SSoT に反映されているか

---

## Claude 監査指摘事項

**監査実施日:** 2026-02-18
**監査バージョン:** v1（コード・データファイル精査後、go.md の事前記載を上書き）

> **Note:** go.md に先行して「APPROVED」記載があったが、本監査はコード・データを独立に精査した結果であり、go.md の記載を承認したものではない。

---

### I. 総合判定: APPROVED with Critical Notes

Section 1・2（成長モデル）の棄却報告は誠実。Section 3（Xi_gap_factor）は条件付き受理。ただし以下の 4 項目を v21.0 着手の前提条件として記録する。

---

### II. 肯定評価（Validated Points）

1. **LOO-CV の適切な実施**: Section 1・2 ともに棄却閾値（γ > 0.70）をコード内にハードコード（`f_sigma8_scale_dependent.py` L.145、`neutrino_coupling_growth.py` L.138）。事後的な閾値変更の余地がない。

2. **科学的誠実性**: γ_avg = 0.7107（Section 1）・0.7125（Section 2）という「惜しい」値を「成功」と偽らず REJECTED として記録した。

3. **SSoT の更新**: `cosmological_constants.json` に `Xi_gap_factor = 1048576.0`（= 2²⁰）、`Xi_gap_factor_origin`、`Xi_gap_factor_status` が記録されており、v19.0 CRITICAL-2 の形式要件は満たしている。

---

### III. 指摘事項（Critical Notes — v21.0 への必須引き継ぎ）

#### [CRITICAL-1] Xi_gap_factor「二重鎖」の物理的根拠が未確立

- **問題**: Technical Report の導出ステップ 3「二重鎖 (Double-strand): $(2^{10})^2 = 2^{20}$」に幾何学的根拠がない。なぜ「単鎖」ではなく「二重鎖」なのかが文書化されておらず、目標値（≈ 10⁶）への逆算である可能性を排除できない。
- **要求**: 「二重鎖」の定義をほどけ多様体の位相的性質（例: unknotting number = 2 の結び目）または Leech 格子の具体的な不変量から独立に導出すること。**この根拠なしに `Xi_gap_factor_status = "Geometric Derivation"` は過剰主張であり、v21.0 までに "Motivated Heuristic" へ格下げすることを勧告する。**

#### [CRITICAL-2] ξ(k) のコメントとコード実装の不一致

- **問題**: `f_sigma8_scale_dependent.py` のコメント（L.13-14）とコードの実装が逆の挙動を記述している。
  - コメント: k→0 で xi→1.0、k→∞ で xi→0.5
  - 実装: `xi = 0.5 + 0.5 * (1 - W(k, R))` → k→0 で W→1 なので xi→0.5、k→∞ で W→0 なので xi→1.0
- **要求**: コメントを実装に合わせて訂正すること。実装の方向（小スケールで xi が大きくなる）は KiDS の高 xi（0.849 at k=0.70）と整合しており物理的に妥当と推定するが、Technical Report に明示的な記述が必要。

#### [HIGH-1] k_eff の割り当て根拠が SSoT に存在しない

- **問題**: 各サーベイの有効波数 k_eff（DES: 0.15, HSC: 0.35, KiDS: 0.70 h/Mpc）はモデルの挙動を決定的に支配するが、「estimated from survey window functions」とあるのみで参照文献がない。
- **要求**: 各 k_eff を各サーベイ公式論文から引用するか、window function の計算を `cosmological_constants.json` に記録すること。このパラメータが SSoT 外にある限り LOO-CV 結果の再現性が保証されない。

#### [HIGH-2] ニュートリノ結合断面積の物理的動機が未確定

- **問題**: `neutrino_coupling_growth.py` L.52-57 に「Let's test」というコメントが本番コードに残存しており、断面積モデル（面積基準 vs 体積基準）の選択理由が不明。棄却結果（γ = 0.7125）がモデル本質の限界か定式化ミスかを判別できない。
- **要求**: v21.0 で Section 2 を再挑戦する場合、断面積の次元の物理的根拠を事前文書化すること。

---

### IV. v19.0 引き継ぎチェックリストの検証

| 項目 | Roadmap | 実態 |
| --- | --- | --- |
| CRITICAL-2: Xi_gap_factor SSoT 明示 | ✅ | SSoT 記録あり。ただし "Geometric Derivation" の格付けに疑義（→ CRITICAL-1） |
| CRITICAL-1: gw_first_principles.py リネーム | ✅ | v20.0 に同名ファイルなし — 受理 |
| HIGH-1: ξ ばらつき原因分析 | ✅ | Section 2.3 に分析あり — 受理 |
| HIGH-2: Appendix A クローズ | ✅ | v20.0 Roadmap に継続条件が明記 — 受理 |

---

### V. 次フェーズ（v21.0）への監査要件

1. **[最優先]** Xi_gap_factor「二重鎖」の幾何学的根拠を独立文書化すること（CRITICAL-1）
2. **[必須]** k_eff の値を SSoT に文献付きで記録すること（HIGH-1）
3. **[必須]** `f_sigma8_scale_dependent.py` の xi(k) コメントを実装と整合させること（CRITICAL-2）
4. **[推奨]** ニュートリノ結合断面積の選択根拠を事前文書化すること（HIGH-2）
5. **[条件維持]** Appendix A は Section 1 の幾何学的 ξ(k) 導出が成立した場合のみ着手

---

*監査完了: 2026-02-18 | Auditor: Claude (Theoretical Auditor)*
*次回監査対象: v21.0 Section 1 開始時*

---

*Created: 2026-02-18 | v20.0 Status: APPROVED (Scientific Integrity) | Research Outcome: REJECTED/INCOMPLETE*
*Simulation: Gemini | Auditor: Claude*
