# 🎤 KnowBot — Live Demo Guide (10 minutes)

The chatbot answers **only from the knowledge base you load** (your PDF).
Anything outside it gets an honest *"not found in my knowledge base"* — never a made-up answer.

## Setup before class (one time)

1. Put your Gemini key in `.env` → `GEMINI_API_KEY=...` (already done).
2. Drop your knowledge base PDF into `backend/knowledge_base/`, then:
   ```bash
   cd backend
   python scripts/seed_kb.py --reset      # wipes old knowledge, loads ONLY your PDF
   python scripts/check_setup.py          # must print "RESULT: All good!"
   ```
3. Double-click **`run_demo.bat`** → opens http://localhost:8000
   (keep a terminal visible so the class can see the log lines live — great effect).

## Demo accounts

| Role | Username | Password | Can do |
|------|----------|----------|--------|
| Regular user | `user` | `user123` | chat only |
| Admin | `admin` | `admin123` | chat + manage the knowledge base |

---

## Part 1 — Grounded answers (as `user`)

- Read your PDF beforehand and pick **4-5 concrete facts** (names, dates, numbers, places).
- Ask each one in the chat. Expected: a correct answer + **📚 Sources** panel showing the
  document name, an expandable snippet and the **match %** + ⚡ response time.
- Ask one **list-type** question (e.g. *"What are the ... mentioned in the document?"*) —
  the bot summarizes the relevant passage.

**Point at the UI:** every answer cites its source — proof that answers come from the PDF,
not from the model's imagination.

## Part 2 — Conversation memory

1. Ask *"Who is <person>?"* (a person from your PDF).
2. Follow up with *"Where is his office?"* / *"Tell me more about that"* — the short-term
   memory rewrites the follow-up into a standalone query and answers from context.

## Part 3 — Graceful out-of-scope handling (the requirement)

| Ask | Expected |
|-----|----------|
| Who will win the next football World Cup? | Polite fallback: not in my knowledge base |
| What is the capital of Australia? | Polite fallback |
| hello / thanks | Canned greeting (no LLM call) |
| What can you do? | Describes itself + lists the topics it actually has |

**Key line for the class:** *"Two layers protect against hallucination — a similarity floor
rejects unrelated questions before the LLM, and the LLM is contract-bound to reply
`NOT_IN_KB` when the retrieved context lacks the answer."*

## Part 4 — KB updates WITHOUT retraining (the killer demo)

1. Logout → login as `admin/admin123` → **Admin Panel**.
2. Upload a small new `.txt` file live (prepare one with a unique fact, e.g.:
   *"The new campus food court opens in January 2027 next to the Student Center."*).
3. The upload result shows *"N chunks embedded"* instantly.
4. Back to Chat → ask about that fact → correct answer, from a file uploaded seconds ago.
5. Say it out loud: **"No model retraining happened — we simply added vectors to the Chroma
   vector database."**
6. (Optional) Delete the doc in the Admin Panel → ask again → graceful fallback.

## Part 5 — Engineering closing shots

- **/docs** — Swagger UI; fire one `POST /api/chat/ask` from the browser.
- **backend/logs/app.log** — request lines with retrieval score + latency.
- **One-line architecture:** *"React frontend → FastAPI → LangChain retrieval from a Chroma
  vector DB → Gemini generates an answer strictly from the retrieved context; anything
  outside the PDF gets an honest fallback."*
- **Tests:** `python -m pytest` (backend) — auth, roles, ingestion, incremental update,
  fallback, memory, ownership — all green.

## If something misbehaves

| Symptom | Fix |
|---------|-----|
| "LLM is not configured" | `.env` key missing/typo → fix → restart backend |
| "temporarily unavailable" answer | free-tier quota hit → bot stays polite; wait for reset or switch `LLM_MODEL` in `.env` (e.g. `gemini-3.5-flash-lite`) → restart |
| Backend won't start | `python scripts/check_setup.py` and read the report |
| Want to start the KB over | `python scripts/seed_kb.py --reset` |

> **Free-tier quota tip:** the default model `gemini-flash-lite-latest` has the most generous
> free daily limit. Bigger models like `gemini-3.8-flash` allow only ~20 requests/day free —
> plenty for a 10-minute demo, but don't burn it on test runs that day.
