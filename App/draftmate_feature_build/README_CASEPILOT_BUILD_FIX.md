# CasePilot frontend build fix

This patch fixes the CasePilot upgrade build issue in `frontend/src/App.tsx`:

- Removes a duplicated block of React, icon, API, and JSON-catalog imports.
- Adds the missing `draftFromCase()` handler used by the CasePilot button. It posts the case narrative to `/api/case/draft`, applies the returned skill/title/content, and opens the generated document in the existing Drafting desk.

## Install

1. Close DraftMate.
2. Extract this ZIP to a new folder (do not merge it over a running copy).
3. Run `RUN_DRAFTMATE.bat`.
4. If you want to patch an existing source folder instead, replace `frontend/src/App.tsx` with the version from this ZIP.

The App.tsx file passes a TypeScript transpilation syntax check. A full dependency-backed production build could not be run in the packaging environment, so the first Windows build still depends on `npm install` completing successfully.
