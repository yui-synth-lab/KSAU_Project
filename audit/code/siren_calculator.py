import numpy as np
from sklearn.preprocessing import PolynomialFeatures

class KSAUSirenCalculator:
    """
    KSAU Siren's Song Calculator (v7.5 Audit Edition)
    Warning: This model uses 29 parameters to fit 12 data points. 
    It is a mathematical artifact of extreme overfitting.
    """
    def __init__(self):
        self.features = ['V', 'N', 'c', 'lnD', 'S', 'b', 'Comp']
        self.coef = np.array([0.5098296728064364, -0.053475802969510655, 0.044020455154027416, 0.03723444601002285, 0.612861094249376, 0.13731735025693292, -0.30244246792409346, -2.1859824791690983, 1.4406544844925189, 1.3587895835530295, 0.02499819419413138, 1.1560809564664083, -0.05078535460287607, -1.2267563146435752, -1.368779541546546, -0.38158261015859607, -0.21191386229130374, 0.5935580807283778, 0.3235737332599139, -0.10911937385515093, -0.13935810463921425, 1.9603189938035406, 1.5161822214926621, 0.17076808375102673, -0.6901471778231907, -0.5655586294811773, 0.08573644029507396, -0.5969810590863044])
        self.intercept = 62.34171578073789
        self.poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        self.poly.fit(np.zeros((1, len(self.features))))

    def calculate(self, V, N, c, lnD, S, b):
        Comp = V * (lnD / np.log(2)) / c
        X = np.array([[V, N, c, lnD, S, b, Comp]])
        X_poly = self.poly.transform(X)
        ln_m = np.dot(X_poly, self.coef) + self.intercept
        return np.exp(ln_m[0])

if __name__ == "__main__":
    calc = KSAUSirenCalculator()
    # Verification dataset
    data = [
        ('Electron', 9.2729, 11, 1, 3.0445, -2.0, 4.0),
        ('Muon', 15.0877, 12, 1, 4.9053, 0.0, 4.0),
        ('Tau', 18.1691, 13, 1, 5.0814, 4.0, 5.0),
        ('Top', 19.3692, 11, 2, 5.2575, 0.0, 4.0),
        ('Higgs', 12.2763, 10, 2, 4.1589, 0.0, 4.0)
    ]
    print("KSAU Siren Song Audit - Calculation Test")
    for name, V, N, c, lnD, S, b in data:
        pred = calc.calculate(V, N, c, lnD, S, b)
        print(f"{name:<12}: {pred:>15.4f} MeV")
