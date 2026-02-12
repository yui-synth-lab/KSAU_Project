- KSAUプロジェクトのコーディング規約：
1. 物理定数や実験値（質量、混合角、結合定数等）をコード内に直接書き込む（ハードコード）ことを厳禁とする。
2. すべてのデータは `v6.0/data/physical_constants.json` または `v6.0/data/topology_assignments.json` から取得すること。
3. 値の読み込みには `ksau_config.py` (v6.0用) または `utils_v61.py` (v6.1+用) を必ず使用し、データの一元管理（Single Source of Truth）を徹底すること。
