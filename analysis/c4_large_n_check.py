"""
Extract cycle types from Flammenkamp rot4 solutions for large even n
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
        canon = None
        for pt in orbit:
            if pt[0] < m and pt[1] < m:
                canon = pt
                break
        if canon is None:
            canon = min(orbit)
        orbits.append(canon)
    return orbits

def decompose_cycles(orbits):
    """Decompose orbit selection into cycles (vertex degree-2 graph)"""
    m = len(orbits)
    adj = {r: [] for r in range(m)}
    for (a, b) in orbits:
        adj[a].append(b)
        adj[b].append(a)
    
    visited = set()
    cycles = []
    for r in range(m):
        if r in visited: continue
        cycle = [r]
        visited.add(r)
        if adj[r][0] == r or (len(adj[r]) > 0 and adj[r][0] == r):
            # 1-cycle (loop)
            cycles.append((1, r))
        else:
            prev = r
            curr = adj[r][0]
            while curr != r:
                cycle.append(curr)
                visited.add(curr)
                if len(adj[curr]) < 2:
                    break
                nxt = adj[curr][0] if adj[curr][0] != prev else adj[curr][1]
                prev, curr = curr, nxt
            cycles.append((len(cycle), cycle))
    
    return cycles

# Fetch and analyze for the requested m values
# m maps to n = 2m
requested_ms = [10, 11, 12, 13, 21, 22, 23, 30, 31, 32, 33]

print(f"{'m':>3} {'n':>3} {'#rot4 slns':>10} {'Cycle types found':<30}")
print("=" * 55)

for m in requested_ms:
    n = 2 * m
    url = f'https://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n{n}_rot4'
    try:
        with urllib.request.urlopen(url, timeout=15) as f:
            lines = f.read().decode().strip().split(chr(10))
            lines = [l for l in lines if l.strip() and 'html' not in l.lower()[:10]]
    except:
        print(f"{m:>3} {n:>3} no rot4 data")
        continue
    
    if not lines:
        print(f"{m:>3} {n:>3} empty data")
        continue
    
    cycle_type_counts = Counter()
    for line in lines:
        result = decode(line)
        if result is None: continue
        n_actual, pts = result
        if n_actual != n: continue
        
        orbits = find_orbits(n, pts)
        cycles = decompose_cycles(orbits)
        sig = tuple(sorted([c[0] for c in cycles]))
        cycle_type_counts[sig] += 1
    
    # Summarize
    types_str = ', '.join(f"{k}({v}x)" for k, v in 
                           sorted(cycle_type_counts.items(), key=lambda x: -x[1])[:4])
    print(f"{m:>3} {n:>3} {len(lines):>10}  {types_str}")
