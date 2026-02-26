# AIRDP Roadmap — KSAU Project Cycle 17

**作成日:** 2026-02-26
**Orchestrator:** Gemini-2.0-flash
**seed.md:** E:\Obsidian\KSAU_Project\cycles\cycle_17\seed.md
**SSoT参照:** E:\Obsidian\KSAU_Project\ssot

## 仮説一覧

| ID | 仮説名 | 優先順位 | 最大イテレーション |
|----|--------|----------|------------------|
| H41 | Lepton Mass Inversion Correction | 高 | 5 |
| H42 | Boson Systematic Shift (Brunnian Scaling) | 高 | 5 |
| H43 | Refined TSI for Decay Widths | 中 | 5 |

## イテレーション割り当て表

**【Researcher へ】** 各イテレーション開始時に、この表の `[ ]` のうち最も若い番号の行を選び、その仮説IDとタスクを実行してください。
**【Reviewer へ】** 査読完了（CONTINUE または STOP 判定）後に、該当行の `[ ]` を `[x]` に更新してください。MODIFY 判定の場合は更新しないこと。

| Iter | 仮説ID | タスク概要 | 状態 |
|------|--------|-----------|------|
| 1    | H41    | レプトンセクター（Electron/Muon/Tau）の $V_{eff}$ 逆転を解消する Linking number/Torsion 補正項の抽出 | [x] |
| 2    | H41    | 補正済み $V_{eff}$ を用いたレプトン質量モデルの検証（$\kappa = \pi/24$ 固定） | [x] |
| 3    | H42    | ボソン成分数 ($C=3$) と SSoT 定数 5.5414 の物理的結合モデルの構築 | [x] |
| 4    | H42    | 全 12 粒子統一モデル（ボソンシフト込）の精度検証と残留誤差分析 | [x] |
| 5    | H43    | TSI 定義の精緻化（$s=0$ 粒子およびボソンセクターへの適合） | [x] |
| 6    | H43    | PDG 全データを用いた崩壊幅相関モデルの統計的検証 | [x] |
| 7    | H41    | [H41 継続用] レプトン・クォーク統一境界条件の検証 | [ ] |
| 8    | H42    | [H42 継続用] ボソン・重力子（$C=6$）へのスケーリング拡張性の検証 | [ ] |
| 9    | H43    | [H43 継続用] 安定・不安定粒子のトポロジカル閾値の特定 | [ ] |
| 10   | H41    | [H41 最終] 最終報告書作成と SSoT 統合提案 | [ ] |

---

## 仮説 H41: Lepton Mass Inversion Correction

### 帰無仮説 (H0)
レプトンセクターの質量階層は、現行の $V_{eff}$ モデル（Muon > Tau 逆転状態）において統計的に許容されるノイズの範囲内である。

### 対立仮説 (H1)
レプトンセクターは、その成分数（$C=2$）に起因する追加のトポロジカル相 $exp(i 	heta_{torsion})$ または Linking number による補正を受け、有効体積は $V_{eff}' = V_{eff} + \Delta V_{lep}$ となり、逆転が解消される。
> **根拠:** レプトンはクォーク（$C=10$）と比較して少成分のリンク構造を持ち、成分間の相互作用（Linking number）が質量エネルギー密度に直接寄与する。

### データ要件
- `ssot/constants.json` (particle_data.leptons)
- `data/linkinfo_data_complete.csv` (Linking number, Torsion indices)

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** レプトンセクター（Electron, Muon, Tau）に限定。ただし、クォークセクターに適用した場合に R² を悪化させないこと。
- **最大自由パラメータ数:** 1 (Linking number または Torsion に比例する係数)
- **導出要件:** 補正項はトポロジー的不変量（整数または半整数）に基づくこと。任意の浮動小数点フィッティングは禁止。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 物理的制約を満たさないモデルを提出した場合 → 即座に MODIFY
- 5 イテレーション到達で進展なし → REJECT
- Reviewer の連続 STOP 判定 2回 → 強制終了

### テスト手法
レプトン 3 点の $V_{eff}$ 順序が質量順序と一致することを確認後、全フェルミオン 9 点での回帰分析を実行。

