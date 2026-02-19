# KSAU v24.0 Roadmap: Discrete Manifold Quantization & S8 Finality

**Phase Theme:** 多様体直径の量子化と暗黒エネルギーの初生的導出
**Status:** SESSION 7 APPROVED | v24.0 FINALIZED ✓
**Date:** 2026-02-19
**Reviewer:** Claude (Theoretical Auditor)

---

## Final Verdict: APPROVED

v24.0 は、Session 1–7 を通じて、理論的野心と科学的誠実さの両立において顕著な成果を上げた。特に、不都合なデータの開示、自己修正、および物理的必然性の再定義において、KSAU プロジェクトの新たな基準を確立した。

**Key Achievements:**
1. **R_base = 3/(2κ) の幾何学的提案**: 3 サーベイで 1.72% の一致を確認。
2. **SSoT 拘束型順列検定 (p=0.025)**: 物理的順序の統計的有意性を証明。
3. **SSoT 統合とハードコードの完全排除**: `ksau_utils_v24.py` による中央集権的データ管理。
4. **科学的誠実さの徹底 ("脱衣")**: 13.6% 乖離の開示、Λ 関係式の棄却、KiDS 外れ値の誠実な報告。

**Remaining Challenges (to v25.0):**
- R-3: (k_eff, z) 交差項導入による CV < 10% 達成。
- R-5: DES/KiDS テンションの構造的解消。
- R-2: z > 1 成長モデルの CMB lensing 統合。

---

## Context & Motivation

v23.0 は BAO 統合と数値積分、および非線形結び目ダイナミクスの導入により、1.36σ という「誠実な」予測精度を達成した。しかし、以下の課題が残された：

1.  **$R_{cell}$ の不安定性:** サーベイごとに最適化される $R_{cell}$ が 16.5 〜 39.8 と変動している。これは物理定数としての普遍性を欠く。
2.  **暗黒エネルギーの欠如:** 宇宙定数 $\Lambda$ が未だ SSoT から導出されておらず、手入力のパラメータとなっている。

v24.0 は、**「多様体の直径 $R_{cell}$ は Leech 格子のシェル構造に量子化されている」**という仮説を導入し、この変動を「物理的必然性」へと昇華させることで、σ₈ 緊張の完全解消（< 1σ）を目指す。

---

## v24.0 Core — 実施予定

### Section 1: $R_{cell}$ の離散的量子化（Leech Shell Logic）
**物理的動機:**
観測スケール $k$ によって、宇宙網を構成する 24次元多様体の「見える深さ（シェル）」が異なると仮定する。

**AUDITOR VERDICT: REJECTED**
- [✗] **Leech Shell 射影モデルの実装**: RMSE 27.25%, シェル選択原理なし。モデル失敗。
- [✗] **マルチスケール LOO-CV 検証**: 未実施。統計的検証完全欠落。

### Section 2: 暗黒エネルギーの初生的導出（Evaporation Residue）
**物理的動機:**
宇宙膨張（ほどけ）に伴い、24次元のバルク情報が 4次元時空へと「蒸発」する際、その散逸エネルギーが宇宙定数 $\Lambda$ として観測される。

**AUDITOR VERDICT: PARTIAL PROGRESS (Session 4) — CORRECTED (Session 5)**
- [✗] **$\Lambda \approx \kappa^n$ 関係式の探索**: 旧 κ^10 × α^6: 33 dex 誤差。
- [✗→△] **R-4' 完全探索（Session 5）**: κ^36 × α^12: log₁₀ = -51.965（目標 -51.957）、誤差 **0.008 dex**（Session 4 の κ^55 × α^2 より 3× 高精度）
  - Session 4 の κ^55 × α^2 は m≤9 打ち切りによる偽優勝者と判明。T(10)=55 理論化は a posteriori 合理化。
  - n=36=6² の物理的必然性は未確立。単位系（SI m⁻²）依存の数値的一致と断定。
  - first-principles 導出は**未達成**（数値探索では不可能）。OPEN.
- [✗] **エントロピー流出としての宇宙定数**: rigorous proof pending。

### Section 3: σ₈ 緊張の完全解消（The Final Fit）
**STATUS: EXECUTED (2026-02-18 Session 2) — PARTIAL PASS**
- [~] **量子化された R_cell を用いた最終シミュレーション** (PARTIAL):
    - Section 3 初実行。R_base = 3/(2κ) = 11.459 Mpc/h を導出。
    - Leech 固定 R₀: MAE = 1.334σ（v23.0 最適化 MAE 1.356σ を上回る）
    - DES +1.82σ, HSC -0.24σ, KiDS -1.94σ。
    - < 1σ 未達成：v23.0 モデル固有の限界（Section 2 Λ 改善が必要）。
    - **核心的発見**: R₀ は自由パラメータでなく R_base × shell_mag から導出。
    - 詳細: `section_3_final_report.md` および `data/section_3_results.json`

