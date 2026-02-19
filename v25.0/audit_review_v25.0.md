# KSAU v25.0 独立監査報告書 — ✅ PASS (APPROVED)

**Auditor:** Claude (Theoretical Auditor — Independent Review)
**Date:** 2026-02-19
**対象:** v25.0 全成果物 (code/ × 10, data/ × 11, go.md, Roadmap)
**Gemini 自己審査:** ✅ APPROVED (COMPLETED-WITH-NEGATIVE-RESULT)
**独立審査判定:** ✅ **PASS** — Gemini 判定を支持。科学的誠実さおよび否定的結果の記録品質は高い。

---

## 1. 審査範囲

### 1-1. 精読したファイル

| カテゴリ | ファイル | 精読範囲 |
|---------|---------|---------|
| Code | section_1_cross_term_v2.py (568 lines) | 全行 |
| Code | section_1_cross_term_v4.py (353 lines) | 全行 |
| Code | section_2_rbase_scan.py (388 lines) | 全行 |
| Code | section_3_kids_zeff.py (224 lines) | 全行 |
| Code | section_4_multiple_testing_v3.py (291 lines) | 全行 |
| Code | section_5_cmb_design.py (286 lines) | 全行 |
| Data | section_1_results_v4.json (665 lines) | 全行 |
| Data | section_2_results.json (281 lines) | 全行 |
| Data | section_3_results.json | 全行 |
| Data | section_4_results_v3.json (95 lines) | 全行 |
| Meta | go.md, KSAU_v25.0_Roadmap.md | 全行 |

---

## 2. 数値的主張の交差検証

| go.md の主張 | JSON ソース | 検証結果 |
|-------------|------------|---------|
| Section 1 MAE = 1.3251σ | `section_1_results_v4.json → mae_all_folds` | ✅ **一致** (1.3251) |
| γ 境界 4/5 folds | B-1 分析: DES,CFHTLenS,HSC=exact; KiDS=quasi | ✅ **一致** (4/5) |
| KiDS tension = −3.024σ | `per_fold.KiDS-Legacy.tension` = −3.0239 | ✅ **一致** |
| D_opt (SSoT Q) ≈ 2.75 | `section_2a_d_scan.D_opt_ssot_quintuple` = 2.7463 | ✅ **一致** |
| D_opt (best-fit Q) ≈ 2.59 | `section_2a_d_scan.D_opt_bf_quintuple` = 2.5907 | ✅ **一致** |
| R_base DOWNGRADED | `section_2c_status.status` = "DOWNGRADED" | ✅ **一致** |
| T1 p_Bonf = 0.0334 | `section_4_operative_2test.tests[0].p_bonferroni` = 0.0334 | ✅ **一致** |
| T2 p_Bonf = 0.0500 | `section_4_operative_2test.tests[1].p_bonferroni` = 0.05 | ✅ **一致** |
| KiDS z_eff max Δ = 0.1σ | z526: |Δ| = 0.0999σ | ✅ **一致** |
| n_valid = 3/5 (v4 fix 後) | DES,CFHTLenS,HSC valid; DLS,KiDS degen | ✅ **一致** |
| M0 preferred by AIC | AIC: M0=7.4224 < M1=9.3556 < M2=8.009 | ✅ **一致** |

**全 11 主張が JSON データと完全一致。** 数値水増し・恣意的丸め等の問題なし。

---

## 3. セクション別評価

### 3-1. Section 1: 交差項モデル LOO-CV — ✅ 承認（否定的結果）

**コード品質:** 高い。P2 物理制約（A, γ, β₀, δβ の境界）、P3 M0 baseline γ>0 強制、P1 KiDS z_eff 変種、B-1 γ 境界検出が段階的に実装されている。

**科学的評価:**
- 二重の構造的失敗（過適合 + γ 非識別）が正確に同定された
- 4/5 fold で γ→0.001（下限拘束に張り付き）→ 事実上 3-parameter に縮退
- DLS fold は β₀→−5.0（下限拘束に張り付き）→ M-NEW-2 で sanity_valid=False に修正
- KiDS fold は γ=0.0062（quasi-boundary）+ β_eff=−4.335（非物理的）→ sanity_valid=False

