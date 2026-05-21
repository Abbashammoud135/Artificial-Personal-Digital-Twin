import json
from pathlib import Path
from typing import List
from tools.pdf_tool import PDFTool
from core.rag.embeddings import EmbeddingModel
from core.rag.vector_store import VectorStore


class KnowledgeBase:
    def __init__(self, data_folder: str | None = None):
        self.data_folder = Path(data_folder) if data_folder else Path(__file__).resolve().parents[2] / "data"
        self.index_dir = self.data_folder / ".faiss"
        self.index_path = self.index_dir / "knowledge.index"
        self.metadata_path = self.index_dir / "knowledge.metadata.json"
        self.signatures_path = self.index_dir / "knowledge.signatures.json"

        self.embedder = EmbeddingModel()
        self.store = VectorStore()
        self.initialized = False

    def initialize(self):
        if self.initialized:
            return

        if not self.data_folder.exists():
            print(f"⚠️ KnowledgeBase data path not found: {self.data_folder}")
            self.initialized = True
            return

        self.index_dir.mkdir(parents=True, exist_ok=True)

        if self._load_persisted_index():
            print(f"✅ Loaded persisted FAISS knowledge base from {self.index_path}")
            self.initialized = True
            return

        documents = []
        indexed_files = []

        for candidate in sorted(self.data_folder.rglob("*")):
            if not candidate.is_file():
                continue

            if candidate.suffix.lower() == ".pdf":
                pages = PDFTool.extract_pages(str(candidate))
                if pages:
                    indexed_files.append(candidate.name)
                for page_index, page_text in enumerate(pages, start=1):
                    for chunk_index, chunk in enumerate(self._chunk_text(page_text), start=1):
                        documents.append({
                            "text": chunk,
                            "source": candidate.name,
                            "page": page_index,
                            "chunk": chunk_index
                        })
            elif candidate.suffix.lower() in {".txt", ".md"}:
                try:
                    text = candidate.read_text(encoding="utf-8", errors="ignore")
                except Exception as exc:
                    print(f"⚠️ Failed to read knowledge file {candidate}: {exc}")
                    continue
                if text.strip():
                    indexed_files.append(candidate.name)
                for chunk_index, chunk in enumerate(self._chunk_text(text), start=1):
                    documents.append({
                        "text": chunk,
                        "source": candidate.name,
                        "page": None,
                        "chunk": chunk_index
                    })

        if indexed_files:
            print(f"✅ KnowledgeBase will embed: {', '.join(sorted(set(indexed_files)))}")

        if not documents:
            print(f"⚠️ No knowledge documents indexed from {self.data_folder}")
            self.initialized = True
            return

        vectors = self.embedder.embed([doc["text"] for doc in documents])
        self.store.add(vectors, documents)
        self.store.save(self.index_path, self.metadata_path)
        self._save_file_signatures()

        self.initialized = True
        print(f"✅ KnowledgeBase indexed and persisted {len(documents)} chunks from {self.data_folder}")

    def _chunk_text(self, text: str, max_chars: int = 800) -> List[str]:
        if not text:
            return []

        text = text.replace("\n", " ").strip()
        chunks = []
        start = 0
        while start < len(text):
            end = min(len(text), start + max_chars)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end
        return chunks

    def _gather_data_files(self):
        return [candidate for candidate in sorted(self.data_folder.rglob("*"))
                if candidate.is_file() and candidate.suffix.lower() in {".pdf", ".txt", ".md"}]

    def _build_file_signatures(self, files: List[Path]) -> dict:
        return {
            str(file.relative_to(self.data_folder)): {
                "mtime": file.stat().st_mtime,
                "size": file.stat().st_size
            }
            for file in files
        }

    def _save_file_signatures(self):
        files = self._gather_data_files()
        signatures = self._build_file_signatures(files)
        with self.signatures_path.open("w", encoding="utf-8") as signature_file:
            json.dump(signatures, signature_file, ensure_ascii=False, indent=2)

    def _load_persisted_index(self) -> bool:
        if not self.index_path.exists() or not self.metadata_path.exists() or not self.signatures_path.exists():
            return False

        files = self._gather_data_files()
        current_signatures = self._build_file_signatures(files)
        with self.signatures_path.open("r", encoding="utf-8") as signature_file:
            saved_signatures = json.load(signature_file)

        if current_signatures != saved_signatures:
            return False

        try:
            self.store.load(self.index_path, self.metadata_path)
            return True
        except Exception as exc:
            print(f"⚠️ Failed to load persisted FAISS index: {exc}")
            return False

    def retrieve(self, query: str, k: int = 5):
        if not query or self.store.index.ntotal == 0:
            return []
        print(query)

        query_vec = self.embedder.embed([query])[0]
        return self.store.search(query_vec, k)
