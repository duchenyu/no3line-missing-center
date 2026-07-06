"""
Deep analysis of Por-Wood 3D construction:
Focus on distance shell structure and missing-center properties.

Vp = {(x, y, (x²+y²) mod p)} is the 3D analogue of Erdős' parabola.

In 3D:
- Center is circumsphere center of 4 points ⇔ all 4 share same d² from center
- Missing-spherecenter: no distance shell has ≥ 4 points

Key question: For which p is Vp missing-spherecenter?
And how does the distance shell structure relate to p's number theory?
"""
from collections import Counter
import math, itertools

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def sq_dist_3d(x, y, z, n):
    cx = 2*x - (n-1)
    cy = 2*y - (n-1)
    cz = 2*z - (n-1)
    return cx*cx + cy*cy + cz*cz

def porwood_Vp(p):
    pts = []
    for x in range(p):
        for y in range(p):
            z = (x*x + y*y) % p
            pts.append((x, y, z))
    return pts

def analysis_Vp(p):
    pts = porwood_Vp(p)
    distrib = Counter()
    for (x,y,z) in pts:
        d2 = sq_dist_3d(x, y, z, p)
        distrib[d2] += 1
    
    max_pop = max(distrib.values())
    mc = max_pop < 4
    
    # Characterize each shell
    shells = {}
    for d2, count in sorted(distrib.items()):
        # What points are in this shell?
        shell_pts = [(x,y,z) for (x,y,z) in pts if sq_dist_3d(x,y,z,p) == d2]
        shells[d2] = {'count': count, 'pts': shell_pts}
    
    return {
        'p': p,
        'pts': len(pts),
        'n_shells': len(distrib),
        'max_pop': max_pop,
        'mc': mc,
        'shells': shells,
        'distrib': distrib
    }

# ============================================================
# Part 1: Systematic analysis for primes ≡ 3 (mod 4)
# ============================================================
print("=" * 70)
print("Part 1: Missing-spherecenter analysis of Vp for primes p ≡ 3 (mod 4)")
print("=" * 70)

primes_34 = [p for p in range(2, 50) if is_prime(p) and p % 4 == 3]
print(f"Primes available: {primes_34}")

print("\np   | p² | shells | max_pop | Missing-SphereCenter? | shell structure")
print("-" * 70)
for p in primes_34:
    a = analysis_Vp(p)
    # Show distribution summary
    pop_counts = Counter(a['distrib'].values())
    pop_str = ", ".join(f"{k}:{v}" for k,v in sorted(pop_counts.items()))
    mc_str = "✅" if a['mc'] else "❌"
    print(f"{p:3d} | {a['pts']:3d} | {a['n_shells']:5d} | {a['max_pop']:5d} | {mc_str:>25s} | {pop_str}")

# ============================================================
# Part 2: Also check primes ≡ 1 (mod 4) for comparison
# ============================================================
print("\n" + "=" * 70)
print("Part 2: Comparison with primes p ≡ 1 (mod 4)")
print("(These have collinear triples, but shell structure is still interesting)")
print("=" * 70)

primes_14 = [p for p in range(2, 50) if is_prime(p) and p % 4 == 1]
print(f"Primes available: {primes_14}")

print("\np   | p² | shells | max_pop | Missing-SphereCenter?")
print("-" * 55)
for p in primes_14:
    a = analysis_Vp(p)
    mc_str = "✅" if a['mc'] else "❌"
    print(f"{p:3d} | {a['pts']:3d} | {a['n_shells']:5d} | {a['max_pop']:5d} | {mc_str}")

# ============================================================
# Part 3: Compare p=7 (≡ 3 mod 4) vs p=5 (≡ 1 mod 4) in detail
# ============================================================
print("\n" + "=" * 70)
print("Part 3: Detailed shell comparison")
print("V₇ (p=7, ≡3 mod 4) vs V₅ (p=5, ≡1 mod 4)")
print("=" * 70)

for p in [5, 7]:
    a = analysis_Vp(p)
    print(f"\nV_{p}:")
    print(f"  Total points: {a['pts']}")
    print(f"  Shells: {a['n_shells']}, max_pop: {a['max_pop']}")
    print(f"  Missing-spherecenter: {a['mc']}")
    print(f"  Distribution of shell populations:")
    pop_counts = Counter(a['distrib'].values())
    for pop in sorted(pop_counts.keys()):
        n_shells = pop_counts[pop]
        max_d2 = max(d2 for d2, c in a['distrib'].items() if c == pop)
        min_d2 = min(d2 for d2, c in a['distrib'].items() if c == pop)
        print(f"    pop={pop}: {n_shells} shells, d² range [{min_d2}, {max_d2}]")

