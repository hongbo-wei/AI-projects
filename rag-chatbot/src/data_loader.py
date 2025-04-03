# src/data_loader.py
"""
File: data_loader.py
Load and preprocess documents from the data/raw directory.
"""

import os

class Document:
    def __init__(self, content, source):
        self.content = content
        self.source = source

def load_documents(raw_dir="data/raw"):
    documents = []
    for filename in os.listdir(raw_dir):
        if filename.endswith(".txt"):
            path = os.path.join(raw_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append(Document(content=text, source=filename))
    return documents

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents.")
