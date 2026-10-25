# CasePilot `Failed to fetch` connection fix

This update adds a build identifier and CasePilot feature flag to `/api/health`, and Electron now refuses to silently attach to an older/incompatible API already occupying port 8000. The frontend also reports a more useful local-API connection message instead of only `Failed to fetch`.

## Install
1. Close all DraftMate windows.
2. Extract this ZIP to a new folder.
3. Run `RUN_DRAFTMATE.bat` from that folder.
4. If the startup dialog says an older backend is responding, open Task Manager, end leftover DraftMate/Electron/Python processes belonging to the older copy, and launch the batch file again.
5. Ollama must be running with the configured model installed for AI drafting. The local API dashboard can start without Ollama, but AI generation may use a fallback template.

The feature flag checks that the running API includes CasePilot's `/api/case/draft` and speech cleanup implementation. It does not guarantee that Ollama is available or that model output is legally correct.
