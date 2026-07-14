"""
verify_c4_rings.py -- verify the PROVABLE radial fact and the EMPIRICAL ring law
on all cached rot4 solutions, before README entry.

PROVEN (to be confirmed numerically as a sanity check):
  (a) each C4 orbit of a lifted point is equidistant to the board center
      => all 4 lie on the same ring;
  (b) since a rot4 solution S is C4-invariant and n=2m is even (center is the
      half-integer point (m-1/2,m-1/2), never a lattice point), every orbit has
      size exactly 4, so |S ∩ ring| ≡ 0 (mod 4).

EMPIRICAL (labeled as conjecture in README):
  (c) cell-level "<= 2 cells per ring" law (research_M): at most 2 fundamental
      cells share a ring  <=>  at most 8 board points per ring  <=> occupancy
      in {0,4,8}.
"""
import sys, math
from collections import Counter, defaultdict
sys.path.insert(0, ".")
from solve_m37_r9b import orbit_c4
from quadratic_sidon_completeness import load_known, cell_xy

def ring_of_board_point(X, Y, n):
    c2 = (n - 1)            # 2*center
    return (2 * X - c2) ** 2 + (2 * Y - c2) ** 2   # 4 * squared-dist, integer

def main():
    print("m | #sols | orbit-equidist | ring%%4==0 | <=2 cells/ring | max cells/ring")
    print("-" * 78)
    grand_equi = grand_mod4 = grand_le2 = True
    for m in range(5, 20):
        sols = load_known(m, cap=200)
        if not sols:
            continue
        n = 2 * m
        equi_ok = mod4_ok = le2_ok = True
        max_cells = 0
        for pairs in sols:
            cells = [cell_xy(a, b, m) for (a, b) in pairs]
            # (a) orbit equidistance
            for (x, y) in cells:
                orb = set(orbit_c4((x, y), n))
                rings = {ring_of_board_point(X, Y, n) for (X, Y) in orb}
                if len(rings) != 1:
                    equi_ok = False
                if len(orb) != 4:      # (b) orbit size exactly 4
                    mod4_ok = False
            # (b) board-point occupancy per ring multiple of 4
            board = set()
            for (x, y) in cells:
                board |= set(orbit_c4((x, y), n))
            bc = Counter(ring_of_board_point(X, Y, n) for (X, Y) in board)
            if any(v % 4 != 0 for v in bc.values()):
                mod4_ok = False
        # (c) cell-level <=2 per ring (cell ring = its r=0 board rep ring)
        for pairs in sols:
            cells = [cell_xy(a, b, m) for (a, b) in pairs]
            cc = Counter()
            for (x, y) in cells:
                # representative lifted point of the cell (r=0)
                X, Y = (x, y)
                cc[ring_of_board_point(X, Y, n)] += 1
            mx = max(cc.values())
            max_cells = max(max_cells, mx)
            if mx > 2:
                le2_ok = False
        grand_equi &= equi_ok; grand_mod4 &= mod4_ok; grand_le2 &= le2_ok
        print(f"{m:2d}| {len(sols):5d} | {str(equi_ok):^14} | {str(mod4_ok):^9} |"
              f" {str(le2_ok):^13} | {max_cells}")
    print("-" * 78)
    print(f"PROVEN facts hold on all data: orbit-equidist={grand_equi}, "
          f"ring occupancy %4==0={grand_mod4}")
    print(f"EMPIRICAL law (<=2 cells/ring) holds on all data: {grand_le2}")

if __name__ == "__main__":
    main()
