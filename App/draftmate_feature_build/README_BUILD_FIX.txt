DraftMate AI - Build and Voice Fix

This patch fixes the frontend TypeScript errors reported in the startup log:
- Defines speakText() for automatic AI read-aloud and the Read aloud button.
- Corrects malformed escaped regular expressions in speechFriendlyText().
- Keeps showFormatted state for the formatted-preview / edit-source toggle.
- Cleans Markdown markers before speech and prefers an installed en-IN voice when available.
- Uses punctuation and paragraph breaks to preserve natural speech phrasing.

Install/run:
1. Extract this ZIP into a new folder.
2. Open draftmate_feature_build/frontend in a terminal.
3. Run npm install if dependencies are missing.
4. Run npm run build.
5. Start DraftMate using the included Windows launcher/instructions.

Note: speechSynthesis voices are provided by the operating system/runtime. The app prefers an installed Indian English voice, but voice gender and quality depend on the voices installed on Windows. A full build could not be verified in this environment because frontend dependencies (React and lucide-react) are not present and network installation is unavailable.
