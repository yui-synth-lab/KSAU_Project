# KSAU Extended Verifier v2 (Hypothesis Testing: 9_1 vs 10_17)

import pandas as pd
import re
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

CSV_PATH = "KSAU/knotinfo_data_complete.csv"

TARGET_CANDIDATES = ["9_1", "10_17"]

def _is_empty(x: Any) -> bool:
    if x is None: return True
    if isinstance(x, float) and pd.isna(x): return True
    s = str(x).strip()
    return s in ("", "0", "nan", "None")

def _try_get(row: pd.Series, key_candidates: List[str]) -> Any:
    for k in key_candidates:
        if k in row.index and not _is_empty(row[k]): return row[k]
        for idx in row.index:
            if isinstance(idx, tuple) and k in idx:
                if not _is_empty(row[idx]): return row[idx]
    return None

def parse_poly_span(poly_str: str) -> int:
    if _is_empty(poly_str): return 0
    s = str(poly_str).replace(" ", "").replace("(-", "(NEG")
    parts = s.split("^")
    exps = []
    for p in parts[1:]:
        m = re.match(r"\(?([A-Z0-9\-]+)\)?", p.replace("NEG", "-"))
        if m:
            try:
                exps.append(int(m.group(1)))
            except: pass
    if not exps:
        if "t" in s and "t^" not in s: exps.extend([1, 0])
        return 0
    return max(exps) - min(exps)

def get_homfly_v_span(homfly_str: str) -> int:
    if _is_empty(homfly_str): return 0
    s = str(homfly_str).replace(" ", "").replace("(-", "(NEG")
    v_exps = []
    matches = re.findall(r"v\^?\(?(NEG\d+|[0-9\-]+)\)?", s.replace("NEG", "-"))
    for m in matches:
        try:
            val = m.replace("NEG", "-")
            v_exps.append(int(val))
        except: pass
    if not v_exps: return 0
    return max(v_exps) - min(v_exps)

def read_knotinfo(csv_path: str) -> pd.DataFrame:
    attempts = [dict(sep="|", header=[0, 1]), dict(sep="|", header=0), dict(sep=",", header=0)]
    for kwargs in attempts:
        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False, **kwargs)
            if "name" in df.columns: df = df.set_index("name")
            else: df = df.set_index(df.columns[0])
            if any(k in df.index for k in TARGET_CANDIDATES): return df
        except: continue
    raise RuntimeError("Failed to load CSV")

def main():
    df = read_knotinfo(CSV_PATH)
    
    print("\n=== Hypothesis Testing: 9_1 vs 10_17 ===")
    
    results = []
    for name in TARGET_CANDIDATES:
        if name not in df.index:
            print(f"Knot {name} not found in CSV.")
            continue
        row = df.loc[name]
        
        sym_type = _try_get(row, ["symmetry_type", "Symmetry Type"])
        alex_str = _try_get(row, ["alexander_polynomial", "Alexander"])
        alex_span = parse_poly_span(alex_str)
        is_alt = _try_get(row, ["alternating", "Alternating"])
        homfly_str = _try_get(row, ["homfly_polynomial", "HOMFLY"])
        homfly_span = get_homfly_v_span(homfly_str)
        crossing = _try_get(row, ["crossing_number", "Crossing Number"])
        ropelength = _try_get(row, ["ropelength", "Ropelength"])
        
        results.append({
            "Knot": name,
            "Symmetry": sym_type,
            "Alternating": is_alt,
            "Crossing": crossing,
            "Alex Span": alex_span,
            "Span=2g?": "YES" if alex_span == 8 else f"NO ({alex_span})",
            "HOMFLY v-Span": homfly_span,
            "Ropelength": ropelength
        })
        
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    
    print("\n[Analysis]")
    print("1. If 10_17 is Amphicheiral, it fits the 'Even Generation = Amphicheiral' hypothesis.")
    print("2. Check if Alex Span is 8 (Required for Genus 4).")
    print("3. Compare Ropelength: Higher ropelength roughly implies higher Möbius energy.")

if __name__ == "__main__":
    main()