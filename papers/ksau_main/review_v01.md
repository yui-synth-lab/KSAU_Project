# Review — draft_v01 (Revised)

**査読日:** 2026-03-01
**Reviewer:** Claude (AIRDP Auditor Role)
**対象:** draft_v01.md (修正後バージョン)
**VERDICT:** REVISE

---

## 総評

前回査読（Revision 0）で指摘した 8 件のうち、CKM R²・η_quark・G 有効数字・自由パラメータ表・"deeply encoded" の 5 件は適切に修正された。しかし、**ボソン切片 C = π√3 が SSoT の C = π√3 + 1/10 と不一致**であること、**Abstract から否定的結果の明示的言及が削除されたこと（後退）**、および **must-include の要素（DM 候補・アクシオン予測値・H23）が依然欠落**していることから、現時点での ACCEPT はできない。

---

## 必須修正事項

### [R-1]: ボソン切片 C の値が SSoT と不一致（新規検出）
**深刻度:** 重大
**該当箇所:** Section 2（Theoretical Framework）、最終文
**問題:**
Draft は「The global intercept $C$ is linked to the boson mass scale, theoretically derived as $C = \pi\sqrt{3}$ (H68)」と記述している。しかし SSoT `constants.json` には以下のように明記されている。

```json
"scaling_laws": {
    "boson_scaling": {
        "C": 5.5414,
        "C_theoretical": "pi * sqrt3 + 1/10"
    }
}
```

数値照合:
- $\pi\sqrt{3} \approx 5.4414$（draft の主張）
- $\pi\sqrt{3} + 1/10 = 5.5414$（SSoT 値 `C: 5.5414` と一致）

0.1 の差は偶然ではなく、SSoT が明示的に `+1/10` を理論式に含んでいる。draft の式 C = π√3 は SSoT と 0.1（約 1.8%）相違しており、SSoT との不一致として必須修正とする。なお brief にも「C = π√3」と記載されているが、SSoT が上位権威（CLAUDE.md §2）であるため、brief 側の記載も合わせて要修正（Brief 更新は Orchestrator 管轄）。

**修正要求:**
Section 2 を以下のように修正すること。
```
C = \pi\sqrt{3} + \frac{1}{10} \approx 5.5414
```
併せて、`1/10` 項の幾何学的起源（H68 の内容）を 1 文で補足すること。

---

### [R-2]: Abstract から否定的結果の明示的言及が削除された（後退）
**深刻度:** 重大
**該当箇所:** Abstract（最終文）
**問題:**
前版 draft の Abstract には「including 24 documented rejections which delineate the boundaries of the theory」という明確な記述があったが、修正後の Abstract ではこれが削除され、代わりに「providing a comprehensive record of both verified correlations and theoretical limits」という曖昧な表現に置き換えられた。Brief §5 は Abstract の必須要素として以下を指定している。

> 否定的結果への一言言及（「複数の仮説が棄却された」）

「theoretical limits」は否定的結果を意味しない。この変更は、論文の透明性を後退させている。

**修正要求:**
Abstract の最終文に、否定的結果の明示的言及を復元すること。例として前版の表現「24 documented rejections which delineate the theoretical boundaries」を再採用するか、それに相当する文を追加すること。

---

### [R-3]: ダークマター候補の記述が依然欠落
**深刻度:** 重大
**該当箇所:** Results または Discussion（いずれにも不在）
**問題:**
Brief §2「含めるが注意書き付き（requires_caveat）」は「ダークマター候補 | 67 個のリンク候補 | 実験的検証不可能な段階」の記述を要求しているが、修正後の draft にもこの記述は存在しない。SSoT には以下のように記録されている。

```json
"dark_matter_candidates": {
    "stable_link_candidates_count": 67,
    "rule_basis": "det_mod_24_zero_and_tsi_gte_24",
    "validated_by": "cycle_12_h30"
}
```

これは別の陽性結果（H30）であり、論文のスコープに含まれる。実験的検証不可能という制限の明記を条件に、Results または Discussion に追加すること。

**修正要求:**
Section 4（Results）に「Dark Matter Candidates（optional prediction）」サブセクションを追加し、以下を含めること:
- 安定リンク候補が 67 件存在すること（H30、サイクル 12）
- 選択基準（det ≡ 0 mod 24 かつ TSI ≥ 24）
- **「実験的検証手段は現時点で存在しない」という明示的な caveat**
- FPR または統計的根拠の記述

---

### [R-4]: アクシオン質量予測値 12.16 μeV が明示されていない
**深刻度:** 重大
**該当箇所:** Section 5.2
**問題:**
Section 5.2 の H58 bullet に「A joint test of axion mass, gravity deviation, and Top width failed to reach significance (p=0.067)」と記述されているが、アクシオン質量の具体的な予測値（12.16 μeV）および ADMX 探索範囲との関係が述べられていない。Brief §2 は以下を要求している。

