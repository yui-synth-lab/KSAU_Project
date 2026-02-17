import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================================
# KSAU v17.0: Jones Polynomial Unraveling Simulator
# ============================================================================
# Hypothesis:
# Topological Complexity C(K) decays as the universe expands.
# The decay rate is governed by alpha_ksau = 1/48.
# Complexity is proxied by the Crossing Number / Span of Jones Polynomial.
# ============================================================================

class JonesUnraveler:
    def __init__(self, steps=1000):
        self.steps = steps
        self.alpha_ksau = (np.pi / 24.0) / (2.0 * np.pi) # 1/48 approx 0.0208
        
    def expansion_model(self, t):
        """Simple power law expansion for matter dominated era a ~ t^(2/3)."""
        # t is in Gyr. t0 ~ 0.001
        return (t / 13.8)**(2/3) # Normalized to current age

    def complexity_evolution(self, t_range):
        """
        Evolve complexity C(t) according to dC/dt = -alpha * H * C
        Solution: C(t) = C0 * (a0/a(t))^alpha
        
        [AUDIT CORRECTION 2026-02-17]: 
        - a0 = 1e-6 (Initial scale factor at early universe/reheating)
        - a_final = 1.0 (Present day scale factor)
        - Expansion Factor = a_final / a0 = 10^6
        - C_final / C0 = (10^-6)^(1/48) = 10^(-0.125) approx 0.75
        """
        # Generate scale factor array
        a = self.expansion_model(t_range)
        
        # Initial Complexity (Early Universe High-Knot State)
        C0 = 100.0 
        
        # Define the base a0 as 1e-6 to represent a 10^6 expansion factor to present (a=1)
        a_initial_reference = 1e-6
        
        # C(t) scales as (a0 / a(t))^alpha
        C_t = C0 * (a_initial_reference / a)**self.alpha_ksau
        
        return a, C_t

    def simulate(self):
        t = np.linspace(0.01, 15.0, self.steps) # Gyr
        a, C = self.complexity_evolution(t)
        
        # Theoretical Comparison
        # What if alpha was 0 (Stable Knots)?
        C_stable = 100.0 * np.ones_like(t)
        
        # What if alpha was 1 (Rapid Decay)?
        # Use 1e-6 as reference (Initial Complexity = 100 at a=1e-6)
        C_rapid = 100.0 * (1e-6 / a)**1.0
        
        return t, a, C, C_stable, C_rapid

if __name__ == "__main__":
    print(f"KSAU Unraveling Simulation (alpha = 1/48)")
    sim = JonesUnraveler()
    t, a, C, C_stable, C_rapid = sim.simulate()
    
    # Total Retention from a=10^-6 to a=1.0
    total_retention = (1e-6 / 1.0)**sim.alpha_ksau * 100
    
    print(f"Total Cosmological Retention (a=10^-6 to a=1): {total_retention:.2f}%")
    print(f"Simulation Start (t=0.01Gyr) Complexity: {C[0]:.2f}")
    print(f"Simulation Final (t=15.0Gyr) Complexity: {C[-1]:.2f}")
    print(f"Retention over simulated interval: {C[-1]/C[0]*100:.2f}%")
    
    # Save data
    df = pd.DataFrame({'Time': t, 'ScaleFactor': a, 'Complexity': C})
    df.to_csv('v17.0/data/jones_scaling.csv', index=False)
    print("Data saved to v17.0/data/jones_scaling.csv")
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(t, C, 'b-', linewidth=2, label=f'KSAU Unraveling (alpha=1/48)')
    plt.plot(t, C_stable, 'k--', label='Stable Knots (alpha=0)')
    plt.plot(t, C_rapid, 'r:', label='Rapid Decay (alpha=1)')
    plt.xlabel('Time (Gyr)')
    plt.ylabel('Topological Complexity (Normalized)')
    plt.title('KSAU v17.0: Evolution of Topological Complexity')
    plt.legend()
    plt.grid(True)
    plt.savefig('v17.0/figures/jones_scaling.png')
    print("Plot saved to v17.0/figures/jones_scaling.png")
