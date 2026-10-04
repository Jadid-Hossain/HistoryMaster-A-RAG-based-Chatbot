# 🤖 KnowBot — AI Knowledge-Base Chatbot (RAG)

A production-style **RAG (Retrieval-Augmented Generation) chatbot** that answers questions
**strictly from a custom knowledge base** (a big PDF handbook + documents in many formats),
politely refuses anything outside it, and shows **sources + match scores** for every answer.

> Final Project 1 — "AI-powered chatbot with knowledge handling capabilities"
> Built with **FastAPI + LangChain + ChromaDB + Google Gemini** on the backend and
> **React (Vite)** on the frontend.

---

## ✨ How it works (the RAG pipeline)

```
                         ┌────────────────────────── Backend (FastAPI) ─────────────────────────┐
 PDF / DOCX / TXT /      │                                                                       │
 MD / HTML / URL   ───►  │  LangChain Loaders ──► RecursiveCharacterTextSplitter ──► Embeddings  │
     (admin uploads)     │                                                            │          │
                         │                                                            ▼          │
                         │                                              ┌────────────────────┐   │
 user question  ───────► │  memory rewrite ──► similarity search ─────► │  CHROMA VECTOR DB  │   │
                         │  (short-term)       (cosine, top-k)          │  (persistent)      │   │
                         │                                              └────────────────────┘   │
                         │                                                            │          │
                         │              grounded prompt (context only)  ◄─────────────┘          │
                         │                        │                                              │
                         │                        ▼                                              │
                         │              Gemini LLM (API key)  ──► answer + sources + score       │
                         │                        │                                              │
                         │         NOT_IN_KB ──►  polite fallback message                        │
                         └───────────────────────────────────────────────────────────────────────┘
```

**Why it can't hallucinate:** the LLM receives *only* the retrieved knowledge-base chunks and is
instructed to reply `NOT_IN_KB` when the context lacks the answer — that reply is converted to a
graceful "not found in knowledge base" message. A similarity floor rejects unrelated questions
before the LLM is even called.

---

## 📋 Requirements checklist (faculty mapping)

### Core requirements (must have)

| # | Requirement | Where |
|---|-------------|-------|
| 1 | Trainable on a custom, medium-size knowledge base | Admin panel upload / `scripts/seed_kb.py` — the 14-page sample PDF + 12 docs → ~90 chunks indexed into Chroma |
| 2 | Responds accurately **using only** the knowledge base | `app/services/rag.py` — grounded prompt + `NOT_IN_KB` contract + retrieval floor |
| 3 | Graceful handling of out-of-scope questions | `app/services/chatbot.py::_fallback` — polite "not found in my knowledge base" + rephrasing suggestion |

### Additional features (good to have)

| # | Feature | Where |
|---|---------|-------|
| 1 | Intelligent knowledge retrieval | Chroma cosine similarity search + Gemini answer generation with source citations (`sources[]` in every response) |
| 2 | Conversation memory (short-term) | `app/services/memory.py` — follow-ups like *"Where is his office?"* are rewritten into standalone queries using the last turns |
| 3 | Multiple data formats | PDF, TXT, MD, DOCX, HTML + **web page URLs** (LangChain loaders) |
| 4 | KB updates without full retraining | New documents are chunk-embedded **incrementally** — upload a doc and ask about it immediately; deletion removes exactly its vectors |
| 5 | Authentication (users/admins) | JWT auth (`app/security.py`) — PBKDF2 password hashing, `admin` role gates KB management |
| 6 | API documentation | Auto-generated **Swagger UI** at `/docs` and ReDoc at `/redoc` |
| 7 | Logger for backend | Rotating file logger → `backend/logs/app.log` + every request/question/answer logged |

### System requirements (must have)

| # | Requirement | Where |
|---|-------------|-------|
| 1 | Complete frontend chat interface | React + Vite app (`frontend/`) — login, chat with sources, admin panel |
| 2 | Backend for queries / KB / responses | FastAPI (`backend/app/`) |
| 3 | Clean API-based architecture | Frontend ⇄ REST ⇄ backend, OpenAPI documented |
| 4 | Maintained on GitHub | Repo root here — commit history + GitHub Actions CI (`.github/workflows/tests.yml`) |

---

## 🚀 Quick start

### 0. Prerequisites
- Python 3.11+ and Node 18+
- A (free) Google Gemini API key → https://aistudio.google.com/apikey

### 1. Configure the LLM key

Copy `.env.example` to `.env` (already created) and paste your key:

```env
GEMINI_API_KEY=AIza...your_key_here
```

### 2. Backend setup (first time)

```bash
cd backend
python -m venv ../venv                      # (skip if venv/ already exists)
../venv/Scripts/activate                    # Windows Git Bash; on cmd: ..\venv\Scripts\activate.bat
pip install -r requirements.txt

python scripts/download_models.py           # one-time: local embedding model (~90 MB)
python scripts/make_sample_kb.py            # one-time: generates the sample PDF/DOCX files
python scripts/seed_kb.py                   # load the sample knowledge base into Chroma

python scripts/check_setup.py               # ✅ verifies key + models + DB + a live LLM call
```

### 3. Run

**One-click demo (Windows):** double-click **`run_demo.bat`** — builds the frontend, starts the
backend, and opens **http://localhost:8000**.

Manual:

```bash
# terminal 1 - backend (serves the built frontend too)
cd backend && ../venv/Scripts/python -m uvicorn app.main:app --port 8000

# terminal 2 - frontend dev mode (optional; hot reload)
cd frontend && npm install && npm run dev    # http://localhost:5173
```

