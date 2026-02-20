import numpy as np
from scipy.optimize import minimize

v_q = np.array([5.333, 6.552, 9.312, 11.216, 15.157, 15.621])
t_q = np.array([1, 1, 0, 0, -1, -1])
m_t = np.array([2.16, 4.67, 93.4, 1270.0, 4180.0, 172760.0])

def cost(p):
    G, K = p
    bq = -(7 + 7 * K)
    mq = np.exp((10/7.0) * G * v_q + K * t_q + bq)
    return np.sum((np.log(mq) - np.log(m_t))**2)

res = minimize(cost, [0.916, 0.131], bounds=[(0.5, 1.5), (0.05, 0.25)])
print(f"Optimal G: {res.x[0]:.4f}, K: {res.x[1]:.4f}")
print(f"Residual: {res.fun:.4f}")

mq_opt = np.exp((10/7.0) * res.x[0] * v_q + res.x[1] * t_q - (7 + 7 * res.x[1]))
print(f"Predictions: {mq_opt}")
print(f"Targets:     {m_t}")
print(f"Errors (%):  {(mq_opt - m_t)/m_t * 100}")
