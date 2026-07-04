#!/usr/bin/env python3
"""
Z3 Unsat Core 分析：为什么 n=8 没有缺失中心解？

用 Z3 的 assert_and_track + unsat_core 找出导致不可行的关键约束。
"""
import sys, math
from collections import defaultdict
from itertools import combinations
from z3 import *

def analyze_unsat(n):
    print(f"="*60)
    print(f"Z3 Unsat Core Analysis: n={n}")
    print(f"="*60)
    
    solver = Solver()
    solver.set("timeout", 60000)
    
    # Variables
    x = [[Bool(f"x_{r}_{c}") for c in range(n)] for r in range(n)]
    x_int = [[If(x[r][c], 1, 0) for c in range(n)] for r in range(n)]
    
    track_names = {}  # track_var -> description
    track_vars = []   # list of (track_var, desc) for mining
    
    cx2 = cy2 = n - 1
    
    print(f"\nAdding constraints with tracking...")
    
    # Row constraints (PbEq exactly 2)
    for r in range(n):
        tv = Bool(f"track_row_{r}")
        solver.assert_and_track(PbEq([(x[r][c], 1) for c in range(n)], 2), tv)
        track_names[tv] = f"Row {r}: exactly 2"
        track_vars.append(tv)
    
    # Column constraints
    for c in range(n):
        tv = Bool(f"track_col_{c}")
        solver.assert_and_track(PbEq([(x[r][c], 1) for r in range(n)], 2), tv)
        track_names[tv] = f"Col {c}: exactly 2"
        track_vars.append(tv)
    
    print(f"  Row/col constraints: {2*n}")
    
    # Line constraints (PbLe at most 2 per non-axis line)
    lines = defaultdict(set)
    line_count = 0
    for r1 in range(n):
        for c1 in range(n):
            for r2 in range(r1, n):
                for c2 in range(n):
                    if r1 == r2 and c1 >= c2: continue
                    if r1 == r2: continue
                    if c1 == c2: continue
                    dr = r2 - r1
                    dc = c2 - c1
                    a, b = dr, -dc
                    c_val = dc*r1 - dr*c1
                    g = math.gcd(math.gcd(abs(a), abs(b)), abs(c_val))
                    if g > 1: a, b, c_val = a//g, b//g, c_val//g
                    if a < 0 or (a == 0 and b < 0):
                        a, b, c_val = -a, -b, -c_val
                    lines[(a,b,c_val)].add((r1,c1))
                    lines[(a,b,c_val)].add((r2,c2))
    
    for (a,b,c_val), pts in lines.items():
        if len(pts) <= 2: continue
        pts_list = list(pts)
        tv = Bool(f"track_line_{line_count}")
        solver.assert_and_track(PbLe([(x[r][c], 1) for (r,c) in pts_list], 2), tv)
        track_names[tv] = f"Line a={a} b={b} c={c_val}: {len(pts_list)} pts"
        track_vars.append(tv)
        line_count += 1
    
    print(f"  Line constraints: {line_count}")
    
    # Ring constraints
    ring_count = 0
    rings = defaultdict(list)
    for r in range(n):
        for c in range(n):
            d = (2*c - cx2)**2 + (2*r - cy2)**2
            rings[d].append((r,c))
    
    for d, pts in rings.items():
        if len(pts) > 2:
            tv = Bool(f"track_ring_{ring_count}")
            solver.assert_and_track(PbLe([(x[r][c], 1) for (r,c) in pts], 2), tv)
            track_names[tv] = f"Ring d={d}: {len(pts)} pts"
            track_vars.append(tv)
            ring_count += 1
    
    print(f"  Ring constraints: {ring_count}")
    print(f"  Total: {2*n + line_count + ring_count}")
    print(f"\nSolving...")
    
    result = solver.check()
    
    if result == unsat:
        core = solver.unsat_core()
        print(f"\n  ✅ UNSATISFIABLE (unsat core has {len(core)} constraints)")
        
        # Analyze core
        core_by_category = defaultdict(int)
        print(f"\n{'='*60}")
        print(f"Unsatisfiable Core Analysis")
        print(f"{'='*60}")
        print(f"\nCore contains {len(core)} constraints:")
        
        for c in core:
            desc = track_names.get(c, "Unknown")
            if desc.startswith("Row"): core_by_category["Row"] += 1
            elif desc.startswith("Col"): core_by_category["Column"] += 1
            elif desc.startswith("Line"): core_by_category["Line"] += 1
            elif desc.startswith("Ring"): core_by_category["Ring"] += 1
            else: core_by_category["Other"] += 1
            print(f"  {desc}")
        
        print(f"\nCore by category:")
        for cat, cnt in sorted(core_by_category.items()):
            print(f"  {cat}: {cnt}")
        
        # Show core analysis only (minimality check requires Z3 API differently)
        print(f"\n{'='*60}")
        print(f"Interpretation")
        print(f"{'='*60}")
        
        # Count by category
        row_in = sum(1 for c in core if str(c).startswith('track_row'))
        col_in = sum(1 for c in core if str(c).startswith('track_col'))
        line_in = sum(1 for c in core if str(c).startswith('track_line'))
        ring_in = sum(1 for c in core if str(c).startswith('track_ring'))
        
        print(f"\nConstraints in unsat core:")
        print(f"  Row constraints:    {row_in}/{n}") 
        print(f"  Column constraints: {col_in}/{n}")
        print(f"  Line constraints:   {line_in}/{line_count}")
        print(f"  Ring constraints:   {ring_in}/{ring_count}")
        
        # Find which specific rings are in the core
        ring_core = []
        for c in core:
            desc = track_names.get(c, "")
            if "Ring" in desc:
                ring_core.append(desc)
        
        if ring_core:
            print(f"\nRings in unsat core:")
            for r in ring_core:
                print(f"  {r}")
        
        line_core = []
        for c in core:
            desc = track_names.get(c, "")
            if "Line" in desc:
                line_core.append(desc)
        
        if line_core:
            print(f"\nLines in unsat core ({len(line_core)}):")
            for l in line_core[:10]:
                print(f"  {l}")
        
    elif result == sat:
        print(f"\n  ✅ SATISFIABLE (no unsat core available)")
    else:
        print(f"\n  ? UNKNOWN")

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    analyze_unsat(n)
