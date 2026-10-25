# CasePilot Upgrade

CasePilot is the new voice-first case-intake workflow in DraftMate AI.

## What changed
- Added a CasePilot entry card to the home / Drafting desk screen and a dedicated **Case listener** workspace page.
- Reuses the existing microphone capture and speech output workflow. Speech transcription uses the locally executed Whisper Tiny model through `@huggingface/transformers`; the first run needs an internet connection to cache the model. Audio transcription runs in the app rather than being sent to a hosted speech API.
- Added `POST /api/case/draft`, which classifies a case narrative into a supported drafting skill, then calls the existing local Ollama drafting workflow with that skill.
- Added heuristic routing as a fallback when the local Ollama classifier is unavailable or returns invalid data.
- Routes the generated content back to the existing editable drafting desk and carries across the selected skill and case narrative.
- Adds safeguards to mark missing facts with placeholders and require human legal review.

## Try it
1. Start Ollama and confirm the model configured in `backend/.env` is installed.
2. Run `RUN_DRAFTMATE.bat` as usual.
3. On the home screen, select **CasePilot · Tell the case, get the right draft**.
4. Type case facts or select **Dictate case details**. Stop recording or pause for four seconds after speaking.
5. Select **Identify type & draft automatically**. DraftMate chooses a workflow, drafts, and opens the result in the existing editable Drafting desk.

## Important limitations
- Speech model weights may be downloaded and cached on first use; they are not bundled into this source archive.
- Automatic routing is a best-effort classification. Review the chosen instrument before relying on the output.
- If Ollama is unavailable, the backend may return its safe template fallback instead of an AI-generated draft. The interface reports the generation mode/warning.
- Drafts are working drafts, not legal advice. Verify facts, evidence, deadlines, forum, and authorities with qualified counsel.
