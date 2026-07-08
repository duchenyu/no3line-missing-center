#!/usr/bin/env python3
"""
build_overlay.py — Generate a self-contained HTML that overlays No-Three-In-Line
solutions for EVEN n in 12..72.

For each even n present in the Flammenkamp cache, concatenating its symmetry-class
files (iden, rot2, dia1, rot4, rct4, dia2, ort1, ort2, full) yields the D4-inequivalent
solution list in the same order the paper counts them. The k-th D4-inequivalent
solution = the k-th line overall. We decode and embed each solution's 2n column
coordinates (row order) into the HTML so the user can pick any (n, k) and overlay.

Largest selected n is rendered as the FIXED base layer; smaller-n layers are
drawn on top and are draggable with the mouse.

No circles this time (per user request) — just grid lines + solution points.
"""
import os, re, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "flammenkamp_cache")

# Flammenkamp 90-char encoding alphabet (base-62 prefix + extension for n>=62).
# First 62 chars equal standard base-62, so legacy regular files still decode.
ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#$%&@?!()[]<>{}=*+\\|/~^_:;,."
VAL = {c: i for i, c in enumerate(ALPH)}


def valid_solution(pts, n):
    """pts: list of (r,c). Check 2n distinct points, no three collinear."""
    if len(set(pts)) != 2 * n:
        return False
    m = len(pts)
    for i in range(m):
        xi, yi = pts[i]
        for j in range(i + 1, m):
            xj, yj = pts[j]
            for k in range(j + 1, m):
                xk, yk = pts[k]
                if (xj - xi) * (yk - yi) - (yj - yi) * (xk - xi) == 0:
                    return False
    return True

CLASSES = ['iden', 'rot2', 'dia1', 'rot4', 'rct4', 'dia2', 'ort1', 'ort2', 'full']

# Known D4-inequivalent totals (from the extended paper table, tab:d4 to n=53,
# plus rot4-only counts for 54..72 from the cache). Used only to VALIDATE decode.
KNOWN = {12: 566, 14: 1366, 16: 5900, 18: 19204, 20: 118057, 22: 1275,
         24: 2920, 26: 4949, 28: 12203, 30: 24925, 32: 175, 34: 172, 36: 282,
         38: 338, 40: 541, 42: 747, 44: 1017, 54: 7696, 56: 10441, 58: 19,
         60: 32, 62: 5, 64: 25, 66: 2, 68: 2, 70: 1, 72: 1}

CAP = 4000  # max solutions stored per n (keeps file size reasonable)

EVEN_ALL = list(range(12, 73, 2))  # 12..72 inclusive


def decode_line(line, n):
    """line = 1-char symmetry prefix + 2n base-62 chars. Returns flat columns list."""
    body = line[1:1 + 2 * n]
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


