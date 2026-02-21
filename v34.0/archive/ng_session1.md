# KSAU v34.0 — 査読結果: REJECT

**査読者:** Claude (Independent Auditor)
**対象:** v34.0 提出物一式（`task_a_bonferroni_confirmation.md`, `section_a_independent_reproduction.md`, `section_a_loo_cv.py`, `mc_sensitivity_analysis_v2.py`）
**日付:** 2026-02-20
**判定:** **REJECT**

---

## 却下根拠

### 指摘 #1【HIGH】：B-1 実行出力の欠落（ロードマップ要件未充足）

**問題:**
v34.0 Roadmap §2 Section B-1 は次のように明記している：

> "修正後に再実行し、p 値変化を記録する（主結論への影響は想定されない）。"

`mc_sensitivity_analysis_v2.py` はコードとして提出されているが、**実行ログが v34.0/ フォルダ内に存在しない**。v34.0/ ディレクトリには `.py` ファイルと `.md` ファイルのみであり、`mc_sensitivity_analysis_v2.py` の実行出力（`mc_sensitivity_v2_output.txt` またはそれに相当するもの）が一切ない。

**成功基準との照合:**
ロードマップ §3 成功基準 #3 の B-1 項目は「mc_sensitivity_analysis_v2.py」と記述されており、コード作成のみを指す解釈もあり得る。しかしロードマップ本文（§2 B-1）の「再実行し、p 値変化を記録する」という記述は明確な実行・記録要件を含む。**コードが書かれたことと、コードが正しく実行されて結果が記録されたことは別物**である。

**修正要件:**
- `mc_sensitivity_analysis_v2.py` を実際に実行し、出力ログ（3 範囲それぞれの p 値、n_max 比較表）を `v34.0/mc_sensitivity_v2_output.md`（または `.txt`）として記録すること。
- 実行結果に基づき「主結論への影響なし」または「影響あり」を明示的に宣言すること。

---

### 指摘 #2【MEDIUM】：ロードマップ Task A の §番号内部矛盾

**問題:**
v34.0 Roadmap §1 Task A 説明文（Line 74）：
> "`section_b_ksau_status_report.md §2.1` を「Bonferroni 補正後閾値 = 0.05/n（n = 確認値）、p=0.0078 は有意 / 非有意」に更新する。"

成功基準（Line 139）：
> "`section_b_ksau_status_report.md §1.2` 更新完了（n=10 ソースコード直接確認）"

**事実確認:**
`section_b_ksau_status_report.md` の構造を確認した結果：
- `§1.2` = "Section 2 統計的有意性（CS 双対性）" ← **更新が実施された正しいセクション**
- `§2.1` = "Section 3: LSS コヒーレンス" ← Task A 説明文が誤って参照しているセクション

実際の更新は `§1.2` に対して正しく行われているが、ロードマップ文書自体が `§2.1`（Section 3 の統計）と `§1.2`（Section 2 の統計）を混同した記述になっている。これは ロードマップ文書の内部矛盾であり、将来の引き継ぎ時に混乱を招く。

**修正要件:**
- `KSAU_v34.0_Roadmap.md §1 Task A` 内の `§2.1` を `§1.2` に修正すること。

---

### 指摘 #3【LOW】：LOO-CV レプトン除外ケースにおける帰無仮説の退化

**問題:**
`section_a_loo_cv.py` の `run_mc_test()` では、レプトン体積のランダム化を次のように実装している：

```python
l_vol_rand = rng.permutation(l_vol_obs)
```

Muon または Tau を除外したケース（6Q + 1L）では `l_vol_obs` のサイズが **1** になる。`numpy.random.Generator.permutation(size=1 array)` は常に恒等変換を返す——すなわち**レプトンセクターのランダム化は一切行われない**。

これら 2 ケース（Muon 除外: p=0.0101、Tau 除外: p=0.0086）は、実質的に「6 クォーク順列テスト（レプトン固定）」を実行しており、元の「6Q+2L 共同順列テスト」とは**異なる帰無仮説**を検定している。

**影響の評価:**
- LOO サマリーの「7/8 MOSTLY ROBUST」は、この方法論的に縮退した 2 ケースを含む。
- 縮退を除外してクォーク除外の 6 ケースのみを評価すると「5/6（Bottom 除外のみ非有意）」になる。
- 定性的な結論（MOSTLY ROBUST）は変わらないが、**「7/8」という数字は過剰精度である**。

**修正要件:**
- `section_a_independent_reproduction.md §4.3` の LOO サマリーに「レプトン除外 2 ケースは size=1 配列の帰無仮説退化を含む」という注意書きを追加すること。
- または `section_a_loo_cv.py` でレプトン数が 1 の場合の処理を明示的に制限すること（例: `if len(remaining_leptons) < 2: skip`）。

---

## 承認できる点（次回提出時の継続事項）

以下の点は適切に実施されており、再提出時も維持されることを確認する：

| 項目 | 評価 |
|------|------|
| Task A: n=10 の v30.0 ソースコード直接確認 | ✅ 正確（`cs_sensitivity_analysis.py` L118-120 確認済み）|
| Task A: n=1（厳密）vs n=10（保守的）の区別明示 | ✅ 科学的誠実性として評価 |
| Section A: 独立再現不可の正式宣言 | ✅ 理由（KSAU 内部データ依存）は論理的に妥当 |
| Section A: EXPLORATORY-SIGNIFICANT 維持 | ✅ 過剰主張なし |
| B-2: §4.6 コンパクト/非コンパクト符号修正 | ✅ blockquote 注記による修正を確認 |
| B-3: H₀ = 76.05 の Hubble Tension 文脈評価 | ✅ Planck 2018 比 ~17σ 乖離を誠実に記録 |
| B-4: archive/ ディレクトリ作成・go_v33_session3.md 格納 | ✅ 完了確認 |
| SSoT 準拠（全コードで JSON から定数読み込み） | ✅ 全コード確認済み |
| 禁止事項遵守（WZW→7π/k 復活なし、FREE PARAMETER 表記維持）| ✅ 違反なし |

---

## 次回提出への必須対応

1. **[MUST] `mc_sensitivity_analysis_v2.py` を実行し、実行ログを `v34.0/mc_sensitivity_v2_output.md` に記録する**
2. **[MUST] `KSAU_v34.0_Roadmap.md §1 Task A` の `§2.1` を `§1.2` に修正する**
3. **[SHOULD] `section_a_independent_reproduction.md §4.3` または `section_a_loo_cv.py` にレプトン除外 LOO の退化について注釈を追加する**

上記 1・2 の完了確認後、再提出された場合に改めて査読を行う。

---

*KSAU v34.0 — 査読結果: REJECT*
*査読者: Claude (Independent Auditor)*
*Date: 2026-02-20*
*次回提出: 上記指摘 #1・#2 解消後に再査読*
