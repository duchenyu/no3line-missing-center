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

// ===== Forbid accumulator: maintain per-row blocked column masks =====
// Add blocking from cross-row pair (r1,c1)-(r2,c2) [r1<r2] for all rows > r2
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
    int row_cols[32][2];   // columns placed at each row
    int cols[32];
    int diag1_cnt[64];     // x+y diagonal occupancy
    int diag2_cnt[64];     // x-y+N-1 diagonal occupancy
    uint64_t forbid[32];   // per-row forbidden column masks
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

            // No O(k²) collinear check — forbid[row] already filtered c1,c2 above
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

            // No O(k²) collinear check — forbid[row] already filtered both cols
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
