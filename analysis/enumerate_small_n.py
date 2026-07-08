"""
Exhaustive enumeration of 2-per-row No-Three-In-Line solutions for small n (2-13).
Fills gaps in Flammenkamp cache and extends relaxed-constraint analysis.
"""
import sys
import os
import csv
from itertools import combinations
from collections import Counter
import time

CACHE = os.path.join(os.path.dirname(__file__), '..', 'flammenkamp_cache')
os.makedirs(CACHE, exist_ok=True)

# ============================================================
# 2-per-row solver (backtracking with collinearity check)
# ============================================================
def is_collinear(p1, p2, p3):
    """Check if three points are collinear using cross product."""
    return (p2[1] - p1[1]) * (p3[0] - p1[0]) == (p3[1] - p1[1]) * (p2[0] - p1[0])

class NoThreeSolver2PerRow:
    """Exhaustive search for n×n grid, exactly 2 points per row."""
    
    def __init__(self, n):
        self.n = n
        self.col_pairs = list(combinations(range(n), 2))
        self.solutions = []  # list of point lists
    
    def check_collinearity(self, points, new_points):
        """Check if adding new_points creates any collinear triple."""
        all_pts = points + new_points
        # Only need to check triples involving at least one new point
        m = len(points)
        k = len(all_pts)
        for i in range(m, k):
            for j in range(i + 1, k):
                for l in range(j + 1, k):
                    if is_collinear(all_pts[i], all_pts[j], all_pts[l]):
                        return True
        # Also check triples with old and new points
        for i in range(m):
            for j in range(m, k):
                for l in range(j + 1, k):
                    if is_collinear(all_pts[i], all_pts[j], all_pts[l]):
                        return True
            for j in range(i + 1, m):
                for l in range(m, k):
                    if is_collinear(all_pts[i], all_pts[j], all_pts[l]):
                        return True
        return False
    
    def backtrack(self, row, points):
        if row == self.n:
            # Check column usage: each column exactly 2 times
            col_counts = Counter(p[1] for p in points)
            if all(c == 2 for c in col_counts.values()) and len(col_counts) == self.n:
                self.solutions.append(list(points))
            return
        
        for c1, c2 in self.col_pairs:
            new_pts = [(row, c1), (row, c2)]
            if not self.check_collinearity(points, new_pts):
                self.backtrack(row + 1, points + new_pts)
    
    def solve(self):
        self.solutions = []
        self.backtrack(0, [])
        return self.solutions


# ============================================================
# Relaxed (no row constraint) solver - cell-by-cell backtracking
# ============================================================
class NoThreeSolverRelaxed:
    """Cell-by-cell backtracking for n×n grid, no row constraint."""
    
    def __init__(self, n):
        self.n = n
        self.N = n * n
        self.target = 2 * n
        self.solutions = []
    
    def is_collinear_check(self, points, new_x, new_y):
        """Check if adding (new_x, new_y) creates any collinear triple."""
        for p1 in points:
            for p2 in points:
                if p1 is p2: continue
                if is_collinear(p1, (p2[0], p2[1]), (new_x, new_y)):
                    return True
        return False
    
    def backtrack(self, cell_idx, points):
        if len(points) == self.target:
            self.solutions.append(list(points))
            return
        
        # Prune: not enough remaining cells
        remaining = self.N - cell_idx
        if len(points) + remaining < self.target:
            return
        
        x = cell_idx // self.n
        y = cell_idx % self.n
        
        # Skip this cell
        self.backtrack(cell_idx + 1, points)
        
        # Use this cell (if allowed)
        if not self.is_collinear_check(points, x, y):
            points.append((x, y))
            # Prune: row capacity not exceeded
            row_count = sum(1 for p in points if p[0] == x)
            if row_count <= 2:  # no row constraint
                self.backtrack(cell_idx + 1, points)
            points.pop()
    
    def solve(self):
        self.solutions = []
        self.backtrack(0, [])
        return self.solutions


# ============================================================
# Analysis
# ============================================================
def has_center(n, pts):
    X = n - 1
    rings = Counter()
    for x, y in pts:
        d2 = (2*x - X)**2 + (2*y - X)**2
        rings[d2] += 1
    return any(v >= 3 for v in rings.values())

def analyze_solutions(n, solutions, label=""):
    total = len(solutions)
    missing = sum(1 for pts in solutions if not has_center(n, pts))
    rate = missing / total * 100 if total else 0
    print(f"  n={n:>2} {label}: {total:>8} total, {missing:>8} missing ({rate:.2f}%)")
    return total, missing


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    # Part 1: 2-per-row for n=2..13
    print("=" * 60)
    print("Part 1: 2-per-row enumeration (n=2 to 13)")
    print("=" * 60)
    
    for n in range(2, 14):
        t0 = time.time()
        solver = NoThreeSolver2PerRow(n)
        sols = solver.solve()
        t = time.time() - t0
        total, missing = analyze_solutions(n, sols)
        print(f"       time: {t:.2f}s")
        
        # Save to CSV for verification
        csv_path = os.path.join(os.path.dirname(__file__), '..', f'results/result_n{n}_mode0.csv')
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write("n,total_solutions,with_center,missing_center,time_seconds,mode\n")
            f.write(f"{n},{total},{total-missing},{missing},{t:.2f},0\n")
        print(f"       saved to results/result_n{n}_mode0.csv")
    
    # Part 2: Relaxed constraint for n=4..8
    print()
    print("=" * 60)
    print("Part 2: Relaxed constraint (cell-by-cell, n=4 to 8)")
    print("=" * 60)
    
    for n in range(4, 9):
        t0 = time.time()
        solver = NoThreeSolverRelaxed(n)
        sols = solver.solve()
        t = time.time() - t0
        if sols:
            total, missing = analyze_solutions(n, sols, "relaxed")
            # Save
            csv_path = os.path.join(os.path.dirname(__file__), '..', f'results/result_d4_n{n}.csv')
            with open(csv_path, 'w') as f:
                f.write("n,total_solutions,with_center,missing_center,time_seconds\n")
                f.write(f"{n},{total},{total-missing},{missing},{t:.2f}\n")
            print(f"       time: {t:.2f}s")
        else:
            print(f"  n={n:>2} relaxed: no solutions found or timeout")
