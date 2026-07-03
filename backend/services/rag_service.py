import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings


class RAGService:
    def __init__(self):
        from sentence_transformers import SentenceTransformer

        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def _embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()

    def add_documents(
        self, ids: list[str], texts: list[str], metadatas: list[dict] | None = None
    ):
        embeddings = self._embed(texts)
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self, query_text: str, n_results: int = 5, metadata_filter: dict | None = None
    ) -> list[dict]:
        query_embedding = self._embed([query_text])[0]
        where = metadata_filter or {}
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )
        documents = []
        for i in range(len(results["ids"][0])):
            documents.append(
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                    if results["metadatas"]
                    else {},
                    "distance": results["distances"][0][i]
                    if results["distances"]
                    else None,
                }
            )
        return documents

    def delete_document(self, doc_id: str):
        self.collection.delete(ids=[doc_id])

    def count(self) -> int:
        return self.collection.count()


_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
