"""Live accuracy evaluation of the RAG pipeline against the sample knowledge base.

Run AFTER seeding (python scripts/seed_kb.py) and configuring .env:

    python scripts/eval_chat.py

Prints a table with every test question, the bot's answer, and PASS/FAIL,
and saves the full report to ../docs/EVAL_RESULTS.md.
"""
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.logger import setup_logging  # noqa: E402
from app.services import chatbot  # noqa: E402
from app.services.embeddings import embedder  # noqa: E402
from app.services.llm import llm_service  # noqa: E402
from app.services.vectorstore import vector_store  # noqa: E402

# (question, substrings that must appear in the answer) - None = expect fallback
CASES = [
    ("When was Greenfield University founded?", ["1998"]),
    ("Who is the head of the CSE department?", ["James Carter"]),
    ("What is the tuition fee for CSE?", ["4,200"]),
    ("How many books can I borrow from the library?", ["5"]),
    ("What are the names of the hostels?", ["Ash Hall"]),
    ("Who teaches the Machine Learning course?", ["Elena Rodriguez"]),
    ("How many credits is the Machine Learning course?", ["3"]),
    ("When are the final examinations of the Fall semester?", ["December 8"]),
    ("What is the campus emergency hotline?", ["0911"]),
    ("What scholarships are available?", ["Chancellor"]),
    ("What is the application fee for local students?", ["40"]),
    ("Where is the Admissions Office located?", ["102"]),
    ("What is the fine for overdue library books?", ["25"]),
    ("What is the minimum GPA for undergraduate admission?", ["3.50"]),
    ("Who is the Vice-Chancellor?", ["Sarah Mitchell"]),
    ("Which clubs won the National Robotics Olympiad?", ["Robotics Club"]),
    # out-of-scope -> graceful fallback
    ("Who will win the next football World Cup?", None),
    ("What is the capital of Australia?", None),
    ("How do I bake a chocolate cake at home?", None),
    # small talk -> canned
    ("hello", None),
]


def main() -> int:
    setup_logging()
    embedder.load()
    vector_store.load()
    llm_service.load()
    if not llm_service.ready:
        print("LLM not configured - put your API key in .env first.")
        return 1
    print(f"Evaluating {len(CASES)} questions | provider={llm_service.provider} "
          f"model={llm_service.model_name} | chunks={vector_store.count()}\n")

    passed = 0
    rows = []
    for question, must_include in CASES:
        started = time.time()
        result = chatbot.answer_question(question)
        elapsed = time.time() - started
        answer = result["answer"].replace("\n", " ")
        if must_include is None:
            ok = (not result["in_scope"]) or result["kind"] in ("greeting", "capabilities")
            expect = "<graceful fallback / canned>"
        else:
            ok = result["in_scope"] and all(m.lower() in answer.lower() for m in must_include)
            expect = " AND ".join(must_include)
        passed += ok
        mark = "PASS" if ok else "FAIL"
        rows.append((mark, question, expect, answer[:110], elapsed))
        print(f"[{mark}] {question}")
        print(f"       -> {answer[:150]}")
        print(f"       (expected: {expect}) {elapsed:.1f}s\n")

    print("=" * 70)
    print(f"RESULT: {passed}/{len(CASES)} passed")
    print("=" * 70)

    out = BACKEND_DIR.parent / "docs" / "EVAL_RESULTS.md"
    with out.open("w", encoding="utf-8") as f:
        f.write("# KnowBot RAG evaluation results\n\n")
        f.write(f"- LLM: `{llm_service.provider}/{llm_service.model_name}`\n")
        f.write(f"- Knowledge base: {vector_store.count()} chunks\n")
        f.write(f"- Score: **{passed}/{len(CASES)}**\n\n")
        f.write("| Status | Question | Expected | Answer (trimmed) | Time |\n|---|---|---|---|---|\n")
        for mark, question, expect, answer, elapsed in rows:
            f.write(f"| {mark} | {question} | {expect} | {answer} | {elapsed:.1f}s |\n")
    print(f"Report saved to {out}")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
