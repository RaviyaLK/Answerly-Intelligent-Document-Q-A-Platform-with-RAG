
#   embed_store.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os
from db.db import insert_chunks_and_embeddings,get_chunks_and_embeddings_for_user # ✅ Use your db logic

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---- Embedding ----
def embed_chunks(chunks):
    return model.encode(chunks)

# ---- SINGLE PDF option (local) ----
def save_faiss_index(embeddings, chunks, index_path="faiss_index/index.faiss"):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)

    with open("data/chunks.json", "w") as f:
        json.dump(chunks, f)

# ---- MULTIPLE PDF option (MongoDB) ----
def store_pdf_chunks_for_user(user_id: str, collection_name: str, chunks: list, embeddings=None):
    if embeddings is None:
        embeddings = embed_chunks(chunks)
    insert_chunks_and_embeddings(user_id, collection_name, chunks, embeddings)

def load_embeddings_from_mongodb(user_id: str, collection_name: str):
    return get_chunks_and_embeddings_for_user(user_id, collection_name)