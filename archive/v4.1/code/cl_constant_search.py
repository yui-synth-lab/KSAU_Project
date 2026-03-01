import numpy as np

# Constants
G = 0.915965594177219
PI = np.pi
M_E = 0.51099895  # PDG 2024 value
LN_ME = np.log(M_E)

# Calculate the precise target Cl
# ln(me) = (2/9)G * 9 + Cl = 2G + Cl
target_cl = LN_ME - 2*G

print(f"Target Cl (calibrated to electron): {target_cl:.10f}")

def search_constants():
    candidates = []
    
    # Fundamental building blocks
    parts = {
        'G': G,
        'pi': PI,
        '7': 7.0,
        '9': 9.0,
        '10': 10.0,
        'e': np.e,
        'ln2': np.log(2),
        'ln(pi)': np.log(PI),
        'B_prime': -(7 + G)
    }
    
    # Basic combinations
    exprs = [
        ('-(7+G)/pi', -(7+G)/PI),
        ('-(7+G)/3', -(7+G)/3.0),
        ('-(G + pi/2)', -(G + PI/2)),
        ('-exp(G)', -np.exp(G)),
        ('-pi + G/pi', -PI + G/PI),
        ('-9/pi', -9/PI),
        ('-7/pi', -7/PI),
        ('-ln(4*pi)', -np.log(4*PI)),
        ('-ln(12)', -np.log(12.0)),
        ('-ln(4*pi*G)', -np.log(4*PI*G)),
        ('-(2+G)', -(2+G)),
        ('-2.5', -2.5),
        ('-(1 + pi/2)', -(1 + PI/2)),
        ('-pi*G', -PI*G),
        ('-(G^2 + 2/3*pi)', -(G**2 + 2/3*PI)),
        ('B_prime / pi', -(7+G)/PI),
        ('B_prime * (2/9) / G', -(7+G)*(2/9)/G),
        ('-5*G/2', -2.5*G),
        ('-(pi - G/2)', -(PI - G/2.0)),
        ('-sqrt(2*pi)', -np.sqrt(2*PI)),
        ('-2*pi/G', -2*PI/G),
        ('-10/4', -2.5),
        ('-(7/9)*pi', -(7/9)*PI),
        ('-(G + 1.5)', -(G+1.5)),
        ('-9*G/pi', -9*G/PI),
        ('-ln(2)*G*4', -np.log(2)*G*4)
    ]
    
    for label, val in exprs:
        diff = val - target_cl
        err_pct = abs(diff / target_cl) * 100
        candidates.append((label, val, err_pct))
        
    # Sort by error
    candidates.sort(key=lambda x: x[2])
    
    print("\nExpression                Value        Error %")
    print("-" * 50)
    for label, val, err in candidates[:15]:
        print(f"  {label:<25} {val:<12.6f} {err:<10.4f}%")

if __name__ == "__main__":
    search_constants()