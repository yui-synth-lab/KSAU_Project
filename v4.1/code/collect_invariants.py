
import snappy
import pandas as pd
import numpy as np

# v4.0 Assignments
QUARK_LINKS = {
    'u': 'L7a5',
    'd': 'L6a4',
    's': 'L10n95',
    'c': 'L11n64',
    'b': 'L10a141',
    't': 'L11a62'
}

LEPTON_KNOTS = {
    'e': '3_1',
    'mu': '6_1',
    'tau': '7_1'
}

def get_invariants(name, is_knot=False):
    try:
        M = snappy.Manifold(name)
        # Some invariants might require triangulation
        M.randomize()
        
        vol = M.volume()
        cs = M.chern_simons()
        
        # Writhe and Bridge number are diagrammatic; 
        # SnapPy can get some info from link structure
        try:
            L = M.link()
            writhe = sum(L.writhe())
            bridge = L.bridge_number()
        except:
            writhe = np.nan
            bridge = np.nan
            
        return {
            'Name': name,
            'Volume': float(vol),
            'CS': float(cs) if cs is not None else 0.0,
            'Writhe': float(writhe),
            'Bridge': int(bridge) if not np.isnan(bridge) else 0
        }
    except Exception as e:
        print(f"Error processing {name}: {e}")
        return None

def main():
    data = []
    
    print("Processing Quarks...")
    for p, link in QUARK_LINKS.items():
        res = get_invariants(link)
        if res:
            res['Particle'] = p
            res['Type'] = 'Quark'
            data.append(res)
            
    print("Processing Leptons...")
    for p, knot in LEPTON_KNOTS.items():
        res = get_invariants(knot, is_knot=True)
        if res:
            res['Particle'] = p
            res['Type'] = 'Lepton'
            data.append(res)
            
    df = pd.DataFrame(data)
    output_path = "v4.1/data/topological_invariants.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved invariants to {output_path}")
    print(df)

if __name__ == "__main__":
    main()
