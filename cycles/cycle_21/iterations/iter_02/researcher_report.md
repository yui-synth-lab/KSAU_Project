# Researcher Report — Iteration 2

**実施日:** 2026-02-27
**担当タスク:** 統計的有意性（Bootstrap CI, Monte Carlo FPR）の検証（修正対応）

## 1. 実施内容の概要
前回の指摘（N=2 による過学習と撤退基準抵触）に基づき、分析対象をレプトンだけでなくクォークおよびボソン（計 9 粒子）に拡大し、統計的頑健性を確保した上で再解析を実施した。
具体的には、以下の 9 粒子の実寿命データを SSoT (`parameters.json`, `topology_assignments.json`) から取得した：
Strange, Charm, Bottom, Top, Muon, Tau, W, Z, Higgs。
これによりデータ点数 $N=9$ となり、自由パラメータ数 $k=2$ に対し $k < N/3$ （$2 < 3$）の撤退基準をクリアした。
解析では、$\ln(	au) = -\alpha V + \beta$ の回帰係数算出、10,000回のモンテカルロ置換検定による FPR (False Positive Rate) の算出、および既存の h17 モデル（4パラメータ）との AIC (赤池情報量基準) による比較を行った。

## 2. E:\Obsidian\KSAU_Project\cycles\cycle_21
g.md への対応
- **[問題1] への対応:** データ点数を $N=2$ から $N=9$ へ拡大。撤退基準 $k < N/3$ を満たし、自明な $R^2=1.0$ を回避した。
- **[問題2] への対応:** 10,000回のモンテカルロ置換検定を実施。FPR $\approx 0.018$ を得て、統計的有意性の検証を実データに基づき実施した。
- **[問題3] への対応:** 既存の h17 モデルとの比較を実施。2パラメータモデルの簡潔さと、多変量モデルの精度のトレードオフを評価した。

## 3. 計算結果
全 9 粒子を用いた回帰分析の結果：
- **$R^2$:** 0.5548
- **FPR (Monte Carlo):** 0.0184
- **$\alpha$ (回帰係数):** 2.4165
- **$\beta$ (切片):** -9.7273
- **AIC (H52):** 49.27

**既存モデルとの比較:**
SSoT の h17 モデル（Crossing, Det, Vol を使用）は $R^2 = 0.9915$ を達成しており、今回の $V$ 単一変数モデル ($R^2=0.55$) よりも記述精度が圧倒的に高い。AIC 評価においても、h17 モデルの方が統計的に優れた「現象の記述」を行っている可能性が高い。

## 4. SSoT コンプライアンス
- 使用した SSoT 定数のキー: `quarks`, `leptons`, `bosons`, `topology_assignments`, `analysis_parameters`
- ハードコードの混在: なし
- 合成データの使用: なし（実データのみ）

## 5. 修正・作成したファイル一覧
- E:\Obsidian\KSAU_Project\cycles\cycle_21\iterations\iter_02/code/h52_extended_analysis.py: 拡張データセットによる回帰分析スクリプト
- E:\Obsidian\KSAU_Project\cycles\cycle_21\iterations\iter_02/results.json: 計算結果
- E:\Obsidian\KSAU_Project\cycles\cycle_21\iterations\iter_02/researcher_report.md: 本ファイル

## 6. Reviewer への申し送り
$V$ 単独では全セクターの寿命を $R^2 > 0.95$ で説明することは困難であることが判明しました（$R^2=0.55$）。これは崩壊プロセスが「体積（作用の大きさ）」だけでなく、「交差数（トポロジーの複雑さ）」に強く依存しているという h17 モデルの妥当性を裏付けています。H52 の今後のイテレーションでは、単一変数に拘泥せず、幾何学的位相緩和コストの理論的根拠を Crossing Number 等の不変量と組み合わせて再構築することを検討すべきかもしれません。
