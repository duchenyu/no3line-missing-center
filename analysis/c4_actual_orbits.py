"""
Direction A, Step 2: Decode actual rot4 solutions to find their orbit selections
"""
import urllib.request
from collections import Counter

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
char_to_val = {c: i for i, c in enumerate(ALPHABET)}

def R(p, n):
    return (n-1-p[1], p[0])

def decode(line):
    line = line.strip()
    if not line: return None
    rest = line[1:]
    n = len(rest)//2
    pts = []
    for r in range(n):
        pts.append((r, char_to_val[rest[2*r]]))
        pts.append((r, char_to_val[rest[2*r+1]]))
    return n, pts

def find_orbits(n, pts):
    """Find C4 orbits in a solution, normalized to m×m orbit coordinates"""
    m = n // 2
    point_set = set(pts)
    remaining = set(point_set)
    orbits = []
    while remaining:
        p = remaining.pop()
        orbit = {p}
        for _ in range(3):
            p = R(p, n)
            remaining.discard(p)
            orbit.add(p)
        # Canonical: rotate until both coordinates < m
        # For n=2m, orbit O(a,b) where 0≤a,b<m has all 4 pts:
        # (a,b), (2m-1-b,a), (2m-1-a,2m-1-b), (b,2m-1-a)
        # Find the point with both coords < m
        canon = None
        for pt in orbit:
            if pt[0] < m and pt[1] < m:
                canon = pt
                break
        if canon is None:
            # Fallback: min by lex
            canon = min(orbit)
        orbits.append(canon)
    m = n // 2
    return m, orbits

# Download actual rot4 solutions and analyze orbit selections
print("=" * 75)
print("Analyzing orbit selections in actual rot4 solutions from Flammenkamp DB")
print("=" * 75)

for n in [12, 14, 16, 18, 20, 30]:
    url = f'https://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n{n}_rot4'
    try:
        with urllib.request.urlopen(url, timeout=15) as f:
            lines = f.read().decode().strip().split(chr(10))
            lines = [l for l in lines if l.strip() and 'html' not in l.lower()[:10]]
    except:
        print(f"\nn={n}: no data")
        continue
    
    print(f"\n--- n={n} ({len(lines)} rot4 solutions) ---")
    
    for li, line in enumerate(lines[:5]):  # first 5 solutions
        result = decode(line)
        if result is None: continue
        n_actual, pts = result
        if n_actual != n: continue
        
        m, orbits = find_orbits(n, pts)
        
        # Check row coverage pattern
        row_count = Counter()
        for (i,j) in orbits:
            row_count[i] += 1
            row_count[j] += 1
        
        print(f"  Sol #{li}: orbits={sorted(orbits)}, row_counts={dict(sorted(row_count.items()))}")
