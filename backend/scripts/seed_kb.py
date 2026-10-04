"""Seed the knowledge base with all sample documents from knowledge_base/.

Usage:
    python scripts/seed_kb.py           # ingest all KB files into Chroma
    python scripts/seed_kb.py --reset   # wipe DB + vector store first, then ingest
"""
import shutil
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app import database                      # noqa: E402
from app.logger import setup_logging          # noqa: E402
from app.services import ingest               # noqa: E402
from app.services.embeddings import embedder  # noqa: E402
from app.services.vectorstore import vector_store  # noqa: E402


def reset_stores() -> None:
    data_dir = BACKEND_DIR / "data"
    for name in ["knowbot.db", "knowbot.db-wal", "knowbot.db-shm"]:
        path = data_dir / name
        if path.exists():
            path.unlink()
            print(f"Removed {path.name}")
    chroma_dir = data_dir / "chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print("Removed chroma vector store")


def main() -> None:
    setup_logging()
    if "--reset" in sys.argv:
        reset_stores()
    database.init_db()
    embedder.load()
    vector_store.load()

    kb_dir = BACKEND_DIR / "knowledge_base"
    files = sorted(
        p for p in kb_dir.iterdir()
        if p.suffix.lower() in {".pdf", ".txt", ".md", ".docx", ".html", ".htm"}
    )
    if not files:
        print(f"No knowledge base files found in {kb_dir}")
        return

    print(f"Seeding knowledge base from {kb_dir} ({len(files)} files) ...\n")
    total_chunks = 0
    for path in files:
        try:
            documents = ingest.load_documents_from_path(path)
            result = ingest.ingest_documents(
                path.name, path.suffix.lstrip("."), documents, "system",
                size_bytes=path.stat().st_size,
            )
            total_chunks += result["num_chunks"]
            print(f"  [OK]   {path.name:<46} {result['num_chunks']:>3} chunks")
        except Exception as exc:
            print(f"  [FAIL] {path.name:<46} {exc}")

    docs = database.query_one("SELECT COUNT(*) AS n FROM documents")
    print(f"\nDone. Knowledge base now has {docs['n']} documents / "
          f"{vector_store.count()} chunks in the Chroma vector DB "
          f"(added {total_chunks} chunks this run).")
    print("Default accounts (auto-seeded at first server start): "
          "admin/admin123, user/user123")


if __name__ == "__main__":
    main()
