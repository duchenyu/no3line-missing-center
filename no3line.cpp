// ============================================================
// No-Three-In-Line Problem - v2 (Precomputed Blocking + O(1) check)
// Full search + missing-only mode, multi-threaded
// Mirror symmetry pruning, distance pruning, diagonal pruning
// ============================================================
#include <iostream>
#include <fstream>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <cstdio>
#include <string>
using namespace std;

int N;
int NUM_THREADS = 12;
int64_t cx_times2, cy_times2;
vector<int> dist_lookup;
mutex file_mutex;
FILE* sol_file = NULL;

atomic<long long> total_sol(0);
atomic<long long> missing_sol(0);

inline int get_dist(int c, int r) {
    return dist_lookup[r * N + c];
}

// ====================================================================
// Forbid Accumulator — O(1) collinearity check via precomputed blocking
// ====================================================================
// CORE IDEA:
//   Instead of O(k²) nested-loop checking every pair of existing points
//   when placing a new point, we maintain a per-row bitmask array
//   `forbid[row]` that pre-accumulates all columns that would create a
//   collinear triple with ANY two previously placed points.
//
//   At placement time for row 'r', column 'c':
//       if (forbid[r] has bit c set) → reject immediately (O(1))
//
//   The check is provably complete because:
//   - Every collinear triple (r1,c1)-(r2,c2)-(r3,c3) has a unique pair
//     with the two largest row indices.
//   - When that pair's second point is placed (at the higher row),
//     the line equation is used to compute the blocking column at r3.
//
//   This works for ALL slopes, not just axis-aligned or ±45°:
//   The line through (r1,c1)-(r2,c2) is y = c1 + (c2-c1)/(r2-r1) * (x-r1).
//   For any future row tr, the collinear column is:
//       col = c1 + (c2-c1)*(tr-r1) / (r2-r1)
//   which must be an integer (the divisible check num % dr == 0).
//
//   Bit width (uint64_t): sufficient for n ≤ 46 since 46 < 64.
//   For n > 46, uint64_t would need to be replaced with __int128 or
//   a bitset, but the problem's maximum D(n) is only studied up to n=71.
// ====================================================================

// Add blocking from cross-row pair (r1,c1)-(r2,c2) [r1<r2] for all rows > r2
// For each future row tr, we compute whether the line through (r1,c1)-(r2,c2)
// passes through an integer grid column at that row, using integer arithmetic
// to avoid floating point.
static inline void add_block(uint64_t* forbid, int r1, int c1, int r2, int c2) {
    int dr = r2 - r1;
    int dc = c2 - c1;
    for (int tr = r2 + 1; tr < N; tr++) {
        int num = dc * (tr - r1);
        if (num % dr == 0) {
            int col = c1 + num / dr;
            if (col >= 0 && col < N)
                forbid[tr] |= (1ULL << col);
        }
    }
}

// Update forbid[] after placing (c1,c2) at [row]
// Pairs (row, c1) and (row, c2) with every point from rows 0..row-1
static inline void update_block(uint64_t* forbid, const int row_cols[][2], int row) {
    int c1 = row_cols[row][0];
    int c2 = row_cols[row][1];
    for (int i = 0; i < row; i++) {
        int a = row_cols[i][0], b = row_cols[i][1];
        add_block(forbid, i, a, row, c1);
        add_block(forbid, i, a, row, c2);
        add_block(forbid, i, b, row, c1);
        add_block(forbid, i, b, row, c2);
    }
}

    // ========== Mode 0: Full search ==========
struct FullState {
    int row_cols[32][2];   // columns placed at each row (max n=32, expandable)
    int cols[32];          // column usage count (each column appears exactly 2×)
    int diag1_cnt[64];     // x+y diagonal occupancy counter (for anti-diag pruning)
    int diag2_cnt[64];     // x-y+N-1 diagonal occupancy counter (for diag pruning)
    uint64_t forbid[32];   // per-row forbidden column bitmasks — the core accelerator
                           // bit c set → placing column c at this row creates collinearity
                           // uint64_t suffices for n ≤ 46 (46 < 64 bits)
    long long local_total;
    long long local_missing;
};

