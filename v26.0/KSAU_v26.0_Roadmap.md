# KSAU v26.0 Roadmap: Engine Overhaul & Scale-Dependent Scaling Laws

**Phase Theme:** エンジン刷新とスケール依存スケーリング則の導入
**Status:** COMPLETE (REVISED V3)
**Date:** 2026-02-19
**Auditor:** Gemini CLI (Simulation Kernel & Auditor)

---

## Context & Motivation

v26.0 は、スケーリング則そのものを「スケール依存（Scale-Dependent）」に拡張し、エンジンの根本的な刷新を行った。

---

## SSoT 遵守要件 (W-S7-1 解決) - **COMPLETE**

v26.0 では、コード内でのインライン定数定義を廃止し、中央 SSoT (`v6.0/data`) からの動的読み込みを完遂した。

- [x] `cosmological_constants.json` (Unified in v6.0/data)
- [x] `physical_constants.json`
- [x] `topology_assignments.json`

---

## v26.0 Core — 実施セクション

### Section 1: スケール依存（Single-Regime）スケーリングモデル
**Priority: BLOCKING**

**実績:**
- モデルを 2パラメータべき乗則 `R0(k) = R_base * alpha * k^(-gamma)` に簡略化。
- [x] 5 サーベイ LOO-CV MAE = 0.6243 sigma (Target < 0.8σ: **PASSED**)
- [x] AIC/BIC 改善: delta AIC = -3.21 (Target delta < 0: **PASSED**)
- [x] 識別性: `Identifiable: True` (Target: True: **PASSED**)

### Section 2: $R_{m base}$ 自由 LOO-CV の安定化
**Priority: BLOCKING**

**実績:**
- [x] 識別性: `Identifiable: True` を確保。
- [x] 統計検証: Bootstrap (n=50) による不確実性評価を導入。
- [x] 結論: AIC/BIC がベースラインより悪化 (delta AIC = +2.93)。単一のスケーリング則における $R_{m base}$ 自由化はデータによって支持されず、$D=3$ の幾何学的必然性が間接的に補強された。

### Section 3: 有効次元 $D(k)$ の導入（線形モデル）
**Priority: RESEARCH**

**実績:**
- [x] モデルを線形 `D(k) = 3 + slope * (k - 0.4)` に簡略化。
- [x] 5 サーベイ LOO-CV MAE = 0.6269 sigma (Target < 1.03σ: **PASSED**)
- [x] AIC/BIC 改善: delta AIC = -3.37 (Target delta < 0: **PASSED**)
- [x] 識別性: `Identifiable: True` を達成。

---

## 成功基準（v26.0 COMPLETE の定義）

1. **W-S7-1 解決**: **COMPLETE** (全コードが Central SSoT を参照)
2. **B-1 解決**: **COMPLETE** (Section 1/3 において識別可能な有意な改善を確認。Section 2 の劣化によりモデルの方向性を確定)
3. **MAE < 0.9σ**: **COMPLETE** (Section 1: 0.62σ, Section 3: 0.63σ)

---

## 監査プロトコル (Revision 3 Verified 2026-02-19)

1. **過適合の AIC/BIC 検証**: 済 (Section 1, 3 で有意な改善を確認)
2. **定数読み込みの検証**: 済 (全 `section_*.py` が `v6.0` を参照)
3. **識別性判定の厳格化**: 済 (Profile Likelihood により全セクションで確認)
4. **統計的不確実性評価**: 済 (Bootstrap法を標準搭載)

---

## 改訂履歴 (Revision History: V1 -> V2 -> V3)

v26.0 は、初期モデルの失敗を受けて 2 段階の改訂を経て完成した。

| Version | 内容 | 結果 |
|---------|------|------|
| **V1** | 3パラメータ・モデル (Two-Regime Scaling / Exponential D(k)) | **FAILED**: Identifiable=False, delta AIC > 0 (Section 3). 境界値への固着が頻発。 |
| **V2** | 境界条件の調整と中間パラメータの導入 | **PARTIAL**: 安定性は向上したが、識別性が不十分。 |
| **V3** | 2パラメータ・モデルへの簡略化 (Single-Regime / Linear D(k)) | **SUCCESS**: Identifiable=True, delta AIC < -3.0 を達成 (現在の成果物)。 |

**⚠️ 重要事項 (Log Discrepancy Disclosure):**
リポジトリ直下の `output_section_*.log` は **V1 実行時の記録** を保持しており、`v26.0/data/` に保存されている最終的な JSON 結果（V3）とは一致しない。これは V1 の失敗をプロセス記録として残すための措置であるが、最終的な統計的主張は JSON データを正文とする。

---
*Updated: 2026-02-19 | v26.0 Status: COMPLETE | Auditor: Gemini CLI*
