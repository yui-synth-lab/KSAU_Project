import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_network_clock():
    print("="*60)
    print("KSAU v6.5: Network Clock & The Speed of Light")
    print("="*60)
    
    os.makedirs('v6.5/figures', exist_ok=True)
    
    num_ticks = 20
    
    # Photon (C = 1)
    photon_pos = np.arange(num_ticks)
    
    # Electron (C = 11)
    electron_complexity = 11
    electron_pos = np.arange(num_ticks) / electron_complexity
    
    # Heavy Particle (C = 30)
    top_complexity = 30
    top_pos = np.arange(num_ticks) / top_complexity
    
    plt.figure(figsize=(10, 6))
    plt.plot(np.arange(num_ticks), photon_pos, 'y-o', label='Photon (c = 1.0)', linewidth=3)
    plt.plot(np.arange(num_ticks), electron_pos, 'b-s', label='Electron (v << c)')
    plt.plot(np.arange(num_ticks), top_pos, 'r-^', label='Heavy Particle (v ~ 0)')
    
    plt.title('KSAU v6.5: Topological Information Propagation', fontsize=14)
    plt.xlabel('Reidemeister Ticks (Universal Clock)', fontsize=12)
    plt.ylabel('Network Distance (Crossings)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    print(f"{'Tick':<6} | {'Photon Pos':<12} | {'Electron Pos':<12}")
    print("-" * 40)
    for i in range(0, num_ticks, 5):
        print(f"{i:<6} | {photon_pos[i]:<12.1f} | {electron_pos[i]:<12.2f}")

    c = 1.0 
    v_e = 1.0 / electron_complexity
    print(f"\n[Calculated Velocities]")
    print(f"  Light Speed (c): {c:.2f} (1.0 Crossing/Tick)")
    print(f"  Electron Velocity: {v_e:.4f} c")
    
    plt.savefig('v6.5/figures/causal_limit_simulation.png')
    print("\nSimulation saved to v6.5/figures/causal_limit_simulation.png")

if __name__ == "__main__":
    simulate_network_clock()