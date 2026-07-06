"""
Systematic investigation of the shifted parabola product construction.

Construction: S(p,k) = {(x, x² mod p, y, y²+s mod p) | 0≤x,y<p, 0≤s<k}

This gives k·p² points in a p×p×p×p bounding box.
We need to find, for each p, the maximum k such that S(p,k) has no 3 collinear.

Goal: Prove k ≥ c·p for some constant c, implying vol(n,4,1) = O(n^{4/3}).
"""
import random, sys, math
random.seed(42)

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

def check_4d_collinear_triples(pts, max_checks=30000):
    """Check for 3 collinear points. Returns (found, count_checked)."""
    n = len(pts)
    if n < 3: return False, 0
    count = 0
    # Systematic sampling: first 30 points x first 50 x next 70
    limit_i = min(30, n)
    limit_j = min(50, n)
    limit_k = min(70, n)
    for i in range(limit_i):
        for j in range(i+1, limit_j):
            for k_idx in range(j+1, limit_k):
                v1 = [pts[j][d] - pts[i][d] for d in range(4)]
                v2 = [pts[k_idx][d] - pts[i][d] for d in range(4)]
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
# Systematic scan: for each prime p, find max k
# ============================================================
print("=" * 70)
print("SYSTEMATIC SCAN: maximum k for shifted parabola product")
print("S(p,k) = {(x, x² mod p, y, y²+s mod p)}")
print("=" * 70)

print(f"\n{'p':>4s} | {'p²':>4s} | {'max_k':>5s} | {'k/p':>5s} | {'max_pts':>7s} | {'factor':>6s} | pattern of successes")
print("-" * 70)

results = {}
for p in range(5, 50):
    if not is_prime(p): continue
    
    p2 = p * p
    successes = []
    failures = []
    
    for k in range(1, p + 1):
        pts = []
        for x in range(p):
            for y in range(p):
                for shift in range(k):
                    pt = (x, (x*x) % p, y, ((y*y) + shift) % p)
                    pts.append(pt)
        pts = list(set(pts))
        
        if len(pts) <= p2:
            continue  # no new points added
        
        # Sample for speed for large point sets
        if len(pts) > 800:
            sample = random.sample(pts, 800)
        else:
            sample = pts
        
        coll, _ = check_4d_collinear_triples(sample, 20000)
        
        if not coll:
            successes.append(k)
        else:
            failures.append(k)
    
    max_k = successes[-1] if successes else 0
    k_over_p = max_k / p
    max_pts = max_k * p2 if max_k > 0 else 0
    
    # Show success pattern
    max_block = 0
    if successes:
        # Find max consecutive block
        # Find max consecutive block
        max_block = 0
        curr_block = 0
        for k in range(1, max_k + 1):
            if k in successes:
                curr_block += 1
                max_block = max(max_block, curr_block)
            else:
                curr_block = 0
        
        success_str = f"1-{max_k}" if successes == list(range(1, max_k+1)) else f"{successes[:3]}...{successes[-2:]}" if len(successes) > 5 else str(successes)
    else:
        success_str = "none"
    
    results[p] = {'max_k': max_k, 'k/p': k_over_p, 'max_pts': max_pts}
    
    print(f"{p:4d} | {p2:4d} | {max_k:5d} | {k_over_p:5.3f} | {max_pts:7d} | {max_block:6.1f}x | k={success_str}")

# Show best results
print("\n" + "=" * 70)
print("BEST RESULTS (highest k/p ratio)")
print("=" * 70)
sorted_results = sorted(results.items(), key=lambda x: -x[1]['k/p'])
print(f"\n{'p':>4s} | {'k':>4s} | {'k/p':>6s} | {'pts':>7s} | {'= vol ratio':>12s}")
print("-" * 35)
for p, info in sorted_results[:15]:
    vol_ratio = f"{info['max_pts']**(1/2):.1f} vs n^{2/3}"
    print(f"{p:4d} | {info['max_k']:4d} | {info['k/p']:6.3f} | {info['max_pts']:7d}")

# ============================================================
# Try to understand the pattern
# ============================================================
print("\n" + "=" * 70)
print("PATTERN ANALYSIS")
print("Which p have k > p/3? k > p/4?")
print("=" * 70)

for threshold, label in [(0.5, "k > p/2"), (0.35, "k > p/3"), (0.25, "k > p/4")]:
    passing = [(p, info) for p, info in results.items() if info['k/p'] > threshold]
    print(f"\n{label}: {len(passing)} primes")
    print(f"  Primes: {[p for p, _ in passing]}")
    if passing:
        avg_kp = sum(info['k/p'] for _, info in passing) / len(passing)
        print(f"  Avg k/p: {avg_kp:.3f}")

# ============================================================
# Deeper investigation: Try proving k = Ω(p)
# The construction fails when 3 points from DIFFERENT shifts
# become collinear. When does this happen?
# ============================================================
print("\n" + "=" * 70)
print("FAILURE ANALYSIS: Why does S(p,k) fail?")
print("=" * 70)

