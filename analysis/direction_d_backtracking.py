"""
Direction D — Advanced Proof Attempt: Constraint-Driven Backtracking

We encode the rot2 problem with direction constraints and use SAT-style
backtracking to find solutions for n=27,29,31,33.
If UNSAT at n=31, we extract the UNSAT core to show why.

The encoding:
  Variables: for each canonical pair (i,j), selected or not
  Constraints:
    1. Row degrees: for each row i, exactly 2 selected (or 1 for i=m)
    2. Column degrees: for each col j, exactly 2 selected (or 1 for j=m)
    3. Direction uniqueness: no two selected pairs share reduced direction
  
Key theorem (proved above): Constraints 1-3 are EQUIVALENT to the full rot2 problem.
"""

import sys
import math
import time

def canonical_direction(i, j, m):
    """Return canonical direction key for point (i,j) relative to center (m,m)."""
    di, dj = i - m, j - m
    if di == 0 and dj == 0:
        return None
    g = math.gcd(abs(di), abs(dj))
    dr, dc = di // g, dj // g
    if dr < 0 or (dr == 0 and dc < 0):
        dr, dc = -dr, -dc
    return (dr, dc)

def solve_rot2(n):
    """Use constraint propagation + backtracking to find a rot2 solution."""
    m = (n - 1) // 2
    
    # Generate all canonical pairs
    all_pairs = []
    for i in range(n):
        for j in range(n):
            if (i, j) == (m, m):
                continue
            i2, j2 = n - 1 - i, n - 1 - j
            if (i2, j2) < (i, j):
                continue
            dir_key = canonical_direction(i, j, m)
            all_pairs.append((i, j, dir_key))
    
    # Row/col degree targets
    row_target = [2] * n
    col_target = [2] * n
    row_target[m] = 1  # center row needs 1 pair (contributes 2 points)
    col_target[m] = 1  # center col needs 1 pair
    
    print(f"n={n} (m={m}): {len(all_pairs)} canonical pairs")
    print(f"  Row targets (0..{n-1}): center row {m}=1, others=2")
    print(f"  Col targets (0..{n-1}): center col {m}=1, others=2")
    
    # Check total degree sum
    total_row_deg = sum(row_target)
    total_col_deg = sum(col_target)
    print(f"  Total row degree: {total_row_deg}, col degree: {total_col_deg}, pairs needed: {total_row_deg}")
    assert total_row_deg == total_col_deg, f"Row/col degree mismatch: {total_row_deg} != {total_col_deg}"
    
    # Build index: each canonical pair (i,j) contributes to:
    # - Row i and row 2m-i (if i=m: contributes 2 to row m)
    # - Col j and col 2m-j (if j=m: contributes 2 to col m)
    # So we need to track contributions to ALL affected rows/cols
    
    # For each row, list of (contributing_pair, direction, other_affected_row)
    row_pairs = [[] for _ in range(n)]
    col_pairs = [[] for _ in range(n)]
    
    for idx, (i, j, dk) in enumerate(all_pairs):
        # Row contributions
        if i == m:
            # Contributes 2 to row m
            row_pairs[m].append((j, dk, idx, m))  # both contributions go to row m
        else:
            # Contributes 1 to row i and 1 to row 2m-i
            i2 = n - 1 - i
            row_pairs[i].append((j, dk, idx, i2))
            row_pairs[i2].append((j, dk, idx, i))
        
        # Column contributions
        if j == m:
            col_pairs[m].append((i, dk, idx, m))
        else:
            j2 = n - 1 - j
            col_pairs[j].append((i, dk, idx, j2))
            col_pairs[j2].append((i, dk, idx, j))
    
    # Also track pair indices that contribute to each row via antipode
    # For canonical (i,j), the antipode (2m-i,2m-j) contributes to row 2m-i, not i
    # But in our canonical form, i is already in the "upper half"
    
    # Simple backtracking with constraint propagation
    # State: selected set of pair indices
    # Constraints: row degrees, col degrees, direction uniqueness
    
    used_directions = set()
    row_deg_used = [0] * n
    col_deg_used = [0] * n
    selected = []
    pair_selected = [False] * len(all_pairs)
    
    # For fast lookup: which pairs are still available?
    # We'll maintain: for each row, which (j, dir, idx) are still feasible
    
    def prune_and_select():
        """Try to find a solution via greedy + backtracking."""
        nonlocal used_directions, row_deg_used, col_deg_used, selected, pair_selected
        
        # Reset state
        used_directions = set()
        row_deg_used = [0] * n
        col_deg_used = [0] * n
        selected = []
        pair_selected = [False] * len(all_pairs)
        
        # Order pairs by row (process center row first since it's most constrained)
        # Also pre-sort pairs: those from under-constrained rows go later
        
        # Greedy: at each step, pick the most constrained remaining row
        # and try each available pair for it
        
        def backtrack():
            if len(selected) == total_row_deg:
                return True  # Solution found!
            
            # Pick the row with fewest remaining slots (most constrained)
            # but most available pairs
            min_remaining = n + 1
            best_row = -1
            for i in range(n):
                remaining = row_target[i] - row_deg_used[i]
                if remaining > 0:
                    # Count available pairs
                    avail = 0
                    for j, dk, idx in row_pairs[i]:
                        if not pair_selected[idx] and dk not in used_directions \
                           and col_deg_used[j] < col_target[j]:
                            avail += 1
                    if avail == 0 and remaining > 0:
                        return False  # Dead end
                    # Choose row with minimum remaining but non-zero avail
                    # Actually, choose the one with minimum (remaining / max(avail, 1))
                    # to prioritize constrained rows with less choice
                    priority = remaining / max(avail, 1)
                    # Hmm, let's just try the row with minimum avail first
                    if avail < min_remaining or (avail == min_remaining and remaining > 0):
                        min_remaining = avail
                        best_row = i
            
            if best_row == -1:
                return False
            
            i = best_row
            remaining_i = row_target[i] - row_deg_used[i]
            
            # Try each available pair for this row
            candidates = []
            for j, dk, idx in row_pairs[i]:
                if not pair_selected[idx] and dk not in used_directions \
                   and col_deg_used[j] < col_target[j]:
                    candidates.append((j, dk, idx))
            
            # Sort: prefer directions with fewer other options (rare directions first)
            # and columns with fewer remaining slots
            candidates.sort(key=lambda x: (
                sum(1 for _, _, _idx in row_pairs[x[1]] if not pair_selected[_idx]),
                x[0]
            ))
            
            for j, dk, idx in candidates:
                # Select this pair
                pair_selected[idx] = True
                row_deg_used[i] += 1
                col_deg_used[j] += 1
                used_directions.add(dk)
                selected.append((i, j, dk))
                
                if backtrack():
                    return True
                
                # Undo
                selected.pop()
                used_directions.discard(dk)
                col_deg_used[j] -= 1
                row_deg_used[i] -= 1
                pair_selected[idx] = False
            
            return False
        
        found = backtrack()
        if found:
            print(f"  ✓ SOLUTION FOUND! {len(selected)} pairs selected")
            # Verify
            rows_ok = all(row_deg_used[i] == row_target[i] for i in range(n))
            cols_ok = all(col_deg_used[j] == col_target[j] for j in range(n))
            dirs_ok = len(used_directions) == len(selected)
            print(f"    Row constraints satisfied: {rows_ok}")
            print(f"    Col constraints satisfied: {cols_ok}")
            print(f"    Direction uniqueness: {dirs_ok}")
            
            for i, j, dk in selected:
                print(f"    ({i:>2},{j:>2}) dir={dk}")
        else:
            print(f"  ✗ No solution found (backtracking exhausted)")
        
        return found
    
    t0 = time.time()
    result = prune_and_select()
    t1 = time.time()
    print(f"  Time: {t1-t0:.2f}s")
    print()
    return result

# Test
for n in [21, 23, 25, 27, 29, 31, 33]:
    solve_rot2(n)
