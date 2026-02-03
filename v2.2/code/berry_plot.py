import numpy as np
import matplotlib.pyplot as plt
import os

os.makedirs("figures", exist_ok=True)

print("=== KSAU v2.x Berry Phase & Spectrum Analysis ===")

# Seifert Matrices
V_strange = np.array([
    [-1, 1, -1, 0],
    [0, -1, 1, -1],
    [0, 0, 1, 0],
    [0, 0, -1, 1]
])

V_top = np.array([
    [0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0],
    [0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 0],
    [0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 1, -1, 0],
    [0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, -1, 1, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
])

def topological_hamiltonian(V, theta):
    w = np.exp(1j * theta)
    w_bar = np.exp(-1j * theta)
    # M = (1-w)V + (1-w_bar)V.T
    return (1 - w) * V + (1 - w_bar) * V.T

def calculate_signature(V, theta):
    H = topological_hamiltonian(V, theta)
    evals = np.linalg.eigvalsh(H)
    pos = np.sum(evals > 1e-6)
    neg = np.sum(evals < -1e-6)
    return pos - neg

def analyze_spectrum(V, name, label):
    # Avoid theta=0 singularity by shifting slightly
    # Loop from epsilon to 2pi - epsilon
    steps = 100
    epsilon = 0.01
    thetas = np.linspace(epsilon, 2*np.pi - epsilon, steps)
    eigenvalues = []
    ground_states = []

    for theta in thetas:
        H = topological_hamiltonian(V, theta)
        evals, evecs = np.linalg.eigh(H)
        eigenvalues.append(evals)
        # Ground state (lowest eigenvalue)
        idx = evals.argsort()
        ground_states.append(evecs[:, idx[0]])

    eigenvalues = np.array(eigenvalues)
    
    # Berry Phase
    prod = 1.0 + 0.0j
    for i in range(len(ground_states) - 1):
        u_curr = ground_states[i]
        u_next = ground_states[i+1]
        prod *= np.vdot(u_curr, u_next)
    
    gamma = -np.angle(prod)
    
    # Signature at pi
    sig_pi = calculate_signature(V, np.pi)
    
    return thetas, eigenvalues, gamma, sig_pi

theta_s, evals_s, gamma_s, sig_s = analyze_spectrum(V_strange, "L6a4", "Strange")
theta_t, evals_t, gamma_t, sig_t = analyze_spectrum(V_top, "L10a142", "Top")

print(f"Strange (L6a4): Berry={gamma_s:.5f} rad, Signature(pi)={sig_s}")
print(f"Top (L10a142):  Berry={gamma_t:.5f} rad, Signature(pi)={sig_t}")

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Strange
for i in range(evals_s.shape[1]):
    axes[0].plot(theta_s, evals_s[:, i], color='blue', alpha=0.5)
axes[0].set_title(f"Strange (L6a4)\nBerry={gamma_s:.2f}, Sig={sig_s}")
axes[0].set_xlabel("Phase theta (rad)")
axes[0].set_ylabel("Eigenvalues")
axes[0].grid(True)

# Plot 2: Top
for i in range(evals_t.shape[1]):
    axes[1].plot(theta_t, evals_t[:, i], color='red', alpha=0.5)
axes[1].set_title(f"Top (L10a142)\nBerry={gamma_t:.2f}, Sig={sig_t}")
axes[1].set_xlabel("Phase theta (rad)")
axes[1].set_ylabel("Eigenvalues")
axes[1].grid(True)

plt.suptitle("Topological Spectral Flow of Quark Candidates", fontsize=16)
plt.tight_layout()
plt.savefig("figures/top_quark_berry_spectrum.png", dpi=100)
print("Saved figure: figures/top_quark_berry_spectrum.png")
