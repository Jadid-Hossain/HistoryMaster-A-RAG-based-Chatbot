"""Chroma vector database wrapper.

All knowledge chunks (text + embedding + metadata) live in a persistent
Chroma collection, so the index survives restarts without rebuilding.
Deleting a document removes exactly its chunks - no retraining involved.
"""
import threading

from ..config import CHROMA_DIR
from ..logger import get_logger
from .embeddings import embedder

log = get_logger("historymaster.vectorstore")

COLLECTION_NAME = "knowbot_knowledge_base"


class VectorStoreService:
    def __init__(self) -> None:
        self._store = None
        self._lock = threading.Lock()

    @property
    def ready(self) -> bool:
        return self._store is not None

    def load(self) -> None:
        with self._lock:
            if self._store is not None:
                return
            from langchain_chroma import Chroma

            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            log.info("Opening Chroma vector DB at %s ...", CHROMA_DIR)
            self._store = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embedder.get(),
                persist_directory=str(CHROMA_DIR),
                collection_metadata={"hnsw:space": "cosine"},
            )
            log.info("Vector DB ready (%d chunks indexed).", self.count())

    def get(self):
        if self._store is None:
            raise RuntimeError("Vector store not loaded yet.")
        return self._store

    def count(self) -> int:
        if self._store is None:
            return 0
        try:
            return self._store._collection.count()
        except Exception:
            return 0

    def add_chunks(self, doc_id: int, filename: str, chunks: list[str]) -> int:
        """Embed + store chunks for one document. Returns the chunk count."""
        if not chunks:
            return 0
        store = self.get()
        ids = [f"doc{doc_id}-chunk{i}" for i in range(len(chunks))]
        metadatas = [
            {"doc_id": int(doc_id), "filename": filename, "chunk_index": i}
            for i in range(len(chunks))
        ]
        store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
        return len(chunks)

    def delete_document(self, doc_id: int) -> None:
        self.get()._collection.delete(where={"doc_id": int(doc_id)})

    def search(self, query: str, top_k: int) -> list[tuple]:
        """Return [(Document, cosine_similarity)] sorted best-first."""
        store = self.get()
        pairs = store.similarity_search_with_score(query, k=top_k)
        # Chroma returns cosine *distance*; convert to similarity.
        return [(doc, 1.0 - float(distance)) for doc, distance in pairs]


vector_store = VectorStoreService()