void bt_full(FullState& s, int row) {
    if (row == N) {
        // Verify all columns used exactly twice
        for (int c = 0; c < N; c++)
            if (s.cols[c] != 2) return;
        s.local_total++;
        // Check center presence via distance rings
        int dc[512] = {0};
        bool has3 = false;
        for (int i = 0; i < N; i++) {
            int d = get_dist(s.row_cols[i][0], i);
            if (++dc[d] >= 3) { has3 = true; break; }
            d = get_dist(s.row_cols[i][1], i);
            if (++dc[d] >= 3) { has3 = true; break; }
        }
        if (!has3) s.local_missing++;
        return;
    }

    uint64_t forbid_row = s.forbid[row];
    uint64_t saved[32];
    memcpy(saved, s.forbid, sizeof(saved));

    // Build available columns (not full, not blocked by existing pairs)
    int avail[32], ac = 0;
    for (int c = 0; c < N; c++)
        if (s.cols[c] < 2 && !(forbid_row & (1ULL << c)))
            avail[ac++] = c;

    for (int i = 0; i < ac; i++) {
        int c1 = avail[i];
        if (s.diag1_cnt[c1 + row] >= 2) continue;
        if (s.diag2_cnt[c1 - row + N - 1] >= 2) continue;
        s.cols[c1]++;
        s.diag1_cnt[c1 + row]++;
        s.diag2_cnt[c1 - row + N - 1]++;

        for (int j = i + 1; j < ac; j++) {
            int c2 = avail[j];
            if (s.diag1_cnt[c2 + row] >= 2) continue;
            if (s.diag2_cnt[c2 - row + N - 1] >= 2) continue;
            s.cols[c2]++;
            s.diag1_cnt[c2 + row]++;
            s.diag2_cnt[c2 - row + N - 1]++;

            // NO O(k²) COLLINEAR CHECK NEEDED — forbid[row] already filtered c1,c2
            // The forbid_accum array has been maintained by update_block() at
            // every previous row, blocking all columns that would create a
            // collinear triple with any two existing cross-row points.
            // This is the key optimization: O(k²) -> O(1) per placement.
            s.row_cols[row][0] = c1;
            s.row_cols[row][1] = c2;
            memcpy(s.forbid, saved, sizeof(saved));
            update_block(s.forbid, s.row_cols, row);
            bt_full(s, row + 1);

            s.diag2_cnt[c2 - row + N - 1]--;
            s.diag1_cnt[c2 + row]--;
            s.cols[c2]--;
        }
        s.diag2_cnt[c1 - row + N - 1]--;
        s.diag1_cnt[c1 + row]--;
        s.cols[c1]--;
    }
}

// ========== Mode 1: Missing-only with distance pruning ==========
struct MissState {
    int row_cols[32][2];
    int cols[32];
    int diag1_cnt[64];
    int diag2_cnt[64];
    int dist_cnt[512];
    uint64_t forbid[32];
    long long local_missing;
};

void bt_miss(MissState& s, int row) {
    if (row == N) {
        for (int c = 0; c < N; c++)
            if (s.cols[c] != 2) return;
        // Dump to CSV
        {
            lock_guard<mutex> lock(file_mutex);
            fprintf(sol_file, "%d", N);
            for (int i = 0; i < N; i++)
                fprintf(sol_file, ",%d,%d", s.row_cols[i][0], s.row_cols[i][1]);
            fprintf(sol_file, "\n");
            fflush(sol_file);
        }
        s.local_missing++;
        return;
    }

    uint64_t forbid_row = s.forbid[row];
    uint64_t saved[32];
    memcpy(saved, s.forbid, sizeof(saved));

    // Build available columns (not full, not blocked by existing pairs)
    int avail[32], ac = 0;
    for (int c = 0; c < N; c++)
        if (s.cols[c] < 2 && !(forbid_row & (1ULL << c)))
            avail[ac++] = c;

    for (int i = 0; i < ac; i++) {
        int c1 = avail[i];
        int d1 = get_dist(c1, row);
        if (s.dist_cnt[d1] >= 2) continue;
        if (s.diag1_cnt[c1 + row] >= 2) continue;
        if (s.diag2_cnt[c1 - row + N - 1] >= 2) continue;
        s.cols[c1]++;
        s.diag1_cnt[c1 + row]++;
        s.diag2_cnt[c1 - row + N - 1]++;
        s.dist_cnt[d1]++;

        for (int j = i + 1; j < ac; j++) {
            int c2 = avail[j];
            int d2 = get_dist(c2, row);
            if (s.dist_cnt[d2] >= 2) continue;
            if (s.diag1_cnt[c2 + row] >= 2) continue;
            if (s.diag2_cnt[c2 - row + N - 1] >= 2) continue;
            s.cols[c2]++;
            s.diag1_cnt[c2 + row]++;
            s.diag2_cnt[c2 - row + N - 1]++;
            s.dist_cnt[d2]++;

            // NO O(k²) COLLINEAR CHECK NEEDED — see comment in bt_full()
            s.row_cols[row][0] = c1;
            s.row_cols[row][1] = c2;
            memcpy(s.forbid, saved, sizeof(saved));
            update_block(s.forbid, s.row_cols, row);
            bt_miss(s, row + 1);

            s.dist_cnt[d2]--;
            s.diag2_cnt[c2 - row + N - 1]--;
            s.diag1_cnt[c2 + row]--;
            s.cols[c2]--;
        }
        s.dist_cnt[d1]--;
        s.diag2_cnt[c1 - row + N - 1]--;
        s.diag1_cnt[c1 + row]--;
        s.cols[c1]--;
    }
}

// ========== Workers ==========
void worker_full(int c1, int c2, int mult) {
    FullState s;
    memset(&s, 0, sizeof(s));
    s.row_cols[0][0] = c1;
    s.row_cols[0][1] = c2;
    s.cols[c1] = 1; s.cols[c2] = 1;
    // row 0 has no previous rows, so no forbid update needed
    bt_full(s, 1);
    total_sol += s.local_total * mult;
    missing_sol += s.local_missing * mult;
}

