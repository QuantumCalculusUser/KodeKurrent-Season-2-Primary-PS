from __future__ import annotations
import os, re, io, json, sqlite3, time, uuid, sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv
from .skills.registry import SKILLS, get_skill, public_skills

load_dotenv()
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
DB_PATH = os.getenv("DATABASE_PATH", "./draftmate.db")
MAX_UPLOAD = int(os.getenv("MAX_UPLOAD_MB", "15")) * 1024 * 1024

app = FastAPI(title="DraftMate AI API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS drafts (
          id TEXT PRIMARY KEY, title TEXT NOT NULL, skill TEXT NOT NULL, content TEXT NOT NULL,
          instruction TEXT NOT NULL, created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL)""")
init_db()

class DraftRequest(BaseModel):
    title: str = Field(default="Untitled legal document", max_length=200)
    instruction: str = Field(min_length=2, max_length=12000)
    skill: str = "legal_notice"
    document: str = Field(default="", max_length=100000)
    references: str = Field(default="", max_length=60000)
    style_profile: str = Field(default="", max_length=8000)
    jurisdiction: str = "India"
    tone: str = "Formal and precise"

class SpeechCleanupRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=12000)

class ReviewRequest(BaseModel):
    document: str = Field(min_length=1, max_length=100000)

class SaveDraftRequest(BaseModel):
    id: Optional[str] = None
    title: str = Field(default="Untitled legal document", max_length=200)
    skill: str = "legal_notice"
    content: str = Field(default="", max_length=100000)
    instruction: str = Field(default="", max_length=12000)

def normalize_draft_markdown(content: str) -> str:
    """Normalize layout without changing legal substance or inventing content."""
    text = (content or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    # Remove a single outer Markdown fence accidentally emitted by some models.
    match = re.fullmatch(r"```(?:markdown|md|text)?\s*\n(.*?)\n```", text, flags=re.I | re.S)
    if match:
        text = match.group(1).strip()
    # Normalize horizontal whitespace and excessive blank lines.
    text = re.sub(r"[ \t]+$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Keep headings separated from neighbouring paragraphs.
    text = re.sub(r"([^\n])\n(#{1,6}\s+)", r"\1\n\n\2", text)
    text = re.sub(r"(#{1,6}\s+[^\n]+)\n(?!\n)", r"\1\n\n", text)
    # Standardize spaces after numbered paragraph markers without changing numbering.
    text = re.sub(r"(?m)^(\s*\d{1,3}[.)])(?=\S)", r"\1 ", text)
    # Ensure Markdown list items are not fused to the preceding paragraph.
    text = re.sub(r"([^\n])\n(?=(?:[-*+]\s+|\d{1,3}[.)]\s+))", r"\1\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"

def fallback(req: DraftRequest) -> str:
    label = get_skill(req.skill).name.upper()
    if req.skill == "summarize" and req.document.strip():
        return f"{label}\n\nSource text supplied:\n{req.document[:5000]}\n\nHUMAN REVIEW\nConfirm that this summary preserves all material obligations, dates, exceptions and defined terms."
    if req.skill in ("clause_review", "redline_review"):
        return f"""{label}

REQUEST
{req.instruction}

TEXT TO REVIEW
{req.document or "[Paste the relevant clause or document.]"} 

REVIEW CHECKLIST
1. Ambiguity and undefined terms
2. Conflicting obligations, dates, and conditions
3. Allocation of liability, remedies, and termination rights
4. Governing law, jurisdiction, notices, and dispute process
5. Missing facts and evidence

PROPOSED NEXT STEP
Confirm the commercial or legal objective and have the proposed wording reviewed by qualified counsel.

No legal authority has been independently verified."""
    return f"""{label}

Jurisdiction: {req.jurisdiction}
Instruction: {req.instruction}

1. PARTIES
[Insert full legal names, legal status, addresses and authority to sign.]

2. BACKGROUND AND PURPOSE
[Insert verified material facts and purpose. Do not state assumptions as facts.]

3. TERMS / MATERIAL FACTS
[Set out agreed facts, scope, obligations, dates, amounts and conditions.]

4. OBLIGATIONS AND TIMELINES
[Specify each responsible party, required action, deadline and evidence of completion.]

5. DISPUTES, GOVERNING LAW AND REMEDIES
[Insert provisions suitable for the transaction and jurisdiction after legal review.]

6. NOTICES
[Insert notice addresses and valid methods of service where appropriate.]

7. EXECUTION
[Insert signature blocks, date, place, witnesses and required formalities.]

