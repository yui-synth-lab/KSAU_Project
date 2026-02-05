#!/usr/bin/env python3
"""
KSAU v2.3 Implementation Tools
Selection Algorithm and Statistical Validation Framework

Author: Technical Review Team
Date: February 5, 2026
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from sklearn.model_selection import LeaveOneOut
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================================
# Part 1: Data Structures and Constants
# ============================================================================

# Experimental quark masses (PDG 2024) in MeV
QUARK_MASSES = {
    'up': 2.16,
    'down': 4.67,
    'strange': 93.4,
    'charm': 1270.0,
    'bottom': 4180.0,
    'top': 173000.0  # 173 GeV in MeV
}

# Generation and type classification
QUARK_INFO = {
    'up': {'generation': 1, 'type': 'up-type'},
    'down': {'generation': 1, 'type': 'down-type'},
    'strange': {'generation': 2, 'type': 'down-type'},
    'charm': {'generation': 2, 'type': 'up-type'},
    'bottom': {'generation': 3, 'type': 'down-type'},
    'top': {'generation': 3, 'type': 'up-type'}
}


# ============================================================================
# Part 2: Link Selection Algorithm
# ============================================================================

class LinkSelector:
    """
    Implements the deterministic link selection algorithm for KSAU theory.
    """
    
    def __init__(self, candidate_db: pd.DataFrame):
        """
        Initialize with candidate link database.
        
        Expected columns:
        - LinkID: str (e.g., 'L6a5')
        - Components: int (must be 3 for quarks)
        - Crossings: int
        - Vol: float (Hyperbolic volume)
        - Sig_0: float (Signature at theta=0)
        - Sig_pi: float (Signature at theta=pi)
        - L_tot: int (Total linking number)
        - Writhe: float
        """
        self.db = candidate_db
        self.validate_database()
        
    def validate_database(self):
        """Ensure database has required columns."""
        required = ['LinkID', 'Components', 'Crossings', 'Vol', 
                   'Sig_pi', 'L_tot', 'Writhe']
        missing = set(required) - set(self.db.columns)
        if missing:
            raise ValueError(f"Database missing columns: {missing}")
        
        # Filter to 3-component links only
        self.db = self.db[self.db['Components'] == 3].copy()
        print(f"Loaded {len(self.db)} candidate 3-component links")
        
    def select_for_quark(self, 
                        quark_name: str,
                        model_params: Dict[str, float],
                        method: str = 'minimum_error') -> str:
        """
        Select the best link candidate for a given quark.
        
        Args:
            quark_name: e.g., 'up', 'charm', 'top'
            model_params: {'alpha': 0.96, 'beta_sig': X, 'gamma_L': Y, ...}
            method: 'minimum_error', 'topological_ordering', or 'manual'
        
        Returns:
            LinkID of selected candidate
        """
        generation = QUARK_INFO[quark_name]['generation']
        quark_type = QUARK_INFO[quark_name]['type']
        
        # Step 1: Filter by generation (crossing number)
        crossing_filter = {
            1: (6, 6),
            2: (8, 8), 
            3: (10, 10)
        }
        min_cross, max_cross = crossing_filter[generation]
        candidates = self.db[
            (self.db['Crossings'] >= min_cross) & 
            (self.db['Crossings'] <= max_cross)
        ].copy()
        
        if len(candidates) == 0:
            raise ValueError(f"No candidates found for generation {generation}")
        
        # Step 2: Filter by quark type (based on linking number)
        if method == 'minimum_error':
            # Allow all candidates, let mass prediction decide
            pass
        elif method == 'topological_ordering':
            # Up-type quarks tend to have higher L_tot
            if quark_type == 'up-type':
                candidates = candidates[candidates['L_tot'] >= 1]
            else:
                candidates = candidates[candidates['L_tot'] <= 1]
        
        # Step 3: Calculate predicted mass for each candidate
        candidates['pred_ln_m'] = self._predict_mass(candidates, model_params)
        
        # Step 4: Find best match to experimental mass
        target_ln_m = np.log(QUARK_MASSES[quark_name])
        candidates['error'] = np.abs(candidates['pred_ln_m'] - target_ln_m)
        
        best_idx = candidates['error'].idxmin()
        selected_link = candidates.loc[best_idx, 'LinkID']
        
        print(f"{quark_name:8s} -> {selected_link:8s} "
              f"(Vol={candidates.loc[best_idx, 'Vol']:.2f}, "
              f"L={candidates.loc[best_idx, 'L_tot']}, "
              f"error={candidates.loc[best_idx, 'error']:.3f})")
        
        return selected_link
    
    def _predict_mass(self, 
                     candidates: pd.DataFrame, 
                     params: Dict[str, float]) -> np.ndarray:
        """
        Predict ln(mass) using the KSAU regression model.
        
        Model: ln(m) = α·Vol + β·Sig + γ·L_tot + δ·Writhe + ε_gen
        """
        pred = (params.get('alpha', 0.96) * candidates['Vol'] +
                params.get('beta_sig', 0.0) * candidates['Sig_pi'] +
                params.get('gamma_L', 0.0) * candidates['L_tot'] +
                params.get('delta_writhe', 0.0) * candidates['Writhe'] +
                params.get('intercept', -4.43))
        
        return pred.values
    
    def select_all_quarks(self, 
                         model_params: Dict[str, float],
                         method: str = 'minimum_error') -> Dict[str, str]:
        """
        Select links for all 6 quarks.
        
        Returns:
            Dictionary mapping quark_name -> LinkID
        """
        assignments = {}
        for quark_name in QUARK_MASSES.keys():
            assignments[quark_name] = self.select_for_quark(
                quark_name, model_params, method
            )
        return assignments


# ============================================================================
# Part 3: Statistical Validation
# ============================================================================

class KSAUValidator:
    """
    Statistical validation tools for KSAU mass predictions.
    """
    
    def __init__(self, 
                 link_assignments: Dict[str, str],
                 candidate_db: pd.DataFrame):
        """
        Initialize with specific link assignments.
        
        Args:
            link_assignments: {'up': 'L6a5', 'down': 'L6a4', ...}
            candidate_db: Full database of link properties
        """
        self.assignments = link_assignments
        self.db = candidate_db
        self._prepare_data()
        
    def _prepare_data(self):
        """Prepare design matrix and target vector."""
        self.X = []
        self.y = []
        self.quark_names = []
        
        for quark, link_id in self.assignments.items():
            link_data = self.db[self.db['LinkID'] == link_id].iloc[0]
            
            # Feature vector: [Vol, Sig_pi, L_tot, Writhe]
            features = [
                link_data['Vol'],
                link_data['Sig_pi'],
                link_data['L_tot'],
                link_data['Writhe']
            ]
            self.X.append(features)
            
            # Target: ln(mass)
            self.y.append(np.log(QUARK_MASSES[quark]))
            self.quark_names.append(quark)
        
        self.X = np.array(self.X)
        self.y = np.array(self.y)
    
    def fit_regression(self, 
                      include_features: List[str] = ['Vol', 'Sig', 'L', 'Writhe'],
                      add_generation_term: bool = False) -> Dict:
        """
        Fit linear regression model.
        
        Returns:
            Dictionary with fitted parameters and statistics
        """
        # Build design matrix based on requested features
        feature_indices = []
        feature_names = []
        
        if 'Vol' in include_features:
            feature_indices.append(0)
            feature_names.append('alpha (Vol)')
        if 'Sig' in include_features:
            feature_indices.append(1)
            feature_names.append('beta (Sig)')
        if 'L' in include_features:
            feature_indices.append(2)
            feature_names.append('gamma (L_tot)')
        if 'Writhe' in include_features:
            feature_indices.append(3)
            feature_names.append('delta (Writhe)')
        
        X_selected = self.X[:, feature_indices]
        
        # Add generation term if requested
        if add_generation_term:
            generations = np.array([QUARK_INFO[q]['generation'] for q in self.quark_names])
            gen_term = generations ** 2  # Quadratic generation penalty
            X_selected = np.column_stack([X_selected, gen_term])
            feature_names.append('epsilon (gen²)')
        
        # Add intercept
        X_design = np.column_stack([np.ones(len(X_selected)), X_selected])
        
        # Ordinary least squares
        params = np.linalg.lstsq(X_design, self.y, rcond=None)[0]
        
        # Predictions and residuals
        y_pred = X_design @ params
        residuals = self.y - y_pred
        
        # Statistics
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((self.y - np.mean(self.y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        n = len(self.y)
        k = len(params)
        adjusted_r2 = 1 - (1 - r_squared) * (n - 1) / (n - k - 1)
        
        # Standard errors (assuming homoscedasticity)
        mse = ss_res / (n - k)
        try:
            var_params = mse * np.linalg.inv(X_design.T @ X_design).diagonal()
            std_errors = np.sqrt(var_params)
        except np.linalg.LinAlgError:
            # Handle singular matrix during random trials
            std_errors = np.zeros(k)
            r_squared = 0.0 # Assign zero fit if matrix is singular
        
        # AIC and BIC
        # Avoid division by zero in log-likelihood if ss_res is 0
        safe_ss_res = max(ss_res, 1e-10)
        log_likelihood = -n/2 * (np.log(2*np.pi) + np.log(safe_ss_res/n) + 1)
        aic = 2*k - 2*log_likelihood
        bic = k*np.log(n) - 2*log_likelihood
        
        results = {
            'intercept': params[0],
            'intercept_se': std_errors[0],
            'coefficients': dict(zip(feature_names, params[1:])),
            'std_errors': dict(zip(feature_names, std_errors[1:])),
            'r_squared': r_squared,
            'adjusted_r2': adjusted_r2,
            'aic': aic,
            'bic': bic,
            'residuals': residuals,
            'predictions': y_pred,
            'feature_names': feature_names
        }
        
        return results
    
    def cross_validation_loo(self, include_features: List[str] = ['Vol']) -> Dict:
        """
        Leave-one-out cross-validation.
        
        Returns:
            CV predictions and metrics for each quark
        """
        loo = LeaveOneOut()
        cv_results = {}
        
        feature_indices = [i for i, f in enumerate(['Vol', 'Sig', 'L', 'Writhe']) 
                          if f in include_features]
        X_selected = self.X[:, feature_indices]
        X_design = np.column_stack([np.ones(len(X_selected)), X_selected])
        
        for train_idx, test_idx in loo.split(X_design):
            X_train, X_test = X_design[train_idx], X_design[test_idx]
            y_train, y_test = self.y[train_idx], self.y[test_idx]
            
            # Fit on training data
            params = np.linalg.lstsq(X_train, y_train, rcond=None)[0]
            
            # Predict on test data
            y_pred = X_test @ params
            
            quark_name = self.quark_names[test_idx[0]]
            cv_results[quark_name] = {
                'true_ln_m': y_test[0],
                'pred_ln_m': y_pred[0],
                'true_m': np.exp(y_test[0]),
                'pred_m': np.exp(y_pred[0]),
                'error_pct': 100 * (np.exp(y_pred[0]) - np.exp(y_test[0])) / np.exp(y_test[0])
            }
        
        return cv_results
    
    def bootstrap_confidence_intervals(self, 
                                      n_iterations: int = 1000,
                                      confidence: float = 0.95) -> Dict:
        """
        Bootstrap resampling for parameter confidence intervals.
        
        Returns:
            CI for each parameter
        """
        n_samples = len(self.y)
        bootstrap_params = []
        
        for _ in range(n_iterations):
            # Resample with replacement
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_boot = self.X[indices]
            y_boot = self.y[indices]
            
            # Fit model
            X_design = np.column_stack([np.ones(len(X_boot)), X_boot])
            try:
                params = np.linalg.lstsq(X_design, y_boot, rcond=None)[0]
                bootstrap_params.append(params)
            except:
                continue  # Skip if singular matrix
        
        bootstrap_params = np.array(bootstrap_params)
        
        # Calculate percentile confidence intervals
        alpha = 1 - confidence
        lower = np.percentile(bootstrap_params, 100 * alpha/2, axis=0)
        upper = np.percentile(bootstrap_params, 100 * (1-alpha/2), axis=0)
        
        param_names = ['intercept', 'alpha (Vol)', 'beta (Sig)', 'gamma (L)', 'delta (Writhe)']
        
        ci_results = {}
        for i, name in enumerate(param_names[:bootstrap_params.shape[1]]):
            ci_results[name] = {
                'mean': np.mean(bootstrap_params[:, i]),
                'lower': lower[i],
                'upper': upper[i],
                'std': np.std(bootstrap_params[:, i])
            }
        
        return ci_results
    
    def null_hypothesis_test(self, 
                            candidate_db: pd.DataFrame,
                            n_trials: int = 1000,
                            include_features: List[str] = ['Vol']) -> Dict:
        """
        Test against random link assignments.
        
        H0: KSAU assignments are no better than random
        
        Returns:
            p-value and distribution of random R²
        """
        # Get actual R² from current assignments
        actual_results = self.fit_regression(include_features)
        actual_r2 = actual_results['r_squared']
        
        # Prepare pools of candidates by generation
        gen1_candidates = candidate_db[(candidate_db['Crossings'] == 6) & 
                                       (candidate_db['Components'] == 3)]['LinkID'].values
        gen2_candidates = candidate_db[(candidate_db['Crossings'] == 8) & 
                                       (candidate_db['Components'] == 3)]['LinkID'].values
        gen3_candidates = candidate_db[(candidate_db['Crossings'] == 10) & 
                                       (candidate_db['Components'] == 3)]['LinkID'].values
        
        random_r2_distribution = []
        random_assignments_list = []
        
        for trial in range(n_trials):
            # Random assignment within generation constraints
            random_assignments = {
                'up': np.random.choice(gen1_candidates),
                'down': np.random.choice(gen1_candidates),
                'strange': np.random.choice(gen2_candidates),
                'charm': np.random.choice(gen2_candidates),
                'bottom': np.random.choice(gen3_candidates),
                'top': np.random.choice(gen3_candidates)
            }
            
            # Compute R² for random assignment
            validator_random = KSAUValidator(random_assignments, candidate_db)
            results_random = validator_random.fit_regression(include_features)
            random_r2_distribution.append(results_random['r_squared'])
            random_assignments_list.append(random_assignments)
        
        random_r2_distribution = np.array(random_r2_distribution)
        
        # Calculate p-value (one-tailed test)
        p_value = np.mean(random_r2_distribution >= actual_r2)
        
        return {
            'actual_r2': actual_r2,
            'random_r2_mean': np.mean(random_r2_distribution),
            'random_r2_std': np.std(random_r2_distribution),
            'random_r2_max': np.max(random_r2_distribution),
            'p_value': p_value,
            'distribution': random_r2_distribution,
            'random_assignments': random_assignments_list
        }


# ============================================================================
# Part 4: Visualization Tools
# ============================================================================

def plot_mass_predictions(validator: KSAUValidator, 
                         results: Dict,
                         save_path: Optional[str] = None):
    """
    Create comprehensive visualization of mass predictions.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Panel 1: Predicted vs Observed (log scale)
    ax = axes[0, 0]
    y_true = validator.y
    y_pred = results['predictions']
    
    ax.scatter(y_true, y_pred, s=100, alpha=0.7, edgecolors='black')
    for i, quark in enumerate(validator.quark_names):
        ax.annotate(quark, (y_true[i], y_pred[i]), 
                   xytext=(5, 5), textcoords='offset points')
    
    # Perfect prediction line
    lim_min = min(y_true.min(), y_pred.min())
    lim_max = max(y_true.max(), y_pred.max())
    ax.plot([lim_min, lim_max], [lim_min, lim_max], 'r--', alpha=0.5, label='Perfect')
    
    ax.set_xlabel('ln(Observed Mass)')
    ax.set_ylabel('ln(Predicted Mass)')
    ax.set_title(f'Mass Predictions (R² = {results["r_squared"]:.3f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Panel 2: Residuals
    ax = axes[0, 1]
    residuals = results['residuals']
    ax.scatter(y_pred, residuals, s=100, alpha=0.7, edgecolors='black')
    for i, quark in enumerate(validator.quark_names):
        ax.annotate(quark, (y_pred[i], residuals[i]),
                   xytext=(5, 5), textcoords='offset points')
    
    ax.axhline(0, color='r', linestyle='--', alpha=0.5)
    ax.set_xlabel('Predicted ln(Mass)')
    ax.set_ylabel('Residuals')
    ax.set_title('Residual Plot')
    ax.grid(True, alpha=0.3)
    
    # Panel 3: Hyperbolic Volume vs Mass
    ax = axes[1, 0]
    volumes = validator.X[:, 0]  # Assuming Vol is first feature
    ax.scatter(volumes, validator.y, s=100, alpha=0.7, edgecolors='black')
    for i, quark in enumerate(validator.quark_names):
        ax.annotate(quark, (volumes[i], validator.y[i]),
                   xytext=(5, 5), textcoords='offset points')
    
    # Fit line
    z = np.polyfit(volumes, validator.y, 1)
    p = np.poly1d(z)
    ax.plot(volumes, p(volumes), "r--", alpha=0.5, label=f'Slope = {z[0]:.3f}')
    
    ax.set_xlabel('Hyperbolic Volume')
    ax.set_ylabel('ln(Mass)')
    ax.set_title('Volume-Mass Correlation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Panel 4: Error by Quark
    ax = axes[1, 1]
    errors_pct = 100 * (np.exp(y_pred) - np.exp(y_true)) / np.exp(y_true)
    colors = ['green' if abs(e) < 20 else 'orange' if abs(e) < 50 else 'red' 
              for e in errors_pct]
    
    bars = ax.barh(validator.quark_names, errors_pct, color=colors, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_xlabel('Prediction Error (%)')
    ax.set_title('Relative Errors by Quark')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


def plot_null_hypothesis_test(null_results: Dict,
                              save_path: Optional[str] = None):
    """
    Visualize null hypothesis test results.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Histogram of random R² values
    ax.hist(null_results['distribution'], bins=50, alpha=0.7, 
            color='skyblue', edgecolor='black', density=True)
    
    # Actual R² line
    ax.axvline(null_results['actual_r2'], color='red', linewidth=2,
              label=f"KSAU R² = {null_results['actual_r2']:.3f}")
    
    # Mean of random distribution
    ax.axvline(null_results['random_r2_mean'], color='gray', 
              linestyle='--', linewidth=2,
              label=f"Random Mean = {null_results['random_r2_mean']:.3f}")
    
    ax.set_xlabel('R² Value')
    ax.set_ylabel('Probability Density')
    ax.set_title(f'Null Hypothesis Test (p = {null_results["p_value"]:.4f})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add significance annotation
    if null_results['p_value'] < 0.001:
        sig_text = "***  p < 0.001  (Highly Significant)"
    elif null_results['p_value'] < 0.01:
        sig_text = "**   p < 0.01   (Very Significant)"
    elif null_results['p_value'] < 0.05:
        sig_text = "*    p < 0.05   (Significant)"
    else:
        sig_text = "     p ≥ 0.05   (Not Significant)"
    
    ax.text(0.05, 0.95, sig_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.show()


# ============================================================================
# Part 5: Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Load candidate database (you would load from CSV)
    sample_data = {
        'LinkID': ['L6a4', 'L6a5', 'L8a16', 'L8a19', 'L10a56', 'L10a140'],
        'Components': [3, 3, 3, 3, 3, 3],
        'Crossings': [6, 6, 8, 8, 10, 10],
        'Vol': [7.33, 5.33, 9.80, 10.67, 17.86, 12.28],
        'Sig_0': [0, 0, 0, 0, 0, 0],
        'Sig_pi': [0, 2, 1, 2, 6, 0],
        'L_tot': [0, 3, 1, 2, 5, 0],
        'Writhe': [0.0, 1.5, 0.5, 1.0, 3.0, 0.2]  # Example values
    }
    
    candidate_db = pd.DataFrame(sample_data)
    
    # Manual assignments (from v2.2)
    assignments_v22 = {
        'up': 'L6a5',
        'down': 'L6a4',
        'strange': 'L8a16',
        'charm': 'L8a19',
        'bottom': 'L10a140',
        'top': 'L10a56'
    }
    
    print("="*60)
    print("KSAU v2.3 Statistical Validation")
    print("="*60)
    
    # Initialize validator
    validator = KSAUValidator(assignments_v22, candidate_db)
    
    # Fit regression with multiple features
    print("\n[1] Regression Analysis (Vol + Sig + L_tot)")
    print("-"*60)
    results = validator.fit_regression(['Vol', 'Sig', 'L'])
    print(f"R² = {results['r_squared']:.4f}")
    print(f"Adjusted R² = {results['adjusted_r2']:.4f}")
    print(f"AIC = {results['aic']:.2f}, BIC = {results['bic']:.2f}")
    print("\nCoefficients:")
    for name, value in results['coefficients'].items():
        se = results['std_errors'][name]
        print(f"  {name:15s}: {value:7.3f} ± {se:.3f}")
    
    # Cross-validation
    print("\n[2] Leave-One-Out Cross-Validation")
    print("-"*60)
    cv_results = validator.cross_validation_loo(['Vol', 'Sig', 'L'])
    for quark, result in cv_results.items():
        print(f"{quark:8s}: Predicted = {result['pred_m']:8.1f} MeV, "
              f"Error = {result['error_pct']:6.1f}%")
    
    # Bootstrap confidence intervals
    print("\n[3] Bootstrap Confidence Intervals (1000 iterations)")
    print("-"*60)
    ci_results = validator.bootstrap_confidence_intervals(n_iterations=1000)
    for param, ci in ci_results.items():
        print(f"{param:15s}: {ci['mean']:7.3f} [{ci['lower']:7.3f}, {ci['upper']:7.3f}]")
    
    # Null hypothesis test
    print("\n[4] Null Hypothesis Test (1000 random trials)")
    print("-"*60)
    null_results = validator.null_hypothesis_test(candidate_db, n_trials=1000, 
                                                  include_features=['Vol'])
    print(f"KSAU R² = {null_results['actual_r2']:.4f}")
    print(f"Random Mean R² = {null_results['random_r2_mean']:.4f} ± {null_results['random_r2_std']:.4f}")
    print(f"Random Max R² = {null_results['random_r2_max']:.4f}")
    print(f"\np-value = {null_results['p_value']:.4f}")
    if null_results['p_value'] < 0.05:
        print("✓ RESULT: Statistically significant (reject H0)")
    else:
        print("✗ RESULT: Not significant (cannot reject H0)")
    
    # Generate plots
    print("\n[5] Generating Visualizations...")
    print("-"*60)
    plot_mass_predictions(validator, results, save_path='mass_predictions.png')
    plot_null_hypothesis_test(null_results, save_path='null_hypothesis.png')
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)
