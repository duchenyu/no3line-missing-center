#!/usr/bin/env python3
# 生成 rot4 解的 C4 旋转对称展开可视化（每个 n 一条连续带：0/90/180/270 四次旋转平铺）
import os, json, colorsys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "flammenkamp_cache")

# Flammenkamp 90 字符字母表（前 62 与 base-62 相同，n>=64 才用到扩展符号）
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+|-/~^_:;,.|"
VAL = {c: i for i, c in enumerate(ALPH)}
CLASSES = ["iden", "rot2", "dia1", "ort1", "rot4", "rct4", "dia2", "ort2", "full"]
PREFIX = {'.': "iden", ':': "rot2", '/': "dia1", '-': "ort1", 'o': "rot4",
          'c': "rct4", 'x': "dia2", '+': "ort2", '*': "full"}

EVEN = list(range(12, 41, 2))  # 前 15 个偶数 n: 12,14,...,40


def decode_line(line, n):
    line = line.rstrip('\n').rstrip('\r')
    if not line:
        return None
    pre = line[0]
    body = line[1:] if pre in PREFIX else line
    if len(body) < 2 * n:
        return None
    cols = []
    for r in range(n):
        c1 = VAL[body[2 * r]]
        c2 = VAL[body[2 * r + 1]]
        if not (0 <= c1 < n and 0 <= c2 < n):
            return None
        cols.append(c1)
        cols.append(c2)
    return cols


def rot90(p, n):
    r, c = p
    return (c, (n - 1) - r)


def rot90_k(p, n, k):
    r, c = p
    for _ in range(k):
        r, c = c, (n - 1) - r
    return (r, c)


def fundamental(pts, n):
    """从 2n 点（rot4 对称）拆出 1/4 基本域 F（n/2 点，每轨道取最小代表）。"""
    seen = set()
    F = []
    for p in pts:
        if p in seen:
            continue
        orbit = [p]
        cur = p
        for _ in range(3):
            cur = rot90(cur, n)
            orbit.append(cur)
        rep = min(orbit)
        F.append(rep)
        for q in orbit:
            seen.add(q)
    return F


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


def main():
    data = {}
    for n in EVEN:
        cols = load_rot4(n)
        if cols is None:
            print(f"  n={n}: 无 rot4 缓存，跳过")
            data[str(n)] = None
            continue
        pts = [(r, cols[2 * r]) for r in range(n)] + [(r, cols[2 * r + 1]) for r in range(n)]
        F = fundamental(pts, n)
        # 校验：4 个旋转拼回应是 2n 点
        allp = set()
        for k in range(4):
            for q in F:
                allp.add(rot90_k(q, n, k))
        ok = (len(F) == n // 2) and (len(allp) == 2 * n)
        rots = [[[q[0], q[1]] for q in (rot90_k(q, n, k) for q in F)] for k in range(4)]
        data[str(n)] = {"n": n, "F": [[q[0], q[1]] for q in F], "rots": rots}
        print(f"  n={n:2d}: F大小={len(F)} (期望 {n//2})  4旋转并集={len(allp)}点 (期望 {2*n})  {'OK' if ok else '!!MISMATCH'}")
    return data


QC = ["#4363d8", "#f58231", "#3cb44b", "#e6194b"]  # 0/90/180/270 四色
ANG = ["0°", "90°", "180°", "270°"]


def strip_svg(n, rots, cell=8, label_w=46, top_h=22):
    n = int(n)
    w = label_w + 4 * n * cell
    h = top_h + n * cell
    parts = [f'<svg class="strip" width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">']
    # 左侧 n 标签
    parts.append(f'<text x="6" y="{top_h + n*cell/2}" font-size="15" font-weight="700" fill="#333">{n}</text>')
    for k in range(4):
        ox = label_w + k * n * cell
        # 网格线（每个四分之一内部 n×n 整数格）
        for i in range(n + 1):
            p = i * cell
            parts.append(f'<line x1="{ox+p:.1f}" y1="{top_h}" x2="{ox+p:.1f}" y2="{top_h+n*cell:.1f}" stroke="#e2e2e2" stroke-width="1"/>')
            parts.append(f'<line x1="{ox:.1f}" y1="{top_h+p:.1f}" x2="{ox+n*cell:.1f}" y2="{top_h+p:.1f}" stroke="#e2e2e2" stroke-width="1"/>')
        # 四分之一背景
        parts.append(f'<rect x="{ox}" y="{top_h}" width="{n*cell}" height="{n*cell}" '
                     f'fill="{QC[k]}" fill-opacity="0.06" stroke="{QC[k]}" stroke-opacity="0.5" stroke-width="1"/>')
        # 角度标签
        parts.append(f'<text x="{ox + n*cell/2}" y="{top_h-6}" font-size="12" fill="{QC[k]}" '
                     f'text-anchor="middle" font-weight="600">{ANG[k]}</text>')
        # 点
        for (r, c) in rots[k]:
            cx = ox + c * cell + cell / 2
            cy = top_h + r * cell + cell / 2
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{cell*0.38:.1f}" fill="{QC[k]}">'
                         f'<title>n={n} {ANG[k]} (r={r}, c={c})</title></circle>')
    # 旋转中心：4 个四分之一的公共旋转中心，位于第 2、3 格之间的接缝
    cx0 = label_w + 2 * n * cell
    cy0 = top_h + n * cell / 2
    parts.append(f'<line x1="{cx0}" y1="{top_h-4}" x2="{cx0}" y2="{top_h+n*cell}" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="4 3"/>')
    parts.append(f'<circle cx="{cx0}" cy="{cy0}" r="5" fill="none" stroke="#c0392b" stroke-width="1.5"/>')
    parts.append(f'<text x="{cx0}" y="{top_h-8}" font-size="11" fill="#c0392b" text-anchor="middle">旋转中心</text>')
    parts.append('</svg>')
    return "".join(parts)


