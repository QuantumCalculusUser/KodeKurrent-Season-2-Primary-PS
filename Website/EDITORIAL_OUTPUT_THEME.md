# DraftMate Editorial Output Theme

## Visual direction
- Warm ivory paper, ink-black text, restrained terracotta accents, thin rules, editorial serif headings and generous whitespace.
- Analytical outputs lead with executive summary/key findings, then evidence, analysis, action items, assumptions and open items for review.
- Tables for risks, obligations, timelines, comparisons and extracted facts.
- Formal legal instruments preserve conventional legal structure, clause numbering, signatures and court formatting; editorial styling must never compromise filing suitability.

## Implementation
- Updated the local Ollama system prompt in `backend/app/main.py` so all 77 registered skills are asked to follow the same theme while keeping output type-specific.
- `SKILL_VISUAL_REFERENCE_CATALOG.html` contains 10 targeted image-search links per registered skill (770 searches total). `SKILL_VISUAL_REFERENCE_CATALOG.json` contains the structured catalogue. The images are not downloaded or redistributed; links open search results and each source's licence must be checked before reuse.

## Web research used for the design direction
- Clio, *How to Create a Legal Document Template in Word for Lawyers*: https://www.clio.com/resources/ms-word-for-legal-drafting/create-legal-document-template-word/ (emphasises reliable styles, heading hierarchy and template consistency).
- Behance legal-design example: https://www.behance.net/gallery/180586149/Projeto-grafico-e-diagramacao-Legal-design (visual example of more readable legal document design).
- Legale Smart Documents: https://legale.io/docs/smart-documents/ (illustrates a draft-review-customise workflow).

These are design references, not legal authorities.
