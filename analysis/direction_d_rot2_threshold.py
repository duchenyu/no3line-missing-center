"""
Direction D: Proving the rot2 UNSAT Threshold at n=31

For rot2 symmetry on odd n=2m+1 grid:
- Points come in antipodal pairs {p, -p} where -(i,j) = (2m-i, 2m-j)
- Center (m,m) is a fixed point (cannot be selected)
- Each pair lies on a unique line through the center
- Need to select n=2m+1 pairs such that:
  1. Each row has exactly 2 points
  2. Each column has exactly 2 points  
  3. No three collinear from selected points

The UNSAT threshold: rot2 has 44,828 solutions at n=29, ZERO at n=31.
Goal: Find a counting/combinatorial proof.

Key idea: For n≥31, any selection of n rot2 pairs collides with itself.
"""

from collections import Counter
import math
from fractions import Fraction

def center_lines(n):
    """Count distinct center-crossing lines (directions) for odd n=2m+1.
    Each line is identified by reduced direction (dx,dy) where gcd(|dx|,|dy|)=1.
    Only count canonical directions (dx>0 or dx=0,dy>0)."""
    m = (n-1)//2
    lines = set()
    for dx in range(-m, m+1):
        for dy in range(-m, m+1):
            if dx == 0 and dy == 0:
                continue
            g = math.gcd(abs(dx), abs(dy))
            dxr, dyr = dx//g, dy//g
            # Canonical form: make first non-zero positive
            if dxr < 0 or (dxr == 0 and dyr < 0):
                dxr, dyr = -dxr, -dyr
            lines.add((dxr, dyr))
    return lines

def line_by_point(n, i, j):
    """Get the canonical center-crossing line through (i,j)."""
    m = (n-1)//2
    dx, dy = i-m, j-m
    if dx == 0 and dy == 0:
        return None
    g = math.gcd(abs(dx), abs(dy))
    dxr, dyr = dx//g, dy//g
    if dxr < 0 or (dxr == 0 and dyr < 0):
        dxr, dyr = -dxr, -dyr
    return (dxr, dyr)

def collinear(p1, p2, p3):
    x1,y1=p1; x2,y2=p2; x3,y3=p3
    return (x2-x1)*(y3-y1) == (x3-x1)*(y2-y1)

def check_rot2_solution(n, pairs):
    """Verify a complete rot2 solution (list of n pairs)."""
    pts = []
    for (i,j) in pairs:
        pts.append((i,j))
        pts.append((n-1-i, n-1-j))
    
    # Row/col check
    rc, cc = Counter(), Counter()
    for i,j in pts:
        rc[i] += 1; cc[j] += 1
    if not (all(c==2 for c in rc.values()) and all(c==2 for c in cc.values())):
        return False
    
    # Collinearity check
    for a in range(len(pts)):
        for b in range(a+1, len(pts)):
            for c in range(b+1, len(pts)):
                if collinear(pts[a], pts[b], pts[c]):
                    return False
    return True

def rot2_available_pairs(n):
    """List all available rot2 pairs (canonical form)."""
    m = (n-1)//2
    pairs = []
    for i in range(n):
        for j in range(n):
            if (i,j) == (m,m): continue  # skip center
            i2, j2 = n-1-i, n-1-j
            if (i2, j2) < (i, j): continue  # avoid duplicate
            pairs.append((i,j))
    return pairs

print("=" * 85)
print("DIRECTION D: PROVING rot2 UNSAT THRESHOLD AT n=31")
print("=" * 85)
print()

# Part 1: Count center-crossing lines
print("--- Part 1: Center-Crossing Line Capacity ---")
print()
print(f"{'n':>3} {'m':>3} {'Lines':>6} {'Need':>5} {'Ratio':>6} {'Available_pairs':>15} {'Pairs/steps':>10}")
print("-" * 55)

for n in range(21, 45, 2):
    m = (n-1)//2
    lines = center_lines(n)
    pairs = rot2_available_pairs(n)
    need = n  # need n pairs
    unique_lines_all = len(lines)
    
    # Count how many pairs are on each line
    line_counts = Counter()
    for (i,j) in pairs:
        l = line_by_point(n, i, j)
        if l: line_counts[l] += 1
    
    # At most 1 pair per line (otherwise 4+ collinear on same line)
    max_pairs = len(line_counts)  # 1 per line
    ratio = need / max_pairs
    
    print(f"{n:>3} {m:>3} {unique_lines_all:>6} {need:>5} {ratio:>5.2f} {len(pairs):>15} {max(line_counts.values()) if line_counts else 0:>10}")

print()
print("Key: need/max_pairs > 1 means impossible (not enough lines)")
print()

# Part 2: Row-column constraints for rot2
print("--- Part 2: Row-Column Pairing Constraints ---")
print()
print("For rot2 on odd n, each pair {(i,j),(2m-i,2m-j)}:")
print("  - If i=m: pair contributes 2 points to row m (center row)")
print("  - If j=m: pair contributes 2 points to col m (center col)")
print("  - Row m needs exactly 2 points → EXACTLY 1 center-row pair")
print("  - Col m needs exactly 2 points → EXACTLY 1 center-col pair")
print()

