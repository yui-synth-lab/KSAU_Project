# KSAU v32.0 Roadmap: Co₀ 表現論探索フェーズ

**Phase Theme:** v31.0 で PARTIAL と判定された Co₀ → G₂ 写像の決着と、v31.0 統合報告書の作成。「因子 7」問題に残された唯一の代数的経路を徹底調査する。
**Status:** PLANNING — v31.0 Session 4 引き継ぎ
**Date:** 2026-02-20
**Auditor:** Claude (Independent Audit Active)

---

## v31.0 からの引き継ぎ（確定事項）

### 確立された成果

| Task/Section | 最終ステータス | 根拠ファイル |
|---|---|---|
| Task A: 三者統一仮説 | CONJECTURE（格下げ確定） | `algebraic_mapping_7d.py` VERDICT |
| Section A: BAO ブリッジ | MOTIVATED_SIGNIFICANT（代数的ブリッジ未発見） | `section_A_paper_draft.md` §A.4 |
| Section B: q_mult 起源 | FREE PARAMETER（正式宣言） | `co0_g2_algebraic_bridge_analysis.md` §3 |
| Section C: 非標準 WZW | 未解決（文献なし）確定 | `co0_g2_algebraic_bridge_analysis.md` §2 |
| Co₀ → G₂ 写像 | **PARTIAL**（間接的接続あり、完全写像未構成） | `co0_g2_algebraic_bridge_analysis.md` §3 |

### 閉鎖された経路（v32.0 で再探索不要）

| 経路 | 結果 |
|------|------|
| 標準 WZW による $7\pi/k$ 導出 | 不可能（数学的確定、v30.0）|
| $\alpha_{em}$ の幾何学的導出 | 不可能（統計的棄却 FPR 87%、v30.0）|
| $N_{Leech}^{1/4}/r_s$ の統計的有意性 | なし（Bonferroni 補正後 $p > 0.0024$、v31.0）|
| $Co_0$ 極大部分群に $G_2$ 型のもの | 存在しない（ATLAS 確認済、v31.0）|

### v31.0 go.md 留保事項（v32.0 引き継ぎ）

| 優先度 | 内容 |
|--------|------|
| MEDIUM | `n_max` の動的設定への移行（各 $(p, \text{scale})$ ごとに $n_{max} = \text{round}(s/R) + \text{margin}$） |
| LOW | D_CMB との組み合わせがスケール効果による見かけ上の有意性を生む可能性の論文草稿への明記 |
| MEDIUM | `ERR_THRESH = err_7` の循環的閾値設定（MC p 値の過小評価方向バイアス）を将来の統計設計で修正 |

---

## v32.0 フェーズ定義: Co₀ 表現論探索

v31.0 の `co0_g2_algebraic_bridge_analysis.md` が PARTIAL を宣言し、以下の3経路を「未調査として残る」と明記した：

1. **$Co_0$ の 7 次元・14 次元表現の探索**（$G_2$ の基本・随伴表現との対応）
2. **$G_2(2)' \cong PSU(3,3)$ の $Co_0$ 内存在確認**（ATLAS 直接確認が未実施）
3. **$\Lambda_{24}$ の $G_2$-部分格子の探索**

これらを調査し「DERIVED / 接続なし（FREE PARAMETER）」で完全決着させることが v32.0 の中核課題。

---

## 1. 必達タスク（v31.0 留保の継続解消）

### Task 0: 統計設計の改善（優先度: MEDIUM）

- [x] `section_a_numerical_patrol.py` の `n_max` を各 $(p, \text{scale})$ ごとに動的設定する実装へ移行
  - 実装: `n_max = round(scale / R_p) + margin`（margin=5 を基準）
  - 再実行して結果が変わらないことを確認（主結論は有意性なし）

**成功基準**: 動的設定実装完了、再実行で主結論（Bonferroni 補正後 p > 0.0024）に変化なし確認。

---

## 2. v32.0 新規目標 (Core Objectives)

### Section A: Co₀ 表現論による因子 7 の最終調査（最重要）

v31.0 の PARTIAL 判定に残された3経路の完全調査。

- [x] **経路 1: Co₀ の 7 次元・14 次元表現の探索**
  - $Co_0$ の既知表現リストから 7 次元表現の有無を確認
  - $G_2$ の基本表現（7 次元）および随伴表現（14 次元）と $Co_0$ 表現の整合性を評価
  - 計算ツール: GAP/SageMath または ATLAS の Character Tables を参照

- [x] **経路 2: $G_2(2)' \cong PSU(3,3)$ の $Co_0$ 内存在確認**
  - ATLAS of Finite Groups で $Co_0$ の部分群として $PSU(3,3)$（位数 6048）の有無を直接確認
  - $|Co_0| = 2^{22} \cdot 3^9 \cdot 5^4 \cdot 7^2 \cdot 11 \cdot 13 \cdot 23$ との整合性は位数制約からは可能

