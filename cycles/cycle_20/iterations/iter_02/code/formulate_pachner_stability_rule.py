import sys
from pathlib import Path
import json
import pandas as pd
import math

# SSOT Setup
current_file = Path(__file__).resolve()
project_root = current_file.parents[5]
ssot_path = project_root / "ssot"
sys.path.insert(0, str(ssot_path))    
from ksau_ssot import SSOT

def evaluate_pachner_rule():
    ssot = SSOT()
    math_consts = ssot.constants().get("mathematical_constants", {})
    assignments = ssot.topology_assignments()
    k_res = math_consts.get("k_resonance", 24)
    
    print("### Pachner Move Stability Rule Evaluation (K=%d) ###\n" % k_res)
    
    # Rule Evaluation
    results = []
    for p, data in assignments.items():
        n = data.get("crossing_number")
        c = data.get("components")
        
        # Proposed Rule:
        # 1. c=1 (Knots) -> n < 8 (Leptons)
        # 2. c>=2 (Links) -> n >= 8 (Quarks/Bosons)
        
        if c == 1:
            classification = "Lepton (Knot)"
            rule_match = (n < 8)
        else:
            classification = "Quark/Boson (Link)"
            rule_match = (n >= 8)
            
        results.append({
            "particle": p,
            "n": n,
            "c": c,
            "class": classification,
            "rule_match": rule_match
        })
        
    df = pd.DataFrame(results)
    print(df[["particle", "n", "c", "class", "rule_match"]].to_string(index=False))
    
    success_rate = df["rule_match"].mean() * 100
    print("\nRule Success Rate: %.1f%%" % success_rate)
    
    print("\n### Formal Rule Definition ###")
    print("1. Stability Constraint (c=1): n < 8. Knots with n < 8 are topologically stable (Leptons).")
    print("2. Resonance Constraint (c>=2): n >= 8. Links with n >= 8 are dynamic (Quarks/Bosons).")
    print("3. Saturation Principle: The maximum stable complexity for links in the 24-cell vacuum is n=11.")

if __name__ == "__main__":
    evaluate_pachner_rule()
