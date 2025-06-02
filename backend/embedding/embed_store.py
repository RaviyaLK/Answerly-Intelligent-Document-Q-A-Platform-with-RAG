# embedding/embed_store.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks):
    embeddings = model.encode(chunks)
    return embeddings

def save_faiss_index(embeddings, chunks, index_path="faiss_index/index.faiss"):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    with open("data/chunks.json", "w") as f:
        json.dump(chunks, f)
