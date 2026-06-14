import os
from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        self.embedder = SentenceTransformerEmbeddingFunction(model_name=settings.EMBEDDING_MODEL)

    def _collection(self, role: str):
        name = role.lower().replace("/", "_").replace(" ", "_")[:60]
        return self.client.get_or_create_collection(name=name, embedding_function=self.embedder)

    def chunk_text(self, text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunks.append(" ".join(words[start:end]))
            start = max(end - overlap, end)
        return [c for c in chunks if len(c) > 80]

    def ingest_role_documents(self, role: str) -> int:
        kb_dir = Path(settings.KNOWLEDGE_BASE_DIR) / role.lower().replace("/", "_").replace(" ", "_")
        kb_dir.mkdir(parents=True, exist_ok=True)
        collection = self._collection(role)
        count = 0
        for file in kb_dir.glob("*.txt"):
            text = file.read_text(encoding="utf-8", errors="ignore")
            chunks = self.chunk_text(text)
            if not chunks:
                continue
            ids = [f"{file.stem}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": file.name, "role": role, "chunk": i} for i in range(len(chunks))]
            collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
            count += len(chunks)
        return count

    def retrieve(self, role: str, queries: list[str], top_k: int = 4) -> list[dict]:
        self.ingest_role_documents(role)
        collection = self._collection(role)
        results = []
        for q in queries[:3]:
            hit = collection.query(query_texts=[q], n_results=top_k)
            docs = hit.get("documents", [[]])[0]
            metas = hit.get("metadatas", [[]])[0]
            dists = hit.get("distances", [[]])[0]
            for doc, meta, dist in zip(docs, metas, dists):
                results.append({"content": doc, "metadata": meta, "distance": dist})
        seen = set()
        unique = []
        for item in results:
            key = item["content"][:120]
            if key not in seen:
                unique.append(item)
                seen.add(key)
        return unique[:top_k]