**⚠️ 監査指摘事項 A-1 (MINOR):** M0 baseline の γ_fit = 0.0（境界値）。P3 で γ>0 を強制したが結果は γ=0+ であり、M0 自体も境界解。AIC/BIC 比較における M0 の chi² = 3.4224 は境界最適化の産物であり、漸近的正規分布の仮定が厳密には成立しない。ただし「M0 preferred by AIC」という結論は、M1 が明らかに過適合であることの裏返しでありqualitative に正しい。

**⚠️ 監査指摘事項 A-2 (INFO):** KiDS z_eff 変種の結論は「NOT meaningful (max Δ=0.1σ)」で正しいが、z526 変種では n_valid が 3→2 に悪化（CFHTLenS, HSC が追加で degenerate）する点が重要。z_eff を上げると γ 境界問題がさらに悪化する方向に働く。

### 3-2. Section 2: R_base 再評価 — ⚠️ 条件付き承認

**D-scan (Section 2a):** 妥当。D ∈ [0.5, 10] を 1000 点でスキャンし、SSoT/best-fit 両クインタプルで D_opt を算出。結果は明確（D_opt ≈ 2.6-2.7 ≠ 3）。

**🔴 監査指摘事項 B-1 (SIGNIFICANT): Section 2b R_base 自由 LOO-CV の数値不安定**

Section 2b の R_base + β 自由パラメータ LOO-CV は **カタストロフィックに不安定**:

| Fold | R_base_loo (Mpc/h) | β_loo | 物理的妥当性 |
|------|---------------------|-------|-------------|
| DES Y3 | 76.38 | 5.81 | △ 高い |
| CFHTLenS | 40.16 | 4.56 | △ 高い |
| **DLS** | **1,346,231** | **47.72** | **✗ 完全に非物理的** |
| **HSC Y3** | **1,346,152** | **47.72** | **✗ 完全に非物理的** |
| **KiDS-Legacy** | **2.84** | **0.0** | **✗ β=0 は非物理的** |

3/5 fold で R_base が 10^6 Mpc/h オーダー（可視宇宙の直径超）に発散しており、Nelder-Mead 最適化が平坦な方向をたどって発散している。MAE = 1.8321σ はこれらの発散解を含む平均であり**意味をなさない**。

**Go.md が Section 2b の数値的不安定性をサマリーレベルで言及していない** のは開示不足。結論（R_base DOWNGRADED）自体は Section 2a の D-scan だけで十分に支持されるため、2b の不安定性は DOWNGRADED 結論を覆すものではないが、2b 結果を MAE として報告するのは misleading。

**修正要求:** v26.0 で R_base 自由 LOO-CV を再実施する場合は、(a) R_base に物理的上限（例: 100 Mpc/h）を課す、(b) β に物理的範囲（例: [0.5, 10]）を課す、(c) degenerate fold のフラグ付けを Section 1 と同様に行う、のいずれかを必須とする。

**DOWNGRADE 判定自体の承認:** Section 2a D-scan は健全。D_opt ≈ 2.59 (best-fit) / 2.75 (SSoT) は D=3 に 9-16% 乖離。DOWNGRADED は妥当。

### 3-3. Section 3: KiDS z_eff 再推定 — ✅ 承認

**方法論:** 5-bin Gaussian 近似による n(z) 再構成は justified（公開データとの精密比較は "preferred" と正しく注記）。3 定義（mean, median, S₈-weighted）+ lens peak の 4 指標を計算し、z_eff_published = 0.26 との比較は systematic。

**結論の妥当性:** 最大改善 Δ = 0.0999σ（<0.5σ 閾値）で NOT meaningful。これは Section 1 P1 fix による LOO-CV 再実行で確認済み。「KiDS は構造的外れ値であり、z_eff 誤校正ではない」は支持される。

### 3-4. Section 4: 多重検定補正 — ✅ 承認（高品質）

