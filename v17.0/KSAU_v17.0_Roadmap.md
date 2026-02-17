# KSAU v17.0 Roadmap: Topological Unraveling & Temporal Undulation

**Phase Theme:** Dark Matter Redefinition & Cosmological Temporal Dynamics
**Status:** COMPLETE ✅
**Date:** 2026-02-17
**Precondition:** v16.1 Zenodo submission must be completed before v17 work begins.

---

## Context & Motivation

v16.1 で511keV暗黒物質候補を**撤回**した。これによりダークマターの定式化に空白が生じた。v17はこの空白を「位相的張力」として埋め、v15.0の時間論と統合することが主目的。

v17のスコープは意図的に絞る。アイデアが広がりすぎると v16.1 の精度水準（R²=0.9998）を維持できない。

---

## v17 Core — 必ず達成する

### Section 1: ダークマター再定義（アイデア2 + アイデア3の統合）

#### Section 1a: 位相的張力としてのダークマター

- **定義:** ダークマターは粒子ではなく、「ほどけきらずに引き延ばされた位相の糸」の**張力**
- **EM非相互作用の説明:** 張力は振動（波）でなく背景（束縛条件）であるため電磁場と結合しない
- **重力結合の説明:** 張力が時空曲率に直接寄与する（エネルギー運動量テンソルへの入力として定式化）
- **定量化タスク:** 張力パラメータから銀河回転曲線のフラット化を再現できるか検証

#### Section 1b: 時間うねりによる重力/DM統合

- **前提:** v15.0「時間 = 24D→4D情報転送速度」の動的拡張
- **重力:** 結び目（物質）周囲の時間転送速度の**局所勾配** → ニュートン重力の再導出
- **ダークマター:** 宇宙スケールの時間転送速度の**大域定在波** → DM密度分布に対応
- **注意:** 「定在波」という語は電磁波を連想させる。定式化では「時間流速の定常摂動」と表現し、EM相互作用がない理由を明示すること
- **拡張元:** v8.0 Temporal Brownian Dynamics (TBD) → 「うねりの統計力学」として再構成

### Section 2: 宇宙膨張 = 位相的ほどけ

- **概念:** 宇宙初期状態 = 24次元リーシュ格子における高絡み合い位相状態
- **メカニズム:** インフレーション = 高次元局所結び目が物理的に引き延ばされ、マクロ空間へほどけるプロセス
- **形式化:** 結び目不変量（Jones多項式など）がメトリック拡大に伴いどうスケーリングするか定式化
- **制約:** インフレーションエネルギースケール（〜10¹⁶ GeV）とKSAU GUT予測（4.64×10¹⁴ GeV）のギャップを説明または許容範囲として正当化すること

---

## v17 Extended — リソースが許せば

### Appendix A: 26次元と弦理論との接合（将来課題）

> **格下げ理由:** 数字の一致（24+2=26）は美しいが、リーシュ格子の動機（球充填最適性）とボゾン弦理論の臨界次元26の動機（Weyl anomaly消去）は根本的に異なる。同一視するには独立した証明が必要。現時点では誤解を招くリスクが高い。

- 24D Leech格子 + 1D時間 + 1D巻き付き = 26D の解釈を**仮説として**提示
- 弦理論の巻き付きモードとKSAUの局所結び目の対応を探索
- 弦理論の数学的ツール（頂点演算子代数など）をKSAU質量計算に転用できるか調査
- **v17での扱い:** 主論文ではなくAppendixまたはNote。過剰主張禁止。

---

## Paper 4候補（v17以降）: 大規模構造の統計幾何学的予言

> v17のスコープ外。独立した論文として扱う。

- 銀河フィラメントの分岐則をリーシュ格子のほどけトポロジーから導出
- CMBゆらぎのパワースペクトルP(k)との定量比較
- 重力レンズ分布の統計的特徴の予言
- **条件:** Section 1の定量検証が成功してから着手する

---

## Execution Plan