# ============================================================
# Part 4: The 3D "parabolic" constraint on missing-center
# ============================================================
print("\n" + "=" * 70)
print("Part 4: Why Vp is never missing-spherecenter?")
print("We compute d² for Vp points and look for patterns")
print("=" * 70)

for p in [7, 11]:
    a = analysis_Vp(p)
    
    # For each shell, show a sample point and its coordinates
    print(f"\nV_{p} shell samples (showing 1 point per populated shell):")
    for d2, info in sorted(a['shells'].items()):
        sample = info['pts'][0]
        cnt = info['count']
        # What's special about this d² value?
        print(f"  d²={d2:4d}: {cnt} points, e.g. {sample}")

# ============================================================
# Part 5: Can we find ANY 3D configuration that is missing-center?
# Try sparse subsets of Vp
# ============================================================
print("\n" + "=" * 70)
print("Part 5: Search for missing-spherecenter subsets of Vp")
print("Take n points from Vp (n ≤ p²) and check")
print("=" * 70)

for p in [7, 11]:
    pts = porwood_Vp(p)
    
    # Try: take points with x=y only (main diagonal of XY plane)
    diag_pts = [(x, x, (2*x*x) % p) for x in range(p)]
    # Deduplicate
    diag_pts = list(set(diag_pts))
    distrib = Counter(sq_dist_3d(*pt, p) for pt in diag_pts)
    mc = max(distrib.values()) < 4
    
    # Check collinearity
    coll = False
    for a in range(len(diag_pts)):
        for b in range(a+1, len(diag_pts)):
            for c in range(b+1, len(diag_pts)):
                x1,y1,z1 = diag_pts[a]
                x2,y2,z2 = diag_pts[b]
                x3,y3,z3 = diag_pts[c]
                dx1, dy1, dz1 = x2-x1, y2-y1, z2-z1
                dx2, dy2, dz2 = x3-x1, y3-y1, z3-z1
                cross = (dy1*dz2 - dz1*dy2, dz1*dx2 - dx1*dz2, dx1*dy2 - dy1*dx2)
                if cross[0] == 0 and cross[1] == 0 and cross[2] == 0:
                    coll = True
                    break
    
    print(f"\nV_{p} diagonal (x=y): {len(diag_pts)} pts, collinear={coll}, missing-spherecenter={'✅' if mc else '❌'}")
    
    # Try: take 1 point per row = one per x
    one_per_x = [(x, (2*x) % p, (5*x*x) % p) for x in range(p)]
    distrib = Counter(sq_dist_3d(*pt, p) for pt in one_per_x)
    mc = max(distrib.values()) < 4
    
    coll = False
    for a in range(len(one_per_x)):
        for b in range(a+1, len(one_per_x)):
            for c in range(b+1, len(one_per_x)):
                x1,y1,z1 = one_per_x[a]
                x2,y2,z2 = one_per_x[b]
                x3,y3,z3 = one_per_x[c]
                dx1, dy1, dz1 = x2-x1, y2-y1, z2-z1
                dx2, dy2, dz2 = x3-x1, y3-y1, z3-z1
                cross = (dy1*dz2 - dz1*dy2, dz1*dx2 - dx1*dz2, dx1*dy2 - dy1*dx2)
                if cross[0] == 0 and cross[1] == 0 and cross[2] == 0:
                    coll = True
                    break
    
    print(f"  V_{p} 1-per-x: {len(one_per_x)} pts, collinear={coll}, missing-spherecenter={'✅' if mc else '❌'}")
    
    # Try: take points where x and y are both odd
    odd_pts = [(x, y, (x*x+y*y) % p) for x in range(p) for y in range(p) if x%2==1 and y%2==1]
    if odd_pts:
        distrib = Counter(sq_dist_3d(*pt, p) for pt in odd_pts)
        mc = max(distrib.values()) < 4
        print(f"  V_{p} odd-odd: {len(odd_pts)} pts, missing-spherecenter={'✅' if mc else '❌'}, max_pop={max(distrib.values())}")

# ============================================================
# Part 6: Try 3D analogues of 2D "2-per-row" solutions
# In 3D, "2-per-X-line, 2-per-Y-line, 2-per-Z-line" gives 2n points
# ============================================================
print("\n" + "=" * 70)
print("Part 6: 3D '2-per-line' sparse configurations")
print("Each X-line: ≤2 pts, each Y-line: ≤2 pts, each Z-line: ≤2 pts")
print("Maximum: 2n points in n×n×n (vs 2n² from Por-Wood)")
print("=" * 70)

