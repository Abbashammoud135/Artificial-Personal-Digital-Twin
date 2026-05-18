from core.rag.embeddings import EmbeddingModel

class Retriever:

    def __init__(self, vector_store):
        self.embedder = EmbeddingModel()
        self.vector_store = vector_store

    def retrieve(self, query: str, k=5):
        if self.vector_store.index.ntotal == 0:
                return []
        print("FAISS vectors:", self.vector_store.index.ntotal)
        print("Metadata size:", len(self.vector_store.metadata))
        
        query_vec = self.embedder.embed([query])[0]

        return self.vector_store.search(query_vec, k)