# DraftMate Skill Reference Gallery and Output Format Update

## Included

- `SKILL_VISUAL_REFERENCE_CATALOG.json`: 77 skill entries, each with 10 topic-specific image-search references (770 total).
- `SKILL_VISUAL_REFERENCE_CATALOG.html`: standalone catalog index for browsing the same references.
- Skills Library UI: search the 77 catalog entries, open a skill's ten-reference gallery, and open image results in a browser.
- Output contract appended to drafting prompts: main deliverable, structured sections, assumptions, missing information, sources/citation status, review checklist, clean Markdown, and legal human-review reminder. It directs output to adapt to the skill type rather than force every task into a legal-document layout.

## Reference sourcing and limitations

The gallery searches public web image results using topic-specific queries. It loads preview thumbnails from Bing's image thumbnail service and links each tile to the associated image-search result page. Search results can change and the original publisher may apply copyright or other reuse conditions. Inspect each original source and licence before copying an image into a distributed application or document. The references are not bundled for offline use and are not presented as legal authorities.

Useful public legal-template sources discovered during implementation:

- Startup India templates: https://www.startupindia.gov.in/content/sih/en/reources/templates.html
- LawRato legal documents: https://lawrato.com/legal-documents
- Legitify drafting templates: https://www.legitimate.co.in/drafting-templates
- ClearTLC document formats: https://www.cleartlc.com/documents

These sources provide examples for document structure, but each source's terms and each document's legal applicability should be checked before reuse. No full documents or images from those sites are bundled into this package.

## Run and build

Extract the project and use the existing `RUN_DRAFTMATE.bat` and `build_windows.bat` workflows. The frontend dependencies must be installed before a complete build can be verified. Existing local Ollama drafting remains the generation engine; the gallery does not require a paid AI API.
