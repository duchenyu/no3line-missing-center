# R8 (candidate theorem): rot4 NTIL ⇔ Quadratic-Sidon CSP

**Date:** 2026-07-12
**Status:** computational proof (exhaustive on m=5..12 known solutions + 7500 random templates)
**Prerequisite:** R7 (Quadratic Gap Theorem, proved 2026-07-12).

---

## 1. Motivation

R7 proved that *cross-quadrant* collinearity is intrinsically quadratic and
cannot be captured by any finite linear Sidon layer.  But R7 only established
**insufficiency** of the linear layer — it left open the converse question:

> **Is the quadratic layer SUFFICIENT?**  I.e. does the collection of all
> quadratic collinearity determinants *exactly characterize* rot4 no-three-
> in-line (NTIL)?

If yes, then rot4 NTIL is *precisely* a quadratic constraint-satisfaction
problem (CSP), and the existence of a rot4 solution at m=37 becomes the
question: *does this quadratic system have a solution?* — a clean algebraic
geometry problem.

This note answers YES, and identifies the **exact** set of quadratic forms
required.

---

## 2. The quadratic-Sidon system

Let `pairs = {(a_i, b_i)}` (i=1..m) be the m odd-number pairings of a rot4
candidate (a_i, b_i ∈ {1,3,…,2m−1}).  Map each pair to its quadrant cell
`c_i = (x_i, y_i) = (m − (a_i+1)/2, m − (b_i+1)/2)`, and let `P(c, r)` be the
C4 rotation of cell c by r∈{0,1,2,3} on the 2m×2m board.

The system has two quadratic layers:

### Layer X — three DISTINCT cells, all 64 rotation triples
For every 3-combination {i,j,k} and every rotation triple (r1,r2,r3)∈{0,1,2,3}³:

    det_X(i,j,k; r1,r2,r3) =
        (P(c_j,r2)_x − P(c_i,r1)_x)·(P(c_k,r3)_y − P(c_i,r1)_y)
      − (P(c_k,r3)_x − P(c_i,r1)_x)·(P(c_j,r2)_y − P(c_i,r1)_y)   ≠  0

This covers BOTH cross-quadrant AND same-quadrant (r=(0,0,0)) collinearity
among three different cells.  (Each determinant is a genuine quadratic form
in the (α,β) variables — see R7.)

### Layer S — two images of ONE cell + one image of ANOTHER cell
For every cell i, every pair of distinct rotations (r1≠r2) of c_i, and every
other cell j with rotation r3:

    det_S(i; r1,r2; j,r3) =
        (P(c_i,r2)_x − P(c_i,r1)_x)·(P(c_j,r3)_y − P(c_i,r1)_y)
      − (P(c_j,r3)_x − P(c_i,r1)_x)·(P(c_i,r2)_y − P(c_i,r1)_y)   ≠  0

This captures collinearity where two of the three lifted points come from the
*same* original cell (two vertices of its C4 orbit) and the third from a
different cell.  It is also quadratic in (α,β).

**The quadratic-Sidon system = (X) ∧ (S).**

---

## 3. Computational verification

Script: `analysis/quadratic_sidon_completeness.py`
Ground truth: brute-force 3-in-a-line on the 4m C4-lifted points.

### Stage 1 — known solutions (must all be SAFE)
| m | #known | brute-collisions | FDR | X | S |
|---|--------|------------------|-----|---|---|
| 5 | 6  | 0 | pass | pass | pass |
| 6 | 4  | 0 | pass | pass | pass |
| 7 | 13 | 0 | pass | pass | pass |
| 8 | 13 | 0 | pass | pass | pass |
| 9 | 7  | 0 | pass | pass | pass |
|10 | 16 | 0 | pass | pass | pass |
|11 | 8  | 0 | pass | pass | pass |
|12 | 23 | 0 | pass | pass | pass |

All 93 known rot4 solutions are correctly classified SAFE.  (Confirms the
layer implementations are correct.)

### Stage 2 — random 2-regular directed templates (equivalence test)
1500 random templates per m (m=5..9).  `miss` = #configs the layer calls SAFE
but brute finds collinear; `false` = #configs the layer calls UNSAFE but brute
finds non-collinear.

