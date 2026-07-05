/*
 * Direction A: C4 Cycle Explorer — Extended version
 * 
 * For larger m (7+), we only test promising cycle types:
 * - Full m-cycle: (m)
 * - One loop + one cycle: (1, m-1), (2, m-2), ..., (floor(m/2), m-floor(m/2))  
 * - Two cycles of equal-ish length
 * - Three cycles
 *
 * To handle m! growth, we fix vertex 0 at the start of the first cycle.
 */
#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <set>
#include <map>
#include <cstring>
using namespace std;

int N, M;

struct Point { int x, y; };

// Generate the 4 points of C4 orbit O(i,j) for n=2m
vector<Point> orbit_points(int i, int j) {
    int n = N;
    return {{i, j}, {n-1-j, i}, {n-1-i, n-1-j}, {j, n-1-i}};
}

// Check collinearity fast
bool has_collinear(const vector<Point>& pts) {
    int npts = pts.size();
    for (int a = 0; a < npts; a++)
        for (int b = a+1; b < npts; b++)
            for (int c = b+1; c < npts; c++) {
                int dx = pts[b].x - pts[a].x;
                int dy = pts[b].y - pts[a].y;
                if (dx * (pts[c].y - pts[a].y) == dy * (pts[c].x - pts[a].x))
                    return true;
            }
    return false;
}

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

bool check_orbits(const vector<pair<int,int>>& orbits) {
    vector<Point> pts;
    for (auto& [i, j] : orbits) {
        auto p = orbit_points(i, j);
        pts.insert(pts.end(), p.begin(), p.end());
    }
    if (!check_row_col(pts)) return false;
    if (has_collinear(pts)) return false;
    return true;
}

// Check a cycle type with given vertex order, trying all direction assignments
bool check_with_directions(const vector<int>& vertices, 
                           const vector<int>& cycle_type,
                           vector<pair<int,int>>& output_orbits) {
    vector<pair<int,int>> edge_pairs;
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
    for (int mask = 0; mask < (1 << m); mask++) {
        vector<pair<int,int>> orbits;
        for (int i = 0; i < m; i++) {
            auto [v1, v2] = edge_pairs[i];
            if (mask & (1 << i))
                orbits.push_back({v2, v1});
            else
                orbits.push_back({v1, v2});
        }
        if (check_orbits(orbits)) {
            output_orbits = orbits;
            return true;
        }
    }
    return false;
}

// Test all permutations for a given cycle type
// Returns number of valid solutions found
int test_cycle_type(const vector<int>& cycle_type, 
                     int max_permutations = 1000000) {
    vector<int> vertices(M);
    iota(vertices.begin(), vertices.end(), 0);
    
    int found = 0;
    int tested = 0;
    do {
        // Skip rotation duplicates for efficiency
        if (cycle_type[0] > 1) {
            int first_cycle_end = cycle_type[0];
            int min_in_first = *min_element(vertices.begin(), vertices.begin() + first_cycle_end);
            if (vertices[0] != min_in_first) continue;
        }
        
        vector<pair<int,int>> output_orbits;
        if (check_with_directions(vertices, cycle_type, output_orbits)) {
            found++;
            if (found <= 3) {
                cout << "  VALID #" << found << ": order=[";
                for (int v : vertices) cout << v << ",";
                cout << "] orbits=[";
                for (auto& [i,j] : output_orbits) cout << "(" << i << "," << j << ")";
                cout << "]" << endl;
            }
        }
        tested++;
        if (tested >= max_permutations) break;
        
    } while (next_permutation(vertices.begin(), vertices.end()));
    
    return found;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <m> [max_cycle_types]" << endl;
        return 1;
    }
    
    M = atoi(argv[1]);
    N = 2 * M;
    int max_types = (argc > 2) ? atoi(argv[2]) : 1000;
    
    cout << "==================================================" << endl;
    cout << "C4 Cycle Explorer: n=" << N << " (m=" << M << ")" << endl;
    cout << "==================================================" << endl;
    
    auto start = chrono::steady_clock::now();
    
    // Generate cycle types
    vector<vector<int>> cycle_types;
    
    // Full m-cycle
    cycle_types.push_back({M});
    
    // Two cycles: (a, M-a)
    for (int a = 1; a <= M/2; a++) {
        if (a != M-a) // avoid duplicates like (3,3) already covered
            cycle_types.push_back({a, M-a});
        else
            cycle_types.push_back({a, a}); // (M/2, M/2)
    }
    
    // Three cycles for smaller m (skip if m too large)
    if (M <= 12) {
        for (int a = 1; a <= M-2; a++)
            for (int b = 1; b <= M-a-1; b++) {
                int c = M - a - b;
                // Only unique combinations
                if (a <= b && b <= c)
                    cycle_types.push_back({a, b, c});
            }
    }
    
    int tested = 0;
    vector<vector<int>> valid_types;
    
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
        
        int max_perm = 200000;
        int found = test_cycle_type(ct, max_perm);
        
        auto t1 = chrono::steady_clock::now();
        double secs = chrono::duration<double>(t1-t0).count();
        cout << "  Found: " << found << " valid, Time: " << secs << "s" << endl;
    }
    
    auto end = chrono::steady_clock::now();
    cout << "\nTotal time: " << chrono::duration<double>(end-start).count() << "s" << endl;
}
