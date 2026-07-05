/*
 * C4 Fast Cycle Test — step pattern families for multiple m
 * 
 * For each m, test:
 * 1. Full m-cycle: [0, k, 2k, ... mod m] for k=1..m/2
 * 2. (1, m-1): loop at L, (m-1)-cycle as step pattern
 * 3. (a, m-a): both cycles as step patterns, try a subset of vertex assignments
 */
#include <iostream>
#include <vector>
#include <set>
#include <numeric>
#include <algorithm>
#include <chrono>
using namespace std;

int N, M;

struct Point { int x, y; };

vector<Point> orbit_pts(int i, int j) {
    int n = N;
    return {{i,j}, {n-1-j,i}, {n-1-i,n-1-j}, {j,n-1-i}};
}

bool collinear(const vector<Point>& pts) {
    int n = pts.size();
    for (int a=0;a<n;a++) for (int b=a+1;b<n;b++) for (int c=b+1;c<n;c++) {
        int dx = pts[b].x - pts[a].x, dy = pts[b].y - pts[a].y;
        if (dx*(pts[c].y-pts[a].y) == dy*(pts[c].x-pts[a].x)) return true;
    }
    return false;
}

bool check(const vector<pair<int,int>>& orb) {
    vector<Point> pts;
    for (auto& [i,j] : orb) { auto p = orbit_pts(i,j); pts.insert(pts.end(),p.begin(),p.end()); }
    vector<int> rc(N,0), cc(N,0);
    for (auto& p : pts) { rc[p.x]++; cc[p.y]++; }
    for (int c : rc) if (c!=2) return false;
    for (int c : cc) if (c!=2) return false;
    return !collinear(pts);
}

bool try_all_dirs(const vector<pair<int,int>>& edges, vector<pair<int,int>>& out) {
    int m = edges.size();
    for (int mask=0; mask<(1<<m); mask++) {
        vector<pair<int,int>> orb;
        for (int i=0;i<m;i++)
            orb.push_back((mask&(1<<i)) ? make_pair(edges[i].second,edges[i].first) : edges[i]);
        if (check(orb)) { out=orb; return true; }
    }
    return false;
}

// Step pattern for a cycle: vertices[0..len-1] arranged as [0, step, 2*step, ...]
vector<int> step_order(const vector<int>& verts, int step) {
    int len = verts.size();
    vector<int> res;
    int cur=0;
    for (int i=0;i<len;i++) { res.push_back(verts[cur]); cur=(cur+step)%len; }
    return res;
}

int main(int argc, char* argv[]) {
    vector<int> mvals = {10,11,12,13,21,22,23,30,31,32,33};
    if (argc>1) { mvals.clear(); for(int i=1;i<argc;i++) mvals.push_back(atoi(argv[i])); }
    
    for (int mi : mvals) {
        M=mi; N=2*M;
        cout << "\n=== m=" << M << " (n=" << N << ") ===" << endl;
        
        // 1. Full m-cycle with step patterns
        cout << "  Full (m)-cycle: ";
        int f=0;
        for (int s=1;s<M;s++) {
            if (s>M/2) continue;
            vector<int> order;
            int cur=0;
            for (int i=0;i<M;i++) { order.push_back(cur); cur=(cur+s)%M; }
            set<int> uniq(order.begin(),order.end());
            if ((int)uniq.size()!=M) continue;
            
            vector<pair<int,int>> edges;
            for (int i=0;i<M;i++) edges.push_back({order[i],order[(i+1)%M]});
            
            vector<pair<int,int>> out;
            if (try_all_dirs(edges,out)) f++;
        }
        cout << f << " valid step patterns" << endl;
        
        // 2. (1, m-1) with step patterns
        cout << "  (1,m-1): ";
        int o=0;
        for (int loop=0;loop<M;loop++) {
            vector<int> others;
            for (int v=0;v<M;v++) if (v!=loop) others.push_back(v);
            
            for (int s=1;s<M-1;s++) {
                if (s>(M-1)/2) continue;
                vector<int> cycle = step_order(others, s);
                set<int> u(cycle.begin(),cycle.end());
                if ((int)u.size()!=(M-1)) continue;
                
                // Build: loop + cycle
                vector<int> full = {loop};
                full.insert(full.end(), cycle.begin(), cycle.end());
                
                // Edges: loop (0,0) + remaining cycle
                vector<pair<int,int>> edges;
                edges.push_back({loop,loop}); // the 1-cycle
                for (int i=0;i<M-1;i++)
                    edges.push_back({full[i+1], full[(i+2)%M==0 ? 1 : (i+2)%(M)]});
                
                vector<pair<int,int>> out;
                if (try_all_dirs(edges,out)) o++;
            }
        }
        cout << o << " valid" << endl;
        
        // 3. Two-cycle splits (a, M-a) — limited sampling
        cout << "  Two-cycles: ";
        int t=0;
        for (int a=2;a<=M/2;a++) {
            int b=M-a;
            // Try a few vertex partitions
            for (int part=0;part<min(5,M);part++) {
                vector<int> ca, cb;
                for (int v=0;v<M;v++) {
                    if (v>=part && v<part+a) ca.push_back(v);
                    else cb.push_back(v);
                }
                if ((int)ca.size()!=a) continue; // wrong count
                if ((int)cb.size()!=b) continue;
                
                for (int sa=1;sa<a;sa++) {
                    if (sa>a/2) continue;
                    vector<int> oa = step_order(ca, sa);
                    set<int> ua(oa.begin(),oa.end());
                    if ((int)ua.size()!=a) continue;
                    
                    for (int sb=1;sb<b;sb++) {
                        if (sb>b/2) continue;
                        vector<int> ob = step_order(cb, sb);
                        set<int> ub(ob.begin(),ob.end());
                        if ((int)ub.size()!=b) continue;
                        
                        vector<pair<int,int>> edges;
                        for (int i=0;i<a;i++) edges.push_back({oa[i],oa[(i+1)%a]});
                        for (int i=0;i<b;i++) edges.push_back({ob[i],ob[(i+1)%b]});
                        
                        vector<pair<int,int>> out;
                        if (try_all_dirs(edges,out)) { t++; goto nexta; }
                    }
                }
            }
            nexta:;
        }
        cout << t << " valid (at least one (a,M-a))" << endl;
    }
}
