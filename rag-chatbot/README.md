# RAG Chatbot

This project is a Retrieval-Augmented Generation (RAG) chatbot that answers questions using external documents.

## Folder Structure

- **data/**: Contains raw and processed documents.
- **embeddings/**: (Optional) Persisted FAISS index and serialized embeddings.
- **src/**: Source code including data loading, text splitting, embedding, vector store, retrieval, generator, and chatbot logic.
- **ui/**: Gradio interface for the chatbot.
- **requirements.txt**: Python dependencies.
- **.env**: Environment variables (e.g., API keys).

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt


Here's how it all links together:

You load and embed documents somewhere earlier (most likely in vector_store.py or during init).

The retriever uses the same embedder model to convert your query.

The search() method finds documents with closest vector distance (cosine similarity or something similar).

Those chunks are then passed to the generator (Generator() in chatbot.py) to form the final answer.