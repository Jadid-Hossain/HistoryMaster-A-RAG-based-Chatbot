# 🎓 History Master — Viva & Demo Preparation Guide

Read this top to bottom once, and you will be able to demo the project and
answer viva questions comfortably. Numbers mentioned here are the REAL numbers
of your project.

---

## 1. The 30-second pitch (memorize this)

> "My project is **History Master**, an AI chatbot that answers questions about
> the history of Bangladesh **strictly from a knowledge base** — the book
> *A History of Bangladesh*. It uses **RAG — Retrieval-Augmented Generation**:
> when a user asks a question, the system first **retrieves** the most relevant
> passages of the book from a **vector database**, then asks **Google Gemini**
> to write an answer using **only those passages**. Every answer shows its
> **sources with a match score**, and if the answer is not in the book, the bot
> honestly says *"not found in my knowledge base"* instead of making things up.
> The frontend is React, the backend is FastAPI, the vector database is Chroma,
> and the whole thing is connected through a documented REST API."

---

## 2. The problem and the solution (why this project exists)

| Problem with plain ChatGPT/Gemini | How History Master solves it |
|---|---|
| Hallucinates facts (invents answers) | The LLM only sees retrieved book passages; instructed to reply `NOT_IN_KB` if they don't contain the answer |
| No sources — can't verify | Every answer shows the source document + snippet + match % |
| Generic knowledge, not your documents | Retrieval is done over YOUR knowledge base |
| Paid/limited context for whole books | Only the top ~20 relevant chunks are sent per question |

---

## 3. Architecture (draw this on the whiteboard if asked)

```
        React Frontend (Vite build, served by FastAPI)
            |  REST + JWT (Authorization: Bearer)
            ▼
        FastAPI Backend  ──── Swagger docs at /docs
            |
            |-- SQLite      → users, chat sessions, messages (metadata)
            |
            |-- RAG pipeline:
            |     1. small talk?  → canned reply (no LLM)
            |     2. memory       → rewrite follow-ups ("Where is his office?")
            |     3. retrieval    → Chroma vector DB (cosine, top-20)
            |     4. hybrid probe → keyword match for name spellings
            |     5. generation   → Gemini, grounded prompt, NOT_IN_KB contract
            |     6. fallback     → polite "not in my knowledge base"
            |
            └── Logger → backend/logs/app.log (rotating file + console)
```

**One line to remember:** *Question → embed → find similar book chunks in
Chroma → give them to Gemini → Gemini answers only from them → show sources.*

---

## 4. What is RAG? (the core concept — they WILL ask this)

**RAG = Retrieval-Augmented Generation.**

- **Retrieval**: find the few relevant pieces of your documents for a question.
- **Augmented**: attach them to the LLM prompt as context.
- **Generation**: the LLM writes the answer using that context.

**Why RAG instead of fine-tuning the model on the book?** (very common viva question)
- Fine-tuning teaches *style/patterns*, not reliable *facts*; it still hallucinates.
- Fine-tuning is expensive and must be redone whenever the knowledge base changes.
- RAG needs **no training at all** — upload a new document and it is instantly
  usable ("knowledge base updates without full retraining" — our core requirement).
- RAG gives **sources** for every answer; fine-tuning cannot.

---

## 5. Step-by-step: what happens when you ask a question

Example question: *"When was Bangladesh liberated?"*

1. **Auth check** — the React app sends the question with a JWT token; FastAPI
   validates it before anything runs.
2. **Small-talk check** — "hello", "thanks", "what can you do?" are answered with
   canned replies; no LLM call, no cost.
3. **Memory rewrite** — if the question is a follow-up ("Where is his office?"),
   the last 6 messages are used to rewrite it into a standalone query
   ("Who is the head of the CSE department? Where is his office?").
4. **Embedding** — the question is converted to a 384-dimension vector by
   `all-MiniLM-L6-v2` (runs locally on CPU, free, offline).
5. **Vector search (Chroma)** — cosine similarity between the question vector
   and all 992 book-chunk vectors; the top 20 most similar chunks are returned.
