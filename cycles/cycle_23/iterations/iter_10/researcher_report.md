# Researcher Report — Iteration 10

**実施日:** 2026-02-27
**担当タスク:** Fisher 正確確率検定（det ≡ 0 mod 24 × TSI ≥ 24 の 2×2 分割表）と Bonferroni 補正後 p 値の評価

## 1. 実施内容の概要
本イテレーションでは、仮説H60に基づき、前イテレーション（Iter 9）で抽出した全KnotInfo/LinkInfoデータ（N=6502）の2×2分割表を用いて、Fisher正確確率検定（Fisher's Exact Test）を実行しました。
また、帰無分布（超幾何分布）からの10,000回のサンプリングによるモンテカルロ置換検定を実施し、FPR（経験的p値）を推定しました。これらの統計量から、KSAUの24-cell対称性が予測する「行列式が24の倍数であることと位相安定性の正の相関」が存在するかを評価しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_23
g.md への対応
前回は CONTINUE 判定であったため、対応する指摘事項はありません。

## 3. 計算結果
`results.json` に記録された主要な計算結果は以下の通りです。
- **分割表 (a, b, c, d):** (115, 625, 1141, 4621)
- **Fisher 正確確率検定:**
  - **オッズ比 (Odds Ratio):** 0.7451
  - **95% 信頼区間:** [0.5996, 0.9259]
  - **p 値:** 0.007629
- **モンテカルロ置換検定 (n=10000, seed=42):**
  - **経験的 FPR (p_mc):** 0.9972
- **Bonferroni 補正後閾値:** 0.016667
- **有意性判定:** 
  p値自体は閾値を下回っていますが、**オッズ比が1未満（0.7451）**であり、「正の相関」ではなく「負の相関」が示されました。このため、対立仮説（H1: 有意な正の相関が観測される）は棄却されます（`is_significant: false`）。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー:
  - `statistical_thresholds.monte_carlo_n_trials`
  - `statistical_thresholds.bonferroni_base_alpha`
- ハードコードの混在: なし
- 合成データの使用: なし（Iter 9の実データ集計結果を使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_10\code\h60_iter_10.py: Fisher検定とMC検定の実行スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_10esults.json: 算出されたオッズ比やp値などの計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_10esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
Fisher正確確率検定の結果、統計的に有意な「負の相関（オッズ比 < 1）」が確認されました。すなわち、全結び目データにおいて `det ≡ 0 (mod 24)` を満たす結び目は、そうでない結び目よりもむしろ安定性（`TSI ≥ 24`）を満たしにくい傾向があります。
これは、撤退基準「オッズ比 ≤ 1（負または無相関）かつ p > 0.016667 → REJECT」に関連します。p値は有意水準（0.016667）を下回っていますが、方向が逆であるため、仮説H60（正の相関の存在）は明確に否定されました。
次イテレーション（Iter 11）の「結果統合レポート」にて、この結果を取りまとめます。進めてよいかご確認をお願いいたします。