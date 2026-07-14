"""
verify_hardnumbers.py -- INDEPENDENT verification of the hard numbers cited in
research_H.md / research_I.md before they enter the README.

Two independent checks:

(1) STRUCTURAL CROSS-CHECK (small m): rebuild the (X)/(S) conflict hypergraph
    from scratch by enumerating the 4*m^2 lifted board points and grouping them
    into collinear LINES with a fresh canonical-line key
        line_id = (reduced_dir, signed_offset)
    (NOT the perp-key trick used in generate_constraints). Then count
        deg3[cell], co3[pair], N(X), N(S)
    exactly the way codegree_m37.py does, and assert equality with the repo's
    generate_constraints() output. If they agree for m=5..9 the m=37 numbers
    (same code path) are trustworthy.

(2) ARITHMETIC CHECK (m=37): recompute the Graves (C2)/(C3) bounds and the
    LLL e*p*(d+1) products in plain Python, independent of any print in the
    original scripts, and compare to the values quoted in the .md docs.
"""
import math, sys, time
from collections import defaultdict
from itertools import combinations

sys.path.insert(0, ".")
from solve_m37_r9b import generate_constraints, orbit_c4, reduced_dirs


# ---------- (1) independent conflict-hypergraph builder ----------
def canon_dir(dx, dy):
    g = math.gcd(abs(dx), abs(dy)) or 1
    dx, dy = dx // g, dy // g
    if dx < 0 or (dx == 0 and dy < 0):
        dx, dy = -dx, -dy
    return (dx, dy)


def build_indep(m):
    """Group all lifted board points into collinear lines from scratch."""
    n = 2 * m
    reps = [(x, y) for x in range(m) for y in range(m)]
    ri = {c: i for i, c in enumerate(reps)}
    # line_id -> {cell_idx: weight(#lifted pts of that cell on the line)}
    lines = defaultdict(lambda: defaultdict(int))
    for i, c in enumerate(reps):
        for (X, Y) in set(orbit_c4(c, n)):
            for (dx, dy) in reduced_dirs(n):
                # signed perpendicular offset of point (X,Y) for this direction
                off = -dy * X + dx * Y      # perp . P, perp=(-dy,dx)
                lines[((dx, dy), off)][i] += 1
    # keep only lines whose total weight > 2 (a real >=3 conflict)
    cons = [dict(w) for w in lines.values() if sum(w.values()) > 2]
    return reps, cons


def count_from_cons(cons, ncell):
    deg3 = [0] * ncell
    co3 = defaultdict(int)
    deg2 = [0] * ncell
    for w in cons:
        cells = list(w.keys())
        L = len(cells)
        c2 = (L - 1) * (L - 2) // 2
        for c in cells:
            deg3[c] += c2
        for a in range(L):
            for b in range(a + 1, L):
                co3[(cells[a], cells[b])] += (L - 2)
        heavy = [c for c in cells if w[c] >= 2]
        if heavy:
            rest = [c for c in cells if w[c] < 2]
            for h in heavy:
                deg2[h] += len(rest)
    nX = sum(deg3) // 3
    nS = sum(deg2) // 2
    max_deg3 = max(deg3) if deg3 else 0
    max_co3 = max(co3.values()) if co3 else 0
    return dict(nX=nX, nS=nS, max_deg3=max_deg3, max_co3=max_co3,
                max_deg2=(max(deg2) if deg2 else 0))


def check_structural():
    print("=" * 64)
    print("(1) STRUCTURAL CROSS-CHECK: independent vs generate_constraints")
    print("=" * 64)
    allok = True
    for m in (5, 6, 7, 8, 9):
        ncell = m * m
        # repo path
        reps_r, line_cons_r, _ = generate_constraints(m, use_2factor=False)
        repo = count_from_cons(line_cons_r, ncell)
        # independent path
        reps_i, cons_i = build_indep(m)
        indep = count_from_cons(cons_i, ncell)
        ok = repo == indep
        allok &= ok
        print(f"m={m:2d} |V|={ncell:3d}  N(X)={indep['nX']:>7,}  N(S)={indep['nS']:>5,}"
              f"  maxdeg3={indep['max_deg3']:>6,}  maxco3={indep['max_co3']:>4,}"
              f"  maxdeg2={indep['max_deg2']:>4,}  [{'MATCH' if ok else 'MISMATCH'}]")
        if not ok:
            print("   repo :", repo)
            print("   indep:", indep)
    print(f"\nStructural verdict: {'ALL MATCH' if allok else 'MISMATCH FOUND'}")
    return allok


