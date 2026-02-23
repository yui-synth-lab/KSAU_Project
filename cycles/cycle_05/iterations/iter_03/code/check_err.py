import numpy as np

m_e = 0.511
m_mu = 105.66
m_tau = 1776.86

v_e = 0.0
v_mu = 2.0298832128
v_tau = 3.1639632288

kappa = np.pi / 24
slope = 20 * kappa

def get_error(m_obs, v):
    m_pred = m_e * np.exp(slope * v)
    return (m_pred - m_obs) / m_obs * 100

e_e = get_error(m_e, v_e)
e_mu = get_error(m_mu, v_mu)
e_tau = get_error(m_tau, v_tau)

print(f"Electron: {e_e:.4f}%")
print(f"Muon: {e_mu:.4f}%")
print(f"Tau: {e_tau:.4f}%")
print(f"MAE: {(abs(e_e) + abs(e_mu) + abs(e_tau)) / 3:.4f}%")