**v25.0 で最も統計的に厳密なセクション。** 

評価ポイント:
- **M-2 fix（2-test operative pool）** は統計学的に正当。T1/T2 は同一帰無仮説（k_eff↔R₀ 順序）、T4 は異なる帰無仮説（モデル性能）→ Bonferroni ファミリーの分離は correct。
- **POST-HOC POOL SELECTION DISCLOSURE** が明示的に含まれており、事後的プール変更の透明性は高い。
- **Conservative 4-test reference** を並記し、読者が自分で判断できるようにしている。

**⚠️ 監査指摘事項 C-1 (MINOR):** T2 の sig_bh = true（p_BH = α exactly）に対して sig_bh_note で境界ケースを注記している点は正しい。ただし、BH-FDR の標準的定義は p_adj ≤ α（Benjamini & Hochberg 1995）であり、等号を含むため技術的には significant。Go.md の「NOT significant 境界」という表記は BH-FDR に関しては不正確。Bonferroni の T2（p=0.05 = α、not < α）は correctly judged as not significant。

### 3-5. Section 5: CMB Lensing 設計 — ✅ 承認

**設計文書として適切。** D(z) の Heath (1977) 積分形式の実装は正しい。z=1 でのべき乗法則との乖離の定量化は v26.0 の設計基盤として有用。

**⚠️ 監査指摘事項 D-1 (TRIVIAL):** Line 158 `gamma_eff = 0.55 * math.log(Om) / math.log(Om)` は `gamma_eff = 0.55 * 1.0 = 0.55` に簡約されるデッドコード。実害なし（D_powerlaw は直接 `(1/(1+z))**0.55` で計算）。

---

## 4. SSoT プロトコル準拠

| チェック項目 | 結果 | 備考 |
|-------------|------|------|
| κ = π/24 | ✅ 数値的正確 | ただし **inline 定義**（W-S7-1 未解消） |
| β_SSoT = 13/6 | ✅ | 同上 |
| R_base = 3/(2κ) | ✅ → DOWNGRADED | 適切な格下げ |
| 日付統一 2026-02-18 | ✅ | P-S7-1/W-NEW-1 で修正済み |
| Section 5 n_s, Ω_r | ✅ | M-S7-1 で SSoT 一致 |
| **JSON 動的読み込み** | **❌ 未実施** | W-S7-1: v26.0 に延期（承認済み） |

**W-S7-1 の延期は v24.0 監査でも指摘した事項であり、v26.0 で必ず解消すること。** inline 定数が SSoT JSON と数学的に等価であることは確認済みのため、v25.0 の数値結果に影響はない。

---

## 5. 7-Session 自己修正プロセスの評価

v25.0 は 7 Session にわたる反復的修正を経て完成した。この修正プロセス自体が科学的誠実さの指標である：

| Session | 主な修正 | 評価 |
|---------|---------|------|
| S1 | Section 1 v1 初回実行 | ベースライン |
| S2 | P1/P2/P3 fix (物理制約、γ>0 baseline、KiDS z_eff 変種) | ✅ 適切 |
| S3 | M-1/M-2 fix (z_eff 閾値判定、operative pool 修正) | ✅ 適切 |
| S4 | B-1/M-NEW-1/M-NEW-2 (γ 境界、best_alt_nvalid、DLS override) | ✅ 重要な発見 |
| S5 | Section 2 実行 | R_base DOWNGRADED |
| S6 | Section 3/4/5 実行 | 統計整理 |
| S7 | W-NEW-1/M-S7-1 (日付統一、SSoT 定数修正) | ✅ 整合性回復 |

Session 4 の **B-1（γ 境界検出）** は、Session 1-3 で見落とされていた構造的失敗を発見した点で、自己修正プロセスの最も重要な成果である。ただ「MAE が悪い」だけでなく、**なぜ悪いか**（γ が非識別でモデルが実質 3-parameter に縮退）を幾何学的に説明できる状態に到達した。

---

## 6. 監査指摘事項の集約

