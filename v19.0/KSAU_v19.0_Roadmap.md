# KSAU v19.0 Roadmap: Structure Growth Tension Resolution

**Phase Theme:** σ₈ Problem & Cosmological Precision Upgrade
**Status:** APPROVED — Audit (v2) Passed (Scientific Integrity Validated)
**Date:** 2026-02-18
**Reviewer:** Claude (Theoretical Auditor)

---

## Context & Motivation

v18.0 で「ハッブル・テンションの部分的緩和（3σ改善）」と「SPARC 175 銀河の回転曲線全数検証（LOO-CV MAE = 17.7 km/s）」を達成した。しかし以下の未解決事項が残存する：

1. **成長指数の乖離** — 現状 γ ≈ 0.825 は LCDM 期待値（0.55）から大幅に逸脱しており、`f_sigma8_ksau.py` は未実装
2. **σ₈ 緊張の未対応** — Hubble 緊張に並ぶ現代宇宙論の2大テンションの後者が手つかず
3. **Scenario 2 の非物理性** — 動的 Ω_tens モデルなしでは平坦宇宙制約を満たせない
4. **GW 背景放射の理論的不完全性** — Appendix B はオーダー推算に留まり、第一原理導出へのアップグレードが必要
5. **次元数 × Schwarzschild 半径の接続** — idea.md アイデア2が γ の幾何学的再導出と接続できる可能性（検証待ち）

v19.0 はこれらを「宇宙論的精密化」として解決する。

---

## 監査指摘事項 (v1 Audit Response)

- **統計的誠実性**: LOO-CV 結果 (γ ≈ 0.727) が否定条件 (γ ≥ 0.70) を超えていることを認め、理論値 (0.6875) で隠蔽しない。
- **幾何学的解釈**: ξ = 0.5 (24-cell) は理論的「核」であるが、実測値との乖離は Ω_tens の動的進化または抑制の不足を示唆している。
- **物理的再定義**: Section 2 において定数 ξ ではなく動的進化を導入し、データの不一致を物理的に説明する。

---

## 継続課題（v18.0 からの持ち越し）

これらは v18.0 Roadmap の第6回監査指摘に由来し、v19.0 スコープとして正式に継続する。

| 優先度 | 課題 | 出典 |
| --- | --- | --- |
| **CRITICAL** | 成長指数 γ の精密化と `f_sigma8_ksau.py` 実装 | v18.0 第6回 |
| **HIGH** | Scenario 2 動的 Ω_tens モデル（初期宇宙時間進化） | v18.0 go.md |
| **HIGH** | GW 背景放射の有効作用量による第一原理導出 | v18.0 go.md |

---

## v19.0 Core — 実施予定

### Section 1: σ₈ 緊張への KSAU 応答

**目標:** 線形成長率方程式に位相的張力の非線形寄与を組み込み、γ を LCDM 整合値（0.55±0.05）に向けて修正する。

**主要タスク:**

- [x] `f_sigma8_ksau.py` の新規実装（SSoT: `cosmological_constants.json` 参照必須）
- [x] 線形成長率方程式 $f = d\ln D / d\ln a \approx \Omega_m(a)^\gamma$ に $\rho_{\text{tens}}$ 項を追加
- [x] 成長指数の幾何学的再導出 — v18.0 第6回指摘の $\pi/\kappa \approx 24 = K(4)$ 接続を検証
- [x] LOO-CV による γ の統計的推定（自由パラメータ数 vs 観測量の比を明示）
- [x] KiDS / DES / HSC の $S_8 = \sigma_8 \sqrt{\Omega_m/0.3}$ 測定値との比較

**否定条件:** LOO-CV 後の γ が 0.70 以上に留まる場合、位相的張力による成長抑制モデルは棄却し、別機構を探索する。 (Result: γ_LOO_CV = 0.727 > 0.70, Static Model REJECTED. Moving to Dynamic Evolution in Section 2.)

---

### Section 2: 動的 Ω_tens モデル（Scenario 2 の物理的再定義）

**目標:** Scenario 2 で発生した平坦宇宙制約違反（Ω_total ≈ 1.018）の根本原因に対応する。Ω_tens を定数と扱う仮定を外し、初期宇宙における位相転移として動的モデル化する。

**主要タスク:**

- [x] $\Omega_{\text{tens}}(a)$ の time-evolution モデルの導出（`dynamic_omega_tens.py` 実装）
- [x] 平坦宇宙制約 $\sum \Omega_i = 1$ の厳密な維持（`Scenario 2_Dynamic` パラメータ算出）
- [x] Scenario 2 の非物理性判断（$\Omega_m < 0$ による棄却）

**否定条件:** 動的モデルが追加自由パラメータ ≥ 3 を要求する場合、または非物理的なパラメータ（$\Omega_m < 0$ 等）を要求する場合、Occam の剃刀に従い Scenario 2 を廃棄し Scenario 1 に一本化する。 (Result: Scenario 2 Dynamic requires $\Omega_m < 0$ to maintain flatness. **Scenario 2 DISCARDED**. Focusing exclusively on Scenario 1.)

