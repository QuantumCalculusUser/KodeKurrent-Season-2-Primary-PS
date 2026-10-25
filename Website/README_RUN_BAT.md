# DraftMate AI: one-click local launcher

## Start the app
1. Extract this whole folder to a writable location such as `Documents\DraftMateAI`.
2. Install Node.js LTS and Python 3.11+ if they are not already installed.
3. Double-click `RUN_DRAFTMATE.bat`.
4. The first run installs dependencies and builds the desktop interface; it needs internet access and may take several minutes. Later starts reuse the installed dependencies.
5. Keep the launcher window open while DraftMate AI is running. Backend logs/errors will appear in this window.

Ollama must also be installed and running for AI generation. This launcher does not install Ollama or download a multi-gigabyte model. Check models with `ollama list`; the default is `qwen2.5:7b`.

## If AI generation fails
After clicking Generate draft, read the new error lines in the launcher window. The app can still open if Ollama is unavailable, but generation may use a clearly labelled fallback template. A fallback template is not a successful AI response.

## Privacy and storage
The API listens on `127.0.0.1:8000` only. Draft data is stored in the current Windows user's app-data folder. Do not share legal documents containing confidential information unless authorized.

## Notes
This is a source-based launcher, not a compiled installer. It bootstraps dependencies on first run and starts the Electron desktop app directly, avoiding the need to manually open separate Command Prompt windows. `build_windows.bat` remains available to create an installer later.
