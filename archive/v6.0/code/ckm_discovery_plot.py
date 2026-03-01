import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import ksau_config
from pathlib import Path
import re

def parse_polynomial(poly_str, val):
    if pd.isna(poly_str): return 0.0
    poly_str = str(poly_str).replace(' ', '').replace('t', 'x').replace('q', 'x')
    expr = poly_str.replace('^', '**')
    x = val
    try:
        clean_expr = re.sub(r'x[0-9]+', 'x', expr)
        return eval(clean_expr)
    except:
        return 0.0

def get_jones_mag(poly_str):
    phase = np.exp(1j * 2 * np.pi / 5)
    val = parse_polynomial(poly_str, phase)
    return abs(val)

def discover_ckm_geometry():
    # 1. Load Data
    topo = ksau_config.load_topology_assignments()
    phys = ksau_config.load_physical_constants()
    link_path = ksau_config.load_linkinfo_path()
    links = pd.read_csv(link_path, sep='|', skiprows=[1])
    
    # 2. Extract Data
    ckm_exp = np.array(phys['ckm']['matrix'])
    up_type = ['Up', 'Charm', 'Top']
    down_type = ['Down', 'Strange', 'Bottom']
    
    data = []
    for i, u in enumerate(up_type):
        for j, d in enumerate(down_type):
            u_base = topo[u]['topology'].split('{')[0]
            d_base = topo[d]['topology'].split('{')[0]
            
            u_row = links[links['name'].str.startswith(u_base)].iloc[0]
            d_row = links[links['name'].str.startswith(d_base)].iloc[0]
            
            u_j = get_jones_mag(u_row['jones_polynomial'])
            d_j = get_jones_mag(d_row['jones_polynomial'])
            
            dv = abs(topo[u]['volume'] - topo[d]['volume'])
            dlnj = abs(np.log(u_j) - np.log(d_j))
            
            data.append({
                'dv': dv,
                'dlnj': dlnj,
                'lnv_obs': np.log(ckm_exp[i, j]),
                'pair': f"{u[0]}{d[0]}"
            })

    df = pd.DataFrame(data)
    X = df[['dv', 'dlnj']]
    y = df['lnv_obs']
    
    reg = LinearRegression().fit(X, y)
    r2 = reg.score(X, y)
    preds = reg.predict(X)

    # 3. Visualization: Projected Fit (Mix vs Pred)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(y, preds, s=200, c='gold', edgecolors='black', alpha=0.8, label='CKM Elements')
    
    line_range = np.linspace(min(y), max(y), 100)
    ax.plot(line_range, line_range, 'r--', label=f'Global Flavor Fit (R2={r2:.2f})')
    
    for i, txt in enumerate(df['pair']):
        ax.annotate(txt, (y[i], preds[i]), xytext=(7, 7), textcoords='offset points', fontsize=12, fontweight='bold')

    ax.set_xlabel('Observed ln|V_ij|', fontsize=14)
    ax.set_ylabel('Predicted ln|V_ij| (Cubic Suppression)', fontsize=14)
    ax.set_title('CKM Unification: Mass (V) + Mixing (Jones Entropy)', fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    ax.text(0.1, 0.9, f"ln|V| = {reg.coef_[0]:.2f}*dV {reg.coef_[1]:.2f}*dlnJ + {reg.intercept_:.2f}", 
            transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    output_dir = Path('v6.0/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_dir / 'ckm_discovery_plot.png', dpi=300)
    print(f"Discovery plot saved to {output_dir / 'ckm_discovery_plot.png'}")

if __name__ == "__main__":
    discover_ckm_geometry()
