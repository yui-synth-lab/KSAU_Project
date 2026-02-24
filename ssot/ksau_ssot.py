"""
ksau_ssot.py — KSAU Project Single Source of Truth ローダー

使い方（Researcher のコード冒頭に必ずこれだけ書く）:

    import sys

    current_file = Path(__file__).resolve()
    project_root = current_file.parents[5]
    ssot_path = project_root / "ssot"
    sys.path.insert(0, str(ssot_path))    
    from ksau_ssot import SSOT

    ssot = SSOT()
    consts = ssot.constants()
    knots_df, links_df = ssot.knot_data()

このファイル自身が ssot/ にあるため、SSOT_DIR は自動解決される。
パスをコードに書く必要はない。
"""

import json
from pathlib import Path

import pandas as pd

# このファイルが置かれている場所 = ssot/
_SSOT_DIR = Path(__file__).parent

# KnotInfo CSV は ssot/ の隣の data/ にある
_DATA_DIR = _SSOT_DIR.parent / "data"


class SSOT:
    """KSAU SSoT への読み取り専用アクセサ。"""

    def constants(self) -> dict:
        """ssot/constants.json を読み込んで返す。"""
        with open(_SSOT_DIR / "constants.json", encoding="utf-8") as f:
            return json.load(f)

    def parameters(self) -> dict:
        """ssot/parameters.json を読み込んで返す。"""
        with open(_SSOT_DIR / "parameters.json", encoding="utf-8") as f:
            return json.load(f)

    def hypothesis(self, hid: str) -> dict:
        """ssot/hypotheses/H*.json を読み込んで返す。例: ssot.hypothesis('H3')"""
        path = _SSOT_DIR / "hypotheses" / f"{hid}.json"
        if not path.exists():
            raise FileNotFoundError(f"Hypothesis file not found: {path}")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def topology_assignments(self) -> dict:
        """ssot/data/raw/topology_assignments.json を読み込んで返す。"""
        with open(_SSOT_DIR / "data" / "raw" / "topology_assignments.json", encoding="utf-8") as f:
            return json.load(f)

    def knot_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        KnotInfo / LinkInfo CSV を読み込んで (knots_df, links_df) を返す。
        低メモリモードで読み込むため大規模データでも安全。
        """
        knot_path = _DATA_DIR / "knotinfo_data_complete.csv"
        link_path = _DATA_DIR / "linkinfo_data_complete.csv"

        knots_df = pd.read_csv(knot_path, sep='|', skiprows=[1], low_memory=False) if knot_path.exists() else pd.DataFrame()
        links_df = pd.read_csv(link_path, sep='|', skiprows=[1], low_memory=False) if link_path.exists() else pd.DataFrame()

        return knots_df, links_df

    def analysis_params(self) -> dict:
        """constants.json の analysis_parameters セクションを返す。"""
        return self.constants().get("analysis_parameters", {})

    def statistical_thresholds(self) -> dict:
        """constants.json の statistical_thresholds セクションを返す。"""
        return self.constants().get("statistical_thresholds", {})

    @property
    def ssot_dir(self) -> Path:
        """SSoT ディレクトリの Path オブジェクト（デバッグ用）。"""
        return _SSOT_DIR

    @property
    def data_dir(self) -> Path:
        """KnotInfo データディレクトリの Path オブジェクト（デバッグ用）。"""
        return _DATA_DIR
