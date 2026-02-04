"""
KSAU Search for True Generation 4 Candidate.

Criteria:
1. Genus (3-Genus) = 4
2. Alexander Span = 8 (Strict equality condition of KSAU)

Goal: Find the knot with minimal crossing number satisfying both.
"""

import pandas as pd
import re
from typing import Any, List

CSV_PATH = "KSAU/knotinfo_data_complete.csv"

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
            try: exps.append(int(m.group(1)))
            except: pass
    if not exps:
        if "t" in s and "t^" not in s: exps.extend([1, 0])
        return 0
    return max(exps) - min(exps)

def read_knotinfo(csv_path: str) -> pd.DataFrame:
    attempts = [dict(sep="|", header=[0, 1]), dict(sep="|", header=0), dict(sep=",", header=0)]
    for kwargs in attempts:
        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False, **kwargs)
            if "name" in df.columns: df = df.set_index("name")
            else: df = df.set_index(df.columns[0])
            # Check if we have some data
            if len(df) > 100: return df
        except: continue
    raise RuntimeError("Failed to load CSV")

def main():
    print("Loading data...")
    df = read_knotinfo(CSV_PATH)
    print(f"Loaded {len(df)} knots.")
    
    candidates = []
    
    print("Searching for True Gen 4 (Genus=4, Span=8)...")
    
    for name, row in df.iterrows():
        # 1. Check Genus = 4
        genus_val = _try_get(row, ["three_genus", "Genus-3D"])
        if _is_empty(genus_val): continue
        try:
            g = int(float(genus_val))
        except: continue
            
        if g != 4: continue
        
        # 2. Check Span = 8
        alex_str = _try_get(row, ["alexander_polynomial", "Alexander"])
        span = parse_poly_span(alex_str)
        
        if span == 8:
            # Found one!
            crossing = _try_get(row, ["crossing_number", "Crossing Number"])
            sym_type = _try_get(row, ["symmetry_type", "Symmetry Type"])
            try: n_cross = int(crossing)
            except: n_cross = 999
            
            candidates.append({
                "Knot": name,
                "Crossing": n_cross,
                "Symmetry": sym_type,
                "Poly": alex_str[:30] + "..." if len(str(alex_str))>30 else alex_str
            })
            
    if not candidates:
        print("No candidates found in this dataset.")
        return
        
    # Convert to DataFrame and sort by Crossing
    res_df = pd.DataFrame(candidates).sort_values(by="Crossing")
    
    print(f"\nFound {len(res_df)} candidates.")
    print("Top 10 Simplest Candidates:")
    print(res_df.head(10).to_string(index=False))
    
    # Analyze best candidate
    best = res_df.iloc[0]
    print(f"\n[Conclusion]\n")
    print(f"The true KSAU 4th generation candidate is: {best['Knot']} (N={best['Crossing']})")
    
    # Check for Amphicheirality in top candidates
    amphi_cands = res_df[res_df['Symmetry'].str.contains("amphicheiral", case=False, na=False)]
    if not amphi_cands.empty:
        best_amphi = amphi_cands.iloc[0]
        print(f"Nearest Amphicheiral Candidate: {best_amphi['Knot']} (N={best_amphi['Crossing']})")
    else:
        print("No Amphicheiral candidates found among Span=8 knots (in this dataset).")

if __name__ == "__main__":
    main()
