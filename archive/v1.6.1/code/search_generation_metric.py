"""
KSAU Generation Metric Search.

Goal: Find topological invariants 'X' such that:
  X(3_1) = 1
  X(6_3) = 2
  X(7_1) = 3

If found, search for knots with X(K) = 4 to predict the alternative 4th generation.
"""

import pandas as pd
from typing import Any, List, Dict

CSV_PATH = "KSAU/knotinfo_data_complete.csv"

TARGETS = {"3_1": 1, "6_3": 2, "7_1": 3}

def _is_empty(x: Any) -> bool:
    if x is None: return True
    if isinstance(x, float) and pd.isna(x): return True
    s = str(x).strip()
    return s in ("", "nan", "None")

def read_knotinfo(csv_path: str) -> pd.DataFrame:
    attempts = [dict(sep="|", header=[0, 1]), dict(sep="|", header=0), dict(sep=",", header=0)]
    for kwargs in attempts:
        try:
            df = pd.read_csv(csv_path, dtype=str, low_memory=False, **kwargs)
            if "name" in df.columns: df = df.set_index("name")
            else: df = df.set_index(df.columns[0])
            if "3_1" in df.index: return df
        except: continue
    raise RuntimeError("Failed to load CSV")

def main():
    print("Loading data...")
    df = read_knotinfo(CSV_PATH)
    
    # Identify candidate columns (exclude names, notations, and polynomial strings)
    # We look for columns that have integer values.
    
    candidate_cols = []
    
    # Check 3_1 row sample to filter columns
    row_3_1 = df.loc["3_1"]
    
    for col in df.columns:
        val = row_3_1[col]
        if _is_empty(val): continue
        if isinstance(val, str) and not val.replace("-", "").isdigit(): continue # Skip non-integers
        
        # Check if it matches Target 1 for 3_1
        try:
            v_int = int(val)
            if v_int == 1:
                candidate_cols.append(col)
        except: continue
        
    print(f"Initial scan: {len(candidate_cols)} columns have value '1' for 3_1.")
    
    # Filter by 6_3 (=2) and 7_1 (=3)
    matched_metrics = []
    
    for col in candidate_cols:
        try:
            v1 = int(df.loc["3_1"][col])
            v2 = int(df.loc["6_3"][col])
            v3 = int(df.loc["7_1"][col])
            
            if v1 == 1 and v2 == 2 and v3 == 3:
                matched_metrics.append(col)
        except: continue
        
    print(f"\nFound {len(matched_metrics)} metrics fitting the 1-2-3 pattern:")
    for m in matched_metrics:
        print(f" - {m}")
        
    # If metrics found, search for value 4
    if matched_metrics:
        print("\n=== Predicting 4th Generation based on these metrics ===")
        
        for metric in matched_metrics:
            print(f"\nMetric: {metric}")
            print(f"Searching for knots with {metric} = 4...")
            
            hits = []
            for name, row in df.iterrows():
                try:
                    val = int(row[metric])
                    if val == 4:
                        # Get Crossing Number for sorting
                        cross = 999
                        try: cross = int(row["crossing_number"] if "crossing_number" in row else row[df.columns[28]]) # rough fallback
                        except: pass
                        # Try to find specific crossing col
                        c_candidates = [c for c in df.columns if "crossing" in str(c).lower()]
                        if c_candidates and not _is_empty(row[c_candidates[0]]):
                            cross = int(row[c_candidates[0]])
                            
                        hits.append((name, cross))
                except: continue
            
            if hits:
                hits.sort(key=lambda x: x[1]) # Sort by crossing number
                print(f"Found {len(hits)} candidates. Top 5 simplest:")
                for h in hits[:5]:
                    print(f"  {h[0]} (N={h[1]})")
            else:
                print("No candidates found.")

if __name__ == "__main__":
    main()
