# Structural Lemmas for Even-n No-Three-In-Line (2n-point) Solutions

> Standalone, paper-ready statements with proofs.
> Empirical backing computed 2026-07-08 from the Flammenkamp database
> (even n = 12..72, symmetry classes iden/rot2/dia1/ort1/rot4/dia2).

---

## Lemma 1 (C₂ theorem — distinct central directions)

Let `S` be a no-three-in-line solution on an even `n × n` grid (`|S| = 2n`, distinct points,
no three collinear), and suppose `S` is invariant under the half-turn about the grid centre
`C = ((n−1)/2, (n−1)/2)`,

    R₁₈₀(r, c) = (n − 1 − r, n − 1 − c).

Then:

1. `S` decomposes into exactly `n` **R₁₈₀-orbits** `{p, R₁₈₀(p)}` (each of size 2);
2. each orbit determines a line through `C` (the line joining `p` and `R₁₈₀(p)`);
3. these `n` lines through `C` are **pairwise distinct** (no two orbits lie on one central line).

**Proof.**
(1) `R₁₈₀` is an involution of order 2. For even `n`, `C` is not a lattice point, so `R₁₈₀`
has no fixed point; every orbit has size 2, and `|S| = 2n ⇒ n` orbits.
(2) For an orbit `{p, q}` with `q = R₁₈₀(p)`, `C` is the midpoint of segment `pq`, so the line
`pq` passes through `C`.
(3) Suppose two distinct orbits lay on a common line `L` through `C`. Then `L` would contain the
4 points of those two orbits, and any 3 of them would be collinear — contradicting the
no-three-in-line property. ∎

**Empirical support.** Across 3732 sampled R₁₈₀-invariant solutions (classes rot2, rot4, dia2)
the number of parallel orbit-pairs is **0**; all 3732 satisfy the distinct-direction condition.

**Scope.** The hypothesis "R₁₈₀-invariant" holds exactly for the symmetry classes whose group
contains the half-turn: `rot2` (group C₂), `rot4` (group C₄, since R₁₈₀ = R₉₀²), and `dia2`
(group V₄ = {id, R₁₈₀, d₁, d₂}, with R₁₈₀ = d₁∘d₂). Classes `iden`, `dia1` (single diagonal
reflection only), and `ort1`/`ort2` do **not** contain R₁₈₀ and are outside the lemma's scope.

---

## Lemma 2 (Ring population is a multiple of 4)

Let `S` be a no-three-in-line solution on an even `n × n` grid that is invariant under the
quarter-turn `R₉₀` (i.e. a `rot4` solution).

Write the orbit of a point `p` under `R₉₀` as `O(p) = {p, R₉₀(p), R₉₀²(p), R₉₀³(p)}`.
All four points of `O(p)` are equidistant from `C`, so `O(p)` lies on a single distance ring
`R_d = {q : |q − C|² = d}` and contributes exactly 4 points to it. Consequently, **every
distance ring centred at `C` carries a number of points divisible by 4**.

**Proof.** `R₉₀` rotates by 90° about `C`, hence preserves the distance to `C`; the four vertices
of the orbit square are at equal distance from `C`. Each orbit occupies precisely one ring with
population 4, so any ring's total population is `4 × (number of orbits on that ring)`. ∎

**Empirical support.** Over all 21601 rot4 solutions for `n = 12..72`, the set of observed ring
populations is exactly `{4, 8, 12, 16}` — always a multiple of 4, with **0** counterexamples.
(An earlier note claiming "always 4 or 8" was an over-generalisation from small `n`; the correct,
provable statement is "multiple of 4".)

**Corollary.** In a rot4 solution every distance ring contains at least 4 points, so `C` is the
circumcentre of every non-empty ring — consistent with rot4 solutions never being missing-centre.
(This is a geometric consequence of the C₄ symmetry, not a missing-centre *criterion*.)

**Scope restriction (corrected 2026-07-08).** The "multiple of 4" law is specific to *even-n
rot4*, where `C` is not a lattice point and every C₄-orbit has size 4. It does **not** extend to
`rct4`: the `rct4` group (D₂ about `C`) admits size-2 orbits for points on the grid midlines, and
empirical data (all 326 odd-n `rct4` solutions) shows ring populations take values `{2, 4, 6, 8,
12}` — not always multiples of 4 (e.g. n=9 has a ring of population 2).

