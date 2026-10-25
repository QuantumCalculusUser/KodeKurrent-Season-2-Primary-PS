# DraftMate AI — Gemini Website Edition

This package serves DraftMate as a real browser website using the **same visual interface from the supplied website build**, the 77-skill registry, and Google Gemini API on the backend. It is not the Electron desktop shell.

## Local setup (Windows)

1. Install Python 3.11+ and Node.js 20+.
2. Copy `backend/.env.example` to `backend/.env` if an example file is available in your source checkout. This package intentionally excludes private `.env` files and credentials.
3. Put your own `GEMINI_API_KEY` in `backend/.env`; never place it in frontend files or commit it.
4. From the repository root, run `RUN_DRAFTMATE_WEB.bat`. On first run it installs dependencies and builds the web frontend. The browser should open at `http://127.0.0.1:8000`.
5. Keep the terminal window open while using the website.

If the launcher does not load environment variables, start the backend with the working directory set to `backend` or configure `GEMINI_API_KEY` in the shell environment before starting it.

## Deploy to Render

1. Push the contents of this package to a GitHub repository.
2. In Render, create a Blueprint using the included `render.yaml` or a Docker web service using the included `Dockerfile`.
3. Add `GEMINI_API_KEY` as a secret environment variable. Confirm `GEMINI_MODEL` is supported by your Google AI Studio/API project; change the default in `render.yaml` if necessary.
4. Deploy and verify `/api/health`, then create a small test draft.

## Important

- `frontend-web/` is the browser website UI.
- `backend/app/web_main.py` is the website API entry point and calls Gemini server-side.
- `backend/app/skills/registry.py` contains 77 skill definitions.
- API keys, local databases, `.venv`, and `node_modules` are intentionally excluded.
- The model is not fine-tuned by this package. The 77 workflows are prompt/skill definitions.
- Legal output is a draft, not a verified legal opinion. Check current law, facts, court rules, citations, and jurisdiction before use.
- Before making the website public, add authentication, authorization, rate limits, secure storage, and a privacy review. Legal data can be sensitive.
