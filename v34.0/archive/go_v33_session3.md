# KSAU v33.0 Session 3 — 査読結果: APPROVED with WARNINGS

**査読者:** Claude (Independent Auditor)
**対象:** `output_log.md`（v33.0 Session 3: ng.md 全7指摘への対応）
**日付:** 2026-02-21
**判定:** **APPROVED with WARNINGS**

---

## §1: 承認根拠

### §1.1 指摘 #1【CRITICAL】：MC感度分析の定量的実施 — RESOLVED

`mc_sensitivity_analysis.py` を新規作成し、3サンプリング範囲での MC 感度分析を実施した。
SSoT 準拠（`physical_constants.json` および `cosmological_constants.json` からの読み込み）を確認。
Bonferroni 閾値 `α = 0.05/21 = 0.002381` の根拠（7べき乗 × 3宇宙論スケール = 21組み合わせ）も適切。

| 範囲 | RS_MIN | RS_MAX | hits | MC_p | Bonf 有意 |
|------|--------|--------|------|------|-----------|
| standard [50,500] | 50 | 500 | 1176 | 0.01176 | no |
| wide [30,1000] | 30 | 1000 | 613 | 0.00613 | no |
| narrow [80,300] | 80 | 300 | 2453 | 0.02453 | no |

全3範囲で Bonferroni 補正後有意なし。SESSION 2 の「言語的概算のみ」という問題は解消された。

**ただし WARNING（後述 §3.1）:** `mc_sensitivity_analysis.py` における `n_max` の固定化問題。

---

### §1.2 指摘 #2【CRITICAL】：WARNING #3 の正確な再分類 — RESOLVED（DEFERRED）

n=10 が逆算推定値であることを `go_session1_archive.md §2 WARNING #3` に明記し、WARNING #3 を「DEFERRED（Section 2 元文書参照による正式検定数確認が必要）」に正確に再分類した。

ng.md の要求（「✅ RESOLVED」の取り消しと「DEFERRED 再分類」）に正確に応答している。

---

### §1.3 指摘 #3【HIGH】：go_session1_archive.md の作成 — RESOLVED（構造的限界付き）

Session 1 の go.md を、Session 2 `output_log.md` および `ng.md` の引用内容から再構成し、`go_session1_archive.md` として SSoT 化した。「再構成」であり「原文ではない」ことを §5 で明示している点は誠実。

**構造的な限界（受容可能）:** 元文書が失われており独立確認が不可能である点は解消不能。しかしこれは Session 3 が作り出した問題ではなく、Session 1 終了後の運用問題であり、本アーカイブの誠実性は認める。

---

### §1.4 指摘 #4【HIGH】：元文書 §4.6 の修正 — RESOLVED

`section_a_nonstandard_wzw_survey.md §4.6` に修正注記を追加し、「$\pi$ そのものを値として持つ物理的な表現は存在しない」という過剰主張を否定した。

- 離散系列: 判別式 $1 - 28\pi < 0$（実数解なし、代数的確定）
- 連続系列: 数値的達成可能だが代数的選択原理不在（循環論法）

元文書と補足文書の矛盾が解消された。§4.8「不可能と確定」判定は維持されている。

---

### §1.5 指摘 #5【MEDIUM】：cosmological_constants.json 更新 — RESOLVED

```json
"bao_sound_horizon_relative_uncertainty": 0.00176803805
```

4桁丸め（旧値: 0.001768）から完全精度（新値: 0.00176803805 = 0.26/147.09）へ更新済み。
更新コメントに ng.md #5 対応であることを明記。SSoT 原則の完全性が向上した。

---

### §1.6 指摘 #6【MEDIUM】：Section B §2.1 の曖昧記述修正 — RESOLVED

`section_b_ksau_status_report.md §2.1` の「または」を削除し、「Bonferroni 補正後の評価: 未実施（Section 3 の検定数が正式確認されておらず補正後閾値を適用できない）」と明確化した。「補正後有意性なし」を現時点では宣言できないことを明示。

---

### §1.7 指摘 #7【MEDIUM】：§2.3 の有限 k 論拠への置換 — RESOLVED

`section_a_case3_supplement.md §2.3` を修正し、$k \to \infty$ 展開論拠を「符号の根本的不整合」論拠に置換した：

$$h = \frac{C_2(j)}{k-2} + n \geq 0 \quad (C_2 > 0, n \geq 0, k > 2)$$
$$b_q(k) = -7(1+\pi/k) < 0 \quad \forall k > 0$$

この矛盾は任意の有限 $k > 2$ で直接成立する厳密な排除論拠である。数学的に正確と確認。

---

## §2: 7件の指摘に対する最終ステータス

