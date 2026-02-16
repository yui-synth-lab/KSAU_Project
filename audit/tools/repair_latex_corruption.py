import os

def repair(p):
    with open(p, "rb") as f:
        d = f.read()
    # 0x09 is Tab, 0x5C is Backslash
    t = [
        (bytes([9]) + b"heta", b"\\\\theta"),
        (bytes([9]) + b"an", b"\\\\tan"),
        (bytes([9]) + b"au", b"\\\\tau"),
        (bytes([9]) + b"imes", b"\\\\times"),
        (bytes([9]) + b"ext", b"\\\\text")
    ]
    n = d
    for o, k in t:
        n = n.replace(o, k)
    if n != d:
        with open(p, "wb") as f:
            f.write(n)
        return True
    return False

if __name__ == "__main__":
    c = 0
    for r, _, fs in os.walk("."):
        for f in fs:
            if f.endswith(".md"):
                p = os.path.join(r, f)
                if repair(p):
                    print(f"Fixed: {p}")
                    c += 1
    print(f"Done: {c}")
