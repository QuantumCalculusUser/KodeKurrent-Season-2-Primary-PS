# DraftMate AI — rebuilt prototype

A fresh implementation for the Kodekurrent Season 2 Legal Drafting Studio challenge. Dark modern legal workspace, React/TypeScript frontend, FastAPI backend, Ollama local inference, modular skills, document upload/extraction, style-profile extraction, citation triage with source evidence records, voice input, and Markdown/DOCX export.

## Requirements
- Python 3.10+
- Node.js 20+
- Ollama (optional for template-only mode; recommended for actual generation)

## Run backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
ollama pull qwen2.5:7b
uvicorn app.main:app --reload --port 8000
```
If Ollama is already installed, ensure `ollama serve` is running. Change `OLLAMA_MODEL` in `backend/.env` to an installed model name if needed.

## Run frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite (normally http://localhost:5173). The frontend proxies `/api` to FastAPI.

## Implemented in this prototype
- Modular skill registry: legal notice, contract, agreement, petition/application, clause review, redline review, research brief, case analysis, due diligence, document summary.
- Ollama `/api/chat` integration with conservative legal drafting instructions and explicit fallback templates.
- Upload and extract PDF, DOCX, TXT and Markdown, with size limits.
- Reference-style profile extraction (structure, tone signals, headings and recurring phrases) from user-provided material.
- Citation-like pattern detection plus verification evidence schema. Since no live authoritative case-law API is configured by default, detected citations stay **unverified**. Source URLs are provided as research starting points; they are not evidence that a citation was validated.
- Voice input via browser Web Speech API when supported; text entry remains available.
- Draft history stored in SQLite, plus Markdown and DOCX export.
- Human review warning and confirmation before destructive draft deletion.

## Not implemented / needs real integration
- No automatic authoritative citation validation by default. Add and test a licensed/official case-law and legislation data source before showing "verified".
- No authentication, multi-user permissions, encryption-at-rest or production deployment hardening.
- Style adaptation extracts a lightweight profile; it does not train or fine-tune a model.
- Browser voice support varies by browser and may require a network speech service.
- Legal analysis is not legal advice. All facts, authorities, deadlines and procedural rules require human verification.

## Structure
```text
backend/
  app/main.py
  app/skills/registry.py
  requirements.txt
  .env.example
frontend/
  index.html
  package.json
  vite.config.ts
  tsconfig.json
  src/main.tsx
  src/App.tsx
  src/styles.css
  src/lib/api.ts
```


## Feature update (October 2026)
- Expanded Skills Library to 70 workflows based on the supplied DraftMate feature specification. These use a shared guarded local-model engine and are template-driven; they are not 70 independently trained agents.
- Prompt Strength meter and Improve Prompt action. If Ollama is unavailable, prompt improvement uses a clearly labelled local template fallback.
- Export current editable content as DOCX, Markdown, TXT or structured JSON.
- `/api/models` reports models installed in the local Ollama server.
- Citation detection remains pattern-based only; no citation is claimed verified without source-level lookup.

## Current limitations
This update does not implement every proposed item in the specification. PDF export, OCR for scanned documents, a true legal-source verification pipeline, genuine Word tracked changes, collaborative matters, full document manager, streaming, token accounting, voice command confirmation, and robust version/audit history still require separate implementation and testing. Browser voice dictation remains dependent on browser support.

## Document formatting and voice reading update
- Generated output now opens in a formatted document preview. Markdown-style `**bold**` and `__bold__` emphasis is rendered as bold text rather than showing the asterisks. Use **Edit source** to edit the raw draft and **Preview formatting** to switch back.
- Read Aloud strips Markdown formatting markers, heading markers, list markers, and link URLs before speech synthesis, so it does not pronounce asterisks as “asterisk”. It uses an `en-IN` voice when available, prefers a matching female-named Indian English voice when the OS exposes one, and uses a 0.95 speech rate. Commas and semicolons are normalized to natural pauses; sentence punctuation is retained for sentence breaks.
- Voice selection depends on voices installed and exposed by Windows/Electron. If Windows does not expose an Indian English female voice, speech synthesis will fall back to the available voice; the application cannot create a missing voice by selecting a locale.
