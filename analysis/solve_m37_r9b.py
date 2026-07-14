"""
solve_m37_r9b.py  --  R9b 2-regular reformulation + fast per-line encoder for
rot4 (C4) NTIL, optimized for m=37 (n=74).

Two independent improvements over the original cpsat_symmetric_ntil.py:

(A) FAST MODEL BUILD.  The original generate_constraints loops
        directions -> points -> reps
    = O(#dirs * n^2 * #reps) ~ 10^10 ops at m=37  ->  it never even reaches
    the solver (0-byte log).  Here we loop
        reps -> lifted points -> directions
    = O(#reps * |G| * #dirs) ~ 3e7 ops  ->  model ready in seconds.

(B) R9b 2-FACTOR STRUCTURE (Th-44).  A rot4 NTIL's m fundamental-quadrant cells
    form a 2-regular graph on the m odd coordinate values: every odd value
    a in {1,3,...,2m-1} appears in EXACTLY 2 of the m cells (as an a-coord or a
    b-coord).  In the top-left fundamental quadrant (cell (x,y), x,y in 0..m-1)
    this is the clean linear family
            rowSum[i] + colSum[i] == 2     for each i in 0..m-1
    where rowSum[i] = sum_x sel[i][x], colSum[i] = sum_y sel[y][i].
    Verified on all known rot4 solutions (m=5..20, 0 violations).  Adding it
    does NOT change the solution set (valid NTIL are 2-regular by Th-44) but
    gives CP-SAT a tight global structure to propagate on.

Exactness: the per-line weighted at-most-2 family is, by definition, exactly
"no 3 lifted points collinear" = rot4 NTIL (R8/SIRH Part III).  The 2-factor is
an extra necessary condition layered on top.

Usage:
  python solve_m37_r9b.py --validate            # small-m sound+reach sweep, 2F on/off
  python solve_m37_r9b.py --m 10                # smoke test (should find a solution)
  python solve_m37_r9b.py --m 37 --timelimit 7200 --workers 8 \
        --checkpoint results/m37_r9b_ckpt.json --resume results/m37_r9b_ckpt.json
"""
import os, sys, time, json, math, argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from quadratic_sidon_completeness import c4, brute_collinear, load_known

try:
    from ortools.sat.python import cp_model
    HAVE_ORTOOLS = True
except Exception:
    HAVE_ORTOOLS = False

NONE_G = None