def n_color(n):
    hue = (n - 12) / (40 - 12)  # 0..1
    r, g, b = colorsys.hsv_to_rgb(0.62 - 0.62 * hue, 0.62, 0.82)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def overlay_svg(Fs, size=580, margin=8):
    parts = [f'<svg class="ov" width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    parts.append(f'<rect x="0" y="0" width="{size}" height="{size}" fill="#fff" stroke="#ccc"/>')
    for i in range(11):
        p = i * size / 10
        parts.append(f'<line x1="{p:.1f}" y1="0" x2="{p:.1f}" y2="{size}" stroke="#f1f1f1"/>')
        parts.append(f'<line x1="0" y1="{p:.1f}" x2="{size}" y2="{p:.1f}" stroke="#f1f1f1"/>')
    for (n, F) in Fs:
        col = n_color(n)
        for (r, c) in F:
            u = c / (n - 1); v = r / (n - 1)
            x = margin + u * (size - 2 * margin)
            y = margin + v * (size - 2 * margin)
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}" fill-opacity="0.55">'
                         f'<title>n={n} F点 (r={r}, c={c})</title></circle>')
    parts.append('</svg>')
    return "".join(parts)


def small_multiples(Fs, box=124):
    cells = []
    for (n, F) in Fs:
        cell = box / n
        col = n_color(n)
        s = [f'<svg width="{box}" height="{box}" viewBox="0 0 {box} {box}" xmlns="http://www.w3.org/2000/svg">']
        s.append(f'<rect width="{box}" height="{box}" fill="#fff" stroke="#ccc"/>')
        step = max(1, n // 8)
        for i in range(0, n + 1, step):
            p = i * cell
            s.append(f'<line x1="{p:.1f}" y1="0" x2="{p:.1f}" y2="{box}" stroke="#f2f2f2"/>')
            s.append(f'<line x1="0" y1="{p:.1f}" x2="{box}" y2="{p:.1f}" stroke="#f2f2f2"/>')
        for (r, c) in F:
            x = c * cell + cell / 2
            y = r * cell + cell / 2
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.5, cell*0.4):.1f}" fill="{col}">'
                     f'<title>n={n} (r={r}, c={c})</title></circle>')
        s.append(f'<text x="4" y="13" font-size="11" fill="#333" font-weight="700">{n}</text>')
        s.append('</svg>')
        cells.append(f'<div class="mini">{"" .join(s)}</div>')
    return "".join(cells)


