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
