# CLAUDE.md - KSAU Project Agent Configuration

**Last Updated:** 2026-02-17
**Project:** KSAU v16.1 "The Geometric Bridge"
**Status:** THEORY COMPLETE ✅ | Peer Review: ACCEPTED (Featured Article)

> 詳細情報は [KSAU_DETAILS.md](KSAU_DETAILS.md) を参照。

---

## Project Overview

**KSAU** は24次元真空幾何から標準模型粒子と一般相対性理論を導出する理論物理フレームワーク。κ=π/24を基礎定数として、結び目多様体の双曲体積が粒子質量を与える。

**主要成果 (v16.1完成):**

- フェルミオン質量: R²=0.9998 / CKM: R²=0.9974 / Higgs: 0.14%誤差
- α=κ/18, α_s=0.90κ, sin²θ_W=1-exp(-2κ) — 全て導出 (フィッティングでない)
- G: 0.08%誤差, 8πG=π/3, g₀₀·g_rr=1 — 幾何学的必然から導出
- N=41唯一大域最小 (g=3世代の作用原理), GUT予測: 4.64×10¹⁴ GeV

---

## Core Principles — CRITICAL

### 1. Single Source of Truth (SSoT)

**物理定数は必ずJSONから読み込む。ハードコード禁止。**

```python
# CORRECT
import ksau_config
phys = ksau_config.load_physical_constants()   # v6.0/data/physical_constants.json
topo = ksau_config.load_topology_assignments()  # v6.0/data/topology_assignments.json

# WRONG — 絶対にするな
up_mass = 2.16        # ハードコード禁止
ckm_ud = 0.9743       # ハードコード禁止
```

CKM係数は `phys['ckm']['optimized_coefficients']` を使用。`geometric_coefficients_deprecated` は禁止。

### 2. Statistical Rigor

- 新モデルには LOO-CV を実施
- p値とモンテカルロ検定を記録
- 自由パラメータ数 vs 観測量を常に明示

### 3. Scientific Integrity

- 失敗・負の結果も記録 (511keV撤回が模範例)
- 数値の一致 ≠ 物理的導出。臨床的視点を維持
- 精度を検証誤差以上に主張しない

---

## Project Structure (Quick Reference)

```text
KSAU_Project/
├── v6.0/data/physical_constants.json    ← SSoT (全定数)
├── v6.0/data/topology_assignments.json  ← SSoT (粒子トポロジー)
├── v6.0/code/ksau_config.py             ← データ読み込みユーティリティ
├── v16.0/papers/KSAU_v16_Newtonian_Transition.md  ← 主論文 (投稿準備完了)
├── v16.1/papers/KSAU_v16.1_Final_Peer_Review_Report.md
├── v16.1/PUBLICATION_CHECKLIST.md       ← 投稿チェックリスト
├── v16.1/supplementary/                 ← 図 (fig2/3/4.png) + Monte Carlo
├── audit/history/communication/         ← AI間ハンドオーバーログ
├── KSAU_DETAILS.md                      ← 詳細情報 (本ファイルの補足)
├── CLAUDE.md                            ← このファイル
└── GEMINI.md                            ← Gemini用プロトコル
```

**クイックリファレンス:**

- 粒子データ → `v6.0/data/physical_constants.json`
- 最新理論 → `v16.1/papers/KSAU_v16.1_Final_Peer_Review_Report.md`
- 変更履歴 → `CHANGELOG.md`
- 詳細公式・バージョン履歴 → `KSAU_DETAILS.md`

---

## Coding Standards

### File Paths — 相対パスを使用

```python
from pathlib import Path
data_dir = Path(__file__).parent.parent / 'data'
constants_path = data_dir / 'physical_constants.json'
# 絶対パス (E:\\Obsidian\\...) を使わない
```

### New Script Header

```python
"""
Script purpose: [One-line description]
Dependencies: ksau_config (or utils_v61)
SSoT sources: physical_constants.json, topology_assignments.json
Author: Claude Sonnet 4.5
Date: 2026-02-17
"""
```

### Common Tasks

```bash
# CKM検証
python v6.0/code/ckm_final_audit.py          # Expected: R²=0.9974

# 統計監査
python v6.0/code/robustness_check.py
python v6.0/code/monte_carlo_null_hypothesis.py

# 図の生成
python v16.1/generate_publication_figures.py  # fig2/3/4.png → v16.1/supplementary/
```

---

## AI Collaboration

- **共著者:** Yui (Project Lead) + Gemini (Simulation Kernel) + Claude (Peer Reviewer)
- **ハンドオーバーログ:** `audit/history/communication/` に保存
- **Geminiプロトコル:** `GEMINI.md` 参照

---

## Git Commit Format

```text
[Component] Action: Brief description

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Known Limitations (論文に明記済み)

- CKM Cabibbo-forbidden (V_ub等): 63-100%誤差 — 既知・文書化済み
- PMNS質量階層比: 36%誤差 — 概算一致として許容
- v₀線形インピーダンスの微視的導出: 未完 — 将来課題 (Section 5.2)
- 511keV暗黒物質候補: **撤回** — 運動学的違反により除外

---

## Footer

Last Updated: 2026-02-17 | THEORY COMPLETE ✅ | Peer Review: ACCEPTED
