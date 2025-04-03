# src/retrieval.py
"""
File: retrieval.py
Retrieve relevant context based on a user query using the vector store.
"""

from embedder import Embedder
from vector_store import VectorStore

class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query, top_k=3):
        query_embedding = self.embedder.embed_text(query)
        results = self.vector_store.search(query_embedding, top_k)
        return results

if __name__ == "__main__":
    embedder = Embedder()
    store = VectorStore(dimension=384)
    import numpy as np
    dummy_embeddings = [np.random.rand(384) for _ in range(5)]
    dummy_docs = [{"content": f"Document {i}", "source": f"doc{i}"} for i in range(5)]
    store.add_embeddings(dummy_embeddings, dummy_docs)
    retriever = Retriever(embedder, store)
    res = retriever.retrieve("sample query", top_k=2)
    print(res)
