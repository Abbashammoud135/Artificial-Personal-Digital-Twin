import faiss
import numpy as np

class VectorStore:

    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, vectors, metadata):
        if len(vectors) != len(metadata):
          raise ValueError("Vectors and metadata must match")
      
        self.index.add(np.array(vectors).astype("float32"))
        self.metadata.extend(metadata)

    def search(self, query_vector, k=5):

        if self.index.ntotal == 0:
            return []

        D, I = self.index.search(
            np.array([query_vector]).astype("float32"), k
        )

        results = []

        for i in I[0]:
            if 0 <= i < len(self.metadata):
                results.append(self.metadata[i])

        return results