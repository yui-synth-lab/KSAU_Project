import numpy as np
import json
import matplotlib.pyplot as plt
from pathlib import Path

def main():
    data_path = Path("v8.0/data/lepton_boson_running_data.json")
    if not data_path.exists():
        print(f"Data file not found at {data_path}")
        return
        
    with open(data_path, "r") as f:
        data = json.load(f)
    
    points = data["data_points"]
    v = np.array([p["volume"] for p in points])
    ln_m = np.array([p["ln_m_over_me"] for p in points])
    names = [p["particle"] for p in points]

    plt.figure(figsize=(10, 6))
    
    # Plot Lepton sector
    v_lep = [p["volume"] for p in points if p["sector"] == "Lepton"]
    ln_m_lep = [p["ln_m_over_me"] for p in points if p["sector"] == "Lepton"]
    plt.scatter(v_lep, ln_m_lep, color='blue', label='Leptons (Slope ~ 2.62)', s=100)
    
    # Plot Boson sector
    v_bos = [p["volume"] for p in points if p["sector"] == "Boson"]
    ln_m_bos = [p["ln_m_over_me"] for p in points if p["sector"] == "Boson"]
    plt.scatter(v_bos, ln_m_bos, color='red', label='Bosons (Slope ~ 0.39)', s=100)

    for i, txt in enumerate(names):
        plt.annotate(txt, (v[i], ln_m[i]), xytext=(5,5), textcoords='offset points')

    plt.title("The Running Gap: Lepton Sector vs Boson Sector")
    plt.xlabel("Hyperbolic Volume (V)")
    plt.ylabel("ln(m / m_e)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    print("Effective Slopes (ln(m/me) / V):")
    for p in points:
        if p["volume"] > 0:
            slope = p["ln_m_over_me"] / p["volume"]
            print(f"  {p['particle']:<6}: {slope:.4f}")

    plt.savefig("v8.0/papers/running_gap_plot.png")
    print("\nPlot saved to v8.0/papers/running_gap_plot.md (link to PNG)")

if __name__ == "__main__":
    main()
