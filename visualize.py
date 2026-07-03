#!/usr/bin/env python3
"""
visualize.py — Generate visualizations of No-Three-In-Line solutions.

Produces a grid plot with:
  - Grid lines and intersection points
  - The selected 2n points highlighted
  - Color-coded distance rings (squared Euclidean distance from center)
  - Optional: circumcircle annotations for center-present solutions

Dependencies (install if needed):
    pip install matplotlib numpy

Usage:
    python visualize.py solutions/sols_n12.csv          # Show all solutions as slideshow
    python visualize.py solutions/sols_n12.csv --save    # Save frames to PNGs
    python visualize.py solutions/sols_n12.csv --index 0 # Show only solution #0
"""

import csv
import sys
import os
import math
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False
    print("matplotlib not installed. Install with: pip install matplotlib numpy")
    print("Falling back to SVG generation mode.")


def parse_solutions(csv_path):
    """Yield (n, pts_list) tuples from the solution CSV."""
    solutions = []
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
            solutions.append((n, pts))
    return solutions


def compute_distance_map(n):
    """Compute dx²+dy² distance from center for all grid points."""
    if n % 2 == 0:
        cx2, cy2 = n - 1, n - 1
    else:
        c = 2 * (n // 2)
        cx2, cy2 = c, c
    
    dist_map = {}
    for r in range(n):
        for c in range(n):
            dx = 2 * c - cx2
            dy = 2 * r - cy2
            d = dx * dx + dy * dy
            dist_map[(c, r)] = d
    return dist_map


def get_distinct_rings(dist_map):
    """Get sorted list of distinct squared distances."""
    return sorted(set(dist_map.values()))


def ring_color(d, all_rings, n_colors=20):
    """Assign a color to a distance ring using a perceptible colormap."""
    idx = all_rings.index(d) % n_colors
    # Use matplotlib tab20 colormap cycle
    colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
        '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5',
    ]
    return colors[idx % len(colors)]


def generate_svg(n, pts, output_path, dist_map=None):
    """
    Generate a standalone SVG visualization without matplotlib.
    Useful for including directly in README or documentation.
    """
    if dist_map is None:
        dist_map = compute_distance_map(n)
    
    all_rings = get_distinct_rings(dist_map)
    ring_colors_map = {d: ring_color(d, all_rings) for d in all_rings}

    # SVG dimensions
    margin = 40
    spacing = 30
    size = (n - 1) * spacing + 2 * margin
    dot_radius = 4

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size + 160} {size + 40}" width="100%" height="100%">')
    lines.append(f'  <rect width="100%" height="100%" fill="#ffffff"/>')
    
    # Title
    lines.append(f'  <text x="{size/2 + 40}" y="20" text-anchor="middle" font-family="monospace" font-size="14" fill="#333">')
    lines.append(f'    n={n} Missing-Center Solution — Distance Rings Colored')
    lines.append(f'  </text>')
    
    # Grid lines (light)
    lines.append(f'  <g stroke="#ddd" stroke-width="0.5">')
    for i in range(n):
        x = margin + i * spacing
        y = margin
        lines.append(f'    <line x1="{x}" y1="{margin}" x2="{x}" y2="{margin + (n-1)*spacing}"/>')
        lines.append(f'    <line x1="{margin}" y1="{x}" x2="{margin + (n-1)*spacing}" y2="{x}"/>')
    lines.append(f'  </g>')
    
    # Axis labels
    lines.append(f'  <g fill="#999" font-family="monospace" font-size="10">')
    for i in range(n):
        x = margin + i * spacing
        lines.append(f'    <text x="{x}" y="{margin + n*spacing + 15}" text-anchor="middle">{i}</text>')
        lines.append(f'    <text x="{margin - 15}" y="{x + 3}" text-anchor="end">{i}</text>')
    lines.append(f'  </g>')
    
    # Draw all grid points (faded) with distance ring coloring
    lines.append(f'  <g fill-opacity="0.15" stroke="none">')
    for r in range(n):
        for c in range(n):
            d = dist_map[(c, r)]
            color = ring_colors_map[d]
            cx = margin + c * spacing
            cy = margin + r * spacing
            lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{dot_radius}" fill="{color}"/>')
    lines.append(f'  </g>')
    
    # Draw solution points (bold) with ring coloring
    lines.append(f'  <g stroke="#333" stroke-width="1.5">')
    for px, py in pts:
        d = dist_map[(px, py)]
        color = ring_colors_map[d]
        cx = margin + px * spacing
        cy = margin + py * spacing
        lines.append(f'    <circle cx="{cx}" cy="{cy}" r="{dot_radius + 2}" fill="{color}" stroke="#333" stroke-width="1.5"/>')
    lines.append(f'  </g>')
    
    # Legend for distance rings used by solution
    used_distances = sorted(set(dist_map[p] for p in pts))
    legend_x = size + 70
    legend_y = margin
    
    lines.append(f'  <text x="{legend_x}" y="{legend_y - 5}" font-family="monospace" font-size="11" fill="#333">Distance Rings</text>')
    for i, d in enumerate(used_distances):
        y = legend_y + 15 + i * 16
        color = ring_colors_map[d]
        lines.append(f'  <rect x="{legend_x}" y="{y - 5}" width="10" height="10" fill="{color}" stroke="#999" stroke-width="0.5"/>')
        lines.append(f'  <text x="{legend_x + 18}" y="{y + 1}" font-family="monospace" font-size="9" fill="#666">d={d}</text>')
    
    # Center marker
    center_x = margin + (n - 1) * spacing / 2
    center_y = center_x
    lines.append(f'  <g stroke="red" stroke-width="1" stroke-dasharray="3,3">')
    lines.append(f'    <circle cx="{center_x}" cy="{center_y}" r="{3*dot_radius}" fill="none"/>')
    lines.append(f'    <line x1="{center_x - 6}" y1="{center_y}" x2="{center_x + 6}" y2="{center_y}"/>')
    lines.append(f'    <line x1="{center_x}" y1="{center_y - 6}" x2="{center_x}" y2="{center_y + 6}"/>')
    lines.append(f'  </g>')
    lines.append(f'  <text x="{center_x + 12}" y="{center_y + 4}" font-family="monospace" font-size="9" fill="red">center</text>')

    lines.append('</svg>')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return output_path


