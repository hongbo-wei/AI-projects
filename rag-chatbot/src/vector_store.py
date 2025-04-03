# src/vector_store.py
"""
File: vector_store.py
Build and query the FAISS vector store.
"""

import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []  # List of document dictionaries

    def add_embeddings(self, embeddings, documents):
        # embeddings: list of vectors, documents: list of document dicts
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(documents)

    def search(self, query_embedding, top_k=3):
        query_vec = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vec, top_k)
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        return results

if __name__ == "__main__":
    # Dummy test
    store = VectorStore(dimension=384)  # 384 is the embedding dimension for all-MiniLM-L6-v2
    import numpy as np
    dummy_embeddings = [np.random.rand(384) for _ in range(5)]
    dummy_docs = [{"content": f"Document {i}", "source": f"doc{i}"} for i in range(5)]
    store.add_embeddings(dummy_embeddings, dummy_docs)
    query_vec = np.random.rand(384)
    results = store.search(query_vec, top_k=2)
    print(results)