> アクシオン質量予測 12.16 μeV | ADMX 探索範囲内 | ただし H58 で独立統計検証は失敗 (p=0.067)

SSoT に記録された予測値:
```json
"axion_prediction": {
    "m_a_uev": 12.16,
    "basis": "Combined FPR 0.14%",
    "last_updated": "2026-02-27"
}
"axion_exclusion": {
    "admx_2023": {
        "mass_range_uev": [11.0, 14.0]
    }
}
```

予測値を明記せずに「joint test failed」のみを述べることは、読者が独立検証可能な予測の存在を把握できない構造となっており、否定的結果の文脈を不完全にする。

**修正要求:**
H58 の bullet を以下の構造に拡充すること:
1. アクシオン質量予測 $m_a = 12.16\ \mu\text{eV}$（ADMX 2023 の探索範囲 11–14 μeV 内）を明記
2. joint test 失敗（p=0.067）と個別予測の有意性との対比を明記
3. 実験的検証の可能性と未確定状態を honest に記述すること

---

### [R-5]: H23（K=24 のトートロジー問題）が Methods に言及なし
**深刻度:** 重大
**該当箇所:** Section 3（Methods）
**問題:**
Brief §2 に「H23: 位相離散化 K=24 がトートロジカル（FPR=93.82%）→ Methods: K=24 は導出結果であり検証対象ではない」が明示されている。Section 3 では κ = π/24 の使用について言及しているが、K=24 が独立に統計検証された量ではないという注意が一切ない。これを省略することは、K=24 を経由した検証の循環性リスクを読者に隠蔽することになる。

**修正要求:**
Section 3.1 の Bonferroni Correction の説明近辺に以下の内容を追加すること:
「The discretization constant K=24 is not treated as a free parameter or independently tested hypothesis; it is a mathematical consequence of the 24-cell resonance condition K(4)·κ=π (H6). Treating K=24 as a candidate for statistical validation would constitute a circular test (H23: FPR=93.82%); therefore, it is fixed as a theoretical constant throughout all analyses.」

---

### [R-6]: Appendix A が不完全（8/69 仮説のみ）
**深刻度:** 重大
**該当箇所:** Appendix A
**問題:**
修正後も Appendix A に記載されているのは H1, H6, H11, H20, H33, H58, H65, H67 の 8 件のみであり、残り 61 件は「...」で省略されている。Brief §5 は「全 69 仮説の一覧表（ID, 名称, 判定, 主要指標）」を明示的に要求している。69 仮説の体系的テストという論文の中核的主張は、Appendix による完全な記録があって初めて査読可能・再現可能となる。

**修正要求:**
`ssot/project_status.json` の `hypotheses_index` から全 69 件を読み込み、Appendix A を完全版（69 行）に更新すること。最低限以下の列を含むこと: ID, 簡潔な仮説名, Cycle 番号, 判定（ACCEPT/REJECT/MODIFIED）, 主要指標（p 値または R²）。

---

## 推奨修正事項（任意）

* **Section 5.1 の文法**: 「the framework face significant quantitative limits」→「faces」に修正すること。
* **CKM モデル記述の正確性**: Section 4.4 の「using Jones polynomial phases at the 24-cell resonance point」は、SSoT が記録するモデル名「Logit-Geometric + Holonomy」および式 `logit(V_ij) = C + A·dV + B·dlnJ + beta/V_bar + gamma·(dV·dlnJ)` と一致しない。「using a logit-geometric model with Jones polynomial features (H67)」等の正確な記述への変更を推奨。
* **References の品質**: Witten 1989（Comm. Math. Phys. 121:351-399）および Atiyah 1990 の正式 DOI / 巻号を追記することを推奨。Ref. [4] は内部文書であり、arXiv 投稿前に Zenodo アーカイブ後の DOI に置き換えること。
* **Section 4.2 の FPR 記述**: SSoT の実記録値は `fpr=0.0`（10,000 試行中 0 件）。「FPR < 0.2%」は技術的に正しいが不正確。「FPR = 0.0 (0/10,000 permutations; resolution = 10⁻⁴)」の形式を推奨。
* **"12 SM particles" と fermion mass formula の整合性**: Section 4.1 の「regression of the 12 SM particles」は、Brief が「フェルミオン質量公式」と分類していることと矛盾しうる。質量公式の対象が 12 粒子（フェルミオン + ボソン）である場合は明記し、そうでなければ「fermion mass formula (9 fermions)」等に修正すること。

---

## 数値照合結果

