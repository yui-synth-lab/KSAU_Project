# KSAU Project: Negative Results Index
## 探索済み空間の地図 — 「何がうまくいかないか」の記録

このドキュメントは、AIRDP フレームワークによって REJECT された仮説や、検証の過程で得られた否定的知見を記録します。将来の探索において無駄な労力を省き、理論の境界を明確にすることを目的とします。

---

### [NEG-20260227-01] H47: Independent Regression Validation of κ via V_eff
- **仮説:** V_eff を独立変数とする単回帰推定量 κ_fit の 95% Bootstrap 信頼区間が理論値 π/24 (≈ 0.1309) を含む。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (CI_MISMATCH)
- **証拠:** Cycle 19, Iter 6. Bootstrap 95% CI = [0.9954, 1.9411] (N=10,000, seed=42). π/24 = 0.1309 は CI 下限の 1/7.6 以下。Iter 4 での単回帰: κ_fit=1.4251, R²=0.7954, p=0.00123。2 イテレーション通じて κ_fit は変化なし（1.4251→1.4263）。
- **閉鎖バージョン:** Cycle 19, Iteration 6
- **再開条件:** 現行の V_eff = V + lepton_correction 定義では κ スケールが約 11 倍過大評価される。V_eff の根本日再定義（κ = π/24 を回復するような幾何学的補正の導出）、またはκ理論値そのものの幾何学的再導出が必要。

### [NEG-20260227-02] H48: Non-linear Topological Mass Correction via Exponential Torsion Damping
- **仮説:** 指数関数的トーション減衰項 exp(-Det/n) を含む非線形モデル（ln(m) = κ V_eff + β exp(-Det/n) + C）がフェルミオン 9 点の質量残差を Bonferroni 補正後閾値未満の有意数準で削減する。
- **ステータス:** CLOSED
- **閉鎖理由:** BONFERRONI_FAILURE
- **証拠:** Cycle 19, Iter 7 (p=0.0435 > 0.016666, FPR=0.0495, R²=0.5385, β=-17.86) および Iter 9 (p=0.0435 継続, LOO-CV MAE 比=1.264). Reviewer 連続 STOP 判定 2 回（Iter 7, Iter 9）。
- **閉鎖バージョン:** Cycle 19, Iteration 9
- **再開条件:** exp(-Det/n) 以外の非線形不変量の第一原理的導出（幾何学的正当化が必要）、またはフェルミオンサンプルサイズの増加（現行 9 点では統計検出力が不足）。線形 ST 補正（NEG-20260226-04）との重複は許容されないため、数学的に独立した補正項の提案が必須。

### [NEG-20260225-01] H28: Decay Width Prediction via TSI
- **仮説:** 粒子の崩壊幅 $\Gamma$ は TSI 指数 ($n \cdot u / |s|$) と対数線形相関 ($\ln(\Gamma) = -A \cdot TSI + B$) を持つ。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION
- **証拠:** Cycle 12, Iter 09 (p=0.4310, FPR=0.4310). 公式定義の遵守下では安定粒子と不安定粒子の階層を正しく記述できないことが判明。
- **閉鎖バージョン:** Cycle 12, Iteration 09
- **再開条件:** TSI 指数の幾何学的定義の根本 radical な再定義、または $s=0$ 粒子を自然に扱う正則化手法の確立。

### [NEG-20260225-02] H29: Fermion Mass Correction via Smallest Torsion
- **仮説:** フェルミオン質量の予測残差 $\Delta \ln m$ は結び目多様体の Smallest Torsion (ST) と相関する。
- **ステータス:** CLOSED
- **閉鎖理由:** BONFERRONI_FAILURE
- **証拠:** Cycle 12, Iter 10 (p=0.0588 > 0.0167). 削減率 25% を達成したが、統計的に有意な予測モデルとは認められない。
- **閉鎖バージョン:** Cycle 12, Iteration 10
- **再開条件:** なし（現在のフェルミオン数では統計的限界）。

---

