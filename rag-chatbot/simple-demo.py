import gradio as gr
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

# Initialize InferenceClient for text generation
client = InferenceClient(model="meta-llama/Meta-Llama-3-8B-Instruct")

# Sample knowledge base (You can replace with your own docs)
docs = [
    "Gradio is a Python library that lets you build UIs for ML models.",
    "RAG stands for Retrieval-Augmented Generation.",
    "FAISS is a library for efficient similarity search.",
    "Transformers can be used for tasks like text generation, classification, and more.",
    "SentenceTransformers make it easy to create embeddings for semantic search.",
    "Hongbo Wei is his own hero, he is a future Asian boxing champion.",
]

# Load embedding model and embed knowledge base
embedder = SentenceTransformer('all-MiniLM-L6-v2')
doc_embeddings = embedder.encode(docs, convert_to_tensor=False)

# Create FAISS index
index = faiss.IndexFlatL2(doc_embeddings[0].shape[0])
index.add(np.array(doc_embeddings))

def rag_chat(query):
    # Embed query
    query_vec = embedder.encode([query])
    D, I = index.search(np.array(query_vec), k=1)
    
    # Retrieve top doc
    retrieved_doc = docs[I[0][0]]
    
    # Augment query with context
    augmented_input = f"Context: {retrieved_doc}\n\nUser: {query}\nBot:"
    
    # Generate response using Inference API
    response = client.text_generation(
        prompt=augmented_input,
        max_new_tokens=100,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )
    
    # Extract just the bot's response (after "Bot:")
    return response.split("Bot:")[-1].strip()

# Gradio UI
iface = gr.Interface(
    fn=rag_chat, 
    inputs="text", 
    outputs="text", 
    title="RAG Chatbot 💬",
    description="A chatbot that uses RAG with Meta-Llama-3-8B-Instruct via HuggingFace Inference API"
)
iface.launch()