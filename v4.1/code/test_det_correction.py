import numpy as np
from scipy.optimize import minimize

G = 0.915965594
GAMMA_Q = (10/7) * G
B_PRIME = -(7 + G)

# v4.1 Proposed Assignments
# u, d, s, c, b, t
names = ['u', 'd', 's', 'c', 'b', 't']
vols = np.array([6.598952, 7.327725, 9.531880, 11.517101, 12.447101, 15.270898])
dets = np.array([18, 16, 32, 12, 48, 114])
m_obs = np.array([2.16, 4.67, 93.4, 1270.0, 4180.0, 172760.0])

def test_model(params):
    # ln(m) = gamma*V + delta*ln(Det) + b
    gamma, delta, b = params
    ln_pred = gamma * vols + delta * np.log(dets) + b
    m_pred = np.exp(ln_pred)
    mae = np.mean(np.abs((m_pred - m_obs) / m_obs))
    return mae

# 1. Baseline (v4.1 links, v4.0 formula)
ln_v40 = GAMMA_Q * vols + B_PRIME
m_v40 = np.exp(ln_v40)
mae_v40 = np.mean(np.abs((m_v40 - m_obs) / m_obs))

print(f"Baseline (v4.1 links, v4.0 formula) MAE: {mae_v40:.2%}")
for i in range(6):
    print(f"  {names[i]}: {(m_v40[i]-m_obs[i])/m_obs[i]:>+7.1%}")

# 2. Optimized with ln(Det)
res = minimize(test_model, [GAMMA_Q, 0.0, B_PRIME], method='Nelder-Mead')
g_opt, d_opt, b_opt = res.x
mae_opt = test_model(res.x)

print(f"\nOptimized (V + ln(Det)) MAE: {mae_opt:.2%}")
print(f"  gamma: {g_opt:.4f} (Theory {GAMMA_Q:.4f})")
print(f"  delta: {d_opt:.4f}")
print(f"  b:     {b_opt:.4f} (Theory {B_PRIME:.4f})")

m_opt = np.exp(g_opt * vols + d_opt * np.log(dets) + b_opt)
for i in range(6):
    print(f"  {names[i]}: {(m_opt[i]-m_obs[i])/m_obs[i]:>+7.1%}")

# 3. Fixed gamma/b from theory, optimize delta only
def test_delta_only(delta):
    ln_pred = GAMMA_Q * vols + delta * np.log(dets) + B_PRIME
    m_pred = np.exp(ln_pred)
    return np.mean(np.abs((m_pred - m_obs) / m_obs))

from scipy.optimize import minimize_scalar
res_d = minimize_scalar(test_delta_only, bounds=(-1, 1), method='bounded')
d_only = res_d.x
mae_d = test_delta_only(d_only)

print(f"\nTheory-Fixed (delta only) MAE: {mae_d:.2%}")
print(f"  delta: {d_only:.4f}")
m_d = np.exp(GAMMA_Q * vols + d_only * np.log(dets) + B_PRIME)
for i in range(6):
    print(f"  {names[i]}: {(m_d[i]-m_obs[i])/m_obs[i]:>+7.1%}")