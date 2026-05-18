from core.rag.embeddings import EmbeddingModel
from core.rag.vector_store import VectorStore

class MedicalMemory:

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.store = VectorStore()
    
    def add_report(self, text: str, meta: dict):

        vec = self.embedder.embed([text])[0]

        self.store.add([vec], [meta])

    def retrieve_similar(self, text: str):
        vec = self.embedder.embed([text])[0]

        return self.store.search(vec, k=5)