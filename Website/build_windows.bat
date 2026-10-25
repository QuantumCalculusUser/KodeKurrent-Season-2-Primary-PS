@echo off
setlocal
cd /d "%~dp0"
echo =====================================================
echo DraftMate AI - Windows desktop installer builder
echo =====================================================
echo.
where node >nul 2>nul || (echo ERROR: Install Node.js LTS first: https://nodejs.org/ & pause & exit /b 1)
where npm >nul 2>nul || (echo ERROR: npm was not found. Reinstall Node.js LTS. & pause & exit /b 1)
where py >nul 2>nul || (echo ERROR: Install Python 3.11 or newer first: https://www.python.org/downloads/windows/ & pause & exit /b 1)
echo [1/5] Installing frontend dependencies and building UI...
cd frontend
call npm install || (echo Frontend dependency install failed.& pause & exit /b 1)
call npm run build || (echo Frontend build failed.& pause & exit /b 1)
cd ..
echo [2/5] Preparing backend static files...
if exist backend\static rmdir /s /q backend\static
xcopy frontend\dist backend\static /E /I /Y >nul || (echo Could not copy frontend build.& pause & exit /b 1)
echo [3/5] Creating backend Python environment...
if not exist backend\.venv py -m venv backend\.venv
call backend\.venv\Scripts\python.exe -m pip install --upgrade pip || (echo pip setup failed.& pause & exit /b 1)
call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt pyinstaller || (echo Backend dependency install failed.& pause & exit /b 1)
echo [4/5] Bundling backend executable...
cd backend
call .venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --name draftmate-api --add-data "static;static" --collect-all uvicorn --collect-all fastapi --collect-all pydantic --collect-all docx --collect-all pypdf --collect-all dotenv --collect-all multipart desktop_entry.py
if errorlevel 1 (cd .. & echo Backend bundling failed.& pause & exit /b 1)
cd ..
if not exist backend-dist mkdir backend-dist
copy /Y backend\dist\draftmate-api.exe backend-dist\draftmate-api.exe >nul || (echo Backend executable not found.& pause & exit /b 1)
echo [5/5] Building Windows installer...
call npm install || (echo Electron dependencies failed.& pause & exit /b 1)
call npm run dist:win
if errorlevel 1 (echo Installer build failed. See errors above.& pause & exit /b 1)
echo.
echo SUCCESS. Look inside the release folder for DraftMate-AI-Setup-1.0.0.exe
echo Ollama must be installed separately for local AI generation.
pause
