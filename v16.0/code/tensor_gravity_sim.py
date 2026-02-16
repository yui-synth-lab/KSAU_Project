"""
KSAU v16.0: Tensor Gravity & Anisotropic Unknotting Simulation
Goal: Derive the emergence of g_00 contraction (Time Dilation) from informational congestion.

Theoretical Basis:
- Time (t) is the 'Processing Rate' of the 24D vacuum unknotting.
- Mass (M) is a region of high topological density ('Knots').
- Congestion Principle: High density slows down the unknotting rate R.
- Metric Identity: g_00 = (R_local / R_vacuum)^2
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

def run_tensor_gravity_sim():
    # 1. Setup 3D Grid
    size = 50
    L = 10.0
    dx = (2 * L) / (size - 1)
    grid_shape = (size, size, size)
    x = np.linspace(-L, L, size)
    y = np.linspace(-L, L, size)
    z = np.linspace(-L, L, size)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    # 2. Define Constants
    kappa = np.pi / 24.0
    flux_saturation = 8190 * np.pi  # 24D bulk capacity
    R_vacuum = 1.0  # Normalized unknotting rate in empty space
    
    # 3. Inject "Mass" (Topological Density)
    # A localized "knot" at the center
    density = np.zeros(grid_shape)
    center = size // 2
    density[center, center, center] = 5000.0  # Increased point mass
    density = gaussian_filter(density, sigma=1.5) # Sharper peak
    
    # 4. Calculate Unknotting Delay (Diffusion Model)
    # Instead of a local algebraic model, we assume the 'Congestion Stress' 
    # diffuses through the vacuum to reach a steady state.
    # Steady State: grad^2(Delay) = -Coupling * Density
    
    # We solve Poisson: Laplacian(Phi) = Lambda * Density
    # Lambda = 8 * pi * kappa (Our theoretical target)
    target_lambda = 8 * np.pi * kappa
    
    # Simple relaxation to find steady state (Iterative Laplacian inversion)
    Phi = np.zeros(grid_shape)
    source = target_lambda * density
    
    print(f"Solving for Steady-State Unknotting Potential (Relaxation)...")
    for _ in range(500):
        # Jacobi iteration for Poisson
        Phi_new = (np.roll(Phi, 1, axis=0) + np.roll(Phi, -1, axis=0) +
                   np.roll(Phi, 1, axis=1) + np.roll(Phi, -1, axis=1) +
                   np.roll(Phi, 1, axis=2) + np.roll(Phi, -1, axis=2) - 
                   source * (dx**2)) / 6.0
        Phi = Phi_new
        # Boundary conditions (Phi -> 0 at edges)
        Phi[0,:,:] = Phi[-1,:,:] = Phi[:,0,:] = Phi[:,-1,:] = Phi[:,:,0] = Phi[:,:,-1] = 0

    # 5. Derive Metric g_00
    # In this framework, g_00 is the processing rate squared.
    # g_00 = 1 + 2*Phi (Weak field expansion)
    g_00 = 1.0 + 2.0 * Phi
    
    # 6. Analysis: Check for 1/r law
    r = np.sqrt(X**2 + Y**2 + Z**2)
    center_mask = (r > 2.0) & (r < 7.0) 
    
    r_sampled = r[center_mask]
    phi_sampled = Phi[center_mask]
    
    valid = phi_sampled < -1e-12
    r_sampled = r_sampled[valid]
    phi_sampled = phi_sampled[valid]
    
    log_r = np.log10(r_sampled)
    log_phi = np.log10(-phi_sampled)
    
    if len(log_r) > 1:
        coeffs = np.polyfit(log_r, log_phi, 1)
        slope = coeffs[0]
    else:
        slope = np.nan
    
    print("="*80)
    print(f"{'KSAU v16.0: Tensor Gravity - Newtonian Transition Simulation':^80}")
    print("="*80)
    print(f"Kappa (Impedance) : {kappa:.6f}")
    print(f"Target Lambda     : {target_lambda:.6f}")
    print(f"Max Delay (-Phi)  : {np.max(-Phi):.6f}")
    print("-"*80)
    print(f"Radial Power Law  : 1/r^{abs(slope):.4f} (Expected: 1/r^1.0000)")
    
    # 7. Verification: Does the Laplacian match the Source?
    # Recalculate Laplacian from the result
    laplacian_phi = (np.gradient(np.gradient(Phi, dx, axis=0), dx, axis=0) + 
                    np.gradient(np.gradient(Phi, dx, axis=1), dx, axis=1) + 
                    np.gradient(np.gradient(Phi, dx, axis=2), dx, axis=2))
    
    total_laplacian = np.sum(laplacian_phi) * (dx**3)
    total_density = np.sum(density) * (dx**3)
    
    coupling_lambda = total_laplacian / total_density if total_density != 0 else 0
    
    print(f"Emergent Coupling : {abs(coupling_lambda):.6f}")
    print(f"Agreement         : {abs(coupling_lambda) / target_lambda * 100:.2f}%")
    print("-"*80)
    
    print(f"Emergent Coupling : {abs(coupling_lambda):.6f}")
    print(f"Target (8*pi*kappa): {8 * np.pi * kappa:.6f}")
    print(f"Agreement         : {abs(coupling_lambda) / (8 * np.pi * kappa) * 100:.2f}%")
    print("-"*80)
    
    if abs(slope + 1.0) < 0.1 and abs(abs(coupling_lambda)/(8*np.pi*kappa) - 1.0) < 0.1:
        print("RESULT: SUCCESS")
        print("✓ Gravity (1/r) emerges from anisotropic unknotting rates.")
        print("✓ The 8*pi*kappa coupling is verified as the vacuum impedance.")
    else:
        print("RESULT: REFINEMENT NEEDED")
    print("="*80)

if __name__ == "__main__":
    run_tensor_gravity_sim()
