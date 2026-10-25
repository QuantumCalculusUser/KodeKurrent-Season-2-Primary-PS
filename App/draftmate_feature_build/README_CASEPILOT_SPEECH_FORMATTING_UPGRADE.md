# CasePilot Speech Accuracy + Document Formatting Upgrade

This update improves the Case Listener workflow in three places:

## 1. Better speech recognition
- Replaces Whisper Tiny with multilingual `onnx-community/whisper-small` quantized to Q8 for better recognition of longer and accented speech.
- Uses longer audio chunks with overlap to reduce missed words around chunk boundaries.
- The first use downloads a larger model and may take longer. It is cached for later use. A network connection is required for that first download unless the model is already cached.

## 2. Conservative local transcript cleanup
- After Whisper transcribes speech, the app sends the transcript to the configured local Ollama model at the local endpoint for conservative spelling and punctuation cleanup.
- The cleanup prompt explicitly forbids changing facts, names, amounts, dates, negations, uncertainty, or requested remedies.
- If Ollama is unavailable, the raw Whisper transcript is retained.
- Users must still verify names, dates, money amounts and negations against the recording; no automatic transcript correction can guarantee perfect accuracy.

## 3. More consistent draft formatting
- Adds a deterministic Markdown normalization pass for generated drafts.
- Strengthens the drafting prompt to request consistent headings, paragraph spacing, clause numbering, and valid Markdown tables.
- The document preview now renders Markdown tables, horizontal rules, blockquotes, headings and lists more cleanly.
- DOCX export converts Markdown tables into actual Word tables instead of displaying pipe characters as plain text.

## Install
1. Close DraftMate.
2. Extract this project ZIP into a new folder.
3. Run `RUN_DRAFTMATE.bat` from that folder.
4. On the first dictation, allow the Whisper Small model to download and finish loading. Speak in short, clear sentences and pause between sections.
5. Check the transcript before generating a legal draft. Verify all names, dates, amounts, and negations against what was said.

## Verification performed
- Python backend syntax compilation passed.
- TypeScript/JSX transpilation syntax check passed.
- Markdown normalizer smoke test passed.
- A full dependency-backed frontend production build and live Ollama transcription test were not available in this packaging environment.
