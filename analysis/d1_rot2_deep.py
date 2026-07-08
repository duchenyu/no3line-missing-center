#!/usr/bin/env python3
"""
D1 deep: rot2 UNSAT at n=31 — bipartite matching analysis.

Hypothesis: The UNSAT at n=31 is caused by a constraint density / Hall-type
violation in the bipartite matching, driven by the number-theoretic structure
of (n²-1)/4 = (n-1)(n+1)/4.
"""
import os, math, json
from collections import defaultdict

OUT_DIR = r'D:\djr82\Documents\workbuddy\2026-07-03-16-29-36\no3line-publish\analysis'

def analyze_rot2_bipartite():
    """Analyze the rot2 constraint as a bipartite matching problem."""
    
    print(f"{'='*70}")
    print("D1 Deep: rot2 Bipartite Matching Analysis")
    print(f"{'='*70}\n")
    
    for n in range(7, 39, 2):
        m = (n - 1) // 2
        
        # For rot2 on odd n:
        # - Each of (m+1) domain rows must select 2 columns
        # - Each direction can be used at most once (direction uniqueness)
        # - The direction of cell (r,c) in domain is: reduced vector (r-m, c-m)
        
        # Count available directions
        directions = defaultdict(list)  # direction -> list of domain cells
        for r in range(m + 1):
            for c in range(2 * m + 1):
                if r == m and c == m:
                    continue  # center cell
                a = r - m
                b = c - m
                if a == 0 and b == 0:
                    continue
                g = abs(math.gcd(a, b)) or 1
                a //= g
                b //= g
                if a < 0 or (a == 0 and b < 0):
                    a, b = -a, -b
                directions[(a, b)].append((r, c))
        
        # Count cells per row
        cells_per_row = {r: 0 for r in range(m + 1)}
        for r in range(m + 1):
            for c in range(2 * m + 1):
                if r == m and c == m:
                    continue
                cells_per_row[r] += 1
        
        # Direction uniqueness analysis
        # Each direction can contribute at most 1 cell to the solution
        # (since selecting 2 cells with same direction from center creates collinearity with center)
        
        dir_sizes = sorted([len(v) for v in directions.values()])
        dir_count = len(directions)
        
        # Need: m+1 rows, each needs 2 cells = 2(m+1) selections
        # But each selection uses a direction → need 2(m+1) distinct directions
        # Actually, each domain row selects 2 cells → each selection takes 1 direction
        # So we need 2(m+1) distinct directions total
        needed_dirs = 2 * (m + 1)
        
        # Maximum possible cells respecting direction uniqueness
        # = sum over directions of min(1, len(dir_cells)) = dir_count
        max_cells_unique = dir_count
        
        # But we also need each row to have exactly 2 cells
        # This is a bipartite matching problem: rows × directions
        # Row r and direction d are compatible if there exists a cell (r,c) with that direction
        
        # Build compatibility matrix
        row_dir_compat = {r: set() for r in range(m + 1)}
        for (a, b), cells in directions.items():
            for r, c in cells:
                row_dir_compat[r].add((a, b))
        
        avg_compat = sum(len(s) for s in row_dir_compat.values()) / (m + 1)
        min_compat = min(len(s) for s in row_dir_compat.values())
        max_compat = max(len(s) for s in row_dir_compat.values())
        
        # The direction uniqueness constraint says:
        # Each row needs 2 cells from distinct directions
        # So each row needs at least 2 compatible directions
        # And the total number of distinct directions used = 2(m+1)
        
        has_enough_dirs = min_compat >= 2
        has_enough_total = max_cells_unique >= needed_dirs
        
        # v₂ analysis: 2-adic valuation of (n²-1)/4
        # (n²-1)/4 = (n-1)(n+1)/4
        nsq_minus_1 = n * n - 1
        v2 = 0
        temp = nsq_minus_1
        while temp % 2 == 0:
            v2 += 1
            temp //= 2
        
        # v₂ of (n-1)(n+1)/4
        # (n-1)(n+1) = n²-1 
        # v₂((n²-1)/4) = v₂(n²-1) - 2
        v2_quarter = max(0, v2 - 2)
        
        print(f"n={n:>3} (m={m:>2}): "
              f"dirs={dir_count:>4}, needed={needed_dirs:>3}, "
              f"enough={'✅' if has_enough_total else '❌'}, "
              f"compat=[{min_compat:>3},{avg_compat:>5.1f},{max_compat:>3}], "
              f"v₂((n²-1)/4)={v2_quarter:>2}")
    
    print()
    print("Key question: why does n=29 → 44,828 solutions but n=31 → 0?")
    print()
    
    # Let's check if there's a specific direction count limitation
    # The directions for rot2 on odd n = 2m+1:
    # Total distinct directions = number of (a,b) with gcd=1, |a|,|b| ≤ m
    # under (a,b) ~ (-a,-b)
    
    print("Direction count formula vs n:")
    for n in [27, 29, 31, 33, 35, 37]:
        m = (n - 1) // 2
        # Count (a,b): |a| ≤ m, |b| ≤ m, gcd=1, (a,b) ≠ (0,0)
        count = 0
        for a in range(-m, m+1):
            for b in range(-m, m+1):
                if a == 0 and b == 0:
                    continue
                g = abs(math.gcd(a, b)) or 1
                a1, b1 = a//g, b//g
                if a1 < 0 or (a1 == 0 and b1 < 0):
                    a1, b1 = -a1, -b1
                if a1 == a and b1 == b:
                    count += 1
        needed = (m + 1) * 2
        surplus = count - needed
        print(f"  n={n:>3}: {count:>4} total dirs, need {needed:>3}, surplus {surplus:>4}")
    
    # Check: does the row m (center row) have a special limitation?
    print()
    print("Center row (r=m) analysis:")
    for n in [27, 29, 31, 33]:
        m = (n - 1) // 2
        center_cells = []
        for c in range(2 * m + 1):
            if c == m: continue  # can't select center
            a, b = 0, c - m
            g = abs(math.gcd(a, b)) or 1
            a, b = a//g, b//g
            if b < 0: b = -b
            center_cells.append(((a, b), c))
        
        dirs_center = len(set(d[0] for d in center_cells))
        print(f"  n={n:>3}: center row has {len(center_cells)} available cells, "
              f"{dirs_center} unique directions (need 2), "
              f"surplus={dirs_center - 2}")
        
        # Each of the 2 selections on center row maps to 2 cells (one on each side of center)
        # The direction from center uniquely determines which column

if __name__ == '__main__':
    analyze_rot2_bipartite()
