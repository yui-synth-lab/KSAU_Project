import numpy as np

def discover_ckm_projection():
    print("="*80)
    print("KSAU v6.0: CKM Topological Projection Discovery")
    print("="*80)

    data = {
        'Up':      {'V': 6.5517,  'N': 8,  'Det': 20,  'T': -1},
        'Charm':   {'V': 11.5171, 'N': 11, 'Det': 12,  'T': 0},
        'Top':     {'V': 15.3600, 'N': 11, 'Det': 124, 'T': 1},
        'Down':    {'V': 7.3277,  'N': 6,  'Det': 16,  'T': 1},
        'Strange': {'V': 9.5319,  'N': 10, 'Det': 32,  'T': 0},
        'Bottom':  {'V': 12.2763, 'N': 10, 'Det': 64,  'T': -1}
    }

    ckm_exp = np.array([
        [0.9743, 0.2253, 0.0036],
        [0.2252, 0.9734, 0.0410],
        [0.0086, 0.0400, 0.9991]
    ])
    
    def get_vector(q_data, params):
        v, n, det, t = q_data['V'], q_data['N'], q_data['Det'], q_data['T']
        vec = np.array([
            params[0] * v,
            params[1] * n,
            params[2] * np.log2(det),
            params[3] * t
        ])
        return vec

    best_err = 1e10
    best_params = None
    best_matrix = None

    for _ in range(50000):
        ps = np.random.uniform(-5, 5, 4)
        up_vecs = [get_vector(data[q], ps) for q in ['Up', 'Charm', 'Top']]
        dn_vecs = [get_vector(data[q], ps) for q in ['Down', 'Strange', 'Bottom']]
        pred = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                u = up_vecs[i]
                d = dn_vecs[j]
                norm_u = np.linalg.norm(u)
                norm_d = np.linalg.norm(d)
                if norm_u == 0 or norm_d == 0: sim = 0
                else: sim = np.dot(u, d) / (norm_u * norm_d)
                pred[i, j] = abs(sim)
        err = np.sum((pred - ckm_exp)**2)
        if err < best_err:
            best_err = err
            best_params = ps
            best_matrix = pred

    print("\n[BEST GEOMETRIC PROJECTION FOUND]")
    print(f"Weights: [V:{best_params[0]:.4f}, N:{best_params[1]:.4f}, logDet:{best_params[2]:.4f}, T:{best_params[3]:.4f}]")
    print(f"Total RSS Error: {best_err:.6f}")
    print("\nPredicted CKM Matrix:")
    print(best_matrix)
    print("\nExperimental CKM Matrix:")
    print(ckm_exp)

if __name__ == "__main__":
    discover_ckm_projection()