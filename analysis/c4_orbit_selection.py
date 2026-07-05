"""
Direction A: C4 Orbit Selection Conjecture

For even n = 2m, we have an m×m grid of C4 orbits.
Each orbit O(i,j) contains 4 points:
  (i,j), (2m-1-j, i), (2m-1-i, 2m-1-j), (j, 2m-1-i)

We need to select m orbits such that:
  1. In the original n×n grid, each row has exactly 2 points
  2. Each column has exactly 2 points
  3. No three points are collinear

Key observation (from earlier analysis):
- Each C4 orbit contributes 1 point to 4 different rows, forming 2 opposite-row-pairs:
  rows {i, n-1-i} and {j, n-1-j}
- Each opposite-row-pair {r, n-1-r} needs exactly 4 points (2 per row)
- So each row-pair needs to be covered by exactly 2 orbits

This makes it a combinatorial covering problem!
"""
from collections import Counter
from itertools import combinations
import math

def orbit_points(i, j, m):
    """Return the 4 points of C4 orbit O(i,j) for n=2m"""
    n = 2 * m
    return [(i, j), (n-1-j, i), (n-1-i, n-1-j), (j, n-1-i)]

def row_pairs_covered(i, j, m):
    """Which opposite-row-pairs does orbit O(i,j) cover?
    Returns set of frozensets (r1, r2) where r2 = n-1-r1
    """
    n = 2 * m
    pairs = set()
    pairs.add(frozenset([i, n-1-i]))
    pairs.add(frozenset([j, n-1-j]))
    return pairs

def check_selection(selected_orbits, m):
    """Check if selection of orbits satisfies row constraints (2 per row, 2 per col)"""
    n = 2 * m
    row_count = Counter()
    col_count = Counter()
    pts = []
    for (i, j) in selected_orbits:
        for p in orbit_points(i, j, m):
            row_count[p[0]] += 1
            col_count[p[1]] += 1
            pts.append(p)
    
    # Check rows
    if not all(c == 2 for c in row_count.values()):
        return False, 'row fail', pts
    if len(row_count) != n:
        return False, f'row count: {len(row_count)} != {n}', pts
    
    # Check columns
    if not all(c == 2 for c in col_count.values()):
        return False, 'col fail', pts
    if len(col_count) != n:
        return False, f'col count: {len(col_count)} != {n}', pts
    
    # Check no 3 collinear
    for a in range(len(pts)):
        for b in range(a+1, len(pts)):
            x1, y1 = pts[a]
            x2, y2 = pts[b]
            dx, dy = x2-x1, y2-y1
            for c in range(b+1, len(pts)):
                x3, y3 = pts[c]
                if dx * (y3 - y1) == dy * (x3 - x1):
                    return False, 'collinear', pts
    
    return True, 'valid', pts

# ============================================================
# C4 ORBIT COVERAGE: The covering problem
# ============================================================
# For n=2m, each orbit O(i,j) for 0≤i,j<m covers 2 opposite-row-pairs:
#   {i, n-1-i} and {j, n-1-j}
# 
# We need to select m orbits such that each of the m opposite-row-pairs 
# {0,n-1}, {1,n-2}, ..., {m-1,m} is covered exactly TWICE.
#
# This is equivalent to: selecting m pairs (i,j) from an m×m grid such that
# each value 0,1,...,m-1 appears exactly TWICE as either i or j.
#
# That's a (2,2)-regular bipartite incidence structure!

print("=" * 70)
print("Direction A: C4 Orbit Selection - The Row Coverage Problem")
print("=" * 70)

