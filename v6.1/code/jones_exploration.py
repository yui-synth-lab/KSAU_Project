import numpy as np
import pandas as pd
import ksau_config
from sklearn.linear_model import LinearRegression

def parse_polynomial(poly_str):
    """
    Parses polynomial vector string like "[-1, 2, -1]" or dictionary format.
    Returns a list of coefficients. 
    Note: KnotInfo format varies. This is a robust parser attempt.
    """
    if pd.isna(poly_str):
        return []
    
    # Handle string representation of list
    try:
        # Remove brackets and split
        clean_str = str(poly_str).replace('[', '').replace(']', '').replace('{', '').replace('}', '')
        if not clean_str:
            return []
        
        # Split by comma
        parts = clean_str.split(',')
        coeffs = [float(p) for p in parts]
        return coeffs
    except:
        return []

def evaluate_jones(coeffs, t_val):
    """
    Evaluates Jones polynomial at t = t_val.
    Coeffs are usually centered or indexed. 
    KnotInfo often lists coeffs from lowest power.
    We'll assume a standard ordering for exploration.
    """
    if not coeffs:
        return 0.0
    
    # Simple evaluation: sum(c_i * t^i)
    # We center the powers to avoid huge numbers if possible, but standard eval is fine for ratio.
    val = 0.0
    # Center the polynomial roughly
    offset = -len(coeffs) // 2
    
    for i, c in enumerate(coeffs):
        power = i + offset
        val += c * (t_val ** power)
    
    return abs(val)

