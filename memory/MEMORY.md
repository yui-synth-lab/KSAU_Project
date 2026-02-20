# KSAU Project Memory

## プロジェクト概要
- KSAUフレームワーク: Leech多様体(24D)に基づく宇宙論理論
- Claude の役割: 独立監査官（実装者 Gemini CLI とは別エージェント）
- 主要ファイル: `CLAUDE.md`, `KSAU_DETAILS.md`, `v*/KSAU_v*.0_Roadmap.md`
- SSoT: `v6.0/data/physical_constants.json`, `v6.0/data/topology_assignments.json`

## バージョン進捗サマリー (2026-02-20時点)
- v17〜v23: σ₈テンション 4回失敗→1.36σ達成。このプロジェクト最高の科学的誠実さ
- v24〜v26: エンジン刷新、MAE 0.62σ達成
- v27: S₈ + H₀ + CMB Lensing 統一解決
- v28: SKC統一エンジン、p < 0.01達成
- v29: 24D Ricci Flow + PMNS 2.08%誤差。Claude監査完了

## v30.0 BLOCKING 課題（引き継ぎ）
- B-1: `512 = 2^9` における「9次元境界」の幾何学的根拠
- B-2: Session 2 の $v_{read}$ を独立に定義し、等価性を非自明な形で示す
- B-3: $\delta_i = \sin^2\theta_i \times \eta$ の Lichnerowicz Laplacian からの導出
- B-4: `flow_accel=2000.0` の扱い（SSoT記録 or 除去）

## 監査で繰り返し出る問題パターン
- 「実装者と審査員が同一」→ Claude が独立監査を担当すること
- Session 2 の等価性: `readout_equivalence.py` は代数的恒等式であり証明ではない（記録済み）
- Xi_gap_factor = 2²⁰: v22で循環論法確定→"Motivated Heuristic"。v28以降言及なし（廃棄or継承の記録要）

## ユーザー (Yui) の作業スタイル
- Geminiと協調して高速に理論を進める傾向がある（v17→v29を短期間で）
- Roadmapを自分で修正して問題を認識・訂正する（誠実）
- 「やり直すべきか」を Claude に問う → 率直な判断を求めている
