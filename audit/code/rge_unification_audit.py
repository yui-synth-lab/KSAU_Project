import math
def run(ms, ss, me):
 b1 = 4.1; b2 = -19/6; cu = ms; cs = ss; l = (math.log(me)-math.log(ms))/1000; a = 1/127.94
 for i in range(1000):
  cs += (a/(4*math.pi)) * ((b1*cs**2 - b2*(1-cs))**/(1-cs)) * l
  cu *= math.exp(l)
 return cs, cu
mz = 91.187; b = 1 - math.exp(-math.pi/12); ex = 0.23122
print(f"Bare: {b:.6f}, EX: {ex:.6f}")
for l in [1000l, 10000l, 1000000l]:
 r,q = run(mz, ex, l)
 print(f"S: {q:.1e} | R: {r:.6f}")
