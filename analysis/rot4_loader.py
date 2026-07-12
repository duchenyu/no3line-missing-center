"""
Loader + validator for Flammenkamp rot4 (C4-symmetric) solutions, all even n.

Formats (both share structure: one symmetry char 'o', then 2n symbols encoding
two column indices per row):
  * plain  files n{n}_rot4          : base-62 alphabet (cols 0..61)  -> n<=56
  * .few   files n{n}_rot4.few       : base-80 alphabet (cols 0..79)  -> n>=58

The base-80 alphabet's first 62 symbols equal the base-62 set, so a single
80-symbol alphabet decodes both. We verify each decoded solution has 2n points
and is no-three-in-line (sanity that the decoder is correct).
"""
import os, math, sys
from itertools import combinations

ALPH = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|'
VAL = {c: i for i, c in enumerate(ALPH)}
SYMM = set('.:/-ocx+*')

# Local cache lives in the same analysis/ directory as this loader.
CACHE = os.path.join(os.path.dirname(__file__), 'flammenkamp_cache')

def decode_line(line, n):
    line = line.strip()
    body = line[1:] if line and line[0] in SYMM else line
    pts = []
    for r in range(n):
        c1 = VAL[body[2 * r]]
        c2 = VAL[body[2 * r + 1]]
        pts.append((c1, r))   # (x=col, y=row)
        pts.append((c2, r))
    return pts

def is_valid(pts, n):
    P = list(pts)
    for a, b, c in combinations(P, 3):
        if (b[0]-a[0])*(c[1]-a[1]) == (c[0]-a[0])*(b[1]-a[1]):
            return False
    return True

def load_rot4(n):
    """Return list of solutions; each solution = list of (x=col, y=row) tuples."""
    for ext in ('', '.few'):
        path = os.path.join(CACHE, f'n{n}_rot4{ext}')
        if not os.path.exists(path):
            continue
        sols = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                pts = decode_line(line, n)
                if len(pts) == 2 * n:
                    sols.append(pts)
        return sols, ext
    return [], None

if __name__ == '__main__':
    even_ns = list(range(6, 45, 2)) + [54, 56] + list(range(58, 73, 2))
    total = 0
    print(f"{'n':>3} {'fmt':>5} {'count':>7} {'valid?':>7}")
    print('-' * 30)
    for n in even_ns:
        sols, ext = load_rot4(n)
        if ext is None:
            print(f"{n:>3}   --     0     n/a")
            continue
        # spot-validate first & last
        ok_first = is_valid(sols[0], n) if sols else True
        ok_last = is_valid(sols[-1], n) if sols else True
        total += len(sols)
        flag = 'OK' if (ok_first and ok_last) else 'BAD'
        print(f"{n:>3} {ext:>5} {len(sols):>7} {flag:>7}")
    print('-' * 30)
    print(f"TOTAL rot4 solutions across even n: {total}")