def build():
    data_n = {}
    present = []
    for n in EVEN_ALL:
        files = []
        for cls in CLASSES:
            p = os.path.join(CACHE, f"n{n}_{cls}")
            pf = p + ".few"
            if os.path.exists(p):
                files.append(p)
            elif os.path.exists(pf):
                files.append(pf)
        if not files:
            continue  # e.g. 46,48,50,52 not cached
        flat = []
        total = 0
        for p in files:
            with open(p, 'r') as f:
                for line in f:
                    line = line.rstrip('\n').rstrip('\r')
                    if not line:
                        continue
                    cols = decode_line(line, n)
                    if cols is None:
                        continue
                    total += 1
                    if len(flat) // (2 * n) < CAP:
                        flat.extend(cols)
        stored = len(flat) // (2 * n)
        data_n[str(n)] = {"total": total, "stored": stored, "sols": flat}
        # ---- validate decode (critical for n>=64 .few files) ----
        check_idx = {0, stored - 1}
        if n in (64, 66, 68, 70, 72):
            check_idx = set(range(stored))
        bad = 0
        for idx in sorted(i for i in check_idx if i >= 0):
            ptlist = []
            for r in range(n):
                c1 = flat[idx * 2 * n + 2 * r]
                c2 = flat[idx * 2 * n + 2 * r + 1]
                ptlist.append((r, c1)); ptlist.append((r, c2))
            if not valid_solution(ptlist, n):
                bad += 1
        if bad:
            print(f"  !! n={n}: {bad} INVALID solutions among {len(check_idx)} checked")
        present.append(n)
        # validate
        if n in KNOWN and total != KNOWN[n]:
            print(f"  !! WARNING n={n}: decoded total {total} != known {KNOWN[n]}")
        else:
            print(f"  n={n:2d}: total={total:7d} stored={stored:7d}  {'OK' if n in KNOWN else '(no check)'}")
    missing = [n for n in EVEN_ALL if n not in present]
    print(f"Present even n: {present}")
    print(f"Missing (not cached): {missing}")
    return {"cap": CAP, "availableEven": present,
            "missingEven": missing, "n": data_n}


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>No-Three-In-Line — 偶数解重叠可视化 (12–72)</title>
<style>
  :root { --bg:#fafafa; --panel:#fff; --ink:#222; --muted:#777; --line:#e3e3e3; --accent:#4363d8; }
  * { box-sizing:border-box; }
  body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--ink); }
  header { padding:14px 18px; border-bottom:1px solid var(--line); background:var(--panel); }
  header h1 { margin:0; font-size:17px; }
  header p { margin:4px 0 0; font-size:12.5px; color:var(--muted); line-height:1.5; }
  .wrap { display:flex; gap:18px; padding:18px; align-items:flex-start; flex-wrap:wrap; }
  .stagebox { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:10px; }
  #stage { display:block; background:#fff; border:1px solid var(--line); border-radius:6px; touch-action:none; }
  .side { flex:1; min-width:320px; max-width:460px; }
  .card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; margin-bottom:14px; }
  .card h2 { margin:0 0 10px; font-size:14px; }
  .layer { display:flex; align-items:center; gap:6px; flex-wrap:wrap; padding:7px 0; border-top:1px dashed var(--line); font-size:13px; }
  .layer:first-of-type { border-top:none; }
  .sw { width:14px; height:14px; border-radius:50%; display:inline-block; flex:0 0 auto; }
  select, input.kinput { font-size:13px; padding:3px 5px; border:1px solid #ccc; border-radius:5px; }
  input.kinput { width:64px; }
  .st { color:var(--muted); font-size:11.5px; }
  button { font-size:13px; padding:5px 10px; border:1px solid var(--accent); background:var(--accent); color:#fff; border-radius:6px; cursor:pointer; }
  button.ghost { background:#fff; color:var(--accent); }
  button.rem { background:#fff; color:#c0392b; border-color:#e0a9a0; padding:2px 8px; }
  .row-btns { display:flex; gap:8px; margin-top:6px; }
  .note { font-size:11.5px; color:var(--muted); margin-top:8px; line-height:1.5; }
  .legend { font-size:12px; line-height:1.7; }
  .legend b { font-weight:600; }
</style>
</head>
<body>
<header>
  <h1>No-Three-In-Line — 偶数解重叠可视化（n = 12 … 72）</h1>
  <p>
    在下方为若干个偶数 n 指定「第几个解」，它们按<b>统一坐标比例</b>重叠绘制在同一画布上
    （每格像素相同：n=72 填满整幅，较小的 n 只占左上角对应的一小块区域）。
    <b>最大的 n 固定不动</b>（底层灰色网格为参考），其余较小的解绘制在上层、用各自颜色描出
    <b>彩色线框</b>标示其 n×n 范围，且<b>可用鼠标拖动</b>。拖动时会<b>就近吸附到网格线</b>，
    并<b>始终限制在最大 n 方框范围内</b>（不会拖出去）。本次仅画网格线与解点，不画外接圆。
  </p>
</header>

<div class="wrap">
  <div class="stagebox">
    <svg id="stage" width="680" height="680" viewBox="0 0 680 680"></svg>
  </div>

  <div class="side">
    <div class="card">
      <h2>解层（Layers）</h2>
      <div id="layers"></div>
      <div class="row-btns">
        <button id="add">+ 添加一层</button>
        <button id="reset" class="ghost">复位位置</button>
      </div>
      <div class="note" id="missing"></div>
    </div>
    <div class="card">
      <h2>图例 / 状态</h2>
      <div class="legend" id="legend"></div>
    </div>
  </div>
</div>

<script>
const DATA = /*__DATA__*/;
const SVGNS = "http://www.w3.org/2000/svg";
const SIZE = 680;
const PALETTE = ["#e6194b","#3cb44b","#4363d8","#f58231","#911eb4","#008080","#f032e6","#bcf60c","#9a6324","#46f0f0"];
const svg = document.getElementById("stage");
const layerList = document.getElementById("layers");
const legendEl = document.getElementById("legend");
let layers = [];
let drag = null;

function maxN(){ return layers.reduce((m,l)=>Math.max(m,l.n), 0); }

function getPoints(n, k){
  const o = DATA.n[String(n)];
  if(!o) return {error:"无缓存数据"};
  if(k < 1 || k > o.stored) return {error:`k 超出可选范围 (1..${o.stored})`};
  const off = (k-1) * 2 * n;
  const a = o.sols;
  const pts = [];
  for(let r=0; r<n; r++){
    const c1 = a[off + 2*r], c2 = a[off + 2*r + 1];
    pts.push([r, c1]); pts.push([r, c2]);
  }
  return {pts: pts};
}

function attachDrag(g, l){
  g.style.cursor = "move";
  g.addEventListener("pointerdown", e=>{
    drag = {l:l, g:g, sx:e.clientX, sy:e.clientY, ox:l.dx, oy:l.dy};
    g.setPointerCapture(e.pointerId);
    e.preventDefault();
  });
  g.addEventListener("pointermove", e=>{
    if(!drag || drag.g !== g) return;
    // 屏幕像素 -> SVG 单位（防止 CSS 缩放导致比例失真）
    const r = svg.getBoundingClientRect();
    const s = SIZE / r.width;
    let nx = drag.ox + (e.clientX - drag.sx) * s;
    let ny = drag.oy + (e.clientY - drag.sy) * s;
    // 就近吸附到基准网格格线 + 限制在小 n 方框内不越界
    const baseN = maxN();
    const cell = SIZE / baseN;
    const maxOff = (baseN - l.n) * cell;
    nx = Math.round(nx / cell) * cell;
    ny = Math.round(ny / cell) * cell;
    if(nx < 0) nx = 0; if(nx > maxOff) nx = maxOff;
    if(ny < 0) ny = 0; if(ny > maxOff) ny = maxOff;
    l.dx = nx; l.dy = ny;
    g.setAttribute("transform", `translate(${l.dx},${l.dy})`);
  });
  const end = ()=>{ drag = null; };
  g.addEventListener("pointerup", end);
  g.addEventListener("pointercancel", end);
}

// 小 n 的彩色线框：用与基准相同的坐标比例，画出它的 n×n 范围（左上角小块）
function drawWireframe(g, n, cell, color){
  const w = n * cell;
  const rect = document.createElementNS(SVGNS, "rect");
  rect.setAttribute("x", 0); rect.setAttribute("y", 0);
  rect.setAttribute("width", w); rect.setAttribute("height", w);
  rect.setAttribute("fill", color); rect.setAttribute("fill-opacity", "0.07");
  rect.setAttribute("stroke", color); rect.setAttribute("stroke-width", "2");
  g.appendChild(rect);
  const gl = document.createElementNS(SVGNS, "g");
  gl.setAttribute("stroke", color); gl.setAttribute("stroke-width", "1");
  gl.setAttribute("stroke-opacity", "0.4");
  for(let i=1; i<n; i++){
    const p = i * cell;
    const a = document.createElementNS(SVGNS, "line");
    a.setAttribute("x1",0); a.setAttribute("y1",p); a.setAttribute("x2",w); a.setAttribute("y2",p);
    const b = document.createElementNS(SVGNS, "line");
    b.setAttribute("x1",p); b.setAttribute("y1",0); b.setAttribute("x2",p); b.setAttribute("y2",w);
    gl.appendChild(a); gl.appendChild(b);
  }
  g.appendChild(gl);
}

function render(){
  while(svg.firstChild) svg.removeChild(svg.firstChild);
  if(layers.length === 0){
    legendEl.innerHTML = "<span class='st'>尚未添加任何层。点击「+ 添加一层」。</span>";
    return;
  }
  const baseN = maxN();
  let overlayCount = 0;
  layers.forEach((l, idx)=>{
    const isBase = (l.n === baseN);
    const g = document.createElementNS(SVGNS, "g");
    g.setAttribute("transform", `translate(${l.dx},${l.dy})`);
    const res = getPoints(l.n, l.k);
    if(!res || res.error){
      const t = document.createElementNS(SVGNS, "text");
      t.setAttribute("x", 12); t.setAttribute("y", 24);
      t.setAttribute("fill", "#c0392b"); t.setAttribute("font-size", "14");
      t.textContent = `n=${l.n} #${l.k} — ${res?res.error:'无数据'}`;
      g.appendChild(t);
    } else {
      const cell = SIZE / baseN;
      const rad = Math.max(2, Math.min(6, cell * 0.32));
      if(isBase){
        const gl = document.createElementNS(SVGNS, "g");
        gl.setAttribute("stroke", "#e6e6e6"); gl.setAttribute("stroke-width", "1");
        for(let i=0; i<=l.n; i++){
          const p = i * cell;
          const a = document.createElementNS(SVGNS, "line");
          a.setAttribute("x1",0); a.setAttribute("y1",p); a.setAttribute("x2",SIZE); a.setAttribute("y2",p);
          const b = document.createElementNS(SVGNS, "line");
          b.setAttribute("x1",p); b.setAttribute("y1",0); b.setAttribute("x2",p); b.setAttribute("y2",SIZE);
          gl.appendChild(a); gl.appendChild(b);
        }
        g.appendChild(gl);
        const cc = document.createElementNS(SVGNS, "circle");
        cc.setAttribute("cx", SIZE/2); cc.setAttribute("cy", SIZE/2);
        cc.setAttribute("r", 5); cc.setAttribute("fill","none");
        cc.setAttribute("stroke", "#c0392b"); cc.setAttribute("stroke-width", 1.5);
        g.appendChild(cc);
        const lbl = document.createElementNS(SVGNS, "text");
        lbl.setAttribute("x", 8); lbl.setAttribute("y", 18);
        lbl.setAttribute("fill", "#c0392b"); lbl.setAttribute("font-size", "13");
        lbl.setAttribute("font-family", "monospace");
        lbl.textContent = `固定基准 n=${l.n} (中心 ○)`;
        g.appendChild(lbl);
      } else {
        drawWireframe(g, l.n, cell, l.color);
      }
      res.pts.forEach(([r,c])=>{
        const cx = c*cell + cell/2, cy = r*cell + cell/2;
        const circ = document.createElementNS(SVGNS, "circle");
        circ.setAttribute("cx", cx); circ.setAttribute("cy", cy); circ.setAttribute("r", rad);
        circ.setAttribute("fill", l.color);
        circ.setAttribute("fill-opacity", isBase ? 0.92 : 0.85);
        circ.setAttribute("stroke", isBase ? "#333" : "none");
        circ.setAttribute("stroke-width", isBase ? 1 : 0);
        g.appendChild(circ);
      });
      if(!isBase){
        overlayCount++;
        const off = Math.round(Math.hypot(l.dx, l.dy));
        const lbl = document.createElementNS(SVGNS, "text");
        lbl.setAttribute("x", 8); lbl.setAttribute("y", 8 + overlayCount*15);
        lbl.setAttribute("fill", l.color); lbl.setAttribute("font-size", "12");
        lbl.setAttribute("font-family", "monospace");
        lbl.textContent = `n=${l.n} #${l.k}  (偏移 ${off}px)`;
        g.appendChild(lbl);
      }
    }
    if(!isBase) attachDrag(g, l);
    svg.appendChild(g);
  });
  renderLegend(baseN);
}

function renderLegend(baseN){
  let html = "";
  layers.forEach((l, idx)=>{
    const o = DATA.n[String(l.n)];
    const tag = (l.n === baseN) ? "<b>固定</b>" : "可拖动";
    const tot = o ? o.total : 0, st = o ? o.stored : 0;
    html += `<div><span class="sw" style="background:${l.color}"></span> `
          + `n=${l.n} · 第 ${l.k} 解 · ${tag} · 共 ${tot} 解`
          + (st < tot ? `（本地可选前 ${st}）` : ``)
          + `</div>`;
  });
  legendEl.innerHTML = html;
}

function renderControls(){
  layerList.innerHTML = "";
  const baseN = maxN();
  layers.forEach((l, idx)=>{
    const row = document.createElement("div");
    row.className = "layer";
    const sw = document.createElement("span");
    sw.className = "sw"; sw.style.background = l.color;
    const sel = document.createElement("select");
    DATA.availableEven.forEach(n=>{
      const o = document.createElement("option");
      o.value = n; o.textContent = "n="+n;
      if(n === l.n) o.selected = true;
      sel.appendChild(o);
    });
    sel.onchange = ()=>{ l.n = parseInt(sel.value); render(); };
    const k = document.createElement("input");
    k.type = "number"; k.min = 1; k.className = "kinput"; k.value = l.k;
    const o = DATA.n[String(l.n)];
    k.max = o ? o.stored : 1;
    k.onchange = ()=>{ l.k = parseInt(k.value) || 1; render(); };
    const st = document.createElement("span");
    st.className = "st";
    const tot = o ? o.total : 0, st2 = o ? o.stored : 0;
    st.textContent = `(共${tot}解, 可选1..${st2})` + ((l.n===baseN) ? " 固定" : " 可拖动");
    const rm = document.createElement("button");
    rm.className = "rem"; rm.textContent = "✕";
    rm.onclick = ()=>{ layers.splice(idx,1); renderControls(); render(); };
    row.appendChild(sw); row.appendChild(sel);
    row.appendChild(document.createTextNode(" 第"));
    row.appendChild(k);
    row.appendChild(document.createTextNode(" 解 "));
    row.appendChild(st); row.appendChild(rm);
    layerList.appendChild(row);
  });
}

function addLayer(){
  const used = new Set(layers.map(l=>l.n));
  // pick smallest available even not yet used (fallback: first available)
  let pick = DATA.availableEven.find(n=>!used.has(n)) || DATA.availableEven[0];
  layers.push({n:pick, k:1, dx:0, dy:0, color:PALETTE[layers.length % PALETTE.length]});
  renderControls(); render();
}

document.getElementById("add").onclick = addLayer;
document.getElementById("reset").onclick = ()=>{
  layers.forEach(l=>{ l.dx=0; l.dy=0; });
  render();
};

const miss = DATA.missingEven || [];
document.getElementById("missing").textContent = miss.length
  ? `注意：本地缓存缺失偶数 n = ${miss.join(", ")}，无法选择（仅含已下载的 Flammenkamp 数据）。`
  : "";

// default demo: largest fixed + a small overlay
addLayer(); // n=72 (k=1)
layers[0].n = 72; layers[0].k = 1;
addLayer(); // another layer
layers[1].n = 12; layers[1].k = 1;
renderControls();
render();
</script>
</body>
</html>
"""


def main():
    print("Decoding cached even-n solutions ...")
    data = build()
    js = json.dumps(data, separators=(',', ':'))
    print(f"JSON payload size: {len(js)/1024/1024:.2f} MB")
    html = TEMPLATE.replace("/*__DATA__*/", js)
    out = os.path.join(HERE, "even_overlay.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out}  ({len(html)/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