def cell_xy(a, b, m):
    return (m - (a + 1) // 2, m - (b + 1) // 2)


def orbit_c4(cell, n):
    return [c4(cell, r, n) for r in range(4)]


def reduced_dirs(n):
    dirs = set()
    for dx in range(-(n - 1), n):
        for dy in range(0, n):
            if dx == 0 and dy == 0:
                continue
            g = math.gcd(abs(dx), dy) or 1
            rdx, rdy = dx // g, dy // g        # local copies: never mutate loop vars
            if rdx < 0 or (rdx == 0 and rdy < 0):
                rdx, rdy = -rdx, -rdy
            dirs.add((rdx, rdy))
    return dirs


def generate_constraints(m, use_2factor=True):
    """Top-left fundamental quadrant reps; fast per-line weighted at-most-2.

    Returns (reps, line_cons, twofactor_cons).
      reps        : list of (x,y), x,y in 0..m-1  (length m^2)
      line_cons   : list of {rep_idx: weight} with total weight > 2
      twofactor   : list of (row_index,) meaning rowSum[i]+colSum[i]==2
    """
    n = 2 * m
    reps = [(x, y) for x in range(m) for y in range(m)]
    ri = {c: i for i, c in enumerate(reps)}
    orbits = [orbit_c4(c, n) for c in reps]
    D = reduced_dirs(n)

    # reps -> lifted points -> directions
    line_w = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # (dx,dy)->key->{rep:w}
    for i, (x, y) in enumerate(reps):
        for (X, Y) in orbits[i]:
            for (dx, dy) in D:
                perp = (-dy, dx)
                key = perp[0] * X + perp[1] * Y
                line_w[(dx, dy)][key][i] += 1

    line_cons = []
    for d, lines in line_w.items():
        for key, pos_w in lines.items():
            if sum(pos_w.values()) > 2:
                line_cons.append(dict(pos_w))

    twofactor = list(range(m)) if use_2factor else []
    return reps, line_cons, twofactor


class _SolCb(cp_model.CpSolverSolutionCallback):
    """Live-checkpoint every feasible solution found (enables warm resume)."""
    def __init__(self, sel, m, ckpt):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.sel = sel
        self.m = m
        self.ckpt = ckpt
        self.n = 0

    def OnSolutionCallback(self):
        cells = [(i, j) for i in range(self.m) for j in range(self.m)
                 if self.Value(self.sel[i][j]) == 1]
        _write_ckpt(self.ckpt, cells)
        self.n += 1


def solve_ortools(reps, line_cons, twofactor, timelimit, workers=8,
                  mem_mb=0, checkpoint=None, resume=None, verbose=False):
    m = int(round(math.sqrt(len(reps))))   # reps = m^2
    model = cp_model.CpModel()
    sel = [[model.NewBoolVar(f"s{i}_{j}") for j in range(m)] for i in range(m)]

    # per-line weighted at-most-2  (progress prints so a hang is localizable)
    t = time.time()
    print(f"[build] adding {len(line_cons)} per-line constraints...", flush=True)
    for idx, d in enumerate(line_cons):
        terms = [w * sel[reps[k][0]][reps[k][1]] for k, w in d.items()]
        model.Add(sum(terms) <= 2)
        if (idx + 1) % 200000 == 0:
            print(f"[build] per-line {idx+1}/{len(line_cons)} "
                  f"({time.time()-t:.0f}s)", flush=True)

    # R9b 2-factor: rowSum[i] + colSum[i] == 2  (subsumes card == m)
    for i in twofactor:
        model.Add(sum(sel[i]) + sum(sel[r][i] for r in range(m)) == 2)
    print(f"[build] model complete ({time.time()-t:.0f}s)", flush=True)

    if resume and os.path.exists(resume):
        try:
            with open(resume) as f:
                data = json.load(f)
            for (x, y) in data.get("cells", []):
                if 0 <= x < m and 0 <= y < m:
                    model.AddHint(sel[x][y], 1)
            if verbose:
                print(f"[resume] hinted {len(data.get('cells', []))} cells",
                      file=sys.stderr)
        except Exception as e:
            if verbose:
                print(f"[resume] warn: {e}", file=sys.stderr)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timelimit
    # CRITICAL: max_time_in_seconds does NOT bound the presolve phase.  On a
    # ~1.26M-constraint model, unbounded presolve can wedge for hours and never
    # reach the timelimited search.  Cap presolve passes so Solve() is guaranteed
    # to return within (presolve + timelimit).
    solver.parameters.max_presolve_iterations = 3
    solver.parameters.num_search_workers = workers
    if mem_mb and mem_mb > 0:
        solver.parameters.max_memory_in_mb = mem_mb
    if verbose:
        solver.parameters.log_search_progress = True

    cb = _SolCb(sel, m, checkpoint) if checkpoint else None
    print(f"[solve] start timelimit={timelimit}s workers={workers} "
          f"live_ckpt={bool(cb)}", flush=True)
    t0 = time.time()
    st = solver.Solve(model, cb) if cb else solver.Solve(model)
    status = solver.StatusName(st)
    cells = []
    if status in ("FEASIBLE", "OPTIMAL"):
        for i in range(m):
            for j in range(m):
                if solver.Value(sel[i][j]) == 1:
                    cells.append((i, j))
    if cells and checkpoint:
        _write_ckpt(checkpoint, cells)
    if cb:
        print(f"[solve] {cb.n} solutions live-checkpointed", flush=True)
    return status, cells, time.time() - t0


def _write_ckpt(path, cells):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"cells": cells, "ts": time.time()}, f)
    os.replace(tmp, path)


def verify_cells(cells, m):
    """cells = list of (x,y) in top-left quadrant.  Lift via C4, brute no-3-collinear."""
    pairs = [(2 * (m - x) - 1, 2 * (m - y) - 1) for (x, y) in cells]
    return (not brute_collinear(pairs, m)), len(cells)


def extract_topleft(pairs, m):
    """Given known-solution pairs (odd a,b), return the unique top-left cell per orbit."""
    cells = []
    seen = set()
    for (a, b) in pairs:
        c = cell_xy(a, b, m)
        # c is in top-left quadrant; its C4 orbit's top-left rep is just c
        # (proven: exactly one orbit point lies in x<m,y<m)
        cells.append(c)
    return cells


def check_2factor(cells, m):
    rs = [0] * m
    cs = [0] * m
    for (x, y) in cells:
        rs[x] += 1
        cs[y] += 1
    ok = all(rs[i] + cs[i] == 2 for i in range(m))
    return ok, list(rs[i] + cs[i] for i in range(m))


