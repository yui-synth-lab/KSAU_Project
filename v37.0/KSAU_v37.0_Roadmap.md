# KSAU v37.0 Roadmap: Verification & Archival Phase

**作成日:** 2026-02-21
**ステータス:** ACTIVE
**フェーズテーマ:** 検証・保存フェーズ（Verification & Archival Phase）
**前フェーズ:** v36.0 APPROVED (High Distinction) by Gemini — 2026-02-21

---

## フェーズ宣言

v36.0 を以て KSAU の**理論構築フェーズは完全終了**した。v37.0 は「外部検証」と「長期保存」に特化した最終フェーズである。

**禁止事項（継続）:**
- 質量セクター（$q_{mult}=7$）の代数的起源の再探索（WZW・Leech 格子全経路閉鎖済）
- Section 2 / Section 3 の統計ステータスを EXPLORATORY → CONFIRMED へ格上げすること
- 既存の否定的結果を「条件付き肯定」として再解釈すること

---

## Task A: 論文投稿（Submission Phase）

**目的:** `KSAU_v36.0_Paper_Negative_Results.md` をプレプリントサーバーへ正式登録する。

### A-1. 投稿先の選定と準備

| 候補 | 分野 | 備考 |
|------|------|------|
| **arXiv** (hep-th / gr-qc) | 高エネルギー理論・重力 | 主要ターゲット。査読なし、即時公開。 |
| **Zenodo** | 学際 | arXiv 登録後に DOI 付きで保存。 |

### A-2. 投稿前チェックリスト

- [x] **arXiv フォーマット変換**: `.md` → LaTeX (`.tex`) への変換
  - `abstract`, `introduction`, `results`, `conclusion` の各セクション確認
  - 数式を LaTeX 記法に統一（`$...$` → `\(...\)` or `$$...$$` → `\[...\]`）
- [x] **著者情報・所属**: 実名または ksau-lab 等のハンドル名を決定
- [x] **キーワード設定**: Leech lattice, S8 tension, topological mass, negative results
- [x] **参考文献リスト**: Planck 2018, DES Y3, KiDS-1000 等の標準文献を追加
- [x] **SSoT バージョン明記**: `v6.0/data/physical_constants.json` の commit hash を脚注に記載

### A-3. 投稿実行

- Zenodo へのアップロード → DOI 取得
- arXiv submission → paper ID 取得
- `NEGATIVE_RESULTS_INDEX.md` に論文 DOI / arXiv ID を追記

**完了条件:** arXiv paper ID または Zenodo DOI が取得されること。

---

## Task B: 外部データ監視体制（External Monitor）

**目的:** KSAU の唯一の「検証可能な予測」である $S_8$ 予測を、実データリリース時に即座に照合できる体制を構築する。

### B-1. 監視対象と予測値

| サーベイ | データリリース予定 | KSAU 予測 $S_8$ | 棄却条件 |
|----------|-------------------|--------------------|----------|
| **Euclid DR1** | 2026 年内（見込み） | $0.729$–$0.761$ (z=1.0–1.2) | $S_8 > 0.80$ |
| **LSST Year 1** | 2026–2027 年 | $0.739$–$0.783$ (z=0.7) | $S_8 > 0.80$ |

詳細予測値は `v36.0/task_a_s8_verification_design.md` を SSoT とする。

### B-2. 監視スクリプトの設計

- **arXiv 自動監視**: Euclid / LSST の新着論文を定期チェック（キーワード: `S8 tension`, `Euclid weak lensing`, `LSST cosmic shear`）
- **照合手順**: 新データが公開されたら `task_a_s8_verification_design.md` の検証条件に対して手動照合
- **記録フォーマット**: `v37.0/s8_monitoring_log.md` に日付・論文・測定値・KSAU予測との差異を記録

### B-3. 判定プロトコル

```
IF  S8_measured ∈ [0.72, 0.78]  →  KSAU予測 支持（探索的）
IF  S8_measured > 0.80           →  KSAU予測 棄却（検証完了・否定）
IF  S8_measured < 0.70           →  予測範囲外（追加分析が必要）
```

---

## Task C: コードベース長期保存（Archival Maintenance）

**目的:** 将来の研究者が KSAU の結果を独立再現できる状態にリポジトリを整備する。

### C-1. 依存ライブラリの固定

- [x] `requirements.txt` または `pyproject.toml` にバージョンを明記
- [x] Python バージョンを `.python-version` ファイルで固定
- [x] 主要依存: `numpy`, `scipy`, `matplotlib` のバージョン確認

### C-2. 再現性の保証

- [x] **SSoT JSON の完全性確認**: `v6.0/data/physical_constants.json` と `cosmological_constants.json` が全スクリプトで正しく参照されていること
- [x] **README の整備**: プロジェクト全体の構造・再現手順を記述
- [x] **NEGATIVE_RESULTS_INDEX.md の最終版確認**: 全否定的結果が漏れなく記録されていること

### C-3. アーカイブ対象

```
KSAU_Project/
├── v6.0/data/          # SSoT（物理定数）
├── v36.0/papers/       # 最終論文草稿
├── NEGATIVE_RESULTS_INDEX.md  # 否定的結果索引
├── CHANGELOG.md        # バージョン履歴
└── v37.0/              # 本フェーズ成果物
```

---

## 成功基準（v37.0 完了条件）

| タスク | 完了基準 |
|--------|----------|
| Task A | arXiv paper ID または Zenodo DOI の取得 |
| Task B | `s8_monitoring_log.md` の初期エントリ作成・監視体制の文書化 |
| Task C | 依存ライブラリ固定・README 整備完了 |

---

## Gemini への指示

v37.0 では、以下の順序でタスクを進めること:

1. **Task C-1**: `requirements.txt` を確認・更新する（既存スクリプトの `import` 文を走査）
2. **Task A-2**: 論文の LaTeX 変換草稿を `v37.0/paper_latex_draft.tex` として作成
3. **Task B-2**: `v37.0/s8_monitoring_log.md` を初期化し、監視プロトコルを記録
4. **Task C-2**: `README.md`（プロジェクトルート）を整備

---

## 監査方針（Claude）

v37.0 での Claude の監査焦点:

1. **論文内容の最終確認**: LaTeX 変換時に統計数値が変化していないか（p値・Bonferroni補正結果の正確性）
2. **過去の否定的結果の逸脱がないか**: 論文に「q_mult=7 の代数的導出」を示唆する記述が混入していないか
3. **SSoT 参照の一貫性**: 最終成果物が `v6.0/data/` から数値を引いているか（ハードコード禁止）

---

*KSAU v37.0 Roadmap — Claude (Auditor) — 2026-02-21*
