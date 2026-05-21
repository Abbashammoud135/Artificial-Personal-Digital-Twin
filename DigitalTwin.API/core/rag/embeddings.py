from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, texts):
        if not texts:
            return np.zeros((0, 384), dtype="float32")

        vectors = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        return vectors.astype("float32")