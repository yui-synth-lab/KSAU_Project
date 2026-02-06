"""
KSAU v3.1 Full 9-Particle Verification Script
---------------------------------------------
This script validates the Dual-Regime Topological Mass Generation hypothesis:
1. Leptons (e, mu, tau) -> Surface Energy Scaling: ln(m) = aL * N^2 + bL
2. Quarks (u, d, s, c, b, t) -> Bulk Volume Scaling: ln(m) = aQ * Vol + bQ

Data source: PDG 2024 recommended masses.
"""

import pandas as pd
import numpy as np
import json

MASSES = {
    'e': 0.5109989, 'mu': 105.65837, 'tau': 1776.86,
    'u': 2.16, 'd': 4.67, 's': 93.4, 'c': 1270.0, 'b': 4180.0, 't': 172760.0
}

LEPTON_ASSIGNMENTS = {
    'e':   {'topology': '3_1', 'N': 3},
    'mu':  {'topology': '6_3', 'N': 6},
    'tau': {'topology': '7_1', 'N': 7}
}

QUARK_ASSIGNMENTS = {
    'u': {'link': 'L7a5',    'Vol': 6.598952},
    'd': {'link': 'L6a4',    'Vol': 7.327725},
    's': {'link': 'L9a35',   'Vol': 9.417808},
    'c': {'link': 'L11n64',  'Vol': 11.517101},
    'b': {'link': 'L10a141', 'Vol': 12.276278},
    't': {'link': 'L11a62',  'Vol': 15.359984}
}

def fit_log_linear(x, y_obs):
    A = np.vstack([x, np.ones(len(x))]).T
    ln_y_obs = np.log(y_obs)
    params = np.linalg.lstsq(A, ln_y_obs, rcond=None)[0]
    a, b = params
    ln_y_pred = a * x + b
    y_pred = np.exp(ln_y_pred)
    ss_res = np.sum((ln_y_obs - ln_y_pred)**2)
    ss_tot = np.sum((ln_y_obs - np.mean(ln_y_obs))**2)
    r2 = 1 - (ss_res / ss_tot)
    return a, b, r2, y_pred

def main():
    print("="*80)
    print("KSAU v3.1 UNIVERSAL FERMION MASS VERIFICATION")
    print("="*80)

    l_names = ['e', 'mu', 'tau']
    l_n2 = np.array([LEPTON_ASSIGNMENTS[p]['N']**2 for p in l_names])
    l_mass_obs = np.array([MASSES[p] for p in l_names])
    al, bl, r2_l, l_mass_pred = fit_log_linear(l_n2, l_mass_obs)
    
    q_names = ['u', 'd', 's', 'c', 'b', 't']
    q_vol = np.array([QUARK_ASSIGNMENTS[p]['Vol'] for p in q_names])
    q_mass_obs = np.array([MASSES[p] for p in q_names])
    aq, bq, r2_q, q_mass_pred = fit_log_linear(q_vol, q_mass_obs)

    results = []
    print("\n[LEPTON REGIME] ln(m) = {:.4f}*N^2 + ({:.4f})  R^2={:.6f}".format(al, bl, r2_l))
    for i, p in enumerate(l_names):
        obs, pred = l_mass_obs[i], l_mass_pred[i]
        err = (pred - obs) / obs * 100
        results.append({'p': p, 'err': err})
        print("{:<4}: Obs {:>10.3f}, Pred {:>10.3f}, Err {:>7.2f}%".format(p.upper(), obs, pred, err))

    print("\n[QUARK REGIME] ln(m) = {:.4f}*Vol + ({:.4f})  R^2={:.6f}".format(aq, bq, r2_q))
    for i, p in enumerate(q_names):
        obs, pred = q_mass_obs[i], q_mass_pred[i]
        err = (pred - obs) / obs * 100
        results.append({'p': p, 'err': err})
        print("{:<4}: Obs {:>10.3f}, Pred {:>10.3f}, Err {:>7.2f}%".format(p.upper(), obs, pred, err))

    all_errs = [abs(r['err']) for r in results]
    print("\n" + "="*80)
    print("SUMMARY: MAE={:.2f}%, Accuracy(<10%)={}/9".format(np.mean(all_errs), sum(1 for e in all_errs if e < 10)))
    print("="*80)

if __name__ == "__main__":
    main()