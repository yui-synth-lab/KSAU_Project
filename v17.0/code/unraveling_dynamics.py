import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import odeint

# ============================================================================
# KSAU v17.0: Topological Unraveling & Dark Matter Tension Simulator
# ============================================================================
# [PHASE 1 UPDATED 2026-02-17]: KSAU PARAMETER CONNECTED
# alpha (unraveling rate) is derived from fundamental constant kappa.
# ----------------------------------------------------------------------------
# Hypothesis:
# 1. The universe begins as a highly entangled 'Knot State' in 24D Leech Lattice.
# 2. Expansion (Inflation/Hubble Flow) acts as a 'Unraveling Force'.
# 3. Dark Matter is the 'Topological Tension' (Background Constraint).
# 4. alpha = kappa / (2*pi) = 1/48 (Stochastic unraveling probability).
# ============================================================================

class UnravelingUniverse:
    def __init__(self, omega_m0=0.31, omega_lambda0=0.69, h0=0.07):
        self.Omega_m0 = omega_m0
        self.Omega_L0 = omega_lambda0
        self.H0 = h0  # 1/Gyr approx (70 km/s/Mpc)
        
        # KSAU Constants
        self.kappa = np.pi / 24.0
        self.alpha_ksau = self.kappa / (2.0 * np.pi) # Result: 1/48 approx 0.02083
        
        self.conversion_efficiency = 0.1 # General placeholder for scaling

    def hubble_rate(self, a):
        """Standard LambdaCDM H(a) for comparison foundation."""
        return self.H0 * np.sqrt(self.Omega_m0 * a**(-3) + self.Omega_L0)

    def topological_tension_model(self, y, t, alpha, beta):
        """
        Differential equations for Topological Unraveling.
        y[0] = a(t) : Scale Factor
        y[1] = T(t) : Topological Tension (Background constraint proxy for DM)
        y[2] = M(t) : Relaxed Matter (Baryonic Matter density proxy)
        """
        a, T, M = y
        
        # Ensure non-negative densities for stability
        T = max(T, 0)
        M = max(M, 0)
        
        # Effective Density for Gravity
        rho_eff = T + M + self.Omega_L0 
        
        # Friedman 1: (da/dt)^2 ~ rho * a^2
        dadt = a * self.H0 * np.sqrt(rho_eff)
        
        # Unraveling Rate: Derived from KSAU alpha
        H = dadt / a
        unraveling_rate = alpha * H * T 
        
        # Tension Equation: 1D defect scaling (a^-2) + Unraveling decay
        dTdt = -2 * H * T - unraveling_rate
        
        # Matter Equation: 3D fluid scaling (a^-3) + Unraveling replenishment
        dMdt = -3 * H * M + unraveling_rate
        
        return [dadt, dTdt, dMdt]

    def run_simulation(self, steps=1000):
        t = np.linspace(0.001, 15, steps) # Time in arbitrary units (~Gyr)
        
        # Initial Conditions (Early Universe)
        a0 = 0.001
        T0 = 10.0 # High initial tension (Dark Matter dominated)
        M0 = 0.0  # Zero baryons initially (all trapped in knots)
        
        # Use derived KSAU alpha
        alpha = self.alpha_ksau
        beta = 0.0
        
        sol = odeint(self.topological_tension_model, [a0, T0, M0], t, args=(alpha, beta))
        
        results = pd.DataFrame({
            'Time': t,
            'ScaleFactor': sol[:, 0],
            'Tension_DM': sol[:, 1],
            'Matter_Baryon': sol[:, 2]
        })
        
        results['Redshift'] = (1 / results['ScaleFactor']) - 1
        results['Total_Density'] = results['Tension_DM'] + results['Matter_Baryon']
        results['DM_Fraction'] = results['Tension_DM'] / results['Total_Density']
        
        return results

if __name__ == "__main__":
    print("Initializing KSAU v17.0 Topological Unraveling Simulation...")
    sim = UnravelingUniverse()
    df = sim.run_simulation()
    
    print(f"\nSimulation Complete using KSAU alpha = {sim.alpha_ksau:.6f} (1/48)")
    print("\nSnapshot at t_final:")
    print(df.iloc[-1])
    
    print("\nKSAU Phase 1 Scaling Analysis:")
    print(f"Initial DM Fraction: {df.iloc[0]['DM_Fraction']:.4f}")
    print(f"Final DM Fraction:   {df.iloc[-1]['DM_Fraction']:.4f}")
    
    # Save results
    df.to_csv('v17.0/data/unraveling_simulation_results.csv', index=False)
    print("\nData saved to v17.0/data/unraveling_simulation_results.csv")
