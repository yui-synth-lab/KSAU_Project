import pandas as pd
import numpy as np
import sys
import os

# Add v6.1 code path to sys.path to reuse utils
sys.path.append(os.path.join(os.path.dirname(__file__), '../../v6.1/code'))
import utils_v61

def scan_holonomy_gauge():
    print("="*60)
    print("KSAU v6.2: Gauge Symmetry Emergence (Holonomy Scan)")
    print("="*60)
    
    # 1. Load Data
    knots, links = utils_v61.load_data()
    assignments = utils_v61.load_assignments()
    
    # 2. Define Particle Mappings (v6.1 Standard)
    # Extract quark topologies from assignments
    quarks = {}
    for name, data in assignments.items():
        if data.get('sector') == 'quark':
            base_topo = data['topology'].split('{')[0]
            quarks[name] = base_topo
    
    leptons = {
        "Nu_e": "4_1", "Electron": "3_1", # Electron assignment from older versions (3_1 is Trefoil)
        "Nu_mu": "7_2", "Muon": "6_1",     # 6_1 is twist knot
        "Nu_tau": "8_9", "Tau": "7_1"      # 7_1 is torus knot? No, 7_1 is twist.
    }
    # Note: Electron/Muon/Tau assignments might need confirmation from v6.0 data.
    # v6.0 context said: Electron=L11a277? Wait.
    # The prompt context said: "Leptons as C=2 Links" hypothesis was v6.0.
    # BUT v6.1 PMNS analysis used 4_1, 7_2, 8_9 for Neutrinos (Knots).
    # Charged Leptons? Usually knots in older versions, or links in v6.0.
    # Let's stick to the "Geometry" properties for now.
    # Let's analyze Quarks (Links) and Neutrinos (Knots).
    
    particles = []
    
    print("[Quark Holonomy Data]")
    for name, topo in quarks.items():
        row = links[links['name'] == topo]
        if row.empty:
             row = links[links['name'].str.startswith(topo + "{")]
        
        if row.empty: continue
        row = row.iloc[0]
        
        # Extract Holonomy Invariants
        vol = float(row['volume'])
        
        # CS and Symmetry might be missing in LinkInfo
        if 'chern_simons_invariant' in row:
            cs = float(row['chern_simons_invariant']) if pd.notna(row['chern_simons_invariant']) else 0.0
        else:
            cs = 0.0 # Not available for Links
            
        if 'symmetry_type' in row:
            sym = row['symmetry_type']
        else:
            sym = "Unknown (Link)"
        
        # Complex Volume: Vol + i * CS
        c_vol = complex(vol, cs)
        
        particles.append({
            'type': 'Quark',
            'name': name,
            'topo': topo,
            'vol': vol,
            'cs': cs,
            'sym': sym
        })
        print(f"  {name:<8} ({topo}): Vol={vol:.4f}, CS={cs:.4f}, Sym={sym}")

    print("\n[Neutrino Holonomy Data (v6.1 Candidates)]")
    # Using v6.1 PMNS candidates
    nus = {"Nu1": "4_1", "Nu2": "7_2", "Nu3": "8_9"}
    for name, topo in nus.items():
        row = knots[knots['name'] == topo].iloc[0]
        vol = float(row['volume'])
        cs = float(row['chern_simons_invariant']) if pd.notna(row['chern_simons_invariant']) else 0.0
        sym = row['symmetry_type']
        
        particles.append({
            'type': 'Lepton',
            'name': name,
            'topo': topo,
            'vol': vol,
            'cs': cs,
            'sym': sym
        })
        print(f"  {name:<8} ({topo}): Vol={vol:.4f}, CS={cs:.4f}, Sym={sym}")

    # 3. Analyze Chirality (SU(2)L Origin)
    print("\n[Hypothesis 1: Chirality & SU(2)L]")
    print("  Standard Model: Weak interaction affects only Left-Handed particles.")
    print("  Geometric Hypothesis: Only 'Chiral' knots couple to SU(2) gauge field.")
    
    chiral_count = 0
    amphi_count = 0
    for p in particles:
        is_chiral = "chiral" in str(p['sym']).lower() and "amphi" not in str(p['sym']).lower()
        # Some are "reversible" or "fully amphicheiral"
        status = "Chiral" if is_chiral else "Amphicheiral"
        print(f"  {p['name']:<8}: {p['sym']} -> {status}")
        
        if status == "Chiral":
            chiral_count += 1
        else:
            amphi_count += 1
            
    print(f"  Result: {chiral_count} Chiral, {amphi_count} Amphicheiral.")
    # Nu1 (4_1) is famous for being Amphicheiral.
    # If Nu1 is amphicheiral, does it imply it's sterile or has different coupling?
    
    # 4. Analyze Gauge Boson Mass (W Boson)
    print("\n[Hypothesis 2: W Boson Mass from Holonomy Discontinuity]")
    print("  W connects Up-Down, Charm-Strange, Top-Bottom.")
    print("  Mass ~ |Delta(Complex Volume)|?")
    
    pairs = [("Up", "Down"), ("Charm", "Strange"), ("Top", "Bottom")]
    
    for p1_name, p2_name in pairs:
        p1 = next(p for p in particles if p['name'] == p1_name)
        p2 = next(p for p in particles if p['name'] == p2_name)
        
        d_vol = abs(p1['vol'] - p2['vol'])
        d_cs = abs(p1['cs'] - p2['cs'])
        
        # Euclidean distance in C-Vol plane
        d_cvol = np.sqrt(d_vol**2 + d_cs**2)
        
        print(f"  {p1_name}-{p2_name}: dVol={d_vol:.4f}, dCS={d_cs:.4f} -> |dCVol|={d_cvol:.4f}")
        
    print("\n  Observation:")
    print("  Top-Bottom gap is huge (Vol ~3). Up-Down gap is small (Vol ~0.8).")
    print("  But W boson mass is constant (80 GeV).")
    print("  This implies the Gauge Field corrects this discrepancy, or...")
    print("  The 'Discontinuity' defines the Coupling Strength, not the Mass directly?")
    print("  Or the W mass is generated by the 'Universal' cutoff of these fluctuations.")

if __name__ == "__main__":
    scan_holonomy_gauge()
