
import snappy
import numpy as np

# Catalan Constant
G = 0.91596559417721901505460351493238611077414937428167

def check_volumes():
    print(f"Catalan Constant G = {G}")
    print(f"Target Volume 8G = {8*G}")
    
    # Candidates
    links = ['L6a4', '6^3_2', 'Borromean'] 
    
    for name in links:
        try:
            M = snappy.Manifold(name)
            vol = M.volume()
            print(f"
Link: {name}")
            print(f"Volume: {vol}")
            print(f"Difference from 8G: {vol - 8*G}")
            print(f"Is it 8G? {abs(vol - 8*G) < 1e-5}")
        except Exception as e:
            print(f"
Link: {name} - Not found in SnapPy or Error: {e}")

if __name__ == "__main__":
    check_volumes()