| 指摘 | 重大度 | Session 3 対応 | 査読評価 |
|------|--------|----------------|---------|
| #1: WARNING #2「解消」虚偽 | CRITICAL | `mc_sensitivity_analysis.py` 実行 | ✅ RESOLVED（Warning付き、後述§3.1）|
| #2: WARNING #3 循環論法 | CRITICAL | DEFERRED 再分類・n=10推定を明記 | ✅ RESOLVED（DEFERRED化）|
| #3: go.md 不在 | HIGH | `go_session1_archive.md` 作成 | ✅ RESOLVED（構造的限界付き）|
| #4: 元文書 §4.6 誤記 | HIGH | 元文書に修正注記追加 | ✅ RESOLVED |
| #5: WARNING #4 未実施 | MEDIUM | JSON を完全精度値に更新 | ✅ RESOLVED |
| #6: Section B §2.1 曖昧 | MEDIUM | 「または」削除・明確化 | ✅ RESOLVED |
| #7: §2.3 有限k問題 | MEDIUM | 符号論拠（有限k有効）に置換 | ✅ RESOLVED |

---

## §3: 継続 WARNINGS（次フェーズ引き継ぎ必須）

### WARNING #1【MEDIUM】：`mc_sensitivity_analysis.py` の `n_max` 固定化問題

`mc_sensitivity_analysis.py` は `n_max = compute_nmax(R_S, R4, MARGIN)` を 3 範囲共通で使用している。

```python
N_MAX_RS = compute_nmax(R_S, R4, MARGIN)  # ≈ 12（r_s = 147.09 Mpc に基づく）
```

これは `standard [50,500]` 範囲に対して設定された値であり、`wide [30,1000]` 範囲に対して用いると：

- `rs_rand` が最大 1000 Mpc まで取り得る
- `ratio_rand = rs_rand / R4` は最大 `1000/21.06 ≈ 47.5`
- しかし `n_rand > 12` のサンプルは `1 <= n_rand <= N_MAX_RS` 条件で棄却される
- 実効的な帰無仮説空間が `[50, ~252]` Mpc 程度に狭まっている可能性がある

**影響の方向:** この問題は `wide` 範囲の p 値を**過小評価する**（= 帰無仮説が出す「ヒット」が実際より少なく計算される）方向に働く。結果 p = 0.00613 は実際より小さい可能性があり、非有意という主結論を**強化**する方向のバイアスである。

**ERR_THRESH バイアスとの比較:**
旧 ERR_THRESH 循環閾値は有意性を「過大評価」する方向のバイアスだった（p 値を小さく見せた）。本問題は逆方向（p 値を大きく見せる = 非有意を強化）であり、**主結論の信頼性を損なう方向ではない**。しかし帰無仮説の設計として不整合を含む。

**次フェーズ対応（LOW 優先度）:**
`mc_sensitivity_analysis.py` を修正し、各範囲に応じた動的 `n_max`（= `compute_nmax(scale_nominal=rs_rand_expected_center, R4, MARGIN)` または固定の大きな値）を設定すること。

ただし、主結論（Bonferroni 補正後全範囲で非有意）はこのバイアスを考慮しても変化しない。`wide` 範囲の実際の p 値は 0.00613 より大きい可能性があるが、閾値 0.002381 の約 2.6 倍以上の余裕がある。

---

### WARNING #2【DEFERRED 継続】：WARNING #3 の最終解消

Section 2 元文書参照による Bonferroni 検定数 n=10 の正式確認が未実施。次フェーズの **必須タスク** として引き継ぐ。

---

### WARNING #3【LOW】：`section_a_nonstandard_wzw_survey.md §4.6` の表記不整合

§4.6 本文中に残存する：

$$h = \frac{C_2(\text{rep})}{k + h^\vee_G}$$

この表記は**コンパクト WZW** の慣習的な記号法（$k + h^\vee_G$ の符号）であるが、$SL(2,\mathbb{R})$ WZW では `$h^\vee_{SL(2,\mathbb{R})} = 2$` の符号が**負**方向に入り、分母は `$k - 2$` となる。`section_a_case3_supplement.md §2.3` は正しく `$h = C_2(j)/(k-2) + n$` と記述しているが、元文書の一般式では `$k + h^\vee_G$` のままである。

これは Session 3 以前から存在した記述の不統一であり、修正注記の追加によっても解消されていない。

**次フェーズ対応（LOW 優先度）:** §4.6 の一般式を `$h = C_2(\text{rep}) / (k - h^\vee_G)$`（非コンパクト群では `$k - |h^\vee|$`）に修正するか、コンパクト/非コンパクトの符号の違いを注記で明示すること。

---

## §4: v33.0 セッション全体の評価

