import numpy as np
import matplotlib.pyplot as plt

def run_tbd_simulation(dim=24, steps=10000, particles=100):
    """
    Simulates random walks in D-dimensions to observe the emergence 
    of a constant propagation velocity (Speed of Light c).
    """
    # Initialize particle positions
    positions = np.zeros((particles, dim))
    
    # Store history
    history_wavefront = []
    history_steps = []
    
    for tau in range(1, steps + 1):
        # Brownian step in D-dimensions
        steps_taken = np.random.normal(0, 1, (particles, dim))
        norms = np.linalg.norm(steps_taken, axis=1, keepdims=True)
        steps_taken = steps_taken / norms # Each jump is exactly length 1 (Planck length)
        
        positions += steps_taken
        
        if tau % 100 == 0:
            # We track the 99.9th percentile (the effective "Light Front")
            current_distances = np.linalg.norm(positions, axis=1)
            wavefront = np.percentile(current_distances, 99.9)
            history_wavefront.append(wavefront)
            history_steps.append(tau)
            
    return np.array(history_steps), np.array(history_wavefront)

def analyze_results(steps, dist, dim):
    # Velocity v = dD/dtau
    velocities = np.diff(dist) / np.diff(steps)
    emergent_c = np.mean(velocities[-10:])
    
    # In pure diffusion, dist ~ sqrt(tau) => dist^2 ~ tau
    # In wave propagation, dist ~ tau => dist^2 ~ tau^2
    
    plt.figure(figsize=(10, 10))
    
    # 1. Displacement Plot
    plt.subplot(3, 1, 1)
    plt.plot(steps, dist, 'b-', label=f"99.9th Percentile (D={dim})")
    plt.title("Spacetime Wavefront Propagation (TBD Model)")
    plt.ylabel("Distance R")
    plt.legend()
    plt.grid(True)
    
    # 2. Velocity Plot
    plt.subplot(3, 1, 2)
    plt.plot(steps[1:], velocities, 'g-')
    plt.axhline(y=emergent_c, color='r', linestyle='--', label=f"c_eff = {emergent_c:.4f}")
    plt.ylabel("v = dR/dtau")
    plt.title("Convergence to Invariant Speed c")
    plt.legend()
    plt.grid(True)
    
    # 3. Diffusion Power Law Analysis
    plt.subplot(3, 1, 3)
    plt.plot(np.log(steps), np.log(dist), 'm.', label="Simulation Data")
    # Linear fit in log-log space: log(R) = n*log(tau) + C
    slope, intercept = np.polyfit(np.log(steps), np.log(dist), 1)
    plt.plot(np.log(steps), slope*np.log(steps) + intercept, "k--", label=f"Slope n={slope:.4f}")
    plt.title("Propagation Mode (n=0.5: Diffusion, n=1.0: Wave)")
    plt.xlabel("log(tau)")
    plt.ylabel("log(R)")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("v8.0/figures/tbd_emergence_c.png")
    
    print("-" * 40)
    print(f"Dimension: {dim}")
    print(f"Emergent c (Wavefront): {emergent_c:.6f}")
    print(f"Propagation Power (n): {slope:.4f} (Ideal Diffusion: 0.5)")
    print(f"Effective Diffusion Const: { (dist[-1]**2) / (2 * dim * steps[-1]):.6f}")
    print(f"Kappa (pi/24): {np.pi/24:.6f}")
    print("-" * 40)

if __name__ == "__main__":
    import os
    if not os.path.exists("v8.0/figures"):
        os.makedirs("v8.0/figures")
        
    print("Starting Temporal Brownian Dynamics Simulation (v8.0)...")
    dim = 24
    steps, dist = run_tbd_simulation(dim=dim, steps=10000, particles=1000)
    analyze_results(steps, dist, dim)
