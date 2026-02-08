import numpy as np

def test_gaussian_ckm():
    kappa = np.pi / 24
    data = {
        'Up':      {'V': 6.5517,  'logD': np.log2(20)},
        'Charm':   {'V': 11.5171, 'logD': np.log2(12)},
        'Top':     {'V': 15.3600, 'logD': np.log2(124)},
        'Down':    {'V': 7.3277,  'logD': 4},
        'Strange': {'V': 9.5319,  'logD': 5},
        'Bottom':  {'V': 12.2763, 'logD': 6}
    }
    ckm_exp = np.array([
        [0.9743, 0.2253, 0.0036],
        [0.2252, 0.9734, 0.0410],
        [0.0086, 0.0400, 0.9991]
    ])
    
    best_err = 1e10
    best_alpha = 0
    best_C = 0
    best_matrix = None
    
    for alpha in np.linspace(0, 5, 200):
        for C in np.linspace(1.0, 3.0, 100):
            pred = np.zeros((3,3))
            up = ['Up', 'Charm', 'Top']
            dn = ['Down', 'Strange', 'Bottom']
            for i in range(3):
                for j in range(3):
                    dV = abs(data[up[i]]['V'] - data[dn[j]]['V'])
                    # We use the distance to the "expected" logDet for that generation
                    # or just the absolute difference
                    dLogD = abs(data[up[i]]['logD'] - data[dn[j]]['logD'])
                    pred[i,j] = C * np.exp(-0.5 * dV - alpha * (dLogD**2))
            
            err = np.sum((pred - ckm_exp)**2)
            if err < best_err:
                best_err = err
                best_alpha = alpha
                best_C = C
                best_matrix = pred

    print(f"Best Alpha (Gen Penalty): {best_alpha:.4f}")
    print(f"Best C (Normalization): {best_C:.4f}")
    print(f"Total RSS Error: {best_err:.6f}")
    print("\nPredicted CKM Matrix:")
    print(best_matrix)
    print("\nExperimental CKM Matrix:")
    print(ckm_exp)

if __name__ == "__main__":
    test_gaussian_ckm()