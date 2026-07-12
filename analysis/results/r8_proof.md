# R8 (Theorem): Quadratic-Sidon Completeness — Formal Proof

**Date:** 2026-07-12 (upgraded from "candidate" to theorem)
**Status:** PROVED — finite-geometry case analysis (this note) + computational verification
(**7500** random templates over m=5..9 with `miss(X+S)=0, false(X+S)=0`, and
**93** known rot4 solutions all classified SAFE).

---

## 0. Setup (same notation as `quadratic_sidon_completeness.py`)

- A rot4 candidate is given by `m` cells `c_i = (x_i, y_i) ∈ {0,…,m−1}²`,
  `i = 1..m`.  Each cell is the **unique** representative (in the upper-left
  `m×m` fundamental quadrant) of one C4-orbit of the `2m×2m` board; because the
  board centre is the half-integer `((2m−1)/2,(2m−1)/2)`, exactly one of the 4
  rotations of any orbit falls in `{0,…,m−1}²`, so the `m` orbits ↔ `m`
  **distinct** cells.  (Equivalently the cells arise from an odd-number pairing
  via `x_i = m − (a_i+1)/2, y_i = m − (b_i+1)/2`.)

  **Important correction (2026-07-12):** the cells are an **m-subset** of the
  `m×m` quadrant, *not* in general a permutation matrix.  Rows and columns may
  repeat (verified on the full known-solution corpus: e.g. the m=7 solution has
  two cells in the same row).  The earlier draft claimed a permutation matrix
  by assuming the quadrant reps inherit the `m!` structure of the odd-number
  m-cycle edge list — but the cache stores *point coordinates*, and the
  extracted reps need not be a Latin transversal.  **R8 does not depend on the
  permutation-matrix assumption**: its proof (§1–§2) only uses that the cells
  are `m` distinct orbit representatives, which holds for any m-subset.

- `C4(c, r)` is the rotation of cell `c` by `r ∈ {0,1,2,3}` (90° steps) on the
  `2m×2m` board (center at `((2m−1)/2, (2m−1)/2)`).

- The **lifted point set** is `L = { C4(c_i, r) : i=1..m, r=0..3 }`.
  For off-axis cells `|L| = 4m`; if a cell lies on a symmetry axis its orbit
  still has ≥2 distinct points (only the exact center gives a 1-point orbit,
  which we exclude from rot4 solutions).

- **Layer X** (3 distinct cells): for every 3-combination `{i,j,k}` and every
  rotation triple `(r1,r2,r3) ∈ {0,1,2,3}³`, require
  `det(C4(c_i,r1), C4(c_j,r2), C4(c_k,r3)) ≠ 0`.

- **Layer S** (2 images of one cell + 1 of another): for every cell `i`, every
  pair of distinct rotations `r1≠r2` of `c_i`, every other cell `j≠i`, and every
  rotation `r3 ∈ {0,1,2,3}`, require
  `det(C4(c_i,r1), C4(c_i,r2), C4(c_j,r3)) ≠ 0`.

> **R8 (Quadratic-Sidon Completeness Theorem).**
> Let `m ≥ 2`.  The lifted set `L` contains three collinear points
> **if and only if** the quadratic-Sidon system `(X) ∧ (S)` is violated
> (i.e. at least one listed determinant equals 0).
>
> Consequently, a rot4 configuration (cells off symmetry axes + no three
> collinear) **exists** ⇔ a distinct m-subset of the `m×m` fundamental
> quadrant (one C4-orbit rep per cell) satisfies `(X) ∧ (S)`.

---

## 1. The (⇐) direction: `(X ∧ S)` ⇒ no three collinear in `L`

Assume `(X)` and `(S)` both hold (all listed determinants are non-zero).
Take **any** three distinct collinear points `p, q, r ∈ L`.  Write them as

```
p = C4(c_i, r_p),   q = C4(c_j, r_q),   r = C4(c_k, r_r)
```

with `i, j, k ∈ {1..m}` and `r_p, r_q, r_r ∈ {0,1,2,3}`.  Partition by the
multiset of source cells `{i, j, k}`:

### Case A — `i, j, k` all distinct
`X`, instantiated with the triple of cells `(c_i, c_j, c_k)` and the rotation
combo `(r1, r2, r3) = (r_p, r_q, r_r)` (one of the 64 combinations it tests),
computes exactly `det(p, q, r)`.  By the collinearity of `p, q, r` this
determinant is 0 — contradicting that `X` holds.  So this case cannot occur.

