# DraftMate AI Desktop Edition (Windows)

This wraps the existing cream-and-gold DraftMate web interface in a native Electron desktop window and starts its local FastAPI backend automatically. Drafts and the SQLite database are stored in the current Windows user's Electron app-data directory, not in the installation folder.

## Build the Windows installer

Requirements on the Windows build machine:
- Node.js LTS (npm included)
- Python 3.11+ available as `py`
- Internet access during the first build to download dependencies
- Ollama installed for local AI generation (may be installed before or after building)

1. Extract the entire ZIP into a writable folder, for example `C:\Users\YourName\Documents\DraftMateDesktop`.
2. Double-click `build_windows.bat`.
3. Wait for all five build stages to complete. The first build can take several minutes.
4. Install `release\DraftMate-AI-Setup-1.0.0.exe`.
5. Install/start Ollama and ensure `qwen2.5:7b` is present (`ollama pull qwen2.5:7b`).
6. Launch DraftMate AI from the desktop shortcut.

## How the desktop app works

- Opens in its own Windows application window, not a browser tab.
- Starts the bundled local API service on `127.0.0.1:8000`.
- Uses the local Ollama service on `127.0.0.1:11434` by default.
- Uses the `qwen2.5:7b` model by default. Override `OLLAMA_MODEL` before launch if needed.
- Stores drafts in `%APPDATA%\draftmate-ai-desktop\draftmate.db` (Electron user data path may vary by Windows profile).
- Does not require a paid AI API key.

## Troubleshooting

- If build says Node.js or Python is missing, install it and reopen Command Prompt.
- If port 8000 is already occupied by a manually running backend, close that server before opening the desktop app.
- If the dashboard opens but Ollama status is unavailable, run `ollama list` and then `ollama pull qwen2.5:7b` if needed. Confirm `http://127.0.0.1:11434/api/tags` responds.
- If Windows Defender prompts about a locally built unsigned installer, verify you built it from this source before allowing it.
- Citation checks in this version detect citation-like patterns but do not independently validate authorities against a legal database. Human legal review remains necessary.

## Build status

This package includes the desktop wrapper and build script. The Windows installer must be built on Windows using `build_windows.bat`; a compiled Windows installer is not included in this source ZIP. The script reports errors from the actual build steps.