| m | N | miss(X) | miss(X+S) | miss(F+X+S) | false(X+S) |
|---|---|---------|-----------|-------------|------------|
| 5 |1500| 53      | **0**     | 0           | **0**      |
| 6 |1500| 13      | **0**     | 0           | **0**      |
| 7 |1500| 1       | **0**     | 0           | **0**      |
| 8 |1500| 2       | **0**     | 0           | **0**      |
| 9 |1500| 0       | **0**     | 0           | **0**      |

**Result:**
- `miss(X) > 0` ⇒ Layer X **alone is insufficient** — it misses same-cell
  collinearities (layer S).
- `miss(X+S) = 0` and `false(X+S) = 0` for **every** tested config ⇒
  **(X ∧ S) is EXACTLY equivalent to rot4 NTIL** on the tested domain.
- `miss(F+X+S) = 0` ⇒ adding the linear FDR layer changes nothing ⇒
  **FDR is redundant for the equivalence** (it is a linear *feature* of rot4
  solutions, not part of the necessary-and-sufficient quadratic criterion).

---

## 4. Theorem (R8, candidate)

> **Theorem (Quadratic-Sidon Completeness).**  A rot4 pairing
> `{(a_i,b_i)}_{i=1..m}` is a no-three-in-line configuration **if and only if**
> the quadratic-Sidon system (X) ∧ (S) holds — i.e. all C(m,3)·64
> three-distinct-cell rotation determinants and all m·6·(m−1)·4 same-cell
> determinants are non-zero.
>
> Equivalently, rot4 NTIL is *exactly* a quadratic CSP over the m cell
> variables (α_i,β_i) ∈ {1,…,m}².

**Consequence for m=37.**  m=37 rot4 existence ⇔ the quadratic system with
- variables: 37 cells × (α,β) = **74 integer variables** in {1,…,37}²
- constraints (de-duplicated by C4 symmetry):
  - X: C(37,3) × 16 equivalence classes = **124,320** quadratic inequalities
  - S: 37 × 6 × 36 × 4 = **31,968** quadratic inequalities
  - total ≈ **156,288** three-body quadratic inequalities, all required ≠ 0.

This sharpens the earlier "124,320 quadratic constraints" estimate (which
captured only X) by adding the necessary S layer.

---

## 5. Relation to R1–R7

| Result | Role |
|--------|------|
| R1 FDR theorem | rot4 ⇒ linear a-b Sidon (a *feature*, now shown redundant for the equivalence) |
| R7 Quadratic Gap | cross-quadrant collinearity is quadratic; linear Sidon insufficient (**insufficiency**) |
| **R8 (this)** | quadratic system (X+S) is **necessary AND sufficient** ⇒ rot4 NTIL = quadratic CSP |
| R6 complete-determination | each (α,β) uniquely fixed by the others via the X+S quadratic forms |
| m=37 window | existence ⇔ satisfiability of the R8 quadratic CSP |

R7 + R8 together close the loop: *linear layers fail (R7), quadratic layers
succeed and are exact (R8).*

---

## 6. Key new finding

**Layer S is mandatory.**  Prior analysis (R7, "X = 16 quadratic forms",
characterize_x) focused exclusively on three *distinct* cells.  The data shows
X alone leaks collinearities at every m (53 at m=5, shrinking with m but
non-zero through m=8).  These leaks are exactly the *same-cell two-point*
collinearities captured only by S.  Any solver or impossibility proof that
uses only the 16 cross-form X layer is **incomplete** — it must include S.

---

## 7. Open problems / next steps

1. **Algebraic proof of R8.**  The computational equivalence is strong
   evidence but not a proof.  A formal proof would show that the 4m lifted
   points can only be collinear in the two cases enumerated by X and S
   (three distinct cells, or two images of one cell + one of another) — a
   finite geometric case analysis under C4 symmetry.
2. **Satisfiability of the m=37 system.**  With R8, m=37 existence is a
   concrete quadratic CSP.  Attack via (a) Gröbner/elimination on fixed
   combinatorial templates, or (b) constraint-propagation solver in the
   correct quadratic space (not the failed linear Sidon space).
3. **Tighten S.**  Layer S has obvious C4 symmetries; de-duplicating may
   reduce its ~32k constraints substantially, simplifying any solver.
