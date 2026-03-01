import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_arrow_of_time():
    print("="*60)
    print("KSAU v6.4: The Arrow of Time (Topological Entropy)")
    print("="*60)
    
    os.makedirs('v6.4/figures', exist_ok=True)
    
    # 1. Timeline: From Big Bang to Future
    states = [
        ("Master Link", 74, 45),
        ("GUT Scale", 50, 35),
        ("Baryogenesis", 30, 25),
        ("Standard Model", 12, 15),
        ("Late Universe", 4, 100),
        ("Heat Death", 0.1, 1000)
    ]
    
    times = np.arange(len(states))
    complexities = [s[1] for s in states]
    volumes = [s[2] for s in states]
    
    entropies = [np.log(v/c) for c, v in zip(complexities, volumes)]
    
    # 2. Plotting
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_xlabel('Cosmological Evolution (Topological Steps)')
    ax1.set_ylabel('Complexity (Crossing Number C)', color='tab:red')
    ax1.plot(times, complexities, 'o--', color='tab:red', label='Complexity C')
    ax1.tick_params(axis='y', labelcolor='tab:red')
    
    ax2 = ax1.twinx()
    ax2.set_ylabel('Topological Entropy S = ln(V/C)', color='tab:blue')
    ax2.plot(times, entropies, 's-', color='tab:blue', label='Entropy S', linewidth=3)
    ax2.tick_params(axis='y', labelcolor='tab:blue')
    
    plt.title('The Arrow of Time: Complexity Decay vs Entropy Growth')
    fig.tight_layout()
    
    # 3. Output
    print(f"{'Era':<15} | {'Complexity C':<12} | {'Entropy S':<10}")
    print("-" * 45)
    for i, s in enumerate(states):
        print(f"{s[0]:<15} | {s[1]:<12} | {entropies[i]:<10.4f}")
        
    delta_s = entropies[3] - entropies[0]
    p_reverse = np.exp(-delta_s)
    print(f"\n[Irreversibility Check]")
    print(f"  Entropy Gain (Master -> current): {delta_s:.4f}")
    print(f"  Probability of Spontaneous Re-knotting: {p_reverse:.4e}")
    
    plt.savefig('v6.4/figures/arrow_of_time_entropy.png')
    print("\nGraph saved to v6.4/figures/arrow_of_time_entropy.png")

if __name__ == "__main__":
    simulate_arrow_of_time()