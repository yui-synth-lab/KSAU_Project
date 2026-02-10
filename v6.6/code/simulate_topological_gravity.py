import numpy as np
import matplotlib.pyplot as plt
import os

def simulate_topological_gravity():
    print("="*60)
    print("KSAU v6.6: Gravity as Network Resource Gradient")
    print("="*60)
    
    os.makedirs('v6.6/figures', exist_ok=True)
    
    # 1. Create Space
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    
    # 2. Resource Density rho_u
    R = np.sqrt(X**2 + Y**2)
    rho_u = 1.0 - 0.8 * np.exp(-R**2 / (2 * 2**2))
    
    # 3. Trajectory
    pos = np.array([-8.0, 2.5])
    vel = np.array([1.5, 0.0]) 
    dt = 0.1
    path = [pos.copy()]
    
    for _ in range(150):
        r = np.linalg.norm(pos)
        if r > 0.1:
            force_mag = 4.0 * r * np.exp(-r**2 / 10)
            acc = -force_mag * (pos / r) 
        else:
            acc = np.zeros(2)
            
        vel += acc * dt
        local_rho = 1.0 - 0.8 * np.exp(-r**2 / 10)
        v_norm = np.linalg.norm(vel)
        if v_norm > 0:
            vel = (vel / v_norm) * (1.5 * local_rho)
        
        pos += vel * dt
        path.append(pos.copy())
    
    path = np.array(path)
    
    # 4. Plotting
    plt.figure(figsize=(10, 8))
    plt.contourf(X, Y, rho_u, levels=20, cmap='viridis')
    plt.colorbar(label='Network Update Density (Resource Availability)')
    plt.plot(path[:,0], path[:,1], 'w-', linewidth=2, label='Topological Geodesic')
    plt.scatter([0], [0], color='red', s=200, label='Mass (Resource Drain)')
    plt.title('KSAU v6.6: Gravity as Resource Refraction')
    plt.legend()
    
    plt.savefig('v6.6/figures/topological_gravity_bending.png')
    print("\nSimulation saved to: v6.6/figures/topological_gravity_bending.png")

if __name__ == "__main__":
    simulate_topological_gravity()