| 項目 | draft の値 | SSoT の値 | 一致 |
|------|-----------|----------|------|
| κ = π/24 近似値 | 0.1308997 | 0.1308996938995747 | ✓（有効数字 7 桁の範囲内） |
| 質量公式 R² | 0.9998 | `validation_metrics.H11_R2 = 0.9995`（H11 単体） | △（複合モデルの SSoT 出典明示なし） |
| η for leptons | 20.0 | `theoretical_mass_laws.lepton_slope = 20.0` | ✓ |
| η for quarks | 10.0 | `theoretical_mass_laws.quark_slope = 10.0` | ✓（前版 R-2 解消） |
| ボソン切片 C | π√3 (≈5.4414) | `C_theoretical = "pi * sqrt3 + 1/10"` → 5.5414 | ✗（新規不一致） |
| CKM R² | 0.9980 | `ckm_optimized_coefficients.r2_achieved = 0.9980` | ✓（前版 R-1 解消） |
| G_derived（高精度） | 6.708001762 × 10⁻³⁹ | `G_derived_refined = 6.708001762e-39` | ✓（前版 R-3 解消） |
| G 誤差率 | 0.0000263% | 上記値から計算 ≈ 0.0000263% | ✓ |
| 割当 p 値 | 0.0 | `assignment_rules.statistical_validation.p_value = 0.0` | ✓ |
| 割当 FPR | < 0.2% | `assignment_rules.statistical_validation.fpr = 0.0` | △（値は包含されるが不正確） |
| H58 p 値 | 0.067 | NEG-20260227-02: `mc_joint_p_value = 0.067` | ✓ |
| H59 LOO-R² | 0.11 | NEG-20260227-03: `LOO-R² = 0.1075` | ✓（有効桁 2 桁の範囲内） |
| H60 OR | 0.745 | NEG-20260227-04: `OR = 0.7452` | ✓（有効桁内） |
| 仮説総数 | 41/24/4 | Brief §4 と一致 | ✓ |
| Bonferroni 閾値 | ≈ 0.0167 | `bonferroni_base_alpha = 0.05` / 3 = 0.0167 | ✓ |
| MC seed | 42 | `analysis_parameters.random_seed = 42` | ✓（前版 "seed missing" 解消） |
| アクシオン質量 | 記述なし | `axion_prediction.m_a_uev = 12.16` | ✗（requires_caveat 項目の欠落） |
| DM 候補数 | 記述なし | `dark_matter_candidates.stable_link_candidates_count = 67` | ✗（requires_caveat 項目の欠落） |

---

## 前版（Revision 0）からの修正対応状況

| 前版指摘 | 状態 |
|---------|------|
| R-1: CKM R² 不一致 (0.9930→0.9980) | 解消 ✓ |
| R-2: η_quark 不一致 (10/7→10.0) | 解消 ✓ |
| R-3: G 有効数字不足 | 解消 ✓ |
| R-4: 自由パラメータ過小申告 | 解消 ✓ |
| R-5: requires_caveat 欠落（PMNS, DM, axion） | 部分解消 △ (PMNS ✓, CKM forbidden ✓, DM ✗, axion 値 ✗) |
| R-6: H23 言及欠如 | 未解消 ✗ |
| R-7: "deeply encoded" 過剰主張 | 解消 ✓ |
| R-8: Appendix A 不完全 | 未解消 ✗ |

---

## ACCEPT 基準の充足状況

| 基準 | 状態 | 備考 |
|------|------|------|
| SSoT 数値との一致 | ✗ | C = π√3 vs π√3 + 1/10（R-1） |
| 過剰主張なし | ✓ | "deeply encoded" 削除済み、Conclusion の表現は適切 |
| 否定的結果の言及 | ✗ | Abstract から明示削除（R-2）、DM・axion 値欠落（R-3, R-4） |
| 自由パラメータ明示 | ✓ | Section 4.1・4.4 の表で明示 |
| 統計手法の正確な記述 | ✓ | Bonferroni・LOO-CV・MC seed すべて記述あり |
| Abstract の正確性 | ✗ | 否定的結果の明示言及が欠落（R-2） |
| 合成データ不使用 | △ | 明示的確認なし。SSoT `model_validation._warning` が ln_ST の合成データ起源を記録しており、本 draft の結果が実データのみに基づくことの明示が引き続き推奨される |

---

*Review updated under AIRDP Auditor Protocol — Revision 1 (post-correction)*
*Remaining blockers: R-1 (C value), R-2 (Abstract), R-3 (DM), R-4 (axion), R-5 (H23), R-6 (Appendix A)*
*Next action: Writer addresses R-1 through R-6 and resubmits as draft_v02.*
