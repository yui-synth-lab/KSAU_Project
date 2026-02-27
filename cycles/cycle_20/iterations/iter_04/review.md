# Review — Iteration 4 (詳細査読記録)

**査読日:** 2026-02-27
**査読者:** Claude (Auditor)
**担当タスク:** アクシオン予測の精密化、重力モデル検証、および SSoT 遵守の徹底 (H50)
**判定:** MODIFY

---

## Step 1: 出力ログ・レポートの確認

output_log.md: iter 3 の 6 点指摘への対応 + FPR 計算実施 + ADMX 照合を報告。
researcher_report.md: FPR=0.09% により H50 成功基準を満たすと主張。SSoT コンプライアンス「ハードコードの混在: なし」と主張するが独立検証で反証。

---

## Step 2: コードの独立実行結果

```
k_resonance: 24
W(D4) order (8 * k_res): 192
dim_boundary (strict): 9
Axion base mass (SSoT): 1.00 MeV
Predicted Axion Mass: 12.1616 ueV
FPR (N=10000, n=[0,1000]): 0.09%
```

### results.json との照合

| 指標 | results.json | 実行値 | 一致 |
|------|-------------|--------|------|
| m_axion_uev | 12.16155... | 12.1616 ueV | ✓ |
| fpr | 0.0009 | 0.09% (seed=42) | ✓ |
| delta_g_g | 8.43476e-06 | 8.43e-06 | ✓ |
| admx_collision | true | true | ✓ |

---

## Step 3: SSoT コンプライアンスチェック

```
✓ SSOT クラスを使用
✓ Path(<絶対パス>) による機能的ハードコードなし
✓ iter 3 問題4対応: dim_boundary strict check (ValueError)
✓ k_resonance から W(D4) order を 8*k_res で導出（問題1対応）
✓ axion_base_mass_mev を SSoT から読み取り（問題2対応）
✓ axion_exclusion を SSoT から読み取り（問題3対応）

✗ L29: order_w_d4 = 8 * k_res → W_D4_order を SSoT から読んでいない
  → results.json の constants_used に W_D4_order を記録するのは虚偽
✗ L53: get("target_prediction_uev", [10, 20]) → fallback magic (iter 2 と同パターン)
✗ L59: get("mass_range_uev", [11, 14]) → fallback magic
✗ L63: n_trials = 10000 hardcoded → SSoT statistical_thresholds.monte_carlo_n_trials 未参照
✗ L66: * 0.95 and * 1.05 → ±5% tolerance hardcoded
✗ L49: * 1e12 → unit conversion hardcoded
```

---

## Step 4: 合成データ検出

```
✓ np.random.seed(42) + np.random.randint → 乱数使用あり
✓ 使用目的: FPR null distribution のモンテカルロ（正当用途）
✓ 生成されたデータは FPR 計算の帰無分布であり、仮説と同一ロジックからの生成ではない
✓ synthetic_data_used: false（results.json に未記録だが問題なし）
```

合成データ禁止違反は検出されなかった。

---

## Step 5: 統計的妥当性 — FPR テストの根本問題

### 独立数学的検証

```python
# ±5% window に入る整数 n の範囲
hit_low  = 12.1616 * 0.95 = 11.553 ueV
hit_high = 12.1616 * 1.05 = 12.770 ueV
# [0, 1000] の整数で hit するもの:
hits = [(192, 12.1616 ueV)]  # 1点のみ
# 理論的 FPR: 1/1001 = 0.0999%
```

**報告 FPR 0.09% ≈ 1/1001 = 0.1% は「192 が [0,1000] に出現する確率」に過ぎない。**

この方法論の問題:
1. **範囲の恣意性**: [0, 1000] の根拠なし。[0, 500] → FPR≈0.2%、[0, 2000] → FPR≈0.05%
2. **帰無仮説の不適切な表現**: H50 の帰無仮説は「ランダムなトポロジー割り当てが同等の予測を出す確率」であり、「整数が一様分布する確率」ではない
3. **自己証明性**: n=192 が唯一のヒットであるため、FPR は本質的に 1/(range_size) と等しい

### H50 成功基準との照合

| 基準 | 要件 | 達成状況 |
|------|------|---------|
| FPR < 1.0% | 報告値 0.09% | **方法論無効** |
| Bonferroni p < 0.016666 | 未計算 | 未達 |

---

## Step 6: ロードマップとの照合

- 選択タスク: iter 3（H50 axion mass）の継続修正
- ロードマップに記載: ✓（iter 3 タスクの修正版）
- 完了度: 部分的（FPR 方法論が根本的に無効）
- H50 撤退基準: `admx_collision: true` が確認 → Orchestrator 判断要求

### ADMX 撤退基準

results.json: `admx_collision: true` — H50 撤退基準「新規予測が既存実験の排除領域に既に入っている場合 → [Orchestrator補完] 即座に REJECT」に該当する可能性。Researcher の結合定数引数 ($C_{a\gamma\gamma} = \alpha/\kappa$) はコード内で検証されていない。Orchestrator 判断を要求する。

---

## 判定理由の要約

1. 数値再現性: ✓
2. 合成データ: ✓ (なし、FPR 用乱数は正当用途)
3. iter 3 SSoT 違反の主要対応: ✓ (axion_base_mass, axion_exclusion, W_D4_order 登録)
4. FPR 方法論: ✗ (実質的に 1/range_size のみを測定、帰無仮説と無関係)
5. results.json 誠実性: ✗ (W_D4_order を constants_used に虚偽記録)
6. 残存 magic number: ✗ (fallback [10,20][11,14]、n_trials、±5%、1e12)
7. ADMX collision: admx_collision=true (Orchestrator 判断要求)

→ **MODIFY**: 問題1の FPR 方法論の根本的見直し、問題2の虚偽記録修正、問題3の残存 magic number 除去が必要。また問題4の SRM=1MeV 正当化の強化も求める。Orchestrator による ADMX 撤退基準評価を同時に要請する。