- [x] **経路 3: $\Lambda_{24}$ の $G_2$-部分格子の探索**
  - Leech 格子内に $G_2$ ルート系（$D_4$ ルート系または短根6本・長根6本）に対応する部分格子の探索
  - 既知の Niemeier 格子構造との照合

- [x] **最終判定の宣言**
  - 3経路のいずれかで写像が構成できた場合: **DERIVED（代数的接続確立）**
  - 全3経路で接続なしの場合: **FREE PARAMETER 最終確定**（$G_2$ 経路の閉鎖）

**成功基準**: DERIVED または FREE PARAMETER 最終確定の二択で決着。「調査中」での持ち越し禁止。

### Section B: v31.0 統合最終報告書の作成（HIGH）

v31.0 go.md §4 推奨 4「v31.0 最終報告書の統合」より。

- [x] 全4セクション成果（Task A / Section A / B / C）を統合した v31.0 最終報告書を作成
- [x] `co0_g2_algebraic_bridge_analysis.md` の PARTIAL 判定と v32.0 への引き継ぎ経路を明示
- [x] `section_A_paper_draft.md` を論文草稿として完成させる（Bonferroni 補正後有意性なしを主結論）
- [x] SSoT 準拠・統計的誠実性・否定的結果の平等な扱いを確認

**成功基準**: 外部から評価可能な形式の v31.0 最終報告書の完成。過剰主張なし。

### Section C: $D_{bulk\_compact}=7$ の M 理論的性質の整理（LOW）

- [x] M 理論の $G_2$-holonomy コンパクト化が 7 次元である数学的理由を整理
- [x] KSAU の $D_{bulk\_compact}=7$ との関係を「同語反復（定義による一致）」か「独立な一致」かを明確化
- [x] `v6.0/data/physical_constants.json` の `d_bulk_compact` エントリに整理結果の注釈を追記

**成功基準**: 「一致の性質」の明確な記述と SSoT 注釈追記完了。

---

## 3. 成功基準 (Success Criteria)

1. [x] **Task 0（統計設計改善）**: `n_max` 動的設定実装・再実行・主結論不変確認。
2. [x] **Section A（Co₀ 表現論最終調査）**: DERIVED または FREE PARAMETER 最終確定の二択決着。
3. [x] **Section B（v31.0 統合最終報告書）**: 最終報告書完成。過剰主張なし・SSoT 準拠確認。
4. [x] **Section C（D_bulk_compact 整理）**: SSoT 注釈追記完了。

---

## 4. 監査プロトコル（継続）

- **SSoT**: 全ての数値定数は `v6.0/data/` の JSON から読み込むこと。
- **統計**: 多重比較を実施した場合は Bonferroni 補正を必ず適用し、補正後の結論を主結果とすること。
- **「PARTIAL」の扱い**: 「間接的接続あり」は「DERIVED」ではない。写像の完全構成なしに DERIVED を宣言することを禁ずる。
- **否定的結果の価値**: 「FREE PARAMETER 最終確定」は探索の失敗ではなく、理論の探索空間を絞る科学的成果である。

---

## 5. v31.0 で得た理論的輪郭（v32.0 の出発点）

v31.0 が明らかにした「何が KSAU を説明できないか」、および残された唯一の経路：

| 経路 | 結果 |
|------|------|
| 標準 WZW による $7\pi/k$ 導出 | **閉鎖**（数学的確定、v30.0）|
| $\alpha_{em}$ の幾何学的導出 | **閉鎖**（統計的棄却、v30.0）|
| Section 1 解析的証明 | **停止**（Formal Deferral、v30.0）|
| $N_{Leech}^{1/4}/r_s$ 統計的有意性 | **否定**（Bonferroni 補正後、v31.0）|
| $q_{mult}=7$ の代数的起源（E₈・Leech コセット経路） | **FREE PARAMETER**（v31.0）|
| 非標準 WZW での導出 | **未解決**（文献なし、v31.0）|
| $Co_0$ 極大部分群に $G_2$ 型 | **なし**（ATLAS 確認、v31.0）|
| $Co_0 \to G_2$ 写像（7次元表現・PSU(3,3)・部分格子） | **PARTIAL** → **v32.0 で決着** |

v32.0 の使命は「PARTIAL」を決着させること。DERIVED か FREE PARAMETER 最終確定か——これが v32.0 の唯一の本質的問いである。

---

*KSAU v32.0 Roadmap — Co₀ 表現論探索フェーズ*
*Issued by: Claude (Independent Auditor) — 2026-02-20*
*引き継ぎ元: v31.0 Session 4 APPROVED*