def analyze_jones_correlation():
    print("="*80)
    print("KSAU v6.1 Exploration: Jones Polynomial Analysis")
    print("Searching for hidden correlations in Jones evaluations at roots of unity.")
    print("="*80)

    # 1. Load Data
    topo_assignments = ksau_config.load_topology_assignments()
    phys_constants = ksau_config.load_physical_constants()
    ckm_exp = np.array(phys_constants['ckm']['matrix'])
    
    # Load raw link data for Jones coefficients
    link_csv = ksau_config.load_linkinfo_path()
    df_l = pd.read_csv(link_csv, sep='|', skiprows=[1])
    
    # Map particle names to Jones coeffs
    jones_map = {}
    key_map = {
        'u': 'Up', 'c': 'Charm', 't': 'Top',
        'd': 'Down', 's': 'Strange', 'b': 'Bottom'
    }
    
    print("Extracting Jones Polynomials...")
    for k, name in key_map.items():
        topo_name = topo_assignments[name]['topology']
        # Find row
        row = df_l[df_l['name'] == topo_name]
        if row.empty:
            print(f"Warning: {name} ({topo_name}) not found in DB.")
            jones_map[k] = []
            continue
            
        poly_str = row.iloc[0]['jones_polynomial_vector'] # Adjust column name if needed
        # In LinkInfo, column might be 'jones_polynomial' or similar. 
        # Based on previous file reads, it was 'jones_polynomial_vector' (col 17 in knots, check links)
        # Let's check columns if needed. Assuming 'jones_polynomial_vector' exists.
        
        coeffs = parse_polynomial(poly_str)
        jones_map[k] = coeffs
        print(f"  {name:<8}: {len(coeffs)} coeffs")

    # 2. Test different roots of unity (t = exp(i * theta))
    test_phases = {
        'pi/2 (i)': np.pi/2,
        'pi/3': np.pi/3,
        'pi/4': np.pi/4,
        'pi/6': np.pi/6,
        '2pi/5': 2*np.pi/5
    }

    best_r2 = -1
    best_phase = ""
    
    for label, theta in test_phases.items():
        t_val = np.exp(1j * theta)
        
        data_points = []
        
        up_type = ['u', 'c', 't']
        down_type = ['d', 's', 'b']
        
        for i, u_k in enumerate(up_type):
            for j, d_k in enumerate(down_type):
                u_j = evaluate_jones(jones_map[u_k], t_val)
                d_j = evaluate_jones(jones_map[d_k], t_val)
                
                exp_val = ckm_exp[i, j]
                log_exp = np.log(exp_val)
                
                # Metric: Difference in Jones evaluation (Log ratio if magnitudes)
                # Hypothesis: Transition depends on topological similarity J_u ~ J_d
                # Try absolute difference of magnitudes
                d_jones = abs(u_j - d_j)
                
                # Also try Ratio
                if d_j != 0:
                    r_jones = abs(np.log(u_j / d_j))
                else:
                    r_jones = 0
                
                # We use d_jones for now
                data_points.append([log_exp, d_jones])
        
        # Regression
        data = np.array(data_points)
        y = data[:, 0]
        x = data[:, 1]
        
        # Simple Linear Regression
        model = LinearRegression().fit(x.reshape(-1, 1), y)
        r2 = model.score(x.reshape(-1, 1), y)
        
        print(f"Phase {label:<8}: R^2 = {r2:.4f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_phase = label

    print("-" * 60)
    print(f"Best Correlation found at: {best_phase} (R^2 = {best_r2:.4f})")
    
    # =========================================================================
    # PART 3: HYBRID MODEL TEST (Volume + Jones(2pi/5))
    # =========================================================================
    print("\n" + "="*80)
    print("HYBRID MODEL TEST: Volume + Quantum Topology")
    print("Testing Ansatz: ln|V_ij| = a * dVol + b * dJones(2pi/5) + c")
    print("-" * 80)
    
    # 1. Prepare Data for Hybrid Regression
    # We need to re-loop or store data better. Let's re-loop for clarity with 2pi/5.
    target_theta = 2 * np.pi / 5
    t_val = np.exp(1j * target_theta)
    
    # Get Volume Data
    quarks_vol = {}
    for k, name in key_map.items():
        quarks_vol[k] = topo_assignments[name]['volume']

    hybrid_data = []
    
    up_type = ['u', 'c', 't']
    down_type = ['d', 's', 'b']
    
    for i, u_k in enumerate(up_type):
        for j, d_k in enumerate(down_type):
            # Volume Diff
            d_vol = abs(quarks_vol[u_k] - quarks_vol[d_k])
            
            # Jones Diff (Absolute diff of magnitudes at 2pi/5)
            u_j = evaluate_jones(jones_map[u_k], t_val)
            d_j = evaluate_jones(jones_map[d_k], t_val)
            d_jones = abs(u_j - d_j)
            
            # Log Exp Value
            exp_val = ckm_exp[i, j]
            log_exp = np.log(exp_val)
            
            hybrid_data.append([log_exp, d_vol, d_jones])
            
    # 2. Perform Multiple Regression
    H = np.array(hybrid_data)
    y_h = H[:, 0]
    X_h = H[:, 1:3] # Col 1 (dVol) and Col 2 (dJones)
    
    model_h = LinearRegression().fit(X_h, y_h)
    r2_h = model_h.score(X_h, y_h)
    
    coeffs = model_h.coef_
    intercept = model_h.intercept_
    
    print(f"Hybrid Model Result (Phase 2pi/5):")
    print(f"  R-squared: {r2_h:.4f}")
    print(f"  Equation : ln|V| = {coeffs[0]:.4f} * dVol + {coeffs[1]:.4f} * dJones + {intercept:.4f}")
    
    # Compare with Volume Only
    # Re-calc pure volume R2 on this dataset for fairness
    X_vol = H[:, 1].reshape(-1, 1)
    model_vol = LinearRegression().fit(X_vol, y_h)
    r2_vol = model_vol.score(X_vol, y_h)
    
    print(f"  (Baseline Volume-Only R^2: {r2_vol:.4f})")
    print(f"  Improvement: +{r2_h - r2_vol:.4f}")
    
    if r2_h > 0.6:
        print("\nSUCCESS: Quantum Topology significantly enhances the model!")
        print("The 'Generation Penalty' is likely a Jones Polynomial interference effect.")
    else:
        print("\nRESULT: Improvement is marginal. Jones polynomial is not the sole missing factor.")

    print("="*80)

if __name__ == "__main__":
    analyze_jones_correlation()
