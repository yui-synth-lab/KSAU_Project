# Researcher Report — Iteration 9

**実施日:** 2026-02-27
**担当タスク:** KnotInfo 全データ（交差数 3–12, N=7163）における det(K) mod 24 と TSI(K) の計算・分布確認

## 1. 実施内容の概要
本イテレーションでは、新規仮説H60に基づき、24-cell対称性の一般性を検証するための準備を行いました。
KnotInfo および LinkInfo データベースから交差数3〜12の全結び目・絡み目データ（有効な不変量を持つ N=6502 件）を抽出し、それぞれの行列式 `det` と 位相安定性インデックス `TSI = n * u / |s|` を計算しました。
そして、`det ≡ 0 (mod 24)` を満たすか否か、および `TSI ≥ 24` を満たすか否かで分類し、次イテレーション（Iter 10）でのFisher正確確率検定に向けた2×2の分割表（Contingency Table）を構築しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_23
g.md への対応
新規仮説（H60）の初回イテレーションのため該当なし。

## 3. 計算結果
`results.json` に記録された主要な計算結果および分割表は以下の通りです。
- **処理された結び目・絡み目の総数:** 6502件
- **正則化条件:** $|s| = 0$ の結び目については、TSI = $\infty$ （$\ge 24$ と判定）として処理しました。
- **2×2 分割表:**
  - `det ≡ 0 mod 24` かつ `TSI ≥ 24`: 115
  - `det ≡ 0 mod 24` かつ `TSI < 24`: 625
  - `det ≢ 0 mod 24` かつ `TSI ≥ 24`: 1141
  - `det ≢ 0 mod 24` かつ `TSI < 24`: 4621

この表を用いて、次イテレーションにおいて {det ≡ 0 (mod 24)} の集合が {TSI ≥ 24} に対して有意に偏っているか（正の相関・オッズ比 > 1）をFisher正確確率検定で評価します。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー:
  - `mathematical_constants.k_resonance` (=24)
  - `dark_matter_candidates.tsi_threshold` (=24)
  - `lifetime_model.stability_index_formula`
- ハードコードの混在: なし
- 合成データの使用: なし（KnotInfo / LinkInfo の実データのみを使用）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_09\code\h60_iter_09.py: TSIとdetの計算、および分割表生成スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_09esults.json: 抽出結果および分割表データ
- E:\Obsidian\KSAU_Project\cycles\cycle_23\iterations\iter_09esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
交差数3〜12の全結び目・絡み目に対して、指定の不変量に基づく分類を完了し、2×2分割表の作成に成功しました。
一部の結び目（$|s|=0$）については、ロードマップの「TSI = ∞ (≥ 24) として扱う」という指示に従って適切に正則化処理を行っています。
次イテレーション（Iter 10）では、この分割表を用いてFisher正確確率検定およびモンテカルロ置換検定によるFPRの推定を実行します。進めてよろしいかご確認をお願いいたします。