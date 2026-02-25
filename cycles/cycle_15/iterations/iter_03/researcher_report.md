# Researcher Report — Iteration 3

**実施日:** 2026-02-26
**担当タスク:** モンテカルロ置換検定による有意性検証

## 1. 実施内容の概要
本イテレーションでは、前イテレーションで得られた崩壊幅 $\ln \Gamma$ のトポロジカル不変量（交差数 $n$、非結び目化数 $u$、署名 $|s|$）による重回帰モデルの有意性を検証するため、10,000回のモンテカルロ置換検定を実施しました。目的変数 $\ln \Gamma$ をランダムにシャッフルし、観測された決定係数 $R^2$ (0.6132) 以上の適合度が偶然得られる確率（False Positive Rate, FPR）を算出しました。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_15
g.md への対応（存在した場合）
存在しなかったため、予定通りのタスクを実行しました。

## 3. 計算結果
- **観測された $R^2$:** 0.6132
- **試行回数:** 10,000回
- **FPR (False Positive Rate):** 0.1012
- **シャッフルされた $R^2$ の平均:** 0.3745
- **シャッフルされた $R^2$ の標準偏差:** 0.1674

FPRは 10.12% であり、撤退基準（FPR > 50%）は下回っていますが、統計的有意性の基準（Bonferroni補正後 $p < 0.025$）と比較すると、現状の 9 サンプルでは決定的な有意性を示すには至っていません。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `constants.json` (via Iteration 01 integrated data)
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_03\code\permutation_test.py: 置換検定実行コード
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_03esults.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_15\iterations\iter_03esearcher_report.md: 本ファイル

## 6. Reviewer への申し送り
FPR 0.1012 は、ランダムな割り当てにおいても約 10% の確率で今回の適合度が得られることを示しています。サンプルサイズが 9 と極めて小さいため、自由度（Df Residuals: 5）の不足が統計的有意性の確保を困難にしています。一方で、$R^2 = 0.6132$ という数値は一定の相関を示唆しており、物理的解釈（Iteration 6 予定）において質的な整合性が確認できるかが鍵となります。