### v33.0 の成果（全4セッション）

| セッション | 主要成果 |
|-----------|---------|
| Session 1 | Task A（ERR_THRESH解消）・Task B（シード安定性）・Section A（WZW全経路閉鎖）・Section B（現状マップ）の完了 |
| Session 2 | WARNING #1 の論拠強化（部分的）・WARNING #2〜#4 の記録 |
| Session 3 | ng.md 全7指摘への対応・MC感度分析の定量的実施・元文書修正・SSoT更新 |

### v33.0 完了後の理論的状態

| 項目 | 確定状態 |
|------|---------|
| WZW 全経路（標準＋非標準） | **閉鎖（数学的確定）** |
| ERR_THRESH 循環閾値 | **解消完了** |
| MC シード安定性 | **堅牢性確認** |
| $N_{Leech}^{1/4}/r_s \approx 7$ | **Bonferroni 補正後有意なし（全閾値・全サンプリング範囲）** |
| $q_{mult} = 7$ の代数的起源 | **FREE PARAMETER（WZW全経路閉鎖後も未解決）** |

---

## §5: 次フェーズへの示唆

### 最優先事項（MUST）

1. **WARNING #3 DEFERRED の最終解消:** Section 2 元文書を参照し、Bonferroni 検定数 n を正式に確認する。補正後閾値を確定し、`section_b_ksau_status_report.md §2.1` を更新する。

2. **Section 2 の独立再現計画策定:** EXPLORATORY-SIGNIFICANT（p = 0.0078, Bonferroni 未達）の結果を確証的に検証するための、独立データセットによる再現実験の設計。これが KSAU フレームワークの「現象論的支持」を「確証的支持」に格上げするための唯一の経路。

### 推奨事項（SHOULD）

3. **`mc_sensitivity_analysis.py` の `n_max` 修正（WARNING §3.1）:** 範囲ごとの動的 `n_max` 設定。主結論への影響はないが、帰無仮説設計の誠実性のために実施。

4. **`section_a_nonstandard_wzw_survey.md §4.6` の表記修正（WARNING §3.3）:** コンパクト/非コンパクト WZW の `$k \pm h^\vee$` 符号の明示的区別。

5. **$H_{0,KSAU} = 76.05$ km/s/Mpc の Hubble Tension 文脈評価:** 観測値 67.4（Planck 2018）との乖離 ~13% を定量的に評価し、Section B §1.3 に追記。

6. **アーカイブ運用の改善:** 各セッション終了時に `go.md`/`ng.md` を `archive/` サブディレクトリに即時バックアップする運用を確立する。

### 禁止事項（次フェーズ継続）

- 「WZW から $7\pi/k$ が導出される」という主張の復活（数学的確定棄却済み、v30.0/v33.0）
- $q_{mult} = 7$ を「Leech 格子から代数的に導出された」と記述すること（FREE PARAMETER 最終確定）
- MC p 値（raw < 0.05）を Bonferroni 補正後有意性と混同した記述
- 「感度分析の方向性を記録した」ことを「定量的感度分析を実施した」と表現すること

---

## §6: 監査評価コメント

v33.0 Session 3 は、前回 ng.md の REJECT に対して誠実かつ包括的に対応した。特筆すべき点：

**評価すべき点:**
1. `mc_sensitivity_analysis.py` の設計は SSoT 準拠・シード管理・Bonferroni 閾値設定が適切であり、定量的感度分析として機能している。
2. `section_a_case3_supplement.md §2.3` の符号論拠への置換は、有限 $k$ で厳密に成立する改善された論拠であり、理論的誠実性が向上した。
3. `cosmological_constants.json` の SSoT 更新は軽微だが、原則の一貫性維持として重要。
4. `go_session1_archive.md` の「再構成」であることの明示は、科学的誠実性の観点から適切。

**残存する課題:**
Session 3 を通じて確認された一つの新規問題（`n_max` 固定化）は、主結論を損なわない方向のバイアスであるため、今回の承認を妨げない。しかし次フェーズでの修正を推奨する。

v33.0 全体を通じて KSAU フレームワークが示した最も価値ある科学的成果は、「因子7の代数的起源」に対する全ての主要な WZW 経路が数学的に閉鎖されたという**否定的結果の確定**である。これは探索空間の確定的縮小として記録に値する。

---

*KSAU v33.0 — 査読結果: APPROVED with WARNINGS*
*査読者: Claude (Independent Auditor)*
*Date: 2026-02-21*
*対象セッション: v33.0 Session 3（ng.md 全7指摘への対応）*
*次フェーズ: v34.0（Section 2 独立再現計画・WARNING #3 DEFERRED 最終解消）*
