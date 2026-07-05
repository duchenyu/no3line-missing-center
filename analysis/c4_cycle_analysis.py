"""
Direction A, Step 3: Graph interpretation of C4 orbit selections

Each orbit selection corresponds to a 2-regular graph on m vertices.
Vertices = row-pairs {0,...,m-1}
Edges = orbits (i,j) meaning row-pair i connected to row-pair j
Each vertex degree = 2 (each row-pair covered by exactly 2 orbits)

A 2-regular graph decomposes into disjoint cycles.
The cycle lengths sum to m.

Key question: which cycle decompositions yield collinear-free orbit sets?
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
    return m, orbits

def decompose_cycles(orbits):
    """Decompose orbit selection into cycles"""
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
        prev = r
        curr = adj[r][0]  # first neighbor
        while curr != r:
            cycle.append(curr)
            visited.add(curr)
            nxt = adj[curr][0] if adj[curr][0] != prev else adj[curr][1]
            prev, curr = curr, nxt
        # Check if this is a 1-cycle (loop) — both neighbors are self
        if cycle == [r]:
            cycles.append((1, r))
        else:
            cycles.append((len(cycle), cycle))
    
    return cycles

print("=" * 75)
print("C4 Orbit Selections as Cycle Decompositions")
print("=" * 75)

for n in [12, 14, 16, 18, 20, 30]:
    url = f'https://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n{n}_rot4'
    try:
        with urllib.request.urlopen(url, timeout=15) as f:
            lines = f.read().decode().strip().split(chr(10))
            lines = [l for l in lines if l.strip() and 'html' not in l.lower()[:10]]
    except:
        continue
    
    print(f"\n--- n={n} (m={n//2}, {len(lines)} rot4 solutions) ---")
    cycle_types = Counter()
    
    for li, line in enumerate(lines):
        result = decode(line)
        if result is None: continue
        n_actual, pts = result
        if n_actual != n: continue
        
        m, orbits = find_orbits(n, pts)
        cycles = decompose_cycles(orbits)
        
        # Canonical signature: sorted tuple of cycle lengths
        sig = tuple(sorted([c[0] for c in cycles]))
        cycle_types[sig] += 1
        
        if li < 3:
            print(f"  Sol #{li}: cycles={cycles}")
    
    print(f"  Cycle type distribution:")
    for sig, count in sorted(cycle_types.items()):
        print(f"    {sig}: {count} solutions ({count/len(lines)*100:.0f}%)")

print("\n\n" + "=" * 75)
print("KEY INSIGHT: C4 orbit selection = 2-regular graph on m vertices")
print("              = disjoint cycle decomposition of m")
print("              = partition of m into cycle lengths")
print("=" * 75)
print()
print("Examples of valid decompositions observed:")
print("  n=12: (5,1) = 1-loop + 5-cycle, (3,3) = two 3-cycles")
print("  n=14: (6,1) = 1-loop + 6-cycle, (4,3) etc.")
print("  n=16: (5,3), (4,4), (4,3,1), (3,3,2), etc.")
print("  n=18: (5,4), (9), (8,1), (7,2), (5,3,1) etc.")
print("  n=20: (9,1), (8,2), (7,3), (6,4), (5,5), (5,3,2), (4,4,2) etc.")
print()
print("The full m-cycle (m) is the simplest pattern but FAILS for all m>3.")
print("This is the superdiagonal construction: (0,1),(1,2),...,(m-2,m-1),(m-1,0).")
print()
print("Open question: which cycle decompositions are collinear-free?")
print("Is there always at least one valid decomposition for every m?")