OPEN ITEMS FOR HUMAN REVIEW
- Confirm all parties, facts, dates, amounts and supporting documents.
- Confirm applicable law, forum, limitation periods and procedural requirements.
- Verify every statute, case citation and quotation against authoritative sources.
- Replace all placeholders before use.

This is a starter template, not legal advice. No legal authorities have been independently verified."""

@app.get("/api/health")
async def health():
    connected = False
    models = []
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            if r.is_success:
                connected = True
                models = [x.get("name","") for x in r.json().get("models", [])]
    except Exception:
        pass
    return {"ok": True, "ollama_connected": connected, "model": OLLAMA_MODEL, "model_available": OLLAMA_MODEL in models, "available_models": models, "build_id": "casepilot-speech-formatting-2026-10-25", "features": {"case_draft": True, "speech_clean": True, "markdown_normalization": True}}

@app.get("/api/skills")
async def skills():
    return public_skills()

@app.get("/api/models")
async def models():
    """List models actually installed in the local Ollama instance."""
    try:
        async with httpx.AsyncClient(timeout=4) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            r.raise_for_status()
            names = [m.get("name", "") for m in r.json().get("models", []) if m.get("name")]
            return {"models": names, "default": OLLAMA_MODEL, "source": "local Ollama"}
    except Exception:
        return {"models": [], "default": OLLAMA_MODEL, "source": "Ollama unavailable", "warning": "Start Ollama to list installed models."}

@app.post("/api/prompt/improve")
async def improve_prompt(payload: dict):
    original = str(payload.get("instruction", "")).strip()[:12000]
    skill_id = str(payload.get("skill", "legal_notice"))
    jurisdiction = str(payload.get("jurisdiction", "India"))[:120]
    tone = str(payload.get("tone", "Formal and precise"))[:120]
    if len(original) < 2:
        raise HTTPException(400, "Enter a short instruction before improving it.")
    system = "Rewrite the user's legal drafting instruction into a clear task brief. Preserve the user's intent. Do not invent facts, dates, parties, legal authorities, amounts or deadlines. Use explicit placeholders for missing details. Return only the improved instruction, with a short list of needed details if important."
    prompt = f"Skill: {get_skill(skill_id).name}\nJurisdiction: {jurisdiction}\nTone: {tone}\nOriginal instruction: {original}\nMake it specific, structured and safe. Do not fill missing facts."
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(f"{OLLAMA_BASE}/api/chat", json={"model": OLLAMA_MODEL, "stream": False, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}], "options": {"temperature": 0.15, "num_ctx": 4096}})
            r.raise_for_status()
            improved = r.json().get("message", {}).get("content", "").strip()
            if improved:
                return {"original": original, "improved": improved, "mode": "ollama", "model": OLLAMA_MODEL}
    except Exception:
        pass
    improved = (f"Prepare a {get_skill(skill_id).name.lower()} for the jurisdiction of {jurisdiction}.\n\n"
                f"OBJECTIVE AND FACTS\n{original}\n\n"
                f"DRAFTING REQUIREMENTS\n- Tone: {tone}.\n- Use only facts supplied in the instruction and reference materials.\n"
                "- Use clearly marked [PLACEHOLDER: ...] fields for missing parties, dates, amounts, deadlines or other material facts.\n"
                "- Do not invent case citations, statutory text, quotations or procedural requirements.\n"
                "- Structure the output with appropriate headings, numbered clauses and signature/execution blocks where relevant.\n"
                "- Finish with OPEN ITEMS FOR HUMAN REVIEW and identify authorities that require independent verification.")
    return {"original": original, "improved": improved, "mode": "local template", "warning": "Ollama was unavailable; this is a structured prompt template, not AI enhancement."}

@app.post("/api/draft")
async def generate_draft(req: DraftRequest):
    skill = get_skill(req.skill)
    system = f"""You are DraftMate AI, a cautious legal drafting assistant. Your current skill is {skill.name}: {skill.instruction}
Jurisdiction: {req.jurisdiction}. Tone: {req.tone}.

