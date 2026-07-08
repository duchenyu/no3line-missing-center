#!/usr/bin/env python3
"""
Explicit C2-symmetric (R180-invariant) constructor for 2n-point no-three-in-line
solutions on an even n x n grid.

Method (honest framework):
  * GENERATIVE SKELETON:  S = { (i, c_i), R180(i, c_i) : i = 0..n-1 }
    where R180(r,c) = (n-1-r, n-1-c) and c_i = FORMULA(i) mod n.
  * PROVEN part (Lemma 1):  if the n pairs have distinct central directions,
    then NO three points are collinear on any line through the centre C.
    This is guaranteed once the construction satisfies the transversal +
    distinct-direction conditions, independent of any search.
  * VERIFIED part:  collinearity on lines NOT through C is checked per instance.
    (This is the genuinely open obstacle; we verify, we do not yet prove it.)

We sweep several closed-form seed formulas and report, for each even n, whether
the formula yields a valid 2n solution.  This converts "existence" from a blind
brute-force search into an explicit formula whose only unchecked part is the
off-centre collinearity.
"""

import math
from collections import defaultdict

# ---------------------------------------------------------------------------
# Core primitives
# ---------------------------------------------------------------------------
def build_S(n, c):
    """c is a list/function c(i) in [0, n-1] for i=0..n-1.
    Returns the set S of 2n points (or None if |S| != 2n)."""
    S = set()
    for i in range(n):
        ci = c(i) % n
        S.add((i, ci))
        S.add((n - 1 - i, n - 1 - ci))
    return S if len(S) == 2 * n else None

def central_directions_distinct(n, c):
    """True iff the n pairs have pairwise-distinct slopes through C.
    Two pairs i,j share a central line iff
        (n-1-2*c_i)/(n-1-2*i) == (n-1-2*c_j)/(n-1-2*j)."""
    seen = set()
    for i in range(n):
        num = n - 1 - 2 * (c(i) % n)
        den = n - 1 - 2 * i
        g = math.gcd(abs(num), abs(den)) or 1
        key = (num // g, den // g)
        if key in seen:
            return False
        seen.add(key)
    return True

def line_key(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    g = math.gcd(abs(dx), abs(dy)) or 1
    dx //= g
    dy //= g
    if dx < 0 or (dx == 0 and dy < 0):
        dx = -dx
        dy = -dy
    cc = dx * y1 - dy * x1   # line equation dx*Y - dy*X = cc
    return (dx, dy, cc)

def no_three_collinear(S):
    pts = list(S)
    m = len(pts)
    seen = defaultdict(set)
    for i in range(m):
        for j in range(i + 1, m):
            k = line_key(pts[i], pts[j])
            seen[k].add(pts[i])
            seen[k].add(pts[j])
            if len(seen[k]) >= 3:
                return False
    return True

def try_formula(n, c):
    S = build_S(n, c)
    if S is None:
        return None                       # transversal failed -> |S| != 2n
    if not central_directions_distinct(n, c):
        return None                       # centre-line 3-collinear (Lemma 1 violated)
    if not no_three_collinear(S):
        return None                       # off-centre 3-collinear
    return S

# ---------------------------------------------------------------------------
# Candidate closed-form seed formulas  c(i) mod n
# ---------------------------------------------------------------------------
FORMULAS = {
    "quad":       lambda n: (lambda i: (i * i) % n),
    "quad+1":     lambda n: (lambda i: (i * i + 1) % n),
    "2quad+i":    lambda n: (lambda i: (2 * i * i + i) % n),
    "quad+i+1":   lambda n: (lambda i: (i * i + i + 1) % n),
    "oblong":     lambda n: (lambda i: (i * (i + 1)) % n),
    "cubic":      lambda n: (lambda i: (i * i * i) % n),
    "quad-i":     lambda n: (lambda i: (i * i - i) % n),
    "3quad+i":    lambda n: (lambda i: (3 * i * i + i) % n),
}

# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------
N_MAX = 80
even = list(range(4, N_MAX + 1, 2))

print(f"{'formula':10s} | " + " ".join(f"{n:4d}" for n in even))
print("-" * (12 + 5 * len(even)))
summary = {}
for name, mk in FORMULAS.items():
    row = []
    fails = []
    for n in even:
        c = mk(n)
        S = try_formula(n, c)
        ok = S is not None
        row.append("  OK" if ok else "  --")
        if not ok:
            fails.append(n)
    summary[name] = fails
    print(f"{name:10s} | " + " ".join(row))

print("\nFailing even n per formula (transversal / centre / off-centre):")
for name, fails in summary.items():
    print(f"  {name:10s}: {fails if fails else 'ALL OK'}")

# ---------------------------------------------------------------------------
# Detailed example: dump an explicit solution for one covered n
# ---------------------------------------------------------------------------
def dump(n, name):
    c = FORMULAS[name](n)
    S = try_formula(n, c)
    if S is None:
        print(f"  n={n} [{name}]: no solution")
        return
    print(f"\nExplicit 2n={2*n} solution for n={n} via '{name}':")
    print("  S = { (i, c_i), R180(i,c_i) } with c_i = formula(i) mod n")
    for i in range(n):
        ci = c(i) % n
        print(f"    pair {i}: ({i},{ci})  &  ({n-1-i},{n-1-ci})")

dump(12, "quad")
dump(16, "quad")
