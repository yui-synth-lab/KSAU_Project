# KSAU v34.0 Roadmap: Section 2 独立再現フェーズ

**Phase Theme:** EXPLORATORY-SIGNIFICANT（p=0.0078、Bonferroni 未達）で止まっている Section 2（CS 双対性）を、独立データセットによる再現実験で「確証的支持」へ格上げする。並行して v33.0 引き継ぎの技術的負債を解消する。
**Status:** PLANNING — v33.0 Session 3 引き継ぎ
**Date:** 2026-02-21
**Auditor:** Claude (Independent Audit Active)

---

## v33.0 からの引き継ぎ（確定事項）

### 確立された成果

| Task/Section | 最終ステータス | 根拠ファイル |
|---|---|---|
| Task A: ERR_THRESH 解消 | 独立閾値設定・SSoT 格納・バイアス定量化完了 | `task_a_err_thresh_resolution.py` |
| Task B: MC シード安定性 | 6シードで堅牢性確認（全シード Bonferroni 非有意） | `task_b_seed_stability.py` |
| Section A: 非標準 WZW 全3経路 | **全経路不可能と確定（WZW 全体閉鎖）** | `section_a_nonstandard_wzw_survey.md` |
| Section B: 現状評価レポート | `section_b_ksau_status_report.md` 完成 | `section_b_ksau_status_report.md` |
| MC 感度分析 | 3サンプリング範囲で Bonferroni 全非有意 | `mc_sensitivity_analysis.py` |

### 「因子7」問題の全探索経路（完全クローズ）

| 経路 | 結果 | 確定バージョン |
|------|------|--------------|
| 標準 WZW による $7\pi/k$ 導出 | **閉鎖**（数学的確定） | v30.0 |
| $\alpha_{em}$ の幾何学的導出 | **閉鎖**（統計的棄却） | v30.0 |
| Section 1 解析的証明 | **停止**（Formal Deferral） | v30.0 |
| $N_{Leech}^{1/4}/r_s$ 統計的有意性 | **否定**（Bonferroni 補正後） | v31.0 |
| $q_{mult}=7$ の代数的起源（E₈・Leech コセット） | **FREE PARAMETER** | v31.0 |
| $Co_0$ 極大部分群に $G_2$ 型 | **なし** | v31.0 |
| $Co_0 \to G_2$ 写像（全3経路） | **FREE PARAMETER 最終確定** | v32.0 |
| $D_{bulk\_compact}=7$ | **同語反復確定** | v32.0 |
| 非標準 WZW 全3経路（Curved/Coset/非コンパクト） | **閉鎖**（符号論拠・数学的確定） | v33.0 |

**「因子7」の代数的必然性探索は全経路閉鎖。$q_{mult}=7$ は FREE PARAMETER として確定。**

### v33.0 go.md 引き継ぎ事項

| 優先度 | 内容 |
|--------|------|
| **MUST** | WARNING #3 DEFERRED 最終解消: Section 2 元文書の Bonferroni 検定数 n 正式確認 |
| **MUST** | Section 2 独立再現計画策定・実施: EXPLORATORY → 確証的支持への格上げ |
| SHOULD | `mc_sensitivity_analysis.py` の `n_max` 修正（wide 範囲の帰無仮説設計不整合） |
| SHOULD | `section_a_nonstandard_wzw_survey.md §4.6` 表記修正（コンパクト/非コンパクト符号区別） |
| SHOULD | `H₀,KSAU = 76.05` の Hubble Tension 文脈評価（乖離 ~13% の定量的評価） |
| SHOULD | アーカイブ運用改善（セッション終了時の go.md/ng.md 即時バックアップ） |

---

## v34.0 フェーズ定義: Section 2 確証的検証

v33.0 完了時点での KSAU フレームワーク最大の未解決統計的問題：

$$\text{Section 2 (CS双対性)}: p = 0.0078 \quad > \quad \alpha_{Bonf} = 0.0050 \quad \text{(EXPLORATORY-SIGNIFICANT, 未達)}$$

この結果が「偶然か、真のシグナルか」を判断するには、**独立データセットでの再現**が唯一の経路。
v34.0 の使命: この格上げを試みる。