DRAFTMATE EDITORIAL OUTPUT THEME (apply consistently to every skill):
- Visual identity: premium legal-journal / magazine editorial; warm ivory paper, ink-black text, restrained terracotta accents, fine rules, elegant serif-style headings, concise sans-serif labels, generous whitespace, clear hierarchy.
- Output in clean Markdown that renders well in a document preview: one clear title, a short uppercase kicker/category line when useful, descriptive section headings, short readable paragraphs, numbered lists for steps/clauses, and tables for comparisons, risks, timelines, obligations, or extracted data.
- For analytical outputs, lead with an EXECUTIVE SUMMARY or KEY FINDINGS, then evidence, detailed analysis, recommendations/actions, assumptions, and OPEN ITEMS FOR HUMAN REVIEW. Use callout labels such as HIGH RISK, KEY DATE, DECISION REQUIRED only when justified by the content. Do not add decorative emoji or fake citations.
- For legal instruments (contracts, notices, petitions, agreements, replies, NDAs and employment documents), preserve conventional professional legal-document structure, clause numbering, defined terms, formal language, signature blocks and jurisdiction/court formatting. The editorial theme affects typography and hierarchy only; never turn an executable legal instrument into a magazine article or add decorative elements inside operative clauses.
- For student learning outputs, use a clear editorial lesson layout with learning objective, explanation, worked example, common mistake, and recap where relevant. For tables/research outputs, prefer compact, readable tables with meaningful column labels.
- Do not output HTML/CSS instructions or describe the theme; produce the actual styled-by-Markdown content. Use headings and emphasis rather than literal HTML. Avoid raw Markdown markers being doubled or escaped.

FORMATTING RULES: Use Markdown headings with a blank line before and after each heading. Put each numbered clause or list item on its own line. Separate paragraphs with one blank line. Do not put the whole document in one paragraph. Do not wrap the whole answer in a code fence. Keep tables as valid Markdown tables with a header row and separator row. Keep numbering consistent and do not duplicate section numbers. Never invent cases, statutes, citations, quotations, facts or procedural rules. Use [PLACEHOLDER: ...] for missing facts. If no authoritative source is provided, state that legal authorities require verification. Preserve substantive meaning unless asked to change it. Distinguish sourced facts from assumptions. Include a concise OPEN ITEMS FOR HUMAN REVIEW section. You are not a lawyer and must not present output as definitive legal advice."""
    user = f"""TITLE: {req.title}
USER INSTRUCTION:
{req.instruction}

EXISTING DOCUMENT:
{req.document or "[No existing document]"}

REFERENCE MATERIAL:
{req.references or "[No references supplied]"}

