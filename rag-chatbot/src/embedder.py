# src/embedder.py
"""
File: embedder.py
Generate embeddings using SentenceTransformer.
"""

from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        return self.model.encode(text)

    def embed_documents(self, documents):
        # documents: list of dicts with key "content"
        return [self.embed_text(doc["content"]) for doc in documents]

if __name__ == "__main__":
    embedder = Embedder()
    sample_text = "This is a test sentence."
    vec = embedder.embed_text(sample_text)
    print(vec)