### [NEG-20260222-01] Jones 多項式評価値によるアクシオン抑制因子 ST の説明
- **仮説:** Jones 多項式の複素評価値 $|J(e^{2\pi i/5})|$ は、双曲体積や交差数とは独立にアクシオン抑制因子 $ST$ を説明する有意な説明変数である。
- **ステータス:** CLOSED（STATISTICAL_REJECTION）
- **閉鎖理由:** 重回帰分析（Crossing 3-12 の 2,970 結び目）において、Jones 変数の p 値が 0.8604 を記録し、統計的有意義性が認められなかった。
- **証拠:** `cycles/cycle_01/iterations/iter_03/results.json` — `p_values.ln_jones_p1 = 0.8604`.
- **閉鎖バージョン:** Cycle 01, Iteration 3
- **再開条件:** $q = e^{2\pi i/5}$ 以外の評価点、または Jones 多項式以外の量子不変量（Khovanov ホモロジー等）を用いた場合に再検討の余地あり。

### [NEG-20260222-02-CLOSED] TQFT Chern-Simons レベルへの代数的写像（H3） — Cycle 04 完全棄却

- **仮説:** KSAU の各粒子トポロジーから Chern-Simons レベル $k$ への非自明な代数的写像 $k(T)$ が構築され、かつ既存の CS 不変量（Witten 不変量等）と整合する。
- **ステータス:** CLOSED（Cycle 04 にて STATISTICAL_REJECTION + PHYSICAL_INCONSISTENCY）
- **棄却理由（定量）:**
  - **Witten 合同条件不満足:** `Det(K) mod k == 0` プロキシの不満足率が全 3 モデルで閾値 5% を大幅超過
    - k1（Linear-Sig）: **58.3%** 不満足（最良モデル）
    - k2（Log-Vol）: **66.7%** 不満足 + トートロジー（r=0.9942 ≥ 0.95）
    - k3（Crossing）: **91.7%** 不満足
  - **統計的有意性は確認されたが物理的整合性が欠如:** p 値は全モデル Bonferroni 補正後閾値 (0.00833) を下回るが、Witten 条件を満たすモデルは存在しない
  - **FPR は許容範囲内:** 全モデル FPR < 0.001（偶然ではないが、物理的に無意味）
- **否定的結果の価値:**
  - `Det(K) mod k == 0` は Chern-Simons レベルの有効なプロキシではないことが確認された
  - 統計的に非自明な相関（p < 10⁻⁴）が存在しても Witten 合同条件を満たさない可能性があることを実証
  - 4 イテレーションを通じてモデル改善の余地がなく、H3 の構造的限界が確認された
- **証拠:** `cycles/cycle_04/iterations/iter_05/results.json`（seed=42, n_trials=10000, permute V 方式）
- **閉鎖バージョン:** Cycle 04, Iteration 5（全 5 Iter 完走）
- **再開条件:** SU(2) WRT 不変量の直接数値計算（`Det(K) mod k == 0` プロキシの代替）を用いた場合に再検討の余地あり。ただし Witten プロキシの根本的再設計が必要。

---

**[参考] Cycle 03 Iter 1 結果（REOPENED 根拠）:**
- r(V, ln_Det) = 0.8440（非トートロジー確認）
- R²_resid = 0.2083（独立幾何学的情報が約 20.8% 存在）
- r(V, Signature) = -0.007（Signature は追加不変量候補）
- 証拠: `cycles/cycle_03/iterations/iter_01/results.json`

---

### [NEG-20260223-01] アキシオン質量とトポロジカル・トーション(ST)の相関 (H4)
- **仮説:** アキシオン質量 $m_a$ は双曲体積 $V$ およびトーションの行列式 $ST$ (Smallest Torsion) によって記述され、$\ln(m_a) = \kappa V - \beta \ln(ST) + C$ の形式で高い相関を示す。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (Bonferroni_FAILURE)
- **証拠:** `cycles/cycle_02/iterations/iter_04/results.json` — 最良 p = 0.0588 (Bonferroni 補正後 0.025 未達)、$R^2$ = 0.3921 (成功基準 0.75 未達)。
- **閉鎖バージョン:** Cycle 02, Iteration 4
- **再開条件:** 線形補正モデル以外の非線形・非摂動的結合モデル、またはより高次のトポロジカル不変量の導入が提案された場合。

---