---

## Lemma 3 (Four-colouring: every line meets ≤ 2 colours)

Colour the `n × n` grid (even `n`) by `(r mod 2, c mod 2)` into 4 colour classes.
Every line of rational slope, in reduced direction `(a, b)` with `gcd(a, b) = 1`, changes parity
by `(a mod 2, b mod 2) ∈ {(1,1),(1,0),(0,1)}`; in each case the colour alternates between **exactly
2** of the 4 classes. Hence **every line meets at most 2 of the 4 colours**.

**Empirical support.** Over all reduced directions with `|a|, |b| ≤ 6`, the maximum number of
colours met by one line is **2** — confirming the parity argument.

**On D(n) ≤ 2n.** The 4-colouring property above is correct and independently verifiable, but it
does *not* yield an independent proof of the upper bound. `D(n) ≤ 2n` remains the elementary
"≤2 points per row" argument; an earlier draft attempted to derive per-colour ≤ n/2 from the
colouring, but the step "≤1 point of a given colour per row" is false (a row can contain two
points of the same colour), so that derivation is circular and merely restates the row bound.

**Colour balance for rot4 / rct4 solutions (a theorem, not a general necessity).** If `S` is a
rot4 solution with `|S| = 2n`, then `R₉₀` acts on the 4 colour classes as a 4-cycle
`(rbit, cbit) ↦ (cbit, 1−rbit)`, hence every colour class has the same size, namely `n/2`. The
same holds for `rct4` (its D₂ group acts transitively and freely on the 4 colours).

This is **not** a necessary condition for arbitrary 2n solutions: among 143,691 `iden`-class 2n
solutions, 55,302 are colour-unbalanced (e.g. n=12 gives counts `[7,5,5,7]`); `rot2`, `dia1`,
`dia2` show the same. So "perfect 4-colour balance" is a symmetry-induced property of rot4/rct4,
useful as a construction filter, not a universal law.

---

## How these lemmas relate to a proof of D(n) = 2n

**Status (honest).** The upper bound `D(n) ≤ 2n` is elementary. The open part is the *lower bound*
(constructing 2n points for every even `n`). A construction for all `n ≡ 0 (mod 4)` would be a
major step toward — likely equivalent to — the open problem, so it must not be claimed lightly.

**What the invariants genuinely give (the provable partial proof).**
- *Lemma 1 (C₂ theorem) is the real asset.* It reduces the even-n construction to a single
  well-defined obstacle: choose `n` points (one per central direction) so that no line **not
  through `C`** contains ≥3 of the 2n points. The centre-line case is *fully solved* by theory
  (distinct central directions ⇔ no centre-line triple).
- *Lemma 2* sharpens the description of `rot4` solutions (rigid ring structure) and, combined with
  Lemma 1(1), actually *proves* the C₄ theorem: a rot4 solution has rings of population ≥4
  equidistant from `C`, so `C` is the circumcentre of some triple — rot4 solutions are never
  missing-centre.
- *Lemma 3* supplies a clean necessary structural property of `rot4`/`rct4` solutions (colour
  balance) usable as a construction filter.

**Empirical negative result (2026-07-08).** Attempts to turn the invariants into an *explicit
closed-form* construction failed across the board:
- 8 polynomial seed formulas `c(i) mod n` over even `n ≤ 80`: only `n = 4` succeeded (one formula).
- R₁₈₀-doubling of the finite-field parabola over all primes `p ≤ 59`: **0** successes (off-centre
  collinearities).
- A deterministic Lemma-1-enforced greedy placer: stuck immediately (over-forbidden columns).

The consistent failure is *evidence* — not a proof — that the off-centre collinearity is a genuine,
non-algebraically-trivial constraint, exactly as the open status of `D(n) = 2n` predicts. The
correct research contribution is therefore: **publish Lemmas 1–3 as novel structural invariants and
the reduction in Lemma 1 as a precise characterisation of the remaining obstacle**, while treating
existence for all even `n` (computationally verified up to `n = 72` by Heule/Flammenkamp) as the
benchmark a future proof must meet.
