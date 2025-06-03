from pymongo import MongoClient
from bson import ObjectId
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.rag_qa_db
pdf_embeddings_collection = db["pdf_embeddings"]

def create_collection_for_user(user_id: str, collection_name: str):
    existing = pdf_embeddings_collection.find_one({
        "user_id": user_id,
        "collection_name": collection_name
    })
    if existing:
        raise ValueError("Collection already exists for this user")

    pdf_embeddings_collection.insert_one({
        "user_id": user_id,
        "collection_name": collection_name,
        "chunks": [],
        "embeddings": []
    })

def insert_chunks_and_embeddings(user_id: str, collection_name: str, chunks, embeddings):
    pdf_embeddings_collection.update_one(
        {"user_id": user_id, "collection_name": collection_name},
        {
            "$push": {
                "chunks": {"$each": chunks},
                "embeddings": {"$each": embeddings.tolist()}
            }
        }
    )


def get_chunks_and_embeddings_for_user(user_id: str, collection_name: str):
    results = list(pdf_embeddings_collection.find({
        "user_id": user_id,
        "collection_name": collection_name
    }))

    if not results:
        return [], np.array([])

    # Note: Expecting chunks and embeddings to be stored as lists
    chunks = []
    embeddings = []

    for doc in results:
        chunks.extend(doc.get("chunks", []))
        embeddings.extend(doc.get("embeddings", []))

    return chunks, np.array(embeddings)

