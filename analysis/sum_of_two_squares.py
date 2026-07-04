"""
Sum-of-two-squares analysis: r₂(d) for distance rings.
Connect number theory to missing-center abundance.

Formula: r₂(d) = number of integer solutions (x,y) to x² + y² = d
  = 4 × (d₁ − d₃) where d₁ = # of 4k+1 divisors, d₃ = # of 4k+3 divisors
  = 0 if any 4k+3 prime has odd exponent in d
  = 4 × Π (e_i + 1) for each 4k+1 prime p_i^{e_i} | d, otherwise
"""

from collections import Counter
import math
import numpy as np

# ── Prime factorization ──
def factorize(n):
    """Return dict of prime: exponent for n."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2  # after 2, check odds only
    if n > 1:
        factors[n] = 1
    return factors

def r2(d):
    """Number of integer representations of d as x² + y²."""
    if d == 0:
        return 1  # center point
    factors = factorize(d)
    
    # Check: any 4k+3 prime with odd exponent?
    for p, e in factors.items():
        if p % 4 == 3 and e % 2 == 1:
            return 0  # impossible to represent
    
    # r₂(d) = 4 × Π(e_i + 1) for each 4k+1 prime factor
    result = 4
    for p, e in factors.items():
        if p % 4 == 1:
            result *= (e + 1)
    
    return result

def mod4_type(p):
    """Categorize a prime by its residue mod 4, except p=2."""
    if p == 2:
        return '2'
    if p % 4 == 1:
        return '1'
    return '3'

# ── Distance ring analysis for a grid ──
def analyze_grid(n):
    """For a grid of size n, compute distance ring statistics."""
    m = (n-1)//2  # integer center coordinate
    ctr = (n-1)/2.0
    
    rings = Counter()  # d² -> count of grid points
    for i in range(n):
        for j in range(n):
            d2 = int(round((i-ctr)**2 + (j-ctr)**2))
            rings[d2] += 1
    
    # For each ring, compute r₂(d²)
    ring_stats = {}
    for d2, pop in sorted(rings.items()):
        r = r2(d2)
        factors = factorize(d2)
        
        # Categorize by mod4 of prime factors
        has_4k3_odd = any(p % 4 == 3 and e % 2 == 1 for p, e in factors.items())
        prime_4k1 = [p for p in factors if p % 4 == 1]
        
        ring_stats[d2] = {
            'population': pop,
            'r2': r,
            'factors': factors,
            'has_4k3_odd': has_4k3_odd,
            'prime_4k1_count': len(prime_4k1),
            'max_exponent_4k1': max((e for p, e in factors.items() if p % 4 == 1), default=0)
        }
    
    return rings, ring_stats

# ── Compute for all n ──
print('=' * 90)
print('SUM-OF-TWO-SQUARES ANALYSIS OF DISTANCE RINGS')
print('=' * 90)

# Part 1: Ring population vs r₂(d) comparison
print('\n--- Part 1: Ring population vs r₂(d) comparison ---')
print(f'{"d":>6} {"pop":>5} {"r₂(d)":>6} {"match?":>7} {"4k+1 primes":>12} {"factors":<30}')
print('-' * 70)

for n in [12, 16, 20, 24]:
    rings, stats = analyze_grid(n)
    print(f'\nn={n}:')
    for d2, pop in sorted(rings.items()):
        s = stats[d2]
        match = '✅' if pop == s['r2'] else f'≠({s["r2"]})'
        fac_str = '×'.join(f'{p}^{e}' for p, e in sorted(s['factors'].items())[:3])
        if len(s['factors']) > 3:
            fac_str += '...'
        if pop != s['r2']:
            print(f'  {d2:>6} {pop:>5} {s["r2"]:>6} {match:>7} {s["prime_4k1_count"]:>12} {fac_str:<30}')

# Part 2: How many rings have r₂(d²) < population? (boundary effects)
print('\n--- Part 2: Boundary-limited rings ---')
for n in [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]:
    rings, stats = analyze_grid(n)
    total = len(rings)
    boundary_limited = sum(1 for d2 in rings if stats[d2]['r2'] > rings[d2])
    zero_r2 = sum(1 for d2 in rings if stats[d2]['r2'] == 0)
    print(f'n={n:2d}: {total:3d} rings, {zero_r2:3d} impossible(r₂=0), {boundary_limited:3d} boundary-limited')

# Part 3: Correlation: number of rings with r₂(d²) ≤ 2 vs missing-center rate
print('\n--- Part 3: r₂-based feature vs missing-center rate ---')

# Full reconstructed missing-center data
missing_data = {
    7: (132, 4), 8: (380, 0), 9: (365, 8), 10: (1135, 0),
    11: (1120, 36), 12: (4348, 52), 13: (3622, 292),
    14: (10568, 84), 15: (30634, 2716), 16: (46304, 1392),
    17: (55573, 3872), 18: (152210, 24), 19: (258170, 10280),
    20: (941580, 112), 21: (9701, 768), 22: (5082, 52)
}

print(f'{"n":>3} {"rings":>5} {"r₂=0":>5} {"r₂≤2":>5} {"r₂>pop":>7} {"miss%":>6} {"#4k+1prim":>10} {"d_GG-BB":>8}')
print('-' * 55)

features = []
targets = []
weights = []

for n in sorted(missing_data.keys()):
    ft, fm = missing_data[n]
    rate = fm / ft * 100
    rings, stats = analyze_grid(n)
    
    zero_r2 = sum(1 for d2 in rings if stats[d2]['r2'] == 0)
    r2_le2 = sum(1 for d2 in rings if stats[d2]['r2'] <= 2)
    boundary = sum(1 for d2 in rings if stats[d2]['r2'] > rings[d2])
    max_4k1 = max(stats[d2]['prime_4k1_count'] for d2 in rings)
    
    print(f'{n:>3} {len(rings):>5} {zero_r2:>5} {r2_le2:>5} {boundary:>7} {rate:>5.2f}% {max_4k1:>10} {"-":>8}')
    features.append([len(rings), zero_r2, r2_le2, max_4k1])
    targets.append(rate)
    weights.append(ft)

# Part 4: Refined regression model
print('\n--- Part 4: Refined regression with r₂ features ---')

X = np.array(features)
y = np.array(targets)
w = np.array(weights)

# Model 1: basic features only
X1 = np.column_stack([np.ones(len(X)), X[:, 0], X[:, 1], X[:, 3]])  # rings, zero_r2, max_4k1
W = np.diag(w / w.mean())
beta1 = np.linalg.solve(X1.T @ W @ X1, X1.T @ W @ y)
y_pred1 = X1 @ beta1
rss1 = np.sum(W @ ((y - y_pred1)**2))
tss = np.sum(W @ ((y - np.average(y, weights=w))**2))
r2_1 = 1 - rss1/tss

print(f'Model 1 (rings + r₂=0 + max_4k1):')
for i, name in enumerate(['intercept', 'rings', 'r₂=0', 'max_4k1']):
    print(f'  {name}: {beta1[i]:.4f}')
print(f'  R² = {r2_1:.4f}')

# Model 2: add r₂_le2
X2 = np.column_stack([np.ones(len(X)), X[:, 0], X[:, 1], X[:, 2], X[:, 3]])
beta2 = np.linalg.solve(X2.T @ W @ X2, X2.T @ W @ y)
y_pred2 = X2 @ beta2
rss2 = np.sum(W @ ((y - y_pred2)**2))
r2_2 = 1 - rss2/tss

print(f'\nModel 2 (all features):')
for i, name in enumerate(['intercept', 'rings', 'r₂=0', 'r₂≤2', 'max_4k1']):
    print(f'  {name}: {beta2[i]:.4f}')
print(f'  R² = {r2_2:.4f}')

# Compare with old model
print(f'\nR² improvement: {r2_2 - 0.620:+.4f} vs old three-factor model')

# Part 5: Key finding - explain ring population through number theory
print('\n--- Part 5: Number-theoretic explanation of ring structure ---')
print()
print('For a distance d² = (i-m)² + (j-m)² on an n-grid:')
print()
print('  r₂(d²) = number of integer representations of d² as x² + y²')
print()
print('  Key theorem (Fermat): r₂(d²) > 0 iff every 4k+3 prime factor')
print('  of d² has even exponent.')
print()
print('  When r₂(d²) > 0: r₂(d²) = 4 × Π(e_i + 1) for each 4k+1 prime')
print('  factor p_i^{e_i} dividing d².')
print()
print('  Relationship to ring population:')
print('  - r₂(d²) = number of (x,y) pairs with x²+y²=d²')
print('  - ring population = r₂(d²), truncated by grid boundaries')
print('  - For inner rings (small d), pop = r₂(d²) exactly')
print('  - For boundary rings (large d), pop < r₂(d²)')
print()
print('  Connection to missing-center problem:')
print('  - To avoid center as circumcenter: ≤2 points per ring')
print('  - Rings with r₂(d²) ≤ 2 are the ONLY usable rings')
print('  - Rings with r₂(d²) = 4 must be underfilled (use ≤2 of 4 pts)')
print('  - Rings with r₂(d²) = 0 are irrelevant (no grid points)')
print()
print('  This explains why 4k+3 vs 4k+1 matters:')
print('  - 4k+3 primes create "gaps" in the ring sequence (r₂=0)')
print('  - More 4k+3 prime factors → more unavailable rings')
print('  - This shifts which rings are available for selection')
