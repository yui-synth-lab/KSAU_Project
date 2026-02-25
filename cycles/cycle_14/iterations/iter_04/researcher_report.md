# Researcher Report — Iteration 4

**実施日:** 2026-02-25
**担当タスク:** 様々な不変量組み合わせ（n, ln_det）による V_eff の安定性評価

## 1. 実施内容の概要
本イテレーションでは、仮説 H35 の頑健性を検証するため、有効体積 $V_{eff}$ の構成要素（双曲体積 $V$, 交差数 $n$, 結び目行列式 $\ln(Det)$）の組み合わせが勾配定数 $\kappa$ の再現性に与える影響を定量的に評価した。
1. **モデル比較**: 
   - $V$ のみ（Baseline）
   - $V + n$ 補正
   - $V + \ln(Det)$ 補正
   - $V + n + \ln(Det)$ 補正（Full $V_{eff}$）
   の 4 パターンで回帰分析を行い、$R^2$ および $\kappa$ 理論値（$\pi/24 \approx 0.1309$）からの乖離を算出した。
2. **感度分析**: 理論的に固定された補正係数 $a$ ($n$ の係数) および $b$ ($\ln(Det)$ の係数) を $\pm 10\%$ 変化させ、$\kappa_{fit}$ の安定性を確認した。
3. **自由パラメータ・フィッティング**: 統計的制約を課さない自由な重回帰を行い、理論値との整合性を確認した。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_14
g.md への対応
前回却下指摘なし（Iteration 3 承認済み）。

## 3. 計算結果
### モデル比較結果
- **Model 0 (V のみ)**: $\kappa_{fit} = 0.0647$ (誤差 50.6%), $R^2 = 0.8096$
- **Model 3 (Full $V_{eff}$)**: $\kappa_{fit} = 0.1209$ (誤差 7.67%), $R^2 = 0.8577$
- **考察**: $n$ と $\ln(Det)$ の両方を導入することで、$\kappa$ の再現精度が飛躍的に向上（誤差 50% → 8%）することが確認された。

### 感度分析
- 係数 $a, b$ を共に $+10\%$ 増加させた場合、$\kappa_{fit} = 0.1298$ となり、理論値 $\pi/24$ (0.1309) に極めて近接（誤差 < 1%）する。
- 一方で $R^2$ は 0.8507 と僅かに低下する。これは、理論値 $\pi/24$ への収束と、現在の 9 点のデータサンプルへの統計的適合の間に僅かなトレードオフがあることを示唆している。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `kappa`, `observed_mass_mev`, `volume`, `crossing_number`, `determinant`
- ハードコードの混在: なし（SSoT 経由の物理定数・トポロジーデータのみを使用）
- 合成データの使用: なし

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_04/code/h35_v_eff_stability.py: 安定性評価・感度分析スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_04/results.json: 比較データおよび感度分析結果
- E:\Obsidian\KSAU_Project\cycles\cycle_14\iterations\iter_04/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
- $V_{eff}$ モデルにおける $n$ と $\ln(Det)$ の同時採用は、統計的適合度 ($R^2$) の維持と物理的整合性 ($\kappa$ の再現) の両立において不可欠であることが示されました。
- 係数 $a, b$ の微調整により $\kappa$ の再現精度を 1% 未満まで高めることが可能ですが、過学習を避けるため、次イテレーション以降では H36（理論的導出）による係数の固定を優先すべきと考えます。