void worker_miss(int c1, int c2, int mult) {
    MissState s;
    memset(&s, 0, sizeof(s));
    s.row_cols[0][0] = c1;
    s.row_cols[0][1] = c2;
    s.cols[c1] = 1; s.cols[c2] = 1;
    s.dist_cnt[get_dist(c1, 0)]++;
    s.dist_cnt[get_dist(c2, 0)]++;
    // row 0 has no previous rows, so no forbid update needed
    bt_miss(s, 1);
    missing_sol += s.local_missing * mult;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Usage: no3line.exe <n> [mode] [threads]\n");
        printf("  mode 0 = full search (total + missing)\n");
        printf("  mode 1 = missing only with distance pruning (default)\n");
        printf("Example: no3line.exe 15 0 12\n");
        return 1;
    }
    N = atoi(argv[1]);
    int mode = (argc > 2) ? atoi(argv[2]) : 1;
    NUM_THREADS = (argc > 3) ? atoi(argv[3]) : 12;

    if (N % 2 == 0) { cx_times2 = N - 1; cy_times2 = N - 1; }
    else { cx_times2 = 2 * (N / 2); cy_times2 = cx_times2; }

    // Precompute squared Euclidean distances from grid center for all cells
    // For even n, center = ((n-1)/2, (n-1)/2) is half-integer; we use
    // scaled coordinates: dx = 2*c - cx_times2  (always integer)
    // d = dx² + dy²  — the actual squared Euclidean distance × 4
    // This is the "distance ring" value used in missing-center detection.
    dist_lookup.resize(N * N);
    for (int r = 0; r < N; r++)
        for (int c = 0; c < N; c++) {
            int64_t dx = 2LL * c - cx_times2;
            int64_t dy = 2LL * r - cy_times2;
            dist_lookup[r * N + c] = (int)(dx * dx + dy * dy);
        }

    // Mirror symmetry: only search c1+c2 <= N-1 for first row
    vector<pair<pair<int,int>, int>> tasks;
    for (int c1 = 0; c1 < N; c1++)
        for (int c2 = c1 + 1; c2 < N; c2++) {
            int sum = c1 + c2;
            if (sum < N - 1) tasks.push_back({{c1, c2}, 2});
            else if (sum == N - 1) tasks.push_back({{c1, c2}, 1});
        }

    printf("========================================\n");
    printf(" No-Three-In-Line v2 n=%d  mode=%d  threads=%d\n", N, mode, NUM_THREADS);
    printf(" Tasks: %d (mirror sym pruned)\n", (int)tasks.size());

    // Open solution dump file
    char dname[64];
    sprintf(dname, "sols_n%d.csv", N);
    sol_file = fopen(dname, "w");
    fprintf(sol_file, "n");
    for (int i = 0; i < N; i++)
        fprintf(sol_file, ",r%dc1,r%dc2", i, i);
    fprintf(sol_file, "\n");
    printf("              (dumping solutions to %s)\n", dname);
    printf("========================================\n");

    auto t0 = chrono::high_resolution_clock::now();
    atomic<int> tidx(0);
    vector<thread> threads;

    if (mode == 0) {
        auto f = [&]() {
            while (true) {
                int i = tidx++;
                if (i >= (int)tasks.size()) break;
                worker_full(tasks[i].first.first, tasks[i].first.second, tasks[i].second);
            }
        };
        for (int i = 0; i < NUM_THREADS; i++) threads.emplace_back(f);
    } else {
        auto f = [&]() {
            while (true) {
                int i = tidx++;
                if (i >= (int)tasks.size()) break;
                worker_miss(tasks[i].first.first, tasks[i].first.second, tasks[i].second);
            }
        };
        for (int i = 0; i < NUM_THREADS; i++) threads.emplace_back(f);
    }
    for (auto& t : threads) t.join();

    auto t1 = chrono::high_resolution_clock::now();
    double sec = chrono::duration<double>(t1 - t0).count();

    long long tot = total_sol.load();
    long long mis = missing_sol.load();

    printf("\n=========== RESULTS ===========\n");
    if (mode == 0) {
        printf("  Total solutions : %lld\n", tot);
        printf("  With center     : %lld\n", tot - mis);
    }
    printf("  Missing center  : %lld\n", mis);
    printf("  Time elapsed    : %.3f s\n", sec);
    printf("===============================\n");

    char csvname[64];
    sprintf(csvname, "result_n%d_mode%d.csv", N, mode);
    ofstream fout(csvname);
    fout << "n,total_solutions,with_center,missing_center,time_seconds,mode\n";
    fout << N << "," << tot << "," << (tot - mis) << "," << mis << "," << sec << "," << mode << "\n";
    fout.close();
    if (sol_file) fclose(sol_file);
    printf("\nCSV saved: %s\n", csvname);

    return 0;
}