### [NEG-20260223-02] TQFT Chern-Simons レベルへの線形写像モデルの限界
- **仮説:** 幾何学的不変量 ($V, Det, Sig$) の線形結合により、物理的整合性（Witten 合同条件）を満たす Chern-Simons レベル $k$ への写像を構築できる。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION + PHYSICAL_INCONSISTENCY. 全結び目データセットにおいて Witten 条件充足率が 1.35% に留まり、特に Bulk セクター（大体積領域）では 0.00% を記録した。
- **証拠:** `cycles/cycle_04/iterations/iter_08/results.json` — `global_metrics.witten_consistency_rate = 0.0134`.
- **閉鎖バージョン:** Cycle 04, Iteration 8
- **再開条件:** 線形結合モデルを廃止し、Jones 多項式の整数論的性質や、WRT 不変量の非摂動的項を直接考慮した非線形写像モデルが提案された場合。

---

### [NEG-20260223-04] WRTベース TQFT 写像の精度限界 (H13)
- **仮説:** 非線形パリティシフト写像モデルにより、Witten 整合性レート 80% 以上の CS レベル $k$ を構築できる。
- **ステータス:** CLOSED
- **閉鎖理由:** RESOURCE_EXHAUSTION (進展不足による最大イテレーション到達)
- **証拠:** `cycles/cycle_06/iterations/iter_05/results.json` — `consistency_rate_obs = 0.75` (目標 0.80 未達)。
- **閉鎖バージョン:** Cycle 06, Iteration 5
- **再開条件:** Nelder-Mead 最適化以外の、Jones 多項式の根の位相構造を直接反映した離散的量子化アルゴリズムの導入。

---

### [NEG-20260223-05] H21: H17 寿命モデルによる暗黒物質候補トポロジーの予測
- **仮説:** H17 寿命相関モデルの外挿により、宇宙年齢を超える安定性を持つ特定の未割り当てトポロジーを統計的に有意に特定できる。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION
- **証拠:** `cycles/cycle_09/iterations/iter_08/results.json` — 不確実性（+2 Sigma）を考慮した候補 8,836 個の FPR は 72.66% であり、成功基準 (FPR < 0.01) を満たさず、ノイズ支配的であると判定。
- **閉鎖バージョン:** Cycle 09, Iteration 08
- **再開条件:** フェルミオン質量以外の物理的制約（例：アクシオン抑制因子、ゲージ対称性）を導入し、候補を 1/100 以下に絞り込める理論的根拠が得られた場合。

---

### [NEG-20260225-01] H22: 単純理論勾配モデル (κ = π/24) の統計的限界
- **仮説:** 物理定数 κ を理論導出値 π/24 に固定した単純線形質量モデルのみで、全フェルミオン質量の有意な説明が可能である。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (Bonferroni_FAILURE). p = 0.0354 であり、補正後閾値 0.0167 に達せず。
- **証拠:** `cycles/cycle_10/iterations/iter_07/results.json` — `p_value = 0.0354`.
- **閉鎖バージョン:** Cycle 10, Iteration 7
- **再開条件:** 位相離散化 (K=24) などの追加不変量との統合モデルにおいて、自由度を最小化した状態での再検証。

---

### [NEG-20260225-03] TSI 寿命・安定性相関の普遍性検証 (H26)
- **仮説:** 粒子の崩壊率 Γ = 1/τ は、幾何学的安定性指数 TSI によって規定され、ln(Γ) = -A * TSI + B の指数的抑制関係に従う。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION, SSoT_VIOLATION
- **証拠:** `cycles/cycle_11/iterations/iter_03/results.json` — Bonferroni 補正後 p = 0.1734 (> 0.016666)。また、寿命データのハードコードおよび TSI 定義の恣意的変更（n*u / (|s|+1)）が認められた。
- **閉鎖バージョン:** Cycle 11, Iteration 3
- **再開条件:** SSoT への信頼できる寿命データの登録、および TSI 定義を変更しない状態での有意性確認。

---

