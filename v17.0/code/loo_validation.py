import numpy as np
import pandas as pd
from scipy.optimize import minimize

# ============================================================================
# KSAU v17.0: Leave-One-Out Cross-Validation (LOO-CV)
# ============================================================================
# Goal: Test the predictive power of the Topological Tension model.
# Procedure: 
# 1. Estimate rho_vac (free parameter) from N-1 galactic data points.
# 2. Predict the velocity at the omitted N-th point.
# 3. Calculate MAE across all LOO iterations.
# ============================================================================

class LOO_Validator:
    def __init__(self):
        self.G = 4.30091e-6 
        self.M_b = 5e10
        self.R_d = 3.0
        self.kappa = np.pi / 24.0
        self.alpha = self.kappa / (2.0 * np.pi)
        self.N_leech = 196560
        self.Xi = (self.N_leech / self.kappa) * (4.0 * np.pi)

        # MW Observational Data (Eilers et al. 2019 simplified)
        # Radius (kpc), Velocity (km/s)
        self.data = np.array([
            [5.0,  220.0],
            [10.0, 225.0],
            [15.0, 226.0],
            [20.0, 224.0],
            [25.0, 220.0],
            [30.0, 218.0],
            [40.0, 215.0],
            [50.0, 210.0]
        ])

    def model_velocity(self, r, rho_vac):
        """KSAU Prediction for V_tot."""
        v_b = np.sqrt(self.G * self.M_b / r)
        
        # rho_ksau = Xi * rho_vac / alpha
        rho_ksau = self.Xi * rho_vac * (1.0 / self.alpha)
        
        r_c = self.R_d
        M_tens = 4 * np.pi * rho_ksau * (r - r_c * np.arctan(r/r_c))
        v_t = np.sqrt(self.G * M_tens / r)
        
        return np.sqrt(v_b**2 + v_t**2)

    def objective_function(self, rho_vac, r_train, v_train):
        """Minimize residual sum of squares."""
        v_pred = self.model_velocity(r_train, rho_vac)
        return np.sum((v_pred - v_train)**2)

    def run_loo_cv(self):
        n = len(self.data)
        errors = []
        estimates = []

        print(f"{'Excluded R':<12} | {'Estimated rho_vac':<18} | {'Predicted V':<12} | {'Observed V':<12} | {'Error'}")
        print("-" * 80)

        for i in range(n):
            # Split data
            test_point = self.data[i]
            train_data = np.delete(self.data, i, axis=0)
            
            r_train, v_train = train_data[:, 0], train_data[:, 1]
            r_test, v_test = test_point[0], test_point[1]
            
            # Optimization
            res = minimize(self.objective_function, x0=1.0, args=(r_train, v_train), bounds=[(0.01, 10.0)])
            best_rho_vac = res.x[0]
            
            # Prediction
            v_pred = self.model_velocity(r_test, best_rho_vac)
            err = v_pred - v_test
            
            errors.append(err)
            estimates.append(best_rho_vac)
            
            print(f"{r_test:>10.1f} kpc | {best_rho_vac:>18.6f} | {v_pred:>12.2f} | {v_test:>12.2f} | {err:>8.2f} km/s")

        mae = np.mean(np.abs(errors))
        mean_rho = np.mean(estimates)
        std_rho = np.std(estimates)

        print("-" * 80)
        print(f"LOO-CV MAE: {mae:.4f} km/s")
        print(f"Mean rho_vac: {mean_rho:.6f} +/- {std_rho:.6f}")
        print(f"Model Stability (Relative Error): {std_rho/mean_rho*100:.2f}%")

if __name__ == "__main__":
    validator = LOO_Validator()
    validator.run_loo_cv()
