#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

int N=10, M=5;

struct Point { int x,y; };
vector<Point> orbit_pts(int i, int j) {
    int n=N; return {{i,j},{n-1-j,i},{n-1-i,n-1-j},{j,n-1-i}};
}

int main() {
    // Test the step=2 pattern for the full 5-cycle
    vector<int> order;
    int cur=0;
    for (int i=0;i<M;i++) { order.push_back(cur); cur=(cur+2)%M; }
    cout << "Order: ";
    for (int v:order) cout << v << " ";
    cout << endl;
    
    set<int> u(order.begin(),order.end());
    cout << "Unique: " << u.size() << "/" << M << endl;
    
    vector<pair<int,int>> edges;
    for (int i=0;i<M;i++) edges.push_back({order[i],order[(i+1)%M]});
    cout << "Edges: ";
    for (auto [a,b]:edges) cout << "(" << a << "," << b << ") ";
    cout << endl;
    
    // Try all directions
    for (int mask=0;mask<32;mask++) {
        vector<Point> pts;
        for (int i=0;i<M;i++) {
            auto [a,b] = edges[i];
            if (mask&(1<<i)) swap(a,b);
            auto p = orbit_pts(a,b);
            pts.insert(pts.end(),p.begin(),p.end());
        }
        
        vector<int> rc(N,0),cc(N,0);
        for (auto& p:pts) { rc[p.x]++; cc[p.y]++; }
        bool ok=true;
        for (int c:rc) if (c!=2) ok=false;
        for (int c:cc) if (c!=2) ok=false;
        if (!ok) continue;
        
        bool coll=false;
        for (int a=0;a<(int)pts.size()&&!coll;a++)
            for (int b=a+1;b<(int)pts.size()&&!coll;b++)
                for (int c=b+1;c<(int)pts.size()&&!coll;c++) {
                    int dx=pts[b].x-pts[a].x, dy=pts[b].y-pts[a].y;
                    if (dx*(pts[c].y-pts[a].y) == dy*(pts[c].x-pts[a].x)) coll=true;
                }
        if (!coll) {
            cout << "VALID mask=" << mask << ": orbits=[";
            for (int i=0;i<M;i++) {
                auto [a,b] = edges[i];
                if (mask&(1<<i)) swap(a,b);
                cout << "(" << a << "," << b << ")";
            }
            cout << "]" << endl;
        }
    }
    cout << "Done" << endl;
}
