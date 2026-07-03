@echo off
setlocal enabledelayedexpansion

:: ========================================
::  Configuration
:: ========================================
:: MODE 0 = Full search (total + missing, SLOW for large n)
:: MODE 1 = Missing only with distance pruning (FAST, recommended for n>=15)
set MODE=1

:: Number of CPU threads (your server has 12 vCPU)
set THREADS=12

:: List of n values to compute (space separated)
set N_LIST=15 17 19 21 23

:: ========================================
echo ========================================
echo   No-Three-In-Line Batch Runner
echo   Mode = %MODE%  (0=full, 1=missing only)
echo   Threads = %THREADS%
echo   N list  = %N_LIST%
echo ========================================
echo.

if not exist no3line.exe (
    echo [ERROR] no3line.exe not found! Run compile.bat first.
    pause
    exit /b 1
)

:: Create summary CSV
echo n,total_solutions,with_center,missing_center,time_seconds,mode > summary_results.csv

for %%n in (%N_LIST%) do (
    echo.
    echo ========================================
    echo  Starting n=%%n ...
    echo  Time: %date% %time%
    echo ========================================
    
    no3line.exe %%n %MODE% %THREADS%
    
    :: Append to summary
    if exist result_n%%n_mode%MODE%.csv (
        for /f "skip=1 delims=, tokens=1-6" %%a in (result_n%%n_mode%MODE%.csv) do (
            echo %%a,%%b,%%c,%%d,%%e,%%f >> summary_results.csv
        )
        echo  [OK] result_n%%n_mode%MODE%.csv saved
    )
    
    echo  Finished n=%%n at %date% %time%
)

echo.
echo ========================================
echo  ALL DONE! Summary saved to summary_results.csv
echo ========================================
type summary_results.csv
echo.
pause