def cycle_decomp(cells, m):
    """Decompose the R9b 2-factor into its cycle signature.

    The constraint rowSum[i]+colSum[i]==2 means: for each index i (0..m-1),
    (cells in row i) + (cells in col i) == 2.  So treat the m indices as
    vertices of ONE graph, where a selected cell (x,y) is the edge x--y
    (directed x->y).  Each vertex then has total undirected degree 2, so the
    support is a 2-regular graph on m vertices = disjoint union of cycles
    (length >= 2; a loop (i,i) is a length-1 cycle, two opposite cells
    (i,j),(j,i) form a length-2 cycle).  Sum of cycle lengths == m.

    Returns the sorted list of cycle lengths -- the combinatorial fingerprint of
    a fundamental-quadrant selection, the natural object for structural theory.
    """
    loops = set()
    adj = {i: [] for i in range(m)}
    for (x, y) in cells:
        if x == y:
            loops.add(x)                 # loop = length-1 cycle (degree 2 from itself)
        else:
            adj[x].append(y)
            adj[y].append(x)
    cycles = [1] * len(loops)
    visited = set(loops)
    for start in range(m):
        if start in visited or not adj[start]:
            continue
        cyc = [start]
        prev = -1
        cur = start
        while True:
            nxt = None
            for w in adj[cur]:
                if w != prev:
                    nxt = w
                    break
            if nxt is None:
                break
            if nxt == start:
                break                       # cycle closed; do NOT re-append start
            cyc.append(nxt)
            prev = cur
            cur = nxt
        for v in cyc:
            visited.add(v)
        cycles.append(len(cyc))
    return sorted(cycles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, default=10)
    ap.add_argument("--timelimit", type=float, default=30.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--no-2factor", action="store_true",
                    help="disable R9b 2-factor constraint")
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--resume", default="")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    use_2f = not args.no_2factor

    if args.validate:
        print("== R9b solver: soundness + reachability sweep ==")
        for m in [5, 6, 7, 8, 9, 10]:
            reps, lc, tf = generate_constraints(m, use_2f)
            # (1) known solutions admitted + 2-factor satisfied
            sols = load_known(m, cap=10)
            admit = 0
            twf_ok = 0
            for pairs in sols:
                cells = extract_topleft(pairs, m)
                ok, _ = check_2factor(cells, m)
                twf_ok += ok
                # per-line check on these cells
                bad = 0
                for d in lc:
                    if sum(1 for k in d if (reps[k][0], reps[k][1]) in set(cells)) > 2:
                        bad += 1
                admit += (bad == 0)
            # (2) CP-SAT finds a solution and it verifies
            status, cells, t = solve_ortools(
                reps, lc, tf, 30.0, workers=4, verbose=False)
            vf = False
            if cells:
                vf, _ = verify_cells(cells, m)
            print(f"  m={m}: reps={len(reps)} line_cons={len(lc)} "
                  f"2F_on={use_2f} known_admitted={admit}/{len(sols)} "
                  f"2F_ok_on_known={twf_ok}/{len(sols)} "
                  f"solve={status} found={len(cells)} verify={vf} [{t:.1f}s]")
        return

    m = args.m
    t0 = time.time()
    reps, lc, tf = generate_constraints(m, use_2f)
    tgen = time.time() - t0
    print(f"[gen] m={m}: reps={len(reps)} line_cons={len(lc)} "
          f"2F_on={use_2f} build={tgen:.1f}s")
    if args.verbose:
        for d in lc[:3]:
            print("   sample line cons:", d)
    ckpt = args.checkpoint or None
    resume = args.resume or None
    status, cells, tsolve = solve_ortools(
        reps, lc, tf, args.timelimit, workers=args.workers,
        checkpoint=ckpt, resume=resume, verbose=args.verbose)
    print(f"[solve] status={status} found={len(cells)} solve_time={tsolve:.1f}s")
    if cells:
        vf, nc = verify_cells(cells, m)
        print(f"[verify] no-3-collinear={vf} (n={2*m}, points={4*len(cells)})")
        print("[cells]", cells)
        if ckpt:
            print(f"[checkpoint] -> {ckpt}")
    if ckpt and status in ("OPTIMAL", "FEASIBLE", "INFEASIBLE"):
        with open(ckpt + ".done", "w") as f:
            f.write(f"status={status}\nfound={len(cells)}\n")
        print(f"[done] {ckpt}.done written")


if __name__ == "__main__":
    main()
