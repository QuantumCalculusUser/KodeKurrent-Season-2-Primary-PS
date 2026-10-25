# DraftMate Markdown / contract formatting fix

This patch addresses the formatting issue where generated contracts displayed literal Markdown bold markers such as `**SOFTWARE DEVELOPMENT AGREEMENT**`.

## Changes
- The on-screen formatted preview parses bold and italic markers without relying on regex lookbehind, improving compatibility with older Electron/Chromium builds.
- The DOCX exporter now renders bold/italic runs, heading levels, bullets and numbered paragraphs rather than writing raw Markdown syntax into Word.
- Markdown horizontal rules and fenced-code delimiters are not printed as document text.
- This changes presentation/export only. It does not verify legal facts, statutes, or citations.

## Important: rebuild the desktop app
If you run an already-installed `.exe`, source edits will not change it automatically.

1. Extract this ZIP to a new folder.
2. Run `RUN_DRAFTMATE.bat` for development/test mode, or follow `README_DESKTOP.md` to build the desktop application.
3. If dependencies are already installed, run the frontend build from the `frontend` folder: `npm run build`.
4. Restart the backend and Electron app after rebuilding.
5. Generate a test contract and use **Preview formatting** if the raw editable source is open. Then test **Export DOCX** in Word.

No complete Electron installer is included in this source patch.
