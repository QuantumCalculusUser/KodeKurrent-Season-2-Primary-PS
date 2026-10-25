@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.env" (
  copy "backend\.env.example" "backend\.env" >nul
  echo Created backend\.env from the example.
) else (
  echo Existing backend\.env found. It will not be overwritten.
)
echo.
echo Paste your NEW Gemini key after GEMINI_API_KEY= in backend\.env.
echo Do not paste the key into frontend files or commit backend\.env to Git.
notepad "backend\.env"
echo.
echo Save and close Notepad, then close all DraftMate website API windows.
echo Run RUN_DRAFTMATE_WEB.bat again to restart the backend.
pause