---

### Section 3: GW 背景放射の第一原理導出（Appendix B アップグレード）

**目標:** v18.0 で「オーダー推算」と正直に明記した $\Omega_{GW} h^2 = \alpha / (2\Xi_{\text{gap}})$ を、有効作用量を用いた導出へ昇華させる。

**主要タスク:**

- [x] ほどけイベントの有効作用量 $S_{\text{eff}}$ の定式化 (`gw_first_principles.py` 実装)
- [x] $S_{\text{eff}}$ から $\rho_{GW}$ を算出する経路積分の対数スケーリング導出
- [ ] LISA 感度曲線（2034年打ち上げ予定）に対する予測精度の定量評価
- [ ] NANOGrav 15-year との周波数域比較（既存の定性的一致を定量的に検証）

**否定条件:** 有効作用量が既存の閉じた解を持たない場合、「perturbative order-of-magnitude estimate with geometric motivation」として格下げし、Appendix のステータスを変更する。 (Result: Success. Derived $\Omega_{GW} h^2 \approx 1.04 \times 10^{-8}$ from $S_{eff} = \ln(\Xi/24\alpha)$. **ACCEPTED as First-Principles Correspondence**.)

---

## v19.0 Extended — 探索的タスク

### Appendix A: 次元数 × Schwarzschild 半径（idea.md アイデア2 より）

**前提条件:** Section 1 の γ 再導出において、$\pi/\kappa \approx 24 = K(4)$ との接続が成立した場合のみ着手。

- [ ] n次元 Schwarzschild 半径の一般式 $r_s^{(n)} \propto (GM/c^2)^{1/(n-2)}$ を KSAU の κ・K(d) で書き直す
- [ ] v18.0 の N=41 効率凍結が4次元固有かどうかを確認（独立条件か従属条件か）
- [ ] 「安定ブラックホール存在条件」と KSAU 次元選択律の比較
- [ ] 各次元での KSAU 8πG 恒等式の類似物を導出（$K(d) \cdot \kappa = \pi$ 共鳴が他次元では何になるか）

**スコープ管理:** この Appendix は v19.0 の核心課題（σ₈ 緊張）を損なわない範囲でのみ進める。数値的一致が出ても「対応（Correspondence）」として扱い、「第一原理導出」とは称さない。

---

## 成功基準（v19.0 COMPLETE の定義）

### 必須（CRITICAL）

- [x] `f_sigma8_ksau.py` が実装され、LOO-CV による γ の統計的推定が完了していること
- [x] γ の LOO-CV 結果と KiDS/DES/HSC の $S_8$ 測定値との比較が定量的に報告されていること
- [x] 自由パラメータ数 / 観測量の比が明示されていること

### 推奨（HIGH）

- [x] 動的 Ω_tens モデルが平坦宇宙制約を満たすこと、または Scenario 2 の廃棄判断が明記されていること
- [x] GW 導出の理論的ステータス（第一原理 or オーダー推算）が論文で正直に記述されていること

### 任意（MEDIUM）

- [ ] Appendix A（次元 × Schwarzschild）が Section 1 の γ 導出と接続された場合、その対応関係の記述

---

## 監査ゲート（Claude チェックリスト）

v19.0 の各 Section 完了前に以下を確認する：

1. **SSoT 遵守**: 全パラメータが `cosmological_constants.json` または同等の SSoT ファイルから参照されているか
2. **統計的厳密性**: LOO-CV と Monte Carlo 検定の結果が全セクションで報告されているか
3. **過剰主張の排除**: "resolves"、"proves"、"first principles" が適切な条件下でのみ使用されているか
4. **否定条件の追跡**: 各 Section の「否定条件」に該当するデータが出た場合、正直に報告されているか
5. **自由パラメータ管理**: 新たに導入するパラメータはその都度、物理的動機と観測的制約を明示すること

---

## Claude 監査指摘事項

**監査実施日:** 2026-02-18
**監査バージョン:** v2（コードおよびデータファイル精査後）

---

### I. 総合判定: APPROVED with Critical Notes

v19.0 は「σ₈ 緊張の解決」ではなく「静的モデルの棄却と正直な限界の文書化」という科学的成果を上げた。Technical Report および Roadmap 上の誠実な失敗報告は、本プロジェクトの科学的誠実性プロトコルに合致する。

ただし以下の **4 項目の指摘事項** を記録し、v20.0 への引き継ぎを義務付ける。

---

### II. 肯定評価（Validated Points）

1. **LOO-CV の適切な実施**: `f_sigma8_ksau.py` は 3 サーベイ（DES Y3 / HSC Y3 / KiDS-Legacy）に対して LOO-CV を実行し、γ = 0.727 ± 0.035 という否定条件（γ > 0.70）超過を正直に報告している。棄却ロジックはコード内にハードコードされており（L.157）、事後的な閾値変更の余地がない。

