"""
Por-Wood 3D Construction Analysis:
1. Generate Vp = {(x, y, (x²+y²) mod p)} for primes p ≡ 3 (mod 4)
2. For n ≤ 10, find all valid constructions and project onto XY/XZ/YZ
3. Check if projections are valid 2D No-Three-In-Line solutions
4. Also check missing-center (missing-spherecenter) property
"""
from collections import Counter
import math

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def porwood_Vp(p):
    """Por-Wood construction: {(x, y, (x²+y²) mod p)}"""
    pts = []
    for x in range(p):
        for y in range(p):
            z = (x*x + y*y) % p
            pts.append((x, y, z))
    return pts

def sq_dist_3d(x, y, z, n):
    """Squared distance from grid center"""
    cx = 2*x - (n-1)
    cy = 2*y - (n-1)
    cz = 2*z - (n-1)
    return cx*cx + cy*cy + cz*cz

def check_collinear_3d(pts):
    """Check if any 3 points are collinear"""
    for a in range(len(pts)):
        for b in range(a+1, len(pts)):
            for c in range(b+1, len(pts)):
                x1,y1,z1 = pts[a]
                x2,y2,z2 = pts[b]
                x3,y3,z3 = pts[c]
                # Check collinearity using cross product
                dx1, dy1, dz1 = x2-x1, y2-y1, z2-z1
                dx2, dy2, dz2 = x3-x1, y3-y1, z3-z1
                cross = (dy1*dz2 - dz1*dy2,
                         dz1*dx2 - dx1*dz2,
                         dx1*dy2 - dy1*dx2)
                if cross[0] == 0 and cross[1] == 0 and cross[2] == 0:
                    return True, pts[a], pts[b], pts[c]
    return False, None, None, None

def check_collinear_2d(pts):
    """Check if any 3 2D points are collinear"""
    for a in range(len(pts)):
        for b in range(a+1, len(pts)):
            for c in range(b+1, len(pts)):
                x1,y1 = pts[a]
                x2,y2 = pts[b]
                x3,y3 = pts[c]
                if (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1):
                    return True
    return False

def is_missing_center_3d(pts, n):
    """Check if no 4 points share same d² from center (3D)"""
    distrib = Counter(sq_dist_3d(*p, n) for p in pts)
    max_pop = max(distrib.values())
    return max_pop < 4, max_pop, distrib

def project(pts, plane):
    """Project 3D points onto a plane:
    'xy': (x,y), 'xz': (x,z), 'yz': (y,z)"""
    if plane == 'xy':
        return [(x, y) for (x, y, z) in pts]
    elif plane == 'xz':
        return [(x, z) for (x, y, z) in pts]
    elif plane == 'yz':
        return [(y, z) for (x, y, z) in pts]

def count_per_row_col(pts, n):
    """Count points per row and per column"""
    rc, cc = Counter(), Counter()
    for x, y in pts:
        rc[x] += 1
        cc[y] += 1
    return rc, cc

# ============================================================
# Part 1: Generate Por-Wood constructions for small primes
# ============================================================
print("=" * 70)
print("Por-Wood 3D Constructions Vp for primes p ≡ 3 (mod 4)")
print("=" * 70)

primes_34 = [p for p in range(2, 30) if is_prime(p) and p % 4 == 3]
print(f"Available primes: {primes_34}")

for p in primes_34:
    pts = porwood_Vp(p)
    ok, *coll = check_collinear_3d(pts)
    mc, maxpop, distrib = is_missing_center_3d(pts, p)
    
    print(f"\np={p}: {len(pts)} points in {p}×{p}×{p} grid")
    print(f"  No 3 collinear: {'✅' if not ok else '❌ FOUND!'}")
    print(f"  Missing-spherecenter: {'✅' if mc else '❌ max_pop='+str(maxpop)}")
    
    if not mc:
        # Show which spherical shells have >=4 points
        bad = {k:v for k,v in sorted(distrib.items()) if v >= 4}
        print(f"  Problem shells (d² → count): {bad}")
    
    # XY projection
    for plane in ['xy', 'xz', 'yz']:
        proj = project(pts, plane)
        n_unique = len(set(proj))
        has_coll = check_collinear_2d(proj)
        rc, cc = count_per_row_col(proj, p)
        max_r = max(rc.values())
        max_c = max(cc.values())
        marker = " ❌ COLLINEAR" if has_coll else ""
        print(f"  Projection on {plane}: {n_unique} unique pts, max_r={max_r}, max_c={max_c}{marker}")

# ============================================================
# Part 2: Detailed projection analysis for n ≤ 10
# ============================================================
print("\n" + "=" * 70)
print("Part 2: Detailed projection analysis for n ≤ 10")
print("=" * 70)

