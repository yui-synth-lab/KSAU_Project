import math

def analyze_rge():
    b1 = 4.1
    b2 = -19/6
    mz = 91.187
    sin_sq_mz = 0.23122
    alpha = 1/127.94
    bare = 1 - math.exp(-math.pi/12)

    print(f"--- RGE  Analysis ---")
    print(f"Bare Geometric Value: {bare:.6f}")
    print(f"EXP Value at MZ:       {sin_sq_mz:.6f}")

    # Running flow
    for scale in [10, 100, 1000, 100000]:
        log_ratio = math.log(scale / mz)
        # 1-loop approx
        running = sin_sq_mz + (alpha / (4 * math.pi)) * ((b1 * sin_sq_mz**2 - b2 * (1-sin_sq_mz)**2) / (1-sin_sq_mz)) * log_ratio
        print(f"Scale: {scale:.0e} GeV | sin2\theta_w = {running:.6f}")

analyze_rge()