2. **パラメータ比の透明性**: 自由パラメータ 1（ξ）対観測量 3 という過剰制約系（1:3）を明示。モデルの脆弱性を隠蔽しておらず、SSoT 参照も確認できる。

3. **Scenario 2 の廃棄判断の正当性**: `cosmological_constants.json` に `Scenario 2_Dynamic.omega_m_baseline = -0.01842...` が記録されており、Ω_m < 0 という非物理的結果が実際のコード出力に基づいていることを確認した。廃棄判断は正当である。

4. **GW 格下げの誠実さ**: `gw_first_principles.py` のファイル名は misleading だが、ドキュメント冒頭（L.4–15）に「Heuristic Correspondence」である旨が明記されており、第一原理導出と偽称していない。Technical Report との一致も確認。

---

### III. 指摘事項（Critical Notes — v20.0 への必須引き継ぎ）

#### [CRITICAL-1] `gw_first_principles.py` のファイル名と内容の乖離

- **問題**: ファイル名が `gw_first_principles.py` であるにもかかわらず、内容はヒューリスティックな対応関係（Logarithmic Heuristic Correspondence）である。コードを直接参照するレビュアーが第一原理導出と誤解するリスクがある。
- **要求**: v20.0 では `gw_heuristic_correspondence.py` にリネーム、あるいは冒頭の NOTE をより目立つ形（`WARNING:` プレフィックス等）で明示すること。

#### [CRITICAL-2] Xi_gap_factor の物理的根拠の未明示

- **問題**: `cosmological_constants.json` に `"Xi_gap_factor": 1000000.0` と記載されているが、この値（10⁶）の物理的導出根拠がいかなる文書にも存在しない。`gw_first_principles.py` の S_eff = ln(Ξ/24α) は Ξ に強く依存し、この任意性が GW 予測の信頼性を根本から損なう。
- **要求**: v20.0 において Xi_gap_factor の幾何学的または物理的根拠を第一原理から導出するか、あるいは「フィッティングパラメータ」として明示的に SSoT に記録すること。**この問題が解決されない限り、GW 節の "Logarithmic Heuristic" 格付けは維持する。**

#### [HIGH-1] ξ の LOO-CV ばらつきの解釈不足

- **問題**: LOO-CV の結果として ξ が 0.473（KiDS-Legacy 除外時）から 0.777（DES Y3 除外時）まで変動している（std ≈ 0.126）。Technical Report はこれを「モデルの脆弱性」として記述したが、より具体的な診断が必要である。
  - ξ のばらつきの主因が「サーベイ間の系統誤差」なのか「モデルの自由度不足」なのかが未分離。
- **要求**: v20.0 の Section 1 において、この系統誤差 vs モデル誤差の分離分析を実施すること。

#### [HIGH-2] Appendix A（次元 × Schwarzschild 半径）の前提条件未達と事後処理

- **問題**: Roadmap の Appendix A は「Section 1 の γ 再導出において π/κ ≈ 24 = K(4) との接続が成立した場合のみ着手」という前提条件を設定していた。Section 1 の γ 再導出は棄却されたため、Appendix A への着手条件は満たされていない。しかし go.md の v19.0 Audit Verdict には Appendix A に関する言及がなく、その扱いが宙吊りになっている。
- **要求**: Appendix A を「前提条件未達のため v20.0 に持ち越し」として明示的にステータス更新すること。v20.0 Roadmap では γ の幾何学的再導出が成立した場合にのみ Appendix A の着手許可を与えること。

---

### IV. Roadmap ステータスの齟齬（要修正）

Roadmap 冒頭の `**Status:** APPROVED — Audit (v2) Passed (Scientific Integrity Validated)` という記述について：

- 本レビュー（v2）は「科学的誠実性の観点での APPROVED」であり、「v19.0 の研究目標の達成」を意味しない。
- この区別を冒頭に明記することを推奨する。推奨文言：

  > **Status:** APPROVED (Scientific Integrity) | **Research Outcome:** REJECTED (σ₈ Static Model) / INCOMPLETE (GW First Principles)

---

### V. 次フェーズ（v20.0）への監査要件

v20.0 の開始前に、以下を SSoT として記録することを条件とする：

1. Xi_gap_factor の物理的根拠（またはフィッティングパラメータとしての明示）
2. ξ ばらつきの原因分析（系統誤差 vs モデル誤差）
3. 新たな成長抑制機構（スケール依存性、ニュートリノカップリング等）の物理的動機と自由パラメータ数の事前申告
4. `gw_first_principles.py` のリネームまたはファイル頭部の WARNING 強化

---

*監査完了: 2026-02-18 | Auditor: Claude (Theoretical Auditor)*
*次回監査対象: v20.0 Section 1 開始時*

---

*Created: 2026-02-18 | v19.0 Status: APPROVED (Scientific Integrity) | Research Outcome: REJECTED/INCOMPLETE*
*Simulation: Gemini | Auditor: Claude*
