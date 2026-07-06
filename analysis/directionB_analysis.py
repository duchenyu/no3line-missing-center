"""
Direction B: Maximum Missing-Center Subset of Vp

Problem: Find the largest subset of Vp = {(x, y, x²+y² mod p)}
such that no distance shell has ≥4 points (missing-spherecenter).

Upper bound: sum over shells of min(|shell|, 3)
This bound is NOT always achievable due to cross-shell collinearity.

p=7:  upper=33, achievable=33  (100%, clean)
p=11: upper=82, achievable=82  (100%, clean)
p=13: upper=118, achievable<118 (collinearity barrier)
p=17: upper=210, achievable=?  (unknown)
p=19: upper=239, achievable=239 (100%, clean)
"""
from collections import Counter
import random

def sq_dist_3d(x, y, z, n):
    return (2*x-(n-1))**2 + (2*y-(n-1))**2 + (2*z-(n-1))**2

def has_collinear(pts):
    n = len(pts)
    for a in range(n):
        for b in range(a+1, n):
            for c in range(b+1, n):
                x1,y1,z1 = pts[a]; x2,y2,z2 = pts[b]; x3,y3,z3 = pts[c]
                dx1, dy1, dz1 = x2-x1, y2-y1, z2-z1
                dx2, dy2, dz2 = x3-x1, y3-y1, z3-z1
                if (dy1*dz2 - dz1*dy2 == 0 and 
                    dz1*dx2 - dx1*dz2 == 0 and 
                    dx1*dy2 - dy1*dx2 == 0):
                    return True, (a,b,c)
    return False, None

def exact_max_mc(p, trials=200):
    """Try to find the largest missing-center subset via random sampling."""
    pts_all = [(x,y,(x*x+y*y)%p) for x in range(p) for y in range(p)]
    
    shells = {}
    for pt in pts_all:
        d2 = sq_dist_3d(*pt, p)
        shells.setdefault(d2, []).append(pt)
    
    underfull = {d2: pts for d2, pts in shells.items() if len(pts) <= 3}
    overfull = {d2: pts for d2, pts in shells.items() if len(pts) > 3}
    must_take = []
    for pts in underfull.values():
        must_take.extend(pts)
    
    upper_bound = len(must_take) + 3 * len(overfull)
    best_clean = 0
    
    for trial in range(trials):
        selection = list(must_take)
        for pts in overfull.values():
            selection.extend(random.sample(pts, 3))
        coll, _ = has_collinear(selection)
        if not coll:
            best_clean = max(best_clean, len(selection))
            if best_clean == upper_bound:
                break
    
    return upper_bound, best_clean

print("=" * 70)
print("Direction B: Max Missing-Center Subset of Vp")
print("=" * 70)

print(f"\n{'p':>3s} | {'N':>4s} | {'upper':>6s} | {'best_clean':>10s} | {'ratio':>6s} | {'clean at upper?':>14s}")
print("-" * 55)
for p in [7, 11, 13, 17, 19, 23]:
    upper, best = exact_max_mc(p, trials=300)
    clean_at_upper = "YES" if best == upper else f"NO (best={best})"
    ratio = best / (p*p)
    print(f"{p:3d} | {p*p:4d} | {upper:6d} | {best:10d} | {ratio:6.3f} | {clean_at_upper:>14s}")

print("\n" + "=" * 70)
print("Summary")
print("=" * 70)
print("""
The maximum missing-center subset of Vp is constrained by TWO factors:
1. Distance shell capacity: at most 3 points per shell
2. Cross-shell collinearity: points from different shells can be collinear

For small p (7, 11, 19), factor 1 alone determines the bound.
For p=13, factor 2 reduces the achievable size below the shell-capacity bound.

This is a constrained optimization problem: select ≤3 points from each
distance shell such that no selected triple is collinear. The solution
requires integer programming or advanced combinatorial search for larger p.
""")
