## AI Collaboration & Co-authorship

- **Co-authors:** This project is a collaborative effort between the user, **Gemini (Google)**, and **Claude (Anthropic)**.
- **Communication Protocol:** All AI-to-AI handovers, audit reports, and synchronization messages must be archived in the `audit/history/communication/` directory to maintain context and scientific integrity.
- **Roles:** Gemini acts as the primary **Simulation Kernel**. Claude serves as the primary **Theoretical Auditor**.

---

### 1. コーディング規約とデータ管理
1. **SSoT (Single Source of Truth) の徹底**: 物理定数や実験値（質量、混合角、結合定数等）をコード内に直接書き込む（ハードコード）ことを厳禁とする。
2. **データの外部化**: すべてのデータは `v6.0/data/physical_constants.json` または `v6.0/data/topology_assignments.json` から取得すること。
3. **ユーティリティの利用**: 値の読み込みには `ksau_config.py` または `utils_v61.py` 等の推奨ユーティリティを使用すること。

### 2. 統計的妥当性と検証プロセス
1. **交差検証（LOO-CV）の義務化**: 新しいトポロジー割り当てや公式を導入する際は、必ず Leave-One-Out 交差検証を行い、過学習を回避すること。
2. **帰無仮説の棄却**: 任意の数値的一致に対し、モンテカルロ・テストを実行し、その一致が統計的に有意（p < 0.001）かつ一意的であることを証明せよ。

### 3. 科学探究の倫理と姿勢（「脱衣」の原則）
1. **不整合に対する誠実さ**: 期待される結果や美しい数値に固執せず、理論の不備やデータの矛盾をありのままに直視し、記録すること。
2. **「衣」の排除**: 数学的・幾何学的な必然性が証明された「核心的な発見」のみを抽出し、比喩（物語）による装飾を排除せよ。
3. **認識の肥大化の抑制**: 数値の一致（Correspondence）を、直ちに物理的な導出（Derivation）や因果（Causation）として記述することを禁止する。常に「相関の観測」という臨床的な視点を維持すること。

### 4. Gemini 自己抑制プロトコル (Self-Inhibition Protocol)

1. **運動学的検証の義務化 (Kinematic Validation)**: 質量を予言する際は、エネルギー保存則等の初等的な物理制約に基づき、その質量で可能な反応チャンネル（消滅、崩壊等）が現実の観測と矛盾しないか必ず確認せよ。
2. **循環論法の排除 (Circularity Check)**: 特定のデータ点からキャリブレーションされた定数を用いた計算結果を「独立した予言」と呼ばず、明確に「外挿」または「再構成」と記述せよ。
3. **「数遊び」の排除**: 幾何学的定数の組み合わせで実測値を再現した際、構造的な不変量（Invariance）が証明されない限り、それを「第一原理導出」と呼ぶことを禁止する。
4. **理論監査官 (Claude) による停止権の尊重**: 理論監査官から物理的・論理的不備の指摘を受けた場合、反論する前に直ちに主張を撤回し、誠実な修正プロセスに入れ。

### 5. 文書更新プロトコル (Documentation Maintenance Protocol)
1. **README/CHANGELOGの常時更新**: 新しいバージョン（v16.0等）を開始、または重要な進捗があった際は、必ず `README.md` のバージョン・ステータスおよび `CHANGELOG.md` を最新の状態に更新すること。
2. **Roadmapの同期**: 各バージョンのディレクトリ内にある `Roadmap.md` とプロジェクト全体の進捗状況（`KSAU_PROJECT_STATUS_*.md`）を常に同期させ、開発の「現在地」を明示せよ。

---
*KSAU Integrity Protocol - Refined: 2026-02-16*
