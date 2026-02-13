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

