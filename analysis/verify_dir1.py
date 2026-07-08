#!/usr/bin/env python3
# 方向1: 偶数 n 网格的四染色(按 (r%2, c%2)) 配额分析
# (a) 证明每条直线至多触及 4 色中的 2 色 -> 上界 D(n) <= 2n (平凡上界的独立证明)
# (b) 推导极大(2n)解的"完全颜色平衡"必要条件: 每色恰 n/2 点, 每行恰 1 点入其 2 色
# (c) 用真实 2n 解数据验证平衡条件
import os
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}
PREFIX = set('.:/-ocx+*')

def decode(line, n):
    line = line.rstrip('\n').rstrip('\r')
    if not line:
        return None
    pre = line[0]
    body = line[1:] if pre in PREFIX else line
    if len(body) < 2 * n:
        return None
    cols = []
    for r in range(n):
        c1 = VAL[body[2 * r]]; c2 = VAL[body[2 * r + 1]]
        if not (0 <= c1 < n and 0 <= c2 < n):
            return None
        cols += [c1, c2]
    return cols

def load(n, cls, limit=200):
    for ext in ["", ".few"]:
        p = f"flammenkamp_cache/n{n}_{cls}{ext}"
        if os.path.exists(p):
            out = []
            with open(p) as f:
                for line in f:
                    c = decode(line, n)
                    if c is None:
                        continue
                    pts = [(r, c[2 * r]) for r in range(n)] + [(r, c[2 * r + 1]) for r in range(n)]
                    if len(set(pts)) == 2 * n:
                        out.append(pts)
                    if len(out) >= limit:
                        return out
            return out
    return []

def color(p):
    return (p[0] & 1, p[1] & 1)

print("=== (a) 每条直线至多触及 2 色的逻辑验证(对所有可能斜率) ===")
# 直线方向 (a,b) 既约(gcd=1). 步长改变 (r,c) 奇偶性 by (a%2, b%2).
# 由于 gcd(a,b)=1, a,b 不全偶 -> 步长奇偶性为 (奇,奇)/(奇,偶)/(偶,奇) 三种, 各把颜色在 2 色间交替.
from math import gcd
maxcolors = 0
for a in range(-6, 7):
    for b in range(-6, 7):
        if a == 0 and b == 0:
            continue
        g = gcd(abs(a), abs(b)) or 1
        aa, bb = a // g, b // g
        if aa == 0 and bb == 0:
            continue
        # 从 (0,0) 出发走若干步, 收集颜色
        cols = set()
        r = c = 0
        for _ in range(20):
            cols.add((r & 1, c & 1))
            r += aa; c += bb
        maxcolors = max(maxcolors, len(cols))
print(f"  对 |a|,|b|<=6 的所有既约方向, 一条线触及的颜色数最大值 = {maxcolors} (应=2)")

print("\n=== (b)/(c) 极大 2n 解的颜色平衡(用真实数据) ===")
EVEN = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 44]
for n in EVEN:
    # 用 rot4 类(已知是 2n 解且含 R180 对称)做代表
    sols = load(n, "rot4", limit=50)
    if not sols:
        continue
    bal_ok = 0
    for pts in sols:
        cnt = {c: 0 for c in [(0,0),(0,1),(1,0),(1,1)]}
        rowcnt = {}
        for p in pts:
            cnt[color(p)] += 1
            rowcnt[p[0]] = rowcnt.get(p[0], 0) + 1
        # 平衡: 每色 = n/2, 每行 = 2
        balanced = all(v == n // 2 for v in cnt.values()) and all(v == 2 for v in rowcnt.values())
        if balanced:
            bal_ok += 1
    cnt_sample = {c: 0 for c in [(0,0),(0,1),(1,0),(1,1)]}
    for p in sols[0]:
        cnt_sample[color(p)] += 1
    print(f"  n={n:>2}: 采样 {len(sols)} 解, 平衡(每色=n/2,每行=2) 的解数 = {bal_ok}; 示例配色计数 {cnt_sample}")
