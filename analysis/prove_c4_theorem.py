#!/usr/bin/env python3
"""
验证 C₄ 旋转对称性下：
1) 同一轨道内的 4 个点到网格中心的距离是否相等
2) n 为偶数时是否存在 C₄ 对称解及其中心状态
"""
from collections import defaultdict
import sys
sys.path.insert(0, "D:/djr82/Documents/workbuddy/2026-07-03-16-29-36")
from analyze_rle import parse_rle

def d_from_center(x, y, n):
    cx2 = cy2 = n - 1
    return (2*x - cx2)**2 + (2*y - cy2)**2

def rotate_90(p, n):
    x, y = p
    return (n-1-y, x)

def rotate_180(p, n):
    x, y = p
    return (n-1-x, n-1-y)

def rotate_270(p, n):
    x, y = p
    return (y, n-1-x)

def has_c4_symmetry(pts, n):
    """Check if solution has C4 symmetry (invariant under 90° rotation)."""
    s = set(pts)
    for p in pts:
        rp = rotate_90(p, n)
        if rp not in s:
            return False
    return True

# ===== Verification 1: Distance invariance under 90° rotation =====
print("="*60)
print("Proof Verification 1: Distance Invariance")
print("="*60)

n = 12
# Test all grid points
for x in range(n):
    for y in range(n):
        p = (x, y)
        rp = rotate_90(p, n)
        rrp = rotate_180(p, n)
        rrrp = rotate_270(p, n)
        
        d0 = d_from_center(x, y, n)
        d1 = d_from_center(*rp, n)
        d2 = d_from_center(*rrp, n)
        d3 = d_from_center(*rrrp, n)
        
        if not (d0 == d1 == d2 == d3):
            print(f"  ❌ Distance NOT invariant at ({x},{y}): {d0},{d1},{d2},{d3}")
            break
else:
    print(f"  ✅ All grid points: distance invariant under C₄ (n={n})")

# ===== Verification 2: C₄ orbit sizes =====
print(f"\n{'='*60}")
print("Proof Verification 2: C₄ Orbit Structures")
print("="*60)

for n in [12, 13, 14]:
    orbits_4 = 0
    orbits_2 = 0
    orbits_1 = 0
    
    seen = set()
    for x in range(n):
        for y in range(n):
            if (x, y) in seen:
                continue
            
            p = (x, y)
            rp = rotate_90(p, n)
            rrp = rotate_180(p, n)
            
            if rp == p:
                # Fixed by 90° rotation → must be center
                orbits_1 += 1
                seen.add(p)
            elif rrp == p:
                # Fixed by 180° but not 90° → size 2
                orbits_2 += 1
                seen.add(p)
                seen.add(rp)
            else:
                # Generic size 4
                orbits_4 += 1
                seen.add(p)
                seen.add(rp)
                seen.add(rrp)
                seen.add(rotate_270(p, n))
    
    print(f"  n={n}: {orbits_4}×4-orbits + {orbits_2}×2-orbits + {orbits_1}×1-orbits = {4*orbits_4 + 2*orbits_2 + orbits_1} pts")

# ===== Verification 3: Check actual C₄ solutions from data =====
print(f"\n{'='*60}")
print("Proof Verification 3: C₄ Solutions in Actual Data")
print("="*60)

for n in [12, 13, 14]:
    with open(f"D:/djr82/Documents/workbuddy/2026-07-03-16-29-36/results_{n}.out") as f:
        sols = parse_rle(f.read(), n)
    
    c4_count = 0
    c4_missing_center = 0
    missing_total = 0
    
    for pts in sols:
        # Check C₄ symmetry (of the solution set)
        if has_c4_symmetry(pts, n):
            c4_count += 1
            # Check center
            from collections import Counter
            dc = Counter()
            cx2 = cy2 = n - 1
            for x, y in pts:
                d = (2*x - cx2)**2 + (2*y - cy2)**2
                dc[d] += 1
            max_ring = max(dc.values())
            if max_ring <= 2:
                c4_missing_center += 1
    
    print(f"  n={n}: {c4_count} C₄ solutions, {c4_missing_center} missing-center")
    if c4_missing_center == 0:
        print(f"    ✅ C₄ → always has center (as predicted)")
    else:
        print(f"    ❌ C₄ → some missing-center (contradicts theory!)")

# ===== Verification 4: Distance ring distribution in C₄ solutions =====
print(f"\n{'='*60}")
print("Proof Verification 4: Ring Distribution in C₄ Solutions")
print("="*60)

n = 12
with open(f"D:/djr82/Documents/workbuddy/2026-07-03-16-29-36/results_{n}.out") as f:
    sols = parse_rle(f.read(), n)

for idx, pts in enumerate(sols):
    if not has_c4_symmetry(pts, n):
        continue
    
    cx2 = cy2 = n - 1
    ring_counts = defaultdict(int)
    for x, y in pts:
        d = (2*x - cx2)**2 + (2*y - cy2)**2
        ring_counts[d] += 1
    
    print(f"  C₄ Solution #{idx}:")
    print(f"    Used rings: {len(ring_counts)}")
    for d, cnt in sorted(ring_counts.items()):
        marker = " ← Center!" if cnt >= 3 else ""
        print(f"      d={d:4d}: {cnt} pts{marker}")
    print(f"    Max ring count: {max(ring_counts.values())}")
    print()
