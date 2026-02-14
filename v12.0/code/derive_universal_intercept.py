import numpy as np

def test_electron_geometric_origin():
    m_e_target = 0.510998950e6 # eV
    m_planck = 1.220910e28 # eV
    
    X_obs = np.log(m_planck / m_e_target)
    print(f"Observed X = {X_obs:.6f}")
    
    # Hypothesis: X = 16*pi + 4/pi
    X_pred = 16 * np.pi + 4 / np.pi
    print(f"Predicted X = {X_pred:.6f}")
    
    error = (X_pred / X_obs - 1) * 100
    print(f"Error in exponent: {error:+.4f}%")
    
    me_pred = m_planck * np.exp(-X_pred)
    print(f"\nPredicted m_e: {me_pred:.6e} eV")
    print(f"Target m_e:    {m_e_target:.6e} eV")
    print(f"Mass Error: {(me_pred/m_e_target - 1)*100:+.4f}%")

    # Another candidate: X = 51.528
    # 51.528 ~ 16.4 * pi
    # 16.4 = 82/5
    
    X_pred2 = 16.4 * np.pi
    print(f"\nPredicted X (82/5 * pi): {X_pred2:.6f}")
    me_pred2 = m_planck * np.exp(-X_pred2)
    print(f"Mass Error: {(me_pred2/m_e_target - 1)*100:+.4f}%")

if __name__ == "__main__":
    test_electron_geometric_origin()
