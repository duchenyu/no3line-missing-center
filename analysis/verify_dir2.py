#!/usr/bin/env python3
# 方向2: 把 "rot4 解的对角线方向互异" 推广到所有含 180° 旋转对称的解
# 验证: 偶数 n 的解若对 180° 旋转(R180)不变, 则拆成 n 个 R180-轨道(size 2),
#        每个轨道关于中心对称 -> 定义一条过中心的方向; 这 n 条方向两两不平行
#        (否则 2 个轨道共线 -> 4 点共线 -> 与 no-3-in-line 矛盾).
# 同时确认 iden/dia1 等不含 R180 对称, 划定定律适用范围.
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

def load_solutions(n, cls, limit=200):
    out = []
    for ext in ["", ".few"]:
        p = f"flammenkamp_cache/n{n}_{cls}{ext}"
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    c = decode(line, n)
                    if c is None:
                        continue
                    pts = [(r, c[2 * r]) for r in range(n)] + [(r, c[2 * r + 1]) for r in range(n)]
                    if len(set(pts)) != 2 * n:
                        continue
                    out.append(pts)
                    if len(out) >= limit:
                        return out
            return out
    return out

def R180(p, n):
    return (n - 1 - p[0], n - 1 - p[1])

def invariant_180(pts, n):
    S = set(pts)
    return all(R180(p, n) in S for p in pts)

def decompose_180(pts, n):
    # 返回 R180 轨道列表, 每轨道是 [p, R180(p)] (size 2)
    seen = set(); orbits = []
    for p in pts:
        if p in seen:
            continue
        q = R180(p, n)
        if q == p:
            continue  # 偶数 n 中心非格点, 不应发生
        orbits.append((p, q))
        seen.add(p); seen.add(q)
    return orbits

def direction(p, n):
    # 返回相对中心的偏移向量
    ctr = (n - 1) / 2.0
    return (p[0] - ctr, p[1] - ctr)

def parallels(v1, v2):
    # 半整数坐标 -> 整数叉积
    a = (round(v1[0] * 2), round(v1[1] * 2))
    b = (round(v2[0] * 2), round(v2[1] * 2))
    return a[0] * b[1] - a[1] * b[0] == 0

def check(pts, n):
    if not invariant_180(pts, n):
        return None  # 不含 R180 对称
    orbits = decompose_180(pts, n)
    if len(orbits) != n:
        return ("BAD_ORBIT_COUNT", len(orbits))
    dirs = [direction(o[0], n) for o in orbits]
    # 检查两两不平行
    for i in range(len(dirs)):
        for j in range(i + 1, len(dirs)):
            if parallels(dirs[i], dirs[j]):
                return ("VIOLATION_PARALLEL", i, j, dirs[i], dirs[j])
    return ("OK", len(dirs))

CLASSES = ["iden", "rot2", "dia1", "ort1", "rot4", "dia2"]
EVEN = list(range(12, 73, 2))


def main():
    print(f"{'n':>3} {'class':6s} {'#sol':>5s} {'inv180?':7s} {'结果':>22s}")
    print("-" * 70)
    summary = {}
    for n in EVEN:
        for cls in CLASSES:
            sols = load_solutions(n, cls, limit=200)
            if not sols:
                continue
            inv_count = 0
            ok = 0; viol = 0; bad = 0; noninv = 0
            for pts in sols:
                r = check(pts, n)
                if r is None:
                    noninv += 1
                else:
                    inv_count += 1
                    if r[0] == "OK":
                        ok += 1
                    elif r[0] == "VIOLATION_PARALLEL":
                        viol += 1
                    else:
                        bad += 1
            tag = "inv" if inv_count else "no"
            res = f"OK={ok}" if (viol == 0 and bad == 0) else f"VIOL={viol} BAD={bad}"
            print(f"{n:>3} {cls:6s} {len(sols):>5d} {tag:7s} {res:>22s}  (inv={inv_count}, noninv={noninv})")
            summary[(n, cls)] = (inv_count, ok, viol, bad, noninv)

    print("\n=== 汇总 ===")
    tot_inv = sum(v[0] for v in summary.values())
    tot_viol = sum(v[2] for v in summary.values())
    tot_ok = sum(v[1] for v in summary.values())
    print(f"含 R180 对称的解总数(采样): {tot_inv}")
    print(f"  -> 方向互异(无平行对)的: {tot_ok}")
    print(f"  -> 出现平行对(=4点共线, 应=0): {tot_viol}")
    print("结论: 若 tot_viol==0, 则真实数据支持定理; 定理本身可由'2对同中心线=>4共线'严格证明.")


if __name__ == "__main__":
    main()