### [NEG-20260225-04] H32: Validation of topological torsion correction in mass action
- **仮説:** フェルミオン質量の有効作用は双曲体積 $V$ に加えて、トーション項 $A \ln(ST)$ を含み、$\ln(m) = \kappa V + A \ln(ST) + B$ と記述される。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (BONFERRONI_FAILURE)
- **証拠:** Cycle 13, Iter 08 (p=0.0712 > 0.0167). 残差分散の削減率は 39.2% に達したが、統計的有意義性が認められなかった。
- **閉鎖バージョン:** Cycle 13, Iteration 08
- **再開条件:** 線形結合以外の相互作用項、またはより高次の不変量を用いた非線形モデルの提案。

### [NEG-20260225-05] H33: Independent regression validation of mass gradient constant κ
- **仮説:** フェルミオン質量の対数と双曲体積の間の回帰係数 $\kappa_{fit}$ は、生データからの純粋な統計的推定によって理論値 $\pi/24 \approx 0.1309$ を再現する。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (CI_MISMATCH)
- **証拠:** Cycle 13, Iter 05. 統一モデルにおける Bootstrap 95% 信頼区間は [0.0323, 0.1050] であり、理論値 0.1309 を含まなかった。
- **閉鎖バージョン:** Cycle 13, Iteration 05
- **再開条件:** 第2次幾何補正項（n, ln_det 等）を導入し、有効体積 $V_{eff}$ を定義した上での再回帰。

### [NEG-20260225-06] H34: Linear ST Fermion Mass Correction
- **仮説:** ln(m) = κV + α ln(ST) + β により質量残差を有意に低減できる。
- **ステータス:** CLOSED
- **閉鎖理由:** BONFERRONI_FAILURE
- **証拠:** Cycle 14 Iteration 1 において、全フェルミオン 9 点に対する線形回帰の p 値は 0.0712 であり、多重比較補正後の閾値 0.0167 を達成できなかった。
- **閉鎖バージョン:** Cycle 14, Iteration 1
- **再開条件:** Torsion 寄与 α の幾何学的導出により、自由パラメータを排除した厳密モデルが提示された場合。

---

### [NEG-20260226-01] H37: Topological Correlates of Decay Width
- **仮説:** 粒子の崩壊幅 $\Gamma$ はトポロジカル不変量（交差数 $n$、非結び目化数 $u$、署名 $s$）の線形結合で記述される。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION
- **証拠:** Cycle 15, Iter 03 (p=0.1610, FPR=0.1012, R²=0.6132). 
- **閉鎖バージョン:** Cycle 15, Iteration 03
- **再開条件:** 線形結合モデル以外の非摂動的な位相幾何学的障壁モデル、またはエントロピー的不変量の導入。

### [NEG-20260226-03] H40: Holistic Mass Law Validation via V_eff (Fixed κ = π/24)
- **仮説:** κ = π/24 固定モデルにより、全 12 粒子の質量を R² > 0.999 で統一的に説明できる。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION (REJECT)
- **証拠:** Cycle 16, Iter 05/06. 統計的有意性は p=0.0970 であり、目標値 0.01 に達せず棄却。FPR=0.0950, R²=0.2511, LOO-MAE=3.9255。
- **閉鎖バージョン:** Cycle 16, Iteration 06
- **再開条件:** レプトンセクターにおける $V_{eff}$ の逆転現象（Muon-Tau）を解消する幾何学的補正項の導入、またはボソンセクターの系統的シフト（約 +5.5 ln）を説明する物理モデルの提示。

### [NEG-20260227-01] 寿命-双曲体積相関仮説 (H52)
- **仮説:** 粒子の寿命 $\tau$ の対数値 $\ln(\tau)$ は、そのトポロジーの双曲体積 $V$ と統計的に負の相関を持つ（$\ln(\tau) = -\alpha V + \beta$）。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION, BONFERRONI_FAILURE
- **証拠:** Cycle 21 Iteration 2 において、Bonferroni 補正後 p=0.0213 (> 0.0167)、FPR=1.84% (> 1.0%)。既存の 4 パラメータモデル (h17) を凌駕する説明力を示せなかった。
- **閉鎖バージョン:** Cycle 21, Iteration 2
- **再開条件:** なし。V 単一変数による寿命記述の限界が統計的に示されたため。

