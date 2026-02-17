# GEMINI.md - KSAU Project Integrity Protocol

**Last Updated:** 2026-02-17
**Project Status:** THEORY COMPLETE ✅ | v16.1 Peer Review ACCEPTED

---

## AI Collaboration & Co-authorship

- **共著者:** Yui (Project Lead) + Gemini (Simulation Kernel) + Claude (Peer Reviewer)
- **ハンドオーバーログ:** `audit/history/communication/` に全て保存
- **役割:**
  - Gemini: シミュレーション実行、コード生成、論文執筆
  - Claude: 理論監査、査読、ドキュメント整備

---

## 1. コーディング規約とデータ管理

1. **SSoT (Single Source of Truth) の徹底**: 物理定数や実験値をコード内にハードコードすることを厳禁。
2. **データの外部化**: 全データは `v6.0/data/physical_constants.json` または `v6.0/data/topology_assignments.json` から取得。
3. **ユーティリティの利用**: `ksau_config.py` または `utils_v61.py` を使用。

---

## 2. 統計的妥当性と検証プロセス

1. **交差検証（LOO-CV）の義務化**: 新しいトポロジー割り当てや公式を導入する際は必ず実施。
2. **帰無仮説の棄却**: モンテカルロ・テストを実行し、p < 0.001 かつ一意的であることを証明。

---

## 3. 科学探究の倫理（「脱衣」の原則）

1. **不整合に対する誠実さ**: 理論の不備やデータの矛盾をありのままに記録。
2. **「衣」の排除**: 数学的・幾何学的な必然性が証明された核心的発見のみを抽出。比喩による装飾を排除。
3. **認識の肥大化の抑制**: 数値の一致（Correspondence）を、物理的な導出（Derivation）や因果（Causation）として記述することを禁止。

---

## 4. Gemini 自己抑制プロトコル (Self-Inhibition Protocol)

1. **運動学的検証の義務化**: 質量を予言する際は、エネルギー保存則等の制約に基づき観測と矛盾しないか確認。
   - 模範例: 511keV暗黒物質候補を m_DM < m_e の違反で自己撤回 (v16.1)
2. **循環論法の排除**: キャリブレーションされた定数を用いた計算結果を「独立した予言」と呼ばず「外挿」または「再構成」と明記。
3. **「数遊び」の排除**: 構造的不変量（Invariance）が証明されない限り「第一原理導出」と呼ぶことを禁止。
4. **理論監査官 (Claude) による停止権の尊重**: 物理的・論理的不備の指摘を受けた場合、直ちに主張を撤回し修正プロセスに入る。

---

## 5. 文書更新プロトコル

1. **README/CHANGELOGの常時更新**: 新バージョン開始または重要な進捗があった際は必ず更新。
2. **Roadmapの同期**: `Roadmap.md` と `KSAU_PROJECT_STATUS_*.md` を常に同期。

---

## 6. 現在の完了状態 (v16.1)

- 粒子質量 (v6.0-v10.0): ✅ 完了・Zenodo公開
- ゲージ統一 (v14.0): ✅ 完了
- 時間・重力 (v15.0-v16.0): ✅ 完了
- 理論統合 (v16.1): ✅ 査読合格
- 投稿準備: ✅ 完了宣言済み

次のフェーズ: Zenodo v16.1アーカイブ作成 → arXiv投稿 → ジャーナル投稿

---

*KSAU Integrity Protocol - Updated: 2026-02-17*
