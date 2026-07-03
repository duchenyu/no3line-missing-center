#!/usr/bin/env python3
"""Analyze missing-center solutions for n=12"""
import csv
from collections import Counter

N = 12

# Center calculation (same as C++ code)
cx_times2 = N - 1  # even n
cy_times2 = N - 1

def get_dist(c, r):
    dx = 2*c - cx_times2
    dy = 2*r - cy_times2
    return dx*dx + dy*dy

# Read all solutions
solutions = []
with open('sols_n12.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sol = []
        for r in range(N):
            c1 = int(row[f'r{r}c1'])
            c2 = int(row[f'r{r}c2'])
            sol.append((c1, c2))
        solutions.append(sol)

print(f"Total solutions loaded: {len(solutions)}")

# ============================================================================
# ANALYSIS 1: Which distance rings are used/skipped?
# ============================================================================
all_distinct_d = set()
for r in range(N):
    for c in range(N):
        all_distinct_d.add(get_dist(c, r))
all_d_rings = sorted(all_distinct_d)
print(f"\n=== Distance Ring Analysis ===")
print(f"Distinct distance values: {len(all_d_rings)}")

# For each solution, count how many points on each distance ring
ring_usage = {}  # d -> {0: count, 1: count, 2: count}
for d in all_d_rings:
    ring_usage[d] = Counter()

for sol_idx, sol in enumerate(solutions):
    ring_pts = Counter()
    for r, (c1, c2) in enumerate(sol):
        ring_pts[get_dist(c1, r)] += 1
        ring_pts[get_dist(c2, r)] += 1
    
    for d in all_d_rings:
        ring_usage[d][ring_pts.get(d, 0)] += 1

# Show which rings are consistently skipped (0 points in all solutions)
print(f"\nDistance rings that are NEVER used:")
never_used = []
for d in all_d_rings:
    if ring_usage[d][0] == len(solutions):
        never_used.append(d)
        # Find grid points on this ring
        pts = [(r,c) for r in range(N) for c in range(N) if get_dist(c,r) == d]
        print(f"  d={d:4d}  ({len(pts):2d} points: {pts})")
        
print(f"\nDistance rings that are SOMETIMES skipped:")
for d in all_d_rings:
    n_skipped = ring_usage[d][0]
    if 0 < n_skipped < len(solutions):
        pts = [(r,c) for r in range(N) for c in range(N) if get_dist(c,r) == d]
        skip_pct = 100 * n_skipped / len(solutions)
        used2_pct = 100 * ring_usage[d][2] / len(solutions)
        print(f"  d={d:4d}: skipped {n_skipped}/{len(solutions)} ({skip_pct:.0f}%), "
              f"2pts {ring_usage[d][2]}/{len(solutions)} ({used2_pct:.0f}%)  "
              f"({len(pts)} points)")

print(f"\nDistance rings used in ALL solutions (at least 1 pt):")
for d in all_d_rings:
    if ring_usage[d][0] == 0:
        total_pts = sum(ring_usage[d].values())
        avg_pts = sum(k*v for k,v in ring_usage[d].items()) / len(solutions)
        pts = [(r,c) for r in range(N) for c in range(N) if get_dist(c,r) == d]
        print(f"  d={d:4d}: avg {avg_pts:.2f} pts/sol  ({len(pts)} points in grid)")

# ============================================================================
# ANALYSIS 2: Column cycle structure
# ============================================================================
print(f"\n\n=== Column Cycle Analysis ===")
col_pairs_in_sol = Counter()

for sol_idx, sol in enumerate(solutions):
    # Build graph: for each column, which columns is it paired with (in which rows)
    col_adj = {c: [] for c in range(N)}
    for r, (c1, c2) in enumerate(sol):
        col_adj[c1].append(c2)
        col_adj[c2].append(c1)
    # Encode as tuple of tuples for hashing
    cycles = tuple(sorted(tuple(sorted(adj)) for adj in col_adj.values()))
    col_pairs_in_sol[cycles] += 1

print(f"\nColumn pairing patterns appear in {len(col_pairs_in_sol)} configurations:")
for cycles, count in col_pairs_in_sol.most_common(10):
    print(f"  {count:2d} solutions:")

# ============================================================================
# ANALYSIS 3: For each distance ring, which positions are actually used?
# ============================================================================
print(f"\n\n=== Position Analysis per Distance Ring ===")
for d in sorted(all_d_rings):
    ring_pts = [(r,c) for r in range(N) for c in range(N) if get_dist(c,r) == d]
    used_counts = Counter()
    for sol in solutions:
        for r, (c1, c2) in enumerate(sol):
            if get_dist(c1, r) == d:
                used_counts[(r, c1)] += 1
            if get_dist(c2, r) == d:
                used_counts[(r, c2)] += 1
    
    n_pts = len(ring_pts)
    n_used = len(used_counts)
    if n_used > 0:
        usage_str = ", ".join(f"({r},{c}):{n}" for (r,c), n in used_counts.most_common())
        print(f"  d={d:4d} ({n_pts} pts in grid, {n_used} used in any sol):")
        print(f"       {usage_str}")

# ============================================================================
# ANALYSIS 4: Average distance value per solution
# ============================================================================
print(f"\n\n=== Per-Solution Statistics ===")
for sol_idx, sol in enumerate(solutions[:5]):
    all_d = []
    for r, (c1, c2) in enumerate(sol):
        all_d.append(get_dist(c1, r))
        all_d.append(get_dist(c2, r))
    d_counts = Counter(all_d)
    n_unique = len(d_counts)
    n_pairs = sum(1 for v in d_counts.values() if v == 2)
    print(f"  Sol {sol_idx}: {n_unique} unique distances, {n_pairs} pairs, "
          f"avg d={sum(all_d)/len(all_d):.0f}, "
          f"min d={min(all_d)}, max d={max(all_d)}")

# ============================================================================
# ANALYSIS 5: Which cells are most/least popular?
# ============================================================================
print(f"\n\n=== Cell Popularity ===")
cell_usage = Counter()
for sol in solutions:
    for r, (c1, c2) in enumerate(sol):
        cell_usage[(r, c1)] += 1
        cell_usage[(r, c2)] += 1

# Show unused cells
unused = [(r,c) for r in range(N) for c in range(N) if cell_usage[(r,c)] == 0]
print(f"Cells never used in any solution: {len(unused)}")
# Group by distance ring
from collections import defaultdict
unused_by_ring = defaultdict(list)
for r,c in unused:
    unused_by_ring[get_dist(c,r)].append((r,c))
for d, pts in sorted(unused_by_ring.items()):
    print(f"  d={d:4d}: {pts}")

# Most popular cells
print(f"\nMost popular cells:")
for (r,c), count in cell_usage.most_common(10):
    d = get_dist(c,r)
    print(f"  ({r},{c}) d={d}: {count}/{len(solutions)} solutions")