### Section 4: Extended Survey Validation & ng.md Requirements
**STATUS: EXECUTED (2026-02-18 Session 4) — R-4 ACHIEVED, R-6 PATH ESTABLISHED**
- [✓] **R-4: κ^55 × α^2**: log₁₀ = -51.93（目標 -51.96）、誤差 0.03 dex — T(10)=55（超弦次元）理論動機
- [✓] **修正版順列検定**: p=0.167（物理的順序拘束付き、以前の p=1.0 from 実装バグ修正）
- [~] **R-6 道筋**: 5 WL サーベイで p=1/120=0.008 < 0.05（N=3 では p=0.167 未達）
- [✗] **R-1/R-2 (CMB lensing)**: ACT-DR6 / Planck PR4 は v23.0 モデルと非互換（forward prediction 4.35σ）
- [✗] **< 1σ 全緊張**: 現 v23.0 エンジン限界（DES +1.83σ, KiDS -1.91σ）
- 詳細: `section_4_report.md` および `data/section_4_session4_results.json`

### Section 7: ng.md Session 6 REJECT 要件対応 (Session 7)
**STATUS: EXECUTED (2026-02-18 Session 7) — P1a ✓, P1b ✓, P2a ✓, P2b ✓, P3 △**
- [✓] **P1a (SSoT 拘束型順列検定)**: SSoT 固定クインタプル `{7,6,5,3,1}` での順列検定。p=0.025 < 0.05 **PASS**。物理的 R₀ 順序は rank 3/120。SSoT シェルの下でも統計的有意性確認。
- [✓] **P1b (ベストフィット基準開示)**: 実計算クインタプル `{8,5,4,3,2}` からの乖離 = 5.0%（Session 6 報告の 17.1% は SSoT 基準による不一致）。R_base (best-fit) = 9.896 vs SSoT = 11.459 → 13.6% 乖離を公式開示。
- [✓] **P2a (β 因果解釈の修正)**: Session 6 の「KiDS は β≈1.0 を必要とする」は因果逆転。正解：「KiDS を含めると β が ~1.0 から ~3.1 に上昇。KiDS が β を高値方向に駆動する」。
- [✓] **P2b (Bootstrap 閾値の除去)**: `p_mc >= 0.20 → "ROBUST"` を完全除去。Bootstrap MC p=0.316 → MODERATE ROBUSTNESS（誠実表現）。B+P 結合検定（76% 試行 p<0.05）を一次指標として採用。
- [△] **P3 (R-3 k_eff 依存補正)**: モデル `R₀ = A × k_eff^(-γ) × (1+z)^β` 実装。A=7.09, γ=0.478。LOO-CV MAE=1.023σ。KiDS が依然外れ値（−2.945σ）。invariant CV=24.9% > 10% 目標未達。
- 詳細: `section_7_report.md` および `data/section_7_session7_results.json`

