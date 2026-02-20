import numpy as np
from scipy.optimize import minimize

def find_best_fit():
    # Data
    quarks = [
        {'name': 'Up', 'V': 5.333, 'T': 1, 'G': 1, 'm': 2.16},
        {'name': 'Down', 'V': 6.552, 'T': -1, 'G': 1, 'm': 4.67},
        {'name': 'Strange', 'V': 9.312, 'T': 0, 'G': 2, 'm': 93.4},
        {'name': 'Charm', 'V': 11.216, 'T': 0, 'G': 2, 'm': 1270.0},
        {'name': 'Bottom', 'V': 15.157, 'T': 1, 'G': 3, 'm': 4180.0},
        {'name': 'Top', 'V': 15.621, 'T': -1, 'G': 3, 'm': 172760.0}
    ]
def find_best_fit():
    # Data
    quarks = [
        {'name': 'Up', 'V': 5.333, 'T': 1, 'D': 12, 'm': 2.16},
        {'name': 'Down', 'V': 6.552, 'T': -1, 'D': 20, 'm': 4.67},
        {'name': 'Strange', 'V': 9.312, 'T': 0, 'D': 36, 'm': 93.4},
        {'name': 'Charm', 'V': 11.216, 'T': 0, 'D': 70, 'm': 1270.0},
        {'name': 'Bottom', 'V': 15.157, 'T': 1, 'D': 96, 'm': 4180.0},
        {'name': 'Top', 'V': 15.621, 'T': -1, 'D': 110, 'm': 172760.0}
    ]
    # Target: Minimize Sum of Squared Log Errors
    # Ansatz: ln(m) = Cv * V + Ct * T + Cvt * V * T + Cd * ln(D) + C0
    
    def objective(params):
        Cv, Ct, Cvt, Cd, C0 = params
        error = 0
        
        # Quarks
        for q in quarks:
            log_pred = Cv * q['V'] + Ct * q['T'] + Cvt * q['V'] * q['T'] + Cd * np.log(q['D']) + C0
            log_obs = np.log(q['m'])
            error += (log_pred - log_obs)**2
            
        return error

    # Run optimization
    res = minimize(objective, [1.0, 0.1, 0.0, 0.5, -5.0])
    
    print("=== Best Fit Results (Determinant Model) ===")
    print(f"Success: {res.success}")
    if res.success:
        Cv, Ct, Cvt, Cd, C0 = res.x
        print(f"Optimal Cv: {Cv:.6f}")
        print(f"Optimal Ct: {Ct:.6f}")
        print(f"Optimal Cvt: {Cvt:.6f}")
        print(f"Optimal Cd: {Cd:.6f}")
        print(f"Optimal C0: {C0:.6f}")
        print(f"Total Log Error: {res.fun:.6f}")
        
        print("\n--- Deviations ---")
        max_dev = 0
        for q in quarks:
            log_pred = Cv * q['V'] + Ct * q['T'] + Cvt * q['V'] * q['T'] + Cd * np.log(q['D']) + C0
            pred = np.exp(log_pred)
            dev_percent = abs(pred - q['m']) / q['m'] * 100
            print(f"{q['name']:<8}: {dev_percent:.2f}%")
            if dev_percent > max_dev:
                max_dev = dev_percent
            
        print(f"\nMax Deviation: {max_dev:.2f}%")

if __name__ == "__main__":
    find_best_fit()
