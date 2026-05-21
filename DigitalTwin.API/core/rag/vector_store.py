import json
from pathlib import Path

import faiss
import numpy as np

class VectorStore:

    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadata = []

    def add(self, vectors, metadata):
        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata must match")

        vectors = np.array(vectors, dtype="float32")
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        if vectors.shape[1] != self.dim:
            raise ValueError(f"Expected vector dimension {self.dim}, got {vectors.shape[1]}")

        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_vector, k=5):
        if self.index.ntotal == 0:
            return []

        query_vector = np.array(query_vector, dtype="float32")
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        faiss.normalize_L2(query_vector)
        distances, indices = self.index.search(query_vector, k)
        hits = []

        for idx in indices[0]:
            if idx < 0 or idx >= len(self.metadata):
                continue
            hits.append(self.metadata[idx])

        return hits

    def save(self, index_path: str | Path, metadata_path: str | Path):
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))

        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            json.dump(self.metadata, metadata_file, ensure_ascii=False, indent=2)

    def load(self, index_path: str | Path, metadata_path: str | Path):
        self.index = faiss.read_index(str(index_path))
        with Path(metadata_path).open("r", encoding="utf-8") as metadata_file:
            self.metadata = json.load(metadata_file)
        self.dim = self.index.d