### [NEG-20260227-02] H58: ジョイントMC検定による3予測値の統計的確立
- **仮説:** KSAU 24-cell フレームワークの3予測（アクシオン m_a=12.16μeV、重力偏差ΔG/G=8.43×10⁻⁶、Top崩壊幅Γ=1321MeV）の同時達成精度は、ランダム KnotInfo トポロジーからの同時置換と比較してBonferroni補正後有意水準（p<0.016667）で統計的に優位である。
- **ステータス:** CLOSED
- **閉鎖理由:** BONFERRONI_FAILURE
- **証拠:** Cycle 23, Iter 3（有効実装）: mc_joint_p_value=0.067（FPR=6.7%）、mc_better_count=670/10000、Bonferroni閾値0.016667の4.0倍。Iter 2での合成データ使用（np.random.uniform）はMODIFYにより修正済みであり、最終結果はIter 3の有効実装に基づく。
- **閉鎖バージョン:** Cycle 23, Iteration 3
- **再開条件:** KSAU予測値に対する独立実験データの精度向上（各予測の|z|>2相当に誤差帯が縮小する場合）、またはランダムKnotInfoトポロジーと比較してKSAU割り当てトポロジーが幾何学的に一意である理論的根拠（選択基準の第一原理的正当化）が提示された場合。

### [NEG-20260227-03] H59: LOO-CV検証とα理論導出によるST補正質量モデルの確立
- **仮説:** α = √2 × κ（KSAU幾何学定数から理論導出）として固定したST補正質量モデル ln(m) = κV + α·ln(ST) + γ + β において、LOO-R² ≥ training R² × 0.95 かつ Bonferroni補正後 p（β≠0）< 0.016667 を全フェルミオン9点で同時達成できる。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION
- **証拠:** Cycle 23, Iter 6: training_R²=0.2948, LOO-R²=0.1075（要求0.2801の38%）。LOO-R²のトレーニングR²からの低下率=63%。β p値=1.26×10⁻⁵（有意）、LOO-MAE比=1.125（合格）。FPR未計算。α = √2 × κ = 0.18512（相対誤差6.6×10⁻⁷）の導出は成功したが、H1複合達成条件を満たさず。
- **閉鎖バージョン:** Cycle 23, Iteration 7（最終レポート完了）
- **再開条件:** (a) α·ln(ST)補正項がLOO-安定（LOO-R² ≥ 0.95×training R²）となる追加のトポロジカル不変量との組み合わせモデルが第一原理から提示された場合。または (b) 全9フェルミオンにわたってトーション補正項のLOO安定性を保証する物理的機構（例: STの幾何学的普遍性の証明）が示された場合。なお、α または γ の独立パラメータ化による改善は禁止（自由パラメータ数制約違反）。

### [NEG-20260227-04] H60: Det ≡ 0 (mod 24) 条件と位相安定性（TSI≥24）の正相関検証
- **仮説:** KnotInfo全データ（N=6502、交差数3–12）において、24-cell対称性から予測される {det(K)≡0 mod 24} と {TSI(K)≥24} の間の有意な正の相関が存在する（Fisher正確確率検定 Bonferroni補正後 p<0.016667、オッズ比>1）。
- **ステータス:** CLOSED
- **閉鎖理由:** STATISTICAL_REJECTION
- **証拠:** Cycle 23, Iter 10: Fisher p=0.00556, OR=0.7452（< 1）, 95%CI=[0.605, 0.919], FPR=0.9985（99.85%）。Iter 11: Bonferroni補正後p=0.016686（>0.016667）, φ=-0.034。分割表: {det≡0∩TSI≥24}=115件、{det≡0∩TSI<24}=625件、{det≠0∩TSI≥24}=1141件、{det≠0∩TSI<24}=4621件。24-cell対称性の予測（正の相関）に反し、有意な負の相関が検出された（OR=0.745）。
- **閉鎖バージョン:** Cycle 23, Iteration 10
- **再開条件:** H60の観測（OR=0.745：det≡0(mod 24)の結び目はTSIが低い傾向）の幾何学的機構が24-cell理論から説明され、かつその説明から新たなtestableな予測（正の相関を生む物理条件の特定等）が導かれる場合。または、TSI公式（n*u/|s|）に代わる24-cell対称性に直接対応する安定性指数が第一原理から提案された場合。

