# AIRDP: AI-Driven Research & Discovery Pipeline

## フレームワーク利用ガイド

**Version:** 2.0（汎用化版）
**Last Updated:** 2026-02-23

---

## 1. AIRDPとは

AIRDP は、人間がアイデア（seed）を提供し、AIエージェントが自律的に仮説を検証・反証する研究パイプラインのフレームワークです。

**主な特徴:**
- 仮説の発散を制御する構造化されたフェーズゲート
- 統計的閾値による自動撤退判定
- SSoT（Single Source of Truth）によるデータ一元管理
- 否定的結果の構造化された記録
- 合成データの使用禁止による検証の循環性排除

---

## 2. アーキテクチャ

```
Phase 1: Seed     ← 人間がアイデアを seed.md に記述
Phase 2: Plan     ← Orchestrator が roadmap.md を生成
Phase 3: Execute  ← Researcher ↔ Reviewer の自動イテレーション
Phase 4: Judge    ← Judge が仮説ごとに最終判定
Phase 5: Report   ← Orchestrator がサイクルレポートを生成
```

### ロール定義

| ロール | 役割 | プロンプト |
|--------|------|----------|
| **Orchestrator** | ロードマップ生成・サイクル管理 | `orchestrator_phase2.md`, `orchestrator_phase5.md` |
| **Researcher** | タスク実装・計算実行 | `researcher.md` |
| **Reviewer** | 独立検証・統計的査読 | `reviewer.md` |
| **Judge** | 仮説の最終判定(ACCEPT/REJECT/MODIFY) | `judge_phase4.md` |
| **Writer** | 論文 draft 執筆 | `paper_writer.md` |
| **Paper Reviewer** | 論文 draft 査読 | `paper_reviewer.md` |

---

## 3. ディレクトリ構造

新しいプロジェクトでは以下の構造を作成してください。

```
my_project/
├── airdp_common.ps1              # フレームワーク層（変更不要）
├── airdp_orchestrator.ps1        # フレームワーク層（変更不要）
├── airdp_phase2.ps1              # フレームワーク層（変更不要）
├── airdp_phase3.ps1              # フレームワーク層（変更不要）
├── airdp_phase4.ps1              # フレームワーク層（変更不要）
├── airdp_phase5.ps1              # フレームワーク層（変更不要）
├── airdp_prompts/                # フレームワーク層（変更不要）
│   ├── researcher.md
│   ├── reviewer.md
│   ├── orchestrator_phase2.md
│   ├── orchestrator_phase5.md
│   ├── judge_phase4.md
│   ├── paper_writer.md
│   └── paper_reviewer.md
├── ssot/                         # プロジェクト層（プロジェクトごとに記述）
│   ├── constants.json            # プロジェクト固有の定数・パラメータ
│   ├── parameters.json           # 分析パラメータ
│   ├── changelog.json            # SSoT 変更履歴
│   ├── <project_name>_ssot.py    # プロジェクト固有の SSoT ローダー
│   ├── project_ssot_template.py  # テンプレート（参考用）
│   └── hypotheses/               # 仮説定義ファイル
│       ├── H1.json
│       ├── H2.json
│       └── ...
├── data/                         # プロジェクトの実データ
│   └── [実データファイル群]
├── cycles/                       # サイクル実行記録
│   ├── cycle_01/
│   │   ├── seed.md               # 人間が記述するアイデア
│   │   ├── roadmap.md            # Orchestrator が生成
│   │   ├── iterations/           # Phase 3 のイテレーション
│   │   │   ├── iter_01/
│   │   │   │   ├── code/
│   │   │   │   ├── results.json
│   │   │   │   ├── researcher_report.md
│   │   │   │   └── review.md
│   │   │   └── iter_02/
│   │   ├── verdict.md            # Judge の最終判定
│   │   └── cycle_report.md       # サイクルレポート
│   └── cycle_02/
├── NEGATIVE_RESULTS_INDEX.md     # 否定的結果の累積記録
├── idea_queue.md                 # 将来探索するアイデアのキュー
└── AIRDP_README.md               # このファイル
```

---

## 4. 新しいプロジェクトの始め方

### Step 1: フレームワークファイルをコピー

以下のファイルをプロジェクトディレクトリにコピーしてください（変更不要）:

- `airdp_common.ps1`
- `airdp_orchestrator.ps1`
- `airdp_phase2.ps1` ~ `airdp_phase5.ps1`
- `airdp_prompts/` ディレクトリ全体

### Step 2: SSoT を初期化

```bash
# SSoT ディレクトリを作成
mkdir ssot
mkdir ssot/hypotheses

# テンプレートをコピーして編集
cp ssot/project_ssot_template.py ssot/<project_name>_ssot.py
```

`ssot/<project_name>_ssot.py` を編集し、`load_data()` メソッドをプロジェクトの実データに合わせて実装してください。

### Step 3: constants.json を作成

```json
{
  "project_name": "My Research Project",
  "version": "1.0",
  "statistical_thresholds": {
    "p_value_threshold": 0.05,
    "bonferroni_factor": 3,
    "fpr_max": 0.50,
    "min_effect_size": 0.5
  },
  "analysis_parameters": {
    "max_iterations_per_hypothesis": 5,
    "consecutive_stop_limit": 2
  }
}
```

