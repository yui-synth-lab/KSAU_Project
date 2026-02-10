import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def verify_holographic_gravity():
    print("="*60)
    print("KSAU v6.3: Holographic Gravity Verification")
    print("="*60)
    
    # 1. Load Data & Constants
    knots, links = utils_v61.load_data()
    consts = utils_v61.load_constants()
    
    # Universal Mass Law Parameters from v6.0 data
    # ln(m) = A * V + C
    kappa = consts['kappa']
    A_theo = 10 * kappa 
    C_theo = -(7 + 7 * kappa)
    
    # Combine datasets
    data = pd.concat([knots, links], ignore_index=True)
    
    # 2. Extract Geometric Metrics
    # We need Volume and Cusp Area.
    # Cusp Area A = |Meridian * Longitude| ? No.
    # For a standard cusp torus, Area = |M| * |L| * sin(theta).
    # Since we don't have theta, we approximate Area ~ |M| * |L|.
    # Or simply use "Maximum Cusp Volume" as a proxy? No, that's volume.
    
    # Let's use the available length data.
    # Columns: meridian_length, longitude_length
    
    data['vol'] = pd.to_numeric(data['volume'], errors='coerce')
    data['ml'] = pd.to_numeric(data['meridian_length'], errors='coerce')
    data['ll'] = pd.to_numeric(data['longitude_length'], errors='coerce')
    
    # Filter valid entries
    valid = data[
        (data['vol'] > 0) & 
        (data['ml'] > 0) & 
        (data['ll'] > 0)
    ].copy()
    
    print(f"Valid geometric entries: {len(valid)}")
    
    # Calculate Cusp Area Approximation
    # A ~ M * L
    valid['area'] = valid['ml'] * valid['ll']
    
    # 3. Analyze Volume-Area Scaling
    # Hypothesis: S_BH ~ Area. Mass m ~ exp(Vol).
    # Critical Limit: When Information density saturates.
    # Check the ratio R = Area / Volume.
    # Does it converge to a universal constant "4G"?
    
    valid['ratio'] = valid['area'] / valid['vol']
    
    ratio_mean = valid['ratio'].mean()
    ratio_std = valid['ratio'].std()
    
    print(f"\n[Geometric Ratio R = Area / Volume]")
    print(f"  Mean: {ratio_mean:.4f}")
    print(f"  Std:  {ratio_std:.4f}")
    print(f"  Min:  {valid['ratio'].min():.4f}")
    print(f"  Max:  {valid['ratio'].max():.4f}")
    
    # 4. Derive Planck Scale from Saturation
    # If Mass m = exp(k * V)
    # And Entropy S = Area / 4G_geom
    # At the Black Hole limit, ln(m) ~ S (Mass is Entropy).
    # k * V_crit = Area_crit / 4G_geom
    # k * V_crit = R_mean * V_crit / 4G_geom
    # This implies k = R_mean / 4G_geom is a constant identity?
    
    # Let's flip it. We know G_N (Newton).
    # We want to derive it from the geometry.
    # Let's assume the "KSAU Gravity" is defined by this ratio R.
    # G_ksau = 1 / R_mean? Or R_mean itself?
    
    # Let's look at the Planck Mass M_P in our scaling.
    # M_P ~ 1.2e19 GeV ~ 1.2e22 MeV.
    # ln(M_P) ~ 50.8
    # Using previous scaling (k ~ 1.3): V_P ~ 45.
    
    # If the Volume is limited by Area Saturation.
    # Is there a maximum possible Area for a knot?
    # Or does the ratio R change as V increases?
    
    print("\n[Scaling Analysis]")
    # Bin by volume to see if Ratio evolves
    valid['vol_bin'] = pd.cut(valid['vol'], bins=10)
    grouped = valid.groupby('vol_bin', observed=True)['ratio'].mean()
    print(grouped)
    
    # 5. Testing the "Information Saturation"
    # If R = Area/Vol decreases as V increases, then eventually Area cannot support the Volume information.
    # Let's simulate V -> infinity (or V -> 45).
    # Linear regression of Ratio vs Volume.
    
    from sklearn.linear_model import LinearRegression
    X = valid['vol'].values.reshape(-1, 1)
    y = valid['ratio'].values
    
    reg = LinearRegression().fit(X, y)
    slope = reg.coef_[0]
    intercept = reg.intercept_
    
    print(f"\n[Trend Analysis]")
    print(f"  Ratio(V) = {slope:.4f} * V + {intercept:.4f}")
    
    if slope < 0:
        print("  Observation: The Surface-to-Volume ratio DECREASES as Volume increases.")
        print("  This implies a 'Holographic Bound'.")
        
        # Calculate Critical Volume where Ratio hits a limit?
        # Maybe where Area grows slower than required for entropy?
        # Standard BH: S ~ M^2.
        # Here: ln M ~ V. So S ~ (e^V)^2 = e^{2V}.
        # But Area ~ V (roughly constant ratio).
        # So Area grows linearly, but Entropy demand grows exponentially!
        # This is the clash.
        
        # Critical Point:
        # Area_available = Area_required
        # R_mean * V = alpha * exp(2*V) ? No, that happens immediately.
        
        # Let's assume the standard BH relation S = A/4G holds at the Planck scale.
        # But for particles (KSAU), S_particle ~ V.
        # Saturation: S_particle = S_BH
        # V_crit = (R_mean * V_crit) / 4G_eff ?? No.
        
        # Correct Logic:
        # Particle regime: Mass ~ exp(V). Entropy is low.
        # Black Hole regime: Mass ~ sqrt(Area). Entropy is Area/4G.
        # Crossover (Planck Scale): The two laws meet.
        # M_P ~ exp(V_P) AND M_P ~ sqrt(Area_P) ~ sqrt(R * V_P).
        # exp(V_P) = C * sqrt(V_P)
        # This equation determines V_P!
        
        print("\n[Deriving Planck Volume V_P]")
        print("  Condition: exp(A_theo * V_P) = sqrt(R_mean * V_P)")
        # A_theo ~ 1.3085 (Universal Mass Slope)
        # R_mean ~ (Calculated from data)
        # Solve for V_P.
        
        # Actually, standard units matter here.
        # Let's assume natural units where prefactors are O(1).
        # exp(A_theo * V) = sqrt(V).
        # This has no solution for V > 0 (exp grows faster).
        # Unless the BH mass scaling is different in "Knot Space".
        
        # Re-evaluate:
        # Maybe the saturation is simply V_max ~ 1/slope?
        # If Ratio -> 0.
        v_limit = -intercept / slope
        print(f"  Projected Geometric Limit (Ratio -> 0): V_limit = {v_limit:.4f}")
        
    else:
        print("  Ratio is constant or increasing. No obvious saturation.")

if __name__ == "__main__":
    verify_holographic_gravity()
