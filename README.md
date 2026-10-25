# DraftMate AI — Legal Drafting Studio
### KodeKurrent Season 2 · Primary Problem Statement

<p align="center">
  <strong>Draft smarter. Review carefully. Keep humans in control.</strong>
</p>

DraftMate AI is an AI-assisted legal drafting workspace designed to help users prepare, refine, organize, and export legal documents from a single interface. The project combines a web experience with an app build so the same core product concept can be accessed through either route.

- **Repository:** [QuantumCalculusUser/KodeKurrent-Season-2-Primary-PS](https://github.com/QuantumCalculusUser/KodeKurrent-Season-2-Primary-PS)
- **Hosted website:** [Open DraftMate AI](https://kodekurrent-season-2-primary-ps.onrender.com/)
- **Project context:** KodeKurrent Season 2, Primary Problem Statement
- **License:** MIT (see [`LICENSE`](LICENSE))

> **Important:** DraftMate AI is a drafting and research-support tool, not a lawyer and not a substitute for legal advice. A qualified person must review the facts, legal authorities, deadlines, jurisdiction, and final document before it is used.

---

## Contents

- [Why we built it](#why-we-built-it)
- [Inspiration and design direction](#inspiration-and-design-direction)
- [What it can do](#what-it-can-do)
- [How it works](#how-it-works)
- [Architecture and project layout](#architecture-and-project-layout)
- [Requirements](#requirements)
- [Run the web project locally](#run-the-web-project-locally)
- [Run the AI backend](#run-the-ai-backend)
- [Run the website and backend together](#run-the-website-and-backend-together)
- [Use the hosted website](#use-the-hosted-website)
- [App build](#app-build)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Security and privacy notes](#security-and-privacy-notes)
- [Known limitations](#known-limitations)
- [Roadmap ideas](#roadmap-ideas)
- [Contributing](#contributing)
- [Credits](#credits)

---

## Why we built it

Legal documents can be difficult to start from a blank page. Users may need to work out which type of document they need, provide relevant facts, organize supporting material, and then check whether the draft is clear and complete.

DraftMate AI aims to make that workflow more approachable by bringing common drafting workflows, document input, AI-assisted text generation, and export tools into one workspace. It is intended to help users produce a **first draft** more efficiently while keeping human review central to the process.

## Inspiration and design direction

The project brings together three ideas:

1. **A legal drafting desk:** common document workflows should be easy to find and use without needing to know how the underlying code works.
2. **An editorial, magazine-like interface:** the design direction discussed during development draws inspiration from the strong typography, hierarchy, readable long-form layouts, and high-contrast visual language of publications such as *The New Yorker* and *Bloomberg Businessweek*. This is a design reference, not an affiliation or endorsement.
3. **Local-first AI experimentation:** using [Ollama](https://ollama.com/) makes it possible to run a supported language model on the user's own machine rather than requiring a paid hosted-model API for the main local-generation path.

The product is an original implementation for this project. Inspiration informs the interaction and visual direction; it does not mean the project reproduces another product's source code or claims a partnership with those publications or tools.

## What it can do

The feature set depends on the version and configuration you run. The repository's current prototype documents the following capabilities.

### Drafting workflows

A modular skill registry routes common tasks to suitable drafting instructions and templates. Document workflows include:

- Legal notices
- Contracts and agreements
- Petitions and applications
- Clause review
- Redline-style review support
- Legal research briefs
- Case analysis
- Due-diligence support
- Document summaries

The October 2026 feature update describes an expanded library of 70 workflows. These are template- and prompt-driven workflows sharing a common local-model engine, **not 70 separately trained AI agents**.

### Document input and output

- Upload and extract text from supported PDF, DOCX, TXT, and Markdown files, subject to application size limits.
- Extract a lightweight style profile from user-provided reference material, including structure, tone signals, headings, and recurring phrases.
- Edit generated content in the workspace.
- Export supported content as DOCX, Markdown, TXT, or structured JSON.
- Keep draft history in a local SQLite database in the documented prototype.

Style profiling is a lightweight extraction step. It does not train or fine-tune a model on a user's writing.

### AI assistance

- Send drafting prompts to a locally running model through Ollama.
- Use a prompt-strength indicator and an “Improve Prompt” action where available.
- Use clearly labelled template fallbacks for selected functions when the local model is unavailable.
- Inspect installed Ollama models through the backend's `/api/models` endpoint.

### Voice input

Where supported by the browser, voice dictation uses the browser Web Speech API. Availability and behavior depend on the browser and its speech-recognition implementation. Text input remains the fallback.

### Citation handling

The prototype can detect citation-like patterns and structure evidence records. **Pattern detection is not legal verification.** Unless a properly configured authoritative legal-source integration has actually checked a citation, it must be treated as unverified.

---

## How it works

At a high level, the application follows this flow:

1. **Choose a task.** The user selects a drafting or review workflow.
2. **Provide context.** The user enters facts and instructions, and may upload a supported reference document.
3. **Prepare the request.** The frontend sends the request to the backend API.
4. **Select a workflow.** The backend uses the skill registry and shared drafting logic to assemble the appropriate instructions and context.
5. **Generate or fall back.** When configured and available, the backend sends the request to the Ollama model. Some features can use an explicitly labelled template fallback.
6. **Review and edit.** The user checks the generated text, corrects facts, and makes revisions.
7. **Export.** The user exports the supported output format for further review or use.

```text
User
  |
  v
Web UI / App interface
  |
  | HTTP requests (/api/...)
  v
FastAPI backend
  |
  +--> Skill registry and drafting instructions
  |
  +--> Document extraction and style-profile utilities
  |
  +--> Ollama local language model (when configured)
  |
  +--> SQLite draft history and export utilities
  |
  v
Draft returned to the interface for human review
```

This is a conceptual flow of the documented prototype, not a guarantee that every feature is enabled in every deployment.

## Architecture and project layout

The repository contains separate **App** and **Website** directories. The root README also documents the rebuilt prototype's backend and frontend layout. Exact files may differ between packaged app builds and the web development source.

The documented source layout is:

```text
KodeKurrent-Season-2-Primary-PS/
├── App/
│   └── draftmate_feature_build/   # App build / app-related project files
├── Website/                       # Website project files
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI application entry point
│   │   └── skills/
│   │       └── registry.py        # Workflow / skill registry
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Example local configuration
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Main React interface
│   │   ├── main.tsx               # Frontend entry point
│   │   ├── styles.css             # Global styles
│   │   └── lib/
│   │       └── api.ts             # API client
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── .gitignore
├── LICENSE
└── README.md
```

> **Folder-layout note:** This is the layout described by the current prototype documentation. If your checked-out revision nests the backend/frontend inside `Website/` or `App/draftmate_feature_build/`, run commands from the directory that actually contains the relevant `requirements.txt`, `package.json`, or `app/main.py`. Do not create duplicate folders just to match this illustration.

### Main technologies

| Component | Technology | Purpose |
|---|---|---|
| Web UI | React + TypeScript | Interactive drafting interface |
| Frontend tooling | Vite + Node.js/npm | Local development and frontend build |
| Backend API | Python + FastAPI | Receives requests and runs application workflows |
| API server | Uvicorn | Runs the FastAPI application |
| Local model runtime | Ollama | Runs a supported language model locally |
| Draft history | SQLite | Stores prototype draft history |
| Document processing | Python libraries from `requirements.txt` | Extracts supported document content |
| Hosting | Render for the published website | Hosts the deployed web experience |

The app packaging technology may differ from the web stack. Check the files inside `App/draftmate_feature_build/` for its exact launch or build instructions.

---

## Requirements

### Required for local development

- **Git** to clone the repository.
- **Python 3.10 or newer** for the documented backend.
- **Node.js 20 or newer** and npm for the documented React/Vite frontend.
- A terminal such as Windows PowerShell, Command Prompt, macOS Terminal, or a Linux shell.
- Internet access for the initial dependency installation.

### Recommended for AI generation

- **Ollama**, installed from [ollama.com](https://ollama.com/).
- A model downloaded through Ollama. The repository's existing setup example uses `qwen2.5:7b`; you may use another compatible model by changing `OLLAMA_MODEL` to the exact installed model name.
- Enough RAM and disk space for the model you choose. A 7B model can require several gigabytes of memory and storage; performance depends on your hardware and quantization.

Ollama is optional for template-only mode, but real model-based generation requires a working local model runtime unless the code has been deliberately configured to use another provider.

---

## Run the web project locally

### 1. Download the repository

```bash
git clone https://github.com/QuantumCalculusUser/KodeKurrent-Season-2-Primary-PS.git
cd KodeKurrent-Season-2-Primary-PS
```

### 2. Find the source directories

Check the repository's current layout before running commands. Open the repository in VS Code if helpful:

```bash
code .
```

Look for the directory containing `requirements.txt` and `app/main.py` for the backend, and the directory containing `package.json` and `vite.config.ts` for the frontend. In the documented prototype, these are `backend/` and `frontend/`.

### 3. Install frontend dependencies

Open a terminal in the directory containing the frontend's `package.json`:

```bash
npm install
```

### 4. Start the frontend

In that same frontend directory:

```bash
npm run dev
```

Vite normally prints a local URL such as `http://localhost:5173`. Open the exact URL printed in your terminal.

The frontend is configured to proxy `/api` requests to the FastAPI backend in development. The backend must therefore be running for API-powered features to work.

---

## Run the AI backend

Use a **second terminal**.

### 1. Enter the backend directory

In the documented layout:

```bash
cd backend
```

If the backend is nested inside another folder in your checkout, change to that actual directory instead.

### 2. Create and activate a Python virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example configuration if the repository contains `.env.example`.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Open `.env` and review the available settings. For local model generation, set `OLLAMA_MODEL` to a model that is actually installed on your computer. Do not paste private credentials into source files or commit your `.env`.

### 5. Install and start Ollama

Install Ollama from [https://ollama.com/](https://ollama.com/).

Then download the example model:

```bash
ollama pull qwen2.5:7b
```

Make sure Ollama is running. Depending on the operating system and installation, it may start automatically. If it does not, open another terminal and run:

```bash
ollama serve
```

If you selected a different model, update `OLLAMA_MODEL` in the backend `.env` to match the installed model name.

### 6. Start FastAPI

From the backend directory, with the virtual environment activated:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend should be available at:

- API base: `http://127.0.0.1:8000`
- Interactive API documentation, if enabled: `http://127.0.0.1:8000/docs`
- Installed Ollama models endpoint: `http://127.0.0.1:8000/api/models`

Keep this terminal open while using the application.

### 7. Open the frontend

Return to the frontend terminal and open the Vite URL printed by `npm run dev` (normally `http://localhost:5173`).

You should now have both services running:

| Service | Typical local address |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://127.0.0.1:8000` |
| API docs | `http://127.0.0.1:8000/docs` |

If the frontend uses a different port or the API documentation route is disabled, use the address shown by the running service and the configuration in the checked-out source.

---

## Run the website and backend together

The project uses two development processes in the documented setup:

1. **Terminal 1:** start the backend and, if necessary, Ollama.
2. **Terminal 2:** start the frontend.

Start the backend first if you want to test AI features immediately. Starting only the frontend may show the interface, but API-dependent actions will fail until the backend is available.

### Quick-start checklist

- [ ] Git clone completed.
- [ ] Python virtual environment created and activated.
- [ ] `pip install -r requirements.txt` completed successfully.
- [ ] Frontend `npm install` completed successfully.
- [ ] `.env` reviewed and `OLLAMA_MODEL` matches an installed model.
- [ ] Ollama is running and the model has been downloaded.
- [ ] Backend starts on port `8000`.
- [ ] Frontend starts and its local URL opens.
- [ ] A small test prompt works before trying large documents.

---

## Use the hosted website

You can open the deployed website without installing Python, Node.js, or Ollama locally:

**[https://kodekurrent-season-2-primary-ps.onrender.com/](https://kodekurrent-season-2-primary-ps.onrender.com/)**

Deployment behavior depends on the current hosting configuration. A hosted interface does not automatically mean every local-model feature is available in production. If a hosted feature reports that the backend or model is unavailable, it may not be configured on the deployment.

Free hosting instances may sleep after periods of inactivity, so the first request after a quiet period can take longer. If the site is down, check the repository's deployment configuration and the hosting service's logs.

---

## App build

The repository includes an app-related directory at `App/draftmate_feature_build/`. Use that directory for the packaged or app-specific version.

Because the exact packaging files can change between revisions, first inspect the directory for a `README`, `package.json`, `pyproject.toml`, `requirements.txt`, `*.spec`, installer script, or other build instructions. Follow the instructions matching the files actually present rather than assuming the app is an Electron, Tauri, or PyInstaller application.

If the app uses the same backend, start or configure that backend according to the previous section. If the app bundles its own backend or serves its own frontend, follow its included launcher and configuration instead. The app and hosted website may look alike while using different startup paths.

---

## Configuration

### Ollama model

The documented example uses:

```env
OLLAMA_MODEL=qwen2.5:7b
```

This is an example setting, not a requirement to use that exact model. Choose a model supported by your installed Ollama version and hardware, download it, and ensure the environment variable matches its name.

### Ports and API URLs

- The backend example uses port `8000`.
- Vite normally uses port `5173`.
- If you change a port, update the frontend's API proxy or API base URL as appropriate.

Review `vite.config.ts` and the frontend API client (documented as `src/lib/api.ts`) if the UI cannot connect to the backend.

### Secrets

Never commit API keys, access tokens, passwords, or private `.env` files. Keep `.env.example` limited to placeholder values and variable names.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'uvicorn'`

Activate the backend virtual environment and install dependencies from the backend directory:

```bash
python -m pip install -r requirements.txt
python -m pip install uvicorn
```

Then run:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Using `python -m pip` helps ensure packages are installed into the same Python environment used to start the server.

### `uvicorn` cannot import `app.main`

- Make sure the terminal is in the backend directory containing the `app/` package.
- Confirm that `app/main.py` exists in your checked-out revision.
- Activate the virtual environment and reinstall requirements.
- Use the entry-point documented by the actual source tree if it differs from `app.main:app`.

### The frontend loads but AI actions fail

- Check that the backend is running on port `8000`.
- Look for API errors in the browser developer console and backend terminal.
- Verify the frontend proxy/API URL.
- Check that Ollama is running and the configured model has been downloaded.
- Check that the model name in `.env` exactly matches an installed model.

### `npm` or `node` is not recognized

Install Node.js 20 or newer from [https://nodejs.org/](https://nodejs.org/), then close and reopen the terminal. Verify with:

```bash
node --version
npm --version
```

### PowerShell refuses to activate the virtual environment

Use Command Prompt and run:

```bat
.venv\Scripts\activate.bat
```

Alternatively, use the Python environment without activation by invoking its Python executable directly.

### Model generation is slow or runs out of memory

Try a smaller Ollama model, close memory-heavy applications, and confirm your machine has enough RAM and disk space. Larger models are not automatically better if your computer cannot run them comfortably.

### Voice input is unavailable

Use a supported browser and allow microphone access. Browser speech recognition is not uniformly supported, and some implementations rely on an online speech service. Text entry should remain the fallback.

### A citation is detected but not verified

That is expected when the app has only detected a citation-like pattern. Do not treat a detected citation, a generated source URL, or a research starting point as confirmation that a case or statute is real, current, or applicable.

---

## Security and privacy notes

- Treat uploaded legal documents as confidential. Only use deployment environments and machines appropriate for the sensitivity of the material.
- Do not put secrets in source control or screenshots.
- Review what data the selected local model runtime, browser speech service, and hosting provider may process before using confidential information.
- Do not rely on generated legal text without checking facts, names, dates, jurisdiction, legal authorities, limitation periods, and procedural rules.
- Review a document before exporting or sharing it. Use the application's deletion confirmation where available.

The documented prototype does not claim production-grade authentication, multi-user authorization, encryption-at-rest, or comprehensive deployment hardening.

## Known limitations

The current prototype documentation identifies the following limitations or work that requires additional integration and testing:

- No default authoritative case-law or legislation lookup pipeline; citations are not verified automatically.
- No authentication or multi-user permission system in the documented prototype.
- No claimed encryption-at-rest or production security hardening.
- Style-profile extraction is not model training or fine-tuning.
- Voice dictation depends on browser support and may depend on a network speech service.
- PDF export, OCR for scanned documents, genuine Microsoft Word tracked changes, collaborative matters, a full document manager, streaming generation, token accounting, voice-command confirmation, and robust version/audit history are not established as implemented features in the documented update.

Feature availability can change. Check the source code and test a feature before presenting it as production-ready.

## Roadmap ideas

Possible future improvements include:

- Connect an authoritative, appropriately licensed legal-source provider and build a verifiable citation workflow.
- Add document-level permissions, authentication, and secure storage.
- Add OCR for scanned PDFs and improve extraction quality for complex layouts.
- Add robust document versioning, audit history, and collaboration controls.
- Improve test coverage, error messages, accessibility, and installation automation.
- Add integration and deployment tests so the website and app remain consistent.

These are proposed directions, not promises that the features already exist.

## Contributing

Contributions and bug reports are welcome.

1. Fork the repository.
2. Create a focused branch for your change.
3. Make the change and test the affected workflow.
4. Keep secrets, private legal documents, and generated local data out of commits.
5. Submit a pull request describing the problem, the change, and the tests performed.

For bugs, include the operating system, Python and Node versions, relevant terminal error messages, and steps to reproduce. Remove private facts and credentials before sharing logs.

## Credits

- **Project:** DraftMate AI / Legal Drafting Studio
- **Challenge context:** KodeKurrent Season 2, Primary Problem Statement
- **Local model runtime:** [Ollama](https://ollama.com/)
- **Frontend development tooling:** [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), and [Vite](https://vite.dev/)
- **Backend framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Visual inspiration:** editorial and magazine-style design systems, including the typography and hierarchy associated with *The New Yorker* and *Bloomberg Businessweek*

All third-party names and trademarks belong to their respective owners. Mention of a tool or publication indicates inspiration or technology usage only and does not imply endorsement.

---

**Built for the KodeKurrent Season 2 challenge.** Draft responsibly, verify independently, and keep a human in the loop.
