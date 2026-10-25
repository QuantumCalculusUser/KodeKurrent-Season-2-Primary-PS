@echo off
setlocal
cd /d "%~dp0backend"
set "DRAFTMATE_STATIC_DIR=%~dp0backend\static"
echo DraftMate Website API serving Gemini-powered website at http://127.0.0.1:8000
echo Keep this window open while using the website.
.venv\Scripts\python.exe -m uvicorn app.web_main:app --host 127.0.0.1 --port 8000
pause