### Step 4: seed.md を作成

```bash
mkdir cycles/cycle_01
```

`cycles/cycle_01/seed.md` に以下を記述:

```markdown
# Seed: Cycle 01 — [タイトル]

## 1. 核心的な問い (Core Questions)
[何を調べたいか — 1〜3 個の具体的な問いを記述]

## 2. 理論的背景
[出発点の整理]

## 3. 実行フェーズの目標
1. [タスク1]
2. [タスク2]
3. [タスク3]

## 4. Boundary（失敗条件・撤退基準）
| 条件 | 処理 |
| --- | --- |
| [撤退条件] | REJECT |
| Bonferroni 補正後 p > 0.025 | REJECT |
| Reviewer 連続 STOP 2 回 | 強制終了 |

## 5. 成功基準 (Success Criteria)
* [定量的な達成基準]
```

### Step 5: パイプラインを実行

```powershell
# 全フェーズ連続実行
.\airdp_orchestrator.ps1 -ProjectDir . -CycleId 01 `
    -SeedPath .\cycles\cycle_01\seed.md `
    -Orchestrator gemini -Researcher gemini -Reviewer claude -Judge claude

# またはフェーズ個別実行
.\airdp_phase2.ps1 -ProjectDir . -CycleId 01 -SeedPath .\cycles\cycle_01\seed.md
.\airdp_phase3.ps1 -ProjectDir . -CycleId 01 -Researcher gemini -Reviewer claude
.\airdp_phase4.ps1 -ProjectDir . -CycleId 01 -Judge claude
.\airdp_phase5.ps1 -ProjectDir . -CycleId 01 -Orchestrator gemini
```

---

## 5. プレースホルダー一覧

プロンプトテンプレート内で使用されるプレースホルダーは `airdp_common.ps1` の `Expand-PromptTemplate` によって実行時に展開されます。

### 共通プレースホルダー

| プレースホルダー | 展開元 | 説明 |
|-----------------|--------|------|
| `{SSOT_DIR}` | `Resolve-AirdpPaths` | SSoT ディレクトリの絶対パス |
| `{ROADMAP_PATH}` | `Resolve-AirdpPaths` | roadmap.md のパス |
| `{ITER_DIR}` | Phase 3 ループ内 | 現在のイテレーションディレクトリ |
| `{LOG_PATH}` | `Resolve-AirdpPaths` | output_log.md のパス |
| `{GO_PATH}` | `Resolve-AirdpPaths` | go.md のパス |
| `{NG_PATH}` | `Resolve-AirdpPaths` | ng.md のパス |
| `{WORK_DIR}` | `Resolve-AirdpPaths` | サイクルディレクトリ |
| `{CONSTANTS_PATH}` | `Resolve-AirdpPaths` | constants.json のパス |
| `{NEG_RESULTS_PATH}` | `Resolve-AirdpPaths` | NEGATIVE_RESULTS_INDEX.md のパス |

### プロジェクト固有プレースホルダー

以下のプレースホルダーは **フレームワーク層では展開されません**。プロジェクトが `airdp_common.ps1` のパス解決をカスタマイズするか、プロンプト内でプロジェクト固有の情報として参照されます。

| プレースホルダー | 説明 | 設定方法 |
|-----------------|------|---------|
| `{PROJECT_SSOT_LOADER}` | SSoT ローダーのファイル名（例: `my_project_ssot.py`） | プロンプト展開時に `$vars` に追加 |
| `{PROJECT_SSOT_MODULE}` | SSoT ローダーの Python モジュール名（例: `my_project_ssot`） | プロンプト展開時に `$vars` に追加 |

**Phase 3 での展開例:**

```powershell
$researcherVars = @{
    ROADMAP_PATH        = $p.RoadmapPath
    NG_PATH             = $p.NgPath
    GO_PATH             = $p.GoPath
    WORK_DIR            = $p.CycleDir
    LOG_PATH            = $p.LogPath
    ITER_DIR            = $iterDir
    SSOT_DIR            = $p.SsotDir
    PROJECT_SSOT_LOADER = "my_project_ssot.py"     # プロジェクト固有
    PROJECT_SSOT_MODULE = "my_project_ssot"         # プロジェクト固有
}
```

---

## 6. SSoT ローダーの実装ガイド

### テンプレートの構造

`ssot/project_ssot_template.py` には以下が定義されています:

- **`SSOTBase`**: 全プロジェクト共通の基底クラス
  - `constants()`: constants.json の読み込み
  - `parameters()`: parameters.json の読み込み
  - `hypothesis(hid)`: 仮説定義の読み込み
  - `analysis_params()`: 分析パラメータの取得
  - `statistical_thresholds()`: 統計閾値の取得
  - `load_data()`: **抽象メソッド**（プロジェクトが実装）

- **`SSOT(SSOTBase)`**: プロジェクト固有の実装クラス

### 実装例