### Case B — exactly two of `{i, j, k}` coincide
WLOG `i = j ≠ k` (two points from cell `i`, one from cell `k`; the other two
sub-cases are symmetric).  The two points from cell `i` have rotations
`r_p, r_q`, which must be **distinct** (otherwise `p = q`, not a 3-point set).
This is precisely a "two distinct images of cell `i` + one image of cell `k`"
configuration.  `S`, instantiated with double-cell `= i`, single-cell `= k`,
and `(r1, r2, r3) = (r_p, r_q, r_k)`, computes `det(p, q, r) = 0` — contradicting
that `S` holds.  (The sub-cases `i = k ≠ j` and `j = k ≠ i` are covered because
`S` iterates over **all** ordered pairs `(double-cell, single-cell)`.)  So this
case cannot occur either.

### Case C — `i = j = k` (all three from the same cell)
Then `p, q, r` are three **distinct** points among the C4 orbit
`O = {c_i, C4(c_i,1), C4(c_i,2), C4(c_i,3)}`.

**Lemma (no three orbit points collinear).**  Relative to the board centre,
let `c = (u, v)`.  Its C4 orbit is `{c, Rc, R²c, R³c}` where `R` is 90° rotation.
- If `c` is off every symmetry axis (`u ≠ 0, v ≠ 0, u ≠ ±v`), `O` is a
  non-degenerate square; no three vertices of a square are collinear.
- If `c` lies on the horizontal/vertical axis (`v = 0` or `u = 0`, `c ≠ centre`):
  `O = {(a,0),(0,a),(−a,0),(0,−a)` (up to sign), two points on each axis — no
  three collinear.
- If `c` lies on a diagonal (`u = ±v`, `c ≠ centre`): `O` is an axis-aligned
  square `{ (a,a),(−a,a),(−a,−a),(a,−a) }` — again no three collinear.

In every case no three points of `O` are collinear.  Hence Case C contributes
**no** collinearity at all, regardless of `(X)` or `(S)`.

∎ Lemma.

Since Cases A, B, C exhaust all partitions of `{i,j,k}`, and A, B are ruled out
by `(X)`,`(S)` while C is impossible outright, **no three collinear points can
exist in `L`**.  This proves `(X ∧ S)` ⇒ no-three-in-line.

---

## 2. The (⇒) direction: a collinear triple ⇒ `(X ∧ S)` violated

Trivial by construction: if `p,q,r ∈ L` are collinear, the case analysis above
shows they fall under Case A or B (Case C is impossible), and the specific
`(X)` or `(S)` instance that tests exactly that triple has determinant 0.
Hence `(X ∧ S)` is violated.  ∎

---

## 3. Consequences

1. **R8 is exact**, not merely a strong correlation: the only two ways three
   lifted points can be collinear are (a) from three distinct cells or
   (b) from two images of one cell plus one of another — and those are *exactly*
   what `X` and `S` test.  A third configuration (all three from one cell) is
   geometrically impossible.

2. **FDR is redundant for the equivalence** (re-confirmed): `F` (linear a–b
   Sidon) is a *feature* of rot4 solutions but adds no new constraint to
   `(X ∧ S)`; `miss(F+X+S) = 0` already in the computational check.

3. **m = 37 existence is a clean CSP.**  Variables: the `m` cells as a
   distinct m-subset of the `m²` board positions (`C(m²,m)` candidates — *not*
   `m!`, since rows/cols may repeat).  Constraints: the `(X)` + `(S)` quadratic
   inequalities (de-duplicated counts in `r8_minimal_csp.md`).  Existence ⇔
   satisfiability of this finite discrete quadratic CSP.

4. **Solver space is now correct.**  Every earlier failed search (Z3/CP-SAT/SA/
   Sidon/permutation) lived in the *linear* Sidon space and could not, even in
   principle, capture cross-quadrant collinearity (R7).  The engine must operate
   on the `(X + S)` quadratic constraints — see `constraint_prop_solver.py`.

---

## 4. Relation to the rest of the theory

| Result | Role |
|--------|------|
| R1 FDR | rot4 ⇒ linear a–b Sidon (a *feature*; redundant for R8) |
| R7 Quadratic Gap | cross-quadrant collinearity is quadratic; linear layers insufficient |
| **R8 (this, now theorem)** | `(X∧S)` ⇔ no-three-in-line ⇒ rot4 NTIL = quadratic CSP |
| R6 complete-determination | the `(X+S)` system is 0-dimensional; each cell forced by the others |
| m=37 window | existence ⇔ satisfiability of the R8 quadratic CSP |

R7 + R8 close the loop: *linear fails, quadratic is exact.*