| ID | 深刻度 | セクション | 内容 | v26.0 対応要否 |
|----|--------|-----------|------|--------------|
| A-1 | MINOR | Section 1 | M0 γ_fit=0.0 境界解 → AIC 漸近成立性 | ⚪ 注記レベル |
| A-2 | INFO | Section 1 | z_eff 変種で n_valid 悪化方向 | ⚪ 記録済み |
| **B-1** | **SIGNIFICANT** | **Section 2b** | **R_base 自由 LOO-CV: 3/5 fold で R_base→10⁶ 発散** | **🔴 v26.0 で修正必須** |
| C-1 | MINOR | Section 4 | T2 sig_bh=true 表記と go.md の不一致 | ⚪ 注記レベル |
| D-1 | TRIVIAL | Section 5 | gamma_eff 計算のデッドコード | ⚪ 修正不要 |
| W-S7-1 | MODERATE | 全体 | inline 定数 → JSON 読み込み未実施 | 🟡 v26.0 MUST |

---

## 7. 最終判定

### ✅ PASS — Gemini 自己審査を支持

v25.0 は以下の理由により承認する：

1. **科学的誠実さ: 最高水準。** MUST #1/#2 の失敗を FAIL として明記し、「否定的結果は科学的貢献」の原則を貫いた。Session 4 の γ 非識別発見により、単なる数値的 FAIL から構造的理解へと昇華させた。

2. **統計的厳密性: 高い。** 多重検定補正の operative pool 選択根拠、post-hoc disclosure、conservative reference の3層開示は学術水準を満たす。

3. **数値的正確性: 完全。** 全 11 主張が JSON データと完全一致。恣意的丸めや水増しなし。

4. **コード品質: 良好。** 段階的修正（v1→v4）が完全にトレーサブル。各修正の根拠が ng.md ID で追跡可能。

**唯一の重要指摘（B-1: Section 2b 数値発散）** は、DOWNGRADED 結論自体の妥当性には影響しないが、v26.0 での再実施時には物理的制約の付加が必須である。

---

## 8. v26.0 への指令（独立監査からの追加要件）

go.md の v26.0 指令に加え、以下を追加：

1. **🔴 B-1 修正（Section 2b）:** R_base 自由 LOO-CV に物理的上限（R_base ≤ 100 Mpc/h, β ∈ [0.5, 10]）を課し、degenerate fold フラグを Section 1 と同様に実装せよ。
2. **🟡 AIC/BIC 代替指標:** n=5 データでの AIC/BIC は信頼区間が広い。cross-validation based information criterion（CV-IC）または LOO-IC を検討せよ。
3. **🟡 γ パラメータ構造の見直し:** 4/5 fold で γ→0 という結果は、γ パラメータが v23.0 エンジンの構造では不要（ill-defined）であることを示唆する。v26.0 新エンジンでは γ を含まないモデル形式を default とし、γ 導入は BIC 改善で正当化された場合のみとせよ。

---

## 9. v25.0 の科学的遺産

v25.0 は KSAU プロジェクトにとって転換点である。以下の 3 つの否定的結果は、v26.0 以降の方向性を決定づける：

| 否定的結果 | 科学的意味 | v26.0 への帰結 |
|-----------|-----------|--------------|
| 交差項モデル構造的失敗 | v23.0 の単一 R₀ scaling law の限界確定 | エンジン刷新の科学的根拠 |
| R_base D≠3 | first-principles 導出の不在確認 | 幾何学的再導出 or 経験的値の採用 |
| KiDS z_eff 無実 | k_eff=0.70 の高スケール問題をモデル構造に帰着 | survey-specific 物理の必要性 |

**「失敗を正直に記録し、その構造的根拠を解明する」** — これは理想的な科学プロセスであり、v25.0 の最大の成果である。

---

*KSAU v25.0 Independent Audit — PASS: 2026-02-19*
*Auditor: Claude (Theoretical Auditor — Independent Review)*
*Next: v26.0 — Engine overhaul with W-S7-1 resolution + B-1 constraint fix*