for n in range(21, 45, 2):
    m = (n-1)//2
    pairs = rot2_available_pairs(n)
    
    # Count pairs by row/col categories
    center_row_pairs = [(i,j) for (i,j) in pairs if i == m]
    center_col_pairs = [(i,j) for (i,j) in pairs if j == m]
    diag_pairs = [(i,j) for (i,j) in pairs if i == m and j == m]  # empty (center excluded)
    center_both = [(i,j) for (i,j) in pairs if i == m and j != m]
    
    print(f"n={n} (m={m}): center_row_pairs={len(center_row_pairs)}, "
          f"center_col_pairs={len(center_col_pairs)}, "
          f"both_axes={len(center_both)}")

print()

# Part 3: The critical threshold - collinearity between pairs on different lines
print()
print("--- Part 3: Cross-Line Collinearity Density ---")
print()
print("For two lines L1 and L2, can pairs from L1 and L2 coexist?")
print("We need: for selected pair p∈L1 and q∈L2, p,-p,q must NOT be collinear.")
print("p,-p,q are collinear iff q lies on line L1.")
print("So pairs from different lines NEVER create collinearity via {p,-p,q}.")
print("BUT: p,q,r could be collinear where r is from a third line L3,")
print("or even a point from one of the same pairs.")
print()

# Compute: for each pair of directions, how many pairs collide?
print("Cross-pair collisions: for each pair of directions (dx1,dy1) and (dx2,dy2),")
print("how many collisions exist?")
print()

for n in [27, 29, 31, 33]:
    m = (n-1)//2
    pairs = rot2_available_pairs(n)
    
    # Build line index
    line_pairs = {}
    for (i,j) in pairs:
        l = line_by_point(n, i, j)
        if l not in line_pairs: line_pairs[l] = []
        line_pairs[l].append((i,j))
    
    lines_list = list(line_pairs.keys())
    n_lines = len(lines_list)
    
    # For each pair of lines, check if they can coexist
    # Two lines can coexist if no point from line1's pair is collinear with
    # any point from line2's pair and the center (or each other)
    compatible = Counter()
    
    for li_idx in range(n_lines):
        l1 = lines_list[li_idx]
        pts1 = line_pairs[l1]
        
        for lj_idx in range(li_idx+1, n_lines):
            l2 = lines_list[lj_idx]
            pts2 = line_pairs[l2]
            
            # Check: does any pair from l1 conflict with any pair from l2?
            conflict = False
            for p in pts1:
                if conflict: break
                for q in pts2:
                    # Check if p, -p, q are collinear (means q is on line L1)
                    if line_by_point(n, q[0], q[1]) == l1:
                        conflict = True
                        break
                    # Check if q, -q, p are collinear (means p is on line L2)
                    if line_by_point(n, p[0], p[1]) == l2:
                        conflict = True
                        break
                    # Check extended collinearity
                    p_neg = (n-1-p[0], n-1-p[1])
                    q_neg = (n-1-q[0], n-1-q[1])
                    if collinear(p, q, p_neg) or collinear(p, q, q_neg):
                        conflict = True
                        break
                    if collinear(p, q_neg, p_neg) or collinear(q, p_neg, q_neg):
                        conflict = True
                        break
            
            if not conflict:
                compatible[(l1, l2)] = True
    
    avg_compat = len(compatible) / max(1, n_lines * (n_lines-1) // 2) * 100
    
    # Key: maximum independent set in the 'compatibility graph'
    # This gives the MAXIMUM number of pairs that can coexist
    # If max < n, then rot2 is UNSAT for this n
    
    # Simple upper bound: greedy by min-conflict
    # For each line, count how many other lines are compatible
    
    line_conflict_count = {}
    for l in lines_list:
        conflicts = 0
        for l2 in lines_list:
            if l != l2:
                if (l, l2) not in compatible and (l2, l) not in compatible:
                    conflicts += 1
        line_conflict_count[l] = conflicts
    
    min_conflict = min(line_conflict_count.values())
    max_conflict = max(line_conflict_count.values())
    avg_conflict = sum(line_conflict_count.values()) / len(line_conflict_count)
    
    print(f"n={n} (m={m}): {n_lines} lines, avg_compat={avg_compat:.1f}%")
    print(f"  Conflict range: {min_conflict}-{max_conflict} (avg={avg_conflict:.1f})")
    
    # How many lines have 0 conflicts?
    zero_conflict = sum(1 for v in line_conflict_count.values() if v == 0)
    low_conflict = sum(1 for v in line_conflict_count.values() if v <= 3)
    print(f"  Lines with 0 conflicts: {zero_conflict}, ≤3 conflicts: {low_conflict}")
    
    # Greedy: pick lines with fewest conflicts first
    lines_sorted = sorted(lines_list, key=lambda l: line_conflict_count[l])
    selected = []
    for l in lines_sorted:
        # Check if compatible with all already selected
        ok = True
        for sel in selected:
            if (l, sel) not in compatible and (sel, l) not in compatible:
                ok = False
                break
        if ok:
            selected.append(l)
    
    print(f"  Greedy max-selectable: {len(selected)} (need {n})")
    
    # Also: the n-1 most-conflicted lines account for how much?
    most_conflicted = sorted(line_conflict_count.values(), reverse=True)
    top10_pct = sum(most_conflicted[:max(1, n_lines//10)]) / (n_lines-1) * 100
    print(f"  Top 10% lines account for {top10_pct:.0f}% of total conflicts")
    print()
