"""
codegree_m37.py -- exact degree & codegree of the rot4-NTIL conflict
hypergraph H_cf at m=37, for the Graves-type (C2)/(C3) check.

H_cf:
  * vertices = the m^2 fundamental cells (|V| = 1369)
  * (X) hyperedges = 3-subsets of cells lying on a common collinear line
    (i.e. whose C4-lift is 3-in-line).  These are the ternary conflicts
    (97% of all conflicts per conflict_hypergraph_params.json).
  * (S) edges    = 2-cell binary conflicts (slope+-1 / heavy-cell); tiny.

We compute, over the FULL cell set (the hypergraph the theorem sees):
  deg3[i]     = # (X) triples containing cell i          (max degree, rank 3)
  co3[i][j]   = # (X) triples containing BOTH cells i,j  (max codegree, rank 3)
and analogous tiny deg2/co2 for (S) (size-2).

Efficient: iterate lines L (cell lists from generate_constraints). For a line
of length L_len, the # of 3-subsets through a fixed cell i in L is C(L_len-1,2),
and through a fixed PAIR {i,j} in L is (L_len-2). Accumulate without storing
all C(1369,3) triples.
"""
import time, sys
from itertools import combinations
sys.path.insert(0, ".")
from solve_m37_r9b import generate_constraints

m = 37
ncell = m * m
t0 = time.time()
reps, line_cons, _ = generate_constraints(m, use_2factor=False)
print(f"[build] {len(reps)} cells, {len(line_cons)} lines in {time.time()-t0:.1f}s",
      flush=True)

deg3 = [0] * ncell          # rank-3 (X) degree per cell
co3 = [[0] * ncell for _ in range(ncell)]   # rank-3 (X) codegree per pair
# (S) size-2: a cell with >=2 lifted points on a line + another cell on that line
deg2 = [0] * ncell
co2 = [[0] * ncell for _ in range(ncell)]

t1 = time.time()
for pos_w in line_cons:
    cells = list(pos_w.keys())
    cnt = {c: pos_w[c] for c in cells}
    L = len(cells)
    # --- (X): all 3-subsets of this line ---
    # degree contribution per cell: C(L-1,2)
    c2 = (L - 1) * (L - 2) // 2
    for c in cells:
        deg3[c] += c2
    # codegree contribution per pair: (L-2)
    for a in range(L):
        ca = cells[a]
        for b in range(a + 1, L):
            cb = cells[b]
            v = L - 2
            co3[ca][cb] += v
            co3[cb][ca] += v
    # --- (S): heavy cell (>=2 lifted pts on line) + another cell on line ---
    heavy = [c for c in cells if cnt[c] >= 2]
    if heavy:
        # every (heavy, other) pair is one size-2 conflict edge
        rest = [c for c in cells if c not in set(heavy)]
        for h in heavy:
            deg2[h] += len(rest)
            for o in rest:
                co2[h][o] += 1
                co2[o][h] += 1

print(f"[loop] done in {time.time()-t1:.1f}s", flush=True)

# statistics
import statistics
max_deg3 = max(deg3)
avg_deg3 = sum(deg3) / ncell
# codegree: only count positive entries
pos_co3 = [co3[i][j] for i in range(ncell) for j in range(i + 1, ncell) if co3[i][j] > 0]
max_co3 = max(pos_co3) if pos_co3 else 0
avg_co3 = sum(pos_co3) / len(pos_co3)
# max degree over a size-2 conflict edge's endpoint (for (C2) rank 2):
max_deg2 = max(deg2)
avg_codeg2 = (sum(co2[i][j] for i in range(ncell) for j in range(i+1, ncell) if co2[i][j] > 0)
              / max(1, sum(1 for i in range(ncell) for j in range(i+1, ncell) if co2[i][j] > 0)))

# total # (X) triples & (S) edges (cross-check against lll_matching.py)
nX = sum(deg3) // 3
nS = sum(deg2) // 2

print("\n==== CONFLICT HYPERGRAPH H_cf (m=37, FULL cell set) ====")
print(f"|V| = {ncell}")
print(f"(X) rank-3 triples N = {nX:,}   (lll_matching reported 30,992,032)")
print(f"  deg3  max = {max_deg3:,}   avg = {avg_deg3:.1f}")
print(f"  co3   max = {max_co3:,}   avg(pos) = {avg_co3:.2f}   #pairs>0 = {len(pos_co3):,}")
print(f"(S) rank-2 edges N = {nS:,}   (lll_matching reported 6,756)")
print(f"  deg2  max = {max_deg2:,}   avg = {sum(deg2)/ncell:.2f}")
print(f"  co2   avg(pos) = {avg_codeg2:.3f}")

# ---- Graves-type (C2)/(C3) check with host degree d = m^2 = 1369 ----
d = ncell
ell = 3
print("\n==== GRAVES / GLOCK-et-al (2407.18144) (C2)(C3) CHECK ====")
print(f"host degree parameter d = |V| = {d}   max conflict size ell = {ell}")
# (C2): Delta(C^(j)) <= ell * d^{j-1}
c2_deg3_bound = ell * d ** (3 - 1)      # j=3
c2_deg2_bound = ell * d ** (2 - 1)      # j=2
print(f"(C2) j=3: deg3 <= {c2_deg3_bound:,}   -> max_deg3={max_deg3:,} "
      f"{'OK' if max_deg3 <= c2_deg3_bound else 'FAIL'}")
print(f"(C2) j=2: deg2 <= {c2_deg2_bound:,}   -> max_deg2={max_deg2:,} "
      f"{'OK' if max_deg2 <= c2_deg2_bound else 'FAIL'}")
# (C3): Delta_{j'}(C^(j)) <= d^{j-j'-eps}  (j=3, j'=2 -> exponent 1-eps)
print("(C3) j=3, j'=2: co3 <= d^(1-eps)  for various eps:")
for eps in (0.5, 0.3, 0.2, 0.1, 0.05):
    bound = d ** (1 - eps)
    print(f"   eps={eps:<4} bound={bound:,.1f}  -> max_co3={max_co3:,} "
          f"{'OK' if max_co3 <= bound else 'FAIL'}")