6. **Hybrid keyword probe** — distinctive words of the question (e.g. "Siraj")
   are substring-matched against the corpus so name-spelling variants
   ("Siraj ud-Daulah" vs the book's "Sirajuddaula") are not missed.
7. **Retrieval floor** — if even the best chunk has similarity < 0.15, the
   question is unrelated to the book → **polite fallback** immediately (no LLM
   call, no cost).
8. **Grounded generation (Gemini)** — the 20 chunks are placed in a prompt:
   > "Answer ONLY from this CONTEXT. If it doesn't contain the answer, reply
   > NOT_IN_KB."  (temperature 0.1 — near-deterministic)
9. **Refusal mapping** — if Gemini replies `NOT_IN_KB` (or a clear refusal),
   the bot sends the polite fallback message instead.
10. **Response** — the API returns the answer + **sources** (document name,
    snippet, match %) + latency; the frontend shows them, and both messages are
    saved to SQLite for the session history.

Typical latency: **1.5–4 seconds** per question.

---

## 6. Component-by-component (know one line about each)

### Backend — FastAPI (Python) `backend/app/`
| File | What it does |
|---|---|
| `main.py` | FastAPI app, startup (loads models), routes, serves the built React app |
| `config.py` | All settings from `.env` (API keys, model names, thresholds) |
| `security.py` | JWT tokens (HS256, 12h) + PBKDF2-SHA256 password hashing (200,000 iterations) + role checks |
| `database.py` | SQLite: users, sessions, messages, document registry |
| `logger.py` | Rotating file logger (`backend/logs/app.log`, 5 MB × 3 backups) + request-timing middleware |
| `routers/auth.py` | register / login / me / users list |
| `routers/chat.py` | ask / sessions / history / capabilities |
| `routers/kb.py` | upload files, add URL, list, delete, re-index, stats (admin only) |
| `services/llm.py` | LLM provider abstraction — Gemini/OpenAI/Groq/DeepSeek, chosen from `.env` |
| `services/embeddings.py` | Local MiniLM embeddings (or Gemini API embeddings if configured) |
| `services/vectorstore.py` | Chroma wrapper — add/delete/search, hybrid keyword probes |
| `services/ingest.py` | LangChain loaders (PDF/DOCX/TXT/MD/HTML/Web) → text splitter → vector DB |
| `services/rag.py` | The grounded prompt + `NOT_IN_KB` parsing |
| `services/memory.py` | Short-term memory: follow-up question rewriting |
| `services/chatbot.py` | The pipeline orchestrator + fallback messages |

### Frontend — React (Vite) `frontend/src/`
- `pages/Login.jsx` — split-screen login/register
- `pages/Chat.jsx` — chat UI: messages, sources with match %, timestamps, copy button, session sidebar
- `pages/Admin.jsx` — drag-&-drop upload, URL ingest, document table, users tab, stats
- Built with `npm run build` → `frontend/dist` → served by FastAPI at port 8000 (single origin, no CORS issues in the demo)

### AI stack
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`, 384 dims, local & free
- **Vector DB:** Chroma (persistent, cosine space, 992 chunks)
- **LLM:** Google Gemini (`gemini-flash-lite-latest`) via API key in `.env`

---

## 7. Key design decisions + WHY (viva gold)

| Question you'll get | Your answer |
|---|---|
| Why Chroma and not FAISS/Pinecone? | Chroma is a persistent, embedded vector DB — survives restarts, supports metadata filtering and incremental add/delete, no server needed. Pinecone is cloud-paid; FAISS is a library, not a DB with persistence semantics. |
| Why local embeddings instead of API? | Ingestion of a 992-chunk book stays free, fast and offline; only answering needs the LLM API. Configurable to API embeddings with one env var. |
| Why temperature 0.1? | Factoid QA must be near-deterministic; high temperature increases creativity AND hallucination. |
| Why chunk size 1000 chars with 150 overlap? | ~2 paragraphs keeps one coherent topic per chunk; overlap prevents answers being cut at chunk boundaries. |
| Why is the retrieval floor 0.15? | It is only a cheap pre-filter to save LLM calls; the precise guard is the LLM's NOT_IN_KB contract. Kept low so short questions with low lexical overlap aren't missed. |
| Why hybrid retrieval? | Embeddings miss spelling variants ("Siraj ud-Daulah" vs "Sirajuddaula") — a substring keyword probe catches them. Bibliography pages are demoted because they match keywords but never answer. |
| How do you prevent hallucination? | Three layers: (1) retrieval floor, (2) NOT_IN_KB contract in the prompt, (3) sources shown so users can verify. Plus low temperature. |
| What if the LLM service is down? | The API catches the error and returns a friendly "temporarily unavailable" message with the retrieved sources — the server never crashes. |

---

## 8. Security design (requirement 5)

- Passwords: **PBKDF2-HMAC-SHA256, 200,000 iterations**, random 16-byte salt per user — never stored in plain text.
- Login returns a **JWT** (HS256 signed, 12-hour expiry) containing username, user id and role.
- Every API call (except register/login/health) requires `Authorization: Bearer <token>`.
- **Roles:** `admin` manages the knowledge base; `user` can only chat. Enforced server-side (403).
- Users can only see their **own** chat sessions (ownership checks — 404 otherwise).
- The API key lives in `.env`, which is **git-ignored** — never committed.

---

## 9. API Documentation (requirement 6)

- FastAPI auto-generates **Swagger UI** at `/docs` and **ReDoc** at `/redoc` from the OpenAPI spec — always in sync with the code.
- 15 endpoints across 4 groups:
  - `Authentication`: register, login, me, users (admin)
  - `Chat`: ask, list sessions, get history, delete session, capabilities
  - `Knowledge Base (admin)`: upload files, add URL, list, delete, re-index, stats
  - `System`: health
- Every endpoint has a summary; login-protected ones show the 🔒 padlock in Swagger.
- Live demo: open `/docs` → Authorize with a token → execute `GET /api/chat/capabilities`.

---

## 10. Live demo script (10 minutes, tested)

**Before:** double-click `run_demo.bat` → wait ~1 minute → browser opens at http://localhost:8000. Log in as `user / user123`.

| # | Do this | Say this |
|---|---|---|
| 1 | Login page | "The system requires authentication — JWT-based, two roles." |
| 2 | Ask: *When was Bangladesh liberated?* | Answer: **1971 / 16 December**, with 📚 Sources + match %. "Notice the answer comes from the book, and the source is shown." |
| 3 | Ask: *Who was Siraj ud-Daulah?* | **Last nawab of Bengal, defeated at Polashi 1757** — "even when the question's spelling differs from the book's." |
| 4 | Ask: *What was Operation Searchlight?* | Rich structured answer — shows list-type questions work. |
| 5 | Ask: *What was the Language Movement?* then *When did it happen?* | Second question uses **conversation memory** ("it" is resolved). |
| 6 | Ask: *Who won the FIFA World Cup 2022?* | Polite **fallback** — "outside my knowledge base. No hallucination — this is a core requirement." |
| 7 | Ask: *hello* / *What can you do?* | Canned replies — handled without the LLM. |
| 8 | Logout → login `admin/admin123` → Admin Panel | Show stats (1 document, 992 chunks), drag-&-drop upload a small .txt with a new fact. |
| 9 | Back to chat, ask about the new fact | **Answered instantly — "knowledge base updated without retraining."** |
| 10 | Open `/docs` | "Full OpenAPI documentation, auto-generated." Execute one GET live. |
| 11 | Show `backend/logs/app.log` | "Every request is logged — requirement 7." |

**Backup questions that work:** *Who wrote this book?* (Willem van Schendel) ·
*What is the Shaheed Minar?* · *What was the Two Nation Theory?* ·
*How did rivers shape the history of Bengal?* · *What was the Swadeshi movement?*

---

## 11. Numbers cheat sheet (memorize!)

| Thing | Value |
|---|---|
| Knowledge base | 1 PDF (*A History of Bangladesh*, Willem van Schendel) |
| Chunks | **992** (splitter: 1000 chars, 150 overlap) |
| Embedding model | all-MiniLM-L6-v2, **384 dimensions**, local CPU |
| Vector DB | **Chroma**, persistent, cosine similarity |
| Retrieved chunks per question | **20** (+ up to 10 keyword-probe candidates) |
| Retrieval floor | **0.15** cosine similarity |
| LLM | **Gemini flash-lite** (API key in `.env`), temperature **0.1** |
| Memory window | last **6** messages |
| JWT | HS256, **12 hours** |
| Password hashing | PBKDF2-SHA256, **200,000** iterations |
| Upload limit | 25 MB; formats: PDF, TXT, MD, DOCX, HTML + URL |
| Test suite | **29 tests, all passing** |
| Accuracy test | 20 history questions: 17 answered well, refusals correct |
| Endpoints | **15** REST endpoints, Swagger at `/docs` |

---

## 12. Likely viva questions & ready answers

1. **What is RAG?** — Retrieval-Augmented Generation: retrieve relevant document chunks, augment the prompt with them, generate a grounded answer. Gives up-to-date, source-backed answers without training.
2. **Why not fine-tune GPT/Gemini on the book?** — Fine-tuning is costly, must be redone for every KB change, still hallucinates, and gives no sources. RAG needs zero training and cites passages.
3. **Why not just ask Gemini directly?** — It answers from general knowledge, hallucinates, gives no sources, and can't know our book.
4. **What is an embedding?** — A numeric vector (here 384 numbers) representing text meaning, such that similar texts have close vectors.
5. **What is cosine similarity?** — cos(θ) between two vectors; 1 = identical meaning, 0 = unrelated. We compare the question vector with every chunk vector.
6. **What is a vector database and why do you need one?** — A DB optimized to store and search high-dimensional vectors (approximate nearest neighbor search, e.g., HNSW). Scanning 992 vectors is fast and persistent across restarts.
7. **How is the PDF read?** — LangChain's PyPDFLoader extracts text page by page; RecursiveCharacterTextSplitter chunks it at 1000 characters with 150 overlap.
8. **What happens if I upload a new document?** — It's split, embedded and added to Chroma immediately — answers about it work seconds later. No retraining, because nothing is trained.
9. **What if I delete a document?** — Its vectors are removed from Chroma by a metadata filter (doc_id), so it stops being answerable immediately.
10. **How does the bot know it doesn't know?** — The prompt forces the model to reply `NOT_IN_KB` when the context lacks the answer; we map that to a polite fallback. A similarity floor rejects unrelated questions even earlier.
11. **How does conversation memory work?** — We store the last 6 messages per session; if a new question contains pronouns/follow-up cues ("it", "more"), we prepend the previous question before embedding.
12. **Is my chat history stored?** — Yes, in SQLite per user session; users can delete sessions from the UI.
13. **How does login work?** — Password verified against a PBKDF2 hash; server issues a signed JWT with role; frontend stores it and sends it as a Bearer token; protected endpoints validate it.
14. **What is the difference between admin and user?** — Admin can manage the knowledge base (upload/delete/re-index) and see stats and users; users can only chat.
15. **Is the API documented?** — Yes — FastAPI auto-generates Swagger UI at /docs and ReDoc at /redoc from the OpenAPI schema; 15 documented endpoints.
16. **What framework is the backend and why?** — FastAPI: async, fast, automatic OpenAPI docs, Pydantic validation, dependency injection for auth.
17. **What is the frontend and how is it served?** — React 18 + Vite; `npm run build` produces static files that FastAPI serves — one origin, one port for demo.
18. **What did you test?** — 29 pytest tests: auth/RBAC, uploads of every format, URL ingest, incremental updates, grounding, fallback, LLM-failure handling, memory, session ownership. Runs in CI (GitHub Actions).
19. **What are the limitations?** — Scanned/image PDFs without text can't be parsed (no OCR); Bangla questions retrieve poorly (English embeddings); LLM depends on API quota; one user's question at a time is single-server scale.
20. **Future improvements?** — OCR for scanned PDFs, Bangla embeddings (multilingual model), answer streaming, hybrid BM25 ranking, user feedback loop, Docker deployment.
21. **What is a token?** — The text units LLMs read (~¾ of a word). Our context of 20 chunks ≈ 5k tokens, well within Gemini's 1M-token window.
22. **What happens on server restart?** — Chroma is persistent on disk; vectors reload instantly, no re-embedding. Only the first-ever setup downloads the embedding model.
23. **How much does it cost to run?** — Local embeddings are free; Gemini free tier covers answering (flash-lite has a generous daily quota); the whole stack runs on a laptop CPU.
24. **What is a hallucination and how do you stop it?** — When an LLM invents facts. We stop it by only allowing context-grounded answers, refusing otherwise, and showing sources.
25. **Why is the answer slow sometimes?** — LLM network latency (1–4 s typical); retrieval itself is milliseconds.

**Glossary one-liners:** *RAG* = retrieve then generate · *Embedding* = meaning as a vector · *Vector DB* = search engine for embeddings · *Chunk* = a ~1000-char piece of the book · *LLM* = large language model (Gemini) · *Hallucination* = confident made-up answer · *JWT* = signed login token · *Swagger/OpenAPI* = auto API documentation · *REST* = JSON over HTTP API style.

---

## 13. If something goes wrong during the demo

| Symptom | Say / Do |
|---|---|
| Slow first answer | "The models were just loaded — subsequent answers are faster." |
| "Temporarily unavailable" answer | "The free LLM quota is rate-limited; the system degrades gracefully instead of crashing." |
| Server won't start | Run `python scripts/check_setup.py` from backend — it prints exactly what's wrong. |
| Asked an unknown question | That IS the demo — point at the polite fallback and explain the two-layer guard. |

Good luck — you built (well, shipped 🙂) a genuinely complete system. Own it.
