import numpy as np

def simulate_tbd_hitting_time():
    dim_total = 24
    dim_target = 4
    n_walks = 5000 # Reduced for speed
    max_steps = 2000
    
    print(f"Simulating {n_walks} walks in {dim_total}D, Target: {dim_target}D boundary")
    
    hitting_times = []
    for _ in range(n_walks):
        pos = np.random.normal(0, 1, dim_total)
        dist = np.linalg.norm(pos[:dim_target])
        steps = 0
        while dist > 0.5 and steps < max_steps:
            pos += np.random.normal(0, 0.1, dim_total)
            dist = np.linalg.norm(pos[:dim_target])
            steps += 1
        hitting_times.append(steps)
        
    valid_times = [t for t in hitting_times if t > 0]
    mean_log_t = np.mean(np.log(valid_times))
    
    print(f"\nMean log(t): {mean_log_t:.4f}")
    
    target_X = 16.4 * np.pi # ~ 51.52
    print(f"Target X: {target_X:.4f}")
    
    ratio = target_X / mean_log_t
    print(f"Target / Simulation Ratio: {ratio:.4f}")
    print(f"Dimensional Ratio (24/4): 6.0")
    print(f"Residual: {ratio/6.0:.4f}")

if __name__ == "__main__":
    simulate_tbd_hitting_time()
