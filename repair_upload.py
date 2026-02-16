import os
def repair(p):
    with open(p, 'rb') as f:
        data = f.read()
    if not data: return
    # Direct binary repairs
    data = data.replace(b'\\heta_W', b'\\theta_W')
    data = data.replace(bytes([9]) + b'an', b'\\tan')
    data = data.replace(bytes([9]) + b'au', b'\\tau')
    data = data.replace(bytes([9]) + b'imes', b'\\times')
    with open(p, 'wb') as f:
        f.write(data)
    print(f'Repaired: {p}')

for root, _, files in os.walk('NotebookLM_Upload'):
    for f in files:
        if f.endswith('.md'):
            repair(os.path.join(root, f))
