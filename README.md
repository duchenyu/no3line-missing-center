# No-Three-In-Line: Missing Center Analysis

An optimized exhaustive search for **missing-center** solutions to the No-Three-In-Line problem.

## The Problem

Place **2n points** on an **n×n grid** such that no three are collinear.

**New perspective**: For each solution, check whether the grid center is a circumcenter of some triple of points. A "missing-center" solution has **no** triple whose circumcircle is centered at the grid center.

### Key Finding: Previous heuristic patterns were wrong

Earlier conjectures based on small-n patterns (prime classification 4k+1 vs 4k+3, "even n always has center") are **falsified** by real computation at n≥12:

| n | Type | Total Solutions | With Center | Missing Center | Verified |
|---|------|----------------|-------------|---------------|----------|
| 2 | Even | 1 | 1 | 0 | ✅ |
| 4 | Even | 11 | 11 | 0 | ✅ |
| 6 | Even | 50 | 50 | 0 | ✅ |
| 8 | Even | 380 | 380 | 0 | ✅ |
| 10 | Even | 1,135 | 1,135 | 0 | ✅ |
| 12 | Even | 4,348 | 4,296 | **52** | ✅ *First even n with missing-center!* |
| 3 | Odd P | 2 | 2 | 0 | ✅ |
| 5 | Odd P (4k+1) | 32 | 28 | 4 | ✅ |
| 7 | Odd P (4k+3) | 132 | 128 | 4 | ✅ |
| 9 | Odd C | 368 | 360 | 8 | ✅ |
| 11 | Odd P (4k+3) | 1,120 | 1,084 | 36 | ✅ |
| 13 | Odd P (4k+1) | — | — | **292** | ✅ *Mode 1 only* |

**Key observations**:
- n=12 is the first even n with missing-center solutions (52)
- Missing counts grow super-exponentially: 4 → 4 → 8 → 36 → 52 → 292
- The earlier "4k+1 vs 4k+3" prime classification does NOT hold (n=13 = 4k+1 has 292 missing, far more than n=11 = 4k+3's 36)

## Algorithm: Forbid Accumulator (v2)

The key optimization turns the collinearity check from **O(k²) to O(1)** per placement.

```
For each row k, maintain forbid_accum[k] = bitmask of columns blocked
by all existing cross-row pairs. Check is O(1): just test the bit.
```

**Speedup**: n=11 mode 0 went from 9.2 minutes → 8.5 seconds (**65×**).

Additional optimizations:
- ✅ Precomputed collinearity accumulation (forbid_accum)
- ✅ Diagonal pre-check (x+y and x-y+N-1 occupancy)
- ✅ Distance ring pruning (mode 1: only count missing-center solutions)
- ✅ Mirror symmetry pruning (search space halved)
- ✅ Multi-threaded (splits by first-row column pairs)
- ✅ Statically linked binary (zero DLL dependencies on Windows)

## Usage

### Build

**Linux**:
```bash
make
```

**Windows (MinGW)**:
```batch
compile.bat
```

**Windows (MSVC)**:
The batch file auto-detects MSVC if MinGW is not found.

### Run

```bash
# Mode 0: Full search (count all solutions + missing-center)
./no3line <n> 0 <threads>

# Mode 1: Missing-center only (distance pruning, recommended for n≥12)
./no3line <n> 1 <threads>

# Examples
./no3line 12 1 16    # n=12 missing-center only, 16 threads
./no3line 15 1 16    # n=15 (needs cloud-grade hardware)
```

### Batch run

**Linux**: `./run_cloud.sh [mode] [threads] ["n1 n2 n3 ..."]`
**Windows**: Edit `run.bat` or run `run.bat`

## Repository Structure

```
├── no3line.cpp          # C++ source (v2 forbid_accum)
├── Makefile             # Linux build
├── compile.bat          # Windows build
├── run.bat              # Windows batch runner
├── run_cloud.sh         # Linux batch runner (16-thread cloud preset)
├── README.md            # This file
├── results/             # Computed result CSVs
│   ├── result_n11_mode0.csv
│   ├── result_n12_mode0.csv
│   ├── result_n13_mode1.csv
│   └── ...
├── solutions/           # Dumped individual solutions
│   └── sols_n12.csv     # All 28 (base) missing-center solutions for n=12
└── analysis/
    └── analyze.py       # Python analysis script for dumped solutions
```

## Results Data

Each CSV row: `n,total_solutions,with_center,missing_center,time_seconds,mode`

- Mode 0: total includes all solutions, with_center = total - missing
- Mode 1: only missing_center is counted (with distance pruning)

## Future Research Directions

### Direction 1: Constructive Missing-Center Solutions

Prove that missing-center solutions exist for all sufficiently large n by **explicit construction**.

**Approach**: The column pairing graph (each column appears exactly twice) decomposes into cycles. Design cycle structures that avoid distance ring collisions.

**Key clue**: d=34 and d=82 rings are used in **every** missing-center solution for n=12 — suggesting they may be "universal" building blocks.

### Direction 2: Circumcircle Spectrum

Map **every** grid point's role as a circumcenter across all solutions. The "circumcircle spectrum" of a solution characterizes which grid points serve as circumcenters for some triple.

### Direction 3: The Even n Threshold

Why n=12 is the first even n with missing-center solutions, while n=6,8,10 have none. Related to the number of distinct distance rings crossing a threshold relative to 2n points.

### Direction 4: Relaxing the Row Constraint

What if we relax the "exactly 2 per row" constraint (imposed by our search algorithm) and allow 1, 2, or 3 points per row? Does the missing-center threshold change?

## License

MIT
