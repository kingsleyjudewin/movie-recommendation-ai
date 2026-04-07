@echo off
REM CineMind AI — Development startup script (Windows)
REM Starts the FastAPI backend and the Vite dev server in separate windows.

echo.
echo  ========================================
echo   CineMind AI — starting dev servers...
echo  ========================================
echo.

REM Force HuggingFace to use the locally cached model (no internet needed)
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1

REM Start FastAPI backend in a new window
start "CineMind Backend" cmd /k "cd /d "%~dp0" && set HF_HUB_OFFLINE=1 && set TRANSFORMERS_OFFLINE=1 && uvicorn api.main:app --reload --port 8000"

REM Wait a moment for the backend to begin loading
timeout /t 3 /nobreak >nul

REM Start Vite dev server in a new window
start "CineMind Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo  Backend : http://localhost:8000
echo  Frontend: http://localhost:8081
echo.
echo  Close the two opened terminal windows to stop the servers.
echo.
