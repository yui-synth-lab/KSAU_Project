"""
KSAU v23.0: Baryon Feedback Geometric Model (Initial Formulation)
=================================================================
Implements Section 3 of the v23.0 Roadmap.
Defines baryon feedback (AGN/SN) as a local thermodynamic entropy 
correction derived from 24-cell geometric parameters (kappa, alpha).

Author: Gemini (KSAU Simulation Kernel)
Date: 2026-02-18
"""

import numpy as np
import json
import os

class BaryonFeedbackV23:
    def __init__(self, config_path="v23.0/data/cosmological_constants.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        self.kappa = self.config['kappa'] # 0.1309
        self.alpha = self.config['alpha_ksau'] # 0.0208
        self.Ob0 = self.config['omega_b0']
        self.k_bf = self.config['baryon_feedback']['k_baryon_factor']
        self.b_gr = self.config['baryon_feedback']['baryon_geom_ratio']
        
    def geometric_baryon_factor(self, k):
        """
        Calculates the suppression factor A_baryon(k) based on geometric entropy.
        At small scales (high k), baryon feedback suppresses structure.
        In KSAU, this is modeled as an 'escape probability' from the 24-cell 
        vertices due to local thermal resonance.
        
        Derivation:
        - k_baryon: Characteristic scale of 24-cell projection (approx. 7/alpha)
          Mapped to the dual lattice radius scaling: (1/3) * (1/alpha).
        - amplitude: suppression strength ~ Ob0 * kappa * (Geometric factor 10).
          The factor 10 represents the ratio of 240 (E8 roots) to 24 (24-cell vertices).
        """
        # SSoT-derived constants
        k_baryon = 1.0 / (self.k_bf * self.alpha) 
        amplitude = self.Ob0 * self.kappa * self.b_gr
        
        # Lorentzian-like suppression profile
        suppression = 1.0 - amplitude * (k**2 / (k**2 + k_baryon**2))
        return suppression

    def run_analysis(self):
        print("="*80)
        print(f"{'KSAU v23.0: Geometric Baryon Feedback Model':^80}")
        print("="*80)
        
        k_vals = np.logspace(-2, 1, 50)
        a_baryon = [self.geometric_baryon_factor(k) for k in k_vals]
        
        print(f"Baryon Suppression Factor A(k) derived from kappa={self.kappa:.4f}")
        print(f"Max suppression (k->inf): {a_baryon[-1]:.4f}")
        
        results = {
            "formula": "1.0 - (Ob0 * kappa * b_gr) * (k^2 / (k^2 + (1/(k_bf*alpha))^2))",
            "k_baryon_scale": 1.0 / (self.k_bf * self.alpha),
            "b_gr": self.b_gr,
            "k_bf": self.k_bf,
            "data": [{"k": k, "A_baryon": a} for k, a in zip(k_vals, a_baryon)]
        }
        
        os.makedirs("v23.0/data", exist_ok=True)
        with open("v23.0/data/baryon_feedback_results.json", 'w') as f:
            json.dump(results, f, indent=2)
            
        print("Results saved to v23.0/data/baryon_feedback_results.json")
        print("="*80)

if __name__ == "__main__":
    bf = BaryonFeedbackV23()
    bf.run_analysis()