```python
# ssot/genomics_ssot.py
from project_ssot_template import SSOTBase
import pandas as pd

class SSOT(SSOTBase):
    def load_data(self):
        """ゲノムデータを読み込む。"""
        variants = pd.read_csv(self.data_dir / "variants.csv")
        phenotypes = pd.read_csv(self.data_dir / "phenotypes.csv")
        return variants, phenotypes

    def gene_annotations(self) -> dict:
        """constants.json の gene_annotations セクションを返す。"""
        return self.constants().get("gene_annotations", {})
```

---

## 7. 合成データ禁止ポリシー

AIRDP v2.0 では、以下を厳格に禁止しています:

| 禁止項目 | 理由 |
|---------|------|
| `np.random.seed` + データ生成 | 検証の循環性を招く |
| Ground Truth のハードコード | 仮説と検証データの同一ソース |
| `generate_synthetic_*` 関数 | 合成データへの回帰は科学的に無効 |
| 理論式から生成した「正解値」への回帰 | 循環論法 |

**Reviewer** は合成データの使用を検出した場合、即座に却下します。
**Judge** は合成データに基づく結果を ACCEPT しません。

---

## 8. フレームワーク層 vs プロジェクト層

### フレームワーク層（変更不要）

| ファイル | 役割 |
|---------|------|
| `airdp_common.ps1` | パス解決・セッション管理・AI呼び出し |
| `airdp_orchestrator.ps1` | 全フェーズ連続実行 |
| `airdp_phase2.ps1` | Phase 2: Plan |
| `airdp_phase3.ps1` | Phase 3: Execute |
| `airdp_phase4.ps1` | Phase 4: Judge |
| `airdp_phase5.ps1` | Phase 5: Report |
| `airdp_prompts/*.md` | 全プロンプトテンプレート |

### プロジェクト層（プロジェクトごとに記述）

| ファイル | 役割 |
|---------|------|
| `ssot/constants.json` | プロジェクト固有の定数 |
| `ssot/parameters.json` | 分析パラメータ |
| `ssot/<project>_ssot.py` | プロジェクト固有の SSoT ローダー |
| `data/` | プロジェクトの実データ |
| `cycles/cycle_NN/seed.md` | 各サイクルの探索テーマ |
| `NEGATIVE_RESULTS_INDEX.md` | 否定的結果の蓄積 |
| `idea_queue.md` | 将来のアイデアキュー |

---

## 9. コマンドリファレンス

### 全フェーズ連続実行

```powershell
.\airdp_orchestrator.ps1 `
    -ProjectDir .        `  # プロジェクトルート
    -CycleId auto        `  # auto = 自動採番
    -SeedPath <path>     `  # seed.md のパス
    -Orchestrator gemini `  # Orchestrator に使う AI
    -Researcher gemini   `  # Researcher に使う AI
    -Reviewer claude     `  # Reviewer に使う AI
    -Judge claude        `  # Judge に使う AI
    -MaxIterations 10    `  # Phase 3 の最大イテレーション
    -SkipApproval           # Phase 2 の人間承認をスキップ（CI用）
```

### フェーズ個別実行

```powershell
# Phase 2: Plan
.\airdp_phase2.ps1 -ProjectDir . -CycleId 01 -SeedPath .\cycles\cycle_01\seed.md

# Phase 3: Execute
.\airdp_phase3.ps1 -ProjectDir . -CycleId 01 -Researcher gemini -Reviewer claude

# Phase 4: Judge
.\airdp_phase4.ps1 -ProjectDir . -CycleId 01 -Judge claude

# Phase 5: Report
.\airdp_phase5.ps1 -ProjectDir . -CycleId 01 -Orchestrator gemini
```

### カスタムプロンプトディレクトリ

```powershell
.\airdp_orchestrator.ps1 -ProjectDir . -CycleId 01 -PromptsDir .\my_custom_prompts
```

---

## 10. 既存プロジェクトからの移行

KSAU プロジェクトなど、既にプロジェクト固有の SSoT ローダー（`ksau_ssot.py`）を使用しているプロジェクトは、以下の手順で移行できます:

1. 既存の `ksau_ssot.py` はそのまま維持
2. Phase 3 の `$researcherVars` に `PROJECT_SSOT_LOADER` と `PROJECT_SSOT_MODULE` を追加
3. プロンプト内の KSAU 固有参照は汎用プレースホルダーに置き換え済み

**移行は段階的に行えます。** 既存のサイクル記録（`cycles/cycle_01/` 等）は一切影響を受けません。

---

## 付録: 設計思想

AIRDP は以下の3つの構造的問題を解決するために設計されました:

| 問題 | 解決策 |
|------|--------|
| **仮説の発散** | 仮説同時並行数の上限（Max 3）+ イテレーション上限 |
| **人間の介入バイアス** | Phase 3 中は人間介入不可（緊急停止のみ） |
| **撤退判断の遅延** | 統計的閾値（Bonferroni補正 p値、FPR）による機械的判断 |
| **検証の循環性** | 合成データ禁止ポリシー + Reviewer による真正性チェック |

詳細な設計書は [AIRDP_Framework_Design.md](AIRDP_Framework_Design.md) を参照してください。
