import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add v6.0 code path for config
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.0/code'))
import ksau_config

def simulate_topological_gravity():
    print("="*60)
    print("KSAU v6.6: Gravity as Network Resource Gradient")
    print("="*60)
    
    # 1. Load Data
    consts = ksau_config.load_physical_constants()
    topo = ksau_config.load_topology_assignments()
    
    # Use Top Quark as the central mass for this local simulation
    m_top = topo['Top']['observed_mass']
    v_top = topo['Top']['volume']
    c_top = topo['Top']['crossing_number']
    
    # Complexity density at the center
    # rho_c = CrossingNumber / Volume
    comp_density = c_top / v_top
    print(f"Central Source: Top Quark (V={v_top:.2f}, C={c_top})")
    print(f"Calculated Complexity Density: {comp_density:.4f}")
    
    os.makedirs('v6.6/figures', exist_ok=True)
    
    # 2. Create Space
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    
    # 3. Resource Density rho_u (Update availability)
    # The presence of mass (complexity density) "drains" the network ticks
    R = np.sqrt(X**2 + Y**2)
    # We use a Gaussian well proportional to the complexity density
    drain_strength = 0.5 * (comp_density / 1.0) # Scaling for viz
    rho_u = 1.0 - drain_strength * np.exp(-R**2 / (2 * 2**2))
    
    # 4. Trajectory Simulation (Geodesic)
    pos = np.array([-8.0, 3.5])
    vel = np.array([1.5, 0.0]) 
    dt = 0.1
    path = [pos.copy()]
    
    # Max steps
    for _ in range(200):
        r = np.linalg.norm(pos)
        if r < 0.1: break
        
        # Current local update density
        local_rho = 1.0 - drain_strength * np.exp(-r**2 / 8)
        
        # Gradient of rho_u (Refractive Force)
        # grad(rho_u) = rho_u * (r/sigma^2)
        force_mag = 2.0 * drain_strength * r * np.exp(-r**2 / 8)
        acc = -force_mag * (pos / r)
        
        vel += acc * dt
        
        # Constraint: Velocity magnitude is limited by local update density (c = rho_u)
        v_norm = np.linalg.norm(vel)
        if v_norm > 0:
            # Maximum allowed speed at this point in the network
            c_local = 1.5 * local_rho 
            vel = (vel / v_norm) * c_local
        
        pos += vel * dt
        path.append(pos.copy())
        
        if np.abs(pos[0]) > 12 or np.abs(pos[1]) > 12: break
    
    path = np.array(path)
    
    # 5. Plotting
    plt.figure(figsize=(10, 8))
    plt.contourf(X, Y, rho_u, levels=20, cmap='inferno')
    plt.colorbar(label='Network Update Density ($rho_u$)')
    plt.plot(path[:,0], path[:,1], 'w-', linewidth=2, label='Topological Geodesic')
    plt.scatter([0], [0], color='cyan', s=200, label='Top Quark Source')
    
    plt.title('KSAU v6.6: Gravitational Refraction (Data-Driven)', fontsize=14)
    plt.xlabel('X (Volume Units)')
    plt.ylabel('Y (Volume Units)')
    plt.legend()
    plt.grid(True, alpha=0.2)
    
    plt.savefig('v6.6/figures/topological_gravity_bending.png')
    print("\nSimulation saved to: v6.6/figures/topological_gravity_bending.png")

if __name__ == "__main__":
    simulate_topological_gravity()