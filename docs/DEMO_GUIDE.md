# 🎤 KnowBot — Live Demo Guide (10 minutes)

Tested question list with **verified expected behaviour**. Rehearse once before class.

## Setup before class (one time)

1. Put your Gemini key in `.env` → `GEMINI_API_KEY=...`
2. `cd backend && python scripts/check_setup.py` → must print **"RESULT: All good!"**
3. `python scripts/seed_kb.py --reset` → fresh knowledge base (~90 chunks)
4. Double-click **`run_demo.bat`** → opens http://localhost:8000
   (keep a terminal visible so the class can see the log lines live — great effect)

## Demo accounts

| Role | Username | Password | Can do |
|------|----------|----------|--------|
| Regular user | `user` | `user123` | chat only |
| Admin | `admin` | `admin123` | chat + manage the knowledge base |

---

## Part 1 — Grounded answers (as `user`)

| Ask | Expected answer (grounded in the handbook PDF) |
|-----|------------------------------------------------|
| When was Greenfield University founded? | 1998 |
| Who is the head of the CSE department? | Dr. James Carter |
| What is the tuition fee for CSE? | 4,200 dollars per semester |
| How many books can I borrow from the library? | 5 books for 14 days |
| What are the names of the hostels? | Ash Hall, Oak Hall (boys) / Birch Hall, Cedar Hall (girls) |
| What topics are covered in the Machine Learning course? | regression, trees, SVMs, clustering, neural networks, CNNs, RNNs, transformers… |
| Who teaches the Machine Learning course? | Dr. Elena Rodriguez |
| When are the final examinations of the Fall semester? | December 8 to December 19 |
| What is the campus emergency hotline? | +1-555-0911 |

**Point at the UI:** every answer shows **📚 Sources** (document name + expandable snippet +
match %) and ⚡ latency — proof that answers come from the knowledge base, not imagination.

## Part 2 — Conversation memory

1. *"What scholarships are available?"* → Chancellor / Dean's List / Vice-Chancellor scholarships.
2. *"Tell me more about the Chancellor one"* → 100% tuition waiver for CGPA 3.90+.
3. *"Who is the warden of River Hall?"* … wait, that's in the test fixture; use: *"Who is the head of the CSE department?"* → *"Where is his office?"* → **Room 210 of the Technology Building** (the "his" was resolved using short-term memory).

## Part 3 — Graceful out-of-scope handling

| Ask | Expected |
|-----|----------|
| Who will win the next football World Cup? | Polite fallback: not found in knowledge base |
| What is the capital of Australia? | Polite fallback (not in KB) |
| hello / thanks | Canned greeting/reply (no LLM call) |
| What can you do? | Describes itself + lists KB topics |

## Part 4 — KB updates WITHOUT retraining (the killer demo)

1. Logout → login as `admin/admin123` → **Admin Panel**.
2. Show the documents table (14-page PDF handbook, DOCX, HTML…).
3. Upload a brand-new small `.txt` file live (prepare one, e.g. `new_cafeteria.txt`:
   *"The new campus food court opened in January 2027 next to the Student Center. It has 8 food stalls and stays open until 11 PM."*).
4. The upload result shows *"N chunks embedded"* instantly.
5. Back to Chat → ask: *"Where is the new food court?"* → correct answer from the file uploaded seconds ago.
6. Say it out loud: **"No model retraining happened — we simply added vectors to the Chroma vector DB."**
7. (Optional) Delete the doc → ask again → graceful fallback. Update cycle complete.

## Part 5 — Engineering closing shots

- **/docs** — Swagger UI; fire one `POST /api/chat/ask` from the browser.
- **backend/logs/app.log** — show a request line with retrieval score + latency.
- **Architecture one-liner:** *"React frontend → FastAPI → LangChain retrieval from a Chroma
  vector DB → Gemini generates an answer strictly from the retrieved context; anything outside
  the KB gets an honest fallback."*
- **Tests:** `python -m pytest` (backend) — auth, RBAC, ingestion formats, incremental update,
  fallback, memory, ownership — all green.

## If something misbehaves

| Symptom | Fix |
|---------|-----|
| "LLM is not configured" | `.env` key missing/typo → fix → restart backend |
| "temporarily unavailable" answer | free-tier quota hit → the bot answers politely; wait for reset, or switch `LLM_MODEL` in `.env` (e.g. `gemini-3.5-flash-lite`) → restart |
| Backend won't start | `python scripts/check_setup.py` and read the report |
| Old answers | `python scripts/seed_kb.py --reset` then restart |

> **Free-tier quota tip:** the current default model `gemini-flash-lite-latest` has the most
> generous free daily limit. Bigger models like `gemini-3.8-flash` allow only ~20 requests/day
> free - plenty for a 10-minute demo, but don't run the eval script with that model on demo day.
> Note: the bot never crashes on quota errors - it replies with a polite
> "temporarily unavailable" message and still shows the retrieved sources.
| Backend won't start | `python scripts/check_setup.py` and read the report |
| Old answers | `python scripts/seed_kb.py --reset` then restart |
