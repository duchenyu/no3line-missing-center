@echo off
echo ========================================
echo   No-Three-In-Line - Compile Script
echo ========================================
echo.

where g++ >nul 2>nul
if %errorlevel%==0 (
    echo [1/2] Found MinGW g++, compiling...
    g++ -O3 -std=c++17 -pthread no3line.cpp -o no3line.exe
    if exist no3line.exe (
        echo [OK] Compile success: no3line.exe
    ) else (
        echo [FAIL] Compile failed!
        pause
        exit /b 1
    )
) else (
    echo [WARN] g++ not found, trying MSVC cl...
    where cl >nul 2>nul
    if %errorlevel%==0 (
        cl /O2 /EHsc /std:c++17 no3line.cpp /Fe:no3line.exe
    ) else (
        echo [FAIL] No compiler found!
        echo Please install MinGW-w64 or Visual Studio.
        echo Download MinGW: https://github.com/niXman/mingw-builds-binaries/releases
        pause
        exit /b 1
    )
)

echo.
echo [2/2] Quick test: n=7 mode=1
no3line.exe 7 1 4
echo.
echo Done! Use run.bat to start computing.
pause
