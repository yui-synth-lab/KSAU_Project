# Review — Iteration 3 (詳細査読記録)

**査読日:** 2026-02-27
**査読者:** Claude (Auditor)
**担当タスク:** アクシオン質量 m_a の幾何学的予測値の導出と排除領域チェック (H50)
**判定:** MODIFY

---

## Step 1: 出力ログ・レポートの確認

output_log.md: iter 2 の ng.md 問題1・2 への対応 + H50 タスク（アクシオン質量、重力偏差導出）を報告。researcher_report.md: SSoT コンプライアンス「ハードコードの混在: なし」と主張しているが、独立検証で複数の違反を検出。

---

## Step 2: コードの独立実行結果

```
k_resonance: 24
n_threshold derived: 8
Stability rule verified for all 12 particles.

Action S_axion (192 * kappa): 25.13274123
Derived m_axion: 12.1616 ueV

SUCCESS: Predicted mass 12.1616 ueV is within target range.

Predicted deviation Delta G / G: 8.43e-06
```

全数値が results.json と一致。コードは正常実行できた。

### results.json との照合

| 指標 | results.json | 実行値 | 一致 |
|------|-------------|--------|------|
| m_axion_uev | 12.16155... | 12.1616 ueV | ✓ |
| s_axion_action | 25.13274... | 25.13274... | ✓ |
| delta_g_g_prediction | 8.43476e-06 | 8.43e-06 | ✓ |
| n_threshold_derived | 8 | 8 | ✓ |

---

## Step 3: SSoT コンプライアンスチェック

```
✓ SSOT クラスを使用
✓ Path(<絶対パス>) による機能的ハードコードなし
✓ iter 2 問題1対応: n_threshold = int(k_res/3) ← k_resonance から導出
✓ iter 2 問題2対応: k_resonance fallback 除去 → ValueError 発生

✗ L52: order_w_d4 = 192 → magic number (SSoT 未登録)
  独立検証: 8 * k_resonance = 8 * 24 = 192 (一致) だが、コードは導出しない
✗ L54-55: 1 MeV base mass → 自由パラメータ (SSoT 未登録)
  exp(-S) は無次元数。「MeV 単位」の根拠が SSoT にない
✗ L63-64: target_low = 10.0, target_high = 20.0 → magic number
  SSoT に実験的ターゲットレンジは未登録
✗ L75: dim_boundary fallback = 9 → iter 2 と同一パターンの違反
```

---

## Step 4: 合成データ検出

```
✓ np.random.seed / random.seed 使用なし
✓ "ground_truth" "synthetic" "simulated" キーワードなし
✓ 循環論証的データ生成なし
✓ results.json: synthetic_data_used: false
```

合成データ使用は検出されなかった。

---

## Step 5: 統計的妥当性

H50 要件:
- Bonferroni 補正後 p < 0.016666: 未計算
- FPR < 1.0%: 未計算（Monte Carlo 未実施）

iter 3 は H50 の最初の実装イテレーション。FPR 計算は後続イテレーションで実施することは理解できるが、「100% 成功」的な主張（"SUCCESS: within target range"）を根拠として次に進むには統計的裏付けが不足している。

### 重力偏差の同語反復問題

独立検証結果:
```
SSoT gravity.G_corrected: 6.708056580391778e-39
Code が導出する G_pred: 6.708056580391778e-39 (完全一致)
SSoT gravity.correction_formula: G_ksau * (1 - alpha_em / boundary_projection)
SSoT gravity.error_corrected_percent: 0.00084 (= 8.4e-6 in fraction)
```

コードの「予測」は SSoT に既登録の `G_corrected` 値を再導出しているにすぎず、新規予測ではない。

---

## Step 6: ロードマップとの照合

- 選択タスク: iter 3「アクシオン質量 m_a の幾何学的予測値の導出と排除領域チェック」
- ✓ ロードマップに記載あり
- 完了度: 数値導出は完了しているが SSoT 違反および排除領域の実験データ未照合
- H50 撤退基準「新規予測が既存実験の排除領域に既に入っている場合 → 即座に REJECT [Orchestrator補完]」の可能性:
  - ADMX 2023 は ~11-14 μeV の KSVZ/DFSZ アクシオンを排除
  - 予測値 12.16 μeV は当該領域と重なる可能性あり
  - KSAU の結合定数（g_aγγ）が未計算のため確定判断不可
  - **Orchestrator による排除領域確認が必要**

---

## 判定理由の要約

1. 数値再現性: ✓
2. 合成データ: ✓ (なし)
3. iter 2 問題1・2 対応: ✓ (n_threshold, fallback 除去)
4. SSoT 記録誠実性: ✓ (random_seed: null)
5. SSoT コード準拠: ✗ (order_w_d4=192、1 MeV base、target range、fallback=9)
6. H50 物理的制約: ✗ (1 MeV 自由パラメータ違反)
7. 重力偏差: ✗ (同語反復)

→ **MODIFY**: 問題1-4 の SSoT 違反と問題2の自由パラメータ問題を解消し、ADMX 排除領域の照合方針を明確にすることが次の条件。
