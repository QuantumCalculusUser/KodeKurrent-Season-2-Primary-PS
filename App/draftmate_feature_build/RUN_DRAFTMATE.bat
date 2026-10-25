@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title DraftMate AI - Launcher
color 0E
echo ==============================================================
echo                  DRAFTMATE AI - STARTUP
echo ==============================================================
echo.

where node >nul 2>nul || (echo [ERROR] Node.js is not installed. Install Node.js LTS from https://nodejs.org/ and run this file again.& pause & exit /b 1)
where npm >nul 2>nul || (echo [ERROR] npm was not found. Reinstall Node.js LTS.& pause & exit /b 1)
where py >nul 2>nul || (echo [ERROR] Python launcher was not found. Install Python 3.11+ from https://www.python.org/downloads/windows/ and enable Add Python to PATH.& pause & exit /b 1)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/5] Creating the local Python environment...
  py -3 -m venv backend\.venv
  if errorlevel 1 (echo [ERROR] Could not create the Python environment.& pause & exit /b 1)
) else (echo [1/5] Python environment already exists.)

if not exist "backend\.venv\Scripts\uvicorn.exe" (
  echo [2/5] Installing backend packages. This may take several minutes on first run...
  call backend\.venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 (echo [ERROR] pip upgrade failed.& pause & exit /b 1)
  call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  if errorlevel 1 (echo [ERROR] Backend package installation failed.& pause & exit /b 1)
) else (echo [2/5] Backend packages already installed.)

if not exist "frontend\node_modules\vite\bin\vite.js" (
  echo [3/5] Installing frontend packages. This may take several minutes on first run...
  pushd frontend
  call npm install
  if errorlevel 1 (popd & echo [ERROR] Frontend package installation failed.& pause & exit /b 1)
  popd
) else (echo [3/5] Frontend packages already installed.)

if not exist "node_modules\electron\dist\electron.exe" (
  echo [4/5] Installing desktop runtime...
  call npm install
  if errorlevel 1 (echo [ERROR] Desktop runtime installation failed.& pause & exit /b 1)
) else (echo [4/5] Desktop runtime already installed.)

if not exist "backend\static\index.html" (
  echo [5/5] Building the interface for desktop use...
  pushd frontend
  call npm run build
  if errorlevel 1 (popd & echo [ERROR] Frontend build failed.& pause & exit /b 1)
  popd
  if exist "backend\static" rmdir /s /q "backend\static"
  xcopy "frontend\dist" "backend\static" /E /I /Y >nul
  if errorlevel 1 (echo [ERROR] Could not copy built interface.& pause & exit /b 1)
) else (echo [5/5] Desktop interface build already exists.)

echo.
echo Starting DraftMate AI. Keep this window open to see diagnostics.
echo The app will open in its own desktop window.
echo.
if not exist "backend\.venv\Scripts\python.exe" (echo [ERROR] Python environment missing.& pause & exit /b 1)
call npm start
set APP_EXIT=%ERRORLEVEL%
echo.
if not "%APP_EXIT%"=="0" echo DraftMate exited with code %APP_EXIT%.
echo You can close this window after reviewing any errors.
pause
exit /b %APP_EXIT%
