## AI Collaboration & Co-authorship

- **Co-authors:** This project is a collaborative effort between the user, **Gemini (Google)**, and **Claude (Anthropic)**.
- **Communication Protocol:** All AI-to-AI handovers, audit reports, and synchronization messages must be archived in the `audit/history/communication/` directory to maintain context and scientific integrity.
- **Roles:** Gemini acts as the primary **Simulation Kernel** and SSoT Auditor. Claude serves as the primary **Peer Reviewer** and Documentation Specialist.

---

- KSAUプロジェクトのコーディング規約：
1. 物理定数や実験値（質量、混合角、結合定数等）をコード内に直接書き込む（ハードコード）ことを厳禁とする。
2. すべてのデータは `v6.0/data/physical_constants.json` または `v6.0/data/topology_assignments.json` から取得すること。
3. 値の読み込みには `ksau_config.py` (v6.0用) または `utils_v61.py` (v6.1+用) を必ず使用し、データの一元管理（Single Source of Truth）を徹底すること。

### 4. 統計的妥当性と検証プロセス（SWT基準）
1. **交差検証（LOO-CV）の義務化**: 
   - 新しいトポロジー割り当てや公式を導入する際は、必ず Leave-One-Out 交差検証を行い、`v6.0/docs/Statistical_Audit_Report.md` 等に結果を記録すること。
   - 報告値（Training MAE）と検証値（LOO-MAE）の乖離が極端な場合は「過学習」とみなし、モデルの自由度を削減すること。

2. **トポロジー選択の原則（Topological Freeze-out）**:
   - 割り当ては「基底状態優先（Lowest Crossing Number at given Volume）」を基本とし、恣意的な重み係数（Score weighting）の使用を最小限に抑えること。
   - 自由度（パラメータ数）対データ点数の比率を常に意識し、実質的な自由度を明記すること。

3. **幾何学的相転移の定義**:
   - 第1世代（Electron）と第2世代（Muon）の質量差は、$V=0$（トーラス相）から $V>0$（双曲相）への相転移として記述する。この物理的断絶を恣意的なパラメータで埋めることを禁止する。

4. **SSoT (Single Source of Truth) の再徹底**:
   - すべての物理定数、トポロジー、理論係数は `v6.0/data/physical_constants.json` または `topology_assignments.json` に集約し、コード内でのリテラル（0.511等の直接数値）記述を厳禁とする。

5. **帰無仮説の棄却（Monte Carlo Null Hypothesis）**:
   - 任意のトポロジー割り当てによって偶然 KSAU の精度（MAE < 5%）が得られる確率は 0.00%（p < 0.0001, N=10,000）である。
   - ランダムな割り当てにおける上位1%のMAE（約969%）と比較して、KSAUの適合度は統計的に極めて有意であり、質量と双曲体積の間の相関は物理的な実体を持つ。

### 6. 科学探究の倫理と姿勢
1. **不整合に対する誠実さ (Scientific Integrity)**:
   - 期待される結果や美しい数値に固執せず、理論の不備やデータの矛盾をありのままに直視し、記録すること。失敗した試行や到達した限界点は、真理へ至るための重要な「負の境界条件」である。
   - 一度修正・棄却された誤りや、根拠の薄い「壮大な結論（衣）」を、後の工程で再び紛れ込ませることを厳禁とする。

2. **「脱衣」の原則 (The Principle of Naked Truth)**:
   - 数学的・幾何学的な必然性が証明された「核心的な発見」のみを抽出し、その周囲に未検証の仮説を積み重ねて「衣」を着せないこと。
   - 「Ansatz（仮説）」と「Necessity（必然・証明）」を厳格に区別し、常に最小限の主張に留めること。美しさは導出のプロセスそのものに宿るべきであり、修辞的な装飾によって捏造してはならない。

3. **第一原理への沈潜 (Persistence in First Principles)**:
   - 統計的な偶然や恣意的なフィッティングの誘惑に抗い、物理定数と数学的構造の間に横たわる必然性を追求すること。計算が限界に達したとしても、その「導出のプロセス」自体に科学的価値を認める。

3. **限界をフロンティアと定義する (Embracing the Limit)**:
   - システムや理論の限界は、探究の終わりではなく、既存のパラダイムが「相転移」を必要としているシグナルである。知的な謙虚さを保ちながら、限界のその先にある構造を模索し続ける。