for n in range(2, 11):
    print(f"\n--- n={n} ---")
    
    # Find primes p ≡ 3 (mod 4) where p ≤ n
    valid_primes = [p for p in primes_34 if p <= n]
    if not valid_primes:
        print("  No valid prime p ≡ 3 (mod 4) ≤ n")
        continue
    
    for p in valid_primes:
        pts = porwood_Vp(p)
        # Check if Vp fits in n×n×n grid
        assert all(0 <= v < n for pt in pts for v in pt), f"V_{p} doesn't fit in {n}×{n}×{n}"
        
        print(f"\n  V_{p}: {len(pts)} points")
        
        # XXX: Also try the "sliced" construction from the paper for n > p
        # But for now, just use Vp

        # Check missing-center for grid size n
        mc, maxpop, distrib = is_missing_center_3d(pts, n)
        print(f"  Missing-spherecenter (grid {n}): {'✅' if mc else '❌ max_pop='+str(maxpop)}")
        
        # Check projections
        for plane in ['xy', 'xz', 'yz']:
            proj = project(pts, plane)
            proj_unique = list(set(proj))
            has_coll = check_collinear_2d(proj_unique)
            
            # Check if projection is a valid 2D no-3-in-line solution
            # For a p×p grid, a valid 2D configuration has ≤ 2p points
            # But Vp has p² points projected...
            # Let's check unique points
            n_proj = len(proj_unique)
            
            # What's the max points per row/col in the projection?
            rc, cc = count_per_row_col(proj, p)
            max_r = max(rc.values())
            max_c = max(cc.values())
            
            marker = " ⚠️ COLLINEAR" if has_coll else ""
            marker2 = " ⚠️ >2/row" if max_r > 2 else ""
            marker3 = " ⚠️ >2/col" if max_c > 2 else ""
            print(f"    {plane}-projection: {n_proj} unique pts, max_r={max_r}, max_c={max_c}{marker}{marker2}{marker3}")

# ============================================================
# Part 3: Extended - try larger n with "sliced" construction
# ============================================================
print("\n" + "=" * 70)
print("Part 3: Extended - Por-Wood's 'sliced' construction")
print("For n=10, use p=7, tile into (ceil(n/p)×p×p box)")
print("=" * 70)

def porwood_sliced(n, p):
    """Sliced construction from Lemma 6:
    Take prime p ≡ 3 (mod 4), use ceil(n/p)×p×p bounding box.
    For each copy of Vp at z-offset k*p, shift coordinates."""
    pts = []
    n_blocks = (n + p - 1) // p  # ceil(n/p)
    for k in range(n_blocks):
        offset_z = k * p
        for x in range(p):
            for y in range(p):
                z = (x*x + y*y) % p + offset_z
                if z < n:  # clip to n
                    pts.append((x, y, z))
    return pts

n_test = 10
for p in primes_34:
    if p > n_test: continue
    pts = porwood_sliced(n_test, p)
    ok, *coll = check_collinear_3d(pts)
    mc, maxpop, distrib = is_missing_center_3d(pts, n_test)
    
    print(f"\nn={n_test}, p={p}: {len(pts)} points (sliced)")
    print(f"  No 3 collinear: {'✅' if not ok else '❌ FOUND!'}")
    print(f"  Missing-spherecenter: {'✅' if mc else '❌ max_pop='+str(maxpop)}")
    
    # Projections
    for plane in ['xy', 'xz', 'yz']:
        proj = project(pts, plane)
        proj_unique = list(set(proj))
        has_coll = check_collinear_2d(proj_unique)
        rc, cc = count_per_row_col(proj, n_test)
        max_r = max(rc.values())
        max_c = max(cc.values())
        marker = " ❌ COLLINEAR" if has_coll else ""
        marker2 = f" ⚠️ max_r={max_r}>2" if max_r > 2 else ""
        marker3 = f" ⚠️ max_c={max_c}>2" if max_c > 2 else ""
        print(f"  {plane}-proj: {len(proj_unique)} unique, {marker}{marker2}{marker3}")

# ============================================================
# Part 4: Draw side-by-side projection visualization
# ============================================================
print("\n" + "=" * 70)
print("Part 4: Visual comparison of V_7 3D → 2D projections vs 2D solutions")
print("=" * 70)

p = 7
pts = porwood_Vp(p)
print(f"\nV_{p} = {{(x, y, (x²+y²) mod {p})}}")
print("=" * 50)

for plane in ['xy', 'xz', 'yz']:
    proj = project(pts, plane)
    proj_set = sorted(set(proj))
    print(f"\n{plane}-projection ({len(proj_set)} unique points):")
    
    # Draw a p×p grid
    grid_str = ""
    for y in range(p-1, -1, -1):
        row = ""
        for x in range(p):
            if plane == 'xy':
                pt = (x, y)
            elif plane == 'xz':
                pt = (x, y)
            else:  # yz
                pt = (y, x)  # (y,z) with y=row, x=col
            row += "●" if pt in proj_set else "·"
        grid_str += f"  {y}: {row}\n"
    print(grid_str)

    # Row/col distribution
    rc, cc = Counter(), Counter()
    for x, y in proj:
        rc[x] += 1
        cc[y] += 1
    print(f"  Row counts: {dict(sorted(rc.items()))}")
    print(f"  Col counts: {dict(sorted(cc.items()))}")
