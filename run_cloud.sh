#!/bin/bash
# ============================================
# No-Three-In-Line Cloud Runner
# Cloud: AMD 9550X 16-core Linux
# ============================================
set -e

MODE=${1:-1}          # 1 = missing only (推荐), 0 = full search
THREADS=${2:-16}      # 16核全开
N_LIST=${3:-"15 17 19 21 23"}  # 要跑的 n 值列表

echo "========================================"
echo " No-Three-In-Line Cloud Runner"
echo " Mode    = $MODE (0=full, 1=missing only)"
echo " Threads = $THREADS"
echo " N list  = $N_LIST"
echo "========================================"
echo ""

# 检查编译
if [ ! -f no3line ]; then
    echo "[INFO] Compiling no3line.cpp..."
    g++ -O3 -march=native -std=c++17 -pthread -o no3line no3line.cpp -pthread
    echo "[OK] Compiled"
    echo ""
fi

# 汇总CSV
echo "n,total_solutions,with_center,missing_center,time_seconds,mode" > summary_results.csv

for N in $N_LIST; do
    echo "========================================"
    echo " Running n=$N  (mode=$MODE, threads=$THREADS)"
    date
    echo "========================================"
    
    ./no3line $N $MODE $THREADS
    
    RESULT_FILE="result_n${N}_mode${MODE}.csv"
    if [ -f "$RESULT_FILE" ]; then
        # 追加到汇总（跳过CSV表头）
        tail -1 "$RESULT_FILE" >> summary_results.csv
        echo "[OK] $RESULT_FILE saved"
    fi
    
    echo " Finished n=$N at $(date)"
    echo ""
done

echo "========================================"
echo " ALL DONE!"
echo "========================================"
cat summary_results.csv
