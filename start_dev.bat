@echo off
echo Starting Bridgr Development Environment...
echo.

echo [1/3] Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend is already running on port 8000
) else (
    echo Starting backend...
    cd backend
    start "Bridgr Backend" cmd /k "python start.py"
    cd ..
    timeout /t 3 /nobreak >nul
)

echo.
echo [2/3] Checking if frontend is running...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo Frontend is already running on port 3000
) else (
    echo Starting frontend...
    cd frontend
    start "Bridgr Frontend" cmd /k "npm start"
    cd ..
)

echo.
echo [3/3] Opening browser...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo ================================
echo Bridgr Development Environment
echo ================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo Health:   http://localhost:8000/health
echo CORS Test: http://localhost:8000/debug/cors
echo ================================
echo.
echo Press any key to exit...
pause >nul