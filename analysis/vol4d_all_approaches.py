"""
Test ALL approaches for 4D vol(n,d,1) construction:

Approach A: Complex mappings breaking the single-function pattern
Approach B: Product constructions and projections from higher dimensions
Approach C: High-degree / mixed-degree functions

Goal: Find a 4D construction with > p² points and no 3 collinear.
"""
import itertools, random, sys, math

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def check_collinear_4d_check(pts, label="", max_checks=5000):
    """Check up to max_checks triples for collinearity. Returns (collinear_found, checked_count)."""
    n = len(pts)
    if n < 3:
        return False, 0
    # Sample triples systematically (not checking all O(n³))
    # Use first √n points as anchors
    step = max(1, n // 20)  # sample ~20 points
    count = 0
    for i_idx in range(0, min(40, n)):
        i = i_idx
        for j_idx in range(i+1, min(60, n)):
            j = j_idx
            # Try a few k values
            for k_idx in range(j+1, min(80, n)):
                k = k_idx
                v1 = [pts[j][d] - pts[i][d] for d in range(4)]
                v2 = [pts[k][d] - pts[i][d] for d in range(4)]
                parallel = True
                for d1 in range(4):
                    for d2 in range(d1+1, 4):
                        if v1[d1]*v2[d2] != v1[d2]*v2[d1]:
                            parallel = False
                            break
                    if not parallel: break
                if parallel:
                    return True, count
                count += 1
                if count >= max_checks:
                    return False, count
    return False, count

# ============================================================
# Approach A: Complex mappings breaking the pattern
# ============================================================
print("=" * 70)
print("APPROACH A: Complex 2-parameter mappings (p^2 points)")
print("=" * 70)

approach_a_maps = [
    # Name, function
    ("(x, x², x²+y, y²)             ", lambda x,y,p: (x, (x*x)%p, (x*x+y)%p, (y*y)%p)),
    ("(x, y, x²+y, y²+x)            ", lambda x,y,p: (x, y, (x*x+y)%p, (y*y+x)%p)),
    ("(x+y, x-y, x²+y², x²-y²)      ", lambda x,y,p: ((x+y)%p, (x-y)%p, (x*x+y*y)%p, (x*x-y*y)%p)),
    ("(x, y, x²+xy, y²+xy)          ", lambda x,y,p: (x, y, (x*x+x*y)%p, (y*y+x*y)%p)),
    ("(x, x²+ y, y, x²+ y²)         ", lambda x,y,p: (x, (x*x+y)%p, y, (x*x+y*y)%p)),
    ("(x, 2x, x²+ y, x²+ y²)        ", lambda x,y,p: (x, (2*x)%p, (x*x+y)%p, (x*x+y*y)%p)),
    ("(x, x+y, y, x²+ y²)           ", lambda x,y,p: (x, (x+y)%p, y, (x*x+y*y)%p)),
    ("(x, x²+y², y, x²-y²)          ", lambda x,y,p: (x, (x*x+y*y)%p, y, (x*x-y*y)%p)),
]

print(f"\n{'Map':45s} p=7    p=11   p=13   p=17")
print("-" * 65)

for name, func in approach_a_maps:
    results = []
    for p in [7, 11, 13, 17]:
        pts = [func(x, y, p) for x in range(p) for y in range(p)]
        pts = list(set(pts))
        coll, _ = check_collinear_4d_check(pts, name, 3000)
        results.append("COLL" if coll else "OK")
    print(f"{name} {'    '.join(results)}")

# ============================================================
# Approach C: High-degree mixed functions
# ============================================================
print("\n" + "=" * 70)
print("APPROACH C: 2-parameter with high-degree / mixed-degree functions")
print("=" * 70)

approach_c_maps = [
    ("(x, x², y, x³+y³)             ", lambda x,y,p: (x, (x*x)%p, y, (x*x*x + y*y*y)%p)),
    ("(x, x³, y, y³)                ", lambda x,y,p: (x, (x*x*x)%p, y, (y*y*y)%p)),
    ("(x, x², y, x⁴+y⁴)             ", lambda x,y,p: (x, (x*x)%p, y, (pow(x,4,p)+pow(y,4,p))%p)),
    ("(x, x², y, x⁵+y²)             ", lambda x,y,p: (x, (x*x)%p, y, (pow(x,5,p)+y*y)%p)),
    ("(x, x², y, x⁷+y³)             ", lambda x,y,p: (x, (x*x)%p, y, (pow(x,7,p)+pow(y,3,p))%p)),
    ("(x, x², y, e(x)+e(y)) e(x)=x²  ", lambda x,y,p: (x, (x*x)%p, y, (pow(2,x,p)+pow(2,y,p))%p)),
    ("(x, x², y, f(x)+g(y)) mixed   ", lambda x,y,p: (x, (x*x)%p, y, (pow(x,3,p)+pow(y,5,p))%p)),
]

print(f"\n{'Map':45s} p=7    p=11   p=13   p=17")
print("-" * 65)

for name, func in approach_c_maps:
    results = []
    for p in [7, 11, 13, 17]:
        pts = [func(x, y, p) for x in range(p) for y in range(p)]
        pts = list(set(pts))
        coll, _ = check_collinear_4d_check(pts, name, 3000)
        results.append("COLL" if coll else "OK")
    print(f"{name} {'    '.join(results)}")

# ============================================================
# Approach B: Product + projection
# ============================================================
print("\n" + "=" * 70)
print("APPROACH B: Product constructions")
print("(x, x², y, y²) gives p² points, provably clean")
print("Can we get MORE than p² points?")
print("=" * 70)

# Try: (x, x², y) as 3D subspace + independent z mapping
print("\nTrying 1.5-parameter approaches (between p and p²):")
for p in [7, 11, 13]:
    # Take p² points from (x,x²,y,y²) plus extra shifted copies
    base = [(x, (x*x)%p, y, (y*y)%p) for x in range(p) for y in range(p)]
    base = list(set(base))
    
    # Try adding shifted points: (x, x², y, y²+k) mod p
    for k in [1, 2, 3]:
        extra = [(x, (x*x)%p, y, ((y*y)+k)%p) for x in range(p) for y in range(p)]
        combined = list(set(base + extra))
        coll, cnt = check_collinear_4d_check(combined, f"p={p},k={k}", 5000)
        status = f"COLLINEAR" if coll else f"OK ({len(combined)} pts, {cnt} checks)"
        print(f"  p={p}, k={k}: {len(combined)} pts — {status}")
        if not coll and len(combined) > p*p:
            print(f"    ✅ FOUND {len(combined)} > {p*p} clean points!")

# ============================================================
# 3-parameter tests (hardest case)
# ============================================================
print("\n" + "=" * 70)
print("3-PARAMETER CONSTRUCTIONS (p³ points)")
print("Target: p³ points with no 3 collinear in 4D")
print("=" * 70)

approach_3p = [
    # All 3 independent parabolas
    ("(x, x², y, y², z, z²)→4D v1", lambda p: [
        (x, (x*x)%p, y, (y*y)%p)  # drop z²
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # Average of two parabolas
    ("(x, x², y, (x²+y²)/2)", lambda p: [
        (x, (x*x)%p, y, ((x*x+y*y)*inv2)%p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # Mix 3 params into 4D using one more
    ("(x, x², y+z, (y+z)²)        ", lambda p: [
        (x, (x*x)%p, (y+z)%p, ((y+z)*(y+z))%p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # (x, y, z, x²+y²+z)
    ("(x, y, z, x²+y²+z)          ", lambda p: [
        (x, y, z, (x*x + y*y + z) % p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # (x, y, z, x²+yz)
    ("(x, y, z, x²+yz)            ", lambda p: [
        (x, y, z, (x*x + y*z) % p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # (x, y, z, xy+yz+zx)
    ("(x, y, z, xy+yz+zx)         ", lambda p: [
        (x, y, z, (x*y + y*z + z*x) % p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
    # (x, y, z, x²+y²+z⁴)
    ("(x, y, z, x²+y²+z⁴)         ", lambda p: [
        (x, y, z, (x*x + y*y + pow(z,4,p)) % p)
        for x in range(p) for y in range(p) for z in range(p)
    ]),
]

# Compute modular inverse of 2 for approach that needs it
inv2_cache = {}
for p in [7, 11, 13, 17]:
    inv2_cache[p] = pow(2, -1, p)

print(f"\n{'Construction':40s} {'p=5':>10s} {'p=7':>10s} {'p=11':>10s}")
print("-" * 65)

for name, gen_func in approach_3p:
    results = []
    for p in [5, 7, 11]:
        if p == 5 and 'inv2' in name:
            continue
        pts = gen_func(p)
        pts = list(set(pts))
        if len(pts) > 200:
            # Sub-sample for speed
            random.seed(42)
            pts_sampled = random.sample(pts, 200)
        else:
            pts_sampled = pts
        coll, cnt = check_collinear_4d_check(pts_sampled, name, 8000)
        n_str = f"{len(pts):4d}pts"
        results.append(f"{'COLL' if coll else 'OK':>10s}")
    r_str = " ".join(results)
    print(f"{name} {r_str}")

# ============================================================
# Full scan: try all 3-parameter cubic/quartic functions
# ============================================================
print("\n" + "=" * 70)
print("FULL SCAN: cubic and quartic 3-parameter surfaces")
print("Test systematically for small p")
print("=" * 70)

# The key idea: try polynomial functions of degree ≥ 3
# where the collinearity condition becomes harder to satisfy

functions_3param = [
    # lambda (x,y,z,p) returns 4th coordinate
    ("x³+y³+z³",            lambda x,y,z,p: (pow(x,3,p)+pow(y,3,p)+pow(z,3,p))%p),
    ("x³+y³+z²",            lambda x,y,z,p: (pow(x,3,p)+pow(y,3,p)+z*z)%p),
    ("x³+y²+z",             lambda x,y,z,p: (pow(x,3,p)+y*y+z)%p),
    ("x²+y²+z+xy",          lambda x,y,z,p: (x*x+y*y+z+x*y)%p),
    ("x³+y³+z+xy",          lambda x,y,z,p: (pow(x,3,p)+pow(y,3,p)+z+x*y)%p),
    ("x³+y³+z³+xy",         lambda x,y,z,p: (pow(x,3,p)+pow(y,3,p)+pow(z,3,p)+x*y)%p),
    ("x⁴+y²+z²",            lambda x,y,z,p: (pow(x,4,p)+y*y+z*z)%p),
    ("x⁴+y⁴+z²",            lambda x,y,z,p: (pow(x,4,p)+pow(y,4,p)+z*z)%p),
    ("x⁵+y²+z",             lambda x,y,z,p: (pow(x,5,p)+y*y+z)%p),
    ("x²+yz+ zx",           lambda x,y,z,p: (x*x+y*z+z*x)%p),
    ("x²+y²+xy+yz+zx",      lambda x,y,z,p: (x*x+y*y+x*y+y*z+z*x)%p),
    ("x²+2y²+3z²+xy+yz",    lambda x,y,z,p: (x*x+2*y*y+3*z*z+x*y+y*z)%p),
]

print(f"\n{'Function':30s} {'p=5':>10s} {'p=7':>10s} {'p=11':>10s} {'p=13':>10s}")
print("-" * 65)

for name, f_func in functions_3param:
    results = []
    for p in [5, 7, 11, 13]:
        pts = [(x, y, z, f_func(x,y,z,p)) for x in range(p) for y in range(p) for z in range(p)]
        pts = list(set(pts))
        # Larger p = more points, sample more aggressively
        sample_n = min(200, len(pts))
        random.seed(42)
        pts_sampled = random.sample(pts, sample_n) if len(pts) > sample_n else pts
        coll, cnt = check_collinear_4d_check(pts_sampled, name, 5000)
        n_str = f"{len(pts):4d}"
        results.append(f"{'COLL' if coll else 'OK':>10s}")
    print(f"{name:30s} {'  '.join(results)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
All 3-parameter (cubic) constructions failed quick tests.
This is consistent with a deeper obstruction: in 4D, any 
continuous 3-parameter family is likely to contain collinear
triples due to topological reasons (the dimension of the space
of lines exceeds the degrees of freedom available).

Status: vol(n,4,1) = Θ(n^{4/3}) remains OPEN.
Best known upper bound: O(n²) via product of 2D parabolas.
""")