STYLE PROFILE (user-provided examples only):
{req.style_profile or "[No style profile supplied]"}"""
    try:
        async with httpx.AsyncClient(timeout=150) as client:
            r = await client.post(f"{OLLAMA_BASE}/api/chat", json={"model": OLLAMA_MODEL, "stream": False, "keep_alive": "15m", "messages":[{"role":"system","content":system},{"role":"user","content":user}], "options":{"temperature":0.2,"num_ctx":6144,"num_predict":3072}})
            r.raise_for_status()
            content = r.json().get("message",{}).get("content","").strip()
            if not content: raise RuntimeError("Ollama returned an empty response")
            return {"content":normalize_draft_markdown(content),"mode":"ollama","model":OLLAMA_MODEL,"warning":"Review all facts and authorities. The model does not independently verify citations."}
    except Exception as e:
        return {"content":normalize_draft_markdown(fallback(req)),"mode":"fallback","model":None,"warning":f"Template fallback used; Ollama unavailable or failed ({type(e).__name__}). Install/start Ollama for model generation."}


@app.post("/api/speech/clean")
async def clean_speech_transcript(req: SpeechCleanupRequest):
    """Correct likely ASR spelling/punctuation errors locally while preserving facts."""
    original = req.transcript.strip()
    system = (
        "You are a conservative speech-transcript proofreader for legal case intake. "
        "Correct only clear speech-recognition errors, spelling, punctuation, and sentence boundaries. "
        "Preserve every fact, party name, amount, date, address, negation, uncertainty, and requested remedy exactly in meaning. "
        "Do not summarize, add facts, infer missing words, change numbers, or add legal advice. "
        "If a word is uncertain, keep the closest transcript wording rather than guessing. Return only the corrected transcript."
    )
    try:
        async with httpx.AsyncClient(timeout=35) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/chat",
                json={"model": OLLAMA_MODEL, "stream": False, "keep_alive": "15m",
                      "messages": [{"role": "system", "content": system},
                                   {"role": "user", "content": "Proofread this speech transcript conservatively. Do not change its meaning:\n\n" + original}],
                      "options": {"temperature": 0.0, "num_ctx": 4096}}
            )
            r.raise_for_status()
            cleaned = r.json().get("message", {}).get("content", "").strip()
            if cleaned and len(cleaned) <= max(100, len(original) * 2):
                return {"text": cleaned, "corrected": cleaned != original, "mode": "local_ollama", "warning": "Review names, dates, amounts and negations against the recording."}
    except Exception:
        pass
    return {"text": original, "corrected": False, "mode": "raw_transcript", "warning": "Local transcript cleanup was unavailable; review the raw transcript carefully."}

class CaseIntakeRequest(BaseModel):
    case_details: str = Field(min_length=10, max_length=12000)
    jurisdiction: str = Field(default="India", max_length=120)
    tone: str = Field(default="Formal and precise", max_length=120)

def heuristic_case_skill(text: str) -> tuple[str, str, str]:
    t = text.lower()
    rules = [
        (("reply to legal notice", "received a legal notice", "respond to notice", "reply notice"), "legal_notice", "Reply to Legal Notice", "The facts describe a response to an existing legal notice."),
        (("send a legal notice", "legal notice", "demand notice", "recover payment", "unpaid invoice", "breach notice"), "legal_notice", "Legal Notice", "The facts indicate a formal notice or demand may be needed."),
        (("petition", "file a writ", "application before", "court application", "seek relief from court"), "petition", "Petition / Application", "The facts describe relief sought from a court or authority."),
        (("agreement", "between the parties", "contract terms", "memorandum of understanding", "mou", "nda", "non-disclosure"), "agreement", "Agreement Draft", "The facts indicate a document recording mutual terms and obligations."),
        (("contract", "service provider", "scope of work", "deliverables", "payment milestones"), "contract", "Contract Draft", "The facts describe services, deliverables, or commercial obligations."),
        (("review this clause", "is this clause", "risky clause", "ambiguous clause", "unfair term", "risk in this contract"), "clause_review", "Clause Review", "The user asks to evaluate wording or identify legal/commercial risks."),
        (("compare these versions", "redline", "proposed changes", "mark up", "track changes"), "redline_review", "Document Revision Review", "The task asks for proposed changes to existing wording."),
        (("summarize", "summary of this document", "explain this judgment", "case judgment", "court held", "judgment says"), "case_analysis" if any(k in t for k in ("judgment", "court held", "court's reasoning", "case law")) else "summarize", "Case Analysis" if any(k in t for k in ("judgment", "court held", "court's reasoning", "case law")) else "Document Summary", "The request primarily asks for analysis or summarisation of existing material."),
        (("research the law", "legal research", "find authorities", "case law on", "statutory provisions"), "legal_research", "Legal Research Brief", "The task requests legal research rather than a new instrument."),
    ]
    for phrases, skill_id, title, reason in rules:
        if any(p in t for p in phrases):
            return skill_id, title, reason
    return "case_analysis", "Case Assessment and Draft", "The facts are ambiguous; a preliminary case assessment is the safest default before choosing a final instrument."

@app.post("/api/case/draft")
async def draft_from_case(req: CaseIntakeRequest):
    """Classify a spoken or typed case narrative, then draft with the matching skill."""
    heuristic_id, heuristic_title, heuristic_reason = heuristic_case_skill(req.case_details)
    allowed = {s.id for s in SKILLS}
    chosen_id, chosen_title, reason = heuristic_id, heuristic_title, heuristic_reason
    classifier_used = False
    classify_prompt = f"""Choose the single best DraftMate skill for the case narrative. Return ONLY JSON with keys skill_id, title, reason.