for m in range(3, 9):
    n = 2 * m
    print(f"\n--- n={n} (m={m}) ---")
    
    # All possible orbits (i,j) with 0 ≤ i,j < m
    all_orbits = [(i, j) for i in range(m) for j in range(m)]
    
    # Build incidence: for each opposite-row-pair r, list orbits covering it
    row_pair_orbits = {}
    for r in range(m):
        pair = frozenset([r, n-1-r])
        row_pair_orbits[pair] = []
    for (i, j) in all_orbits:
        for pair in row_pairs_covered(i, j, m):
            if pair in row_pair_orbits:
                row_pair_orbits[pair].append((i, j))
    
    # Print incidence structure
    print(f"  {m} opposite-row-pairs, {m*m} orbits")
    for r in range(m):
        pair = frozenset([r, n-1-r])
        coverage = len(row_pair_orbits[pair])
        print(f"  Row-pair {r}↔{n-1-r}: {coverage} orbits cover it")
    
    # The covering problem: select m orbits, each row-pair covered exactly twice
    # This is equivalent to: each r∈{0,...,m-1} appears exactly twice among the i's and j's
    
    # Count frequency of each r as i and as j among all_orbits
    i_freq = Counter(i for i, j in all_orbits)
    j_freq = Counter(j for i, j in all_orbits)
    total_freq = Counter()
    for i, j in all_orbits:
        total_freq[i] += 1
        total_freq[j] += 1
    print(f"  Each r appears {total_freq[0]} times as i or j in the orbit grid")
    
    # For small m, brute-force count valid selections
    if m <= 6:
        valid_coverings = 0
        total_collinear_free = 0
        
        # Enumerate all C(m^2, m) selections (use smarter enumeration)
        # Each row-pair needs exactly 2 orbits covering it
        # Equivalent: each value 0..m-1 appears exactly 2 times as i or j
        
        from collections import defaultdict
        
        def count_selections(m):
            """Count selections of m orbits where each r∈{0..m-1} appears exactly twice
            This is equivalent to: choose a multiset of size 2m from {0..m-1} where
            each value appears twice, then pair them up into m orbit coordinates.
            
            Step 1: Choose a sequence of 2m values where each appears twice.
            Step 2: Partition into m pairs = orbit coordinates.
            """
            # For small m, just brute force
            all_orbits = [(i, j) for i in range(m) for j in range(m)]
            total = 0
            valid = 0
            collinear_free = 0
            
            for combo in combinations(all_orbits, m):
                total += 1
                if total % 100000 == 0:
                    print(f"    Checked {total}...", end='\r')
                
                # Check row coverage: each r appears exactly twice
                count = Counter()
                for i, j in combo:
                    count[i] += 1
                    count[j] += 1
                
                if all(count[r] == 2 for r in range(m)):
                    valid += 1
                    # Check collinearity
                    ok, reason, _ = check_selection(combo, m)
                    if ok:
                        collinear_free += 1
                        if collinear_free <= 8:
                            print(f"    VALID #{collinear_free}: orbits={sorted(combo)}")
            
            return total, valid, collinear_free
        
        total, valid, cf = count_selections(m)
        print(f"  Total C({m*m},{m}): {total}")
        print(f"  Valid row-coverings: {valid}")
        print(f"  Collinear-free (valid rot4): {cf}")
        if valid > 0:
            print(f"  Fraction collinear-free: {cf/valid*100:.2f}%")

print()
print("=" * 70)
print("Testing explicit construction families")
print("=" * 70)

def check_construction(name, selection_fn, max_m=12):
    print(f"\n--- {name} ---")
    for m in range(3, max_m + 1):
        orbits = selection_fn(m)
        if orbits is None:
            print(f"  m={m}: SKIP (construction not defined)")
            continue
        ok, reason, _ = check_selection(orbits, m)
        if ok:
            print(f"  m={m}: VALID ✅")
        else:
            print(f"  m={m}: FAIL ({reason})")

# Family 1: Superdiagonal cycle - orbits (0,1), (1,2), ..., (m-2,m-1), (m-1,0)
def superdiagonal(m):
    return [(i, (i+1) % m) for i in range(m)]

check_construction("Superdiagonal cycle (i,i+1 mod m)", superdiagonal)

# Family 2: Shift by 2 - orbits (0,2), (1,3), ..., (m-2,0), (m-1,1)
def shift2(m):
    return [(i, (i+2) % m) for i in range(m)]

check_construction("Shift by 2 (i,i+2 mod m)", shift2)

# Family 3: Cross pattern - orbits (0, m-1), (1, m-2), ..., (m-1, 0)
# This is the "reverse" construction
def reverse_cross(m):
    return [(i, m-1-i) for i in range(m)]

check_construction("Reverse cross (i,m-1-i)", reverse_cross)

# Family 4: Pair up - (0,1), (2,3), (4,5), ... needs even m
def paired(m):
    if m % 2 != 0:
        return None
    return [(2*i, 2*i+1) for i in range(m//2)] * 2

check_construction("Paired blocks", paired)

# Family 5: Use diagonal orbits (i,i) for all
def diagonal(m):
    return [(i, i) for i in range(m)]

check_construction("All diagonal (i,i)", diagonal)