def plot_matplotlib(n, pts, dist_map, output_path=None):
    """Plot using matplotlib with distance ring coloring."""
    if not HAVE_MPL:
        print("matplotlib not available, skipping.")
        return

    all_rings = get_distinct_rings(dist_map)
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    
    # Draw grid
    for i in range(n + 1):
        ax.axhline(i - 0.5, color='#ddd', linewidth=0.5)
        ax.axvline(i - 0.5, color='#ddd', linewidth=0.5)
    
    # Draw all grid points as tiny dots
    ring_used_set = set(dist_map[p] for p in pts)
    for r in range(n):
        for c in range(n):
            d = dist_map[(c, r)]
            color = ring_color(d, all_rings)
            alpha = 0.3 if d in ring_used_set else 0.08
            ax.plot(c, r, 'o', color=color, markersize=4, alpha=alpha, 
                    markeredgecolor='none')
    
    # Draw solution points
    for px, py in pts:
        d = dist_map[(px, py)]
        color = ring_color(d, all_rings)
        ax.plot(px, py, 'o', color=color, markersize=10, 
                markeredgecolor='#333', markeredgewidth=1.5, zorder=5)
    
    # Center marker
    center = (n - 1) / 2.0
    ax.plot(center, center, 'x', color='red', markersize=12, mew=2, zorder=6)
    circle = plt.Circle((center, center), 0.4, fill=False, color='red', 
                        linestyle='--', linewidth=1, zorder=6)
    ax.add_patch(circle)
    
    # Legend (show rings used by solution)
    used_distances = sorted(dist_map[p] for p in pts)
    from matplotlib.patches import Patch
    legend_elements = []
    for d in used_distances:
        color = ring_color(d, all_rings)
        legend_elements.append(Patch(facecolor=color, label=f'd²={d}'))
    # Put legend outside
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5),
              title='Distance Rings (used)', fontsize=8, title_fontsize=9)
    
    ax.set_xlim(-1, n)
    ax.set_ylim(-1, n)
    ax.set_aspect('equal')
    ax.set_title(f'n={n} Missing-Center Solution — Distance Ring View', fontsize=13)
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')
    ax.invert_yaxis()  # Row 0 at top (matching grid convention)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    else:
        plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <csv_file> [options]")
        print("Options:")
        print("  --index N     Show only solution at index N")
        print("  --save        Save PNGs instead of showing")
        print("  --svg         Generate SVG files (works without matplotlib)")
        print("  --outdir DIR  Output directory (default: ./viz_output/)")
        print("\nExamples:")
        print("  python visualize.py solutions/sols_n12.csv --index 0 --svg")
        print("  python visualize.py solutions/sols_n12.csv --save")
        sys.exit(1)

    csv_path = sys.argv[1]
    show_index = None
    save_mode = '--save' in sys.argv
    svg_mode = '--svg' in sys.argv
    
    outdir = './viz_output'
    for i, arg in enumerate(sys.argv):
        if arg == '--outdir' and i + 1 < len(sys.argv):
            outdir = sys.argv[i + 1]
    
    for i, arg in enumerate(sys.argv):
        if arg == '--index' and i + 1 < len(sys.argv):
            show_index = int(sys.argv[i + 1])

    solutions = parse_solutions(csv_path)
    
    if show_index is not None:
        solutions = [solutions[show_index]]
    
    os.makedirs(outdir, exist_ok=True)

    for idx, (n, pts) in enumerate(solutions):
        abs_idx = show_index if show_index is not None else idx
        
        # Validate
        if len(pts) != 2 * n:
            print(f"  ⚠️  Solution #{abs_idx}: expected {2*n} points, got {len(pts)}")
            continue
        
        dist_map = compute_distance_map(n)
        
        if svg_mode or not HAVE_MPL:
            outpath = os.path.join(outdir, f'solution_{n}_{abs_idx}.svg')
            generate_svg(n, pts, outpath, dist_map)
            print(f"  SVG: {outpath}")
        else:
            if save_mode:
                outpath = os.path.join(outdir, f'solution_{n}_{abs_idx}.png')
                plot_matplotlib(n, pts, dist_map, outpath)
            else:
                print(f"\n  Solution #{abs_idx} (n={n}):")
                plot_matplotlib(n, pts, dist_map)

    print(f"\nDone. Output in: {os.path.abspath(outdir)}")


if __name__ == '__main__':
    main()
