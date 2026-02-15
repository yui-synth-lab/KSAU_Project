import itertools

def search_geometric_decomposition():
    # KSAU Geometric Invariants
    invariants = {
        "Rank_G": 16,
        "Rank_V": 24,
        "Level": 41,
        "Sym_A5": 60
    }
    
    target_p = 1509
    target_q = 92
    target_ratio = target_p / target_q 
    
    print(f"Target Ratio: {target_ratio:.6f} (1509/92)")
    print("Searching for simple linear combinations of KSAU invariants...")
    
    basis = [16, 24, 41, 60]
    
    found_q = False
    for r in range(1, 5):
        for combo in itertools.combinations_with_replacement(basis, r):
            if sum(combo) == target_q:
                print(f"MATCH for denominator 92: {' + '.join(map(str, combo))} = 92")
                found_q = True
    
    if not found_q:
        print("Conclusion: 92 does NOT exhibit simple additive relationships with KSAU invariants.")

if __name__ == "__main__":
    search_geometric_decomposition()
