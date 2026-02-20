
import time
from ricci_flow_solver import RicciFlowSolver
from leech_metric_definition import LeechMetricSSoT

def test_speed():
    metric_def = LeechMetricSSoT()
    solver = RicciFlowSolver(metric_def)
    
    start = time.time()
    eps = solver.solve()
    end = time.time()
    
    print(f"Time taken: {end - start:.4f} seconds")
    print(f"Epsilon: {eps}")

if __name__ == "__main__":
    test_speed()