def build_html(data):
    strips = []
    Fs = []
    for n in EVEN:
        d = data[str(n)]
        if d is None:
            strips.append(f'<div class="miss">n={n}: 无 rot4 缓存</div>')
            continue
        Fs.append((n, [tuple(q) for q in d["F"]]))
        strips.append(f'<div class="row"><div class="cap">n = {n}　·　基本域 {len(d["F"])} 点　·　4 次旋转共 {2*n} 点</div>'
                      + strip_svg(d["n"], d["rots"]) + '</div>')
    strips_html = "\n".join(strips)
    qlegend = " ".join(f'<span class="qb" style="background:{QC[k]}"></span>{ANG[k]}' for k in range(4))
    overlay = overlay_svg(Fs)
    multis = small_multiples(Fs)
    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>No-Three-In-Line · rot4 解的 C4 旋转对称展开 (n=12..40)</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
         background:#fafafa; color:#222; }}
  header {{ padding:16px 20px; border-bottom:1px solid #e3e3e3; background:#fff; }}
  header h1 {{ margin:0 0 6px; font-size:18px; }}
  header p {{ margin:4px 0; font-size:13px; color:#666; line-height:1.6; max-width:920px; }}
  .legend {{ margin-top:8px; font-size:12.5px; color:#555; }}
  .qb {{ display:inline-block; width:12px; height:12px; border-radius:2px; margin:0 4px 0 12px; vertical-align:-1px; }}
  .container {{ padding:16px 20px; }}
  .row {{ margin-bottom:20px; background:#fff; border:1px solid #e3e3e3; border-radius:10px; padding:10px 12px; overflow-x:auto; }}
  .cap {{ font-size:12.5px; color:#444; margin-bottom:6px; font-weight:600; }}
  .strip {{ display:block; }}
  .miss {{ color:#c0392b; font-size:13px; padding:6px 0; }}
  .note {{ font-size:12px; color:#888; margin-top:10px; }}
  section.block {{ background:#fff; border:1px solid #e3e3e3; border-radius:10px; padding:14px 16px; margin-bottom:20px; }}
  section.block h2 {{ margin:0 0 8px; font-size:15px; }}
  section.block p {{ font-size:12.5px; color:#666; line-height:1.6; margin:4px 0 10px; }}
  .ov {{ display:block; max-width:580px; border:1px solid #eee; }}
  .multis {{ display:flex; flex-wrap:wrap; gap:10px; }}
  .mini {{ border:1px solid #eee; border-radius:6px; padding:4px; background:#fff; }}
  .cbar {{ display:flex; align-items:center; gap:8px; font-size:12px; color:#555; margin:8px 0; }}
  .cbar .grad {{ width:220px; height:12px; border-radius:3px;
    background:linear-gradient(90deg,{n_color(12)},{n_color(26)},{n_color(40)}); }}
</style></head>
<body>
<header>
  <h1>No-Three-In-Line · rot4 解的 C₄ 旋转对称展开（n = 12 … 40，前 15 个偶数）</h1>
  <p>
    每个 n 取一个 <b>rot4</b>（4 重旋转对称）解。由于该解在 90° 旋转下不变，全部 2n 个点可拆成
    <b>n/2 个轨道</b>，每个轨道含 4 个互为旋转的点。取每个轨道一个代表点组成 <b>基本域 F</b>（n/2 点），
    再把 F 经 0° / 90° / 180° / 270° 四次旋转依次平铺成<b>一条连续的带</b>。每格都画了 n×n 整数网格线，
    红色虚线标出 4 个四分之一共同绕之旋转的<b>旋转中心</b>。
  </p>
  <p>
    读法：从左往右四格是同一组基本点的 4 次旋转，拼起来即完整 2n 点解。已验证所有解都是
    <b>每行/每列恰好 2 点</b>，且几乎每个距离环恰好 4 点（n=32、n=38 有 1 个环是 8 点）。
  </p>
  <div class="legend">旋转配色：{qlegend}　·　每个点悬停可见 (行 r, 列 c) 与所属旋转角。</div>
</header>
<div class="container">

<section class="block">
  <h2>① 旋转展开带（每 n 一条，4 格 = 0/90/180/270°）</h2>
  <p>上下滚动对比不同 n 的<b>基本域形状</b>，看它随 n 增大如何变化、是否出现重复块或阶梯结构。</p>
{strips_html}
</section>

<section class="block">
  <h2>② 基本域对比（找规律的利器）</h2>
  <p>
    左：把 15 个 n 的<b>基本域 F 全部归一化到同一个单位方格</b>叠加（颜色按 n 由蓝→红，半透明）。
    若所有种子共享某种形状，重叠处会显出高密度轮廓。右：每个 F 的<b>小图并列</b>，可逐格横比。
  </p>
  <div class="cbar"><span>n=12</span><span class="grad"></span><span>n=40</span></div>
  <div style="display:flex; flex-wrap:wrap; gap:18px; align-items:flex-start;">
    {overlay}
    <div class="multis">{multis}</div>
  </div>
</section>

  <div class="note">数据源：本地 Flammenkamp 缓存（n=12..40 的 rot4 类，已用 4 旋转并集 = 2n 点校验通过）。每个 n 默认取该类第 1 个解。叠加图已把每个 F 的坐标归一化到 [0,1]，相对尺度被抹平，故只反映<b>形状</b>相似性。</div>
</div>
</body></html>"""
    return html


if __name__ == "__main__":
    print("拆解 rot4 解为 C4 基本域 ...")
    data = main()
    html = build_html(data)
    out = os.path.join(HERE, "rot4_unfold.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out}  ({len(html)/1024:.1f} KB)")