def find_collinear_triple(pts):
    """Find first collinear triple in pts."""
    n = len(pts)
    for i in range(n):
        for j in range(i+1, n):
            for k_idx in range(j+1, n):
                v1 = [pts[j][d] - pts[i][d] for d in range(4)]
                v2 = [pts[k_idx][d] - pts[i][d] for d in range(4)]
                parallel = True
                for d1 in range(4):
                    for d2 in range(d1+1, 4):
                        if v1[d1]*v2[d2] != v1[d2]*v2[d1]:
                            parallel = False
                            break
                    if not parallel: break
                if parallel:
                    return (i, j, k_idx), (pts[i], pts[j], pts[k_idx])
    return None, None

# For a few cases where small k fails, find the collinear triple
print("\nAnalyzing failure cases:")
for p, k in [(7, 2), (11, 3), (17, 3)]:
    pts = []
    for x in range(p):
        for y in range(p):
            for shift in range(k):
                pt = (x, (x*x) % p, y, ((y*y) + shift) % p)
                pts.append(pt)
    pts = list(set(pts))
    idxs, (p1, p2, p3) = find_collinear_triple(pts)
    if idxs:
        print(f"\np={p}, k={k}: collinear triple found")
        print(f"  P1 = {p1}")
        print(f"  P2 = {p2}")
        print(f"  P3 = {p3}")
        # Analyze which shifts they belong to
        def get_shift(pt):
            # pt = (x, x², y, y²+s) → s = pt[3] - pt[2]² mod p
            return pt[3] - (pt[2] * pt[2]) % p
        print(f"  Shift signatures: {get_shift(p1)}, {get_shift(p2)}, {get_shift(p3)}")
    else:
        print(f"p={p}, k={k}: no collinear triple found (passed)")

# ============================================================
# Try the same idea but with x-offset instead of y-offset
# S'(p,k) = {(x, x²+s mod p, y, y² mod p)}
# ============================================================
print("\n" + "=" * 70)
print("VARIANT: shift x instead of y")
print("S'(p,k) = {(x, x²+s mod p, y, y² mod p)}")
print("=" * 70)

print(f"\n{'p':>4s} | {'max_k_xshift':>13s} | {'max_k_yshift':>13s} | {'k/p(x)':>7s} | {'k/p(y)':>7s}")
print("-" * 55)
for p in [7, 11, 13, 17, 19, 23, 29, 31, 37]:
    p2 = p * p
    
    # X-shift
    x_success = []
    for k in range(1, p + 1):
        pts = []
        for x in range(p):
            for y in range(p):
                for shift in range(k):
                    pt = (x, ((x*x) + shift) % p, y, (y*y) % p)
                    pts.append(pt)
        pts = list(set(pts))
        if len(pts) <= p2: continue
        
        sample = random.sample(pts, min(800, len(pts)))
        coll, _ = check_4d_collinear_triples(sample, 20000)
        if not coll:
            x_success.append(k)
    
    max_k_x = x_success[-1] if x_success else 0
    
    # Y-shift (from previous)
    y_success = []
    for k in range(1, p + 1):
        pts = []
        for x in range(p):
            for y in range(p):
                for shift in range(k):
                    pt = (x, (x*x) % p, y, ((y*y) + shift) % p)
                    pts.append(pt)
        pts = list(set(pts))
        if len(pts) <= p2: continue
        
        sample = random.sample(pts, min(800, len(pts)))
        coll, _ = check_4d_collinear_triples(sample, 20000)
        if not coll:
            y_success.append(k)
    
    max_k_y = y_success[-1] if y_success else 0
    
    print(f"{p:4d} | {max_k_x:13d} | {max_k_y:13d} | {max_k_x/p:7.3f} | {max_k_y/p:7.3f}")

# ============================================================
# Try symmetrical 2D offset: shift BOTH x² and y²
# ============================================================
print("\n" + "=" * 70)
print("VARIANT: symmetrical shift (x²+s, y²+s)")
print("S''(p,k) = {(x, x²+s mod p, y, y²+s mod p)}")
print("=" * 70)

for p in [11, 13, 17, 19]:
    p2 = p * p
    successful = []
    for k in range(1, p + 1):
        pts = []
        for x in range(p):
            for y in range(p):
                for shift in range(k):
                    pt = (x, ((x*x) + shift) % p, y, ((y*y) + shift) % p)
                    pts.append(pt)
        pts = list(set(pts))
        if len(pts) <= p2: continue
        
        sample = random.sample(pts, min(800, len(pts)))
        coll, _ = check_4d_collinear_triples(sample, 20000)
        if not coll:
            successful.append(k)
    
    max_k = successful[-1] if successful else 0
    print(f"  p={p}: max_k={max_k}, k/p={max_k/p:.3f}, pts={max_k*p2 if max_k else 0}")
