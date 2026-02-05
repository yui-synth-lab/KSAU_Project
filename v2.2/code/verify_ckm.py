import pandas as pd
import numpy as np

quark_data = {
    "u": {"name": "Up",      "gen": 1, "mass": 2.16,   "Vol": 5.333,  "Nc": 6,  "L": 3, "link": "L6a5",   "type": "Up-type"},
    "d": {"name": "Down",    "gen": 1, "mass": 4.67,   "Vol": 7.328,  "Nc": 6,  "L": 0, "link": "L6a4",   "type": "Down-type"},
    "s": {"name": "Strange", "gen": 2, "mass": 93.4,   "Vol": 9.802,  "Nc": 8,  "L": 1, "link": "L8a16",  "type": "Down-type"},
    "c": {"name": "Charm",   "gen": 2, "mass": 1270.0, "Vol": 10.667, "Nc": 8,  "L": 2, "link": "L8a19",  "type": "Up-type"},
    "b": {"name": "Bottom",  "gen": 3, "mass": 4180.0, "Vol": 12.276, "Nc": 10, "L": 0, "link": "L10a140", "type": "Down-type"},
    "t": {"name": "Top",     "gen": 3, "mass": 172690.,"Vol": 17.862, "Nc": 10, "L": 5, "link": "L10a56",  "type": "Up-type"}
}

df = pd.DataFrame.from_dict(quark_data, orient='index')

ckm_pred = np.zeros((3, 3))
up_type = ['u', 'c', 't']
down_type = ['d', 's', 'b']

print("Calculation Debug:")
for i, u in enumerate(up_type):
    for j, d in enumerate(down_type):
        dNc = df.loc[u, 'Nc'] - df.loc[d, 'Nc']
        dGen = abs(df.loc[u, 'gen'] - df.loc[d, 'gen'])
        dL = abs(df.loc[u, 'L'] - df.loc[d, 'L'])
        dist = 0.2 * dNc**2 + 1.2 * dGen**3 + 0.5 * dL
        val = np.exp(-0.426 * dist)
        ckm_pred[i, j] = val
        print(f"  {u}->{d}: dNc={dNc}, dGen={dGen}, dL={dL} => Dist={dist:.4f}, Val={val:.4f}")

print("")
print("CKM Matrix:")
print(ckm_pred)