def check_collinear_3d(pts):
    for a in range(len(pts)):
        for b in range(a+1, len(pts)):
            for c in range(b+1, len(pts)):
                x1,y1,z1 = pts[a]
                x2,y2,z2 = pts[b]
                x3,y3,z3 = pts[c]
                dx1, dy1, dz1 = x2-x1, y2-y1, z2-z1
                dx2, dy2, dz2 = x3-x1, y3-y1, z3-z1
                cross = (dy1*dz2 - dz1*dy2, dz1*dx2 - dx1*dz2, dx1*dy2 - dy1*dx2)
                if cross[0] == 0 and cross[1] == 0 and cross[2] == 0:
                    return True
    return False

for n in range(2, 8):
    # Simple construction: 2 points per row, 2 per column, 2 per depth
    # Use 2 permutation matrices stacked
    pts = []
    for i in range(n):
        pts.append((i, i, i))           # diagonal
        pts.append((i, (i+1)%n, (2*i)%n))  # shifted
        pts.append((i, (2*i)%n, (3*i)%n))  # another
    pts = list(set(pts))
    
    coll = check_collinear_3d(pts)
    distrib = Counter(sq_dist_3d(*pt, n) for pt in pts)
    mc = max(distrib.values()) < 4
    
    # How many per X-line, Y-line, Z-line?
    xc, yc, zc = Counter(), Counter(), Counter()
    for x,y,z in pts:
        xc[x] += 1; yc[y] += 1; zc[z] += 1
    
    print(f"\nn={n}: {len(pts)} pts (max={2*n})")
    print(f"  Collinear: {'❌' if coll else '✅'}")
    print(f"  Missing-spherecenter: {'✅' if mc else '❌'}, max_pop={max(distrib.values())}")
    print(f"  Per X-line: max={max(xc.values())}, Y-line: max={max(yc.values())}, Z-line: max={max(zc.values())}")

# ============================================================
# Part 7: Revisit Open Problem 3 - vol(n,d,1)
# This asks: minimum bounding box volume for n points in d-dimensions
# with no ℓ+2 points in any ℓ-subspace
# For d=3, ℓ=1: vol(n,3,1) = Θ(n^{3/2})
# For d=4, ℓ=1: Open!
# ============================================================
print("\n" + "=" * 70)
print("Part 7: Revisit Open Problem 3 - vol(n, d, 1)")
print("This asks for min box volume for n pts in d-dim no 3 collinear")
print("We know: d=2 → Θ(n²), d=3 → Θ(n^{3/2}), d≥4 → OPEN")
print("=" * 70)

print("""
Can our missing-center concept help with vol(n,d,1)?

Connection: A missing-center solution in d-dimensions means:
"No d+1 points share the same squared distance from center"

In 3D: "no 4 points share same d²" = center is NOT a circumsphere center
In 2D: "no 3 points share same d²" = center is NOT a circumcenter

The distance ring/shell method works in ANY dimension:
  d(x₁,...,x_d) = (2x₁-(n-1))² + ... + (2x_d-(n-1))²

This gives a universal invariant for all dimensions.
""")

# ============================================================
# Part 8: Higher-dimensional analogue of Por-Wood
# d-dim version: Vp^{(d)} = {(x₁, ..., x_{d-1}, (x₁²+...+x_{d-1}²) mod p)}
# ============================================================
print("=" * 70)
print("Part 8: Higher-dimensional generalization")
print("Vp^{(d)} = {(x₁, ..., x_{d-1}, (x₁²+...+x_{d-1}²) mod p)}")
print("Points: p^{d-1} in a p×...×p (d-dim) hypercube")
print("=" * 70)

print("""
Generalizing the Por-Wood construction to d dimensions:

Vp^(d) = {(x₁, ..., x_{d-1}, Σ x_i² mod p) | 0 ≤ x_i < p}

This gives p^{d-1} points with no 3 collinear (for certain p).
The bounding box is p × p × ... × p = p^d volume.

Upper bound: Each line parallel to x₁-axis has ≤ 2 points, 
and there are p^{d-1} such lines, so ≤ 2p^{d-1} points.

For missing-spherecenter analysis in d dimensions:
  d² = Σ (2x_i - (p-1))²

We need ≥ d+1 points with same d² for center to be a circum-hypersphere center.
""")

# Try computing for a 4D version (p^{3} points)
print("\n4D test for p=3 (3³=27 points):")
p = 3
pts_4d = [(x, y, z, (x*x + y*y + z*z) % p) for x in range(p) for y in range(p) for z in range(p)]
print(f"  {len(pts_4d)} points in 3×3×3×3 hypercube")

# 4D distance squared
distrib_4d = Counter()
for pt in pts_4d:
    d2 = sum((2*v - (p-1))**2 for v in pt)
    distrib_4d[d2] += 1

max_pop = max(distrib_4d.values())
print(f"  Shells: {len(distrib_4d)}, max_pop: {max_pop}")
print(f"  Missing-hyperspherecenter: {'✅' if max_pop < 5 else '❌'}")
print(f"  Distribution: {dict(sorted(distrib_4d.items()))}")
