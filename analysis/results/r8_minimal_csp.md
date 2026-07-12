# R8 — Minimal Constraint Count for the rot4 Quadratic CSP

**Date:** 2026-07-12
**Companion:** `r8_proof.md` (proof), `quadratic_sidon_completeness.md` (verification),
`constraint_prop_solver.py` (solver that uses these counts).

---

## 1. Variable set (corrected 2026-07-12)

By R8, a rot4 NTIL configuration is **exactly** an `m`-subset `C` of the
`m×m` fundamental quadrant `{0,…,m−1}²` (one C4-orbit representative per cell)
such that the `(X)` and `(S)` quadratic collinearity determinants are all
non-zero.

> **Correction vs. earlier draft:** the cells are an *m-subset*, **not** a
> permutation matrix (rows/cols may repeat — verified on the full known-solution
> corpus).  The variable count is therefore **not** `m` ordered pairs
> `(α,β)∈{1..m}²` (the old "74 variables" model); it is a subset-selection:

- As a 0/1 selection CSP: **`m²` binary variables** `x_{r,c} ∈ {0,1}` with
  `Σ_{r,c} x_{r,c} = m` (choose exactly `m` cells).
- Candidate count: **`C(m², m)`** m-subsets (NOT `m!`).

For `m = 37`: `m² = 1369` binary selection variables; `C(1369, 37) ≈ 3.2×10⁶⁹`
candidates.  The constraints below are what prune this astronomically.

---

## 2. Constraint layers

### Layer X — three distinct cells (cross-quadrant)
For every 3-subset `{i,j,k}` of cells and every rotation triple
`(r1,r2,r3) ∈ {0,1,2,3}³`, require
`det(C4(c_i,r1), C4(c_j,r2), C4(c_k,r3)) ≠ 0`.

- Naïve count: `64 · C(m,3)` determinants.
- **C4 board-rotation symmetry** acts on `(r1,r2,r3)` by adding 1 mod 4
  simultaneously.  Every orbit has size exactly 4 (no triple is fixed by a
  90° global rotation).  → `64 / 4 = 16` equivalence classes.
- **Minimal X count:** `X_min(m) = 16 · C(m,3)`.

### Layer S — two images of one cell + one of another
For every ordered pair `(double-cell i, single-cell j≠i)`, every pair of
distinct rotations `r1≠r2` of cell `i`, and every rotation `r3` of cell `j`,
require `det(C4(c_i,r1), C4(c_i,r2), C4(c_j,r3)) ≠ 0`.

- Naïve count: `m · C(4,2) · (m−1) · 4 = 24 · m · (m−1)` determinants.
- Board rotation lets us **fix `r1 = 0`**; then `r2 ∈ {1,2,3}` (3 choices) and
  `r3 ∈ {0,1,2,3}` (4 choices).  → `3 · 4 = 12` forms per ordered `(i,j)`.
- **Minimal S count:** `S_min(m) = 12 · m · (m−1)`.
- (Both directions `i`-double / `j`-double are required and are covered by the
  ordered pair `m·(m−1)`.)

### Layer F (FDR) — redundant
The linear a–b Sidon law `count(d)+count(−d) ≤ 2` is a *feature* of rot4
solutions but adds **no** independent constraint to `(X)∧(S)`; R8 shows
`(X)∧(S) ⇒ F`.  Not counted in the minimal system.

---

## 3. Total minimal constraint count

```
T_min(m) = 16 · C(m,3)  +  12 · m · (m−1)
```

| m  | C(m,3) | X_min = 16·C(m,3) | S_min = 12·m·(m−1) | T_min |
|----|--------|-------------------|--------------------|-------|
| 5  | 10     | 160               | 240                | 400   |
| 10 | 120    | 1,920             | 1,080              | 3,000 |
| 20 | 1,140  | 18,240            | 4,560              | 22,800|
| 36 | 7,140  | 114,240           | 15,120             | 129,360|
| 37 | 7,770  | **124,320**       | **15,984**         | **140,304** |

For reference, the **non-reduced** (full 64/24) count is
`T_full(m) = 64·C(m,3) + 24·m·(m−1)`, which at `m=37` is
`497,280 + 31,968 = 529,248`.  The C4 symmetry reduction cuts the constraint
budget by **≈3.77×** (529,248 → 140,304).

---

## 4. Consequences for the m = 37 attack

- The `m=37` existence question is the satisfiability of a system with
  **1369 binary variables** (`Σ = 37`) and **140,304** quadratic
  (three-body determinant) inequality constraints, all required `≠ 0`.
- Constraint-to-variable ratio ≈ `140,304 / 1369 ≈ 102×` — overwhelmingly
  over-determined, consistent with the **R6 complete-determination principle**
  (the system is 0-dimensional: fixing enough cells forces the rest).  This is
  exactly why a *constraint-propagation* solver (forward-checking on the
  `(X)+(S)` forms) is the right engine, and why the earlier *linear* Sidon
  solvers were searching the wrong space (R7).
- Empirically (Stage D of `constraint_prop_solver.py`, 847 configs) the
  16-class X and 12-class S forms are **exactly equivalent** to the full
  64/24 forms (`mismatches = 0`), so the reduced count is sound.
- **Status:** the system is explicitly written down and the solver lives in
  its space; the satisfiability itself remains **OPEN** (Stage M of the
  solver: Monte-Carlo finds no random hit, bounded backtracking characterises
  pruning strength but cannot complete at m=37 within budget).