- **Chat UI:** http://localhost:8000 (production build) or http://localhost:5173 (dev)
- **API docs (Swagger):** http://localhost:8000/docs
- **Demo accounts:** `admin / admin123` (admin) · `user / user123` (regular user)

### 4. Frontend production build

```bash
cd frontend && npm install && npm run build   # -> frontend/dist, served by FastAPI automatically
```

---

## 🎤 10-minute live demo script

1. **Login page** → sign in as `user/user123`. Point out the auth requirement.
2. Ask a KB question: *"When was Greenfield University founded?"* → **1998**, with **sources** (handbook PDF) and a match score shown under the answer.
3. Factoid questions: *"Who is the head of the CSE department?"*, *"What is the tuition fee for CSE?"*, *"How many books can I borrow from the library?"*
4. List question: *"What topics are covered in the Machine Learning course?"*
5. **Memory:** *"What scholarships are available?"* → then *"Tell me more about the Chancellor one"* (follow-up resolved via short-term memory).
6. **Out-of-scope:** *"Who will win the next World Cup?"* → polite *"not found in my knowledge base"* fallback — no hallucination.
7. **Admin live update (no retraining):** logout → login `admin/admin123` → Admin Panel → upload any new `.txt` file (e.g. `knowledge_base/09_sports_clubs.txt` after removing it, or your own) → back to chat → ask about it **immediately**. Emphasize: *new vectors appended — the LLM was never retrained.*
8. **Multi-format:** show the documents table — a 14-page PDF handbook, DOCX, HTML news page.
9. **API docs:** open `/docs` — every endpoint documented; execute a request live.
10. **Logs:** show `backend/logs/app.log` — each request, retrieval score and answer is logged.

*(Full walkthrough with expected answers: [`docs/DEMO_GUIDE.md`](docs/DEMO_GUIDE.md))*

---

## 🧪 Tests

```bash
cd backend
python -m pytest            # hermetic: fake LLM, isolated temp DB, real Chroma + embeddings
```

Covers auth & roles, KB upload/delete/URL-ingest, incremental updates, grounded answers,
out-of-scope fallback, session memory, ownership rules, and API health. GitHub Actions runs
the same suite on every push.

---

## 🗂 Project structure

```
KnowBot/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app, lifespan, static frontend mount
│   │   ├── config.py             # .env config (LLM keys, RAG knobs)
│   │   ├── database.py           # SQLite: users, sessions, messages, doc registry
│   │   ├── security.py           # JWT + PBKDF2 + role dependencies
│   │   ├── logger.py             # rotating file logger + request middleware
│   │   ├── routers/              # auth.py, chat.py, kb.py
│   │   └── services/
│   │       ├── llm.py            # Gemini/OpenAI/Groq/… provider abstraction
│   │       ├── embeddings.py     # local MiniLM (or Gemini) embeddings
│   │       ├── vectorstore.py    # Chroma persistent vector DB
│   │       ├── ingest.py         # LangChain loaders → splitter → vector DB
│   │       ├── rag.py            # grounded prompt + NOT_IN_KB contract
│   │       ├── memory.py         # short-term conversation memory
│   │       └── chatbot.py        # pipeline orchestrator + fallback
│   ├── knowledge_base/           # sample KB: big PDF handbook + 12 docs
│   ├── scripts/                  # seed_kb, check_setup, download_models, make_sample_kb
│   ├── tests/                    # pytest suite (hermetic)
│   └── data/                     # runtime: SQLite DB, Chroma store, uploads (git-ignored)
├── frontend/
│   └── src/                      # React: Login, Chat, Admin pages + dark UI
├── docs/                         # DEMO_GUIDE.md, architecture notes
├── .env                          # ← your API key (git-ignored)
├── .env.example
├── run_demo.bat                  # one-click demo launcher (Windows)
└── .github/workflows/tests.yml   # CI
```

## 🔧 Configuration knobs (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `GEMINI_API_KEY` | — | LLM API key (or `OPENAI_API_KEY` / `GROQ_API_KEY` / …) |
| `LLM_PROVIDER` | `auto` | `auto` picks the first key present; or force `gemini` / `openai` / `groq` / `deepseek` |
| `LLM_MODEL` | provider default | e.g. `gemini-2.5-flash`, `gemini-2.5-pro` |
| `EMBEDDINGS_PROVIDER` | `local` | `local` (offline MiniLM) or `gemini` (API embeddings) |
| `RETRIEVAL_TOP_K` / `RETRIEVAL_FLOOR` | 5 / 0.30 | chunks fetched / minimum cosine similarity to answer |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 1000 / 150 | splitter settings |

## 📌 Notes for the viva

- **Why Chroma?** A real persistent vector database (HNSW index, metadata filtering) — survives
  restarts, supports incremental add/delete. SQLite stores only relational metadata
  (users/sessions/messages/document registry).
- **Why local embeddings?** Ingestion stays free/fast/offline; only answering needs the LLM API.
  Switchable to API embeddings via one env var.
- **Grounding contract:** system prompt forbids outside knowledge; the literal `NOT_IN_KB` reply
  is mapped to the polite fallback; the retrieval floor rejects unrelated questions early.
- **Security:** PBKDF2-SHA256 (200k iterations) password hashes, signed JWT tokens, role-based
  authorization on every KB endpoint, session ownership checks.
