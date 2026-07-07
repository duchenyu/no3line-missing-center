"""
Fast Python enumeration to fill data gaps in local cache.
Only runs for n values where we don't already have Flammenkamp data.
"""
import sys, os, time, itertools
from collections import Counter

CACHE = os.path.join(os.path.dirname(__file__), '..', 'flammenkamp_cache')
RESULTS = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS, exist_ok=True)

# ============================================================
# Optimized 2-per-row solver using bit masks
# ============================================================
class FastSolver2PerRow:
    def __init__(self, n):
        self.n = n
        # Precompute all column pairs as (c1, c2, bitmap)
        self.pairs = []
        for c1, c2 in itertools.combinations(range(n), 2):
            mask = (1 << c1) | (1 << c2)
            self.pairs.append((c1, c2, mask))
        
        # For collinearity check: precompute cross-product
        # Three points (r1,c1), (r2,c2), (r3,c3) are collinear iff
        # (r2-r1)*(c3-c1) == (r3-r1)*(c2-c1)
        
    def check_row(self, r1, c1, r2, c2, r3, c3):
        """Quick collinearity check."""
        return (r2 - r1) * (c3 - c1) == (r3 - r1) * (c2 - c1)
    
    def solve(self):
        n = self.n
        solutions = []
        col_used = 0  # bitmask of columns used so far
        
        # State: (row, [(r,c), ...], col_bitmask)
        # Use iterative backtracking with precomputed data
        
        def backtrack(row, points, col_mask):
            if row == n:
                # Check each column used exactly twice
                if col_mask == (1 << n) - 1:
                    # Column count check passed in recursion
                    solutions.append(list(points))
                return
            
            for c1, c2, pair_mask in self.pairs:
                # Quick column check
                new_col_mask = col_mask | pair_mask
                
                # Check collinearity with all existing pairs
                ok = True
                for i in range(len(points) - 1):
                    r1, c1_i = points[i]
                    for j in range(i + 1, len(points)):
                        r2, c2_j = points[j]
                        if self.check_row(r1, c1_i, r2, c2_j, row, c1) or \
                           self.check_row(r1, c1_i, r2, c2_j, row, c2):
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    continue
                
                backtrack(row + 1, points + [(row, c1), (row, c2)], new_col_mask)
        
        backtrack(0, [], 0)
        return solutions


# ============================================================
# Check what we already have
# ============================================================
def has_cache(n):
    """Check if Flammenkamp cache has data for this n."""
    files = [f for f in os.listdir(CACHE) if f.startswith(f'n{n}_')]
    return len(files) > 0

# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    def has_center(n, pts):
        X = n-1; rings = Counter()
        for x,y in pts: rings[(2*x-X)**2+(2*y-X)**2] += 1
        return any(v>=3 for v in rings.values())
    
    # Only fill n where cache is missing (n=2, 4, 6)
    print("=== 2-per-row enumeration (missings from cache) ===")
    for n in [2, 3, 4, 5, 6]:
        if has_cache(n):
            print(f"n={n}: already in cache, skip")
            continue
        
        t0 = time.time()
        solver = FastSolver2PerRow(n)
        sols = solver.solve()
        t = time.time() - t0
        
        missing = sum(1 for s in sols if not has_center(n, s))
        total = len(sols)
        print(f"n={n}: {total} total, {missing} missing ({t:.2f}s)")
        
        # Save CSV
        with open(os.path.join(RESULTS, f'result_n{n}_mode0.csv'), 'w') as f:
            f.write("n,total_solutions,with_center,missing_center,time_seconds,mode\n")
            f.write(f"{n},{total},{total-missing},{missing},{t:.2f},0\n")
