# qa_pipline.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from embedding.embed_store import load_embeddings_from_mongodb

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")

HUGGINGFACE_API_KEY = os.getenv("HF_API_KEY")
API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

def load_index(index_path="faiss_index/index.faiss"):
    return faiss.read_index(index_path)

def load_chunks(path="data/chunks.json"):
    with open(path, "r") as f:
        return json.load(f)

# ----------- For single PDF mode (local FAISS) ------------
def retrieve_context_single(query, k=5):
    index = load_index()
    chunks = load_chunks()
    query_vec = model.encode([query])
    _, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]

# ----------- For multiple PDF mode (MongoDB) --------------
def retrieve_context_multi(user_id: str, collection_name: str, query: str, k=5):
    chunks, embeddings = load_embeddings_from_mongodb(user_id, collection_name)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    query_vec = model.encode([query])
    _, I = index.search(np.array(query_vec), k)
    return [chunks[i] for i in I[0]]


# ----------- Sending query to the deepseek chat model --------------

def query_deepseek_chat_model(prompt: str):
    payload = {
        "model": "deepseek/deepseek-v3-0324",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that only uses the provided context to answer questions."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API error: {e}, Response: {getattr(e.response, 'text', 'No response text')}")
        return "Error fetching answer from DeepSeek model."
# ----------- Generating answers based on the question and the chunks --------------
def generate_answer(question, context_chunks):
    context = "\n".join(context_chunks)
    prompt = f"Answer the question based only on the context.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
    return query_deepseek_chat_model(prompt)
