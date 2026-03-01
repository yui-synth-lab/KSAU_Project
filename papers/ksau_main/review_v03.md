# Review — draft_v03

**査読日:** 2026-03-01
**Reviewer:** Claude (AIRDP Auditor Role)
**対象:** draft_v03.md
**VERDICT:** REVISE

---

## 総評

前版（draft_v02）で指摘した 3 件の必須修正（観測量数の一致・H65 η_quark 値・H2 合成データ caveat）はすべて適切に対処された。しかし、**draft_v02 では正常だった LaTeX コマンドのバックスラッシュ（`\`）がタブ文字（`\t`）に置換されるという regression が新たに発生**しており、対象の数式はすべて壊れた状態にある。これは arXiv 投稿において即座にコンパイル失敗を引き起こす致命的な技術的欠陥である。科学的内容はこの 1 点を除いて査読基準を満たしている。

---

## 必須修正事項

### [R-1]: LaTeX バックスラッシュのタブ文字への置換（致命的・regression）
**深刻度:** 致命的
**該当箇所:** Section 4.3（2 箇所）、Section 5.1（2 箇所）、Section 5.2（1 箇所） — 計 5 箇所

**問題:**
draft_v03 において、複数の LaTeX コマンドのバックスラッシュ（`\`、ASCII 0x5C）がタブ文字（ASCII 0x09）に置き換えられている。これは draft_v02 では正しかった箇所が v03 で壊れた regression である。

ファイル内の実際の内容（grep で確認済み）:

```
行 68: $$G_{derived} = 6.708001762 \t imes 10^{-39} \t ext{ GeV}^{-2}$$
行 69: ...experimental value $6.708 \t imes 10^{-39} \t ext{ GeV}^{-2}$
行 93: ...Cabibbo-forbidden ($u \t o b, t \t o d$) show errors...
行 93: ...PMNS angles achieve an MSE of $5.44 \t ext{ deg}^2$...
行 98: ...$m_a = 12.16\ \mu\t ext{eV}$...
```

（`\t` はタブ文字を表す）

正しいコマンドとの対応:
| 壊れた形 | 正しい LaTeX | 意味 |
|---------|------------|------|
| `	imes` | `\times` | ×（掛け算記号） |
| `	ext{...}` | `\text{...}` | テキストモード |
| `	o` | `\to` | → |

これらの箇所は arXiv の LaTeX コンパイラに `times`、`ext`、`o` という未定義コマンドとして解釈され、コンパイルエラーまたは意図しない出力となる。

**修正要求:**
以下の箇所を修正すること:

1. **行 68**: `6.708001762 	imes 10^{-39} 	ext{ GeV}^{-2}` → `6.708001762 \times 10^{-39} \text{ GeV}^{-2}`
2. **行 69**: `6.708 	imes 10^{-39} 	ext{ GeV}^{-2}` → `6.708 \times 10^{-39} \text{ GeV}^{-2}`
3. **行 93（CKM 遷移）**: `$u 	o b, t 	o d$` → `$u \to b, t \to d$`
4. **行 93（PMNS）**: `$5.44 	ext{ deg}^2$` → `$5.44 \text{ deg}^2$`
5. **行 98（アクシオン）**: `\mu	ext{eV}` → `\mu\text{eV}`

修正後、ローカルの LaTeX コンパイラまたは arXiv の TeX システムで当該数式がレンダリングされることを確認すること。

---

## 推奨修正事項（任意）

* **Section 4.5（DM 候補）の H60 cross-reference**: Section 4.5 は「det ≡ 0 mod 24 and TSI ≥ 24」ルールに基づく DM 候補 67 件を "mathematically robust within the framework" と記述しているが、H60（Section 5.2 で報告）はまさに「det ≡ 0 (mod 24) が安定性（TSI ≥ 24）と負の相関（OR=0.745）を持つ」ことを示しており、DM 選択基準の理論的根拠に直接抵触する。Section 4.5 に H60 への cross-reference を追加し「ただし、H60 が示す負の相関（OR=0.745）はこの安定性基準の理論的根拠に疑問を呈している」旨の 1 文を追記することを推奨。"mathematically robust" の表現は "rule-based" 程度に緩めることが望ましい。

* **H7 R²=0.528 の出典確認**: Appendix A の H7 行（ST Refinement GPR）は R²=0.528 を記載しているが、この値は constants.json に記録されていない（最も近い SSoT エントリは `axion_suppression_model_gpr.r2_final = 0.519`、これは H12 の値）。H7.json の判定結果と照合し、0.528 の出典を Appendix に付記するか、SSoT 記録値が存在しない旨の注記を追加することを推奨。

* **Brief との η_quark 値の不一致（プロジェクトレベルの注意）**: SSoT `theoretical_mass_laws.quark_slope = 10.0` と Brief の "quark=10/7" の不一致は未解消のままである。draft_v03 は SSoT の値（10.0）を正しく採用しているが、Brief との齟齬は Orchestrator が Brief を更新することで解消することを推奨する（paper 側の修正は不要）。

---

## 前版（review_v02）からの対応状況

| 前版指摘 | 対応 |
|---------|------|
| R-1: 観測量数の矛盾（9 vs 12）解消 | ✓ (表: 9 観測, 4:9 比率) |
| R-2: H65 名称「クォーク(10/7)」→「クォーク(10.0)」 | ✓ |
| R-3: H2 合成データ caveat 追加 | ✓（Appendix 冒頭注記 + アスタリスク） |
| 推奨: H64 FPR を 0.0 に統一 | ✓ |
| 推奨: H53 精度を 0.0000263% に統一 | ✓ |
| 推奨: Conclusion "topological phase space" への変更 | ✓ |

---

## 数値照合結果

| 項目 | draft の値 | SSoT の値 | 一致 |
|------|-----------|----------|------|
| κ = π/24 | 0.1308997 | 0.1308996938995747 | ✓ |
| 質量公式 R² | 0.9998 | `H11_R2 = 0.9995`（複合モデル出典は別途 H*.json） | △ |
| η for leptons | 20.0 | `lepton_slope = 20.0` | ✓ |
| η for quarks | 10.0 | `quark_slope = 10.0` | ✓ |
| ボソン切片 C | π√3 + 1/10 ≈ 5.5414 | `C_theoretical = "pi * sqrt3 + 1/10"` | ✓ |
| CKM R² | 0.9980 | `ckm_optimized_coefficients.r2_achieved = 0.9980` | ✓ |
| G_derived（値） | 6.708001762 × 10⁻³⁹ | `G_derived_refined = 6.708001762e-39` | ✓（LaTeX は壊れているが数値は正） |
| G 誤差率 | 0.0000263% | 計算値 ≈ 0.0000263% | ✓ |
| 割当 p 値 | 0.0 | `p_value = 0.0` | ✓ |
| 割当 FPR（本文・Appendix） | 0.0 | `fpr = 0.0` | ✓ |
| H23 FPR | 93.82% | NEG index: FPR=93.82% | ✓ |
| H58 p 値 | 0.067 | NEG-20260227-02: 0.067 | ✓ |
| H59 LOO-R² | 0.11 | NEG-20260227-03: 0.1075 | ✓ |
| H60 OR | 0.745 | NEG-20260227-04: 0.7452 | ✓ |
| H2 R²（合成データ） | 0.767* | `h2_model_b_r2 = 0.7674`（丸め 0.767） | △（asterisk 付き注記あり） |
| H12 R² | 0.519 | `axion_suppression_model_gpr.r2_final = 0.519` | ✓ |
| H11 R² | 0.9995 | `validation_metrics.H11_R2 = 0.9995` | ✓ |
| H24 R² | 0.9129 | `validation_metrics.H24_R2 = 0.9129` | ✓ |
| H31 R² | 0.8015 | `theoretical_models.decay_width.r2 = 0.8015` | ✓ |
| H7 R² | 0.528 | 未記録（GPR r2_final=0.519 は H12 向け） | △（constants.json に対応エントリなし） |
| H53 精度 | 0.0000263% | 計算値: 0.0000263% | ✓ |
| アクシオン m_a | 12.16 μeV | `axion_prediction.m_a_uev = 12.16` | ✓ |
| DM 候補数 | 67 | `dark_matter_candidates.stable_link_candidates_count = 67` | ✓ |
| 仮説総数 | 41/24/4 | Appendix 手動集計: ACCEPT=41, REJECT=24, MOD=4 | ✓ |
| MC seed | 42 | `analysis_parameters.random_seed = 42` | ✓ |
| Bonferroni 閾値 | ≈ 0.0167 | 0.05/3 = 0.01667 | ✓ |

---

## ACCEPT 基準の充足状況

| 基準 | 状態 | 備考 |
|------|------|------|
| SSoT 数値との一致 | ✓ | LaTeX encoding が壊れているが数値自体は正しい。H7 は△だが primary claim ではない |
| 過剰主張なし | ✓ | Conclusion・Abstract とも適切な表現 |
| 否定的結果の言及 | ✓ | H33/H47/H58/H59/H60 + Abstract 24 rejections + H23 Methods すべて適切 |
| 自由パラメータ明示 | ✓ | Section 4.1（4:9）・4.4（5:9）・4.3（0）の表が整合 |
| 統計手法の正確な記述 | ✓ | Bonferroni・LOO-CV・MC seed=42・FPR すべて正確 |
| Abstract の正確性 | ✓ | 24 rejections・κ・R²・G 精度・CKM R² すべて記載 |
| 合成データ不使用 | ✓ | Section 3.2 の宣言 + H2 への asterisk caveat により対処済み |

**技術的阻害要因（査読基準外だが出版阻害）:**
| 項目 | 状態 |
|------|------|
| LaTeX コンパイル可能性 | ✗（R-1: タブ文字置換、5 箇所） |

---

*Review generated under AIRDP Auditor Protocol — Revision 3*
*Single blocker: R-1 (LaTeX tab-for-backslash regression). All 7 ACCEPT criteria are satisfied.*
*After fixing R-1, paper is ready for ACCEPT consideration.*
