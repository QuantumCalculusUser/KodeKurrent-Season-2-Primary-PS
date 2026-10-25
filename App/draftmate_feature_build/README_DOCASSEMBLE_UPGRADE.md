# DraftMate legal notice upgrade

## Included
- Docassemble-inspired interview schema at `GET /api/legal-notice/interview`.
- Structured DOCX assembly at `POST /api/legal-notice/assemble`.
- Bundled editable YAML interview draft at `docassemble_package/data/indian_legal_notice.yml`.
- Indian-style notice layout with advocate header, recipient block, facts, demand, optional amount/legal basis/evidence, delivery method, signature and human-review warning.
- Required-field validation before assembly; missing fields return HTTP 422 with a list of missing labels.
- Keeps existing local Ollama drafting, React/Electron UI, and existing DOCX/TXT/MD/JSON exports intact.

## API quick test
Run the backend using the existing `RUN_DRAFTMATE.bat` setup, then open `http://127.0.0.1:8000/docs` and test `GET /api/legal-notice/interview`. For assembly, send JSON to `POST /api/legal-notice/assemble` with `notice_type`, `client_name`, `recipient_name`, `recipient_address`, `facts`, `demand`, `delivery_method`, and `notice_date`. Optional fields: `advocate_name`, `advocate_address`, `amount`, `deadline`, `legal_basis`, `evidence`.

This is a local, docassemble-inspired implementation rather than the full docassemble server. The YAML interview is a draft reference and should be validated against a real docassemble runtime before claiming it runs there. Legal templates need advocate review; do not rely on generated legal deadlines or citations without independent verification.
