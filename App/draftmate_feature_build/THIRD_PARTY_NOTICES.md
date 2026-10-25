# Third-party project notes

DraftMate now includes a **docassemble-inspired interview package** at `docassemble_package/data/indian_legal_notice.yml` and a native local assembly endpoint. The desktop app does not bundle or claim to run the complete docassemble server. The YAML file is a starting interview adaptation and must be validated in an actual docassemble installation before being distributed as a runnable docassemble package.

Primary project reference: [jhpyle/docassemble](https://github.com/jhpyle/docassemble), MIT License. If code or substantial content from upstream is copied into a distribution, include the upstream copyright and full MIT license text. This upgrade uses the interview/document-assembly pattern; it does not vendor docassemble source code.

Complementary sources identified in the supplied research note include `RohasNagpal/legal-ai-skills` (prompt/skill patterns), `Shlok926/rtiassist-api` (structured form-to-draft flow), and `Wolfgangrush/indian-contracts-drafting-litigation` (clause references). Their contents and current license files must be checked directly before copying any code or text. The supplied report itself notes those repositories had not been opened. Do not treat its file/path descriptions as verified.

The DOCX endpoint uses `python-docx`, whose license and bundled dependency notices should be included from the installed package metadata when packaging. No LexNLP/AGPL code is included.

All generated legal notices are drafts. The application does not independently verify statutes, cases, limitation periods, jurisdiction, or service rules. Review with a qualified Indian advocate before use.
