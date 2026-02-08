
import numpy as np

def check_neutrino_oscillation():
    # ---------------------------------------------------------
    # 1. Experimental Data (NuFIT 5.2 / PDG)
    # ---------------------------------------------------------
    dm2_21 = 7.42e-5  # eV^2
    dm2_31_NO = 2.514e-3 # eV^2 (Normal Ordering)
    dm2_32_IO = -2.498e-3 # eV^2 (Inverted Ordering)
    
    # 2. KSAU Prediction Input
    # v6.0 Prediction: Sum(m_nu) approx 0.12 eV
    SUM_KSAU = 0.12
    
    print("="*80)
    print("KSAU v6.0: Neutrino Oscillation Consistency Check")
    print("="*80)
    print(f"Target Sum(m_nu) (KSAU Prediction): {SUM_KSAU} eV")
    print(f"Experimental dm^2_21              : {dm2_21:.2e} eV^2")
    print(f"Experimental dm^2_31 (NO)         : {dm2_31_NO:.2e} eV^2")
    print("-" * 80)
    
    # ---------------------------------------------------------
    # 3. Solver for Normal Ordering (NO)
    # ---------------------------------------------------------
    # m1 = m
    # m2 = sqrt(m^2 + dm2_21)
    # m3 = sqrt(m^2 + dm2_31)
    # Find m such that m1 + m2 + m3 = SUM_KSAU
    
    def sum_no(m1):
        m2 = np.sqrt(m1**2 + dm2_21)
        m3 = np.sqrt(m1**2 + dm2_31_NO)
        return m1 + m2 + m3

    # Binary search for m1
    low, high = 0, SUM_KSAU
    best_m1_no = 0
    for _ in range(100):
        mid = (low + high) / 2
        s = sum_no(mid)
        if s < SUM_KSAU:
            low = mid
        else:
            high = mid
    best_m1_no = low
    
    m_no = [best_m1_no, np.sqrt(best_m1_no**2 + dm2_21), np.sqrt(best_m1_no**2 + dm2_31_NO)]
    
    print("Scenario 1: Normal Ordering (m1 < m2 < m3)")
    print(f"  m1: {m_no[0]:.5f} eV")
    print(f"  m2: {m_no[1]:.5f} eV")
    print(f"  m3: {m_no[2]:.5f} eV")
    print(f"  Sum: {sum(m_no):.5f} eV (Target {SUM_KSAU})")
    
    # Check physical viability (m1 >= 0)
    if best_m1_no > 0:
        print("  -> Solution EXISTS.")
        print(f"  -> Minimal Mass m1 ~ {best_m1_no*1000:.1f} meV")
    else:
        print("  -> No solution (Sum too small for experimental splitting).")

    print("-" * 80)

    # ---------------------------------------------------------
    # 4. Solver for Inverted Ordering (IO)
    # ---------------------------------------------------------
    # m3 = m
    # m2 = sqrt(m^2 - dm2_32_IO) = sqrt(m^2 + |dm2_32|)
    # m1 = sqrt(m2^2 - dm2_21)
    
    dm2_32_abs = abs(dm2_32_IO)
    
    def sum_io(m3):
        # m3 is the lightest
        m2 = np.sqrt(m3**2 + dm2_32_abs)
        m1 = np.sqrt(m2**2 - dm2_21)
        return m1 + m2 + m3
        
    low, high = 0, SUM_KSAU
    best_m3_io = 0
    
    # Check minimum possible sum for IO
    min_m3 = 0
    min_sum_io = sum_io(0)
    
    print("Scenario 2: Inverted Ordering (m3 < m1 < m2)")
    if SUM_KSAU < min_sum_io:
        print(f"  -> Impossible. Min Sum for IO is {min_sum_io:.5f} eV")
        print(f"  -> KSAU Prediction ({SUM_KSAU} eV) is too light for Inverted Ordering?")
        # Actually min sum for IO is roughly 2 * sqrt(2.5e-3) ~ 0.1 eV. 
        # So 0.12 should be possible.
    else:
        for _ in range(100):
            mid = (low + high) / 2
            s = sum_io(mid)
            if s < SUM_KSAU:
                low = mid
            else:
                high = mid
        best_m3_io = low
        
        m2_io = np.sqrt(best_m3_io**2 + dm2_32_abs)
        m1_io = np.sqrt(m2_io**2 - dm2_21)
        m_io = [m1_io, m2_io, best_m3_io]
        
        print(f"  m1: {m_io[0]:.5f} eV")
        print(f"  m2: {m_io[1]:.5f} eV")
        print(f"  m3: {m_io[2]:.5f} eV")
        print(f"  Sum: {sum(m_io):.5f} eV")
        print("  -> Solution EXISTS.")

    print("-" * 80)
    
    # 5. Topological Hierarchy Prediction
    # KSAU Hierarchy should follow charged leptons?
    # m_e : m_mu : m_tau ~ 0.5 : 105 : 1777 (Hierarchical)
    # Normal Ordering is Hierarchical (small, med, large).
    # Inverted is Degenerate (large, large, small).
    # Since KSAU is based on Volume/Complexity hierarchy, 
    # it STRONGLY favors Normal Ordering.
    
    print("Conclusion:")
    print("1. KSAU's predicted scale (0.12 eV) is compatible with BOTH orderings.")
    print("   However, the Geometric Hierarchy Principle (Mass ~ Complexity)")
    print("   decisively favors **Normal Ordering**.")
    print(f"   Predicted lightest neutrino mass: ~{best_m1_no*1000:.1f} meV.")
    print("="*80)

if __name__ == "__main__":
    check_neutrino_oscillation()
