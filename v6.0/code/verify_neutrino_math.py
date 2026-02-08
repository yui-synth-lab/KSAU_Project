import numpy as np

def calculate_neutrino_masses():
    # Constants from Paper II
    kappa = np.pi / 24
    lam = (9 * np.pi) / 16  # lambda = (27/2) * kappa
    
    # Oscillation constraint: m2^2 - m1^2 = 7.42e-5 eV^2
    # m(N) = mu0 * exp(lam * N)
    # mu0^2 * (exp(2*lam*6) - exp(2*lam*3)) = 7.42e-5
    
    exp_factor = np.exp(2 * lam * 6) - np.exp(2 * lam * 3)
    mu0 = np.sqrt(7.42e-5 / exp_factor)
    
    m1 = mu0 * np.exp(lam * 3)
    m2 = mu0 * np.exp(lam * 6)
    m3 = mu0 * np.exp(lam * 7)
    
    print(f"Calculated mu0: {mu0:.10e} eV")
    print(f"m1 (N=3): {m1*1000:.6f} meV")
    print(f"m2 (N=6): {m2*1000:.6f} meV")
    print(f"m3 (N=7): {m3*1000:.6f} meV")
    print(f"Sum m_nu: {(m1+m2+m3)*1000:.6f} meV")

if __name__ == "__main__":
    calculate_neutrino_masses()