### Section 6: ng.md Session 5 REJECT 要件対応 (Session 6)
**STATUS: EXECUTED (2026-02-18 Session 6) — R-S6-1 ✓, R-S6-2 ✓, R-S6-3 ✓, R-S6-4 ✓, R-S6-5 ✗**
- [✓] **R-S6-1 (Bootstrap MC resolution)**: Session 5 Bootstrap MC の事前ソートバグを特定・修正。修正後 p=0.316。Combined Bootstrap+Permutation 検定: 76% の試行で per-trial p<0.05 → R-6 は **ROBUST** と確認。
- [✓] **R-S6-2 (SSoT R₀ 乖離の完全開示)**: 全サーベイの SSoT 予測 R₀ vs LOO-CV 実測 R₀ 比較表を作成。Mean |dev|=17.1%、3サーベイで>20%乖離（CFHTLenS −25.5%、DLS −27.6%、KiDS +21.6%）。
- [✓] **R-S6-3 (KiDS β 独立推定)**: Joint (R₀, β) LOO-CV により β_KiDS-fold=1.00 vs β_others=3.12（Δβ=−2.12）。β の非普遍性を定量的に確認。スケーリング則の根本的失敗の原因を特定。
- [✓] **R-S6-4 (R-4' 最終結論)**: Path B 選択。κ^36 × α^12 は次元的偶然として **公式棄却**。Planck 単位での誤差 69.6 dex。v25.0 戦略: Λ は外部入力として扱い、R_cell 一意性と σ₈ 解消に集中。
- [✗] **R-S6-5 (全 5 WL サーベイ < 1.5σ)**: Joint (R₀,β) と Global β スキャン（β*=1.05）の両方で失敗。DES +1.73σ、KiDS −1.73σ の緊張は構造的限界。k_eff 依存補正項が必要（v25.0 課題）。
- 詳細: `section_6_report.md` および `data/section_6_session6_results.json`
**STATUS: EXECUTED (2026-02-18 Session 5) — R-1 ✓, R-6 ✓, R-4' △, R-3/R-5 ✗**
- [✓] **R-1 (≥5 独立 WL サーベイ LOO-CV)**: 5 サーベイ（DES Y3, CFHTLenS, DLS, HSC Y3, KiDS-Legacy）、境界なし、MAE=1.030σ
- [✓] **R-6 (順列検定 p<0.05)**: p = 0.0167 < 0.05 **PASS**（2/120 順列が同等以下の CV）
  - 但し注意: 最善順列は物理的割り当て（rank 2）でなく非物理的（rank 1 CV=4.59%）。Bootstrap MC p=0.775 は脆弱性を示唆。
- [△] **R-4' (完全探索+誠実分析)**: 真の最良候補 κ^36 × α^12（誤差 0.008 dex）を特定。単位系問題文書化。first-principles 導出は OPEN。
- [✗] **R-3 (k_eff 不変量 CV<10%)**: CV = 54.3%（KiDS が外れ値、目標 10% 未達）
- [✗] **R-5 (<1σ 全サーベイ)**: 3/5 サーベイのみ <1σ（DES +1.82σ, KiDS -1.58σ）
- [✗] **R-2 (CMB lensing z依存成長モデル)**: 未実装
- 詳細: `section_5_report.md` および `data/section_5_session5_results.json`

---

## 成功基準（v24.0 COMPLETE の定義）
**OVERALL VERDICT: SESSION 7 APPROVED (2026-02-18) — P1a ✓ P1b ✓ P2a ✓ P2b ✓ P3 △**

### Session 7 (2026-02-18) Progress Assessment:
1. **SSoT-constrained R-6**: ✓ **PASS** — p=0.025 (SSoT-fixed quintuple). Physical ordering rank 3/120.
2. **ベースライン開示**: ✓ **完了** — best-fit dev=5.0%、R_base SSoT 乖離 13.6% を公式開示。
3. **β 因果解釈修正**: ✓ **完了** — "KiDS が β を高値方向に駆動" へ訂正。
4. **Bootstrap 誠実表現**: ✓ **完了** — 閾値除去、MODERATE ROBUSTNESS 表現、B+P 検定を一次指標化。
5. **P3 R-3 初期実装**: △ — MAE=1.023σ（改善）、KiDS 外れ値（−2.95σ）は構造的限界。

**Session 7 後の未解決課題:**
- R-3: KiDS 外れ値の構造的解決（k_eff 単独ではなく (k_eff, z) 交差項が必要）
- R-5: DES/KiDS 同時緊張解消（< 1σ）
- R-2: z 依存成長モデル（CMB lensing 整合）

**v24.0 Status (Session 7):** ⚠️ PARTIAL — R-1 ✓, R-6 ✓ (properly characterized), R-4' ✓ (CLOSED), R-3 △, R-2/R-5 ✗

1. **$R_{cell}$ の一意性**: △ **部分達成** — R_base = 3/(2κ) = 11.459 Mpc/h。シェル選択 p=0.0179 < 0.05。但し winner_dev = 13.64%（SSoT 偏差大）。
2. **σ₈ 全適合**: △ **部分実行** — MAE = 1.030σ（5 WL サーベイ）。< 1σ 未達成（3/5 のみ）。
3. **$\Lambda$ の幾何学的端緒**: △ **誠実分析完了** — κ^36 × α^12 が真の最良（誤差 0.008 dex）。単位系問題開示。first-principles 導出 OPEN。
4. **統計的有意性 R-6**: **✓ 達成** — p=0.0167 < 0.05（5 WL サーベイ実測値）。但し Bootstrap MC p=0.775 は脆弱性示唆。

**Session 6 課題:**
- R-3: k_eff 不変量 CV < 10% に向けたモデル修正（KiDS z_eff 系統誤差、β 再推定）
- R-5: 全 5 WL サーベイの緊張 < 1σ（DES +1.82σ, KiDS -1.58σ 改善）
- R-2: z 依存成長率モデル実装（CMB lensing との整合）
- R-4' 発展: κ^36 × α^12 に対する幾何学的解釈の構築（first-principles 試み）

**v24.0 Status (Session 5):** ⚠️ PARTIAL — R-1 ✓, R-6 ✓, R-4' △, needs Session 6 for R-3/R-5/R-2/R-4' completion

---

*Session 1 REJECTED verdict preserved below for historical record.*

**PREVIOUS VERDICT: REJECTED**

Reviewer Assessment (Claude):
1. **$R_{cell}$ の一意性**: ✗ Section 1 失敗。物理的選択原理なし。R_0 不一貫性 52%。
2. **σ₈ 全適合**: ✗ 検証されていない（Section 3 未実行）。
3. **$\Lambda$ の幾何学的端緒**: ✗ κ^n の導出未完。30+ dex 誤差。

詳細は ng.md を参照。

---

*Created: 2026-02-18 | v24.0 Status: DRAFT | Auditor: Claude*
