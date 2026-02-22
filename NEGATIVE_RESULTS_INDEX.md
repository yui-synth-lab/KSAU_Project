# KSAU Project: Negative Results Index
## 探索済み空間の地図 — 「何がうまくいかないか」の記録

このドキュメントは、AIRDP フレームワークによって REJECT された仮説や、検証の過程で得られた否定的知見を記録します。将来の探索において無駄な労力を省き、理論の境界を明確にすることを目的とします。

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
