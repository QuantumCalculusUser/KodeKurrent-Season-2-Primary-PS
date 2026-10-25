@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title DraftMate AI - Web Edition
color 0E
echo ==============================================================
echo             DRAFTMATE AI - LOCAL WEBSITE
 echo ============================================================== 
echo.
where node >nul 2>nul || (echo [ERROR] Node.js LTS is required for the first frontend build. Install from https://nodejs.org/ and retry.& pause & exit /b 1)
where npm >nul 2>nul || (echo [ERROR] npm was not found. Reinstall Node.js LTS.& pause & exit /b 1)
where py >nul 2>nul || (echo [ERROR] Python 3.11+ is required. Install from https://www.python.org/downloads/windows/ and enable Add Python to PATH.& pause & exit /b 1)

netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul
if not errorlevel 1 (
  echo [WARNING] Port 8000 is already in use. Another DraftMate backend may be running.
  echo Close the older DraftMate backend window, then run this file again.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/5] Creating Python environment...
  py -3 -m venv backend\.venv
  if errorlevel 1 (echo [ERROR] Could not create Python environment.& pause & exit /b 1)
)
if not exist "backend\.venv\Scripts\uvicorn.exe" (
  echo [2/5] Installing backend dependencies. First run may take several minutes...
  call backend\.venv\Scripts\python.exe -m pip install --upgrade pip
  if errorlevel 1 (echo [ERROR] pip upgrade failed.& pause & exit /b 1)
  call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  if errorlevel 1 (echo [ERROR] Backend dependency installation failed.& pause & exit /b 1)
) else (echo [2/5] Backend dependencies are installed.)

if not exist "frontend-web\node_modules\vite\bin\vite.js" (
  echo [3/5] Installing frontend dependencies. First run may take several minutes...
  pushd frontend-web
  call npm install
  if errorlevel 1 (popd & echo [ERROR] Frontend dependency installation failed.& pause & exit /b 1)
  popd
) else (echo [3/5] Frontend dependencies are installed.)

echo [4/5] Building website...
pushd frontend-web
call npm run build
if errorlevel 1 (popd & echo [ERROR] Website build failed. Read the first error above.& pause & exit /b 1)
popd
if not exist "backend\static" mkdir "backend\static"
robocopy "frontend-web\dist" "backend\static" /MIR >nul
if errorlevel 8 (echo [ERROR] Could not copy built website files.& pause & exit /b 1)

echo [5/5] Starting local website and API...
start "DraftMate API - keep this window open" "%ComSpec%" /k ""%~dp0RUN_DRAFTMATE_WEB_API.bat""
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8000
echo.
echo DraftMate is opening in your default browser at http://127.0.0.1:8000
echo Keep the API window open while using the website.
echo This is a local website; it is not publicly hosted on the internet.
echo Close the API window to stop DraftMate.
echo.
pause
