#!/usr/bin/env python3
# 真正分析 rot4 解的结构规律：基本域 F、距离环、每行的点、斜率/共线残差
import os, math
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "flammenkamp_cache")
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}
EVEN = list(range(12, 41, 2))


def decode_line(line, n):
    line = line.rstrip('\n').rstrip('\r')
    if not line:
        return None
    pre = line[0]
    body = line[1:] if pre in '.:/-ocx+*' else line
    if len(body) < 2 * n:
        return None
    cols = []
    for r in range(n):
        c1 = VAL[body[2 * r]]; c2 = VAL[body[2 * r + 1]]
        if not (0 <= c1 < n and 0 <= c2 < n):
            return None
        cols += [c1, c2]
    return cols


def rot90(p, n):
    return (p[1], (n - 1) - p[0])


def load_rot4(n):
    for ext in ["", ".few"]:
        p = os.path.join(CACHE, f"n{n}_rot4{ext}")
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    cols = decode_line(line, n)
                    if cols:
                        return cols
    return None


def ring(p, n):
    ctr = (n - 1) / 2.0
    return (p[0] - ctr) ** 2 + (p[1] - ctr) ** 2


def analyze(n):
    cols = load_rot4(n)
    pts = [(r, cols[2 * r]) for r in range(n)] + [(r, cols[2 * r + 1]) for r in range(n)]
    S = set(pts)
    # 轨道 -> F
    seen = set(); F = []
    for p in pts:
        if p in seen:
            continue
        orbit = [p]
        cur = p
        for _ in range(3):
            cur = rot90(cur, n); orbit.append(cur)
        F.append(p)
        for q in orbit:
            seen.add(q)
    # 行/列计数
    rowc = Counter(r for r, c in pts)
    colc = Counter(c for r, c in pts)
    per_row = sorted(set(rowc.values()))
    per_col = sorted(set(colc.values()))
    # 距离环
    rings = {}
    for p in F:
        d = ring(p, n)
        rings.setdefault(round(d, 3), 0)
        rings[round(d, 3)] += 1
    distinct_d = sorted(rings.keys())
    # F 的斜率/共线残差：对 F 做最小二乘直线拟合，看残差
    xs = [p[1] for p in F]; ys = [p[0] for p in F]
    mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else 0
    resid = sum((y - (my + slope * (x - mx))) ** 2 for x, y in zip(xs, ys)) / len(xs)
    spread_r = max(ys) - min(ys); spread_c = max(xs) - min(xs)
    # F 点是否落在主对角线附近？算到对角线 |r-c| 分布
    diag = Counter(abs(p[0] - p[1]) for p in F)
    return {
        "n": n, "F": sorted(F), "per_row": per_row, "per_col": per_col,
        "ndistinct_d": len(distinct_d), "distinct_d": distinct_d[:12],
        "slope": slope, "resid": resid,
        "spread_r": spread_r, "spread_c": spread_c, "diag": dict(sorted(diag.items())),
    }


print(f"{'n':>3} {'|F|':>4} {'perRow':>7} {'perCol':>7} {'#rings':>6} {'slope':>7} {'resid':>7}  diag|r-c| top")
print("-" * 100)
for n in EVEN:
    a = analyze(n)
    diag_top = sorted(a["diag"].items(), key=lambda kv: -kv[1])[:3]
    diag_s = " ".join(f"{k}:{v}" for k, v in diag_top)
    print(f"{a['n']:>3} {len(a['F']):>4} {str(a['per_row']):>7} {str(a['per_col']):>7} "
          f"{a['ndistinct_d']:>6} {a['slope']:>7.2f} {a['resid']:>7.2f}  {diag_s}")

print("\n=== 距离环序列（按 n 列出每个基本域点的距离平方，四舍五入）===")
for n in EVEN:
    a = analyze(n)
    print(f"n={n:2d} ({len(a['F'])} rings): {a['distinct_d']}")

print("\n=== F 基本域点（按行顺序 r 列出 (r,c)），看是否沿某条曲线 ===")
for n in EVEN:
    a = analyze(n)
    print(f"n={n:2d}: " + " ".join(f"({r},{c})" for r, c in a["F"][:14]) + (" ..." if len(a["F"]) > 14 else ""))