---

## 1. 必達タスク（v33.0 MUST 事項の解消）

### Task A: WARNING #3 DEFERRED の最終解消（優先度: HIGH）

**背景（v33.0 go.md §5 WARNING #3 より）:**

Section 2 の Bonferroni 補正数 n が「逆算推定値 n ≈ 10」のままであり、Section 2 元文書を参照した正式確認が未実施。`section_b_ksau_status_report.md §2.1` では「Bonferroni 補正後の評価: 未実施」と記述している。

**v34.0 での対応:**

- v30.0 の Section 2 実装コード（`v30.0/` 配下）を読み込み、実際の独立検定数 n を直接確認する。
- 確認した n を用いて Bonferroni 補正後閾値 `α = 0.05/n` を算出し、Section 2 の p=0.0078 との比較を行う。
- `section_b_ksau_status_report.md §1.2` を「Bonferroni 補正後閾値 = 0.05/n（n = 確認値）、p=0.0078 は有意 / 非有意」に更新する。

**成功基準**: n の正式確認完了・補正後評価の明記・`section_b_ksau_status_report.md §1.2` 更新完了。

---

## 2. v34.0 新規目標 (Core Objectives)

### Section A: Section 2 独立再現実験（最重要）

v33.0 go.md §5 MUST 推奨2より。KSAU フレームワークの「現象論的支持」を「確証的支持」に格上げするための唯一の経路。

**Section 2 の現状:**
- v30.0 で確立された CS 双対性の統計的探索。
- 帰無仮説: ランダムな CS 理論パラメータ群では観測された相関が生じない。
- 観測結果: p = 0.0078（raw）、Bonferroni 補正後 p > α（未達、EXPLORATORY-SIGNIFICANT）。

**独立再現の設計方針:**

1. **独立データセットの特定**: Section 2 で使用したデータセットとは独立した CS 理論パラメータセット（文献、数値計算、または異なるゲージ群）を特定する。
2. **同一検定手法の適用**: v30.0 の MC 検定手法を独立データに適用し、同じ手順で p 値を算出する。
3. **事前登録型分析**: 検定実施前に「有意と判断する閾値」を SSoT に格納し、事後的な閾値変更を防ぐ。
4. **結果の解釈**:
   - 独立再現で p < Bonferroni 閾値 → **CONFIRMED（確証的支持）** へ格上げ
   - 独立再現で p ≥ Bonferroni 閾値 → **EXPLORATORY-SIGNIFICANT 維持**（再現性なし）
   - 独立データが取得できない場合 → **「独立再現不可（データ不足）」として正式記録**

**成功基準**: 独立再現実施または「実施不可」の正式宣言。いずれの場合も結論を明記。「検討中」での持ち越し禁止。

---

### Section B: 技術的整合性の最終整備（SHOULD 事項）

v33.0 go.md §5 SHOULD 推奨事項の実施。

#### B-1: `mc_sensitivity_analysis.py` の `n_max` 修正

- `wide [30,1000]` 範囲において `n_max` が `standard` 範囲向けの固定値になっている問題を修正。
- 各サンプリング範囲の中心値に基づく動的 `n_max` を設定する。
- 修正後に再実行し、p 値変化を記録する（主結論への影響は想定されない）。

#### B-2: `section_a_nonstandard_wzw_survey.md §4.6` 表記修正

- 一般式 `$h = C_2(\text{rep}) / (k + h^\vee_G)$` を、コンパクト群（`+`）と非コンパクト群（`-`）で符号が異なることを明示する形に修正。
- `section_a_case3_supplement.md §2.3` との整合性を確認。

#### B-3: `H₀,KSAU = 76.05` の Hubble Tension 文脈評価

- `section_b_ksau_status_report.md §1.3` に定量的評価を追記：
  - Planck 2018 観測値: $H_0 = 67.4 \pm 0.5$ km/s/Mpc
  - KSAU 予測値: $H_0 = 76.05$ km/s/Mpc（乖離 ~13%、約 17σ）
  - SH0ES 観測値: $H_0 = 73.0 \pm 1.0$ km/s/Mpc（乖離 ~4%）
  - 評価: KSAU の $H_0$ 予測は Planck 値とは不一致。Hubble Tension を「解消」するほどではない。