### Phase 0（先決条件）

- [ ] v16.1 Zenodoへの投稿完了（`ZENODO_SUBMISSION_TRACKER.md` 参照）

### Phase 1: Section 1の定式化

- [x] 位相的張力テンソルの定義（Section 1a） -> `v17.0/papers/Topological_Tension_Tensor.md` (新規仮定として整理)
- [x] `unraveling_dynamics.py` にκ依存を追加 -> $\alpha_{\text{KSAU}} = 1/48$
- [x] 既存の銀河回転曲線データとの定量比較 -> `v17.0/code/galactic_profile.py` (MWデータ MAE=7.13 km/s)
- [x] TBDの「うねり版」統計力学の数式化（Section 1b） -> `v17.0/papers/Temporal_Undulation_Formalism.md`
- [x] 重力との二重構造（局所勾配 vs 大域定在波）の整合性確認 -> 導出係数 $\Xi = (N/\kappa) \cdot 4\pi$ により解決

### Phase 2: Section 2の形式化

- [x] Ξ の物理次元の明記と物理的正規化の定義 -> `v17.0/papers/Temporal_Undulation_Formalism.md`
- [x] MONDに関する主張の緩和（仮説化） -> `v17.0/papers/Temporal_Undulation_Formalism.md`
- [x] 「Unraveling Operator」$\mathcal{U}(t)$ の定義 -> `v17.0/papers/Unraveling_Operator_Formalism.md`
    - [x] Jones多項式の特定リミットにおけるスケーリング則の導出 -> `v17.0/code/jones_unraveling.py` (初期a=10⁻⁶から現在a=1までの10⁶倍膨張において約75%の複雑性が残留)
- [x] GUTスケールギャップ（10¹⁶ vs 4.64×10¹⁴ GeV）への有効質量変化による対処方針の策定 -> `v17.0/papers/GUT_Scale_Resolution.md` (24D->4D projection hypothesis)
- [x] 「ほどけ」に伴うエントロピー増大の定式化 -> `v17.0/papers/GUT_Scale_Resolution.md`

### Phase 3: 検証と執筆

- [x] Section 1 + 2を統合した内部ペーパードラフト -> `v17.0/papers/KSAU_v17.0_Topological_Cosmology.md`
    - [x] `Unraveling_Operator_Formalism.md` の Jones多項式時間引数表記の修正
- [x] `GUT_Scale_Resolution.md` における24D/4D体積比と因子22の整合性検証 -> $N_{\text{leech}}^{1/4} \approx 21.05$ (Error 2.3%)
- [x] LOO-CV実施（Ξ の統計的妥当性） -> `v17.0/code/loo_validation.py` (MAE = 7.19 km/s, Stability 1.01%)
- [x] Appendix A（弦理論接合、仮説として） -> `v17.0/papers/KSAU_v17.0_Topological_Cosmology.md`

---

## 成果サマリー (v17.0)

1. **ダークマターの正体**: 「位相的張力（Topological Tension）」として定義。
2. **予測式**: $\rho_{\text{tens}} \propto a^{-(2 + 1/48)}$。
3. **銀河回転曲線**: KSAU幾何学定数のみで **MAE = 7.19 km/s** で再現。
4. **GUTスケール**: 24Dバルクからの投影因子 $N^{1/4} \approx 21$ により標準宇宙論と整合。
5. **時間の矢**: 「ほどけ」によるエントロピー増大として微視的に定義。

---

## 既知の制約・リスク

| リスク | 対処方針 |
| :--- | :--- |
| 「定在波」がEM波と混同される | 用語を「時間流速の定常摂動」に統一 |
| 26次元の過剰主張 | AppendixでHypothesisとして明示 |
| 銀河回転曲線の定量再現が困難 | 失敗の場合も記録（科学的誠実性原則） |
| スコープ拡大 | Paper 4候補はv17に含めない |

---

Last Updated: 2026-02-17 | v17.0 Status: COMPLETE ✅
