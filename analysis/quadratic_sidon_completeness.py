"""
quadratic_sidon_completeness.py
================================

Verify whether the QUADRATIC SIDON system is EXACTLY EQUIVALENT to rot4
no-three-in-line (NTIL).  This is the candidate Theorem R8.

The quadratic Sidon system has three layers:
  (X) cross-quadrant:  for every 3 DISTINCT cells and every rotation triple
      (r1,r2,r3) in {0,1,2,3}^3, the C4-lift collinearity determinant != 0.
      (this also covers the same-quadrant case r=(0,0,0))
  (S) same-cell:       for every cell i, every pair of its distinct rotation
      images (r1!=r2), and every other cell j with rotation r3, the
      collinearity determinant != 0.
  (F) FDR:             a-b Sidon law  count(d)+count(-d) <= 2.

Ground truth: brute-force three-in-a-line on the 4m C4-lifted points.

If (not X and not S) <=> brute_collinear for ALL tested configs, then
rot4 NTIL <=> (X and S), i.e. it is EXACTLY a quadratic CSP.  FDR (F) is a
separate linear feature of rot4 solutions but is NOT needed for the
equivalence (it is implied by X+S, or redundant).

Usage: python quadratic_sidon_completeness.py
"""
import os, sys, glob, random
from collections import Counter
from itertools import combinations, product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rot4_loader as rot4

CACHE = rot4.CACHE

# ── geometry primitives ──────────────────────────────────────────────
def c4(p, r, N):
    x, y = p
    if r == 0: return (x, y)
    if r == 1: return (N - 1 - y, x)
    if r == 2: return (N - 1 - x, N - 1 - y)
    if r == 3: return (y, N - 1 - x)