#### B-4: アーカイブ運用の確立

- `v34.0/archive/` サブディレクトリを作成。
- 各セッション終了時の `go.md`/`ng.md` バックアップ手順を確立し、今セッションから適用する。

**成功基準**: B-1〜B-4 の各項目について「完了」または「実施不可（理由を記録）」の明示。

---

## 3. 成功基準 (Success Criteria)

1. [x] **Task A（WARNING #3 解消）**: Section 2 元文書の検定数 n 正式確認・`section_b_ksau_status_report.md §1.2` 更新完了（n=10 ソースコード直接確認）。
2. [x] **Section A（独立再現）**: 独立再現不可（KSAU トポロジー体積は内部データ）を根拠とともに宣言。LOO-CV 実施: クォーク除外 6 ケース全て k_obs 窓外（NOT ROBUST）、レプトン除外 2 ケースのみ窓内（退化付き）。正確なロバスト性: 2/8。持ち越し禁止を遵守。
3. [x] **Section B（技術的整備）**: B-1〜B-4 の各項目完了（B-1: mc_sensitivity_analysis_v2.py, B-2: §4.6 符号修正, B-3: H₀ 評価追記, B-4: archive/ 作成）。

---

## 4. 監査プロトコル（継続）

- **SSoT**: 全ての数値定数は `v6.0/data/` の JSON から読み込むこと。
- **統計**: 事前登録型分析を徹底すること（独立再現の閾値は実施前に SSoT に格納）。
- **過剰主張禁止**:
  - 「WZW から $7\pi/k$ が導出される」の復活禁止（v33.0 で数学的確定）。
  - $q_{mult}=7$ を「Leech 格子から導出された」と記述することの禁止。
  - MC p 値（raw < 0.05）を Bonferroni 補正後有意性と混同した記述の禁止。
- **EXPLORATORY と CONFIRMED の区別**: p < α（Bonferroni 未達）は CONFIRMED ではない。

---

## 5. v33.0 完了後の KSAU 理論的輪郭（v34.0 の出発点）

### 確立された成果（v34.0 以降も有効）

| 項目 | ステータス | バージョン |
|------|----------|-----------|
| $S_8$ 予測精度（7サーベイ同時適合）| 順列検定 p=0.00556（統計的必然） | v28.0 |
| $H_0 \approx 74.4$ km/s/Mpc（幾何学的導出） | SH0ES と 1.35σ 一致 | v27.0 |
| LCC（$\kappa/512$）の Leech 格子固定点導出 | $H_0 = 67.2$ km/s/Mpc | v29.0 |
| WZW 全経路（標準＋非標準）閉鎖 | 数学的確定 | v30.0/v33.0 |
| ERR_THRESH 解消・MC シード安定性確認 | 統計設計の誠実性回復 | v33.0 |

### 統計的支持（補正後有意性なし）

| 項目 | ステータス | p 値 |
|------|----------|------|
| Section 2（CS 双対性） | EXPLORATORY-SIGNIFICANT | p=0.0078（Bonferroni 未達） |
| Section 3（LSS Coherence） | MOTIVATED_SIGNIFICANT | p=0.032/0.038 |
| $N_{Leech}^{1/4}/r_s \approx 7$ | 有意性なし（Bonferroni 補正後） | p=0.0137/0.0613 |

### 解決すべき残存課題

| 課題 | 優先度 |
|------|--------|
| Section 2 の独立再現（確証的支持へ格上げ試み） | **v34.0 最重要** |
| Section 1 Formal Deferral（PMNS・B=4.0 証明） | 将来の完全理論に棚上げ |
| $q_{mult}=7$ の代数的起源 | FREE PARAMETER 確定（探索経路なし） |

---

*KSAU v34.0 Roadmap — Section 2 独立再現フェーズ*
*Issued by: Claude (Independent Auditor) — 2026-02-21*
*引き継ぎ元: v33.0 Session 3 APPROVED with WARNINGS*
