/*
 * Direction A: C4 Orbit Selection — Cycle Decomposition Explorer
 *
 * For even n = 2m, find which cycle decompositions and vertex arrangements
 * yield collinear-free C4 orbit selections.
 *
 * A 2-regular graph on m vertices decomposes into cycles.
 * Each edge (i,j) represents orbit O(i,j).
 * The m edges must form a cycle decomposition where each vertex degree = 2.
 *
 * This program enumerates all possible cycle decompositions for small m,
 * and checks which vertex arrangements avoid collinearity.
 */
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <set>
#include <map>
#include <cmath>
using namespace std;

int N, M;
int found_total = 0;
int found_valid = 0;

struct Point { int x, y; };
bool operator<(const Point& a, const Point& b) {
    if (a.x != b.x) return a.x < b.x;
    return a.y < b.y;
}
bool operator==(const Point& a, const Point& b) {
    return a.x == b.x && a.y == b.y;
}

// Generate the 4 points of C4 orbit O(i,j) for n=2m
vector<Point> orbit_points(int i, int j) {
    int n = N;
    return {{i, j}, {n-1-j, i}, {n-1-i, n-1-j}, {j, n-1-i}};
}

// Check collinearity for all triples
bool has_collinear(const vector<Point>& pts) {
    for (size_t a = 0; a < pts.size(); a++)
        for (size_t b = a+1; b < pts.size(); b++)
            for (size_t c = b+1; c < pts.size(); c++) {
                int dx = pts[b].x - pts[a].x;
                int dy = pts[b].y - pts[a].y;
                if (dx * (pts[c].y - pts[a].y) == dy * (pts[c].x - pts[a].x))
                    return true;
            }
    return false;
}

// Check row and column counts (2 per row, 2 per column)
bool check_row_col(const vector<Point>& pts) {
    vector<int> row_cnt(N, 0), col_cnt(N, 0);
    for (auto& p : pts) {
        row_cnt[p.x]++;
        col_cnt[p.y]++;
    }
    for (int c : row_cnt) if (c != 2) return false;
    for (int c : col_cnt) if (c != 2) return false;
    return true;
}

// Check a set of orbits (as vector of (i,j) pairs)
bool check_orbits(const vector<pair<int,int>>& orbits) {
    vector<Point> pts;
    for (auto& [i, j] : orbits) {
        auto p = orbit_points(i, j);
        pts.insert(pts.end(), p.begin(), p.end());
    }
    
    // Check row/col coverage
    if (!check_row_col(pts)) return false;
    
    // Check collinearity
    if (has_collinear(pts)) return false;
    
    return true;
}

// Generate a cycle from a vertex ordering
// vertices[0]-vertices[1], vertices[1]-vertices[2], ..., vertices[last]-vertices[0]
// Note: orbit(i,j) != orbit(j,i), so direction matters!
vector<pair<int,int>> cycle_from_order(const vector<int>& vertices) {
    vector<pair<int,int>> edges;
    for (size_t i = 0; i < vertices.size(); i++) {
        int v1 = vertices[i];
        int v2 = vertices[(i+1) % vertices.size()];
        // DO NOT sort! O(v1,v2) != O(v2,v1)
        edges.push_back({v1, v2});
    }
    return edges;
}

// Check all direction assignments for a given cycle ordering
// For each edge in the cycle, we can choose either O(v1,v2) or O(v2,v1)
bool check_with_directions(const vector<int>& vertices, 
                           const vector<int>& cycle_type,
                           vector<pair<int,int>>& output_orbits) {
    // Generate edges
    vector<pair<int,int>> edge_pairs;  // (v1, v2) in cycle direction
    int pos = 0;
    for (int len : cycle_type) {
        for (int i = 0; i < len; i++) {
            int v1 = vertices[pos + i];
            int v2 = vertices[pos + (i+1) % len];
            edge_pairs.push_back({v1, v2});
        }
        pos += len;
    }
    
    int m = edge_pairs.size();
    // Try all 2^m direction assignments
    for (int mask = 0; mask < (1 << m); mask++) {
        vector<pair<int,int>> orbits;
        for (int i = 0; i < m; i++) {
            auto [v1, v2] = edge_pairs[i];
            if (mask & (1 << i))
                orbits.push_back({v2, v1});  // reversed direction
            else
                orbits.push_back({v1, v2});  // cycle direction
        }
        
        if (check_orbits(orbits)) {
            output_orbits = orbits;
            return true;
        }
    }
    return false;
}

// Test all vertex permutations for a given cycle type
// For each permutation, try all 2^m direction assignments
void test_cycle_type(const vector<int>& cycle_type) {
    vector<int> vertices(M);
    iota(vertices.begin(), vertices.end(), 0);
    
    do {
        vector<pair<int,int>> output_orbits;
        if (check_with_directions(vertices, cycle_type, output_orbits)) {
            found_valid++;
            if (found_valid <= 5) {
                cout << "  VALID: cycle type = [";
                for (size_t i = 0; i < cycle_type.size(); i++) {
                    if (i) cout << ",";
                    cout << cycle_type[i];
                }
                cout << "], order = [";
                for (int v : vertices) cout << v << ",";
                cout << "]" << endl;
                
                cout << "    Orbits: ";
                for (auto& [i,j] : output_orbits) cout << "(" << i << "," << j << ")";
                cout << endl;
            }
        }
        found_total++;
        
    } while (next_permutation(vertices.begin(), vertices.end()));
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <m> [max_cycle_types]" << endl;
        return 1;
    }
    
    M = atoi(argv[1]);
    N = 2 * M;
    int max_types = (argc > 2) ? atoi(argv[2]) : 1000;
    
    cout << "=== C4 Orbit Selection: Cycle Decomposition Explorer ===" << endl;
    cout << "n = " << N << " (m = " << M << ")" << endl;
    long long fact = 1;
    for (int i = 2; i <= M; i++) fact *= i;
    cout << "Testing up to " << M << "! = " << fact << " permutations, 2^" << M << " direction variants each" << endl;
    cout << "max cycle types to test: " << max_types << endl;
    cout << endl;
    
    auto start = chrono::steady_clock::now();
    
    // Generate all cycle decompositions (integer partitions of M)
    vector<vector<int>> cycle_types;
    cycle_types.push_back({M});
    for (int a = 1; a <= M/2; a++)
        cycle_types.push_back({a, M-a});
    for (int a = 1; a <= M-2; a++)
        for (int b = 1; b <= M-a-1; b++)
            cycle_types.push_back({a, b, M-a-b});
    for (int a = 1; a <= M-3; a++)
        for (int b = 1; b <= M-a-2; b++)
            for (int c = 1; c <= M-a-b-1; c++)
                cycle_types.push_back({a, b, c, M-a-b-c});
    
    int tested = 0;
    for (auto& ct : cycle_types) {
        if (tested >= max_types) break;
        tested++;
        
        cout << "\n--- Cycle type [";
        for (size_t i = 0; i < ct.size(); i++) {
            if (i) cout << ",";
            cout << ct[i];
        }
        cout << "] ---" << endl;
        
        auto t0 = chrono::steady_clock::now();
        found_total = 0;
        found_valid = 0;
        
        test_cycle_type(ct);
        
        auto t1 = chrono::steady_clock::now();
        double secs = chrono::duration<double>(t1-t0).count();
        
        cout << "  " << found_total << " orderings tested, "
             << found_valid << " valid, "
             << secs << "s" << endl;
    }
    
    auto end = chrono::steady_clock::now();
    cout << "\nTotal time: " << chrono::duration<double>(end-start).count() << "s" << endl;
}
