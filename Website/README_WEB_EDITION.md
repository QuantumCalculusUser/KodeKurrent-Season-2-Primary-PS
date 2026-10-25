# DraftMate AI — Website Edition

This edition runs DraftMate in your browser instead of opening an Electron desktop window. It retains the React interface and FastAPI backend, and uses your configured local Ollama model.

## Run on Windows

1. Install Node.js LTS and Python 3.11+ if not already installed.
2. Make sure Ollama is running and your configured model is available (default: `qwen2.5:7b`).
3. Double-click `RUN_DRAFTMATE_WEB.bat`.
4. On first run, the script installs dependencies and builds the frontend. This can take several minutes and requires an internet connection for package downloads.
5. Your browser opens `http://127.0.0.1:8000`.
6. Keep the API command window open while using the site. Close it to stop the local website.

## What “website” means here

This is a browser-based local website. The interface opens in Chrome/Edge, but the API, draft database, and Ollama model remain on your computer. It does not upload legal facts to a hosted AI provider by default, and it is not publicly accessible from the internet.

To make it publicly available to other people, you would need a server/hosting provider, a deployed backend and model strategy, HTTPS, authentication, access controls, secure database storage, rate limiting, and a privacy/security review. Do not expose this local development server directly to the internet.

## Troubleshooting

- **Port 8000 is already in use:** close any old DraftMate backend command window, then run the launcher again.
- **Ollama unavailable:** start Ollama and check that the configured model is installed. The website can load even if generation cannot yet run.
- **Build error:** capture the first compiler error shown above `Website build failed`, not just the final summary.
- **Voice input:** browser speech recognition support varies by browser and may use the browser's speech service. Check the transcript before drafting.

## Included functionality

The existing DraftMate React UI and FastAPI endpoints are retained, including CasePilot, skills, draft history, exports and local Ollama integration. This packaging change adds a dedicated browser launcher and production static serving; it does not claim that every feature has been tested end-to-end on every machine.


## Gemini API configuration
This website-only edition uses Google Gemini and does not require Ollama. Before launch, copy `backend/.env.example` to `backend/.env`, add a newly rotated `GEMINI_API_KEY`, and see `README_GEMINI_WEBSITE_SETUP.md`. The separate desktop app is not modified.
