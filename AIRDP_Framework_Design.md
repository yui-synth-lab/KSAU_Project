# AIRDP: AI-Driven Research & Discovery Pipeline
## フレームワーク設計書 v1.0

**作成日:** 2026-02-21
**ベースライン:** KSAU Project (v1.0–v38.0) の38バージョンにわたる試行錯誤から抽出
**目的:** AI駆動型研究プロジェクトにおける「発散の制御」と「撤退判断の自動化」を実現する再利用可能なフレームワーク

---

> **"The best framework is one that knows when to stop."**
> — KSAU v38.0 休眠プロトコルより

---

## 目次

1. [エグゼクティブサマリー](#1-エグゼクティブサマリー)
2. [KSAUからの教訓：何がうまくいき、何が失敗したか](#2-ksauからの教訓何がうまくいき何が失敗したか)
3. [アーキテクチャ概要](#3-アーキテクチャ概要)
4. [5つのフェーズ：パイプライン詳細設計](#4-5つのフェーズパイプライン詳細設計)
5. [ロール定義：4つのAIエージェント](#5-ロール定義4つのaiエージェント)
6. [介入制御プロトコル：人間の役割と制約](#6-介入制御プロトコル人間の役割と制約)
7. [SSoT（Single Source of Truth）設計](#7-ssotsingle-source-of-truth設計)
8. [否定的結果の管理](#8-否定的結果の管理)
9. [発散防止メカニズム](#9-発散防止メカニズム)
10. [ディレクトリ構造テンプレート](#10-ディレクトリ構造テンプレート)
11. [実装ガイド：最初のプロジェクトの始め方](#11-実装ガイド最初のプロジェクトの始め方)
12. [付録：KSAUタイムライン分析](#付録ksauタイムライン分析)

---

## 1. エグゼクティブサマリー

AIRDP（AI-Driven Research & Discovery Pipeline）は、人間がアイデアを提供し、AIが自律的に検証・反証を行う研究パイプラインのフレームワークである。

KSAU Projectにおける38バージョンの開発経験から、以下の3つの構造的問題を特定し、それらを解決する設計を提供する。

| 問題 | KSAUでの発現 | AIRDPでの解決策 |
|------|-------------|----------------|
| **発散** | v9–v25で仮説が無制限に拡大 | 仮説同時並行数の上限（Max 3） |
| **人間の介入バイアス** | イテレーション中に新アイデアが注入され撤退判断が遅延 | フェーズゲート制御（介入可能点の厳密な制限） |
| **撤退の遅れ** | Bonferroni補正で棄却される仮説に18バージョンを費やした | 自動撤退判定（統計的閾値による機械的判断） |

---

## 2. KSAUからの教訓：何がうまくいき、何が失敗したか

### 2.1 成功パターン（継承すべきもの）

**SSoTの徹底:** 全バージョンが `v6.0/data/physical_constants.json` を唯一の定数ソースとして参照した。これにより、38バージョンを通じて数値の一貫性が保たれた。一度だけ `calculate_baseline.py` でハードコードが発見されたが（v26.0監査）、即座に修正された。

**否定的結果の構造化:** `NEGATIVE_RESULTS_INDEX.md` に全ての棄却済み仮説が記録された。WZW導出の数学的不可能性、$\alpha_{em} = \pi/432$ のモンテカルロFPR 87%による棄却、$Co_0 \to G_2$ の群論的否定など、閉鎖された全経路が将来の研究者のためにアクセス可能な形で保存された。

**AI間通信の透明性:** `audit/history/communication/` に全てのAI間やり取りが記録され、第三者が意思決定プロセスを追跡可能だった。

**go.md / ng.md による明示的承認:** 各バージョンの成果物は、独立した監査AIによる明示的な承認（go.md）または差し戻し（ng.md）を経なければ次のバージョンに進めなかった。

### 2.2 失敗パターン（修正すべきもの）

**風呂敷の拡大（v9–v15）:** $R^2 > 0.99$ の質量フィットに触発され、Lorentz不変性、Dirac方程式、Einstein方程式、時間の起源を同時に導出しようとした。これらは各々が独立した研究プログラムに値するテーマであり、1プロジェクト内で並行して追求すべきではなかった。

**人間の介入タイミング（v7–v25）:** 自動レビューが「統計的に弱い」「検証不可能」と判定した仮説に対して、人間が「面白いから試してみよう」と上書きするパターンが繰り返された。これがイテレーションの発散を引き起こし、最終的にv26–v38で強制的な収束（撤退の連鎖）を必要とした。

**撤退判断の遅延:** 粒子質量セクター（Section 2, 3）はBonferroni補正後にいずれも有意水準を満たさなかったが、この結論に到達するまでに約18バージョン（v9–v26）を要した。自動化された撤退判定基準が事前に定義されていれば、v12前後で撤退し、$S_8$ セクターにリソースを集中できた可能性がある。

**Output Logの陳腐化（v26.0監査で発覚）:** コードがV1→V3に改訂された際、JSONの結果ファイルのみが更新され、Output Logが初回実行（V1）の結果のまま放置された。go.mdもRoadmapも改訂経緯を記録していなかった。

---

## 3. アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────┐
│                    HUMAN（人間）                          │
│  役割: アイデア提供 / 最終意思決定 / 緊急停止            │
│  制約: イテレーション中は介入不可（Phase 3）              │
└────────────┬──────────────────────────────┬──────────────┘
             │ Phase 1: Seed               │ Phase 5: Receive
             ▼                              ▲
┌─────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR（指揮者AI）                │
│  役割: ロードマップ生成 / フェーズ遷移管理 / 発散制御    │
│  権限: 仮説の事前スクリーニング / イテレーション上限管理  │
└────────┬──────────────┬──────────────┬──────────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐
│  RESEARCHER  │ │   REVIEWER   │ │   JUDGE（判定AI）     │
│（研究者AI）   │ │（査読者AI）   │ │  役割: Accept/Reject │
│  役割:       │ │  役割:       │ │  /Modify の最終判定  │
│  実装・計算  │→│  統計検証    │→│  撤退判断の執行      │
│  文献調査    │←│  反証試行    │ │                      │
│  仮説の具体化│ │  SSoT照合    │ │                      │
└──────────────┘ └──────────────┘ └──────────────────────┘
         ↑              ↑
         └──── Loop ─────┘
        (Phase 3: 自動イテレーション)
```

---

## 4. 5つのフェーズ：パイプライン詳細設計

### Phase 1: Seed（種まき）— 人間 → Orchestrator

**実行者:** 人間
**成果物:** `seed.md`（自然言語によるアイデア記述）
**所要時間:** 制限なし（人間のペースに委ねる）

人間がアイデアを自然言語で記述する。形式は自由だが、以下の3要素を含むことが推奨される。

- **What:** 何を調べたいか（仮説・直感・疑問）
- **Why:** なぜそれが面白いと思うか（動機）
- **Boundary:** 何が出たら「失敗」と認めるか（事前の撤退条件）

Boundaryが記述されていない場合、Orchestratorが Phase 2 で補完する。

**KSAUでの教訓:** KSAUでは人間のアイデアが「Lorentz不変性の導出」「Dirac方程式の導出」「Einstein方程式の導出」と同時に投入された。AIRDPでは、1つの `seed.md` に含められる仮説は最大3つとする。それ以上のアイデアは次のサイクルのキューに入れる。

### Phase 2: Plan（設計）— Orchestrator

**実行者:** Orchestrator AI
**入力:** `seed.md`
**成果物:** `roadmap.md` + `ssot/` 初期化 + `hypotheses/` 初期化
**所要時間:** 1ターン（人間の承認を得て次へ進む）

Orchestratorは `seed.md` を以下の構造に変換する。

1. **仮説の分解:** 抽象的なアイデアを、検証可能な仮説（Testable Hypothesis）に分解する。各仮説には以下を定義する。
   - 帰無仮説（$H_0$）と対立仮説（$H_1$）
   - 成功基準（p値の閾値、誤差の許容範囲など）
   - 撤退基準（Bonferroni補正後の有意水準、FPR閾値など）
   - 最大イテレーション回数（デフォルト: 5）

2. **事前スクリーニング:** 各仮説に対して以下をチェックする。
   - 検証可能性: 定量的に検証可能か？（「面白い」だけでは不可）
   - 独立性: 既存の否定的結果と重複しないか？（`NEGATIVE_RESULTS_INDEX.md` 参照）
   - スコープ: 現在のプロジェクトの範囲内か？

3. **リソース配分:** 仮説間の優先順位とイテレーション回数の配分を決定する。

**人間の介入ポイント:** `roadmap.md` は人間の明示的承認を得て初めて Phase 3 に進む。これが**人間がアイデアを追加できる最後のポイント**である。

### Phase 3: Execute（実行）— Researcher ↔ Reviewer ループ

**実行者:** Researcher AI + Reviewer AI（自動交互起動）
**入力:** `roadmap.md`
**成果物:** 各イテレーションごとの `iteration_N/` ディレクトリ
**所要時間:** 自動（最大イテレーション回数に到達するか、撤退基準に該当するまで）

これがパイプラインの中核であり、**人間は介入できない**。

```
┌─── Iteration Loop ────────────────────────────────┐
│                                                     │
│  Researcher:                                        │
│    1. 仮説に基づくコード実装・計算実行              │
│    2. 結果をSSoTと照合                              │
│    3. `iteration_N/results.json` に結果を保存       │
│    4. `iteration_N/researcher_report.md` を作成     │
│                                                     │
│  Reviewer:                                          │
│    1. Researcherの結果を独立検証                     │
│    2. 統計的妥当性の検査（多重比較補正を含む）      │
│    3. 反証の試行（Monte Carlo null test等）          │
│    4. SSoTとの整合性確認                            │
│    5. 判定: CONTINUE / STOP / MODIFY                │
│    6. `iteration_N/review.md` を作成                │
│                                                     │
│  自動撤退チェック:                                  │
│    - Bonferroni補正後 p > 閾値 → STOP              │
│    - FPR > 50% → STOP                              │
│    - イテレーション上限到達 → STOP                  │
│    - Reviewer が2回連続 STOP 判定 → 強制終了        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**KSAUでの教訓:** KSAUではこのループ中に人間が「でもこのアイデアも試してみよう」と介入し、ゴールポストが移動した。AIRDPでは Phase 3 中の人間の役割は**緊急停止ボタンのみ**とする。新しいアイデアは次のサイクルの `seed.md` としてキューに入れる。

### Phase 4: Judge（判定）— Judge AI

**実行者:** Judge AI（Orchestrator, Researcher, Reviewerのいずれとも独立）
**入力:** 全イテレーションの `results.json` + `review.md`
**成果物:** `verdict.md`（Accept / Reject / Modify）
**所要時間:** 1ターン

Judge AIは以下の判定を行う。

- **ACCEPT:** 仮説が成功基準を満たした。結果をSSoTに統合し、次の仮説またはサイクルに進む。
- **REJECT:** 仮説が撤退基準に該当した。`NEGATIVE_RESULTS_INDEX.md` に記録し、閉鎖する。
- **MODIFY:** 仮説は棄却されなかったが、成功基準も満たしていない。修正案を提示し、Phase 2 に差し戻す（ただし、同一仮説のModifyは最大2回まで）。

**KSAUでの教訓:** KSAUでは go.md/ng.md の判定が作成者AI（Gemini）と査読者AI（Claude）の間で行われたが、両者が直接的な利害関係者であったため、判定の独立性に限界があった。AIRDPではJudgeを第3のエージェントとして独立させる。

### Phase 5: Report（報告）— Orchestrator → 人間

**実行者:** Orchestrator AI
**成果物:** `cycle_report.md`（サイクル全体の要約）
**受領者:** 人間

Orchestratorが以下を含むサイクル報告書を人間に提出する。

- 各仮説の最終判定（Accept / Reject / Modify）
- 新たに閉鎖された経路（否定的結果）
- SSoTへの変更履歴
- 次のサイクルへの推奨事項
- 未処理のアイデアキュー（Phase 3 中に人間が追加したもの）

**人間の介入ポイント:** ここで人間は次のサイクルの `seed.md` を作成できる。

---

## 5. ロール定義：4つのAIエージェント

### 5.1 Orchestrator（指揮者）

**責務:**
- `seed.md` → `roadmap.md` への変換
- 仮説の事前スクリーニング（検証可能性・独立性・スコープ）
- フェーズ遷移の管理
- 発散の検知と警告
- サイクル報告書の作成

**禁止事項:**
- 仮説の実装や計算の実行（Researcherの領域）
- 統計的判定の実行（Reviewer/Judgeの領域）
- 人間の承認なしにロードマップを変更すること

**推奨モデル特性:** 広い知識ベース、構造化能力、メタ認知能力

### 5.2 Researcher（研究者）

**責務:**
- 仮説に基づくコード実装・計算実行
- 文献調査（web検索、arXiv等）
- 結果の記録（`results.json` + `researcher_report.md`）
- SSoTからの定数読み込み（ハードコード禁止）

**禁止事項:**
- 自身の結果に対する統計的判定（Reviewerの領域）
- ロードマップの変更提案（Orchestratorの領域）
- 撤退基準の変更

**推奨モデル特性:** コード生成能力、計算精度、実装力

### 5.3 Reviewer（査読者）

**責務:**
- Researcherの結果の独立検証（コードの再実行を含む）
- 統計的妥当性の検査（多重比較補正、FPRテスト等）
- 反証の試行（帰無仮説のシミュレーション等）
- SSoTとの整合性確認
- 各イテレーションの CONTINUE / STOP / MODIFY 判定

**禁止事項:**
- 新しい仮説の提案（Orchestratorの領域）
- コードの修正（Researcherへの差し戻しのみ）
- 最終判定（Judgeの領域）

**推奨モデル特性:** 批判的思考能力、統計的厳密性、バイアス検出能力

### 5.4 Judge（判定者）

**責務:**
- 全イテレーションを俯瞰した最終判定（Accept / Reject / Modify）
- `NEGATIVE_RESULTS_INDEX.md` への記録
- 判定の根拠の明文化

**禁止事項:**
- 新しい仮説や修正案の詳細設計（Orchestratorの領域）
- コードの実装や実行
- 撤退基準の事後的な緩和

**推奨モデル特性:** 中立性、俯瞰的判断力、科学的誠実性

### 5.5 実装上の注意

4つのロールは必ずしも4つの異なるモデルインスタンスを必要としない。同一モデルでも、システムプロンプトを切り替えることでロールの分離は実現可能である。重要なのは**ロール間の情報遮断**であり、特にJudgeはResearcherの「意図」や「期待」にアクセスすべきでない。Judgeには結果と統計データのみを渡す。

---

## 6. 介入制御プロトコル：人間の役割と制約

### 6.1 介入マトリクス

| フェーズ | 人間が「できる」こと | 人間が「できない」こと |
|----------|---------------------|----------------------|
| Phase 1 (Seed) | アイデアの自由記述 | 仮説数の上限を超えること（Max 3） |
| Phase 2 (Plan) | ロードマップの承認・修正要求 | 撤退基準の削除 |
| Phase 3 (Execute) | **緊急停止のみ** | 新アイデアの注入、撤退基準の変更、ゴールポストの移動 |
| Phase 4 (Judge) | なし（完全自動） | 判定結果の上書き |
| Phase 5 (Report) | 次のseed.mdの作成、アイデアキューの整理 | 過去の判定の遡及的変更 |

### 6.2 緊急停止プロトコル

人間が Phase 3 で行使できる唯一の権限。以下の条件でのみ発動する。

- AIが明らかに誤ったデータや前提に基づいて計算を続けている場合
- 外部環境の変化（新しい実験結果の発表等）により、仮説自体が無意味になった場合
- 計算リソースが想定を大幅に超過している場合

緊急停止が発動された場合、現在のイテレーションは中断され、Phase 4（Judge）に直接移行する。緊急停止の理由は `emergency_stop.md` に記録される。

### 6.3 アイデアキュー

Phase 3 の実行中に人間が思いついた新しいアイデアは、`idea_queue.md` に追記できる。ただし、これらは現在のサイクルには影響を与えず、Phase 5 の報告書に「未処理キュー」として含められる。次のサイクルの `seed.md` の候補となる。

**KSAUでの教訓:** この仕組みがあれば、v9–v25で起きた「途中でゴールポストが動く」問題を防げていた。

---

## 7. SSoT（Single Source of Truth）設計

### 7.1 原則

全てのパイプライン参加者（AI・人間）は、定数・データ・パラメータを唯一のソースから読み込む。ハードコードは一切許可しない。

### 7.2 ディレクトリ構造

```
ssot/
├── constants.json          # 物理定数・数学定数
├── parameters.json         # プロジェクト固有のパラメータ
├── data/                   # 実験データ・観測データ
│   ├── raw/                # 生データ（変更不可）
│   └── processed/          # 前処理済みデータ（変更履歴付き）
├── hypotheses/             # 現在アクティブな仮説の定義
│   ├── H1.json             # 仮説1: 定義・成功基準・撤退基準
│   ├── H2.json             # 仮説2
│   └── ...
└── changelog.json          # SSoTへの全変更履歴
```

### 7.3 SSoTルール

1. **読み込みルール:** 全てのスクリプトは `ssot/constants.json` からのみ定数を取得する。`3.14159` や `0.55` のようなマジックナンバーは禁止。
2. **書き込みルール:** SSoTへの変更は、Judge の ACCEPT 判定後にのみ Orchestrator が実行する。Researcher/Reviewer は SSoT を変更できない。
3. **監査ルール:** Reviewer は各イテレーションで SSoT 整合性チェックを実施する（KSAUの v26.0 監査で発見された `calculate_baseline.py` のハードコード問題を防止）。
4. **バージョニング:** `changelog.json` に全変更を記録する。変更理由と承認者（Judge）を明記する。

---

## 8. 否定的結果の管理

### 8.1 NEGATIVE_RESULTS_INDEX.md

全ての棄却済み仮説を以下のフォーマットで記録する。

```markdown
### [ID] 仮説の短縮名
- **仮説:** [1文での仮説記述]
- **ステータス:** CLOSED（[閉鎖理由の分類]）
- **閉鎖理由:** [具体的な理由。数学的不可能性/統計的棄却/同語反復 等]
- **証拠:** [棄却の根拠となるデータ・計算結果へのリンク]
- **閉鎖バージョン:** [判定が行われたサイクル/イテレーション]
- **再開条件:** [どのような新情報があれば再検討に値するか。「なし」も可]
```

### 8.2 閉鎖理由の分類

| 分類 | 定義 | KSAUでの例 |
|------|------|-----------|
| **MATHEMATICAL_IMPOSSIBILITY** | 数学的に不可能であることが証明された | WZW導出（離散系列の判別式が負） |
| **STATISTICAL_REJECTION** | 統計的検定により棄却された | $\alpha_{em} = \pi/432$（FPR 87%） |
| **TAUTOLOGY** | 仮説が同語反復であり、予測ではなかった | $D_{compact} = 7$（M理論の入力） |
| **GROUP_THEORY_MISMATCH** | 群論的に不可能 | $Co_0 \to G_2$ 写像 |
| **BONFERRONI_FAILURE** | 多重比較補正後に有意水準未達 | Section 2/3 のCS双対性 |
| **RESOURCE_EXHAUSTION** | 最大イテレーション回数に到達し、進展なし | — |

### 8.3 否定的結果の価値

否定的結果は、探索空間を縮小する科学的成果である。`NEGATIVE_RESULTS_INDEX.md` は「失敗のリスト」ではなく「探索済み空間の地図」として扱う。

KSAUの v7.0 報告書が述べた通り：

> *"By honestly reporting what does not work, we prevent future wasted effort on unpromising directions, strengthen confidence in positive results, and narrow the search space for first-principles derivations."*

---

## 9. 発散防止メカニズム

### 9.1 ハードリミット

| パラメータ | デフォルト値 | 説明 |
|-----------|------------|------|
| `MAX_HYPOTHESES_PER_SEED` | 3 | 1サイクルで同時に追求できる仮説の最大数 |
| `MAX_ITERATIONS_PER_HYPOTHESIS` | 5 | 1仮説あたりの最大イテレーション回数 |
| `MAX_MODIFY_COUNT` | 2 | 同一仮説のModify判定の最大回数（超過でREJECT） |
| `BONFERRONI_THRESHOLD` | 0.05 / n | 多重比較補正の閾値（nは仮説数） |
| `FPR_REJECTION_THRESHOLD` | 0.50 | モンテカルロFPRがこの値を超えたら即棄却 |
| `CONSECUTIVE_STOP_LIMIT` | 2 | Reviewerの連続STOP判定でループ強制終了 |

### 9.2 スコープクリープ検知

Orchestrator は各イテレーション後に以下をチェックする。

- **仮説の数:** ロードマップで定義された仮説数を超えていないか
- **仮説の範囲:** Researcher が元の仮説の範囲を超えた計算を行っていないか
- **新概念の導入:** Researcher が `roadmap.md` に記載されていない新しい理論的概念を導入していないか

いずれかに該当する場合、Orchestrator は WARNING を発行し、Reviewer に精査を要請する。

### 9.3 KSAUタイムライン上のトリガーポイント

もしAIRDPがKSAUに適用されていたら、以下のポイントで発散を阻止できていた。

| バージョン | 発散イベント | AIRDPでの対応 |
|-----------|-------------|--------------|
| v9.0 | Lorentz/Dirac/Einstein を同時追求 | `MAX_HYPOTHESES_PER_SEED = 3` により、いずれか1つに絞るよう要求 |
| v15.0 | 「時間の起源」を追加 | スコープクリープ検知により WARNING |
| v19.0 | 静的モデルがREJECTED後も拡張を継続 | `CONSECUTIVE_STOP_LIMIT = 2` により Phase 4 に強制移行 |
| v26.0 | Output Logの陳腐化 | SSoT監査ルール（Reviewer の整合性チェック）で即座に検出 |

---

## 10. ディレクトリ構造テンプレート

```
project_root/
├── README.md                        # プロジェクト概要（常に最新）
├── NEGATIVE_RESULTS_INDEX.md        # 否定的結果のマスターリスト
├── idea_queue.md                    # 人間の未処理アイデアキュー
│
├── ssot/                            # Single Source of Truth
│   ├── constants.json
│   ├── parameters.json
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   ├── hypotheses/
│   │   ├── H1.json
│   │   └── ...
│   └── changelog.json
│
├── cycles/                          # サイクル単位の作業ディレクトリ
│   ├── cycle_01/
│   │   ├── seed.md                  # 人間のアイデア
│   │   ├── roadmap.md               # Orchestratorのロードマップ
│   │   ├── iterations/
│   │   │   ├── iter_01/
│   │   │   │   ├── code/            # Researcherのコード
│   │   │   │   ├── results.json     # 計算結果
│   │   │   │   ├── researcher_report.md
│   │   │   │   └── review.md        # Reviewerの査読
│   │   │   ├── iter_02/
│   │   │   └── ...
│   │   ├── verdict.md               # Judgeの最終判定
│   │   └── cycle_report.md          # Orchestratorのサイクル報告
│   │
│   ├── cycle_02/
│   └── ...
│
├── audit/                           # 監査ログ
│   ├── communication/               # AI間通信の全記録
│   ├── ssot_checks/                 # SSoT整合性チェックの記録
│   └── emergency_stops/             # 緊急停止の記録
│
└── archive/                         # 完了・閉鎖されたサイクルのアーカイブ
```

---

## 11. 実装ガイド：最初のプロジェクトの始め方

### Step 1: リポジトリの初期化

```bash
mkdir my_research_project
cd my_research_project
git init

# テンプレートのディレクトリ構造を作成
mkdir -p ssot/data/{raw,processed} ssot/hypotheses
mkdir -p cycles/cycle_01/iterations
mkdir -p audit/{communication,ssot_checks,emergency_stops}
mkdir -p archive

# 初期ファイルを作成
touch README.md NEGATIVE_RESULTS_INDEX.md idea_queue.md
touch ssot/constants.json ssot/parameters.json ssot/changelog.json
```

### Step 2: SSoTの初期化

`ssot/constants.json` にプロジェクトで使用する全定数を記述する。

```json
{
  "_meta": {
    "created": "2026-02-21",
    "description": "Single Source of Truth for [Project Name]",
    "version": 1
  },
  "physical_constants": {
    "comment": "プロジェクト固有の物理定数をここに記述"
  },
  "statistical_thresholds": {
    "bonferroni_base_alpha": 0.05,
    "fpr_rejection_threshold": 0.50,
    "monte_carlo_n_trials": 10000
  },
  "pipeline_limits": {
    "max_hypotheses_per_seed": 3,
    "max_iterations_per_hypothesis": 5,
    "max_modify_count": 2,
    "consecutive_stop_limit": 2
  }
}
```

### Step 3: 最初の seed.md を書く

```markdown
# Seed: [アイデアのタイトル]

## What
[何を調べたいか]

## Why
[なぜそれが面白いと思うか]

## Boundary
[何が出たら「失敗」と認めるか]
```

### Step 4: AIへのプロンプトテンプレート

**Orchestrator 起動プロンプト:**

```
あなたは AIRDP フレームワークの Orchestrator です。
添付の seed.md を読み、以下を生成してください:
1. roadmap.md: 検証可能な仮説への分解（各仮説にH0/H1、成功基準、撤退基準を定義）
2. ssot/hypotheses/H*.json: 各仮説の構造化定義
制約: 仮説数は最大3つ。撤退基準は必ず定量的に定義すること。
SSoT: ssot/constants.json を参照すること。
```

**Researcher 起動プロンプト:**

```
あなたは AIRDP フレームワークの Researcher です。
roadmap.md の仮説 [H_N] について、イテレーション [M] を実行してください。
1. コードを実装し、計算を実行
2. 結果を iterations/iter_M/results.json に保存
3. researcher_report.md を作成
制約: 全定数は ssot/constants.json から読み込むこと。ハードコード禁止。
```

**Reviewer 起動プロンプト:**

```
あなたは AIRDP フレームワークの Reviewer です。
iterations/iter_M/ の結果を独立検証してください。
1. コードの再実行による結果の再現性確認
2. 統計的妥当性の検査（多重比較補正を含む）
3. SSoT整合性チェック
4. 判定: CONTINUE / STOP / MODIFY（根拠を明記）
制約: 新しい仮説を提案しないこと。判定は定量的根拠に基づくこと。
```

**Judge 起動プロンプト:**

```
あなたは AIRDP フレームワークの Judge です。
仮説 [H_N] の全イテレーション結果を俯瞰し、最終判定を行ってください。
入力: iterations/iter_*/results.json + review.md
判定: ACCEPT / REJECT / MODIFY（根拠を明記）
制約: Researcher の意図や期待にアクセスしないこと。結果と統計データのみに基づくこと。
REJECT の場合は NEGATIVE_RESULTS_INDEX.md への記載案を添付すること。
```

---

## 付録：KSAUタイムライン分析

KSAU Project の38バージョンを、AIRDPの観点から3フェーズに分類した。

```
v1–v6:  ██████████████████████ 収束フェーズ（質量フィット確立）
v7–v8:  ████                   境界探索（否定的結果の初期蓄積）
v9–v15: ██████████████████████ 発散フェーズ（風呂敷拡大）  ← AIRDP で阻止可能
v16–v25:████████████████████████████████████ 停滞フェーズ（進展なき反復）← AIRDP で短縮可能
v26–v33:████████████████████   強制収束（否定的結果の確定）
v34–v37:████████               最終整理（論文・SSoT確定）
v38:    ██                     休眠
```

**もしAIRDPが適用されていたら（推定）：**

```
Cycle 1 (≈v1–v6):   質量フィット確立 → ACCEPT
Cycle 2 (≈v7–v8):   境界探索 → REJECT（否定的結果を記録）
Cycle 3 (≈v9–v12):  拡張仮説（Max 3に制限）→ 大半 REJECT、S8のみ ACCEPT
Cycle 4 (≈v13–v15): S8予測の精緻化 → ACCEPT
Cycle 5 (≈v16):     最終整理・休眠
```

推定所要バージョン: 約16（実際の38の約42%）。

---

## ライセンス

本設計書はMITライセンスのもとで公開される。KSAU Project の成果に基づく。

---

*AIRDP Framework Design v1.0 — 2026-02-21*
*Based on lessons learned from the KSAU Project (v1.0–v38.0)*
*"The best framework is one that knows when to stop."*