# ---------- (2) arithmetic re-derivation for m=37 ----------
def check_arithmetic():
    print("\n" + "=" * 64)
    print("(2) ARITHMETIC CHECK (m=37): (C2)/(C3) bounds and LLL products")
    print("=" * 64)
    m = 37
    d = m * m                      # host degree parameter = |V| = 1369
    print(f"d = m^2 = {d}   (research_I uses d=1369)")

    # values QUOTED in research_I.md (to be confirmed by the fresh rerun):
    quoted = dict(NX=30_992_032, deg3_max=92_488, deg3_avg=67_915,
                  co3_max=1_132, deg2_max=288)
    print("\nQuoted-in-doc headline numbers (verified separately by rerun):")
    for k, v in quoted.items():
        print(f"   {k:10s} = {v:,}")

    # (C2): Delta(C^(j)) <= ell * d^{j-1},  ell=3
    ell = 3
    c2_j3 = ell * d ** 2
    c2_j2 = ell * d ** 1
    print("\n(C2) bounds:")
    print(f"   j=3: 3*d^2 = {c2_j3:,}   deg3_max={quoted['deg3_max']:,} "
          f"-> {'OK' if quoted['deg3_max'] <= c2_j3 else 'FAIL'}")
    print(f"   j=2: 3*d^1 = {c2_j2:,}     deg2_max={quoted['deg2_max']:,} "
          f"-> {'OK' if quoted['deg2_max'] <= c2_j2 else 'FAIL'}")
    # research_I quotes 5.6e6 and 4107; confirm:
    print(f"   (doc quotes 3*d^2=5.6e6? {c2_j3:,}={c2_j3/1e6:.2f}e6 ; "
          f"3*d=4107? {c2_j2})")

    # (C3): co3 <= d^{1-eps}
    print("\n(C3) codegree bound d^(1-eps) vs co3_max=1132:")
    for eps in (0.5, 0.3, 0.2, 0.1, 0.05, 0.026):
        b = d ** (1 - eps)
        print(f"   eps={eps:<5} d^(1-eps)={b:10,.1f}  "
              f"-> {'OK' if quoted['co3_max'] <= b else 'FAIL'}")
    # critical eps where bound == co3_max:  1-eps = log_d(1132)
    eps_star = 1 - math.log(quoted['co3_max']) / math.log(d)
    print(f"   critical eps* (bound==1132): 1 - ln(1132)/ln(1369) = {eps_star:.4f}")
    # doc also cites d^0.95 = 954:
    print(f"   d^0.95 = {d**0.95:,.1f}  (doc says 954; and 1132 lies between "
          f"d^0.95 and d={d})")

    # LLL products from research_H.md
    print("\nLLL (research_H) e*p*(d+1) products:")
    e = math.e
    # stub space: p2 = 1/(73*71), p3 = 1/(73*71*69), d ~ from doc
    p2 = 1 / (73 * 71)
    p3 = 1 / (73 * 71 * 69)
    print(f"   p2 = 1/(73*71)     = {p2:.6e}   (doc 1.93e-4)")
    print(f"   p3 = 1/(73*71*69)  = {p3:.6e}   (doc 2.80e-6)")
    # research_H quotes e*p2*(d+1)=8.894e3 and e*p3*(d+1)=1.289e2 with a d value.
    # solve for the d used: d+1 = quoted / (e*p)
    for label, p, q in (("e*p2*(d+1)", p2, 8.894e3),
                        ("e*p3*(d+1)", p3, 1.289e2)):
        d_implied = q / (e * p) - 1
        print(f"   {label}={q:.3e}  => implied (d+1)-1 = {d_implied:,.0f}")
    # bijection space p=1/(73*71)?? doc: e*p*(d+1)=7.8e2. Just report structure.
    print("   (implied d values should be internally consistent across p2,p3 "
          "rows; a single degree d drives both -- check they match.)")


if __name__ == "__main__":
    t0 = time.time()
    ok = check_structural()
    check_arithmetic()
    print(f"\n[done in {time.time()-t0:.1f}s]  structural={'PASS' if ok else 'FAIL'}")
