# CasePilot Speed Upgrade

This update reduces avoidable Ollama work during automatic drafting.

## Changes
- Clear case narratives matched by the local rules skip the separate LLM classification request and proceed directly to drafting.
- Ambiguous narratives still use a short classification request before drafting.
- Ollama is asked to keep the selected model loaded for 15 minutes, reducing repeated model reload delays.
- Draft generation uses a 6,144-token context and a 3,072-token output ceiling to reduce unnecessarily long generations while retaining room for a substantial first draft.
- Ambiguous classification uses a smaller context and a short output budget.

## Notes
- Actual speed depends on the installed Ollama model, prompt length, GPU offload, and whether the model is already loaded.
- A first model load can still take time.
- The local heuristic can choose the wrong skill for an unusual narrative; check the selected skill and generated draft.
- Output-token limits may make unusually long instruments incomplete. Review the end of every draft before use.
