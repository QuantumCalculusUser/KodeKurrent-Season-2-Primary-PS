# DraftMate Website Edition: Gemini API setup

This website edition uses Google Gemini API for prompt improvement, case classification,
speech transcript cleanup, and draft generation. It does not call Ollama. The separate
desktop application is not changed by this website-only package.

## Important key safety
The API key previously pasted into chat should be treated as exposed. Revoke it in Google AI Studio
and create a replacement key before using this website. Do not commit the key to Git or put it in
frontend files.

## Configure
1. Open `backend/.env.example`.
2. Copy it to `backend/.env`.
3. Replace `replace_with_a_new_rotated_key` with your replacement Gemini API key.
4. Keep `GEMINI_MODEL=gemini-3.8-flash` unless your account uses a different available model.
5. Run `RUN_DRAFTMATE_WEB.bat`.

The backend reads the key from `backend/.env`. The browser never receives the key. The first run
requires internet access. Gemini usage is subject to Google API quotas, billing/limits, and Google's
data handling terms. Avoid submitting confidential client data unless your usage terms and client
confidentiality obligations permit it.

If the API key is missing or invalid, `/api/health` reports that configuration is missing and draft
generation falls back to a clearly labelled starter template; it does not silently claim Gemini wrote it.

## Desktop app isolation
The desktop app continues to use `backend/app/main.py` and `frontend/`. The website launcher builds
`frontend-web/` and starts `backend/app/web_main.py`. This Gemini configuration applies only to the website.


## Troubleshooting: "Template fallback used; Gemini request failed"
- Run `SETUP_GEMINI_KEY.bat` and verify `backend/.env` contains `GEMINI_API_KEY=your_new_key` (no quotes needed).
- The API key that was previously pasted in chat must be revoked; use a newly generated key.
- Fully close the old API console and restart `RUN_DRAFTMATE_WEB.bat`. Environment variables are read at backend startup.
- The backend now loads `backend/.env` by an absolute path and shows a short diagnostic message, such as a missing key, HTTP 400/403/429, model access issue, or timeout.
- Open `http://127.0.0.1:8000/api/health`. `api_key_configured` should be `true`, and `env_file_found` should be `true`. This confirms configuration is loaded, not that Google's API is reachable.


## Model 404 fix
The website default has been changed to `gemini-3.8-flash`, matching the model name in the API error screenshot. If your Google AI Studio account does not expose that model, set `GEMINI_MODEL` in `backend/.env` to a currently available model from your account, then fully restart the website backend.
