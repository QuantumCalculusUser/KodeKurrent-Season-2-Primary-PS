# DraftMate legal notice workflow wiring fix

This patch connects the existing legal-notice form to the previously added structured DOCX endpoint and adds explicit fields for material facts, requested relief, amount, deadline, supplied legal basis, and evidence.

## What changed
- The normal **Generate draft** action now passes the added structured facts/demand fields to the configured local Ollama model instead of relying only on the generic instruction box.
- **Build structured DOCX** calls `POST /api/legal-notice/assemble` and downloads a deterministic, formatted DOCX built from the form fields.
- The structured assembler validates required client/recipient/address/facts/demand/date fields and tells you which ones are missing.
- The legal-review warning remains intentionally visible. It is a caution, not a generation error.

## Apply/run
Use this project folder as the updated source. Install frontend dependencies from `frontend` with `npm install`, then run the project's normal Windows launcher. If you have an older packaged Electron build/installer, rebuilding it is required for source changes to appear in that installed app. Restart the backend after updating it.

The full frontend build was not verified in this environment because npm dependency installation timed out. Backend Python syntax was verified. Please test the UI and DOCX export locally before relying on it.