### 最大イテレーション数
5

---

## 仮説 H42: Boson Systematic Shift (Brunnian Scaling)

### 帰無仮説 (H0)
ボソン質量の +5.5 ln シフトは、フェルミオンモデルからの統計的逸脱であり、物理的根拠を持たない。

### 対立仮説 (H1)
ボソンセクター（Brunnian link, $C=3$）の質量スケーリングは、SSoT 定数 $C_{boson} \approx 5.54$ に支配され、$\ln(m) = \kappa V + C_{boson}$ と記述される。
> **根拠:** Brunnian link の 3 成分連結構造は、バルク空間における位相幾何学的「凝縮」を引き起こし、それが系統的なエネルギーオフセットとして現れる。

### データ要件
- `ssot/constants.json` (particle_data.bosons, scaling_laws.boson_scaling)

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** W, Z, Higgs ボソン。
- **最大自由パラメータ数:** 0 (SSoT 定数 $C_{boson}=5.5414$ をそのまま使用すること)
- **導出要件:** 係数は幾何学的な成分数 3 との関係（例：$3 \cdot \dots$ または $C_{boson}$ そのもの）から説明されること。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- 物理的制約を満たさないモデルを提出した場合 → 即座に MODIFY
- 5 イテレーション到達で進展なし → REJECT

### テスト手法
ボソン 3 点とフェルミオン 9 点を統合した 12 粒子モデルにおいて、ボソンに $C_{boson}$ オフセットを適用した際の R² 改善度を評価。

### 最大イテレーション数
5

---

## 仮説 H43: Refined TSI for Decay Widths

### 帰無仮説 (H0)
粒子の崩壊幅 $\Gamma$ は、交差数 $n$ や非結び目化数 $u$ などの静的トポロジカル不変量とは無相関である（NEG-20260225-01 踏襲）。

### 対立仮説 (H1)
TSI ($n \cdot u / |s|$) にエントロピー項（例：$\ln(Det)$）または $s=0$ 時の正則化を導入した「Refined TSI」は、全粒子の崩壊幅と高い相関（R² > 0.8）を持つ。
> **根拠:** 崩壊は幾何学的安定性と位相的複雑性の競合プロセスであり、行列式 $Det$ は崩壊経路の「多重度」をエンコードしている。

### データ要件
- `ssot/constants.json` (particle_data の decay_width)
- `data/knotinfo_data_complete.csv`

### 物理的制約（PHYSICAL CONSTRAINTS）
- **適用範囲:** 全 12 粒子（または崩壊幅が既知の全粒子）。
- **最大自由パラメータ数:** 1 (正則化項またはエントロピー項の重み)
- **導出要件:** フィッティング残差を埋めるための多項式は禁止。あくまで TSI の物理的拡張であること。

### 統計的有意性基準
- Bonferroni補正後閾値: 0.016666
- FPR（モンテカルロ置換検定）: < 50%

### 撤退基準（削除不可）
- Bonferroni補正後 p > 0.016666 → 即座に REJECT
- FPR > 50% → 即座に REJECT
- R² < 0.7 → REJECT

### テスト手法
Refined TSI と $\ln(\Gamma)$ の線形回帰。

### 最大イテレーション数
5

---

## リソース配分

| 仮説 | イテレーション配分 | 理由 |
|------|------------------|------|
| H41 | 4 | レプトン逆転は統一モデルの最大の障壁であり、解決の優先度が極めて高い。 |
| H42 | 3 | ボソンシフトの物理的根拠付けは、H40 の棄却理由を直接解消するものである。 |
| H43 | 3 | 崩壊幅の幾何学的記述は長年の課題であり、TSI の再定義による突破を試みる。 |

## キュー（次サイクル候補）
- Neutrino 質量セクターへの $\Delta V_{lep}$ の外挿検証
- Brunnian スケーリングの $C=N$ への一般化公式

## 人間への確認事項
- H41 の「Linking number」はレプトン 3 世代において異なる値を持つことが期待されますが、既存の `linkinfo` データとの整合性について。
