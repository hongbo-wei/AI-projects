# src/chatbot.py
"""
File: chatbot.py
Main logic tying retrieval and generation together.
"""

from .data_loader import load_documents
from .text_splitter import split_documents
from .embedder import Embedder
from .vector_store import VectorStore
from .retrieval import Retriever
from .generator import Generator

def build_chatbot():
    # Load raw documents from data/raw
    documents = load_documents("data/raw")
    # Split documents into chunks
    chunks = split_documents(documents, chunk_size=500, overlap=50)
    
    # Initialize embedder and compute embeddings for each chunk
    embedder = Embedder()
    embeddings = embedder.embed_documents(chunks)
    
    # Create vector store (384 is the dimension for our embedding model)
    vector_store = VectorStore(dimension=384)
    vector_store.add_embeddings(embeddings, chunks)
    
    # Initialize retriever and generator
    retriever = Retriever(embedder, vector_store)
    generator = Generator()
    
    return retriever, generator

def chatbot_response(query):
    retriever, generator = build_chatbot()
    # Retrieve top context chunks
    context_chunks = retriever.retrieve(query, top_k=3)
    context_text = "\n".join([chunk["content"] for chunk in context_chunks])
    # Format the prompt by combining the query and retrieved context
    prompt = f"Question: {query}\nContext: {context_text}\nAnswer:"
    # Generate and return the response
    response = generator.generate(prompt)
    return response

if __name__ == "__main__":
    query = "What is artificial intelligence?"
    response = chatbot_response(query)
    print("Response:", response)
