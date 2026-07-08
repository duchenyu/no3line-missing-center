#!/usr/bin/env python3
"""
D2 deep: C4 solution structure analysis — why solutions become rare.

Instead of Turán bounds (which are too weak), analyze the actual structure
of known C4 solutions to understand the phase transition.

Uses antipodal-pair direction approach: for each solution, group the 2n points
into n antipodal pairs {pt, center_image(pt)} and analyze direction from center.
"""
import os, math, json
from collections import defaultdict, Counter

CACHE = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis\flammenkamp_cache'
ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}

HEAVY = {(1,1), (1,-1), (3,1), (1,3), (3,-1), (1,-3)}

def load_solutions(n):
    """Load all C4 solutions for given n."""
    sols = []
    for ext in ['', '.few']:
        p = os.path.join(CACHE, f'n{n}_rot4{ext}')
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.rstrip()
                    if not line:
                        continue
                    pre = line[0]
                    body = line[1:] if pre in '.:/-ocx+*' else line
                    if len(body) < 2 * n:
                        continue
                    pts = []
                    for r in range(n):
                        c1 = VAL.get(body[2*r])
                        c2 = VAL.get(body[2*r+1])
                        if c1 is None or c2 is None or c1 >= n or c2 >= n:
                            break
                        pts.append((r, c1))
                        pts.append((r, c2))
                    if len(pts) == 2 * n:
                        sols.append(pts)
    return sols

def dir_of(pt, n):
    """Reduced direction from center (even n: center at (n-1)/2)."""
    a = 2*pt[0] - (n-1)
    b = 2*pt[1] - (n-1)
    g = math.gcd(a,b) or 1
    a, b = a//g, b//g
    if a < 0 or (a == 0 and b < 0):
        a, b = -a, -b
    return (a,b)

def extract_orbit_dirs(pts, n):
    """
    Group 2n points into N C4 orbits (each orbit = 4 points),
    compute direction from center for the canonical orbit representative.
    """
    N = n // 2
    used = set()
    dirs = []
    for p in pts:
        if p in used:
            continue
        r, c = p
        # C4 orbit: rotate 90° four times
        orbit = [(r, c), 
                 (c, n-1-r), 
                 (n-1-r, n-1-c), 
                 (n-1-c, r)]
        canon = min(orbit)
        used.update(orbit)
        d = dir_of(canon, n)
        dirs.append(d)
    return dirs  # should have N dirs

print(f"{'='*70}")
print("D2 Deep: C4 Solution Structure Analysis")
print(f"{'='*70}\n")

# Key metrics for each n with known solutions
target_ns = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 54, 56]

for n in target_ns:
    sols = load_solutions(n)
    if not sols:
        print(f"n={n:>3}: NO DATA")
        continue
    
    N = n // 2
    
    # Analyze direction structure per solution
    all_dir_sets = []
    heavy_counts = []
    
    sample = sols[:min(len(sols), 100)]  # cheap, sample up to 100
    for pts in sample:
        dirs = extract_orbit_dirs(pts, n)
        if len(dirs) == N:  # must get exactly N antipodal dirs
            all_dir_sets.append(set(dirs))
            heavy_counts.append(sum(1 for d in dirs if d in HEAVY))
    
    if not all_dir_sets:
        print(f"n={n:>3}: {len(sols)} sols but dir extraction failed")
        continue
    
    # Global direction frequency across all sampled solutions
    dir_freq = Counter()
    for ds in all_dir_sets:
        for d in ds:
            dir_freq[d] += 1
    
    total_unique_dirs = len(dir_freq)
    usable_pct = total_unique_dirs / (N * N) * 100
    avg_heavy = sum(heavy_counts) / len(heavy_counts)
    
    # Jaccard similarity between solution direction sets
    if len(all_dir_sets) >= 2:
        jaccards = []
        k = min(len(all_dir_sets), 30)
        for i in range(k):
            for j in range(i+1, k):
                inter = len(all_dir_sets[i] & all_dir_sets[j])
                union = len(all_dir_sets[i] | all_dir_sets[j])
                if union > 0:
                    jaccards.append(inter / union)
        avg_j = sum(jaccards) / len(jaccards) if jaccards else 0
    else:
        avg_j = 0
    
    top5 = dir_freq.most_common(5)
    top_str = ", ".join([f"({d[0]},{d[1]})={c/len(all_dir_sets)*100:.0f}%" for d, c in top5])
    
    print(f"n={n:>3} (N={N:>2}): {len(sols):>6} sols"
          f"\n  usable dirs={total_unique_dirs:>3}/{N*N:>4} ({usable_pct:.1f}%)"
          f" | avg_heavy={avg_heavy:.2f}"
          f" | Jaccard={avg_j:.3f}"
          f"\n  top dirs: {top_str}")
    
    # Ring distribution for one solution
    pts0 = sample[0]
    X = n - 1
    rings = {}
    for r, c in pts0:
        d2 = (2*r - X)**2 + (2*c - X)**2
        rings[d2] = rings.get(d2, 0) + 1
    mc = not any(v >= 3 for v in rings.values())
    print(f"  example: {len(rings)} rings, MC={mc}, ring_pop={sorted(rings.values())[:10]}")

