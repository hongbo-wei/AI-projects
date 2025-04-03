# src/text_splitter.py
"""
File: text_splitter.py
Split documents into manageable chunks.
"""

def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def split_documents(documents, chunk_size=500, overlap=50):
    splitted = []
    for doc in documents:
        chunks = split_text(doc.content, chunk_size, overlap)
        for i, chunk in enumerate(chunks):
            splitted.append({
                "content": chunk,
                "source": doc.source,
                "chunk_id": f"{doc.source}_{i}"
            })
    return splitted

if __name__ == "__main__":
    sample = "This is a sample text. " * 100
    chunks = split_text(sample, chunk_size=100, overlap=20)
    print(f"Created {len(chunks)} chunks.")