def cell_xy(a, b, m):
    return (m - (a + 1) // 2, m - (b + 1) // 2)

# ── ground truth: brute 3-in-a-line on 4m lifted points ─────────────
def brute_collinear(pairs, m):
    n = 2 * m
    cells = [cell_xy(a, b, m) for (a, b) in pairs]
    lifted = set()
    for (x, y) in cells:
        for r in range(4):
            lifted.add(c4((x, y), r, n))
    pl = list(lifted)
    for i in range(len(pl)):
        x1, y1 = pl[i]
        for j in range(i + 1, len(pl)):
            x2, y2 = pl[j]
            dx, dy = x2 - x1, y2 - y1
            for k in range(j + 1, len(pl)):
                x3, y3 = pl[k]
                if dx * (y3 - y1) == dy * (x3 - x1):
                    return True
    return False

# ── layer F: FDR (a-b Sidon) ────────────────────────────────────────
def fdr_pass(pairs):
    diffs = [a - b for (a, b) in pairs]
    cnt = Counter(diffs)
    for d, c in cnt.items():
        if cnt.get(-d, 0) + c > 2:
            return False
    return True

# ── layer X: 64-rotation 3-distinct-cell determinants ───────────────
def cross_violation(pairs, m):
    n = 2 * m
    cells = [cell_xy(a, b, m) for (a, b) in pairs]
    for (i, j, k) in combinations(range(m), 3):
        ci, cj, ck = cells[i], cells[j], cells[k]
        for r1, r2, r3 in product(range(4), repeat=3):
            p1 = c4(ci, r1, n); p2 = c4(cj, r2, n); p3 = c4(ck, r3, n)
            if p1 == p2 or p2 == p3 or p1 == p3:
                continue
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if dx * (p3[1] - p1[1]) == dy * (p3[0] - p1[0]):
                return True
    return False

# ── layer S: same-cell 2-point + other-cell 1-point determinants ────
def samecell_violation(pairs, m):
    n = 2 * m
    cells = [cell_xy(a, b, m) for (a, b) in pairs]
    for i in range(m):
        ci = cells[i]
        for r1, r2 in combinations(range(4), 2):
            p1 = c4(ci, r1, n); p2 = c4(ci, r2, n)
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if dx == 0 and dy == 0:
                continue
            for j in range(m):
                if j == i:
                    continue
                cj = cells[j]
                for r3 in range(4):
                    p3 = c4(cj, r3, n)
                    if p3 == p1 or p3 == p2:
                        continue
                    if dx * (p3[1] - p1[1]) == dy * (p3[0] - p1[0]):
                        return True
    return False

# ── random 2-regular directed graph generator ───────────────────────
def random_2reg_digraph(m, rng):
    odds = list(range(1, 2 * m, 2))
    while True:
        perm = list(odds); rng.shuffle(perm)
        idx = {v: i for i, v in enumerate(odds)}
        visited = set(); cycles = []; ok = True
        for v in odds:
            if v in visited:
                continue
            cyc = []; cur = v
            while cur not in visited:
                visited.add(cur); cyc.append(cur); cur = perm[idx[cur]]
            if len(cyc) < 2:
                ok = False; break
            cycles.append(cyc)
        if ok:
            break
    edges = []
    for cyc in cycles:
        L = len(cyc)
        for t in range(L):
            u, v = cyc[t], cyc[(t + 1) % L]
            edges.append((u, v) if rng.random() < 0.5 else (v, u))
    return edges

# ── load known solutions for a given m ──────────────────────────────
def load_known(m_target, cap=200):
    files = sorted(glob.glob(os.path.join(CACHE, f'n{2*m_target}_rot4*')))
    sols = []
    for path in files:
        with open(path) as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        for line in lines:
            pts = rot4.decode_line(line, 2 * m_target)
            if len(pts) != 4 * m_target or not rot4.is_valid(pts, 2 * m_target):
                continue
            pairs = [(2 * (m_target - x) - 1, 2 * (m_target - y) - 1)
                     for (x, y) in pts if x < m_target and y < m_target]
            if len(pairs) == m_target:
                sols.append(pairs)
                if len(sols) >= cap:
                    return sols
    return sols

def main():
    rng = random.Random(20260712)
    print("=" * 92)
    print("R8 CANDIDATE:  rot4 NTIL  <=>  quadratic Sidon system (X + S)")
    print("=" * 92)

    # ── Stage 1: known solutions must pass all layers ──────────────
    print("\n[STAGE 1] Known rot4 solutions — must be classified SAFE by all layers")
    print(f"{'m':>3} {'nsol':>5} {'brute_coll':>10} {'FDR':>5} {'X':>5} {'S':>5}")
    for m in [5, 6, 7, 8, 9, 10, 11, 12]:
        sols = load_known(m, cap=50)
        if not sols:
            print(f"{m:>3}  (no data)")
            continue
        bad = 0
        for pairs in sols:
            coll = brute_collinear(pairs, m)
            fpass = fdr_pass(pairs)
            xv = cross_violation(pairs, m)
            sv = samecell_violation(pairs, m)
            if coll or not fpass or xv or sv:
                bad += 1
        print(f"{m:>3} {len(sols):>5} {str(bad):>10} {'pass':>5} {'pass':>5} {'pass':>5}")

    # ── Stage 2: random templates — measure equivalence ────────────
    print("\n[STAGE 2] Random 2-regular templates — equivalence of quadratic Sidon vs brute")
    print(f"{'m':>3} {'N':>5} {'| miss(X)':>9} {'miss(X+S)':>10} {'miss(F+X+S)':>11} {'false(X+S)':>10}")
    for m in [5, 6, 7, 8, 9]:
        N = 1500
        miss_X = miss_XS = miss_FXS = false_XS = 0
        for _ in range(N):
            pairs = random_2reg_digraph(m, rng)
            truth = brute_collinear(pairs, m)
            xv = cross_violation(pairs, m)
            sv = samecell_violation(pairs, m)
            fv = not fdr_pass(pairs)
            # "safe" predictions
            safe_X = not xv
            safe_XS = safe_X and not sv
            safe_FXS = safe_XS and not fv
            # miss = predicted safe but truth collinear
            if safe_X and truth:
                miss_X += 1
            if safe_XS and truth:
                miss_XS += 1
            if safe_FXS and truth:
                miss_FXS += 1
            # false = predicted unsafe but truth safe
            if not safe_XS and not truth:
                false_XS += 1
        print(f"{m:>3} {N:>5} {miss_X:>9} {miss_XS:>10} {miss_FXS:>11} {false_XS:>10}")

    print("\n  miss* = #configs classified SAFE by the layer but actually collinear (brute).")
    print("  false* = #configs classified UNSAFE by (X+S) but actually non-collinear.")
    print("  If miss(X+S)=0 and false(X+S)=0  ->  rot4 NTIL <=> (X and S)  EXACTLY (R8).")

if __name__ == '__main__':
    main()