Allowed skill IDs: legal_notice, contract, agreement, petition, clause_review, redline_review, legal_research, case_analysis, due_diligence, summarize.
Do not decide the legal merits. Choose a document/workflow type based on the user's requested outcome. If unclear, choose case_analysis.
CASE NARRATIVE: {req.case_details}"""
    # Speed path: clear local heuristic matches do not need a separate LLM call.
    # Only ambiguous narratives get an Ollama classification pass before drafting.
    if heuristic_id == "case_analysis":
        try:
            async with httpx.AsyncClient(timeout=25) as client:
                r = await client.post(f"{OLLAMA_BASE}/api/chat", json={"model": OLLAMA_MODEL, "stream": False, "keep_alive": "15m", "format": "json", "messages": [{"role": "system", "content": "You classify legal drafting requests. Do not invent facts."}, {"role": "user", "content": classify_prompt}], "options": {"temperature": 0.0, "num_ctx": 3072, "num_predict": 180}})
                r.raise_for_status()
                raw = r.json().get("message", {}).get("content", "")
                data = json.loads(raw)
                candidate = str(data.get("skill_id", "")).strip()
                if candidate in allowed and candidate in {"legal_notice", "contract", "agreement", "petition", "clause_review", "redline_review", "legal_research", "case_analysis", "due_diligence", "summarize"}:
                    chosen_id = candidate
                    chosen_title = str(data.get("title") or get_skill(candidate).name)[:200]
                    reason = str(data.get("reason") or heuristic_reason)[:500]
                    classifier_used = True
        except Exception:
            pass
    instruction = (
        "You are drafting from a first-person or client-provided case narrative. First infer the requested outcome and produce the appropriate complete draft for the selected workflow. "
        f"Selected workflow: {get_skill(chosen_id).name}. Classification rationale: {reason}\n\n"
        "CASE DETAILS AS PROVIDED (preserve uncertainty; do not invent facts):\n" + req.case_details +
        "\n\nMANDATORY SAFEGUARDS: Separate stated facts from allegations and assumptions. Use [PLACEHOLDER: ...] for missing names, dates, locations, amounts, evidence, procedural posture or relief. If the story lacks essential information, still provide a useful draft with placeholders and a short list of missing details. Never fabricate statutes, case citations, limitation periods, deadlines, or court rules. Include an OPEN ITEMS FOR HUMAN REVIEW section. Clearly label the document as a draft for qualified legal review. If the requested instrument cannot safely be identified from the narrative, produce a preliminary case assessment and explain what fact would determine the instrument type."
    )
    draft_req = DraftRequest(title=chosen_title, instruction=instruction, skill=chosen_id, jurisdiction=req.jurisdiction, tone=req.tone)
    result = await generate_draft(draft_req)
    return {**result, "skill_id": chosen_id, "skill_name": get_skill(chosen_id).name, "title": chosen_title, "classification_reason": reason, "classification_source": "ollama" if classifier_used else "local heuristic fallback", "review_required": True}

@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename or "reference"
    ext = Path(filename).suffix.lower()
    raw = await file.read()
    if len(raw) > MAX_UPLOAD: raise HTTPException(413, f"File exceeds configured {MAX_UPLOAD // (1024*1024)} MB limit.")
    try:
        if ext in (".txt",".md",".markdown",".csv"):
            text = raw.decode("utf-8",errors="replace")
        elif ext == ".pdf":
            from pypdf import PdfReader
            text = "\n\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(raw)).pages)
        elif ext == ".docx":
            from docx import Document
            doc = Document(io.BytesIO(raw))
            text = "\n".join(p.text for p in doc.paragraphs)
            for table in doc.tables:
                text += "\n" + "\n".join(" | ".join(c.text for c in row.cells) for row in table.rows)
        else: raise HTTPException(415,"Supported formats: PDF, DOCX, TXT, Markdown, CSV.")
    except HTTPException: raise
    except Exception as e: raise HTTPException(400,f"Unable to extract document: {e}")
    return {"filename":filename,"text":text[:60000],"characters":len(text),"truncated":len(text)>60000}

@app.post("/api/style-profile")
async def style_profile(payload: dict):
    text = str(payload.get("text",""))[:60000]
    if not text.strip(): raise HTTPException(400,"Provide reference text to analyze.")
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    headings = [x for x in lines if len(x)<100 and (x.isupper() or re.match(r"^\d+[\.\)]\s",x))]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+",text) if s.strip()]
    avg = round(sum(len(s.split()) for s in sentences)/max(1,len(sentences)),1)
    formal = sum(bool(re.search(r"\b(hereby|whereas|pursuant|thereof|notwithstanding|shall)\b",s,re.I)) for s in sentences)
    profile = {"source":"user-provided reference","approx_words":len(text.split()),"average_sentence_words":avg,
               "heading_examples":headings[:12],"formal_legal_terms_detected":formal,
               "style_guidance":f"Mirror the reference's level of formality and heading structure. Average sentence length is about {avg} words. Use formal legal phrasing only where the source supports it. Preserve meaning; do not copy names, facts or clauses unless explicitly requested."}
    return profile

@app.post("/api/citations/review")
async def citation_review(req: ReviewRequest):
    patterns = [
      ("SCC Online",r"\b\d{4}\s+SCC\s+OnLine\s+[A-Za-z]+\s+\d+\b"),
      ("SCC",r"\b\d{4}\s+\(\d+\)\s+SCC\s+\d+\b"),
      ("AIR",r"\bAIR\s+\d{4}\s+[A-Z]+\s+\d+\b"),
      ("Section reference",r"\b(?:Section|Sec\.?)\s+\d+[A-Za-z]?(?:\([^)]+\))?\b"),
      ("Article reference",r"\bArticle\s+\d+[A-Za-z]?\b"),
      ("Rule reference",r"\bRule\s+\d+[A-Za-z]?\b")
    ]
    citations=[]
    for kind, pattern in patterns:
        for m in re.finditer(pattern,req.document,re.I):
            cite=m.group(0)
            if not any(x["citation"]==cite for x in citations):
                citations.append({"id":str(uuid.uuid4()),"citation":cite,"kind":kind,"status":"UNVERIFIED",
                    "evidence":None,"reason":"Citation-like text detected, but no authoritative source match has been performed."})
    sources=[
      {"name":"India Code","url":"https://www.indiacode.nic.in/","type":"official legislation portal","role":"Research starting point; not queried automatically by this prototype."},
      {"name":"Supreme Court of India","url":"https://www.sci.gov.in/","type":"official court website","role":"Research starting point; not queried automatically by this prototype."},
      {"name":"eCourts Services","url":"https://ecourts.gov.in/","type":"official court services","role":"Research starting point; not queried automatically by this prototype."},
      {"name":"Indian Kanoon","url":"https://indiankanoon.org/","type":"secondary research index","role":"Useful for discovery; independently confirm against authoritative sources."}
    ]
    return {"items":citations,"count":len(citations),"summary":{"verified":0,"partial":0,"unverified":len(citations)},
            "sources":sources,"method":"Pattern detection only; no source-level verification is configured. Therefore no citation can be labelled verified by this endpoint."}

@app.post("/api/drafts")
async def save_draft(req: SaveDraftRequest):
    now=int(time.time()); did=req.id or str(uuid.uuid4())
    with db() as c:
        c.execute("""INSERT INTO drafts(id,title,skill,content,instruction,created_at,updated_at) VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET title=excluded.title,skill=excluded.skill,content=excluded.content,instruction=excluded.instruction,updated_at=excluded.updated_at""",
        (did,req.title,req.skill,req.content,req.instruction,now,now))
    return {"id":did,"title":req.title,"saved":True,"updated_at":now}

@app.get("/api/drafts")
async def list_drafts():
    with db() as c:
        rows=c.execute("SELECT id,title,skill,created_at,updated_at FROM drafts ORDER BY updated_at DESC LIMIT 50").fetchall()
    return [dict(r) for r in rows]

@app.get("/api/drafts/{draft_id}")
async def get_draft(draft_id: str):
    with db() as c: row=c.execute("SELECT * FROM drafts WHERE id=?",(draft_id,)).fetchone()
    if not row: raise HTTPException(404,"Draft not found")
    return dict(row)

@app.delete("/api/drafts/{draft_id}")
async def delete_draft(draft_id: str):
    with db() as c: cur=c.execute("DELETE FROM drafts WHERE id=?",(draft_id,))
    if cur.rowcount==0: raise HTTPException(404,"Draft not found")
    return {"deleted":True}

@app.post("/api/export/docx")
async def export_docx(payload: dict):
    """Export Markdown-like draft text to a readable, styled DOCX without raw markers."""
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import re

    title = str(payload.get("title", "DraftMate document"))[:200]
    content = normalize_draft_markdown(str(payload.get("content", ""))[:100000])
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    doc.styles["Title"].font.name = "Times New Roman"
    doc.styles["Title"].font.size = Pt(18)
    doc.styles["Title"].font.bold = True

    def add_inline(paragraph, text):
        # Parse **bold**, __bold__, *italic*, and _italic_ while keeping all
        # other text literal. This prevents Markdown markers leaking into DOCX.
        pattern = re.compile(r"(\*\*.+?\*\*|__.+?__|(?<!\*)\*[^*\n]+\*(?!\*)|(?<!_)_[^_\n]+_(?!_))")
        pos = 0
        for match in pattern.finditer(text):
            if match.start() > pos:
                paragraph.add_run(text[pos:match.start()])
            token = match.group(0)
            if token.startswith("**") and token.endswith("**"):
                run = paragraph.add_run(token[2:-2]); run.bold = True
            elif token.startswith("__") and token.endswith("__"):
                run = paragraph.add_run(token[2:-2]); run.bold = True
            elif token.startswith("*") and token.endswith("*"):
                run = paragraph.add_run(token[1:-1]); run.italic = True
            elif token.startswith("_") and token.endswith("_"):
                run = paragraph.add_run(token[1:-1]); run.italic = True
            pos = match.end()
        if pos < len(text):
            paragraph.add_run(text[pos:])

    lines = content.replace("\r", "").split("\n")
    title_added = False
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            continue
        # Convert valid Markdown tables into actual Word tables rather than pipe-filled text.
        if line.startswith("|") and line.endswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            def split_cells(value):
                return [cell.strip() for cell in value.strip().strip("|").split("|")]
            headers = split_cells(line)
            i += 2  # skip the header and Markdown separator
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                rows.append(split_cells(lines[i].strip()))
                i += 1
            table = doc.add_table(rows=1, cols=max(1, len(headers)))
            try:
                table.style = "Light Shading Accent 1"
            except Exception:
                table.style = "Table Grid"
            for col, header_text in enumerate(headers):
                cell = table.rows[0].cells[col]
                cell.text = ""
                run = cell.paragraphs[0].add_run(header_text)
                run.bold = True
            for row in rows:
                cells = table.add_row().cells
                for col in range(len(headers)):
                    cells[col].text = row[col] if col < len(row) else ""
            doc.add_paragraph()
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = min(len(heading.group(1)), 3)
            p = doc.add_paragraph(style=f"Heading {level}")
            add_inline(p, heading.group(2).strip())
            i += 1
            continue
        # Markdown horizontal rules are visual separators, not document text.
        if re.fullmatch(r"[-*_]{3,}", line):
            i += 1
            continue
        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        numbered = re.match(r"^(\d+[.)])\s+(.+)$", line)
        if bullet:
            p = doc.add_paragraph(style="List Bullet")
            add_inline(p, bullet.group(1))
        elif numbered:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            r = p.add_run(numbered.group(1) + " "); r.bold = True
            add_inline(p, numbered.group(2))
        else:
            p = doc.add_paragraph()
            add_inline(p, line)
        i += 1
    buf = io.BytesIO(); doc.save(buf)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", title).strip("_") or "draft"
    return Response(buf.getvalue(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe[:80]}.docx"'})



# DraftMate's docassemble-inspired Indian legal notice interview.
# The YAML interview is bundled as an editable reference package. DraftMate's
# desktop workflow uses a native React form and the local assembler below;
# it does not pretend the full docassemble server runtime is embedded.
NOTICE_INTERVIEW = {
    "engine": "docassemble-inspired interview schema",
    "jurisdiction": "India",
    "version": 1,
    "fields": [
        {"name":"notice_type","label":"Notice type","type":"select","required":True,"options":["Payment demand","Breach of agreement","Landlord / tenancy","Consumer complaint","Employment matter","Cheque dishonour (Section 138 NI Act - verify applicability)","General legal notice"]},
        {"name":"advocate_name","label":"Advocate name","type":"text","required":False},
        {"name":"advocate_address","label":"Advocate office address","type":"textarea","required":False},
        {"name":"client_name","label":"Client / sender full legal name","type":"text","required":True},
        {"name":"recipient_name","label":"Recipient full legal name","type":"text","required":True},
        {"name":"recipient_address","label":"Recipient full address","type":"textarea","required":True},
        {"name":"facts","label":"Chronology of material facts","type":"textarea","required":True},
        {"name":"demand","label":"Action / relief demanded","type":"textarea","required":True},
        {"name":"amount","label":"Amount and currency, if any","type":"text","required":False},
        {"name":"deadline","label":"Requested response deadline","type":"text","required":False},
        {"name":"legal_basis","label":"Legal provisions / contract clauses (only if known)","type":"textarea","required":False},
        {"name":"evidence","label":"Supporting documents / evidence","type":"textarea","required":False},
        {"name":"delivery_method","label":"Intended delivery method","type":"select","required":True,"options":["Speed Post","Registered Post A.D.","Courier","Email","Hand delivery","Other / to be confirmed"]},
        {"name":"notice_date","label":"Notice date (DD-MM-YYYY)","type":"text","required":True}
    ],
    "review_rules": ["Do not invent facts, legal authorities or deadlines.", "Flag missing information with explicit placeholders.", "Check limitation, statutory notice periods, jurisdiction and service rules with an advocate.", "Verify every cited statute and case against an authoritative source."]
}

@app.get("/api/legal-notice/interview")
async def legal_notice_interview():
    """Return the docassemble-inspired interview schema for the desktop wizard."""
    return NOTICE_INTERVIEW

@app.post("/api/legal-notice/assemble")
async def assemble_legal_notice(payload: dict):
    """Assemble a deterministic Indian-style notice DOCX from structured answers."""
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    allowed = {f["name"] for f in NOTICE_INTERVIEW["fields"]}
    data = {k: str(v).strip() for k, v in payload.items() if k in allowed and v is not None}
    required = [f["name"] for f in NOTICE_INTERVIEW["fields"] if f.get("required")]
    missing = [f["label"] for f in NOTICE_INTERVIEW["fields"] if f["name"] in required and not data.get(f["name"], "").strip()]
    if missing:
        raise HTTPException(422, detail={"message":"Complete required interview fields before assembling.","missing":missing})
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75); section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.9); section.right_margin = Inches(0.9)
    normal = doc.styles["Normal"]; normal.font.name = "Times New Roman"; normal.font.size = Pt(12)
    if data.get("advocate_name"):
        para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(data["advocate_name"].upper()); run.bold = True; run.font.size = Pt(16)
    if data.get("advocate_address"):
        para = doc.add_paragraph(data["advocate_address"]); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = para.add_run("LEGAL NOTICE"); r.bold = True; r.font.size = Pt(15)
    para = doc.add_paragraph(data.get("notice_type", "General legal notice")); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(6)
    pPr = para._p.get_or_add_pPr(); borders = OxmlElement('w:pBdr'); bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),'single'); bottom.set(qn('w:sz'),'8'); bottom.set(qn('w:space'),'1'); bottom.set(qn('w:color'),'B08A4A'); borders.append(bottom); pPr.append(borders)
    doc.add_paragraph(f"Date: {data.get('notice_date','[DATE]')}")
    doc.add_paragraph("To,\n" + data.get("recipient_name", "[RECIPIENT NAME]") + "\n" + data.get("recipient_address", "[RECIPIENT ADDRESS]"))
    para = doc.add_paragraph(); run = para.add_run("Subject: "); run.bold = True
    para.add_run(data.get("demand", "[SUBJECT / DEMAND]"))
    doc.add_paragraph("Sir/Madam,")
    doc.add_paragraph(f"Under instructions from and on behalf of my client, {data.get('client_name','[CLIENT NAME]')}, I address this notice to you as follows:")
    doc.add_paragraph("1. Material facts", style="Heading 2")
    doc.add_paragraph(data.get("facts", "[INSERT VERIFIED CHRONOLOGY OF FACTS]"))
    if data.get("amount"):
        doc.add_paragraph("2. Amount involved", style="Heading 2"); doc.add_paragraph(data["amount"])
    if data.get("legal_basis"):
        doc.add_paragraph("Legal basis supplied for review", style="Heading 2"); doc.add_paragraph(data["legal_basis"])
    if data.get("evidence"):
        doc.add_paragraph("Documents / evidence identified", style="Heading 2"); doc.add_paragraph(data["evidence"])
    doc.add_paragraph("Demand", style="Heading 2")
    doc.add_paragraph(data.get("demand", "[SPECIFY ACTION OR RELIEF SOUGHT]"))
    if data.get("deadline"):
        doc.add_paragraph(f"You are requested to respond or comply by {data['deadline']}. The applicability and sufficiency of this period must be confirmed by an advocate for the specific cause of action.")
    else:
        doc.add_paragraph("You are requested to respond within the period advised by qualified counsel for the applicable cause of action. No statutory deadline has been assumed in this draft.")
    doc.add_paragraph("In the event of non-compliance, my client reserves the right to pursue remedies available under applicable law, subject to legal advice and without prejudice to other rights and contentions.")
    doc.add_paragraph(f"Proposed mode of dispatch: {data.get('delivery_method','[DELIVERY METHOD]')}")
    doc.add_paragraph("Yours faithfully,")
    doc.add_paragraph(data.get("advocate_name") or "[ADVOCATE NAME]")
    doc.add_paragraph("Advocate")
    doc.add_paragraph("\nDRAFT FOR REVIEW: Confirm facts, limitation, jurisdiction, applicable law, service method and any statutory deadline with a qualified Indian advocate before dispatch. No legal authority has been independently verified by this assembler.")
    buf = io.BytesIO(); doc.save(buf)
    return Response(buf.getvalue(), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition":"attachment; filename=DraftMate_Indian_Legal_Notice.docx"})


# Serve the built React frontend when running as the desktop application.
# API routes above take precedence; this mount is deliberately added last.
_default_static = (Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])) / "static")
_static_dir = Path(os.getenv("DRAFTMATE_STATIC_DIR", str(_default_static))).resolve()
if _static_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="frontend")
