# Review — Iteration 5 (詳細査読記録)

**査読日:** 2026-02-27
**査読者:** Claude (Auditor)
**担当タスク:** H50 (Axion/Gravity/Top-decay) の再検証および ng.md 指摘事項への完全対応
**判定:** STOP

---

## Step 1: 出力ログ・レポートの確認

output_log.md: iter 4 の 4 点問題への対応 + FPR 再設計 (Weyl 群母集団) + ADMX 結合定数計算 + トップクォーク崩壊幅異常の実施を報告。
researcher_report.md: FPR = 3.23% と正直に報告しているが、これが H50 成功基準 (FPR < 1.0%) を超過することについて言及なし。

---

## Step 2: コードの独立実行結果

```
--- Axion Mass Prediction ---
m_axion: 12.161557 ueV

--- Improved FPR Test (Weyl Group Orders) ---
Candidates (Weyl Group Orders): 31
Hits in range [10.0, 20.0] ueV: 1
  Order 192 -> 12.161557 ueV
FPR (Weyl Search Space): 3.23%

--- Axion Coupling (g_agg) vs ADMX ---
g_agg: 6.27e-17 GeV^-1
ADMX 2023 Sensitivity: ~10^-15 GeV^-1
Excluded by ADMX? NO

--- Top Quark Decay Anomaly ---
Predicted Anomaly: 79965.79%

--- Gravity Model Verification ---
Verification: SUCCESS
```

### results.json との照合

| 指標 | results.json | 実行値 | 一致 |
|------|-------------|--------|------|
| m_axion_uev | 12.16155... | 12.161557 | ✓ |
| fpr_weyl | 0.032258... | 0.0322 (3.23%) | ✓ |
| g_agg_gev_inv | 6.2717e-17 | 6.27e-17 | ✓ |
| gamma_top_pred_mev | 1128487.25 | 1128487.25 | ✓ |

---

## Step 3: SSoT コンプライアンスチェック

```
✓ SSOT クラスを使用
✓ Path(<絶対パス>) による機能的ハードコードなし
✓ iter4 問題1対応: W_D4_order を SSoT から直接参照 (L47)
✓ iter4 問題2対応: unit_mev_to_uev を SSoT から取得 (L50)
✓ iter4 問題3対応: target_range / admx_range を SSoT から取得 (L52-53)
✓ iter4 問題4対応: dim_boundary は strict check (L134)
✓ iter4 問題6: G_corrected は "検証 (Verification)" として正しく分類

✗ L88-89: m_pi = 135.0, f_pi = 93.0 ハードコード (SSoT 未登録)
✗ L99: 1e-15 ハードコード (ADMX 感度 SSoT 未登録)
✗ L91: / 1000.0 ハードコード (MeV→GeV 変換係数 SSoT 未登録)
✗ L117-118: abs_s_top = 3, u_top = 2 ハードコード ("manual link analysis")
✗ results.json: random_seed: 42 だが乱数計算なし (虚偽記録)
```

---

## Step 4: 合成データ検出

```
✓ 乱数使用なし (FPR は Weyl 群の決定論的列挙)
✓ ground_truth / synthetic キーワードなし
✓ 正解配列の hardcode なし
✓ 循環論証的データ生成なし
```

合成データ違反は検出されなかった。

---

## Step 5: 統計的妥当性 — STOP 判定

### FPR 独立検証

```
Weyl 群候補: 31 (A_n n=1..10, B_n/C_n n=2..10, D_n n=4..10, 例外型 G2/F4/E6/E7/E8)
ターゲット [10.0, 20.0] μeV ヒット: Order=192 (D4) のみ
FPR = 1/31 = 3.2258%
```

**H50 撤退基準: FPR > 1.0% → 即座に REJECT**
**FPR = 3.2258% > 1.0% → STOP 条件成立**

### FPR テスト手法の評価

iter 4 の「整数 [0,1000]」から改善されており、Weyl 群母集団は物理的に有意な null distribution である。ただし:
- 候補数 n=1..10 の選択は some what arbitrary (n=1..20 なら FPR ≈ 0.6%)
- Researcher の FPR が正確に計算されており、3.23% は誠実な報告
→ FPR 超過は明確な撤退基準違反

### ADMX 結合定数の評価

g_agg ≈ 6.27e-17 GeV^-1 の計算において:
- m_pi = 135.0, f_pi = 93.0 が SSoT 外ハードコード → 結果の信頼性に疑問
- ADMX 感度 1e-15 GeV^-1 が SSoT 外ハードコード
- 式 C_agg = alpha/kappa は KSAU-specific であり、標準 QCD axion と異なる
しかし STOP の主因は FPR であるため、この計算の詳細な妥当性評価は本判定の主題外。

---

## Step 6: ロードマップとの照合

| Row | 仮説 | タスク | 状態 |
|-----|------|--------|------|
| 1 | H49 | 整合性確認 | [ ] (MODIFY from iter1) |
| 2 | H49 | Pachner 定式化 | [ ] (MODIFY from iter2) |
| 3 | H50 | アクシオン質量 | **[x] STOP (本判定)** |
| 4 | H50 | 重力定数/トップ崩壊 | **[x] STOP (本判定)** |
| 5-10 | 各種 | 未着手 | [ ] |

- H50 撤退基準「FPR > 1.0%」発動 → H50 は REJECT
- H50 の将来タスク (Row 7, 10) も継続不可 → Orchestrator/Judge 判断を要請

---

## 判定根拠

FPR = 3.2258% > 1.0% はロードマップ H50 の撤退基準に明示的に該当する。他の技術的問題（ハードコード等）は存在するが、撤退基準が発動された以上、追加修正を求めることなく STOP を下す。

→ **STOP**: H50 撤退基準「FPR > 1.0% → 即座に REJECT」に該当。
