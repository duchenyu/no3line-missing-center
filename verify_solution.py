#!/usr/bin/env python3
"""
verify_solution.py — Independent solution verifier for No-Three-In-Line.

Reads a solution CSV (format: n, r0c1, r0c2, r1c1, r1c2, ...)
and checks two properties:
  1. No three points are collinear.
  2. The grid center is (or is not) a circumcenter of some triple.

Usage:
    python verify_solution.py <csv_file> [--verbose]

Examples:
    python verify_solution.py solutions/sols_n12.csv
    python verify_solution.py solutions/sols_n12.csv --verbose
"""

import csv
import sys
import math
from collections import Counter

def verify_no_three_in_line(pts):
    """
    Check that no three of the given (x,y) integer points are collinear.
    Uses the determinant (area) method: |x1(y2-y3)+x2(y3-y3)+x3(y1-y2)| != 0
    O(k^3) worst-case, but k = 2n ≤ 46 for our data, so it's fine.
    """
    k = len(pts)
    for i in range(k):
        x1, y1 = pts[i]
        for j in range(i + 1, k):
            x2, y2 = pts[j]
            for m in range(j + 1, k):
                x3, y3 = pts[m]
                # Cross product = (x2-x1)*(y3-y1) - (x3-x1)*(y2-y1)
                # If zero, points are collinear
                area2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
                if area2 == 0:
                    return False, (i, j, m, (x1, y1), (x2, y2), (x3, y3))
    return True, None


def compute_center_times2(n):
    """
    Returns (cx_times2, cy_times2) where the grid center is at
    (cx_times2/2, cy_times2/2).

    For even n: center is at ((n-1)/2, (n-1)/2) = half-integer.
    For odd  n: center is at (n//2, n//2) = integer.
    """
    if n % 2 == 0:
        return n - 1, n - 1  # center = (n-1)/2, scaled by 2
    else:
        c = 2 * (n // 2)
        return c, c  # center = n//2, scaled by 2


def check_missing_center(pts, cx2, cy2):
    """
    Check if the grid center is a circumcenter of some triple.
    
    The center is a circumcenter iff three or more points share the same
    squared Euclidean distance from the center (they lie on the same circle).
    
    Distance metric (scaled for integer arithmetic):
        d = (2*x - cx2)^2 + (2*y - cy2)^2
    """
    dist_counts = Counter()
    for x, y in pts:
        dx = 2 * x - cx2
        dy = 2 * y - cy2
        d = dx * dx + dy * dy
        dist_counts[d] += 1
    
    max_share = max(dist_counts.values())
    has_center = max_share >= 3
    
    return has_center, max_share, dict(dist_counts)


def parse_solution_csv(csv_path):
    """Parse a solution CSV file, yielding individual solutions."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = int(row['n'])
            pts = []
            for r in range(n):
                c1 = int(row[f'r{r}c1'])
                c2 = int(row[f'r{r}c2'])
                pts.append((c1, r))
                pts.append((c2, r))
            yield n, pts


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_solution.py <csv_file> [--verbose]")
        sys.exit(1)

    csv_path = sys.argv[1]
    verbose = '--verbose' in sys.argv

    passed = 0
    failed = 0
    center_count = 0
    missing_count = 0
    total_pairs_seen = 0

    print(f"Verifying solutions from: {csv_path}")
    print("=" * 60)

    for n, pts in parse_solution_csv(csv_path):
        total_pairs_seen += 1

        # Check 1: No three collinear
        collinear_ok, bad_triple = verify_no_three_in_line(pts)
        if not collinear_ok:
            print(f"  ❌ FAIL (collinear): solution #{total_pairs_seen}")
            _, _, _, p1, p2, p3 = bad_triple
            print(f"     Points: {p1}, {p2}, {p3}")
            failed += 1
            continue

        # Check 2: Center presence
        cx2, cy2 = compute_center_times2(n)
        has_center, max_share, dist_dict = check_missing_center(pts, cx2, cy2)

        if has_center:
            center_count += 1
            if verbose:
                print(f"  ✅ Solution #{total_pairs_seen}: No collinear, HAS center (max ring={max_share})")
        else:
            missing_count += 1
            if verbose:
                print(f"  ✅ Solution #{total_pairs_seen}: No collinear, MISSING center (max ring={max_share})")

        passed += 1

    # Summary
    print("=" * 60)
    print(f"\nTotal solutions verified : {passed + failed}")
    print(f"  Passed (valid)         : {passed}")
    print(f"  Failed (collinear!)    : {failed}")
    print(f"  With center            : {center_count}")
    print(f"  Missing center         : {missing_count}")

    if failed > 0:
        print("\n⚠️  WARNING: Some solutions contain collinear triples!")
        sys.exit(1)
    else:
        print("\n✅ All solutions valid — no collinear triples found.")
        print(f"   Center status: {center_count} with center, {missing_count} missing center.")


if __name__ == '__main__':
    main()