# Extrapolation to n=76
print(f"\n{'='*70}")
print("Extrapolation to n=76 (N=38)")
print(f"{'='*70}\n")

# Key metrics:
# N=28: 10,441 sols, very diverse (high unique dirs)
# N=36: 1 sol (Heule)
# N=38: ???

# The direction diversity as a fraction of N² tells us how constrained the solution is
# N=28: ~60% of N² directions are used across solutions
# This means ~40% of directions are NEVER used in ANY solution

# As N grows, this fraction may shrink, eventually making it impossible to
# find N compatible directions

print("Direction diversity trend:")
for n in [12, 16, 20, 24, 28, 32, 36, 40, 44]:
    sols = load_solutions(n)
    if not sols:
        continue
    N = n // 2
    all_usable = set()
    for pts in sols[:min(len(sols), 200)]:
        dirs = extract_orbit_dirs(pts, n)
        for d in dirs:
            all_usable.add(d)
    pct = len(all_usable) / (N * N) * 100
    print(f"  n={n:>3} (N={N:>2}): {len(all_usable):>4} usable dirs / {N*N:>4} total = {pct:.1f}%"
          f"  | need {N}")

# The critical question: is there a phase transition where usable_dirs / N² drops below N / N²?
# I.e., usable_dirs < N?

print()
print("Phase transition condition: need {N usable dirs} from {{usable}} pool")
print(f"At N=36 (Heule): 1 solution found → at least 36 usable dirs exist")
print(f"At N=38: unknown")

# Load hypergraph scaling data to compute expected violations
dp = os.path.join(os.path.dirname(__file__), 'c4_hypergraph_scaling.json')
if os.path.exists(dp):
    with open(dp) as f:
        scaling = json.load(f)
    
    print(f"\nHypergraph-based solution probability estimate:")
    for N in [28, 32, 36, 38]:
        entry = next((r for r in scaling['results'] if r['N'] == N), None)
        if entry:
            density = entry['edge_density']
            expected_viol = math.comb(N, 3) * density
            # Probability that a random N-set is a hyperedge-free independent set
            # ≈ (1-density)^C(N,3) ≈ exp(-density * C(N,3)) = exp(-expected_violations)
            prob_random = math.exp(-expected_viol)
            print(f"  N={N:>2}: density={density:.5f}, C(N,3)={math.comb(N,3):>6}, "
                  f"E[viol]={expected_viol:.1f}, P(rand sol)={prob_random:.2e}")
    
    # Estimate using fit
    Ns = [r['N'] for r in scaling['results']]
    for N_pred in [38]:
        # Power law extrapolation
        last_entry = max(scaling['results'], key=lambda r: r['N'])
        last_N = last_entry['N']
        last_density = last_entry['edge_density']
        
        # density(N) ∝ N^exponent
        # From the data: density ∝ N^(-1.496)
        pred_density = last_density * (N_pred / last_N) ** (-1.496)
        expected_viol = math.comb(N_pred, 3) * pred_density
        print(f"\n  Predicted for N={N_pred}: density≈{pred_density:.5f}, "
              f"E[viol]≈{expected_viol:.1f}")
        print(f"  → P(random N-set is C4 sol) ≈ exp(-{expected_viol:.1f}) = {math.exp(-expected_viol):.2e}")
        print(f"  → Expected number of C4 sols in random search ≈ {math.comb(N_pred*N_pred, N_pred) * math.exp(-expected_viol):.0e}")
        print(f"    (but solutions are not random — structure makes them much rarer)")

print(f"\n{'='*70}")
print("Conclusion")
print(f"{'='*70}")
print("""
The C4 phase transition is driven by two competing effects:
1. Hypergraph constraint slowly tightens (~N^1.5 expected violations)
2. The 2-regular bipartite matching constraint adds structure

At N=28 (n=56): 10,441 solutions — abundant
At N=36 (n=72): 1 solution (Heule SAT) — critical regime
At N=38 (n=76): likely 0-1 solutions if any

The hypergraph alone is NOT the bottleneck (probabilistic method gives
α >> N even at N=38). The REAL bottleneck is the intersection of:
  (a) Hypergraph independence (no collinear triples)
  (b) 2-regular bipartite matching (each row/col has degree exactly 2)  
  (c) C4 orbit structure (orbit uniqueness)

These three constraints together create a very narrow feasible set at N~36.
""")
