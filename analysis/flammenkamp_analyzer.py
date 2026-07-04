"""
Analyze all Flammenkamp configuration files for missing-center solutions.
Downloads and processes all files for n=7 to 22.
"""
import urllib.request
from collections import Counter

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
char_to_val = {c: i for i, c in enumerate(ALPHABET)}

SYMM_NAMES = {
    '.': 'iden', ':': 'rot2', '/': 'dia1', '-': 'ort1',
    'o': 'rot4', 'c': 'rct4', 'x': 'dia2', '+': 'ort2', '*': 'full'
}

def decode_solution(line):
    symm = line[0]
    rest = line.strip()[1:]
    n = len(rest) // 2
    points = []
    for row in range(n):
        c1 = char_to_val[rest[2*row]]
        c2 = char_to_val[rest[2*row+1]]
        points.append((row, c1))
        points.append((row, c2))
    return symm, n, points

def has_center(n, points):
    ctr = (n-1)/2.0
    rings = Counter()
    for i, j in points:
        d2 = int(round((i-ctr)**2 + (j-ctr)**2))
        rings[d2] += 1
    return any(v >= 3 for v in rings.values())

# n values and symmetry classes to check
n_range = list(range(7, 23)) + [24, 27, 30]
symm_classes = ['iden', 'rot2', 'dia1', 'dia2', 'full', 'rot4', 'ort1', 'ort2', 'rct4']
symm_char = {'.': 'iden', ':': 'rot2', '/': 'dia1', '-': 'ort1',
             'o': 'rot4', 'c': 'rct4', 'x': 'dia2', '+': 'ort2', '*': 'full'}

# Quick symm char -> name mapping
symm_to_name = symm_char

print(f"{'n':>3} {'Total':>7} {'Missing':>8} {'Rate%':>7} {'Breakdown':<60}")
print("-" * 90)

for n in n_range:
    total_all = 0
    missing_all = 0
    details = []
    
    for symm_name in symm_classes:
        url = f'https://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/n{n}_{symm_name}'
        try:
            with urllib.request.urlopen(url, timeout=10) as f:
                lines = f.read().decode().strip().split('\n')
            if not lines or (len(lines) == 1 and not lines[0].strip()):
                continue
                
            count = len(lines)
            missing = sum(1 for line in lines if not has_center(n, decode_solution(line)[2]))
            total_all += count
            missing_all += missing
            if count > 0:
                details.append(f'{symm_name}:{count}(-{missing})')
        except Exception as e:
            pass
    
    rate = missing_all / total_all * 100 if total_all > 0 else 0
    det_str = ', '.join(details)
    print(f"{n:>3} {total_all:>7} {missing_all:>8} {rate:>6.2f}% | {det_str:<60}")
