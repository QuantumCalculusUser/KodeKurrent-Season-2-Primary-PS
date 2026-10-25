# DraftMate original website: GitHub deployment

This package preserves the original DraftMate website frontend and backend source files from the supplied project. No redesign or replacement UI was applied. Deployment support files (`Dockerfile`, `render.yaml`, `.gitignore`, this README) were added.

## Deploy
1. Upload the contents of this folder to the root of a GitHub repository.
2. Open Render and select **New → Blueprint**, then connect the repository.
3. When asked for `GEMINI_API_KEY`, enter a newly generated Gemini API key in Render's environment settings. Do not put the key in source code or GitHub.
4. Verify `GEMINI_MODEL` is a model currently available to your Google AI Studio API key. The included default is `gemini-3.8-flash` because that name appeared in the earlier project error; change it in Render if Google no longer offers it to your account.
5. Deploy and open the HTTPS URL from Render.

GitHub Pages alone cannot run this Python backend; use a backend host such as Render. The desktop app source remains included but is not used by the hosted web deployment. The deployed site serves the original `frontend-web` interface.

## Privacy
The local `draftmate.db` was intentionally excluded from the GitHub package so personal drafts are not accidentally published. A fresh runtime database is created on the host. Add authentication before exposing legal drafting to the public. Revoke any API key previously shared in chat and use a replacement.
